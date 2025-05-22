import random


def random_path(
    tours: dict[int, list[list[str]]], distances: dict[int, list[int]]
) -> tuple[list[str], int]:
    num_locations: int = random.choice(list(tours.keys()))
    locations: list[str] = tours[num_locations][0]
    distance: int = distances[num_locations][0]
    return locations, distance
