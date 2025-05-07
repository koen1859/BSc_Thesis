from run_simulation import run_simulation, interpret_results, run_ml
from areas import areas
import ujson
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

with open("final_results.json", "w") as f:
    ujson.dump(final_results, f)


with open("beta_values.tex", "w") as f:
    f.write("\\begin{longtable}{llccc}\cn")
    f.write(
        "\\caption{Empirical estimates for $\\beta$ in selected neighborhoods.} \\label{tab:results}\\\\\n"
    )
    f.write("\\hline\n")
    f.write("Province & Neighborhood & $\\beta$ & MAE (m) & MAPE (\\%) \\\\\n")
    f.write("\\hline\n")
    f.write("\\endfirsthead\n")
    f.write("\\hline\n")
    f.write("Province & Neighborhood & $\\beta$ & MAE (m) & MAPE (\\%) \\\\\n")
    f.write("\\hline\n")
    f.write("\\endhead\n")

    for key, values in final_results.items():
        db, neighborhood = key.split("-", 1)
        neighborhood = neighborhood.replace("_", " ")
        db = db.replace("_", " ")
        f.write(
            f"{db} & {neighborhood} & {values[0]:.4f} & {values[1]:.4f} & {values[2]:.4f} \\\\\n"
        )

    f.write("\\hline\n")
    f.write("\\end{longtable}\n")

print("ML to estimate beta...")
r2, mae, mape, y_test, y_pred = run_ml()
print(f"r2: {r2}, mae: {mae}, mape: {mape}")
