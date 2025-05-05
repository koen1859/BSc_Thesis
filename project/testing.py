from db import get_addresses, get_road_data, get_features
from area import get_area
from map import create_map
from buildings import get_buildings
from nodes import get_nodes
from edges import get_edges
from graph import make_graph
from tsp import create_tsps, solve_tsps
from read_tour import read_tours
from route import paths_subset
from find_beta import find_beta, results, scatterplot, errorsplot
from features_df import features_df
from run_simulation import run_ml

import pandas as pd
import numpy as np

# This is just a file i made to test some things before but it will probably return error now
roads = get_road_data("groningen", "Beijum")
print(f"{len(roads)} roads imported.")
building_data = get_addresses("groningen", "Beijum")
buildings = get_buildings(building_data)
print(f"{len(buildings)} buildings imported.")
# create_map(roads, f"{"groningen"}_{"Beijum"}.html", buildings)
nodes = get_nodes(roads)
print(f"{len(nodes)} nodes extracted.")
edges, weights = get_edges(roads, nodes, buildings)
print(f"{len(edges)} edges extracted.")
graph = make_graph(nodes, buildings, edges, weights)
# create_map(nodes, buildings, graph, f"{"groningen"}_{"Beijum"}.html")
area = get_area(buildings)

tours, lengths = read_tours("tsps_groningen_Beijum")
paths_subset(graph, nodes, buildings, tours, lengths, "groningen_Beijum")
x, y, b_hat, b_hat_n = find_beta(lengths, area)
line, errors, MAE = results(lengths, x, y, b_hat, area)
print(
    f"""MAE: {MAE}\n
Beta: {b_hat}
Beta(n): {b_hat_n}"""
)
r2, mae, mape, y_test, y_pred = run_ml()
print(f"r2: {r2}, mae: {mae}, mape: {mape}")
print(y_test)
print(y_pred)
print(np.min(y_test))
print(np.min(y_pred))
