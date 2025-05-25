from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
)
from sklearn.model_selection import GridSearchCV
import pandas as pd
import matplotlib.pyplot as plt


def random_forest(df_train: pd.DataFrame, df_test: pd.DataFrame):
    y_train = df_train["TSP length"]
    X_train = df_train.drop(columns=["TSP length"])
    y_test = df_test["TSP length"]
    X_test = df_test.drop(columns=["TSP length"])

    param_grid = {
        "n_estimators": [10, 50, 100, 200, 300],
        "max_depth": [None, 10, 20],
    }

    grid_search = GridSearchCV(
        RandomForestRegressor(random_state=42),
        param_grid,
        cv=2,
        scoring="r2",
        n_jobs=-1,
        verbose=1,
    )
    grid_search.fit(X_train, y_train)
    model = grid_search.best_estimator_

    y_train_pred = pd.Series(model.predict(X_train), index=y_train.index)
    y_test_pred = pd.Series(model.predict(X_test), index=y_test.index)

    r2_train = r2_score(y_train, y_train_pred)
    mae_train = mean_absolute_error(y_train, y_train_pred)
    mape_train = mean_absolute_percentage_error(y_train, y_train_pred)

    r2_test = r2_score(y_test, y_test_pred)
    mae_test = mean_absolute_error(y_test, y_test_pred)
    mape_test = mean_absolute_percentage_error(y_test, y_test_pred)

    per_area = pd.DataFrame(
        {
            "y_true": y_test,
            "y_pred": y_test_pred,
        }
    )
    per_area_metrics = per_area.groupby(per_area.index).apply(
        lambda df: pd.Series(
            {
                "mae": mean_absolute_error(df["y_true"], df["y_pred"]),
                "mape": mean_absolute_percentage_error(df["y_true"], df["y_pred"]),
            }
        )
    )

    feature_importances = pd.Series(
        model.feature_importances_, index=X_train.columns
    ).sort_values(ascending=False)

    results = {
        "train": {"r2": r2_train, "mae": mae_train, "mape": mape_train},
        "test": {"r2": r2_test, "mae": mae_test, "mape": mape_test},
        "y_test": y_test,
        "y_test_pred": y_test_pred,
        "per_area_metrics": per_area_metrics,
        "feature_importances": feature_importances,
    }

    results["feature_importances"].head(15).plot(kind="barh")
    plt.gca().invert_yaxis()
    plt.title("Top Feature Importances")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig("plots/feature_importances_full.png")

    return results


def feature_importance(df_train, df_test, results):
    threshold = 0.003
    important_features = results["feature_importances"][
        results["feature_importances"] > threshold
    ].index.tolist()

    df_train_reduced = df_train[important_features + ["TSP length"]]
    df_test_reduced = df_test[important_features + ["TSP length"]]
    results_reduced = random_forest(df_train_reduced, df_test_reduced)

    results_reduced["feature_importances"].head(15).plot(kind="barh")
    plt.gca().invert_yaxis()
    plt.title("Top Feature Importances")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig("plots/feature_importances_reduced.png")

    return results_reduced
