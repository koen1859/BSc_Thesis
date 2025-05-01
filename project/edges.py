from shapely.lib import node
from graph import distance
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree


# This function takes as inputs the roads, nodes and buildings. First all roads are connected
# to themselves and to each other. Then, the buildings need to be connected to the road network
# that was created. To do this, we create a tree, and connect each building to its closest road node.
def get_edges(roads, nodes, buildings):
    edges, weights = [], []

    road_segments = []
    segment_info = {}
    for road in roads:
        road_nodes = [str(id) for id in road[1]]
        oneway = road[4]

        for i in range(1, len(road_nodes)):
            start, end = road_nodes[i - 1], road_nodes[i]

            edges.append((start, end))
            weights.append(distance(nodes[start], nodes[end]))
            if oneway != "yes":  # If the road is two-way, also add the other direction
                edges.append((end, start))
                weights.append(distance(nodes[end], nodes[start]))

            # Preparation to connect the buildings next
            seg = LineString([nodes[start], nodes[end]])
            road_segments.append(seg)
            segment_info[len(road_segments) - 1] = (start, end, oneway)

    tree = STRtree(road_segments)  # make a tree of the road network

    # Counter to add new nodes to connect buildings to road network correctly
    new_node_idx = 0
    for building_id, building_coords in buildings.items():
        building_point = Point(building_coords)

        nearest_segment_idx = tree.nearest(building_point)  # find the nearest edge
        start_node, end_node, oneway = segment_info[nearest_segment_idx]

        # Project the building onto this nearest edge
        nearest_segment = road_segments[nearest_segment_idx]
        projected_point = nearest_segment.interpolate(
            nearest_segment.project(building_point)
        )

        # If the projected point is one of the segments end points, use this
        if projected_point.equals(Point(nodes[start_node])):
            connect_to = start_node
        elif projected_point.equals(Point(nodes[end_node])):
            connect_to = end_node
        else:  # else, we need to create a virtual node and connect the building to it
            virtual_node_id = f"virtual_{new_node_idx}"
            nodes[virtual_node_id] = (projected_point.x, projected_point.y)
            new_node_idx += 1

            # We split the road segment and add the virtual node
            edges.append((start_node, virtual_node_id))
            weights.append(distance(nodes[start_node], nodes[virtual_node_id]))
            edges.append((virtual_node_id, end_node))
            weights.append(distance(nodes[virtual_node_id], nodes[end_node]))

            if oneway != "yes":  # if not one-way, add reverse
                edges.append((virtual_node_id, start_node))
                weights.append(distance(nodes[virtual_node_id], nodes[start_node]))
                edges.append((end_node, virtual_node_id))
                weights.append(distance(nodes[end_node], nodes[virtual_node_id]))

            # And we need to connect the building to the newly created node
            connect_to = virtual_node_id

        # Finally, we make the connections
        edges.append((str(building_id), connect_to))
        weights.append(distance(building_coords, nodes[connect_to]))
        edges.append((connect_to, str(building_id)))
        weights.append(distance(nodes[connect_to], building_coords))

    return edges, weights
