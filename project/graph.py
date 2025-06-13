import itertools
import os
import random

import folium
import geopandas as gpd
import igraph as ig
import numpy as np
import ujson
from edge import Edge
from node import Node
from shapely import concave_hull, union_all
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree


class Graph:
    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self._g = ig.Graph(directed=True)
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self._name2node: dict["str", Node] = {}  # Mapping from name to node

        # Fill the graph with the given nodes and edges
        self.add_vertices(nodes)
        self.add_edges(edges)

    # Functions for checking whether a Node/Edge is in the graph
    def contains_node(self, node: Node) -> bool:
        return node in self.nodes

    def contains_edge(self, edge: Edge) -> bool:
        return edge in self.edges

    # Function to add a vertex to the graph (we try to not use this since this is slow, adding in bulk is faster)
    def add_vertex(self, node: Node) -> None:
        if not self.contains_node(node):
            # We add it in igraph, and to our list of nodes and name to node mapping
            self._g.add_vertex(name=node.name)
            self.nodes.append(node)
            self._name2node[node.name] = node

    # Function to add the vertices in bulk
    def add_vertices(self, nodes: list[Node]) -> None:
        # List of the nodes not already in the graph
        new_nodes: list[Node] = [node for node in nodes if not self.contains_node(node)]

        if new_nodes:
            self._g.add_vertices(len(new_nodes))  # Add the new nodes to igraph
            # The new nodes are added at the end in igraph, so we can get the last nodes from the list of nodes
            # to give the correct names
            self._g.vs[-len(new_nodes) :]["name"] = [node.name for node in new_nodes]

            # Also add to the list of nodes and name to node mapping
            self.nodes.extend(new_nodes)
            for node in nodes:
                self._name2node[node.name] = node

    # Function to add an edge to the graph (we try to not use this since this is slow, adding in bulk is faster)
    def add_edge(self, edge: Edge) -> None:
        # First add the vertices of the edges (the check whether they are already in the graph happens in add_vertex)
        self.add_vertex(edge.start_node)
        self.add_vertex(edge.end_node)
        if not self.contains_edge(edge):
            self._g.add_edge(edge.start_node.name, edge.end_node.name)  # Add to igraph
            self._g.es[-1]["weight"] = (
                edge.weight
            )  # The last edge is the new one, also add the weight in igraph
            self.edges.append(edge)  # Add to list of edges

    # Function to add the edges in bulk
    def add_edges(self, edges: list[Edge]) -> None:
        new_nodes: dict[
            "str", Node
        ] = {}  # Mapping of name to node for the nodes not already in the graph
        # Find any nodes from the list of edges that are not already in the graph
        for edge in edges:
            if not self.contains_node(edge.start_node):
                new_nodes[edge.start_node.name] = edge.start_node
            if not self.contains_node(edge.end_node):
                new_nodes[edge.end_node.name] = edge.end_node

        # If any are found, add them
        if new_nodes:
            self.add_vertices(list(new_nodes.values()))

        new_edges: list[Edge] = [edge for edge in edges if not self.contains_edge(edge)]

        # If new edges are found, add them
        if new_edges:
            self._g.add_edges(
                [edge.start_node.name, edge.end_node.name] for edge in new_edges
            )
            self.edges.extend(new_edges)
            # The new edges are added at the end, so add the weights to the end of the list of edges
            self._g.es[-len(new_edges) :]["weight"] = [
                edge.weight for edge in new_edges
            ]

    def delete_edge(self, edge: Edge) -> None:
        if edge in self.edges:
            self.edges.remove(edge)
            # Remove from igraph as well, we need to filter by start node and end node index
            start: Node = edge.start_node
            end: Node = edge.end_node
            es_to_delete = self._g.es.select(
                _source=self.node2index(start),
                _target=self.node2index(end),
            )
            es_to_delete.delete()

    # Map igraph node index to node name
    def index2name(self, index: int) -> str:
        return self._g.vs[index]["name"]

    # Map node name to node
    def name2node(self, name: str) -> Node:
        return self._name2node[name]

    # Map igraph node index to node
    def index2node(self, index: int) -> Node:
        return self.name2node(self.index2name(index))

    # Map node to igraph index
    def node2index(self, node: Node) -> int:
        return self._g.vs.find(name=node.name).index

    # Find the average coordinates of a graph, to center the maps correctly
    def avg_coords(self) -> tuple[float, float]:
        all_lats = [float(node.lat) for node in self.nodes]
        all_lons = [float(node.lon) for node in self.nodes]
        return (float(np.mean(all_lats)), float(np.mean(all_lons)))

    # A bunch of functions that calculate some interesting features of the graph
    def total_edge_weight(self) -> float:
        return sum(edge.weight for edge in self.edges)

    def num_buildings(self) -> int:
        return len([node for node in self.nodes if node.is_building])

    def avg_edge_weight(self) -> float:
        return float(np.mean([edge.weight for edge in self.edges]))

    def avg_path_length(self) -> float:
        return self._g.average_path_length(weights="weight")

    def diameter(self) -> float:
        return self._g.diameter(weights="weight")

    def radius(self) -> float:
        return self._g.radius(weights="weight")

    def edge_connectivity(self) -> float:
        return self._g.edge_connectivity()

    def vertex_connectivity(self) -> float:
        return self._g.vertex_connectivity()

    def mincut_value(self) -> float:
        return self._g.mincut_value()

    def num_communities_infomap(self) -> float:
        return len(self._g.community_infomap())

    def num_communities_springlass(self) -> float:
        return len(self._g.community_spinglass())

    def modularity_infomap(self):
        return self._g.community_infomap().modularity

    def modularity_springlass(self):
        return self._g.community_springlass().modularity

    def mean_degree(self) -> float:
        return self._g.degree_distribution().mean

    def var_degree(self) -> float:
        return self._g.degree_distribution().var

    def max_degree(self) -> int:
        return self._g.degree_distribution()._max

    # We only want to have the largest connected component when making TSPs on this graph
    def largest_component(self) -> "Graph":
        subgraph = self._g.subgraph(
            max(self._g.components(), key=len)
        )  # Find the largest connected component
        # Then extract the nodes and edges from this subgraph
        nodes: list[Node] = [self.name2node(name) for name in subgraph.vs["name"]]
        edges: list[Edge] = [
            Edge(
                self.name2node(subgraph.vs[edge.source]["name"]),
                self.name2node(subgraph.vs[edge.target]["name"]),
            )
            for edge in subgraph.es
        ]
        return Graph(nodes, edges)  # Return the subgraph

    # We also need to connect the buildings to the graph
    def connect_buildings(self, building_nodes: list[Node]) -> "Graph":
        # Define some mappings we will need to find the closest edge to a building
        edge_to_linestring: dict[Edge, LineString] = {}
        linestrings: list[LineString] = []
        edge_map: dict[LineString, Edge] = {}
        new_nodes: list[Node] = []
        new_edges: list[Edge] = []

        # Load in the graph as a list of linestrings, to create a tree of this graph
        for edge in self.edges:
            start: Node = edge.start_node
            end: Node = edge.end_node
            line: LineString = LineString([(start.lat, start.lon), (end.lat, end.lon)])
            edge_to_linestring[edge] = line
            linestrings.append(line)
            edge_map[line] = edge

        tree: STRtree = STRtree(linestrings)  # Create the tree

        # Counter to see how many virtual nodes were added
        node_id_counter = itertools.count(
            start=max(
                int(n.name.split("_")[-1]) for n in self.nodes if "virtual" in n.name
            )
            + 1
            if any("virtual" in n.name for n in self.nodes)
            else 0
        )

        for building in building_nodes:
            building_point: Point = building.point_lat_lon()  # Convert to Point
            nearest_index: int = tree.nearest(
                building_point
            )  # Find the index of the nearest edge
            nearest_line: LineString = linestrings[
                nearest_index
            ]  # Find the corresponding linestring
            nearest_edge: Edge = edge_map[nearest_line]  # Map to the nearest edge
            start: Node = nearest_edge.start_node
            end: Node = nearest_edge.end_node

            # Find the closest point on this nearest edge to the building
            projected_point: Point = nearest_line.interpolate(
                nearest_line.project(building_point)
            )

            # Find the coordinates of this nearest point
            projected_coords: tuple[float, float] = (
                projected_point.x,
                projected_point.y,
            )

            # For example if the building is on the outside of a corner of a street,
            # then the closest point on the edge is its end or start node. Then we do not need to have a virtual node
            if projected_point.equals(Point((start.lat, start.lon))):
                new_edges.append(Edge(building, start))
                new_edges.append(Edge(start, building))
                continue
            if projected_point.equals(Point((end.lat, end.lon))):
                new_edges.append(Edge(building, end))
                new_edges.append(Edge(end, building))
                continue

            # If the closest point on the edge is not the end or start point we need to make virtual node on this edge
            virtual_node_name: str = f"virtual_{next(node_id_counter)}"
            virtual_node: Node = Node(
                name=virtual_node_name,
                lat=float(projected_coords[0]),
                lon=float(projected_coords[1]),
                is_building=False,
            )
            new_nodes.append(virtual_node)  # Add to list of new nodes

            self.delete_edge(nearest_edge)  # Then we remove the edge from the graph

            # Reconnect the start and end node of the old edge, with the virtual node in it
            # (we do not need to add the other way since the other way is another edge)
            # (this is not perfect since then the building is only connected to the street if you come from the correct side,
            # but I do not think this matters too much)
            new_edges.append(Edge(start, virtual_node))
            new_edges.append(Edge(virtual_node, end))

            # Connect the building to the newly created virtual node
            new_edges.append(Edge(building, virtual_node))
            new_edges.append(Edge(virtual_node, building))

        # Add all the newly created nodes and edges to the graph in bulk
        self.add_vertices(new_nodes)
        self.add_edges(new_edges)

        return self

    def create_map(self, filename: str) -> None:
        os.makedirs("maps", exist_ok=True)
        m: folium.Map = folium.Map(location=list(self.avg_coords()), zoom_start=15)
        for edge in self.edges:
            coords: list[tuple[float, float]] = [
                (edge.start_node.lat, edge.start_node.lon),
                (edge.end_node.lat, edge.end_node.lon),
            ]
            folium.PolyLine(coords, color="red").add_to(m)
        m.save(f"maps/{filename}.html")

    # Get a random sample from the buildings in the graph
    def sample_buildings(self, size: int) -> list[Node]:
        return random.sample(
            [node for node in self.nodes if node.is_building is True], k=size
        )

    # Make a alpha shape of the buildings in the graph, return the area and visualize on a map
    def alpha_shape(self, filename: str) -> float:
        gdf = gpd.GeoDataFrame(
            geometry=[
                node.point_lon_lat() for node in self.nodes if node.is_building is True
            ],
            crs="EPSG:4326",
        ).to_crs("EPSG:28992")
        hull = concave_hull(union_all(gdf), ratio=0.04, allow_holes=True)
        area = hull.area

        hull_wgs = gpd.GeoSeries([hull], crs="EPSG:28992").to_crs("EPSG:4326")[0]
        coords: list[tuple[float, float]] = [
            (y, x) for x, y in hull_wgs.exterior.coords
        ]

        m = folium.Map(location=list(self.avg_coords()), zoom_start=15)

        folium.Polygon(
            locations=coords,
            color="blue",
            fill=True,
            fill_opacity=0.3,
            weight=2,
            popup=f"Area: {area / 10**6:.2f} km²",
        ).add_to(m)

        m.save(f"alpha_shapes/{filename}.html")
        return area

    # Make a distance dictionary {(start_name, end_name): distance} between a list of nodes
    def distance_dict(self, nodes: list[Node]) -> dict[tuple[str, str], float]:
        indices: list[int] = [self.node2index(node) for node in nodes]
        distances: dict[tuple[str, str], float] = {}
        shortest_paths: list[list[float]] = self._g.distances(
            source=indices, target=indices, weights="weight"
        )
        for i, source in enumerate(indices):
            for j, target in enumerate(indices):
                distances[
                    (self.index2node(source).name, self.index2node(target).name)
                ] = shortest_paths[i][j]

        return distances

    # Write a TSP to the disk that LKH can solve
    def generate_tsp(self, size: int, run: int, dirname: str) -> None:
        locations: list[Node] = self.sample_buildings(size)
        distances: dict[tuple[str, str], float] = self.distance_dict(locations)

        # Mapping of the LKH node indices back to our node names (LKH starts counting from 1)
        index_to_location: dict[int, str] = {
            idx + 1: loc.name for idx, loc in enumerate(locations)
        }
        header: list[str] = [
            "NAME : tsp_problem",
            "TYPE : TSP",
            f"DIMENSION : {len(locations)}",
            "EDGE_WEIGHT_TYPE : EXPLICIT",
            "EDGE_WEIGHT_FORMAT : FULL_MATRIX",  # We need full matrix since the graph is directed
            "EDGE_WEIGHT_SECTION",
        ]
        rows: list[str] = []

        # Add the distances separated by spaces
        for loc1 in locations:
            row = [str(int(distances[(loc1.name, loc2.name)])) for loc2 in locations]
            rows.append(" ".join(row))

        body = "\n".join(header + rows + ["EOF"])

        with open(f"{dirname}/problem_{size}_{run}.tsp", "w") as f:
            f.write(body)

        # Write the mapping to json so we can load dictionary back in easily
        with open(f"{dirname}/index_to_location_{size}_{run}.json", "w") as f:
            ujson.dump(index_to_location, f)

        # Write parameter file so LKH uses the correct problem file and writes output to correct output file
        with open(f"{dirname}/problem_{size}_{run}.par", "w") as f:
            f.write(f"PROBLEM_FILE = {dirname}/problem_{size}_{run}.tsp\n")
            f.write(f"OUTPUT_TOUR_FILE = {dirname}/tour_{size}_{run}.txt\n")

    # Loop over the number of locations and number of runs to make all TSPs
    def create_tsps(
        self, num_runs: int, num_locations: list[int], dirname: str
    ) -> None:
        os.makedirs(dirname, exist_ok=True)
        for size in num_locations:
            for run in range(num_runs):
                self.generate_tsp(size, run, dirname)

    # LKH returns the node indices in the order of the shortest path, but we do not know this shortest path.
    # We also want to visualize paths so we need to find the exact shortest paths between nodes
    def get_shortest_path(self, source: Node, target: Node) -> list[Node]:
        path: list[int] = []
        path = self._g.get_shortest_path(
            self.node2index(source),
            self.node2index(target),
            weights="weight",
            output="vpath",
        )
        return [self.index2node(index) for index in path]

    # Given an ordered list of locations (node names) plot the route on a map
    def plot_route(self, locations: list[str], distance: int, filename: str) -> None:
        route: list[Node] = []
        route_nodes: list[Node] = [self.name2node(name) for name in locations]
        tsp_route_nodes: list[Node] = route_nodes + [route_nodes[0]]
        for index, source in enumerate(route_nodes):
            target = tsp_route_nodes[index + 1]
            route.extend(self.get_shortest_path(source, target))
        route_coords: list[tuple[float, float]] = [
            (node.lat, node.lon) for node in route
        ]
        m: folium.Map = folium.Map(location=list(self.avg_coords()), zoom_start=15)
        folium.PolyLine(route_coords, color="red", weight=4.5).add_to(m)
        for node in route_nodes:
            folium.Marker(
                (node.lat, node.lon),
                popup=f"The total route distance is {distance / 1000:.3f}km.",
            ).add_to(m)
        os.makedirs("routes", exist_ok=True)
        m.save(f"routes/{filename}.html")
