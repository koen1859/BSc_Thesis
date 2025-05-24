from db import get_addresses, get_features, get_roads
from node import Node, get_road_nodes, get_building_nodes
from edge import Edge, get_road_edges
from graph import Graph
from tsp import solve_tsps
from read_tour import read_tours
from route import random_path
from find_beta import find_beta, results, scatterplot, errorsplot
from features_df import features_df
from ml_model import random_forest


# This is the main simulation function. It creates, solves,
# visualizes and solves beardwood formula for a given neighborhood
def run_simulation(
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

    graph.create_map(key)
    area: float = graph.alpha_shape(key)
    graph.create_tsps(10, list(range(20, 90, 2)), f"tsps_{key}")

    get_features(DB, neighborhood, roads, graph, area)
    solve_tsps(f"tsps_{key}")

    tours: dict[int, list[list[str]]]
    distances: dict[int, list[int]]
    tours, distances = read_tours(f"tsps_{key}")

    locations: list[str]
    distance: int
    locations, distance = random_path(tours, distances)

    graph.plot_route(locations, distance, f"TSP_{key}")

    x: list[int]
    y: list[float]
    b_hat: float
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


# The same as the above function but just without creating and solving new TSPs,
# since this takes quite long and is not needed if they have already been
# written to the disk.
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
    # get_features(DB, neighborhood, roads, graph, area)

    # tours: dict[int, list[list[str]]]
    # distances: dict[int, list[int]]
    # tours, distances = read_tours(f"tsps_{key}")
    #
    # (
    #     x,
    #     y,
    #     b_hat,
    # ) = find_beta(distances, area)
    #
    # line: list[float]
    # errors: list[float]
    # mae: float
    # mape: float
    # line, errors, mae, mape = results(distances, x, y, b_hat, area)
    #
    # return (key, [b_hat, mae, mape, area, x, y])


def run_ml() -> None:
    df = features_df()
    r2, mae, mape, y_test, y_pred = random_forest(df)
    print(r2, mae, mape)
    with open("ml_results.txt", "w") as f:
        f.write(f"""r2: {r2}\nmae: {mae}\nmape: {mape * 100}\n""")
