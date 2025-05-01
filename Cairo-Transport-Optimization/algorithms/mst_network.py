from typing import Dict, List, Tuple
import heapq

class MSTNetworkDesigner:
    def __init__(self, network):
        self.network = network
        
    def kruskals_algorithm(self, prioritize_population=True, include_facilities=True) -> List[Tuple[int, int, float]]:
        """Modified Kruskal's algorithm for road network design"""
        edges = []
        
        # Convert all edges to a list with modified weights
        for (u, v), data in self.network.edges.items():
            weight = data['distance']
            
            # Apply modifications based on requirements
            if prioritize_population:
                pop_u = self.network.nodes[u].get('population', 0)
                pop_v = self.network.nodes[v].get('population', 0)
                weight /= (pop_u + pop_v + 1)  # Favor high-population connections
                
            if include_facilities and ('facility' in self.network.nodes[u].get('type', '') or 
                                      'facility' in self.network.nodes[v].get('type', '')):
                weight *= 0.7  # Prioritize facility connections
                
            edges.append((weight, u, v))
        
        # Sort edges by modified weight
        edges.sort()
        
        # Initialize disjoint set data structure
        parent = {node: node for node in self.network.nodes}
        rank = {node: 0 for node in self.network.nodes}
        
        def find(u):
            """Find the root of the set containing u"""
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]
            
        def union(u, v):
            """Union the sets containing u and v"""
            u_root = find(u)
            v_root = find(v)
            
            if u_root == v_root:
                return False
                
            if rank[u_root] < rank[v_root]:
                parent[u_root] = v_root
            elif rank[u_root] > rank[v_root]:
                parent[v_root] = u_root
            else:
                parent[v_root] = u_root
                rank[u_root] += 1
            return True
                
        # Build MST
        mst_edges = []
        for weight, u, v in edges:
            if union(u, v):
                mst_edges.append((u, v, weight))
                
        return mst_edges
    
    def evaluate_network_cost(self, mst_edges: List[Tuple[int, int, float]]) -> Dict:
        """Evaluate the cost and characteristics of the proposed network"""
        total_distance = sum(weight for _, _, weight in mst_edges)
        total_population = 0
        facility_connections = 0
        
        # Calculate additional metrics
        for u, v, _ in mst_edges:
            total_population += (self.network.nodes[u].get('population', 0) + 
                               self.network.nodes[v].get('population', 0))
            
            if ('facility' in self.network.nodes[u].get('type', '') or 
                'facility' in self.network.nodes[v].get('type', '')):
                facility_connections += 1
                
        return {
            'total_distance': total_distance,
            'total_population_served': total_population,
            'facility_connections': facility_connections,
            'edge_count': len(mst_edges)
        }
    
    def get_network_statistics(self, mst_edges: List[Tuple[int, int, float]]) -> Dict:
        """Get detailed statistics about the proposed network"""
        stats = self.evaluate_network_cost(mst_edges)
        
        # Calculate average edge weight
        stats['average_edge_weight'] = stats['total_distance'] / stats['edge_count'] if stats['edge_count'] > 0 else 0
        
        # Calculate population density
        total_area = 0  # This would need to be calculated based on node coordinates
        stats['population_density'] = stats['total_population_served'] / total_area if total_area > 0 else 0
        
        return stats 