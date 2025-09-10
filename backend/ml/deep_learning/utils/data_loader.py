"""Simple data loader and preprocessing helpers for deep learning models.

These are intentionally minimal — adapt them to your real dataset and preprocessing needs.
"""

import pandas as pd
import numpy as np


def load_csv_numeric(csv_path, target_column=None):
    df = pd.read_csv(csv_path)
    if target_column is None:
        target_column = df.columns[-1]
    X = df.drop(columns=[target_column]).select_dtypes(include=['number'])
    y = df[target_column]
    return X.values, y.values


def normalize_numpy(X):
    mu = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    std[std == 0] = 1.0
    return (X - mu) / std
