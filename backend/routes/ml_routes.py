# ML Routes
from flask import Blueprint, request, jsonify, send_file
import json
from ml.train_model import train_model, test_model, models as regression_models
from ml.train_classifier import train_classifier, get_classifier_models, classification_models
from ml.recommend_model import recommend_model
from ml.get_coloum import get_coloum
from ml.test_classifier import test_classifier
from ml.data_analysis import analyze_data_quality, get_sample_input_format
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

@ml_bp.route('/analyze_data', methods=['POST'])
def analyze_data():
    """Analyze uploaded data for preview and quality insights."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    target_column = request.form.get('target_column', None)
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        result = analyze_data_quality(file, target_column)
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@ml_bp.route('/sample_input', methods=['POST'])
def get_sample_input():
    """Get sample input format for model testing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    target_column = request.form.get('target_column', None)
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        result = get_sample_input_format(file, target_column)
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": f"Failed to generate sample input: {str(e)}"}), 500


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


@ml_bp.route('/download/deep-learning/<model_name>', methods=['GET'])
def download_deep_learning(model_name):
    # Deep learning models can be .keras or .pkl files
    # Try different possible paths and extensions
    possible_paths = [
        f"trained_models/{model_name}.keras",
        f"trained_models/{model_name}.pkl",
        f"trained_models/{model_name}_pipeline.pkl",
        f"trained_models/deep_mlp_{model_name}.keras"
    ]
    
    # Also try to find the model by pattern if exact name doesn't work
    trained_models_dir = "trained_models"
    if os.path.exists(trained_models_dir):
        import glob
        # Look for files containing the model name
        pattern_paths = [
            f"trained_models/*{model_name}*.keras",
            f"trained_models/*{model_name}*.pkl"
        ]
        for pattern in pattern_paths:
            matching_files = glob.glob(pattern)
            if matching_files:
                # Get the most recent one
                possible_paths.extend(matching_files)
    
    # Try each possible path
    for model_path in possible_paths:
        if os.path.exists(model_path):
            return send_file(model_path, as_attachment=True)
    
    return jsonify({"error": "Deep learning model not found"}), 404


# CNN Image Endpoints
@ml_bp.route('/train/cnn-images', methods=['POST'])
def train_cnn_images():
    """Train CNN model with ZIP file containing images organized by classes"""
    if 'file' not in request.files:
        return jsonify({"error": "No ZIP file uploaded"}), 400
    
    file = request.files['file']
    
    # Validate file
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.lower().endswith('.zip'):
        return jsonify({"error": "Please upload a ZIP file"}), 400
    
    # Get training parameters
    try:
        epochs = int(request.form.get('epochs', 10))
        batch_size = int(request.form.get('batch_size', 32))
        target_size = request.form.get('target_size', '224,224')
        augment = request.form.get('augment', 'true').lower() == 'true'
        validation_split = float(request.form.get('validation_split', 0.2))
        
        # Parse target size
        if isinstance(target_size, str):
            target_size = tuple(map(int, target_size.split(',')))
        
        # Get optional model configuration
        config_str = request.form.get('config', '{}')
        config = json.loads(config_str) if config_str else {}
        
    except (ValueError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Invalid parameter format: {str(e)}"}), 400
    
    try:
        # Import CNN image training
        from ml.deep_learning.training.train_cnn_images import train_cnn_with_images
        
        # Train the model
        result = train_cnn_with_images(
            zip_file=file,
            epochs=epochs,
            batch_size=batch_size,
            target_size=target_size,
            augment=augment,
            validation_split=validation_split,
            config=config
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500


@ml_bp.route('/test/cnn-images', methods=['POST'])
def test_cnn_images():
    """Test CNN model with a single image upload"""
    if 'file' not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400
    
    file = request.files['file']
    model_name = request.form.get('model_name')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not model_name:
        return jsonify({"error": "Model name is required"}), 400
    
    # Validate image file
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return jsonify({"error": "Please upload a valid image file"}), 400
    
    try:
        # Import CNN image testing
        from ml.deep_learning.inference.predict_cnn_images import predict_single_image
        
        # Make prediction
        result = predict_single_image(
            image_file=file,
            model_name=model_name
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@ml_bp.route('/models/cnn-images', methods=['GET'])
def get_cnn_image_models():
    """Get list of available CNN image models"""
    try:
        trained_models_dir = "trained_models"
        cnn_models = []
        
        if os.path.exists(trained_models_dir):
            import glob
            
            # Look for CNN image models (with specific naming pattern)
            cnn_pattern = os.path.join(trained_models_dir, "*cnn_image*.keras")
            cnn_files = glob.glob(cnn_pattern)
            
            for model_path in cnn_files:
                model_name = os.path.basename(model_path)
                model_name = os.path.splitext(model_name)[0]  # Remove extension
                
                # Get model info
                model_info = {
                    "name": model_name,
                    "path": model_path,
                    "created": os.path.getctime(model_path),
                    "size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 2)
                }
                
                # Try to load model metadata if available
                metadata_path = model_path.replace('.keras', '_metadata.json')
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        model_info.update(metadata)
                    except:
                        pass
                
                cnn_models.append(model_info)
        
        # Sort by creation time (newest first)
        cnn_models.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            "models": cnn_models,
            "total": len(cnn_models)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to list CNN models: {str(e)}"}), 500


@ml_bp.route('/validate/zip-structure', methods=['POST'])
def validate_zip_structure():
    """Validate ZIP file structure for CNN image training"""
    if 'file' not in request.files:
        return jsonify({"error": "No ZIP file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not file.filename.lower().endswith('.zip'):
        return jsonify({"error": "Please upload a ZIP file"}), 400
    
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_zip_path = temp_file.name
        
        # Use image processor to validate structure
        from utils.image_processor import extract_zip_file, validate_image_structure
        
        # Extract and validate
        extracted_dir = extract_zip_file(temp_zip_path)
        validation_result = validate_image_structure(extracted_dir)
        
        # Cleanup
        os.unlink(temp_zip_path)
        import shutil
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({"error": f"Validation failed: {str(e)}"}), 500


@ml_bp.route('/download/cnn-images/<model_name>', methods=['GET'])
def download_cnn_image_model(model_name):
    """Download CNN image model file"""
    try:
        trained_models_dir = "trained_models"
        
        # Try different possible paths
        possible_paths = [
            os.path.join(trained_models_dir, f"{model_name}.keras"),
            os.path.join(trained_models_dir, f"cnn_image_{model_name}.keras"),
            os.path.join(trained_models_dir, f"{model_name}_cnn_image.keras")
        ]
        
        # Also try pattern matching
        if os.path.exists(trained_models_dir):
            import glob
            pattern_paths = [
                os.path.join(trained_models_dir, f"*{model_name}*.keras")
            ]
            
            for pattern in pattern_paths:
                matching_files = glob.glob(pattern)
                if matching_files:
                    possible_paths.extend(matching_files)
        
        # Find the first existing file
        for model_path in possible_paths:
            if os.path.exists(model_path):
                return send_file(model_path, as_attachment=True)
        
        return jsonify({"error": "CNN image model not found"}), 404
        
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500
