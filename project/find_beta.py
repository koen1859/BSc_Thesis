import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
)


# This function estimates beta. b_hat is the average beta over all simulations in the
# neighborhood. b_hat_n is a dictionary with as index the number of locations and as values
# the corresponding beta. We do this as in previous research it was found beta differs over n
# hence to be able to make good predictions we might need to let beta vary over n.
def find_beta(lengths, area):
    b, x, y = [], [], []
    b_hat_n = {}

    for n in sorted(lengths.keys()):
        b_n = []
        for length in lengths[n]:
            b.append(length / math.sqrt(n * area))
            b_n.append(length / math.sqrt(n * area))
            x.append(n)
            y.append(length)
        b_hat_n[n] = np.mean(b_n)
    b_hat = np.mean(b)

    return x, y, b_hat, b_hat_n


# Here we make the line that relates the estimated tsp path length to n, the prediction errors
# to later plot these results and calculate the mean absolute prediction error.
def results(lengths, x, y, b_hat, area):
    sorted_keys = sorted(lengths.keys())
    line = [b_hat * math.sqrt(n * area) for n in sorted_keys]
    errors = [line[sorted_keys.index(x[i])] - y[i] for i in range(len(x))]

    y_pred = [line[sorted_keys.index(xi)] for xi in x]
    mae = mean_absolute_error(y, y_pred)
    mape = mean_absolute_percentage_error(y, y_pred)

    # mae = np.mean(np.abs(errors))
    # mape = np.mean(np.mean(np.abs(errors)) / line)

    return line, errors, mae, mape


# This function makes scatterplot of all tsp path lengths and their n, and the line that
# relates tsp path length to n,
def scatterplot(lengths, x, y, b_hat, line, filename):
    os.makedirs("plots/", exist_ok=True)
    fig = plt.figure(figsize=(20, 15))
    plt.scatter(np.log(x), np.log(y), label="Simulated values", alpha=0.6)
    plt.plot(
        np.log(sorted(lengths.keys())),
        np.log(line),
        label=f"Estimated line b = {b_hat:.2f}",
    )
    plt.xlabel("n (number of locations (log scale))")
    plt.ylabel("y (TSP path length (m) (log scale))")
    plt.legend()
    plt.title("Scatterplot of TSP path lengths with estimated line y = b * sqrt(n * A)")
    plt.savefig(f"plots/{filename}")
    plt.close(fig)


# We also make a Histogram of all prediction errors
def errorsplot(errors, filename):
    os.makedirs("plots/", exist_ok=True)
    fig = plt.figure(figsize=(20, 15))
    plt.hist(errors, label="Prediction errors", alpha=0.6)
    plt.xlabel("Prediction error (m)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.title("Histogram of TSP path length prediction errors")
    plt.savefig(f"plots/{filename}")
    plt.close(fig)
