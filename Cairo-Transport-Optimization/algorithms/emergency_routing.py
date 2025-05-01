from typing import Dict, List, Tuple, Optional
import heapq
import math

class EmergencyRouter:
    def __init__(self, network):
        self.network = network
        
    def a_star_search(self, start: int, goal: int, time_of_day: Optional[str] = None) -> Tuple[List[int], float]:
        """A* algorithm with time-dependent weights and emergency priorities"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {node: float('inf') for node in self.network.nodes}
        g_score[start] = 0
        
        f_score = {node: float('inf') for node in self.network.nodes}
        f_score[start] = self.heuristic(start, goal)
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                return self._reconstruct_path(came_from, current), g_score[goal]
                
            for neighbor, data in self.network.get_node_neighbors(current):
                tentative_g_score = g_score[current] + self.get_emergency_weight(
                    current, neighbor, time_of_day)
                    
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    
        return [], float('inf')  # No path found
    
    def get_emergency_weight(self, u: int, v: int, time_of_day: Optional[str]) -> float:
        """Calculate weight with emergency vehicle priorities"""
        base_weight = self.network.get_time_dependent_weight(u, v, time_of_day) if time_of_day else self.network.edges[(u, v)]['distance']
        
        # Apply emergency vehicle priority factors based on speed limit and lanes
        speed_factor = self.network.edges[(u, v)]['speed_limit'] / 60  # Normalize to base speed of 60 km/h
        lanes_factor = self.network.edges[(u, v)]['lanes'] / 2  # Normalize to base of 2 lanes
        
        # Prioritize routes to hospitals and emergency facilities
        if self.network.nodes[v]['type'] in ['hospital', 'police', 'fire_station']:
            base_weight *= 0.7
            
        # Consider road characteristics for emergency vehicles
        road_factor = (speed_factor + lanes_factor) / 2
        base_weight *= (1.5 - road_factor)  # Better roads (higher speed, more lanes) reduce weight
            
        return base_weight
    
    def heuristic(self, a: int, b: int) -> float:
        """Haversine distance heuristic for lat/lon coordinates"""
        lat1, lon1 = self.network.nodes[a]['latitude'], self.network.nodes[a]['longitude']
        lat2, lon2 = self.network.nodes[b]['latitude'], self.network.nodes[b]['longitude']
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of Earth in kilometers
        return c * r
    
    def _reconstruct_path(self, came_from: Dict[int, int], current: int) -> List[int]:
        """Reconstruct path from came_from dictionary"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
    
    def find_nearest_emergency_facility(self, location: int, facility_type: str = 'hospital') -> Tuple[int, List[int], float]:
        """Find the nearest emergency facility of specified type"""
        facilities = self.network.get_facility_nodes(facility_type)
        if not facilities:
            return None, [], float('inf')
            
        best_facility = None
        best_path = []
        best_distance = float('inf')
        
        for facility in facilities:
            path, distance = self.a_star_search(location, facility)
            if distance < best_distance:
                best_facility = facility
                best_path = path
                best_distance = distance
                
        return best_facility, best_path, best_distance
    
    def get_emergency_response_time(self, start: int, end: int, time_of_day: Optional[str] = None) -> Dict:
        """Calculate estimated emergency response time and route details"""
        path, distance = self.a_star_search(start, end, time_of_day)
        
        if not path:
            return {
                'success': False,
                'message': 'No valid emergency route found'
            }
            
        # Calculate estimated time based on distance and road characteristics
        total_time = 0
        road_details = []
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_data = self.network.edges[(u, v)]
            
            # Base speed is the road's speed limit
            base_speed = edge_data['speed_limit']
            
            # Adjust speed based on number of lanes and traffic
            lanes_factor = edge_data['lanes'] / 2  # Normalize to base of 2 lanes
            traffic_factor = 1.0
            if time_of_day and (u, v) in self.network.traffic_patterns:
                traffic_factor = 1.0 / self.network.traffic_patterns[(u, v)][time_of_day]
            
            adjusted_speed = base_speed * lanes_factor * traffic_factor
            
            # Calculate time for this segment
            segment_time = edge_data['distance'] / adjusted_speed
            total_time += segment_time
            
            road_details.append({
                'segment': (u, v),
                'speed_limit': edge_data['speed_limit'],
                'lanes': edge_data['lanes'],
                'distance': edge_data['distance'],
                'time': segment_time
            })
            
        return {
            'success': True,
            'total_distance': distance,
            'estimated_time': total_time * 60,  # Convert to minutes
            'path': path,
            'road_details': road_details
        } 