from db import get_addresses, get_features, get_roads
from node import Node, get_road_nodes, get_building_nodes
from edge import Edge, get_road_edges
from graph import Graph
from alpha_shape import get_area
from tsp import solve_tsps
from read_tour import read_tours
from route import random_path
from find_beta import find_beta, results, scatterplot, errorsplot

DB = "noord_holland"
neighborhood = "Stad van de Zon"
key = f"{DB}-{neighborhood}"

roads = get_roads(DB, neighborhood)
buildings = get_addresses(DB, neighborhood)

road_nodes: list[Node] = get_road_nodes(roads=roads)
building_nodes: list[Node] = get_building_nodes(buildings=buildings)

area = get_area(building_nodes)

road_edges: list[Edge] = get_road_edges(roads=roads, road_nodes=road_nodes)
graph = (
    Graph(nodes=road_nodes, edges=road_edges)
    .connect_buildings(building_nodes)
    .largest_component()
)
graph.avg_path_length()
graph.diameter()
graph.radius()
graph.edge_connectivity()
graph.vertex_connectivity()
graph.mincut_value()
graph.num_communities_infomap()
graph.num_communities_springlass()
graph.mean_degree()
graph.max_degree()
graph.var_degree()

graph.create_map(key)
graph.create_tsps(10, list(range(20, 90, 2)), "testdir")

get_features(DB, neighborhood, roads, graph, area)
solve_tsps("testdir")

tours, distances = read_tours("testdir")
locations, distance = random_path(tours, distances)

graph.plot_route(locations, distance, f"TSP_{neighborhood}")

(
    x,
    y,
    b_hat,
) = find_beta(distances, area)
line, errors, mae, mape = results(distances, x, y, b_hat, area)
scatterplot(distances, x, y, b_hat, line, f"scatter_{key}")
errorsplot(errors, f"errors_{key}")

print((key, [b_hat, mae, mape, area, x, y]))

print(f"Solved TSPs for {key}")
