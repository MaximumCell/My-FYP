"""
Physics Simulation & ML Project - Backend API
===========================================

This Flask application provides REST API endpoints for:
- Machine Learning model training and testing
- Physics simulation with visualization
- Model recommendation system
- Data processing and analysis

Author: MaximumCell
Project: My-FYP
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from components.train_model import train_model, test_model, models as regression_models
from components.train_classifier import train_classifier, get_classifier_models, classification_models
from components.recommend_model import recommend_model
from components.get_coloum import get_coloum
import numpy as np
import pandas as pd
from components.run_simulation import run_simulation
from components.test_classifier import test_classifier


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ Allow requests from any origin

# --- Regression Endpoints ---
@app.route('/models/regression', methods=['GET'])
def get_regression_models():
    """Return a list of available regression models."""
    model_names = list(regression_models.keys())  # Get the list of model names
    return jsonify(model_names)

@app.route('/train/regression', methods=['POST'])
def train_regression_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    model_name = request.form.get('model')
    target_column = request.form.get('target_column', None)  # ✅ Default to None

    if not model_name:
        return jsonify({"error": "Model name is required"}), 400  # ✅ Ensure model is always provided

    try:
        result = train_model(file, model_name, target_column)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # ✅ Catch unexpected errors

@app.route('/test/regression', methods=['POST'])
def test_regression_route():
    try:
        data = request.json
        model_name = data.get("model")
        new_data = data.get("new_data")

        if not model_name or not new_data:
            return jsonify({"error": "Model name and input data required"}), 400

        print(f"Received Test Data (Regression): {new_data}") # Log received data

        result = test_model(model_name, new_data) # Pass the dictionary to test_model

        print(f"Test Result (Regression): {result}")
        return jsonify(result)

    except Exception as e:
        print(f"🔥 Internal Server Error (Regression): {str(e)}")  # ✅ Print exact error
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/download/regression/<model_name>', methods=['GET'])
def download_regression_model(model_name):
    print(f"Downloading model: {model_name}")  # Log the model name being downloaded
    model_path = f"trained_models/{model_name}_pipeline.pkl"
    if os.path.exists(model_path):
        return send_file(model_path, as_attachment=True)
    return jsonify({"error": "Model not found"}), 400

# --- Classification Endpoints ---
@app.route('/models/classification', methods=['GET'])
def get_classification_models_route():
    """Return a list of available classification models."""
    model_names = get_classifier_models()
    return jsonify(model_names)

@app.route('/train/classification', methods=['POST'])
def train_classification_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    model_name = request.form.get('model')
    target_column = request.form.get('target_column', None)

    if not model_name:
        return jsonify({"error": "Model name is required"}), 400

    try:
        result = train_classifier(file, model_name, target_column)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test/classification', methods=['POST'])
def test_classification_route():
    try:
        data = request.json
        model_name = data.get("model")
        new_data = data.get("new_data")

        if not model_name or not new_data:
            return jsonify({"error": "Model name and input data required"}), 400

        print(f"Received Test Data (Classification): {new_data}")

        result = test_classifier(model_name, new_data)

        print(f"Test Result (Classification): {result}")
        return jsonify(result)

    except Exception as e:
        print(f"🔥 Internal Server Error (Classification): {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/download/classification/<model_name>', methods=['GET'])
def download_classification_model(model_name):
    model_path = f"trained_classifiers/{model_name}_classifier_pipeline.pkl"
    if os.path.exists(model_path):
        return send_file(model_path, as_attachment=True)
    return jsonify({"error": "Classifier model not found"}), 404

# --- Other Endpoints (Keep as they are) ---
@app.route("/recommend", methods=["POST"])
def recommend():
    file = request.files["file"]
    df = pd.read_csv(file)

    recommended_model = recommend_model(df)
    return jsonify({"recommended_model": recommended_model})

@app.route('/simulation', methods=['POST'])
def simulation_route():
    """Endpoint for running simulations."""
    data = request.json  # Receive JSON data for the simulation
    result = run_simulation(data)  # Call the simulation function
    return jsonify(result)

@app.route('/download_plot', methods=['GET'])
def download_plot():
    """Endpoint to serve the generated plot."""
    plot_path = "plots/simulation_plot.png"
    return send_file(plot_path, mimetype='image/png', as_attachment=True)

@app.route('/get_columns', methods=['POST'])
def get_columns_route():
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

if __name__ == '__main__':
    app.run(debug=True)