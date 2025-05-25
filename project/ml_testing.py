from run_simulation import run_ml

# from features_df import features_df, split_train_test
# from ml_model import random_forest, feature_importance
# from tables import make_ml_results_table
# import pandas as pd
#
# df: pd.DataFrame = features_df()
# df_train: pd.DataFrame
# df_test: pd.DataFrame
# df_train, df_test = split_train_test(df)
# results = random_forest(df_train, df_test)
# results_reduced = feature_importance(df_train, df_test, results)
# with open("ml_results.txt", "w") as f:
#     f.write(f"Full model:\n{results['train']}\n{results['test']}")
#     f.write(f"Reduced model:\n{results_reduced['train']}\n{results_reduced['test']}")
# make_ml_results_table(results, results_reduced)
run_ml()
