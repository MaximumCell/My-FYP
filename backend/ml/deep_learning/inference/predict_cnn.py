"""CNN inference wrapper."""
try:
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
    import numpy as np
    import pandas as pd
except Exception:
    keras = None
    np = None
    pd = None


def load_and_predict(model_path, image_array):
    if keras is None:
        raise RuntimeError("TensorFlow not installed")
    model = keras.models.load_model(model_path)
    # image_array expected shape (H, W, C) or batch (N, H, W, C)
    arr = np.array(image_array)
    if arr.ndim == 3:
        arr = np.expand_dims(arr, 0)
    preds = model.predict(arr)
    return preds.tolist()
