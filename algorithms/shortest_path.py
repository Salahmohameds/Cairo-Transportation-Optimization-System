from typing import Dict, List, Tuple, Optional
import heapq

class TrafficOptimizer:
    def __init__(self, network):
        self.network = network
        
    def dijkstra(self, start: int, end: int, time_of_day: Optional[str] = None) -> Tuple[List[int], float]:
        """Standard Dijkstra's with optional time-dependent weights"""
        distances = {node: float('inf') for node in self.network.nodes}
        distances[start] = 0
        previous = {node: None for node in self.network.nodes}
        heap = [(0, start)]
        visited = set()
        
        while heap:
            current_dist, u = heapq.heappop(heap)
            
            if u == end:
                break
                
            if u in visited:
                continue
                
            visited.add(u)
            
            for v, data in self.network.get_node_neighbors(u):
                if v in visited:
                    continue
                    
                if time_of_day:
                    weight = self.network.get_time_dependent_weight(u, v, time_of_day)
                else:
                    weight = data['distance']
                    
                if distances[v] > distances[u] + weight:
                    distances[v] = distances[u] + weight
                    previous[v] = u
                    heapq.heappush(heap, (distances[v], v))
                    
        return self._reconstruct_path(start, end, previous), distances[end]
    
    def bidirectional_dijkstra(self, start: int, end: int, time_of_day: Optional[str] = None) -> Tuple[List[int], float]:
        """Bidirectional Dijkstra's algorithm for faster path finding"""
        # Forward search
        distances_f = {node: float('inf') for node in self.network.nodes}
        distances_f[start] = 0
        previous_f = {node: None for node in self.network.nodes}
        heap_f = [(0, start)]
        
        # Backward search
        distances_b = {node: float('inf') for node in self.network.nodes}
        distances_b[end] = 0
        previous_b = {node: None for node in self.network.nodes}
        heap_b = [(0, end)]
        
        visited_f = set()
        visited_b = set()
        best_distance = float('inf')
        best_middle = None
        
        while heap_f and heap_b:
            # Forward search step
            if heap_f:
                current_dist_f, u_f = heapq.heappop(heap_f)
                if u_f in visited_f:
                    continue
                visited_f.add(u_f)
                
                for v, data in self.network.get_node_neighbors(u_f):
                    if v in visited_f:
                        continue
                        
                    if time_of_day:
                        weight = self.network.get_time_dependent_weight(u_f, v, time_of_day)
                    else:
                        weight = data['distance']
                        
                    if distances_f[v] > distances_f[u_f] + weight:
                        distances_f[v] = distances_f[u_f] + weight
                        previous_f[v] = u_f
                        heapq.heappush(heap_f, (distances_f[v], v))
                        
                        # Check if we found a better path through this node
                        if v in visited_b and distances_f[v] + distances_b[v] < best_distance:
                            best_distance = distances_f[v] + distances_b[v]
                            best_middle = v
                            
            # Backward search step
            if heap_b:
                current_dist_b, u_b = heapq.heappop(heap_b)
                if u_b in visited_b:
                    continue
                visited_b.add(u_b)
                
                for v, data in self.network.get_node_neighbors(u_b):
                    if v in visited_b:
                        continue
                        
                    if time_of_day:
                        weight = self.network.get_time_dependent_weight(v, u_b, time_of_day)
                    else:
                        weight = data['distance']
                        
                    if distances_b[v] > distances_b[u_b] + weight:
                        distances_b[v] = distances_b[u_b] + weight
                        previous_b[v] = u_b
                        heapq.heappush(heap_b, (distances_b[v], v))
                        
                        # Check if we found a better path through this node
                        if v in visited_f and distances_f[v] + distances_b[v] < best_distance:
                            best_distance = distances_f[v] + distances_b[v]
                            best_middle = v
                            
            # Early termination if we've found a good path
            if best_middle and min(distances_f[u_f] for _, u_f in heap_f) + min(distances_b[u_b] for _, u_b in heap_b) >= best_distance:
                break
                
        if best_middle is None:
            return [], float('inf')
            
        # Reconstruct path
        path = []
        current = best_middle
        while current != start:
            path.append(current)
            current = previous_f[current]
        path.append(start)
        path.reverse()
        
        current = best_middle
        while current != end:
            current = previous_b[current]
            path.append(current)
            
        return path, best_distance
    
    def _reconstruct_path(self, start: int, end: int, previous: Dict[int, Optional[int]]) -> List[int]:
        """Reconstruct path from previous node dictionary"""
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = previous[current]
            
        if path[-1] != start:
            return []
            
        return path[::-1]
    
    def get_alternative_routes(self, start: int, end: int, time_of_day: Optional[str] = None, 
                             num_alternatives: int = 3) -> List[Tuple[List[int], float]]:
        """Find alternative routes between start and end nodes"""
        routes = []
        used_edges = set()
        
        for _ in range(num_alternatives):
            # Temporarily increase weights of used edges
            original_weights = {}
            for u, v in used_edges:
                if time_of_day:
                    original_weights[(u, v)] = self.network.get_time_dependent_weight(u, v, time_of_day)
                    self.network.edges[(u, v)]['distance'] *= 2
                else:
                    original_weights[(u, v)] = self.network.edges[(u, v)]['distance']
                    self.network.edges[(u, v)]['distance'] *= 2
                    
            # Find new path
            path, distance = self.dijkstra(start, end, time_of_day)
            
            # Restore original weights
            for (u, v), weight in original_weights.items():
                self.network.edges[(u, v)]['distance'] = weight
                
            if path:
                routes.append((path, distance))
                # Add edges of this path to used edges
                for i in range(len(path) - 1):
                    used_edges.add((path[i], path[i + 1]))
                    
        return routes 