import ujson


def make_results_table(final_results):
    with open("final_results.json", "w") as f:
        ujson.dump(final_results, f)

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
            key = key.replace("_", " ")
            f.write(
                f"{key} & {values[0]:.4f} & {values[1]:.4f} & {values[2]*100:.4f} \\\\\n"
            )

        f.write("\\hline\n")
        f.write("\\end{longtable}\n")
