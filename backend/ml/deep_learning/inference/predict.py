"""Inference wrapper for Keras models."""

try:
    from tensorflow import keras
    import numpy as np
    import pandas as pd
except Exception:
    keras = None
    np = None
    pd = None


def load_and_predict(model_path, input_dict):
    if keras is None:
        raise RuntimeError("TensorFlow not installed")
    model = keras.models.load_model(model_path)
    # Expect input_dict to be a single-row mapping of feature->value
    df = pd.DataFrame([input_dict])
    X = df.select_dtypes(include=['number']).values
    preds = model.predict(X)
    return preds.tolist()
