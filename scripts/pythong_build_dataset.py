#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
This is a Python script header.

This header contains information about the script, such as its name, author, version, license, and a detailed description of its purpose and functionality.

It also includes the shebang line, which tells the operating system which interpreter to use to run the script.
"""

# Author: <author>
# Project: <project>
# Version: 1.0.0
# Release Date: <date>
# License: MIT

# Description:
# This script is a comprehensive and versatile tool designed to perform a variety of tasks, including data manipulation, text processing, and machine learning. It is highly customizable and can be adapted to a wide range of applications.

# Usage:
# To run this script, save it as a .py file and execute it from the command line using the following command:
# python <file-name>.py

# Example:
# python <file-name>.py --input data.csv --output results.txt

# Arguments:
# --input: Specifies the input file
# --output: Specifies the output file
# --help: Displays this help message


import pandas as pd
import numpy as np
import toolbox  # my own little package I made to help with curation work

csv_path = "../data/cleaned-data-20231214.csv"
df = pd.read_csv(csv_path, low_memory=False)

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
print("Original dataset info")
df.info()

# focusing on file annotations first
df = df[df["TYPE"] != "folder"]


# drop any missing values to develop training/test sets
df_full = df.dropna(how="any").copy(deep=True)
new_shape = df_full.shape

print("-" * 50)
print("New dataset info")
df_full.info()

print("-" * 50)
print(
    f"Rows removed: {(np.array(og_shape) - np.array(new_shape))[0]} \
        \nPercentage of original dataframe {round(((np.array(og_shape) - np.array(new_shape))[0]/np.array(og_shape))[0] * 100,2)}%"
)

# split dataset into train, validation, test sets
training_percent = 0.6
validation_percent = training_percent + 0.2
# test set is remaining amount

train, validate, test = np.split(
    df.sample(frac=1, random_state=42),
    [int(training_percent * len(df)), int(validation_percent * len(df))],
)
