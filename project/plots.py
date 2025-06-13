import json

import matplotlib.pyplot as plt
import numpy as np


def beta_hist() -> None:
    with open("final_results.json", "r") as f:
        final_results = json.load(f)

    betas: list[float] = []
    for key in final_results:
        betas.append(final_results[key][0])

    plt.hist(betas, bins=50, edgecolor="black")
    plt.title("Distribution of Beta Values")
    plt.xlabel("Beta")
    plt.ylabel("Frequency")
    plt.savefig("plots/histogram.png")


def beta_vs_mape() -> None:
    with open("final_results.json", "r") as f:
        final_results = json.load(f)

    betas: list[float] = []
    mapes: list[float] = []
    for key in final_results:
        betas.append(final_results[key][0])
        mapes.append(final_results[key][2])

    cor: float = np.corrcoef(betas, mapes)[0, 1]
    plt.scatter(betas, mapes, alpha=0.6)
    plt.title(f"MAPE vs Beta\nCorrelation coefficient is {cor:.3f}")
    plt.xlabel("Beta")
    plt.ylabel("MAPE")
    plt.savefig("plots/MAPE_vs_beta.png")


if __name__ == "__main__":
    beta_vs_mape()
