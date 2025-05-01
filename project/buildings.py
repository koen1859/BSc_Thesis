# This function converts the data imported from postgresql into dictionaries,
# with as index the building id and as value the coordinates
# Note that we use a string instead of an int as id since these integers are too large
# so igraph doesnt want these numbers as atttribute to a node, so we convert to a string.
def get_buildings(building_data):
    buildings = {}
    for id, lat, lon, city in building_data:
        buildings[str(id)] = (lat, lon)
    return buildings
