import networkx as nx
import folium
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import numpy as np
from algorithms.shortest_path import TrafficOptimizer
from algorithms.emergency_routing import EmergencyRouter

class RouteVisualizer:
    def __init__(self, network, traffic_optimizer=None, emergency_router=None):
        self.network = network
        self.traffic_optimizer = traffic_optimizer or TrafficOptimizer(network)
        self.emergency_router = emergency_router or EmergencyRouter(network)
        
        # Initialize map center (Cairo coordinates)
        self.map_center = [30.0444, 31.2357]
        self.zoom_start = 12
        
        # Color schemes
        self.route_colors = {
            'best': 'lightgreen',
            'alternate': 'blue',
            'emergency': 'red',
            'transit': 'purple'
        }
        
        # Line weights
        self.line_weights = {
            'best': 8,
            'alternate': 5,
            'emergency': 10,
            'transit': 6
        }
    
    def select_algorithm(self, scenario: str, time_of_day: str = "morning") -> str:
        """
        Choose the appropriate routing algorithm based on the scenario.
        
        Args:
            scenario: One of "emergency", "rush_hour", "transit", or "default"
            time_of_day: Time of day for traffic consideration
            
        Returns:
            str: Selected algorithm name
        """
        if scenario == "emergency":
            return "A*"
        elif scenario == "rush_hour" or time_of_day in ["morning", "evening"]:
            return "Dijkstra with dynamic weights"
        elif scenario == "transit":
            return "Transit-optimized Dijkstra"
        else:
            return "Dijkstra"
    
    def get_route(self, start: int, end: int, scenario: str = "default", 
                 time_of_day: str = "morning") -> Tuple[List[int], float]:
        """
        Calculate the optimal route using the selected algorithm.
        
        Args:
            start: Starting node ID
            end: Destination node ID
            scenario: Routing scenario
            time_of_day: Time of day for traffic consideration
            
        Returns:
            Tuple[List[int], float]: Path and total distance
        """
        algo = self.select_algorithm(scenario, time_of_day)
        
        if algo == "A*":
            path, distance = self.emergency_router.a_star_search(start, end, time_of_day)
        elif algo == "Dijkstra with dynamic weights":
            path, distance = self.traffic_optimizer.dijkstra(start, end, time_of_day)
        elif algo == "Transit-optimized Dijkstra":
            # Use transit-optimized weights
            path, distance = self.traffic_optimizer.dijkstra(start, end, time_of_day, 
                                                          transit_mode=True)
        else:
            path, distance = self.traffic_optimizer.dijkstra(start, end)
            
        return path, distance
    
    def get_alternate_routes(self, start: int, end: int, count: int = 2,
                           time_of_day: str = "morning") -> List[Tuple[List[int], float]]:
        """
        Generate alternate routes between start and end points.
        
        Args:
            start: Starting node ID
            end: Destination node ID
            count: Number of alternate routes to generate
            time_of_day: Time of day for traffic consideration
            
        Returns:
            List[Tuple[List[int], float]]: List of (path, distance) tuples
        """
        return self.traffic_optimizer.get_alternative_routes(start, end, time_of_day, count)
    
    def create_folium_map(self, start: int, end: int, scenario: str = "default",
                         time_of_day: str = "morning", show_alternates: bool = True) -> folium.Map:
        """
        Create an interactive Folium map showing the route and alternatives.
        
        Args:
            start: Starting node ID
            end: Destination node ID
            scenario: Routing scenario
            time_of_day: Time of day for traffic consideration
            show_alternates: Whether to show alternate routes
            
        Returns:
            folium.Map: Interactive map object
        """
        # Create base map
        m = folium.Map(location=self.map_center, zoom_start=self.zoom_start)
        
        # Get main route
        main_path, main_distance = self.get_route(start, end, scenario, time_of_day)
        
        # Plot main route
        route_points = [(self.network.nodes[n]['latitude'], 
                        self.network.nodes[n]['longitude']) for n in main_path]
        
        folium.PolyLine(
            route_points,
            color=self.route_colors['best'],
            weight=self.line_weights['best'],
            opacity=0.8,
            tooltip=f"Best Route ({self.select_algorithm(scenario, time_of_day)})"
        ).add_to(m)
        
        # Add start and end markers
        start_coords = (self.network.nodes[start]['latitude'], 
                       self.network.nodes[start]['longitude'])
        end_coords = (self.network.nodes[end]['latitude'], 
                     self.network.nodes[end]['longitude'])
        
        folium.Marker(
            start_coords,
            popup=f"Start: {self.network.nodes[start].get('name', f'Node {start}')}",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
        folium.Marker(
            end_coords,
            popup=f"End: {self.network.nodes[end].get('name', f'Node {end}')}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add alternate routes if requested
        if show_alternates:
            alternate_routes = self.get_alternate_routes(start, end, time_of_day=time_of_day)
            for i, (alt_path, alt_distance) in enumerate(alternate_routes, 1):
                alt_points = [(self.network.nodes[n]['latitude'], 
                             self.network.nodes[n]['longitude']) for n in alt_path]
                
                folium.PolyLine(
                    alt_points,
                    color=self.route_colors['alternate'],
                    weight=self.line_weights['alternate'],
                    opacity=0.5,
                    tooltip=f"Alternate {i} (Distance: {alt_distance:.2f} km)"
                ).add_to(m)
        
        return m
    
    def save_map(self, map_obj: folium.Map, filename: str = "route_map.html"):
        """
        Save the Folium map to an HTML file.
        
        Args:
            map_obj: Folium map object
            filename: Output filename
        """
        map_obj.save(filename)
    
    def plot_matplotlib(self, start: int, end: int, scenario: str = "default",
                       time_of_day: str = "morning", show_alternates: bool = True):
        """
        Create a static matplotlib plot of the route.
        
        Args:
            start: Starting node ID
            end: Destination node ID
            scenario: Routing scenario
            time_of_day: Time of day for traffic consideration
            show_alternates: Whether to show alternate routes
        """
        plt.figure(figsize=(12, 8))
        
        # Get main route
        main_path, main_distance = self.get_route(start, end, scenario, time_of_day)
        
        # Plot main route
        route_x = [self.network.nodes[n]['longitude'] for n in main_path]
        route_y = [self.network.nodes[n]['latitude'] for n in main_path]
        
        plt.plot(route_x, route_y, color=self.route_colors['best'], 
                linewidth=self.line_weights['best'], alpha=0.8,
                label=f"Best Route ({self.select_algorithm(scenario, time_of_day)})")
        
        # Plot alternate routes if requested
        if show_alternates:
            alternate_routes = self.get_alternate_routes(start, end, time_of_day=time_of_day)
            for i, (alt_path, alt_distance) in enumerate(alternate_routes, 1):
                alt_x = [self.network.nodes[n]['longitude'] for n in alt_path]
                alt_y = [self.network.nodes[n]['latitude'] for n in alt_path]
                
                plt.plot(alt_x, alt_y, color=self.route_colors['alternate'],
                        linewidth=self.line_weights['alternate'], alpha=0.5,
                        label=f"Alternate {i}")
        
        # Add start and end markers
        plt.scatter(self.network.nodes[start]['longitude'], 
                   self.network.nodes[start]['latitude'],
                   color='green', s=200, label='Start')
        plt.scatter(self.network.nodes[end]['longitude'],
                   self.network.nodes[end]['latitude'],
                   color='red', s=200, label='End')
        
        plt.title(f"Route from {self.network.nodes[start].get('name', f'Node {start}')} "
                 f"to {self.network.nodes[end].get('name', f'Node {end}')}")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt.gcf() 