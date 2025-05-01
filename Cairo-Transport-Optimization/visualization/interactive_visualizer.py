import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.patches as mpatches
from matplotlib.widgets import Button, RadioButtons
from algorithms.shortest_path import TrafficOptimizer

class InteractiveRouteVisualizer:
    def __init__(self, network, transit_optimizer=None):
        self.network = network
        self.traffic_optimizer = TrafficOptimizer(network)
        self.transit_optimizer = transit_optimizer
        
        # Initialize state variables
        self.source_node = None
        self.destination_node = None
        self.time_of_day = "morning"
        self.current_path = []
        self.distance = 0
        self.travel_time = 0
        self.selected_mode = "car"  # car, transit, emergency
        self.drawn_edges = set()  # Track drawn edges to prevent duplicates
        self.route_lines = []  # Store route visualization elements
        
        # Node information for display
        self.node_positions = {}
        self.node_labels = {}
        self.node_colors = {}
        self.node_sizes = {}
        self.node_shapes = {}
        
        # Color schemes
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
        
        # Node shapes by type
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
        
        # Extract node information from network
        self._prepare_node_information()
    
    def _prepare_node_information(self):
        """Prepare node positions, colors, sizes and labels"""
        # Extract data from network nodes
        for node_id, data in self.network.nodes.items():
            # Get node position
            self.node_positions[node_id] = (data['longitude'], data['latitude'])
            
            # Create label for node
            if node_id > 100:  # Facility node
                facility_id = f"F{node_id-100}"
                # Find facility name if available
                facility_name = None
                for fid, fdata in self.network.facilities.items():
                    if fdata.get('node_id') == node_id:
                        facility_name = fdata.get('name')
                        break
                self.node_labels[node_id] = facility_name if facility_name else facility_id
            else:
                # District names
                district_names = {
                    1: "Maadi", 2: "Nasr City", 3: "Downtown", 4: "New Cairo", 
                    5: "Heliopolis", 6: "Zamalek", 7: "6th October", 8: "Giza",
                    9: "Mohandessin", 10: "Dokki", 11: "Shubra", 12: "Helwan",
                    13: "New Capital", 14: "Al Rehab", 15: "Sheikh Zayed"
                }
                self.node_labels[node_id] = district_names.get(node_id, str(node_id))
            
            # Determine node color based on type
            node_type = data.get('type', '')
            for type_key in self.node_type_colors:
                if type_key in node_type:
                    self.node_colors[node_id] = self.node_type_colors[type_key]
                    break
            else:
                self.node_colors[node_id] = 'lightblue'  # Default color
            
            # Determine node shape based on type
            for type_key in self.node_type_shapes:
                if type_key in node_type:
                    self.node_shapes[node_id] = self.node_type_shapes[type_key]
                    break
            else:
                self.node_shapes[node_id] = 'o'  # Default shape
            
            # Determine node size based on population
            population = data.get('population', 0)
            if population == 0:  # Facility node
                self.node_sizes[node_id] = 100
            else:
                # Scale by population
                self.node_sizes[node_id] = 80 + min(300, population // 2000)
    
    def show_interactive_route_planner(self):
        """Show interactive route planner visualization"""
        plt.style.use('ggplot')
        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        self.fig.subplots_adjust(bottom=0.15, right=0.82, top=0.90)  # Make room for buttons and title
        
        # Add title and instructions
        self.fig.suptitle("Cairo Interactive Route Planner", fontsize=18, fontweight='bold')
        
        instructions = (
            "Instructions:\n"
            "1. Click on a starting point\n"
            "2. Click on a destination point\n"
            "3. Select time of day and transportation mode\n"
            "4. Click 'Calculate Route' to find the optimal path\n"
            "5. Use 'Reset' to start over"
        )
        
        # Add instructions text at the top
        self.fig.text(0.5, 0.95, instructions, 
                    fontsize=10, ha='center', va='top',
                    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Draw base map
        self._draw_base_map()
        
        # Draw nodes and edges
        self._draw_network()
        
        # Add control widgets
        self._add_widgets()
        
        # Add click event handler
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        # Add info panel for results
        self.info_text = self.ax.text(0.02, 0.02, "Click on nodes to select source and destination",
                                    transform=self.ax.transAxes, fontsize=12,
                                    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'),
                                    zorder=20)
        
        plt.title("Click on map to select locations", fontsize=14)
        self.fig.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout but leave room for title
        plt.show()
    
    def _draw_base_map(self):
        """Draw the base map of Cairo"""
        # Background rectangle
        lower_left = (30.85, 29.80)  # SW corner
        upper_right = (31.9, 30.15)  # NE corner
        rect = plt.Rectangle(lower_left, 
                           upper_right[0] - lower_left[0], 
                           upper_right[1] - lower_left[1], 
                           facecolor='#F5F5DC', alpha=0.3, zorder=0)
        self.ax.add_patch(rect)
        
        # Draw the Nile River
        nile_x = [31.22, 31.23, 31.24, 31.25, 31.27, 31.28, 31.255, 31.25, 31.24, 31.22, 31.20, 31.18]
        nile_y = [29.85, 29.90, 29.95, 30.00, 30.05, 30.10, 30.15, 30.20, 30.25, 30.30, 30.35, 30.40]
        self.ax.plot(nile_x, nile_y, color='#64B5F6', linewidth=8, alpha=0.7, zorder=1)
        
        # Set limits
        self.ax.set_xlim(lower_left[0], upper_right[0])
        self.ax.set_ylim(lower_left[1], upper_right[1])
        
        # Add grid
        self.ax.grid(True, alpha=0.3, linestyle='--')
    
    def _draw_network(self):
        """Draw the transportation network"""
        # Draw edges
        for (u, v), data in self.network.edges.items():
            if (v, u) not in self.drawn_edges:
                # Get positions
                x1, y1 = self.node_positions[u]
                x2, y2 = self.node_positions[v]
                
                # Determine line width based on lanes
                width = data.get('lanes', 2) * 0.3
                
                # Determine color based on speed limit
                speed = data.get('speed_limit', 60)
                if speed >= 80:
                    color = '#4CAF50'  # Green for highways
                elif speed >= 60:
                    color = '#9E9E9E'  # Gray for major roads
                else:
                    color = '#BDBDBD'  # Light gray for smaller roads
                
                # Draw edge
                self.ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, alpha=0.6, zorder=2)
                self.drawn_edges.add((u, v))
                self.drawn_edges.add((v, u))  # Mark both directions
        
        # Draw nodes by shape
        shape_groups = {}
        for node_id, shape in self.node_shapes.items():
            if shape not in shape_groups:
                shape_groups[shape] = []
            shape_groups[shape].append(node_id)
        
        for shape, nodes in shape_groups.items():
            x = [self.node_positions[n][0] for n in nodes]
            y = [self.node_positions[n][1] for n in nodes]
            colors = [self.node_colors[n] for n in nodes]
            sizes = [self.node_sizes[n] for n in nodes]
            
            self.ax.scatter(x, y, c=colors, s=sizes, marker=shape, 
                           edgecolor='black', linewidth=0.5, alpha=0.7, zorder=5,
                           picker=5)  # Make nodes pickable
        
        # Add node labels
        for node_id, (x, y) in self.node_positions.items():
            # Offset labels slightly above nodes
            y_offset = 0.01 if node_id <= 100 else -0.01
            
            self.ax.text(x, y + y_offset, self.node_labels[node_id], fontsize=8,
                        ha='center', va='center',
                        bbox=dict(boxstyle="round,pad=0.2", 
                                fc='white', ec="gray", alpha=0.8),
                        zorder=6)
    
    def _add_widgets(self):
        """Add interactive widgets to the figure"""
        # Time of day selector
        time_radio_ax = self.fig.add_axes([0.85, 0.65, 0.12, 0.2])
        self.time_radio = RadioButtons(time_radio_ax, 
                                      ('Morning', 'Afternoon', 'Evening', 'Night'),
                                      activecolor='blue')
        self.time_radio.on_clicked(self._time_selected)
        
        # Transport mode selector
        mode_radio_ax = self.fig.add_axes([0.85, 0.35, 0.12, 0.2])
        self.mode_radio = RadioButtons(mode_radio_ax, 
                                      ('Car', 'Transit', 'Emergency'),
                                      activecolor='blue')
        self.mode_radio.on_clicked(self._mode_selected)
        
        # Calculate route button
        calculate_button_ax = self.fig.add_axes([0.35, 0.05, 0.15, 0.05])
        self.calculate_button = Button(calculate_button_ax, 'Calculate Route', 
                                     color='lightblue', hovercolor='skyblue')
        self.calculate_button.on_clicked(self._calculate_route)
        
        # Reset button
        reset_button_ax = self.fig.add_axes([0.55, 0.05, 0.15, 0.05])
        self.reset_button = Button(reset_button_ax, 'Reset', 
                                 color='salmon', hovercolor='tomato')
        self.reset_button.on_clicked(self._reset)
        
        # Add legends
        self._add_legends()
    
    def _add_legends(self):
        """Add legends to the visualization"""
        # Legend for node types
        legend_elements = []
        for node_type, color in self.node_type_colors.items():
            shape = self.node_type_shapes.get(node_type, 'o')
            legend_elements.append(
                plt.Line2D([0], [0], marker=shape, color='w', 
                         markerfacecolor=color, markersize=10, 
                         label=node_type.capitalize())
            )
        
        # Add legend
        self.ax.legend(handles=legend_elements, loc='upper right', 
                      title='Area Types', framealpha=0.9)
    
    # Event handlers
    def _on_click(self, event):
        """Handle click events to select nodes"""
        if event.inaxes != self.ax:
            return
        
        # Find the closest node to the click
        min_dist = float('inf')
        closest_node = None
        
        for node_id, (x, y) in self.node_positions.items():
            dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if dist < min_dist and dist < 0.02:  # Threshold for clicking near a node
                min_dist = dist
                closest_node = node_id
        
        if closest_node is not None:
            # Update selection
            if self.source_node is None:
                # First select source
                self.source_node = closest_node
                self._update_visualization()
                self.info_text.set_text(f"Source: {self.node_labels[closest_node]}\nNow click on destination")
            elif self.destination_node is None and closest_node != self.source_node:
                # Then select destination
                self.destination_node = closest_node
                self._update_visualization()
                self.info_text.set_text(
                    f"Source: {self.node_labels[self.source_node]}\n"
                    f"Destination: {self.node_labels[closest_node]}\n"
                    f"Click 'Calculate Route' to find the optimal path"
                )
    
    def _time_selected(self, label):
        """Handle time of day selection"""
        time_map = {
            'Morning': 'morning',
            'Afternoon': 'afternoon',
            'Evening': 'evening',
            'Night': 'night'
        }
        self.time_of_day = time_map[label]
        
        # If we already have a calculated route, update it
        if self.current_path:
            self._calculate_route(None)
    
    def _mode_selected(self, label):
        """Handle transportation mode selection"""
        mode_map = {
            'Car': 'car',
            'Transit': 'transit',
            'Emergency': 'emergency'
        }
        self.selected_mode = mode_map[label]
        
        # If we already have a calculated route, update it
        if self.current_path:
            self._calculate_route(None)
    
    def _calculate_route(self, event):
        """Calculate the route based on selections"""
        if self.source_node is None or self.destination_node is None:
            self.info_text.set_text("Please select both source and destination points")
            return
        
        # Clear previous path
        self._clear_route()
        
        try:
            # Calculate path based on selected mode
            if self.selected_mode == 'car':
                self.current_path, self.distance = self.traffic_optimizer.dijkstra(
                    self.source_node, self.destination_node, self.time_of_day)
                
                # Calculate travel time based on road speed limits
                self.travel_time = 0
                for i in range(len(self.current_path) - 1):
                    u, v = self.current_path[i], self.current_path[i + 1]
                    # Get edge data
                    edge_data = self.network.edges.get((u, v))
                    if edge_data:
                        # Convert to minutes: distance (km) / speed (km/h) * 60
                        speed = edge_data.get('speed_limit', 60)
                        # Adjust speed based on congestion
                        if (u, v) in self.network.traffic_patterns and self.time_of_day in self.network.traffic_patterns[(u, v)]:
                            traffic_factor = self.network.traffic_patterns[(u, v)][self.time_of_day]
                            adjusted_speed = speed / traffic_factor
                        else:
                            adjusted_speed = speed
                        
                        segment_time = (edge_data['distance'] / adjusted_speed) * 60  # minutes
                        self.travel_time += segment_time
            
            elif self.selected_mode == 'emergency':
                # For emergency mode, import and use EmergencyRouter
                from algorithms.emergency_routing import EmergencyRouter
                emergency_router = EmergencyRouter(self.network)
                
                # Use A* search for emergency routing
                self.current_path, self.distance = emergency_router.a_star_search(
                    self.source_node, self.destination_node, self.time_of_day)
                
                # Calculate faster emergency travel time (20% faster than normal)
                self.travel_time = 0
                for i in range(len(self.current_path) - 1):
                    u, v = self.current_path[i], self.current_path[i + 1]
                    edge_data = self.network.edges.get((u, v))
                    if edge_data:
                        # Emergency vehicles get priority and move faster
                        speed = edge_data.get('speed_limit', 60) * 1.2  # 20% faster
                        segment_time = (edge_data['distance'] / speed) * 60  # minutes
                        self.travel_time += segment_time
            
            elif self.selected_mode == 'transit':
                # For transit mode, use simplified path with longer times
                self.current_path, self.distance = self.traffic_optimizer.dijkstra(
                    self.source_node, self.destination_node, self.time_of_day)
                
                # Transit is slower but follows similar routes
                self.travel_time = 0
                for i in range(len(self.current_path) - 1):
                    u, v = self.current_path[i], self.current_path[i + 1]
                    edge_data = self.network.edges.get((u, v))
                    if edge_data:
                        # Transit is typically slower with stops
                        transit_speed = edge_data.get('speed_limit', 60) * 0.6  # 60% of road speed
                        segment_time = (edge_data['distance'] / transit_speed) * 60  # minutes
                        # Add waiting time at stops
                        if i > 0 and i < len(self.current_path) - 1:  # Not first or last stop
                            segment_time += 3  # 3 minutes waiting at each stop
                        self.travel_time += segment_time
            
            # Draw the calculated route
            self._draw_route()
            
            # Update info text
            self.info_text.set_text(
                f"Route from {self.node_labels[self.source_node]} to {self.node_labels[self.destination_node]}\n"
                f"Time of day: {self.time_of_day.capitalize()}\n"
                f"Mode: {self.selected_mode.capitalize()}\n"
                f"Distance: {self.distance:.2f} km\n"
                f"Travel time: {self.travel_time:.1f} minutes"
            )
            
        except Exception as e:
            self.info_text.set_text(f"Error calculating route: {str(e)}")
        
        # Redraw
        self.fig.canvas.draw()
    
    def _reset(self, event):
        """Reset selections and route"""
        self.source_node = None
        self.destination_node = None
        self.current_path = []
        self.distance = 0
        self.travel_time = 0
        
        # Clear visualization
        self._clear_route()
        
        # Reset info text
        self.info_text.set_text("Click on nodes to select source and destination")
        
        # Redraw
        self.fig.canvas.draw()
    
    def _update_visualization(self):
        """Update visualization based on current selections"""
        # Clear previous route visualization
        self._clear_route()
        
        # Draw selected nodes
        if self.source_node is not None:
            x, y = self.node_positions[self.source_node]
            self.source_circle = plt.Circle((x, y), 0.01, color='green', 
                                          fill=True, alpha=0.7, zorder=10)
            self.ax.add_patch(self.source_circle)
        
        if self.destination_node is not None:
            x, y = self.node_positions[self.destination_node]
            self.dest_circle = plt.Circle((x, y), 0.01, color='red',
                                        fill=True, alpha=0.7, zorder=10)
            self.ax.add_patch(self.dest_circle)
        
        # Draw route if available
        if self.current_path:
            self._draw_route()
        
        # Redraw
        self.fig.canvas.draw()
    
    def _draw_route(self):
        """Draw the calculated route on the map"""
        if not self.current_path or len(self.current_path) < 2:
            return
        
        # Create path segments
        self.route_lines = []
        for i in range(len(self.current_path) - 1):
            u, v = self.current_path[i], self.current_path[i + 1]
            x1, y1 = self.node_positions[u]
            x2, y2 = self.node_positions[v]
            
            # Draw route segment with color based on mode
            if self.selected_mode == 'car':
                color = 'blue'
            elif self.selected_mode == 'transit':
                color = 'purple'
            else:  # emergency
                color = 'red'
                
            line, = self.ax.plot([x1, x2], [y1, y2], color=color, 
                               linewidth=4, alpha=0.8, zorder=8)
            self.route_lines.append(line)
            
            # Add distance labels to longer segments
            edge_data = self.network.edges.get((u, v))
            if edge_data and edge_data['distance'] > 5:  # Only show for segments > 5km
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                
                # Get segment specific info
                distance = edge_data['distance']
                if self.selected_mode == 'car':
                    speed = edge_data.get('speed_limit', 60)
                    if (u, v) in self.network.traffic_patterns and self.time_of_day in self.network.traffic_patterns[(u, v)]:
                        traffic_factor = self.network.traffic_patterns[(u, v)][self.time_of_day]
                        speed = speed / traffic_factor
                elif self.selected_mode == 'emergency':
                    speed = edge_data.get('speed_limit', 60) * 1.2
                else:  # transit
                    speed = edge_data.get('speed_limit', 60) * 0.6
                
                # Calculate time for this segment
                time = (distance / speed) * 60  # minutes
                
                text = self.ax.text(mid_x, mid_y, f"{distance:.1f}km\n{time:.1f}min",
                                  fontsize=8, ha='center', va='center',
                                  bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'),
                                  zorder=9)
                self.route_lines.append(text)
        
        # Draw origin/destination markers more prominently
        start = self.current_path[0]
        end = self.current_path[-1]
        
        # Mark start node
        x, y = self.node_positions[start]
        start_marker = self.ax.scatter(x, y, s=200, c='green', marker='o',
                                     edgecolor='white', linewidth=2, zorder=10)
        self.route_lines.append(start_marker)
        
        # Mark end node
        x, y = self.node_positions[end]
        end_marker = self.ax.scatter(x, y, s=200, c='red', marker='o',
                                   edgecolor='white', linewidth=2, zorder=10)
        self.route_lines.append(end_marker)
    
    def _clear_route(self):
        """Clear the currently displayed route"""
        # Remove route lines
        if hasattr(self, 'route_lines'):
            for line in self.route_lines:
                try:
                    line.remove()
                except:
                    pass
            self.route_lines = []
        
        # Remove source/destination circles
        if hasattr(self, 'source_circle') and self.source_circle is not None:
            self.source_circle.remove()
            self.source_circle = None
            
        if hasattr(self, 'dest_circle') and self.dest_circle is not None:
            self.dest_circle.remove()
            self.dest_circle = None
        
        # Redraw
        self.fig.canvas.draw_idle()


def show_interactive_route_planner(network):
    """Function to launch the interactive route planner"""
    visualizer = InteractiveRouteVisualizer(network)
    visualizer.show_interactive_route_planner() 