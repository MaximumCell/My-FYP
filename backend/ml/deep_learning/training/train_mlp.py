"""Training script for the simple MLP model.

Provides a `train_model` function to match project naming conventions.
"""

import os

try:
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
    import numpy as np
    import pandas as pd
except Exception:
    keras = None
    np = None
    pd = None


def train_model(csv_file, target_column=None, epochs=10, batch_size=32, config=None, model_out_path=None):
    """Train an MLP on a CSV dataset and save the trained model to disk.

    Returns dict with model_path and basic metrics or error.
    """
    if pd is None:
        return {"error": "TensorFlow / pandas not installed"}

    try:
        df = pd.read_csv(csv_file)
        if target_column is None:
            target_column = df.columns[-1]

        # Select only numeric columns for features
        numeric_columns = df.select_dtypes(include=['number']).columns
        feature_columns = [col for col in numeric_columns if col != target_column]
        
        if len(feature_columns) == 0:
            return {"error": "No numeric features found in the dataset"}
        
        X = df[feature_columns].values
        y = df[target_column].values

        # Basic data validation
        if X.shape[0] < 10:
            return {"error": "Dataset too small (need at least 10 samples)"}

        # Data preprocessing - normalize features and target
        from sklearn.preprocessing import StandardScaler
        
        # Scale features
        scaler_X = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        
        # Scale target if it has large values
        scaler_y = StandardScaler()
        y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Store scalers for later use in predictions
        import joblib
        scalers_path = model_out_path + '_scalers.pkl' if model_out_path else 'deep_mlp_scalers.pkl'

        # Apply config if provided
        hidden_layers = [128, 64] if config is None else config.get('hidden_layers', [128, 64])
        dropout_rate = 0.2 if config is None else config.get('dropout', 0.2)
        learning_rate = 0.001 if config is None else config.get('learning_rate', 0.001)

        input_shape = X_scaled.shape[1:]
        
        # Build model architecture
        model = keras.Sequential([keras.layers.InputLayer(shape=input_shape)])
        
        for i, units in enumerate(hidden_layers):
            model.add(keras.layers.Dense(units, activation='relu'))
            if dropout_rate > 0:
                model.add(keras.layers.Dropout(dropout_rate))
        
        model.add(keras.layers.Dense(1))  # Output layer
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

        # Train model and capture history with scaled data
        history = model.fit(
            X_scaled, y_scaled, 
            epochs=epochs, 
            batch_size=batch_size, 
            validation_split=0.2,
            verbose=1
        )

        # Generate unique model name
        import time
        timestamp = int(time.time())
        if model_out_path is None:
            model_out_path = os.path.join('trained_models', f'deep_mlp_{timestamp}.keras')
        elif not model_out_path.endswith(('.keras', '.h5')):
            model_out_path = f"{model_out_path}.keras"
        
        os.makedirs(os.path.dirname(model_out_path) or '.', exist_ok=True)
        model.save(model_out_path)
        
        # Save scalers for prediction use
        scalers_path = model_out_path.replace('.keras', '_scalers.pkl')
        joblib.dump({
            'scaler_X': scaler_X,
            'scaler_y': scaler_y
        }, scalers_path)

        # Get final metrics (these are on scaled data)
        final_loss_scaled = float(history.history['loss'][-1])
        final_val_loss_scaled = float(history.history['val_loss'][-1])
        final_mae_scaled = float(history.history['mae'][-1])
        final_val_mae_scaled = float(history.history['val_mae'][-1])
        
        # Convert MAE back to original scale for better interpretation
        # Since we normalized y, we need to scale back the MAE
        y_std = scaler_y.scale_[0]
        final_mae_original = final_mae_scaled * y_std
        final_val_mae_original = final_val_mae_scaled * y_std

        return {
            "message": f"Deep MLP model trained successfully! Trained for {epochs} epochs.",
            "model_path": model_out_path,
            "final_loss": final_loss_scaled,
            "final_val_loss": final_val_loss_scaled,
            "final_mae": final_mae_original,
            "final_val_mae": final_val_mae_original,
            "final_mae_scaled": final_mae_scaled,
            "final_val_mae_scaled": final_val_mae_scaled,
            "epochs_trained": epochs,
            "samples_used": X.shape[0],
            "features_used": X.shape[1],
            "target_std": float(y_std),
            "architecture": {
                "hidden_layers": hidden_layers,
                "dropout_rate": dropout_rate,
                "learning_rate": learning_rate
            }
        }
        
    except Exception as e:
        return {"error": f"Training failed: {str(e)}"}
