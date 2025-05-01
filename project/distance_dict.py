import igraph as ig


# This function calculates the distances between all locations it is provided,
# when traveling over the graph that it is provided with. We use get_shortest_paths_dijkstra
# to very efficiently calculate all distances at once. Then we write this to a dictionary
# for easy access to write it to a file later on.
def distance_dict(graph, locations):
    distances = {}
    all_shortest_paths = graph.shortest_paths_dijkstra(
        source=locations, target=locations, weights="weight"
    )
    for i, source in enumerate(locations):
        for j, target in enumerate(locations):
            distances[(source, target)] = all_shortest_paths[i][j]
    return distances
