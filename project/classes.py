from math import cos, radians, sqrt
import igraph as ig


class Node:
    def __init__(
        self, id: str, latitude: float, longitude: float, is_building: bool
    ) -> None:
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.is_building = is_building

    def distance(self, other: "Node") -> float:
        radius = 6371000
        lat1, lon1, lat2, lon2 = map(
            radians, [self.latitude, self.longitude, other.latitude, other.longitude]
        )
        x = (lon2 - lon1) * cos((lat1 + lat2) / 2)
        y = lat2 - lat1
        return radius * sqrt(x**2 + y**2)


class Edge:
    def __init__(self, id: str, start_node: Node, end_node: Node) -> None:
        self.id = id
        self.start_node = start_node
        self.end_node = end_node
        self.weight = start_node.distance(end_node)


class Graph:
    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self._g = ig.Graph()
        self.nodes = []
        self.edges = []
        self.add_vertices(nodes)

    def contains(self, node: Node) -> bool:
        return node in self.nodes

    def add_vertex(self, node: Node) -> None:
        if not self.contains(node):
            self._g.add_vertex(id=node.id)
            self.nodes.append(node)

    def add_vertices(self, nodes: list[Node]) -> None:
        for node in nodes:
            self.add_vertex(node)


testnode1: Node = Node(id="1", latitude=53.465787, longitude=6.987654, is_building=True)
testnode2: Node = Node(id="2", latitude=53.365787, longitude=6.887654, is_building=True)
testnode3: Node = Node(id="3", latitude=53.363787, longitude=6.444454, is_building=True)

testedge1: Edge = Edge(id="1", start_node=testnode1, end_node=testnode2)

graph: Graph = Graph(nodes=[testnode1, testnode2], edges=[testedge1])

print(graph.contains(testnode1))
print(graph.contains(testnode2))
print(graph.contains(testnode3))
print(graph._g.vs["id"])
print(graph.add_vertex(testnode3))
print(graph.nodes)
print(graph._g.vs["id"])
