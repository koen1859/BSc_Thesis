import os
import random
import itertools
import folium
import igraph as ig
import numpy as np
import ujson
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
from node import Node
from edge import Edge


class Graph:
    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self._g = ig.Graph(directed=True)
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self._name2node: dict["str", Node] = {}
        self.add_vertices(nodes)
        self.add_edges(edges)

    def contains_node(self, node: Node) -> bool:
        return node in self.nodes

    def contains_edge(self, edge: Edge) -> bool:
        return edge in self.edges

    def add_vertex(self, node: Node) -> None:
        if not self.contains_node(node):
            self._g.add_vertex(name=node.name)
            self.nodes.append(node)
            self._name2node[node.name] = node

    def add_vertices(self, nodes: list[Node]) -> None:
        new_nodes: list[Node] = [node for node in nodes if not self.contains_node(node)]
        if new_nodes:
            self._g.add_vertices(len(new_nodes))
            self._g.vs[-len(new_nodes) :]["name"] = [node.name for node in new_nodes]
            self.nodes.extend(new_nodes)
            for node in nodes:
                self._name2node[node.name] = node

    def add_edge(self, edge: Edge) -> None:
        self.add_vertex(edge.start_node)
        self.add_vertex(edge.end_node)
        if not self.contains_edge(edge):
            self._g.add_edge(edge.start_node.name, edge.end_node.name)
            self._g.es[-1]["weight"] = edge.weight
            self.edges.append(edge)

    def add_edges(self, edges: list[Edge]) -> None:
        new_nodes: dict["str", Node] = {}
        for edge in edges:
            if not self.contains_node(edge.start_node):
                new_nodes[edge.start_node.name] = edge.start_node
            if not self.contains_node(edge.end_node):
                new_nodes[edge.end_node.name] = edge.end_node

        if new_nodes:
            self.add_vertices(list(new_nodes.values()))

        new_edges: list[Edge] = [edge for edge in edges if not self.contains_edge(edge)]

        if new_edges:
            self._g.add_edges(
                [edge.start_node.name, edge.end_node.name] for edge in new_edges
            )
            self.edges.extend(new_edges)
            self._g.es[-len(new_edges) :]["weight"] = [
                edge.weight for edge in new_edges
            ]

    def delete_edge(self, edge: Edge) -> None:
        if edge in self.edges:
            self.edges.remove(edge)
            # Remove from igraph as well
            start: Node = edge.start_node
            end: Node = edge.end_node
            es_to_delete = self._g.es.select(
                _source=self.node2index(start),
                _target=self.node2index(end),
            )
            es_to_delete.delete()

    def index2name(self, index: int) -> str:
        return self._g.vs[index]["name"]

    def name2node(self, name: str) -> Node:
        return self._name2node[name]

    def index2node(self, index: int) -> Node:
        return self.name2node(self.index2name(index))

    def node2index(self, node: Node) -> int:
        return self._g.vs.find(name=node.name).index

    def avg_coords(self) -> tuple[float, float]:
        all_lats = [float(node.lat) for node in self.nodes]
        all_lons = [float(node.lon) for node in self.nodes]
        return (float(np.mean(all_lats)), float(np.mean(all_lons)))

    def total_edge_weight(self) -> float:
        return sum(edge.weight for edge in self.edges)

    def num_buildings(self) -> int:
        return len([node for node in self.nodes if node.is_building])

    def avg_edge_weight(self) -> float:
        return float(np.mean([edge.weight for edge in self.edges]))

    def largest_component(self) -> "Graph":
        subgraph = self._g.subgraph(max(self._g.components(), key=len))
        nodes: list[Node] = [self.name2node(name) for name in subgraph.vs["name"]]
        edges: list[Edge] = [
            Edge(
                self.name2node(subgraph.vs[edge.source]["name"]),
                self.name2node(subgraph.vs[edge.target]["name"]),
            )
            for edge in subgraph.es
        ]
        return Graph(nodes, edges)

    def connect_buildings(self, building_nodes: list[Node]) -> "Graph":
        edge_to_linestring: dict[Edge, LineString] = {}
        linestrings: list[LineString] = []
        edge_map: dict[LineString, Edge] = {}
        new_nodes: list[Node] = []
        new_edges: list[Edge] = []

        for edge in self.edges:
            start: Node = edge.start_node
            end: Node = edge.end_node
            line: LineString = LineString([(start.lat, start.lon), (end.lat, end.lon)])
            edge_to_linestring[edge] = line
            linestrings.append(line)
            edge_map[line] = edge

        tree: STRtree = STRtree(linestrings)
        node_id_counter = itertools.count(
            start=max(
                int(n.name.split("_")[-1]) for n in self.nodes if "virtual" in n.name
            )
            + 1
            if any("virtual" in n.name for n in self.nodes)
            else 0
        )

        for building in building_nodes:
            building_point: Point = building.point_lat_lon()
            nearest_index = tree.nearest(building_point)
            nearest_line: LineString = linestrings[nearest_index]
            nearest_edge: Edge = edge_map[nearest_line]
            start: Node = nearest_edge.start_node
            end: Node = nearest_edge.end_node

            projected_point: Point = nearest_line.interpolate(
                nearest_line.project(building_point)
            )
            projected_coords: tuple[float, float] = (
                projected_point.x,
                projected_point.y,
            )

            if projected_point.equals(Point((start.lat, start.lon))):
                self.add_edge(Edge(building, start))
                self.add_edge(Edge(start, building))
                continue
            if projected_point.equals(Point((end.lat, end.lon))):
                self.add_edge(Edge(building, end))
                self.add_edge(Edge(end, building))
                continue

            virtual_node_name: str = f"virtual_{next(node_id_counter)}"
            virtual_node: Node = Node(
                name=virtual_node_name,
                lat=float(projected_coords[0]),
                lon=float(projected_coords[1]),
                is_building=False,
            )
            new_nodes.append(virtual_node)

            self.delete_edge(nearest_edge)

            new_edges.append(Edge(start, virtual_node))
            new_edges.append(Edge(virtual_node, end))

            new_edges.append(Edge(building, virtual_node))
            new_edges.append(Edge(virtual_node, building))

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

    def sample_buildings(self, size: int) -> list[Node]:
        return random.sample(
            [node for node in self.nodes if node.is_building is True], k=size
        )

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

    def generate_tsp(self, size: int, run: int, dirname: str) -> None:
        locations: list[Node] = self.sample_buildings(size)
        distances: dict[tuple[str, str], float] = self.distance_dict(locations)
        index_to_location: dict[int, str] = {
            idx + 1: loc.name for idx, loc in enumerate(locations)
        }
        header: list[str] = [
            "NAME : tsp_problem",
            "TYPE : TSP",
            f"DIMENSION : {len(locations)}",
            "EDGE_WEIGHT_TYPE : EXPLICIT",
            "EDGE_WEIGHT_FORMAT : FULL_MATRIX",
            "EDGE_WEIGHT_SECTION",
        ]
        rows: list[str] = []

        for loc1 in locations:
            row = [str(int(distances[(loc1.name, loc2.name)])) for loc2 in locations]
            rows.append(" ".join(row))

        body = "\n".join(header + rows + ["EOF"])

        with open(f"{dirname}/problem_{size}_{run}.tsp", "w") as f:
            f.write(body)

        with open(f"{dirname}/index_to_location_{size}_{run}.json", "w") as f:
            ujson.dump(index_to_location, f)

        with open(f"{dirname}/problem_{size}_{run}.par", "w") as f:
            f.write(f"PROBLEM_FILE = {dirname}/problem_{size}_{run}.tsp\n")
            f.write(f"OUTPUT_TOUR_FILE = {dirname}/tour_{size}_{run}.txt\n")

    def create_tsps(
        self, num_runs: int, num_locations: list[int], dirname: str
    ) -> None:
        os.makedirs(dirname, exist_ok=True)
        for size in num_locations:
            for run in range(num_runs):
                self.generate_tsp(size, run, dirname)

    def get_shortest_path(self, source: Node, target: Node) -> list[Node]:
        path: list[int] = []
        path = self._g.get_shortest_path(
            self.node2index(source),
            self.node2index(target),
            weights="weight",
            output="vpath",
        )
        return [self.index2node(index) for index in path]

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
