import json
import os
import re


# This function reads the .txt files (the solved tsps paths) and the .json files
# (to map the indices that LKH uses back to the indices that we use), to extract the
# paths and their lengths
def read_tours(
    dirname: str,
) -> tuple[dict[int, list[list[str]]], dict[int, list[int]]]:
    tour_files = sorted([f for f in os.listdir(f"{dirname}/") if f.endswith(".txt")])
    json_files = sorted([f for f in os.listdir(f"{dirname}/") if f.endswith(".json")])

    tours: dict[int, list[list[str]]] = {}
    distances: dict[int, list[int]] = {}
    for tour_file, json_file in zip(tour_files, json_files):
        match = re.match(r"tour_(\d+)_(\d+)\.txt", tour_file)
        if match:
            num_locations = int(match.group(1))
        else:
            continue

        if num_locations not in tours.keys():
            tours[num_locations] = []
            distances[num_locations] = []

        with open(f"{dirname}/{json_file}") as f:
            index_to_location = json.load(f)

        with open(f"{dirname}/{tour_file}") as f:
            lines = f.readlines()

        start: int = lines.index("TOUR_SECTION\n") + 1
        end: int = lines.index("-1\n")

        tour_indices: list[str] = [str(int(node)) for node in lines[start:end]]
        tour_locations: list[str] = [index_to_location[node] for node in tour_indices]

        length_line: str = next(
            line for line in lines if line.startswith("COMMENT : Length")
        )
        distance: int = int(length_line.split("=")[1].strip())

        tours[num_locations].append(tour_locations)
        distances[num_locations].append(distance)
    return tours, distances
