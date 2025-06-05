from db import get_addresses, get_features, get_roads
from node import Node, get_road_nodes, get_building_nodes
from edge import Edge, get_road_edges
from graph import Graph
from tsp import solve_tsps
from read_tour import read_tours
from route import random_path
from find_beta import find_beta, results, scatterplot, errorsplot
from features_df import features_df, split_train_test
from ml_model import random_forest, feature_importance
from tables import make_ml_results_table
import pandas as pd


# This is the main simulation function. It creates, solves,
# visualizes and solves beardwood formula for a given neighborhood
def run_simulation(
    DB: str, neighborhood: str
) -> tuple[str, list[float | list[int] | list[float]]]:
    key: str = f"{DB}-{neighborhood}"  # Key to name files and directories consistently

    # Extract all roads
    roads: list[tuple[int, list[int], list[float], list[float], str]] = get_roads(
        DB, neighborhood
    )
    # Extract all buildings
    buildings: list[tuple[int, float, float]] = get_addresses(DB, neighborhood)

    # Create the nodes from the roads and buildings
    road_nodes: list[Node] = get_road_nodes(roads=roads)
    building_nodes: list[Node] = get_building_nodes(buildings=buildings)

    # Make the road edges
    road_edges: list[Edge] = get_road_edges(roads=roads, road_nodes=road_nodes)

    # First make a graph of all the roads, then connect all buildings to it, and keep the largest connected component
    graph: Graph = (
        Graph(nodes=road_nodes, edges=road_edges)
        .connect_buildings(building_nodes)
        .largest_component()
    )

    # Visualize graph
    graph.create_map(key)

    # Get area and also plot the alpha shape
    area: float = graph.alpha_shape(key)

    # Create the TSPs and write to disk
    graph.create_tsps(10, list(range(20, 90, 2)), f"tsps_{key}")

    # Extract the features and write to disk
    get_features(DB, neighborhood, roads, graph, area)

    # Solve the TSPs with LKH
    solve_tsps(f"tsps_{key}")

    # Read the LKH output
    tours: dict[int, list[list[str]]]
    distances: dict[int, list[int]]
    tours, distances = read_tours(f"tsps_{key}")

    # Take a random TSP solution and plot it
    locations: list[str]
    distance: int
    locations, distance = random_path(tours, distances)
    graph.plot_route(locations, distance, f"TSP_{key}")

    # Solve for the BHH formula using the TSP solutions
    x: list[int]
    y: list[float]
    b_hat: float
    (
        x,
        y,
        b_hat,
    ) = find_beta(distances, area)

    # Get BHH formula accuracy metrics and make plots
    line: list[float]
    errors: list[float]
    mae: float
    mape: float
    line, errors, mae, mape = results(distances, x, y, b_hat, area)
    scatterplot(distances, x, y, b_hat, line, f"scatter_{key}")
    errorsplot(errors, f"errors_{key}")

    return (key, [b_hat, mae, mape, area, x, y])


# The same as the above function but just without creating and solving new TSPs,
# since this takes quite long and is not needed if this has already been done.
# This is just to test some changes to other parts of the project
def interpret_results(
    DB: str, neighborhood: str
) -> tuple[str, list[float | list[int] | list[float]]]:
    key: str = f"{DB}-{neighborhood}"

    roads: list[tuple[int, list[int], list[float], list[float], str]] = get_roads(
        DB, neighborhood
    )
    buildings: list[tuple[int, float, float]] = get_addresses(DB, neighborhood)

    road_nodes: list[Node] = get_road_nodes(roads=roads)
    building_nodes: list[Node] = get_building_nodes(buildings=buildings)

    road_edges: list[Edge] = get_road_edges(roads=roads, road_nodes=road_nodes)
    graph: Graph = (
        Graph(nodes=road_nodes, edges=road_edges)
        .connect_buildings(building_nodes)
        .largest_component()
    )

    area: float = graph.alpha_shape(key)

    tours: dict[int, list[list[str]]]
    distances: dict[int, list[int]]
    tours, distances = read_tours(f"tsps_{key}")

    locations, distance = random_path(tours, distances)

    (
        x,
        y,
        b_hat,
    ) = find_beta(distances, area)

    line: list[float]
    errors: list[float]
    mae: float
    mape: float
    line, errors, mae, mape = results(distances, x, y, b_hat, area)

    scatterplot(distances, x, y, b_hat, line, f"scatter_{key}")
    errorsplot(errors, f"errors_{key}")

    return (key, [b_hat, mae, mape, area, x, y])


def run_ml():
    df: pd.DataFrame = features_df()
    df_train: pd.DataFrame
    df_test: pd.DataFrame
    df_train, df_test = split_train_test(df)
    results = random_forest(df_train, df_test)
    results_reduced = feature_importance(df_train, df_test, results)
    with open("ml_results.txt", "w") as f:
        f.write(
            f"Full model:\nTrain:{results['train']}\nTest:{results['test']}\nParams:{results['best_parameters']}\n"
        )
        f.write(
            f"Reduced model:\n{results_reduced['train']}\n{results_reduced['test']}\nParams:{results_reduced['best_parameters']}\n"
        )
    make_ml_results_table(results, results_reduced)
