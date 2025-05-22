from shapely import union_all, concave_hull
from shapely.wkt import loads
import geopandas as gpd
import matplotlib.pyplot as plt
from graph import Node


# A test function to check whether the hull looks correct
def plot_area(hull):
    polygon = loads(hull)
    x, y = polygon.exterior.xy
    plt.figure(figsize=(10, 10))
    plt.plot(x, y, color="blue")
    plt.fill(x, y, alpha=0.3)
    plt.title("Polygon Plot")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")
    plt.grid(True)
    plt.savefig("Testplot.png")


# Function that returns the area of the convex hull around the list of buildings
def get_area(nodes: list[Node]) -> float:
    gdf = gpd.GeoDataFrame(
        geometry=[node.point_lon_lat() for node in nodes if node.is_building is True],
        crs="EPSG:4326",
    ).to_crs("EPSG:28992")
    hull = concave_hull(union_all(gdf), ratio=0.05, allow_holes=True)
    return hull.area
