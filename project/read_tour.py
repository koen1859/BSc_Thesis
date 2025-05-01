import json
import os
import re


# This function reads the .txt files (the solved tsps paths) and the .json files
# (to map the indices that LKH uses back to the indices that we use), to extract the
# paths and their lengths
def read_tours(dirname):
    tour_files = sorted([f for f in os.listdir(f"{dirname}/") if f.endswith(".txt")])
    json_files = sorted([f for f in os.listdir(f"{dirname}/") if f.endswith(".json")])

    tours, distances = {}, {}
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

        start = lines.index("TOUR_SECTION\n") + 1
        end = lines.index("-1\n")

        tour_indices = [str(int(node)) for node in lines[start:end]]
        tour_locations = [index_to_location[node] for node in tour_indices]

        length_line = next(
            line for line in lines if line.startswith("COMMENT : Length")
        )
        distance = int(length_line.split("=")[1].strip())

        tours[num_locations].append(tour_locations)
        distances[num_locations].append(distance)
    return tours, distances
