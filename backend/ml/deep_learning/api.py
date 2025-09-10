import os
import json
import time
from typing import Any, Dict

from .models import factory

# training/inference modules
from .training import train_cnn, train_sequence, train_transformer
from .inference import predict_cnn, predict_sequence, predict_transformer
from .inference import predict as predict_generic


AVAILABLE_MODELS = ["mlp", "cnn", "sequence", "transformer"]


def list_models() -> Dict[str, Any]:
    return {"models": AVAILABLE_MODELS}


def _save_uploaded_file(file_storage, dest_dir="/tmp") -> str:
    os.makedirs(dest_dir, exist_ok=True)
    filename = f"uploaded_{int(time.time())}.csv"
    path = os.path.join(dest_dir, filename)
    file_storage.save(path)
    return path


def train_deep(model_name: str, file_storage, form: Dict[str, str]) -> Dict[str, Any]:
    model_name = model_name.lower()
    csv_path = _save_uploaded_file(file_storage)
    config = {}
    if 'config' in form and form['config']:
        try:
            config = json.loads(form['config'])
        except Exception:
            config = {}

    # common params
    epochs = int(form.get('epochs', 5))
    batch_size = int(form.get('batch_size', 32))
    target_column = form.get('target_column', None)

    if model_name in ("mlp", "dense"):
        # For MLP use a simple training script that expects numeric CSV
        from .training.train_mlp import train_model as train_mlp
        return train_mlp(csv_path, target_column=target_column, epochs=epochs, batch_size=batch_size, config=config)

    if model_name == 'cnn':
        image_shape = None
        if 'image_shape' in form and form['image_shape']:
            try:
                # expect e.g. "(128,128,3)" or json list
                image_shape = tuple(json.loads(form['image_shape']))
            except Exception:
                try:
                    image_shape = eval(form['image_shape'])
                except Exception:
                    image_shape = None
        if image_shape is None:
            # sensible default
            image_shape = (128, 128, 3)
        return train_cnn.train_model(csv_path, image_shape=image_shape, target_column=target_column, epochs=epochs, batch_size=batch_size, config=config)

    if model_name == 'sequence':
        timesteps = int(form.get('timesteps', 10))
        return train_sequence.train_model(csv_path, target_column=target_column, timesteps=timesteps, epochs=epochs, batch_size=batch_size, config=config)

    if model_name == 'transformer':
        timesteps = int(form.get('timesteps', 10))
        return train_transformer.train_model(csv_path, target_column=target_column, timesteps=timesteps, epochs=epochs, batch_size=batch_size, config=config)

    return {"error": f"Unsupported deep model: {model_name}"}


def test_deep(model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    model_name = model_name.lower()
    model_path = payload.get('model_path')
    if not model_path:
        # provide conventional defaults if not supplied
        model_path = payload.get('model', None)

    try:
        if model_name in ('mlp', 'dense'):
            # generic numeric predictor expects input dict
            input_dict = payload.get('input')
            if input_dict is None:
                return {"error": "Missing 'input' in payload"}
            res = predict_generic.load_and_predict(model_path, input_dict)
            return {"predictions": res}

        if model_name == 'cnn':
            # input should be image array or list
            image = payload.get('input')
            if image is None:
                return {"error": "Missing 'input' image data for cnn"}
            res = predict_cnn.load_and_predict(model_path, image)
            return {"predictions": res}

        if model_name == 'sequence':
            arr = payload.get('input')
            if arr is None:
                return {"error": "Missing 'input' sequence data"}
            res = predict_sequence.load_and_predict(model_path, arr)
            return {"predictions": res}

        if model_name == 'transformer':
            arr = payload.get('input')
            if arr is None:
                return {"error": "Missing 'input' sequence data"}
            res = predict_transformer.load_and_predict(model_path, arr)
            return {"predictions": res}

        return {"error": f"Unsupported model for testing: {model_name}"}
    except Exception as e:
        return {"error": str(e)}
