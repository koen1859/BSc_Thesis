from node import Node


class Edge:
    def __init__(self, start_node: Node, end_node: Node) -> None:
        self.start_node: Node = start_node
        self.end_node: Node = end_node
        self.weight: float = self.start_node.distance(self.end_node)

    def __repr__(self) -> str:
        r: str = f"Edge(start_node={self.start_node.name}, end_node={self.end_node.name}, weight={self.weight})"
        return r


def get_road_edges(
    roads: list[tuple[int, list[int], list[float], list[float], str]],
    road_nodes: list[Node],
) -> list[Edge]:
    edges: list[Edge] = []
    name_to_node: dict[str, Node] = {node.name: node for node in road_nodes}

    for _, road_node_names, _, _, oneway in roads:
        node_names: list[str] = [str(name) for name in road_node_names]

        for i in range(1, len(node_names)):
            start_name: str = node_names[i - 1]
            end_name: str = node_names[i]

            if start_name not in name_to_node or end_name not in name_to_node:
                continue

            start_node: Node = name_to_node[start_name]
            end_node: Node = name_to_node[end_name]

            edge: Edge = Edge(start_node=start_node, end_node=end_node)
            edges.append(edge)

            if oneway != "yes":  # Add reverse edge for two-way roads
                reverse_edge = Edge(start_node=end_node, end_node=start_node)
                edges.append(reverse_edge)

    return edges
