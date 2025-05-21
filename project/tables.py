from sklearn.metrics.pairwise import np
import ujson
import math
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import numpy as np


def make_results_table(final_results):
    with open("final_results.json", "w") as f:
        ujson.dump(final_results, f)

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

    b_hat_avg = np.mean(b_avg)
    mae_avg = mean_absolute_error(y_total, y_pred_avg)
    mape_avg = mean_absolute_percentage_error(y_total, y_pred_avg)

    final_results["Average"] = [b_hat_avg, mae_avg, mape_avg]
    final_results["Total"] = [b_hat_total, mae_total, mape_total]

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
