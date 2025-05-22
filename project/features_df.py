import os
import json
import pandas as pd


def features_df():
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
                    "area": area_name,
                    "n": x,
                    "TSP length": y,
                }
                row.update(features)
                data.append(row)

    df = pd.DataFrame(data)
    df.set_index("area", inplace=True)
    df.fillna(0, inplace=True)
    print(f"df has {df.shape[0]} observations of {df.shape[1]} variables.")
    return df
