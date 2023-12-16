"""General utility functions"""

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


import json
import logging
import numpy as np


class Params:
    """Class that loads hyperparameters from a json file.

    Example:
    ```
    params = Params(json_path)
    print(params.learning_rate)
    params.learning_rate = 0.5  # change the value of learning_rate in params
    ```
    """

    def __init__(self, json_path):
        self.update(json_path)

    def save(self, json_path):
        """Saves parameters to json file"""
        with open(json_path, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    def update(self, json_path):
        """Loads parameters from json file"""
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    @property
    def dict(self):
        """Gives dict-like access to Params instance by `params.dict['learning_rate']`"""
        return self.__dict__


def set_logger(log_path):
    """Sets the logger to log info in terminal and file `log_path`.

    In general, it is useful to have a logger so that every output to the terminal is saved
    in a permanent file. Here we save it to `model_dir/train.log`.

    Example:
    ```
    logging.info("Starting training...")
    ```

    Args:
        log_path: (string) where to log
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Logging to a file
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s: %(message)s")
        )
        logger.addHandler(file_handler)

        # Logging to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(stream_handler)


def save_dict_to_json(d, json_path):
    """Saves dict of floats in json file

    Args:
        d: (dict) of float-castable values (np.float, int, float, etc.)
        json_path: (string) path to json file
    """
    with open(json_path, "w") as f:
        # We need to convert the values to float for json (it doesn't accept np.array, np.float, )
        d = {k: float(v) for k, v in d.items()}
        json.dump(d, f, indent=4)


def create_datasets(dataset, train_percent: float = 0.6, val_percent: float = 0.2):
    # split dataset into train, validation, test sets
    # test set is remaining amount
    train, val, test = np.split(
        dataset.sample(frac=1, random_state=42),
        [
            int(train_percent * len(dataset)),
            int((train_percent + val_percent) * len(dataset)),
        ],
    )

    # train.to_csv(f"../data/training-set-{today}", index=False)
    # val.to_csv(f"../data/val-set-{today}", index=False)
    # test.to_csv(f"../data/test-set-{today}", index=False)

    return train, val, test
