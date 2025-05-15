from run_simulation import run_simulation, interpret_results, run_ml
from tables import make_results_table
from areas import areas
import multiprocessing

tasks = [
    (DB, neighborhood)
    for DB, neighborhoods in areas.items()
    for neighborhood in neighborhoods
]
num_threads = multiprocessing.cpu_count()

with multiprocessing.Pool(num_threads) as pool:
    results = pool.starmap(run_simulation, tasks)

final_results = dict(results)
make_results_table(final_results)

print("ML to estimate beta...")
r2, mae, mape, y_test, y_pred = run_ml()
print(r2, mae, mape)
with open("ml_results.txt", "w") as f:
    f.write(f"""
            r2: {r2}\n
            mae: {mae}\n
            mape: {mape * 100}\n
    """)
