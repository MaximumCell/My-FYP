"""Inference wrapper for Keras models."""

import os

try:
    from tensorflow import keras
    import numpy as np
    import pandas as pd
    import joblib
except Exception:
    keras = None
    np = None
    pd = None
    joblib = None


def load_and_predict(model_path, input_dict):
    if keras is None:
        raise RuntimeError("TensorFlow not installed")
    
    # If model_path doesn't include full path, construct it
    if not os.path.isabs(model_path):
        # Try to find the model in common locations
        possible_paths = [
            os.path.join('trained_models', f'{model_path}.keras'),
            os.path.join('trained_models', model_path),
            os.path.join('backend', 'trained_models', f'{model_path}.keras'),
            os.path.join('backend', 'trained_models', model_path),
            f'{model_path}.keras',
            model_path
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if found_path is None:
            raise FileNotFoundError(f"Model not found. Tried paths: {possible_paths}")
        
        model_path = found_path
    
    # Ensure the model path has the correct extension
    if not model_path.endswith(('.keras', '.h5')):
        # Try adding .keras extension
        keras_path = f"{model_path}.keras"
        if os.path.exists(keras_path):
            model_path = keras_path
        else:
            raise FileNotFoundError(f"Model file not found: {model_path} (tried .keras extension)")
    
    # Load the model
    model = keras.models.load_model(model_path)
    
    # Try to load scalers if they exist
    scaler_path = model_path.replace('.keras', '_scalers.pkl').replace('.h5', '_scalers.pkl')
    scalers = None
    
    if os.path.exists(scaler_path) and joblib is not None:
        try:
            scalers = joblib.load(scaler_path)
        except Exception as e:
            print(f"Warning: Could not load scalers from {scaler_path}: {e}")
    
    # Prepare input data
    df = pd.DataFrame([input_dict])
    X = df.select_dtypes(include=['number']).values
    
    if X.shape[1] == 0:
        raise ValueError("No numeric features found in input data")
    
    # Apply feature scaling if scalers are available
    if scalers and 'scaler_X' in scalers:
        try:
            X = scalers['scaler_X'].transform(X)
        except Exception as e:
            print(f"Warning: Could not apply feature scaling: {e}")
    
    # Make prediction
    preds = model.predict(X, verbose=0)
    
    # Apply inverse scaling to predictions if scalers are available
    if scalers and 'scaler_y' in scalers:
        try:
            preds = scalers['scaler_y'].inverse_transform(preds)
        except Exception as e:
            print(f"Warning: Could not apply inverse scaling to predictions: {e}")
    
    return preds.tolist()
