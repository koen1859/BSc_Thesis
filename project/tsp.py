import os
import subprocess


# This function runs the Lin-Kernighan heuristic to solve the TSPs
def solve_tsps(dirname: str) -> None:
    par_files = [f for f in os.listdir(dirname) if f.endswith(".par")] # Find all parameter files
    for f in par_files:
        subprocess.run(["LKH", f"{dirname}/{f}"], stdout=subprocess.DEVNULL, check=True)
