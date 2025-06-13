import json
import os

import pandas as pd
from sklearn.model_selection import train_test_split


def features_df() -> pd.DataFrame:
    with open("final_results.json") as f:
        final_results = json.load(f)

    features_dir = "features"
    data = []

    for filename in os.listdir(features_dir):
        if filename.endswith(".json"):
            area_name = filename.replace(".json", "").replace("'", "")
            with open(os.path.join(features_dir, filename)) as f:
                features = json.load(f)

            result = final_results.get(area_name)
            if result is None:
                continue

            beta, mae, mape, area, x, y = result

            if len(x) != len(y):
                continue

            for x, y in zip(x, y):
                row = {
                    "area_name": area_name,
                    "n": x,
                    "TSP length": y,
                }
                row.update(features)
                data.append(row)

    df = pd.DataFrame(data)
    df.set_index("area_name", inplace=True)
    df.fillna(0, inplace=True)
    print(f"df has {df.shape[0]} observations of {df.shape[1]} variables.")
    return df


def split_train_test(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    unique_areas = df.index.unique()
    train_areas, test_areas = train_test_split(
        unique_areas, test_size=test_size, random_state=random_state
    )

    df_train = df.loc[df.index.isin(train_areas)]
    df_test = df.loc[df.index.isin(test_areas)]

    print(f"Train set: {df_train.shape[0]} rows from {len(train_areas)} areas.")
    print(f"Test set: {df_test.shape[0]} rows from {len(test_areas)} areas.")

    return df_train, df_test
