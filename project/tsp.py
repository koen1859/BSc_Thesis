import os
import subprocess


# This function runs the Lin-Kernighan heuristic to solve the tsps. We do not want the output
# to display since it gives a lot of output that is not so useful to us, and in the simulation
# some information is printed, this would not be easy to read when there is a lot of stuff
# below and under it we do not need.
def solve_tsps(dirname: str) -> None:
    par_files = [f for f in os.listdir(dirname) if f.endswith(".par")]
    for f in par_files:
        subprocess.run(["LKH", f"{dirname}/{f}"], stdout=subprocess.DEVNULL, check=True)
