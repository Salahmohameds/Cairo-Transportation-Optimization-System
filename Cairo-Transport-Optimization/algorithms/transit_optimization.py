from typing import Dict, List, Tuple, Optional
import heapq

class TransitOptimizer:
    def __init__(self, network):
        self.network = network
        
    def optimize_bus_schedule(self, demand_data: Dict[Tuple[int, int], int]) -> Dict:
        """DP solution for bus scheduling based on demand"""
        # Create a sorted list of time slots and demands
        time_slots = sorted(set(time for _, time in demand_data.keys()))
        routes = list(set(route for route, _ in demand_data.keys()))
        
        # DP table: dp[time][route] = optimal buses assigned
        dp = {}
        prev = {}
        
        # Initialize base cases
        for t in time_slots:
            dp[t] = {}
            prev[t] = {}
            for route in routes:
                demand = demand_data.get((route, t), 0)
                buses_needed = max(1, demand // 50)  # Assume 50 passengers per bus
                
                if t == time_slots[0]:
                    dp[t][route] = buses_needed
                    prev[t][route] = None
                else:
                    # Option 1: Keep same number of buses as previous time
                    option1 = dp[time_slots[t-1]][route] + abs(buses_needed - dp[time_slots[t-1]][route])
                    
                    # Option 2: Adjust to current demand
                    option2 = buses_needed
                    
                    if option1 < option2:
                        dp[t][route] = dp[time_slots[t-1]][route]
                        prev[t][route] = 'maintain'
                    else:
                        dp[t][route] = buses_needed
                        prev[t][route] = 'adjust'
                        
        # Reconstruct optimal schedule
        schedule = {}
        current_t = time_slots[-1]
        while current_t in prev:
            schedule[current_t] = {}
            for route in routes:
                schedule[current_t][route] = {
                    'buses': dp[current_t][route],
                    'action': prev[current_t][route]
                }
            current_t = time_slots[time_slots.index(current_t)-1] if time_slots.index(current_t) > 0 else None
            
        return schedule
    
    def optimize_route_frequency(self, route: List[int], demand_data: Dict[int, int]) -> Dict:
        """Optimize bus frequency for a specific route based on demand"""
        total_demand = sum(demand_data.values())
        avg_demand = total_demand / len(demand_data)
        
        # Calculate base frequency (buses per hour)
        base_frequency = max(1, avg_demand / 50)  # Assume 50 passengers per bus
        
        # Adjust frequency based on peak demand
        peak_demand = max(demand_data.values())
        peak_factor = peak_demand / avg_demand if avg_demand > 0 else 1
        
        # Calculate optimal frequencies for different time periods
        frequencies = {
            'peak': base_frequency * peak_factor,
            'off_peak': base_frequency * 0.7,
            'night': base_frequency * 0.5
        }
        
        return {
            'base_frequency': base_frequency,
            'peak_frequency': frequencies['peak'],
            'off_peak_frequency': frequencies['off_peak'],
            'night_frequency': frequencies['night'],
            'total_demand': total_demand,
            'peak_demand': peak_demand
        }
    
    def optimize_stop_sequence(self, route: List[int], demand_data: Dict[int, int]) -> List[int]:
        """Optimize the sequence of stops to minimize total passenger travel time"""
        n = len(route)
        if n <= 2:
            return route
            
        # Create distance matrix
        distances = {}
        for i in range(n):
            for j in range(n):
                if i != j:
                    path, dist = self.network.dijkstra(route[i], route[j])
                    distances[(route[i], route[j])] = dist
                    
        # Use nearest neighbor algorithm with demand consideration
        unvisited = set(route[1:])  # Exclude first stop
        current = route[0]
        optimized_route = [current]
        
        while unvisited:
            best_next = None
            best_score = float('inf')
            
            for next_stop in unvisited:
                # Score based on distance and demand
                distance = distances[(current, next_stop)]
                demand = demand_data.get(next_stop, 0)
                score = distance / (demand + 1)  # Lower score is better
                
                if score < best_score:
                    best_score = score
                    best_next = next_stop
                    
            if best_next is None:
                break
                
            optimized_route.append(best_next)
            unvisited.remove(best_next)
            current = best_next
            
        return optimized_route
    
    def calculate_route_metrics(self, route: List[int], demand_data: Dict[int, int]) -> Dict:
        """Calculate various metrics for a transit route"""
        total_distance = 0
        total_demand = 0
        max_demand = 0
        demand_stops = []
        
        # Calculate route metrics
        for i in range(len(route) - 1):
            path, dist = self.network.dijkstra(route[i], route[i + 1])
            total_distance += dist
            
        for stop in route:
            demand = demand_data.get(stop, 0)
            total_demand += demand
            if demand > max_demand:
                max_demand = demand
                demand_stops = [stop]
            elif demand == max_demand:
                demand_stops.append(stop)
                
        return {
            'total_distance': total_distance,
            'total_demand': total_demand,
            'max_demand': max_demand,
            'demand_stops': demand_stops,
            'avg_demand': total_demand / len(route) if route else 0,
            'efficiency_score': total_demand / total_distance if total_distance > 0 else 0
        } 