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
from linear_model import linear_model


def run_simulation(DB, neighborhood):
    roads = get_road_data(DB, neighborhood)

    building_data = get_addresses(DB, neighborhood)
    buildings = get_buildings(building_data)

    nodes = get_nodes(roads)
    edges, weights = get_edges(roads, nodes, buildings)
    graph = make_graph(nodes, buildings, edges, weights)

    create_map(nodes, buildings, graph, f"{DB}_{neighborhood}.html")
    create_tsps(graph, 10, range(20, 90, 2), f"tsps_{DB}_{neighborhood}")

    area = get_area(buildings)
    get_features(DB, neighborhood, roads, graph, area)
    print(f"TSPs generated and features extracted for {DB} {neighborhood}")

    solve_tsps(f"tsps_{DB}_{neighborhood}")
    tours, distances = read_tours(f"tsps_{DB}_{neighborhood}")
    # paths_subset(graph, nodes, buildings, tours, distances, DB)

    x, y, b_hat, b = find_beta(distances, area)
    line, errors, MAE = results(distances, x, y, b_hat, area)
    scatterplot(distances, x, y, b_hat, line, f"scatter_{DB}_{neighborhood}")
    errorsplot(errors, f"errors_{DB}_{neighborhood}")

    key = f"{DB}-{neighborhood}"
    print(f"Solved TSPs for {key}")

    return (key, [b_hat, MAE, area, line])


def interpret_results(DB, neighborhood):
    building_data = get_addresses(DB, neighborhood)
    buildings = get_buildings(building_data)

    area = get_area(buildings)

    tours, distances = read_tours(f"tsps_{DB}_{neighborhood}")
    # paths_subset(graph, nodes, buildings, tours, distances, DB)

    x, y, b_hat, b = find_beta(distances, area)
    line, errors, MAE = results(distances, x, y, b_hat, area)
    scatterplot(distances, x, y, b_hat, line, f"scatter_{DB}_{neighborhood}.png")
    errorsplot(errors, f"errors_{DB}_{neighborhood}.png")

    key = f"{DB}-{neighborhood}"
    print(f"Solved TSPs for {DB} {neighborhood}")

    return (key, [b_hat, MAE])


def run_ml():
    df = features_df()
    r2, mae, mape, y_test, y_pred = linear_model(df)
    return r2, mae, mape, y_test, y_pred
