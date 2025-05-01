import folium
import os


# This function creates a map the graph
def create_map(nodes, buildings, graph, filename):
    os.makedirs("maps", exist_ok=True)
    all_nodes = {**nodes, **buildings}
    edges = [
        (graph.vs[edge.source]["name"], graph.vs[edge.target]["name"])
        for edge in graph.es
    ]
    m = folium.Map(location=list(nodes[edges[0][0]]))
    for edge in edges:
        coords = list((all_nodes[edge[0]], all_nodes[edge[1]]))
        folium.PolyLine(coords, color="red").add_to(m)
    m.save(f"maps/{filename}")
