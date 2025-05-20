from shapely import union_all, concave_hull, convex_hull
from shapely.geometry import Point
from shapely.wkt import loads
import geopandas as gpd
import matplotlib.pyplot as plt


# A test function to check whether the hull look correct
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


# Function that returns the area of the convex hull around a set of buildings it takes as input
def get_area(buildings):
    points = [tuple(map(float, coord)) for coord in buildings.values()]
    # Convert the lat,lon to correct format, to be able to calculate area in square meters.
    gdf = gpd.GeoDataFrame(
        geometry=[Point(lon, lat) for lat, lon in points], crs="EPSG:4326"
    ).to_crs("EPSG:28992")
    hull = concave_hull(union_all(gdf), ratio=0.05, allow_holes=True)
    # plot_area(str(hull))
    return hull.area
