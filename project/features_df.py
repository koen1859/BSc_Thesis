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
            beta = final_results.get(area_name, [None])[0]
            features["area"] = area_name
            features["beta"] = beta
            data.append(features)

    df = pd.DataFrame(data)
    df.set_index("area", inplace=True)
    df.dropna(subset=["beta"], inplace=True)
    df.fillna(0, inplace=True)
    return df
