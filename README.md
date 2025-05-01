# Cairo Transportation Optimization System

A comprehensive system for optimizing transportation networks in Cairo, Egypt. This project provides tools for route planning, traffic optimization, emergency routing, and public transit optimization.

## Features

- Interactive route planning with real-time traffic considerations
- Emergency vehicle routing optimization
- Public transit system optimization
- Traffic flow analysis and optimization
- Minimum spanning tree network design
- Visualization tools for network analysis

## Project Structure

### Core Components

- `main.py`: Main entry point for the application
- `config.json`: Configuration file for data paths and parameters

### Data Management (`data/`)
- `raw_data_parser.py`: Parses and processes raw transportation data
  - `load_network_data()`: Loads and processes network data from CSV files
  - `parse_node_data()`: Processes node (location) data
  - `parse_edge_data()`: Processes road/edge data
  - `parse_facility_data()`: Processes facility (hospitals, schools, etc.) data
  - `parse_traffic_data()`: Processes traffic pattern data

### Algorithms (`algorithms/`)
- `shortest_path.py`: Traffic-aware shortest path algorithms
  - `dijkstra()`: Finds shortest path considering traffic conditions
  - `get_alternative_routes()`: Generates alternative routes
  - `calculate_travel_time()`: Estimates travel time with traffic

- `emergency_routing.py`: Emergency vehicle routing
  - `a_star_search()`: A* algorithm for emergency routing
  - `find_nearest_emergency_facility()`: Locates nearest emergency facility
  - `get_emergency_response_time()`: Calculates emergency response time

- `transit_optimization.py`: Public transit optimization
  - `optimize_route_frequency()`: Optimizes bus frequencies
  - `optimize_stop_sequence()`: Optimizes bus stop sequence
  - `calculate_route_metrics()`: Evaluates transit route performance

- `mst_network.py`: Network infrastructure design
  - `kruskals_algorithm()`: Implements Kruskal's algorithm for MST
  - `get_network_statistics()`: Analyzes network metrics

### Visualization (`visualization/`)
- `network_visualizer.py`: Static network visualization
  - `draw_network()`: Draws the transportation network
  - `draw_emergency_routes()`: Visualizes emergency routes
  - `draw_transit_routes()`: Shows transit routes
  - `highlight_path()`: Highlights specific paths

- `interactive_visualizer.py`: Interactive route planning interface
  - `show_interactive_route_planner()`: Launches interactive planner
  - `_draw_base_map()`: Draws Cairo base map
  - `_draw_network()`: Renders transportation network
  - `_add_widgets()`: Adds interactive controls
  - `_calculate_route()`: Computes optimal routes
  - `_draw_route()`: Visualizes calculated routes

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python main.py --mode [mst|traffic|emergency|transit|all|interactive]
```

Modes:
- `mst`: Infrastructure network design
- `traffic`: Traffic flow optimization
- `emergency`: Emergency response planning
- `transit`: Public transit optimization
- `all`: Run all optimizations
- `interactive`: Launch interactive route planner

## Data Files

The system uses several CSV files for data:
- `neighborhoods.csv`: District information
- `roads.csv`: Road network data
- `facilities.csv`: Facility locations
- `traffic.csv`: Traffic pattern data

## Dependencies

- Python 3.8+
- NetworkX
- Matplotlib
- Pandas
- NumPy

## License

This project is licensed under the MIT License - see the LICENSE file for details. 