from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
)
from sklearn.model_selection import train_test_split, GridSearchCV
import pandas as pd


def random_forest(df):
    y = df["TSP length"]
    X = df.drop(columns=["TSP length"])

    # scaler = StandardScaler()
    # X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

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

    y_pred = pd.Series(model.predict(X_test), index=y_test.index)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)

    return r2, mae, mape, y_test, y_pred
