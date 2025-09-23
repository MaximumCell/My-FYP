# ML Routes
from flask import Blueprint, request, jsonify, send_file
import json
from ml.train_model import train_model, test_model, models as regression_models
from ml.train_classifier import train_classifier, get_classifier_models, classification_models
from ml.recommend_model import recommend_model
from ml.get_coloum import get_coloum
from ml.test_classifier import test_classifier
from ml.deep_learning import api as deep_api
import os
import pandas as pd

ml_bp = Blueprint('ml', __name__)

# Regression Endpoints
@ml_bp.route('/models/regression', methods=['GET'])
def get_regression_models_route():
    model_names = list(regression_models.keys())
    return jsonify(model_names)

@ml_bp.route('/train/regression', methods=['POST'])
def train_regression():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    model_name = request.form.get('model')
    target_column = request.form.get('target_column', None)
    # Optional training parameters
    test_size_raw = request.form.get('test_size', None)
    scaling_method = request.form.get('scaling_method', 'standard')
    hyperparams_raw = request.form.get('hyperparams', None)

    # parse numeric and json values
    try:
        test_size = float(test_size_raw) if test_size_raw is not None else 0.2
    except Exception:
        test_size = 0.2
    try:
        hyperparams = json.loads(hyperparams_raw) if hyperparams_raw else {}
    except Exception:
        hyperparams = {}

    if not model_name:
        return jsonify({"error": "Model name is required"}), 400

    try:
        result = train_model(file, model_name, target_column, test_size=test_size, hyperparams=hyperparams, scaling_method=scaling_method)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ml_bp.route('/test/regression', methods=['POST'])
def test_regression():
    try:
        data = request.json
        model_name = data.get("model")
        new_data = data.get("new_data")

        if not model_name or not new_data:
            return jsonify({"error": "Model name and input data required"}), 400

        result = test_model(model_name, new_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@ml_bp.route('/download/regression/<model_name>', methods=['GET'])
def download_regression(model_name):
    model_path = f"trained_models/{model_name}_pipeline.pkl"
    if os.path.exists(model_path):
        return send_file(model_path, as_attachment=True)
    return jsonify({"error": "Model not found"}), 400

# Classification Endpoints
@ml_bp.route('/models/classification', methods=['GET'])
def get_classification_models():
    model_names = get_classifier_models()
    return jsonify(model_names)

@ml_bp.route('/train/classification', methods=['POST'])
def train_classification():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    model_name = request.form.get('model')
    target_column = request.form.get('target_column', None)
    # Optional training parameters
    test_size_raw = request.form.get('test_size', None)
    scaling_method = request.form.get('scaling_method', 'standard')
    hyperparams_raw = request.form.get('hyperparams', None)

    try:
        test_size = float(test_size_raw) if test_size_raw is not None else 0.2
    except Exception:
        test_size = 0.2
    try:
        hyperparams = json.loads(hyperparams_raw) if hyperparams_raw else {}
    except Exception:
        hyperparams = {}

    if not model_name:
        return jsonify({"error": "Model name is required"}), 400

    try:
        result = train_classifier(file, model_name, target_column, test_size=test_size, hyperparams=hyperparams, scaling_method=scaling_method)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ml_bp.route('/test/classification', methods=['POST'])
def test_classification():
    try:
        data = request.json
        model_name = data.get("model")
        new_data = data.get("new_data")

        if not model_name or not new_data:
            return jsonify({"error": "Model name and input data required"}), 400

        result = test_classifier(model_name, new_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@ml_bp.route('/download/classification/<model_name>', methods=['GET'])
def download_classification(model_name):
    model_path = f"trained_classifiers/{model_name}_classifier_pipeline.pkl"
    if os.path.exists(model_path):
        return send_file(model_path, as_attachment=True)
    return jsonify({"error": "Classifier model not found"}), 404

# Other ML Endpoints
@ml_bp.route("/recommend", methods=["POST"])
def recommend_route():
    file = request.files["file"]
    df = pd.read_csv(file)
    recommended_model = recommend_model(df)
    return jsonify({"recommended_model": recommended_model})

@ml_bp.route('/get_columns', methods=['POST'])
def get_columns():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        column_names = get_coloum(file)
        if "error" in column_names:
            return jsonify(column_names), 500
        else:
            return jsonify({"columns": column_names}), 200


# Deep learning endpoints
@ml_bp.route('/deep/models', methods=['GET'])
def deep_list_models():
    try:
        return jsonify(deep_api.list_models())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ml_bp.route('/deep/train', methods=['POST'])
def deep_train():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    model_name = request.form.get('model')
    if not model_name:
        return jsonify({"error": "Model name is required"}), 400
    try:
        result = deep_api.train_deep(model_name, file, request.form)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ml_bp.route('/deep/test', methods=['POST'])
def deep_test():
    try:
        data = request.json
        model_name = data.get('model')
        if not model_name:
            return jsonify({"error": "Model name is required"}), 400
        result = deep_api.test_deep(model_name, data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
