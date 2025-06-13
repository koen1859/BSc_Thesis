from math import cos, radians, sqrt

from shapely.geometry import Point


class Node:
    def __init__(self, name: str, lat: float, lon: float, is_building: bool) -> None:
        self.name: str = name
        self.lat: float = lat
        self.lon: float = lon
        self.is_building: bool = is_building

    def distance(self, other: "Node") -> float:
        radius = 6371000  # Earth's radius
        lat1, lon1, lat2, lon2 = map(
            radians, [self.lat, self.lon, other.lat, other.lon]
        )
        x = (lon2 - lon1) * cos((lat1 + lat2) / 2)
        y = lat2 - lat1
        return radius * sqrt(x**2 + y**2)

    # To use a node for certain libraries we need to convert to Point
    # object. (some use lat,lon, some use lon,lat)
    def point_lat_lon(self) -> Point:
        return Point(self.lat, self.lon)

    def point_lon_lat(self) -> Point:
        return Point(self.lon, self.lat)

    # To make nice print
    def __repr__(self) -> str:
        r: str = f"Node(name={self.name}, lat={self.lat}, lon={self.lon}, is_building={self.is_building})"
        return r


# Fetch road nodes from the raw data we extracted in db.py
def get_road_nodes(
    roads: list[tuple[int, list[int], list[float], list[float], str]],
) -> list[Node]:
    road_nodes: list[Node] = []
    for _, node_ids, node_lats, node_lons, _ in roads:
        for index, name in enumerate(node_ids):
            road_nodes.append(
                Node(
                    name=str(name),
                    lat=node_lats[index],
                    lon=node_lons[index],
                    is_building=False,
                )
            )
    return road_nodes


# Fetch building nodes from the raw data we extracted in db.py
def get_building_nodes(buildings: list[tuple[int, float, float]]) -> list[Node]:
    building_nodes: list[Node] = []
    for name, lat, lon in buildings:
        building_nodes.append(Node(name=str(name), lat=lat, lon=lon, is_building=True))
    return building_nodes
