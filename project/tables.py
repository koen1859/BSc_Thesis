import json
import math

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
)


def make_results_tables():
    with open("final_results.json", "r") as f:
        final_results = json.load(f)

    with open("beta_values.tex", "w") as f:
        f.write("\\begin{longtable}{llccc}\n")
        f.write(
            "\\caption{Empirical estimates for $\\beta$, with prediction errors this beta gives for TSP path length in selected neighborhoods.} \\label{tab:results}\\\\\n"
        )
        f.write("\\hline\n")
        f.write("Province-Neighborhood & $\\beta$ & MAE (m) & MAPE (\\%) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endfirsthead\n")
        f.write("\\hline\n")
        f.write("Province-Neighborhood & $\\beta$ & MAE (m) & MAPE (\\%) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endhead\n")

        for key, values in final_results.items():
            b_hat = values[0]
            mae = values[1]
            mape = values[2]
            key = key.replace("_", " ")
            f.write(f"{key} & {b_hat:.4f} & {mae:.4f} & {mape * 100:.4f} \\\\\n")

        f.write("\\hline\n")
        f.write("\\end{longtable}\n")

    b_total, x_total, y_total, area_total = [], [], [], []
    b_avg, y_pred_avg = [], []
    for key, values in final_results.items():
        b_hat = values[0]
        area = values[3]
        x = values[4]
        y = values[5]

        b_avg.append(b_hat)

        for index, x_value in enumerate(x):
            area_total.append(area)
            x_total.append(x_value)
            y_value = y[index]
            y_total.append(y_value)
            y_pred_avg.append(b_hat * math.sqrt(x_value * area))
            b_total.append(y_value / math.sqrt(x_value * area))

    b_hat_total = np.mean(b_total)
    y_pred_total = [
        b_hat_total * math.sqrt(x_value * area_total[index])
        for index, x_value in enumerate(x_total)
    ]
    mae_total = mean_absolute_error(y_total, y_pred_total)
    mape_total = mean_absolute_percentage_error(y_total, y_pred_total)
    r2_total = r2_score(y_total, y_pred_total)

    mae_avg = mean_absolute_error(y_total, y_pred_avg)
    mape_avg = mean_absolute_percentage_error(y_total, y_pred_avg)
    r2_avg = r2_score(y_total, y_pred_avg)

    with open("small_results_table.tex", "w") as f:
        f.write("\\begin{longtable}{lccc}\n")
        f.write(
            "\\caption{Performance metrics for the BHH formula.} \\label{tab:results_small} \\\\\n"
        )
        f.write("\\hline\n")
        f.write("Model & $R^2$ & MAE (m) & MAPE (\\%) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endfirsthead\n")
        f.write("\\hline\n")
        f.write("Model & $R^2$ & MAE (m) & MAPE (\\%) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endhead\n")

        f.write(
            f"Varying $\\beta$ & {r2_avg:.2f} & {mae_avg:.2f} & {mape_avg * 100:.2f}\\\\\n"
        )
        f.write(
            f"Restricted $\\beta$ & {r2_total:.2f} & {mae_total:.2f} & {mape_total * 100:.2f}\\\\\n"
        )

        f.write("\\hline\n")
        f.write("\\end{longtable}\n")


def make_ml_results_table(results, results_reduced):
    train_results_full = results["train"]
    test_results_full = results["test"]
    train_results_reduced = results_reduced["train"]
    test_results_reduced = results_reduced["test"]

    with open("small_ml_results_table.tex", "w") as f:
        f.write("\\begin{longtable}{lccc}\n")
        f.write(
            "\\caption{Performance metrics for the Random forest models using all features and reduced features.} \\label{tab:ml_results_small} \\\\\n"
        )
        f.write("\\hline\n")
        f.write("Model & $R^2$ & MAE (m) & MAPE (\\%) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endfirsthead\n")
        f.write("\\hline\n")
        f.write("Model & $R^2$ & MAE (m) & MAPE (\\%) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endhead\n")

        f.write(
            f"Full (train) & {train_results_full['r2']:.2f} & {train_results_full['mae']:.2f} & {train_results_full['mape'] * 100:.2f}\\\\\n"
        )
        f.write(
            f"Full (test) & {test_results_full['r2']:.2f} & {test_results_full['mae']:.2f} & {test_results_full['mape'] * 100:.2f}\\\\\n"
        )
        f.write(
            f"Reduced (train) & {train_results_reduced['r2']:.2f} & {train_results_reduced['mae']:.2f} & {train_results_reduced['mape'] * 100:.2f}\\\\\n"
        )
        f.write(
            f"Reduced (test) & {test_results_reduced['r2']:.2f} & {test_results_reduced['mae']:.2f} & {test_results_reduced['mape'] * 100:.2f}\\\\\n"
        )

        f.write("\\hline\n")
        f.write("\\end{longtable}\n")

    per_area_full = results["per_area_metrics"]
    per_area_reduced = results_reduced["per_area_metrics"]
    with open("ml_results_table.tex", "w") as f:
        f.write("\\begin{longtable}{lcc}\n")
        f.write(
            "\\caption{Per-area MAPE from Random Forest models using all features and reduced features.} \\label{tab:ml_results} \\\\\n"
        )
        f.write("\\hline\n")
        f.write("Province-Neighborhood & MAPE (\\%) (F) & MAPE (\\%) (R) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endfirsthead\n")
        f.write("\\hline\n")
        f.write("Province-Neighborhood & MAPE (\\%) (F) & MAPE (\\%) (R) \\\\\n")
        f.write("\\hline\n")
        f.write("\\endhead\n")

        for area in per_area_full.index:
            mape_full = per_area_full.loc[area, "mape"] * 100
            mape_reduced = (
                per_area_reduced.loc[area, "mape"] * 100
                if area in per_area_reduced.index
                else float("nan")
            )

            area_name = area.replace("_", " ")
            f.write(f"{area_name} & {mape_full:.2f} & {mape_reduced:.2f} \\\\\n")

        total_mape_full = results["test"]["mape"] * 100
        total_mape_reduced = results_reduced["test"]["mape"] * 100

        f.write(f"Total & {total_mape_full:.2f} & {total_mape_reduced:.2f} \\\\\n")
        f.write("\\hline\n")
        f.write("\\end{longtable}\n")


if __name__ == "__main__":
    make_results_tables()
