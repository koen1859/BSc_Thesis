import folium


# This function takes a set of locations that form a sorted tour (i.e. a tsp solutions),
# (these are node indexes) and converts this to a sorted list of coordinates, so the path
# can be visualized on a map.
def route(graph, locations):
    path = []
    for i in range(len(locations)):
        path_vertices = graph.get_shortest_path(
            locations[i - 1], locations[i], weights="weight", output="vpath"
        )
        path.extend([graph.vs[node]["name"] for node in path_vertices])
    return path


# This function takes as input such a sorted tour with coordinates and puts them on a map using
# folim, and saves to a html file so it can be viewed and interacted with from a browser.
# It also displays the total length of the path, if you click on a marker.
def plot_route(nodes, buildings, locations, path, distance, filename):
    m = folium.Map(location=[53.2194, 6.5665], zoom_start=12)
    all_nodes = {**nodes, **buildings}
    path_coords = [all_nodes[index] for index in path]
    folium.PolyLine(path_coords, color="red", weight=4.5).add_to(m)
    for i in range(len(locations)):
        folium.Marker(
            all_nodes[locations[i]],
            popup=f"The total route distance is {round(distance / 1000, 3)}km.",
        ).add_to(m)
    m.save(f"maps/{filename}")


# This function puts the previous two together. We have solved a bunch of TSPS, of course plotting
# them all is not viable and not informative. It takes 1 tsp tour from each number of locations
# and makes a map of this path. In the main simulation loop this is commented out since I have
# seen that the paths look correct so to save time for the simulation i do not need this.
# If you want you can always uncomment this part in the loop, to make some visualisations of the
# tsps paths.
def paths_subset(graph, nodes, buildings, tours, distances, city):
    for i in tours.keys():
        locations = tours[i][0]
        distance = distances[i][0]
        path = route(graph, locations)
        plot_route(nodes, buildings, locations, path, distance, f"TSP_{city}_{i}.html")
