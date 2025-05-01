from data.raw_data_parser import TransportationNetwork
from algorithms.mst_network import MSTNetworkDesigner
from algorithms.shortest_path import TrafficOptimizer
from algorithms.emergency_routing import EmergencyRouter
from algorithms.transit_optimization import TransitOptimizer
from visualization.network_visualizer import NetworkVisualizer
from visualization.interactive_visualizer import show_interactive_route_planner
import argparse
import json
from typing import Dict, List, Tuple
import os

def load_config(config_file: str) -> Dict:
    """Load configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Cairo Transportation Optimization System')
    parser.add_argument('--config', type=str, default='config.json',
                      help='Path to configuration file')
    parser.add_argument('--mode', type=str, 
                      choices=['mst', 'traffic', 'emergency', 'transit', 'all', 'interactive'],
                      default='all', help='Operation mode')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize network
    network = TransportationNetwork()
    network.load_network_data(
        node_file=os.path.join(os.path.dirname(__file__), config['data_files']['nodes']),
        road_file=os.path.join(os.path.dirname(__file__), config['data_files']['roads']),
        facility_file=os.path.join(os.path.dirname(__file__), config['data_files']['facilities']),
        traffic_file=os.path.join(os.path.dirname(__file__), config['data_files']['traffic'])
    )
    
    # Check for interactive mode first
    if args.mode == 'interactive':
        print("\n=== Interactive Route Planner ===")
        print("Loading interactive visualization...")
        show_interactive_route_planner(network)
        return
    
    # Initialize visualizer
    visualizer = NetworkVisualizer(network)
    
    # Run selected mode
    if args.mode in ['mst', 'all']:
        print("\n=== Infrastructure Network Design ===")
        mst_designer = MSTNetworkDesigner(network)
        mst_edges = mst_designer.kruskals_algorithm()
        stats = mst_designer.get_network_statistics(mst_edges)
        print(f"Proposed MST network with {stats['edge_count']} connections")
        print(f"Total distance: {stats['total_distance']:.2f} km")
        print(f"Population served: {stats['total_population_served']}")
        print(f"Facility connections: {stats['facility_connections']}")
        
        visualizer.draw_network(mst_edges=[(u,v) for u,v,_ in mst_edges],
                              title="Proposed Infrastructure Network")
        
    if args.mode in ['traffic', 'all']:
        print("\n=== Traffic Flow Optimization ===")
        traffic_optimizer = TrafficOptimizer(network)
        
        # Example route optimization
        start_node = config['example_routes']['start']
        end_node = config['example_routes']['end']
        time_of_day = config['example_routes']['time_of_day']
        
        path, distance = traffic_optimizer.dijkstra(start_node, end_node, time_of_day)
        print(f"Optimal route from {start_node} to {end_node} ({time_of_day}):")
        print(f"Path: {path}")
        print(f"Distance: {distance:.2f} km")
        
        # Get alternative routes
        alternatives = traffic_optimizer.get_alternative_routes(start_node, end_node, time_of_day)
        print("\nAlternative routes:")
        for i, (alt_path, alt_dist) in enumerate(alternatives, 1):
            print(f"Option {i}: {alt_path} (Distance: {alt_dist:.2f} km)")
            
        visualizer.draw_network(highlight_path=path,
                              title=f"Optimal Route - {time_of_day}")
        
    if args.mode in ['emergency', 'all']:
        print("\n=== Emergency Response Planning ===")
        emergency_router = EmergencyRouter(network)
        
        # Example emergency routing
        emergency_location = config['emergency_routes']['location']
        facility_type = config['emergency_routes']['facility_type']
        
        facility, path, distance = emergency_router.find_nearest_emergency_facility(
            emergency_location, facility_type)
            
        if facility:
            print(f"Nearest {facility_type} to location {emergency_location}:")
            print(f"Facility ID: {facility}")
            print(f"Route: {path}")
            print(f"Distance: {distance:.2f} km")
            
            response_time = emergency_router.get_emergency_response_time(
                emergency_location, facility)
            print(f"Estimated response time: {response_time['estimated_time']:.1f} minutes")
            
            visualizer.draw_emergency_routes([emergency_location], facility_type)
            
    if args.mode in ['transit', 'all']:
        print("\n=== Public Transit Optimization ===")
        transit_optimizer = TransitOptimizer(network)
        
        # Example transit optimization
        route = config['transit_routes']['example_route']
        demand_data = config['transit_routes']['demand_data']
        
        # Optimize route frequency
        freq_stats = transit_optimizer.optimize_route_frequency(route, demand_data)
        print("\nRoute frequency optimization:")
        print(f"Base frequency: {freq_stats['base_frequency']:.1f} buses/hour")
        print(f"Peak frequency: {freq_stats['peak_frequency']:.1f} buses/hour")
        print(f"Off-peak frequency: {freq_stats['off_peak_frequency']:.1f} buses/hour")
        
        # Optimize stop sequence
        optimized_route = transit_optimizer.optimize_stop_sequence(route, demand_data)
        print("\nOptimized stop sequence:")
        print(f"Original: {route}")
        print(f"Optimized: {optimized_route}")
        
        # Calculate route metrics
        metrics = transit_optimizer.calculate_route_metrics(optimized_route, demand_data)
        print("\nRoute metrics:")
        print(f"Total distance: {metrics['total_distance']:.2f} km")
        print(f"Total demand: {metrics['total_demand']} passengers")
        print(f"Average demand: {metrics['avg_demand']:.1f} passengers/stop")
        print(f"Efficiency score: {metrics['efficiency_score']:.2f}")
        
        visualizer.draw_transit_routes({0: optimized_route}, demand_data)
        
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main() 