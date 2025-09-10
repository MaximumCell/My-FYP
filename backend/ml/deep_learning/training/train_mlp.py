"""Training script for the simple MLP model.

Provides a `train_model` function to match project naming conventions.
"""

import os

try:
    from tensorflow import keras
    import numpy as np
    import pandas as pd
except Exception:
    keras = None
    np = None
    pd = None


def train_model(csv_file, target_column=None, epochs=10, batch_size=32, model_out_path=None):
    """Train an MLP on a CSV dataset and save the trained model to disk.

    Returns dict with model_path and basic metrics or error.
    """
    if pd is None:
        return {"error": "TensorFlow / pandas not installed"}

    df = pd.read_csv(csv_file)
    if target_column is None:
        target_column = df.columns[-1]

    X = df.drop(columns=[target_column]).select_dtypes(include=['number']).values
    y = df[target_column].values

    input_shape = X.shape[1:]
    model = keras.Sequential([
        keras.layers.InputLayer(input_shape=input_shape),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1)

    if model_out_path is None:
        model_out_path = os.path.join('trained_models', 'deep_mlp')
    os.makedirs(os.path.dirname(model_out_path) or '.', exist_ok=True)
    model.save(model_out_path)

    return {"model_path": model_out_path}
