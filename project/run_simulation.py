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
from linear_model import linear_model, predict_path_lengths


# This is the main simulation function. It creates, solves,
# visualizes and solves beardwood formula for a given neighborhood
def run_simulation(DB, neighborhood):
    key = f"{DB}-{neighborhood}"
    roads = get_road_data(DB, neighborhood)

    building_data = get_addresses(DB, neighborhood)
    buildings = get_buildings(building_data)

    nodes = get_nodes(roads)
    edges, weights = get_edges(roads, nodes, buildings)
    graph = make_graph(nodes, buildings, edges, weights)

    create_map(nodes, buildings, graph, f"{key}.html")
    create_tsps(graph, 10, range(20, 90, 2), f"tsps_{key}")

    area = get_area(buildings)
    get_features(DB, neighborhood, roads, graph, area)
    print(f"TSPs generated and features extracted for {key}")

    solve_tsps(f"tsps_{key}")
    tours, distances = read_tours(f"tsps_{key}")
    paths_subset(graph, nodes, buildings, tours, distances, key)

    x, y, b_hat, b = find_beta(distances, area)
    line, errors, mae, mape = results(distances, x, y, b_hat, area)
    scatterplot(distances, x, y, b_hat, line, f"scatter_{key}")
    errorsplot(errors, f"errors_{key}")

    print(f"Solved TSPs for {key}")

    return (key, [b_hat, mae, mape, area, line])


# The same as the above function but just without creating and solving new TSPs,
# since this takes quite long and is not needed if they have already been
# written to the disk.
def interpret_results(DB, neighborhood):
    key = f"{DB}-{neighborhood}"
    roads = get_road_data(DB, neighborhood)

    building_data = get_addresses(DB, neighborhood)
    buildings = get_buildings(building_data)
    area = get_area(buildings)

    nodes = get_nodes(roads)
    edges, weights = get_edges(roads, nodes, buildings)
    graph = make_graph(nodes, buildings, edges, weights)
    # create_map(nodes, buildings, graph, f"{key}.html")

    tours, distances = read_tours(f"tsps_{key}")
    paths_subset(graph, nodes, buildings, tours, distances, key)

    # x, y, b_hat, b = find_beta(distances, area)
    # line, errors, mae, mape = results(distances, x, y, b_hat, area)
    # scatterplot(distances, x, y, b_hat, line, f"scatter_{key}.png")
    # errorsplot(errors, f"errors_{key}.png")
    #
    print(f"Solved TSPs for {key}")
    #
    # return (key, [b_hat, mae, mape, area, line])


def run_ml():
    df = features_df()
    r2, mae, mape, y_test, y_pred = linear_model(df)
    predict_path_lengths(y_pred)
    return r2, mae, mape, y_test, y_pred
