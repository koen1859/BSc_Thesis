import random


# we sample uniformly from all buildings in the area (i.e. buildings that have a postcode)
def sample(graph, size):
    building_names = [v["name"] for v in graph.vs if v["is_building"] == 1]
    return random.sample(building_names, size)
