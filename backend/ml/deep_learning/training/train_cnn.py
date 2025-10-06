"""Training wrapper for CNN models.

This improves the placeholder by:
- validating image paths
- handling categorical targets (LabelEncoder + one-hot)
- saving models to a timestamped folder under `trained_models/`
"""
import os
import time
from utils.lazy_tf import tf, is_available as tf_is_available
import numpy as np
import pandas as pd

HAS_DEPS = tf_is_available()
keras = tf.keras if HAS_DEPS else None

from ..models.cnn import get_model

try:
    from sklearn.preprocessing import LabelEncoder
except Exception:
    LabelEncoder = None


def train_model(csv_path, image_shape, target_column=None, epochs=5, batch_size=32, config=None, model_out_path=None):
    if not HAS_DEPS or pd is None:
        return {"error": "TensorFlow / pandas not available"}

    df = pd.read_csv(csv_path)
    if target_column is None:
        target_column = df.columns[-1]

    if 'image_path' not in df.columns:
        return {"error": "CSV must contain 'image_path' column with image file paths for CNN training."}

    # Minimal loader using Keras utilities, with basic validation
    try:
        # These will be available once TF is loaded via proxy
        load_img = None
        img_to_array = None
    except Exception:
        load_img = None
        img_to_array = None
    X = []
    y = []
    for idx, row in df.iterrows():
        p = row['image_path']
        if not isinstance(p, str) or not os.path.exists(p):
            return {"error": f"Image file not found: {p} (row {idx})"}
        img = load_img(p, target_size=tuple(image_shape[:2]))
        arr = img_to_array(img) / 255.0
        X.append(arr)
        y.append(row[target_column])

    X = np.stack(X)
    y = np.array(y)

    # Handle categorical target
    is_classification = False
    classes = None
    if y.dtype == object or y.dtype.kind in ('U', 'S') or (LabelEncoder is not None and y.ndim == 1 and any(isinstance(v, str) for v in y)):
        if LabelEncoder is None:
            return {"error": "sklearn is required to train classification targets"}
        le = LabelEncoder()
        y_enc = le.fit_transform(y.astype(str))
        classes = list(le.classes_)
        is_classification = True
        # convert to categorical
        y = keras.utils.to_categorical(y_enc)

    num_classes = y.shape[-1] if (is_classification and y.ndim > 1) else 1

    model = get_model(image_shape, num_classes=num_classes, config=config)

    # choose loss
    loss = 'categorical_crossentropy' if is_classification else 'mse'
    model.compile(optimizer=config.get('optimizer', 'adam') if isinstance(config, dict) else 'adam', loss=loss, metrics=config.get('metrics', ['accuracy']) if isinstance(config, dict) else None)

    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1)

    if model_out_path is None:
        ts = int(time.time())
        model_out_path = os.path.join('trained_models', f'deep_cnn_{ts}')
    os.makedirs(os.path.dirname(model_out_path) or model_out_path, exist_ok=True)
    model.save(model_out_path)
    return {"model_path": model_out_path, "classes": classes}
