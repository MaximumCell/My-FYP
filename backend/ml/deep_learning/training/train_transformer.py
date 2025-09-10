"""Training wrapper for transformer models with basic validation and timestamped saving."""
import os
import time
try:
    from tensorflow import keras
    import numpy as np
    import pandas as pd
except Exception:
    keras = None
    np = None
    pd = None

from ..models.transformer import get_model


def train_model(csv_path, target_column=None, timesteps=10, epochs=5, batch_size=32, config=None, model_out_path=None):
    if pd is None or keras is None:
        return {"error": "TensorFlow / pandas not installed"}
    df = pd.read_csv(csv_path)
    if target_column is None:
        target_column = df.columns[-1]

    X_all = df.drop(columns=[target_column]).select_dtypes(include=['number']).values
    y_all = df[target_column].values
    if X_all.shape[0] <= timesteps:
        return {"error": "Not enough rows for the requested timesteps"}

    X = []
    y = []
    for i in range(len(X_all) - timesteps):
        X.append(X_all[i:i+timesteps])
        y.append(y_all[i+timesteps])
    X = np.array(X)
    y = np.array(y)

    input_shape = X.shape[1:]
    model = get_model(input_shape, output_units=1, config=config)

    model.compile(optimizer=config.get('optimizer', 'adam') if isinstance(config, dict) else 'adam', loss='mse', metrics=config.get('metrics', ['mae']) if isinstance(config, dict) else ['mae'])
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1)

    if model_out_path is None:
        ts = int(time.time())
        model_out_path = os.path.join('trained_models', f'deep_transformer_{ts}')
    os.makedirs(os.path.dirname(model_out_path) or model_out_path, exist_ok=True)
    model.save(model_out_path)
    return {"model_path": model_out_path}
