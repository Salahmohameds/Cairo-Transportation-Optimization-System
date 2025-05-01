import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import List, Tuple, Dict, Optional
from algorithms.emergency_routing import EmergencyRouter
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.collections import LineCollection

class NetworkVisualizer:
    def __init__(self, network):
        self.network = network
        self.graph = nx.Graph()
        
        # Define color schemes
        self.node_type_colors = {
            'residential': 'skyblue',
            'business': 'orange',
            'commercial': 'orange',
            'mixed': 'limegreen',
            'medical': 'red',
            'education': 'purple',
            'government': 'brown',
            'airport': 'yellow',
            'transit_hub': 'yellow',
            'industrial': 'darkgray',
            'sports': 'pink',
            'tourism': 'gold'
        }
        
        # Define node shapes by type
        self.node_type_shapes = {
            'residential': 'o',  # circle
            'business': 's',     # square
            'commercial': 's',   # square
            'mixed': 'o',        # circle
            'medical': 'h',      # hexagon
            'education': 'p',    # pentagon
            'government': 'd',   # diamond
            'airport': '*',      # star
            'transit_hub': '*',  # star
            'industrial': 'v',   # triangle down
            'sports': 'P',       # plus
            'tourism': '^'       # triangle up
        }
        
        # Add nodes and edges to the graph
        for node_id, data in self.network.nodes.items():
            # Create a label for the node
            if node_id > 100:  # This is a facility node
                facility_id = f"F{node_id-100}"
                # Find facility name if available
                facility_name = None
                for fid, fdata in self.network.facilities.items():
                    if fdata.get('node_id') == node_id:
                        facility_name = fdata.get('name')
                        break
                label = facility_name if facility_name else facility_id
            else:
                # Look up district names based on node ID (this is a simple example)
                district_names = {
                    1: "Maadi", 2: "Nasr City", 3: "Downtown", 4: "New Cairo", 
                    5: "Heliopolis", 6: "Zamalek", 7: "6th October", 8: "Giza",
                    9: "Mohandessin", 10: "Dokki", 11: "Shubra", 12: "Helwan",
                    13: "New Capital", 14: "Al Rehab", 15: "Sheikh Zayed"
                }
                label = district_names.get(node_id, str(node_id))
                
            self.graph.add_node(node_id, 
                pos=(data['longitude'], data['latitude']), 
                type=data['type'],
                population=data.get('population', 0),
                label=label,
                shape=self.node_type_shapes.get(data['type'], 'o'))
            
        for (u, v), data in self.network.edges.items():
            # Only add each edge once since networkx treats edges as undirected
            if (v, u) not in self.graph.edges:
                self.graph.add_edge(u, v, 
                    weight=data['distance'],
                    speed_limit=data['speed_limit'],
                    lanes=data['lanes'],
                    travel_time=data['distance'] / (data['speed_limit'] / 60))  # minutes
    
    def draw_network(self, highlight_path: Optional[List[int]] = None,
                    mst_edges: Optional[List[Tuple[int, int]]] = None,
                    node_colors: Optional[Dict[int, str]] = None,
                    edge_colors: Optional[Dict[Tuple[int, int], str]] = None,
                    title: str = "Cairo Transportation Network"):
        """Draw the network with optional highlighting"""
        fig, ax = plt.subplots(figsize=(16, 12))
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Draw Egypt background with subtle coloring
        lower_left = (30.85, 29.80)  # SW corner
        upper_right = (31.9, 30.15)  # NE corner
        # Create a light beige background for the area
        rect = plt.Rectangle(lower_left, 
                           upper_right[0] - lower_left[0], 
                           upper_right[1] - lower_left[1], 
                           facecolor='#F5F5DC', alpha=0.3, zorder=0)
        ax.add_patch(rect)
        
        # Draw the Nile River
        # Simplified Nile coordinates through Cairo
        nile_x = [31.22, 31.23, 31.24, 31.25, 31.27, 31.28, 31.255, 31.25, 31.24, 31.22, 31.20, 31.18]
        nile_y = [29.85, 29.90, 29.95, 30.00, 30.05, 30.10, 30.15, 30.20, 30.25, 30.30, 30.35, 30.40]
        plt.plot(nile_x, nile_y, color='#64B5F6', linewidth=8, alpha=0.7, zorder=1)
        
        # Prepare node colors based on type if not provided
        if not node_colors:
            node_colors = {}
            for node_id, data in self.graph.nodes(data=True):
                node_type = data.get('type', '')
                for type_key in self.node_type_colors:
                    if type_key in node_type:
                        node_colors[node_id] = self.node_type_colors[type_key]
                        break
                else:
                    node_colors[node_id] = 'lightblue'  # Default
        
        # Draw edges with thickness based on number of lanes
        if not edge_colors:
            edge_colors = {}
            edge_widths = {}
            
            for u, v, data in self.graph.edges(data=True):
                # Default width based on lanes
                edge_widths[(u, v)] = data.get('lanes', 2) * 0.5
                
                # Default color based on speed limit
                speed = data.get('speed_limit', 60)
                if speed >= 80:
                    edge_colors[(u, v)] = '#4CAF50'  # Green for highways
                elif speed >= 60:
                    edge_colors[(u, v)] = '#9E9E9E'  # Gray for major roads
                else:
                    edge_colors[(u, v)] = '#BDBDBD'  # Light gray for smaller roads
                    
            # Draw all edges
            for (u, v) in self.graph.edges():
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                       color=edge_colors.get((u, v), '#BDBDBD'),
                       linewidth=edge_widths.get((u, v), 1),
                       alpha=0.6, zorder=2)
        else:
            # Use provided edge colors
            for (u, v) in self.graph.edges():
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                       color=edge_colors.get((u, v), 'lightgray'),
                       linewidth=1.5, alpha=0.6, zorder=2)
            
        # Highlight MST edges if provided
        if mst_edges:
            for u, v in mst_edges:
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                       color='green', linewidth=3, alpha=0.8, zorder=3)
        
        # Highlight path if provided
        if highlight_path:
            path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
            for u, v in path_edges:
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                       color='red', linewidth=4, alpha=0.8, zorder=4)
        
        # Draw nodes with size based on population and shape based on type
        node_sizes = []
        node_shapes = nx.get_node_attributes(self.graph, 'shape')
        
        # Group nodes by shape for efficient plotting
        shape_groups = {}
        for node in self.graph.nodes():
            shape = node_shapes.get(node, 'o')
            if shape not in shape_groups:
                shape_groups[shape] = []
            shape_groups[shape].append(node)
        
        # Draw each shape group separately
        for shape, nodes in shape_groups.items():
            node_list = []
            color_list = []
            size_list = []
            
            for node in nodes:
                node_list.append(node)
                color_list.append(node_colors.get(node, 'lightblue'))
                
                pop = self.graph.nodes[node].get('population', 0)
                # Scale node size based on population
                if pop == 0:
                    size_list.append(150)  # Facility node
                else:
                    # Scale population to reasonable node size
                    size_list.append(100 + min(400, pop // 1000))
            
            # Extract node positions for this group
            pos_list = [pos[node] for node in node_list]
            x = [p[0] for p in pos_list]
            y = [p[1] for p in pos_list]
            
            # Plot this shape group
            ax.scatter(x, y, s=size_list, c=color_list, marker=shape, 
                      edgecolor='black', linewidth=0.5, alpha=0.8, zorder=5)
        
        # Add labels with adjusted positioning and improved visibility
        for node_id, (x, y) in pos.items():
            label = self.graph.nodes[node_id].get('label', str(node_id))
            # Adjust label position based on node type
            if node_id > 100:  # Facility
                y_offset = -0.01  # Place below
            else:
                y_offset = 0.01   # Place above
            
            # Create a text box with white background for better visibility
            ax.text(x, y + y_offset, label, fontsize=9, 
                  ha='center', va='center', 
                  bbox=dict(boxstyle="round,pad=0.3", 
                          fc='white', ec="gray", alpha=0.8),
                  zorder=6)
        
        # Add legend for node types
        legend_elements = []
        for node_type, color in self.node_type_colors.items():
            shape = self.node_type_shapes.get(node_type, 'o')
            legend_elements.append(
                plt.Line2D([0], [0], marker=shape, color='w', 
                         markerfacecolor=color, markersize=10, 
                         label=node_type.capitalize())
            )
        ax.legend(handles=legend_elements, loc='upper right', 
                title='Area Types', framealpha=0.9)
        
        plt.title(title, fontsize=14)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
    
    def draw_traffic_heatmap(self, time_of_day: str):
        """Draw traffic heatmap based on time of day"""
        fig, ax = plt.subplots(figsize=(16, 12))
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Draw Egypt background
        lower_left = (30.85, 29.80)
        upper_right = (31.9, 30.15)
        rect = plt.Rectangle(lower_left, 
                           upper_right[0] - lower_left[0], 
                           upper_right[1] - lower_left[1], 
                           facecolor='#F5F5DC', alpha=0.3, zorder=0)
        ax.add_patch(rect)
        
        # Draw the Nile River
        nile_x = [31.22, 31.23, 31.24, 31.25, 31.27, 31.28, 31.255, 31.25, 31.24, 31.22, 31.20, 31.18]
        nile_y = [29.85, 29.90, 29.95, 30.00, 30.05, 30.10, 30.15, 30.20, 30.25, 30.30, 30.35, 30.40]
        plt.plot(nile_x, nile_y, color='#64B5F6', linewidth=8, alpha=0.7, zorder=1)
        
        # Create colormap for traffic intensity
        traffic_cmap = plt.cm.get_cmap('RdYlGn_r')  # Red for high traffic, green for low
        
        # Find max traffic value
        max_traffic = 0
        for (u, v), traffic in self.network.traffic_patterns.items():
            if time_of_day in traffic and traffic[time_of_day] > max_traffic:
                max_traffic = traffic[time_of_day]
        
        # Create line segments with colors based on traffic
        segments = []
        colors = []
        line_widths = []
        
        for (u, v), data in self.network.edges.items():
            if (u, v) in self.network.traffic_patterns and time_of_day in self.network.traffic_patterns[(u, v)]:
                traffic_value = self.network.traffic_patterns[(u, v)][time_of_day]
                # Normalize traffic value
                normalized_traffic = traffic_value / max_traffic
                
                # Create segment
                segments.append([(pos[u][0], pos[u][1]), (pos[v][0], pos[v][1])])
                colors.append(normalized_traffic)
                
                # Width based on lanes
                line_widths.append(data.get('lanes', 2) * 0.8)
        
        # Create line collection
        line_segments = LineCollection(segments, 
                                      linewidths=line_widths,
                                      cmap=traffic_cmap, 
                                      zorder=2)
        line_segments.set_array(np.array(colors))
        ax.add_collection(line_segments)
        
        # Add colorbar
        cbar = plt.colorbar(line_segments, ax=ax)
        cbar.set_label('Traffic Congestion Level')
        
        # Draw nodes
        node_colors = {}
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('type', '')
            for type_key in self.node_type_colors:
                if type_key in node_type:
                    node_colors[node_id] = self.node_type_colors[type_key]
                    break
            else:
                node_colors[node_id] = 'lightblue'  # Default
        
        # Draw nodes using similar approach as in draw_network
        node_shapes = nx.get_node_attributes(self.graph, 'shape')
        shape_groups = {}
        for node in self.graph.nodes():
            shape = node_shapes.get(node, 'o')
            if shape not in shape_groups:
                shape_groups[shape] = []
            shape_groups[shape].append(node)
            
        for shape, nodes in shape_groups.items():
            node_list = []
            color_list = []
            size_list = []
            
            for node in nodes:
                node_list.append(node)
                color_list.append(node_colors.get(node, 'lightblue'))
                
                pop = self.graph.nodes[node].get('population', 0)
                if pop == 0:
                    size_list.append(150)  # Facility node
                else:
                    size_list.append(100 + min(400, pop // 1000))
            
            pos_list = [pos[node] for node in node_list]
            x = [p[0] for p in pos_list]
            y = [p[1] for p in pos_list]
            
            ax.scatter(x, y, s=size_list, c=color_list, marker=shape, 
                      edgecolor='black', linewidth=0.5, alpha=0.8, zorder=5)
        
        # Add labels
        for node_id, (x, y) in pos.items():
            label = self.graph.nodes[node_id].get('label', str(node_id))
            if node_id > 100:  # Facility
                y_offset = -0.01
            else:
                y_offset = 0.01
                
            ax.text(x, y + y_offset, label, fontsize=9, 
                  ha='center', va='center', 
                  bbox=dict(boxstyle="round,pad=0.3", 
                          fc='white', ec="gray", alpha=0.8),
                  zorder=6)
        
        plt.title(f"Traffic Congestion Map - {time_of_day.capitalize()}", fontsize=14)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
    
    def draw_population_density(self):
        """Draw population density heatmap"""
        fig, ax = plt.subplots(figsize=(16, 12))
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Draw Egypt background
        lower_left = (30.85, 29.80)
        upper_right = (31.9, 30.15)
        rect = plt.Rectangle(lower_left, 
                           upper_right[0] - lower_left[0], 
                           upper_right[1] - lower_left[1], 
                           facecolor='#F5F5DC', alpha=0.3, zorder=0)
        ax.add_patch(rect)
        
        # Draw the Nile River
        nile_x = [31.22, 31.23, 31.24, 31.25, 31.27, 31.28, 31.255, 31.25, 31.24, 31.22, 31.20, 31.18]
        nile_y = [29.85, 29.90, 29.95, 30.00, 30.05, 30.10, 30.15, 30.20, 30.25, 30.30, 30.35, 30.40]
        plt.plot(nile_x, nile_y, color='#64B5F6', linewidth=8, alpha=0.7, zorder=1)
        
        # Find max population for normalization
        max_population = max(node['population'] for node in self.network.nodes.values())
        
        # Draw edges first (as a background)
        for (u, v) in self.graph.edges():
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                   color='#CCCCCC', linewidth=1, alpha=0.4, zorder=2)
        
        # Create a colormap for population density
        pop_cmap = plt.cm.get_cmap('viridis')
        
        # Draw nodes with size and color based on population
        for node_id, data in self.network.nodes.items():
            pop = data.get('population', 0)
            if pop > 0:  # Only draw residential/populated areas
                # Calculate size and color based on population
                size = 100 + (pop / max_population) * 1000  # Scale for visibility
                
                # Normalize population value to 0-1 for colormap
                norm_pop = pop / max_population
                color = pop_cmap(norm_pop)
                
                # Draw node
                ax.scatter(pos[node_id][0], pos[node_id][1], 
                         s=size, c=[color], 
                         alpha=0.7, edgecolor='white', linewidth=0.5,
                         zorder=3)
                
                # Add population label to large nodes
                if pop > 100000:
                    ax.text(pos[node_id][0], pos[node_id][1],
                          f"{pop//1000}k", fontsize=8,
                          ha='center', va='center', color='white',
                          zorder=4)
        
        # Add labels for all nodes
        for node_id, (x, y) in pos.items():
            label = self.graph.nodes[node_id].get('label', str(node_id))
            if node_id > 100:  # Facility
                ax.text(x, y - 0.01, label, fontsize=9, 
                      ha='center', va='center', 
                      bbox=dict(boxstyle="round,pad=0.3", 
                              fc='white', ec="gray", alpha=0.8),
                      zorder=5)
            else:
                ax.text(x, y + 0.01, label, fontsize=9, 
                      ha='center', va='center', 
                      bbox=dict(boxstyle="round,pad=0.3", 
                              fc='white', ec="gray", alpha=0.8),
                      zorder=5)
        
        # Add colorbar for population
        norm = plt.Normalize(0, max_population)
        sm = plt.cm.ScalarMappable(cmap=pop_cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Population')
        
        # Add annotations to explain density clusters
        high_pop_areas = []
        for node_id, data in self.network.nodes.items():
            if data.get('population', 0) > 400000:
                high_pop_areas.append((node_id, data['population']))
        
        high_pop_areas.sort(key=lambda x: x[1], reverse=True)
        
        plt.title("Population Density Map of Cairo", fontsize=14)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
    
    def draw_emergency_routes(self, emergency_locations: List[int],
                            facility_type: str = 'medical'):
        """Draw emergency routes to facilities"""
        fig, ax = plt.subplots(figsize=(16, 12))
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Draw Egypt background
        lower_left = (30.85, 29.80)
        upper_right = (31.9, 30.15)
        rect = plt.Rectangle(lower_left, 
                           upper_right[0] - lower_left[0], 
                           upper_right[1] - lower_left[1], 
                           facecolor='#F5F5DC', alpha=0.3, zorder=0)
        ax.add_patch(rect)
        
        # Draw the Nile River
        nile_x = [31.22, 31.23, 31.24, 31.25, 31.27, 31.28, 31.255, 31.25, 31.24, 31.22, 31.20, 31.18]
        nile_y = [29.85, 29.90, 29.95, 30.00, 30.05, 30.10, 30.15, 30.20, 30.25, 30.30, 30.35, 30.40]
        plt.plot(nile_x, nile_y, color='#64B5F6', linewidth=8, alpha=0.7, zorder=1)
        
        # Create emergency router
        emergency_router = EmergencyRouter(self.network)
        
        # Prepare node colors
        node_colors = {}
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('type', '')
            for type_key in self.node_type_colors:
                if type_key in node_type:
                    node_colors[node_id] = self.node_type_colors[type_key]
                    break
            else:
                node_colors[node_id] = 'lightblue'  # Default
        
        # Draw all edges as background
        for (u, v) in self.graph.edges():
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                   color='#CCCCCC', linewidth=1, alpha=0.4, zorder=2)
        
        # Get facilities
        facilities = []
        for node_id, data in self.network.nodes.items():
            if facility_type in data['type']:
                facilities.append(node_id)
                node_colors[node_id] = 'green'
                
        if not facilities:
            print(f"No {facility_type} facilities found in network.")
            return
            
        # Color emergency locations
        for loc in emergency_locations:
            node_colors[loc] = 'red'
            
        # Draw routes from each emergency location to nearest facility
        all_route_edges = []
        route_distances = {}
        route_times = {}
        
        for loc in emergency_locations:
            facility, path, distance = emergency_router.find_nearest_emergency_facility(
                loc, facility_type)
                
            if path and len(path) > 1:
                # Draw route path with gradient color (yellow to red indicates direction)
                num_segments = len(path) - 1
                
                for i in range(num_segments):
                    u, v = path[i], path[i+1]
                    # Calculate position along the route for gradient coloring
                    ratio = i / max(1, num_segments - 1)
                    # Yellow to red gradient
                    r = min(1, 0.8 + ratio * 0.2)
                    g = max(0, 0.8 - ratio * 0.8)
                    b = 0
                    color = (r, g, b)
                    
                    # Draw route segment
                    ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                           color=color, linewidth=3+ratio, alpha=0.8, zorder=4)
                    
                    all_route_edges.append((u, v))
                
                # Store route data for annotation
                route_distances[loc] = distance
                
                # Calculate estimated travel time (km / speed in km/h * 60 for minutes)
                avg_speed_km_h = 60  # assume 60 km/h average for emergency vehicles
                est_time_min = (distance / avg_speed_km_h) * 60
                route_times[loc] = est_time_min
                
                # Add distance label to the route
                mid_idx = len(path) // 2
                if mid_idx > 0:
                    u, v = path[mid_idx-1], path[mid_idx]
                    text_x = (pos[u][0] + pos[v][0]) / 2 + 0.01
                    text_y = (pos[u][1] + pos[v][1]) / 2 + 0.01
                    
                    ax.text(text_x, text_y, 
                          f"Distance: {distance:.1f} km\nTime: {est_time_min:.1f} min", 
                          bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.3'),
                          fontsize=9, ha='center', zorder=6)
                    
        # Draw nodes
        for node_id, (x, y) in pos.items():
            # Set node size
            if node_id in emergency_locations:
                size = 300  # Larger for emergency locations
                zorder = 7
                edgecolor = 'black'
                linewidth = 2
            elif node_id in facilities:
                size = 250  # Large for facilities
                zorder = 7
                edgecolor = 'black'
                linewidth = 2
            else:
                pop = self.graph.nodes[node_id].get('population', 0)
                if pop == 0:
                    size = 100  # Facility node
                else:
                    size = 80 + min(200, pop // 2000)
                zorder = 3
                edgecolor = 'gray'
                linewidth = 0.5
            
            # Get shape
            shape = self.graph.nodes[node_id].get('shape', 'o')
            
            # Draw the node
            ax.scatter(x, y, s=size, c=node_colors.get(node_id, 'lightblue'),
                     marker=shape, edgecolor=edgecolor, linewidth=linewidth,
                     alpha=0.8, zorder=zorder)
            
            # Add labels
            label = self.graph.nodes[node_id].get('label', str(node_id))
            if node_id > 100:  # Facility
                y_offset = -0.01
            else:
                y_offset = 0.01
            
            ax.text(x, y + y_offset, label, fontsize=9,
                  ha='center', va='center',
                  bbox=dict(boxstyle="round,pad=0.3", fc='white', ec="gray", alpha=0.8),
                  zorder=8)
        
        # Add emergency and facility type info in the title
        emer_loc_names = [self.graph.nodes[loc].get('label', str(loc)) for loc in emergency_locations]
        
        plt.title(f"Emergency Routes: {', '.join(emer_loc_names)} → {facility_type.title()} Facilities", 
                fontsize=14)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, 
                      label='Emergency Location'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10,
                      label=f'{facility_type.capitalize()} Facility'),
            plt.Line2D([0], [0], color='#ffa500', lw=3, label='Emergency Route')
        ]
        ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
        
        # Add summary info box
        if route_distances:
            info_text = "Emergency Routes Summary:\n"
            for i, loc in enumerate(emergency_locations):
                loc_name = self.graph.nodes[loc].get('label', str(loc))
                if loc in route_distances:
                    info_text += f"{loc_name}: {route_distances[loc]:.1f} km ({route_times[loc]:.1f} min)\n"
            
            # Add info box at bottom right
            props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
            ax.text(0.98, 0.02, info_text, transform=ax.transAxes, fontsize=10,
                  verticalalignment='bottom', horizontalalignment='right',
                  bbox=props, zorder=10)
        
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
    
    def draw_transit_routes(self, routes: Dict[int, List[int]],
                          demand_data: Dict[int, Dict[str, int]],
                          time_of_day: str = 'morning'):
        """Draw transit routes with demand-based coloring"""
        fig, ax = plt.subplots(figsize=(16, 12))
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Draw Egypt background
        lower_left = (30.85, 29.80)
        upper_right = (31.9, 30.15)
        rect = plt.Rectangle(lower_left, 
                           upper_right[0] - lower_left[0], 
                           upper_right[1] - lower_left[1], 
                           facecolor='#F5F5DC', alpha=0.3, zorder=0)
        ax.add_patch(rect)
        
        # Draw the Nile River
        nile_x = [31.22, 31.23, 31.24, 31.25, 31.27, 31.28, 31.255, 31.25, 31.24, 31.22, 31.20, 31.18]
        nile_y = [29.85, 29.90, 29.95, 30.00, 30.05, 30.10, 30.15, 30.20, 30.25, 30.30, 30.35, 30.40]
        plt.plot(nile_x, nile_y, color='#64B5F6', linewidth=8, alpha=0.7, zorder=1)
        
        # Draw base edges as background
        for u, v in self.graph.edges():
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                   color='#CCCCCC', linewidth=1, alpha=0.3, zorder=2)
            
        # Prepare node colors based on demand
        node_colors = {}
        node_demands = {}
        
        # Extract demand for the selected time of day
        for node_id, time_demands in demand_data.items():
            if isinstance(time_demands, dict) and time_of_day in time_demands:
                node_demands[node_id] = time_demands[time_of_day]
            elif isinstance(time_demands, (int, float)):
                # Handle case where demand is just a number
                node_demands[node_id] = time_demands
                
        if node_demands:
            max_demand = max(node_demands.values())
            demand_cmap = plt.cm.YlOrRd
            
            for node_id, demand in node_demands.items():
                if demand > 0:
                    # Normalize demand
                    norm_demand = demand / max_demand
                    node_colors[node_id] = demand_cmap(norm_demand)
        
        # Draw each transit route with a distinct color
        route_lines = []
        route_labels = []
        
        # Use a colorful palette for routes
        route_colors = [
            '#FF5722', '#4CAF50', '#2196F3', '#9C27B0', '#FFC107', 
            '#03A9F4', '#E91E63', '#8BC34A', '#9E9E9E', '#673AB7',
            '#CDDC39', '#795548', '#00BCD4', '#607D8B', '#F44336'
        ]
        
        # Draw each route
        for route_idx, (route_id, route) in enumerate(routes.items()):
            if len(route) < 2:
                continue
                
            # Get color for this route
            route_color = route_colors[route_idx % len(route_colors)]
            
            # Calculate average demand for this route
            route_demand = sum(node_demands.get(node, 0) for node in route) / len(route)
            
            # Scale linewidth by demand
            if node_demands:
                base_width = 2
                max_width = 8
                width = base_width + (route_demand / max(node_demands.values())) * (max_width - base_width)
            else:
                width = 3
                
            # Draw route segments
            for i in range(len(route) - 1):
                u, v = route[i], route[i+1]
                
                # Draw the route line
                line = ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                             color=route_color, linewidth=width, alpha=0.8, 
                             solid_capstyle='round', zorder=4,
                             label=f"Route {route_id}" if i == 0 else "")
                
                if i == 0:
                    route_lines.append(line[0])
                    route_labels.append(f"Route {route_id}")
                
                # Add mini "stop" markers at each node
                if i > 0 and i < len(route) - 1:
                    ax.scatter(pos[route[i]][0], pos[route[i]][1], 
                             s=width*10, color='white', edgecolor=route_color,
                             zorder=5)
            
            # Add arrow to show direction
            mid_idx = len(route) // 2
            if mid_idx > 0:
                u, v = route[mid_idx-1], route[mid_idx]
                dx = pos[v][0] - pos[u][0]
                dy = pos[v][1] - pos[u][1]
                # Normalize and scale for arrow
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    dx, dy = dx/length * 0.02, dy/length * 0.02
                    # Draw arrow
                    mid_x = (pos[v][0] + pos[u][0]) / 2
                    mid_y = (pos[v][1] + pos[u][1]) / 2
                    ax.arrow(mid_x-dx/2, mid_y-dy/2, dx, dy, 
                           head_width=0.01, head_length=0.01, 
                           fc=route_color, ec=route_color, zorder=6)
            
            # Add route label at the end
            if len(route) > 1:
                # Create a nicer label
                if isinstance(route_id, str) and route_id.startswith('M'):
                    label = f"Metro Line {route_id[1:]}"
                elif isinstance(route_id, str) and route_id.startswith('B'):
                    label = f"Bus Line {route_id[1:]}"
                else:
                    label = f"Route {route_id}"
                
                # Position text at start of route
                text_x = pos[route[0]][0] + 0.01
                text_y = pos[route[0]][1] + 0.01
                
                ax.text(text_x, text_y, label, 
                      fontsize=9, color=route_color, 
                      bbox=dict(facecolor='white', alpha=0.8, 
                              edgecolor=route_color, boxstyle='round,pad=0.2'),
                      zorder=7)
        
        # Draw nodes colored by demand if available
        for node_id, (x, y) in pos.items():
            demand = node_demands.get(node_id, 0)
            
            # Node appearance based on type and demand
            if node_id in node_demands:
                # High demand node - make it bigger
                size = 100 + (demand / max(node_demands.values())) * 300
                color = node_colors.get(node_id, 'orange')
                edge_color = 'black'
                linewidth = 1
                zorder = 8
            else:
                # Regular node
                pop = self.graph.nodes[node_id].get('population', 0)
                if pop == 0:
                    size = 80  # Facility node
                else:
                    size = 60 + min(150, pop // 3000)
                    
                # Use type-based color
                color = 'lightgray'  # Default color for non-demand nodes
                edge_color = 'gray'
                linewidth = 0.5
                zorder = 3
            
            # Draw the node with appropriate shape
            shape = self.graph.nodes[node_id].get('shape', 'o')
            ax.scatter(x, y, s=size, c=color, marker=shape,
                     edgecolor=edge_color, linewidth=linewidth,
                     alpha=0.8, zorder=zorder)
            
            # Add demand label to high-demand nodes
            if node_id in node_demands and demand >= 0.3 * max(node_demands.values()):
                ax.text(x, y, f"{demand}", fontsize=8,
                      ha='center', va='center', color='white',
                      bbox=dict(boxstyle="round,pad=0.2", 
                              fc='rgba(0,0,0,0.5)', ec=None),
                      zorder=9)
            
            # Add node label
            label = self.graph.nodes[node_id].get('label', str(node_id))
            y_offset = 0.01
            if node_id in node_demands:
                font_weight = 'bold'
            else:
                font_weight = 'normal'
                
            ax.text(x, y + y_offset, label, fontsize=8,
                  ha='center', va='center', weight=font_weight,
                  bbox=dict(boxstyle="round,pad=0.2", 
                          fc='white', ec="gray", alpha=0.8),
                  zorder=10)
        
        # Add a colorbar for demand
        if node_demands:
            norm = plt.Normalize(0, max(node_demands.values()))
            sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label(f'Passenger Demand ({time_of_day.capitalize()})')
        
        # Add custom legend for routes
        if route_lines:
            ax.legend(route_lines, route_labels, loc='upper right', 
                    framealpha=0.9, title="Transit Routes")
                
        plt.title(f"Cairo Transit Routes - {time_of_day.capitalize()} Demand", fontsize=14)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
    
    def save_visualization(self, filename: str):
        """Save the current visualization to a file"""
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close() 