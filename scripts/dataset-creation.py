# Dataset Creation
# Setup
from datetime import datetime
import os
import pandas as pd
import numpy as np

today = datetime.now().strftime("%Y%m%d")

csv_path = "../data/cleaned-data-20231215.csv"  # replace later with config file

dirname = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(dirname, csv_path)

df = pd.read_csv(csv_path, low_memory=False)

# Feature selection
df = df.loc[
    :,
    [
        "ID",
        "TYPE",
        "TABLE",
        "NAME",
        "FILEFORMAT",
        "STUDY",
        "ASSAY",
        "DATATYPE",
        "DATASUBTYPE",
        "RESOURCETYPE",
    ],
]

# Explode list columns into rows
df["ASSAY"] = df["ASSAY"].str.split(",")
df = df.explode("ASSAY")


og_shape = df.shape
# print("Original dataset info")
# df.info()

# focusing on file annotations first
df = df[df["TYPE"] != "folder"]

# drop any missing values to develop training/test sets
df_full = df.dropna(how="any")
new_shape = df_full.shape


df.loc[~df.index.isin(df_full.index),].to_csv(
    os.path.join(dirname, f"../data/testing-dataset-withNulls-{today}.csv", index=False)
)
# print("-" * 50)
# print("New dataset info")
# df_full.info()

# print("-" * 50)
print(
    f"Rows removed: {(np.array(og_shape) - np.array(new_shape))[0]} \
        \nPercentage of original dataframe {round(((np.array(og_shape) - np.array(new_shape))[0]/np.array(og_shape))[0] * 100,2)}%"
)

df_full.to_csv(os.path.join(dirname, f"../data/complete-dataset-{today}"), index=False)
