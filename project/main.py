from run_simulation import run_simulation, interpret_results, run_ml
from tables import make_results_table, make_ml_table
from areas import areas
import multiprocessing

tasks = [
    (DB, neighborhood)
    for DB, neighborhoods in areas.items()
    for neighborhood in neighborhoods
]
num_threads = multiprocessing.cpu_count()

with multiprocessing.Pool(num_threads) as pool:
    results = pool.starmap(interpret_results, tasks)

final_results = dict(results)
make_results_table(final_results)

print("ML to estimate beta...")
r2, mae, mape, y_test, y_pred = run_ml()
print(r2, mae, mape, y_test, y_pred)
# make_ml_table(ml_results)
