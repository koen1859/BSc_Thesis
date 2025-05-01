import ujson
import multiprocessing
import os
import subprocess

from distance_dict import distance_dict
from sample import sample


# This function generates a .tsp, .par and .json file to write to the disk, so LKH can solve
# the TSP later. First we take a random sample of the buildings, then create distance dictionary
# between these buildings. Also, a mapping is made to map 1,2,3,... back to the correct building
# indices since LKH can only use indices starting from 1 but we already have building indices
# from openstreetmap.
def generate_tsp(graph, i, run, dirname):
    locations = sample(graph, i)
    distances = distance_dict(graph, locations)
    index_to_location = {idx + 1: loc for idx, loc in enumerate(locations)}

    header = [
        "NAME : tsp_problem",
        "TYPE : TSP",
        f"DIMENSION : {len(locations)}",
        "EDGE_WEIGHT_TYPE : EXPLICIT",
        "EDGE_WEIGHT_FORMAT : FULL_MATRIX",
        "EDGE_WEIGHT_SECTION",
    ]
    rows = []

    for loc1 in locations:
        row = [str(int(distances[(loc1, loc2)])) for loc2 in locations]
        rows.append(" ".join(row))

    body = "\n".join(header + rows + ["EOF"])

    with open(f"{dirname}/problem_{i}_{run}.tsp", "w") as f:
        f.write(body)

    with open(f"{dirname}/index_to_location_{i}_{run}.json", "w") as f:
        ujson.dump(index_to_location, f)

    with open(f"{dirname}/problem_{i}_{run}.par", "w") as f:
        f.write(f"PROBLEM_FILE = {dirname}/problem_{i}_{run}.tsp\n")
        f.write(f"OUTPUT_TOUR_FILE = {dirname}/tour_{i}_{run}.txt\n")


def create_tsps(graph, num_runs, num_locations, dirname):
    os.makedirs(dirname, exist_ok=True)
    for i in num_locations:
        for run in range(num_runs):
            generate_tsp(graph, i, run, dirname)


# This function runs the Lin-Kernighan heuristic to solve the tsps. We do not want the output
# to display since it gives a lot of output that is not so useful to us, and in the simulation
# some information is printed, this would not be easy to read when there is a lot of stuff
# below and under it we do not need.
def solve_tsps(dirname):
    par_files = [f for f in os.listdir(dirname) if f.endswith(".par")]
    for f in par_files:
        subprocess.run(["LKH", f"{dirname}/{f}"], stdout=subprocess.DEVNULL, check=True)
