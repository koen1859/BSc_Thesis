from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
)
from sklearn.model_selection import train_test_split
import pandas as pd
import math
import json


def linear_model(df):
    y = df["beta"]
    X = df.drop(columns=["beta"])

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = pd.Series(model.predict(X_test), index=y_test.index)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)

    return r2, mae, mape, y_test, y_pred


def predict_path_lengths(y_pred):
    sorted_keys = list(range(20, 90, 2))
    with open("final_results.json") as f:
        final_results = json.load(f)
    ml_results = {}

    for neighborhood in y_pred.index:
        area = final_results[neighborhood][2]
        b_hat_pred = y_pred[neighborhood]
        line_pred = [b_hat_pred * math.sqrt(n * area) for n in sorted_keys]
        line = final_results[neighborhood][3]
        mae = mean_absolute_error(line, line_pred)
        mape = mean_absolute_percentage_error(line, line_pred)
        ml_results[neighborhood] = (mae, mape)

    json.dump(ml_results)
