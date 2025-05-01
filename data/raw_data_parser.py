import csv
from typing import Dict, List, Tuple
import pandas as pd

class TransportationNetwork:
    def __init__(self):
        self.nodes = {}  # {id: {name, type, x, y, population}}
        self.edges = {}  # {(from_id, to_id): {distance, capacity, condition}}
        self.traffic_patterns = {}  # {(from_id, to_id): {morning, afternoon, evening, night}}
        self.facilities = {}  # {id: {name, type, x, y}}
        self.public_transit = {}  # {line_id: {stops, vehicles, passengers}}

    def load_network_data(self, node_file: str, road_file: str, facility_file: str, traffic_file: str):
        """Load network data from CSV files"""
        try:
            # Load node data
            nodes_df = pd.read_csv(node_file)
            for _, row in nodes_df.iterrows():
                self.nodes[row['node_id']] = {
                    'type': row['type'],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'population': int(row['population'])
                }

            # Load road data (undirected edges)
            roads_df = pd.read_csv(road_file)
            for _, row in roads_df.iterrows():
                from_node = int(row['from_node'])
                to_node = int(row['to_node'])
                edge_data = {
                    'distance': float(row['distance']),
                    'speed_limit': int(row['speed_limit']),
                    'lanes': int(row['lanes'])
                }
                # Add edge in both directions
                self.edges[(from_node, to_node)] = edge_data.copy()
                self.edges[(to_node, from_node)] = edge_data.copy()

            # Load facility data
            facilities_df = pd.read_csv(facility_file)
            for _, row in facilities_df.iterrows():
                self.facilities[row['facility_id']] = {
                    'node_id': int(row['node_id']),
                    'type': row['type'],
                    'name': row['name'],
                    'capacity': int(row['capacity'])
                }

            # Load traffic pattern data (undirected)
            traffic_df = pd.read_csv(traffic_file)
            for _, row in traffic_df.iterrows():
                from_node = int(row['from_node'])
                to_node = int(row['to_node'])
                time = row['time_of_day']
                congestion = self._convert_congestion_level(row['congestion_level'])
                
                # Add traffic data in both directions
                if (from_node, to_node) not in self.traffic_patterns:
                    self.traffic_patterns[(from_node, to_node)] = {}
                if (to_node, from_node) not in self.traffic_patterns:
                    self.traffic_patterns[(to_node, from_node)] = {}
                    
                self.traffic_patterns[(from_node, to_node)][time] = congestion
                self.traffic_patterns[(to_node, from_node)][time] = congestion

        except Exception as e:
            print(f"Error loading network data: {str(e)}")
            raise

    def _convert_congestion_level(self, level: str) -> float:
        """Convert text congestion level to numeric factor"""
        levels = {
            'low': 0.5,
            'medium': 1.0,
            'high': 2.0
        }
        return levels.get(level.lower(), 1.0)

    def get_time_dependent_weight(self, from_id: int, to_id: int, time_of_day: str) -> float:
        """Calculate dynamic edge weight based on traffic patterns"""
        if (from_id, to_id) not in self.edges or (from_id, to_id) not in self.traffic_patterns:
            return float('inf')
            
        base_weight = self.edges[(from_id, to_id)]['distance']
        traffic_factor = self.traffic_patterns[(from_id, to_id)].get(time_of_day, 1.0)
        return base_weight * traffic_factor

    def get_node_neighbors(self, node_id: int) -> List[Tuple[int, Dict]]:
        """Get all neighbors of a node with their edge data"""
        neighbors = []
        for (u, v), data in self.edges.items():
            if u == node_id:
                neighbors.append((v, data))
            elif v == node_id:  # Assuming undirected graph
                neighbors.append((u, data))
        return neighbors

    def get_facility_nodes(self, facility_type: str = None) -> List[int]:
        """Get all nodes that are facilities of a specific type"""
        facility_nodes = []
        
        # First look in regular nodes for nodes with the specified type
        for node_id, data in self.nodes.items():
            if facility_type is None or facility_type in data['type']:
                facility_nodes.append(node_id)
                
        # Then check the facilities dictionary - this is for backward compatibility
        for facility_id, facility_data in self.facilities.items():
            if facility_type is None or facility_type == facility_data['type']:
                node_id = facility_data.get('node_id')
                if node_id and node_id not in facility_nodes:
                    facility_nodes.append(node_id)
                    
        return facility_nodes 