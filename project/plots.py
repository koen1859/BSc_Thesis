import json
import matplotlib.pyplot as plt
import numpy as np


def beta_hist() -> None:
    with open("final_results.json", "r") as f:
        final_results = json.load(f)

    betas: list[float] = []
    mapes: list[float] = []
    for key in final_results:
        betas.append(final_results[key][0])
        mapes.append(final_results[key][2])

    cor: float = np.corrcoef(betas, mapes)[0, 1]
    plt.hist(betas, bins=50, edgecolor="black")
    plt.title(
        f"Distribution of Beta Values\nThe correlation between the MAPE and Beta is {cor:.3f}"
    )
    plt.xlabel("Beta")
    plt.ylabel("Frequency")
    plt.savefig("plots/histogram.png")
    plt.show()


if __name__ == "__main__":
    beta_hist()
