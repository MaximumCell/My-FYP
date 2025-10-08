"""
CNN Image Inference Module
Handles prediction with trained CNN models for single image inputs
"""

import os
import json
import tempfile
from typing import Dict, Any, Optional, Union
import logging

try:
    import numpy as np
    from PIL import Image
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
except ImportError:
    HAS_DEPS = False
    tf = None
    np = None
    Image = None

import sys
import os

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from ml.deep_learning.models.cnn import get_model
from ml.deep_learning.image_processing import ImagePreprocessor

logger = logging.getLogger(__name__)

def predict_single_image(image_file, 
                        model_name: str,
                        top_k: int = 5) -> Dict[str, Any]:
    """
    Predict class for a single image using a trained CNN model
    
    Args:
        image_file: Uploaded image file object
        model_name: Name of the trained CNN model
        top_k: Number of top predictions to return
        
    Returns:
        Dictionary with prediction results
    """
    if not HAS_DEPS:
        return {"error": "Required dependencies not available: tensorflow, numpy, PIL"}
    
    temp_image_path = None
    
    try:
        # Save uploaded image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            image_file.save(temp_file.name)
            temp_image_path = temp_file.name
        
        # Find and load the model
        model, metadata = load_cnn_image_model(model_name)
        
        if model is None:
            return {"error": f"Model '{model_name}' not found"}
        
        # Get preprocessing parameters from metadata
        target_size = tuple(metadata.get('target_size', (224, 224)))
        input_shape = metadata.get('input_shape', (*target_size, 3))
        class_names = metadata.get('class_names', [])
        
        # Preprocess the image
        preprocessor = ImagePreprocessor(
            target_size=target_size,
            normalize=True,
            channels=input_shape[-1] if len(input_shape) > 2 else 3
        )
        
        processed_image = preprocessor.preprocess_single_image(temp_image_path)
        
        # Add batch dimension
        image_batch = np.expand_dims(processed_image, axis=0)
        
        # Make prediction
        logger.info(f"Making prediction with model: {model_name}")
        predictions = model.predict(image_batch, verbose=0)
        
        # Process predictions based on model type
        num_classes = len(class_names) if class_names else 1
        
        if num_classes == 1 or (num_classes == 2 and predictions.shape[-1] == 1):
            # Binary classification
            prediction_score = float(predictions[0][0])
            
            if len(class_names) == 2:
                # Two class names provided
                if prediction_score > 0.5:
                    predicted_class = class_names[1]
                    confidence = prediction_score
                else:
                    predicted_class = class_names[0]
                    confidence = 1.0 - prediction_score
                
                results = [
                    {"class": class_names[1], "confidence": prediction_score},
                    {"class": class_names[0], "confidence": 1.0 - prediction_score}
                ]
            else:
                # Single class name or default
                predicted_class = class_names[0] if class_names else "positive"
                confidence = prediction_score if prediction_score > 0.5 else (1.0 - prediction_score)
                
                results = [
                    {"class": predicted_class, "confidence": confidence}
                ]
        else:
            # Multi-class classification
            prediction_probs = predictions[0]
            
            # Get top-k predictions
            top_indices = np.argsort(prediction_probs)[::-1][:top_k]
            
            results = []
            for i, idx in enumerate(top_indices):
                class_name = class_names[idx] if idx < len(class_names) else f"class_{idx}"
                confidence = float(prediction_probs[idx])
                
                results.append({
                    "class": class_name,
                    "confidence": confidence,
                    "rank": i + 1
                })
            
            # Predicted class is the top one
            predicted_class = results[0]["class"]
            confidence = results[0]["confidence"]
        
        # Get image information
        image_info = get_image_info(temp_image_path)
        
        return {
            "success": True,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "predictions": results,
            "model_info": {
                "model_name": model_name,
                "num_classes": num_classes,
                "class_names": class_names,
                "input_shape": input_shape
            },
            "image_info": image_info
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {"error": f"Prediction failed: {str(e)}"}
    
    finally:
        # Cleanup temporary file
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.unlink(temp_image_path)
            except:
                pass

def load_cnn_image_model(model_name: str) -> tuple:
    """
    Load a CNN image model and its metadata
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        Tuple of (model, metadata) or (None, None) if not found
    """
    # Use proxy `tf` which loads real TF on first access. If not available, return early.
    if not tf:
        return None, None
    
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
        pattern_paths = glob.glob(os.path.join(trained_models_dir, f"*{model_name}*.keras"))
        possible_paths.extend(pattern_paths)
    
    # Find the model file
    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    if not model_path:
        logger.error(f"Model not found: {model_name}")
        return None, None
    
    try:
        # Load the model
        model = tf.keras.models.load_model(model_path)
        logger.info(f"Loaded model from: {model_path}")
        
        # Load metadata
        metadata_path = model_path.replace('.keras', '_metadata.json')
        metadata = {}
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {str(e)}")
        
        # If no metadata, try to infer from model
        if not metadata:
            input_shape = model.input_shape[1:]  # Remove batch dimension
            output_shape = model.output_shape[-1] if len(model.output_shape) > 1 else 1
            
            metadata = {
                "input_shape": input_shape,
                "target_size": input_shape[:2] if len(input_shape) >= 2 else (224, 224),
                "num_classes": output_shape,
                "class_names": [f"class_{i}" for i in range(output_shape)] if output_shape > 1 else ["class_0"]
            }
        
        return model, metadata
        
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {str(e)}")
        return None, None

def predict_batch_images(image_paths: list,
                        model_name: str,
                        batch_size: int = 32) -> Dict[str, Any]:
    """
    Predict classes for a batch of images
    
    Args:
        image_paths: List of image file paths
        model_name: Name of the trained CNN model
        batch_size: Batch size for processing
        
    Returns:
        Dictionary with batch prediction results
    """
    if not HAS_DEPS:
        return {"error": "Required dependencies not available"}
    
    try:
        # Load model and metadata
        model, metadata = load_cnn_image_model(model_name)
        
        if model is None:
            return {"error": f"Model '{model_name}' not found"}
        
        # Get preprocessing parameters
        target_size = tuple(metadata.get('target_size', (224, 224)))
        input_shape = metadata.get('input_shape', (*target_size, 3))
        class_names = metadata.get('class_names', [])
        
        # Create preprocessor
        preprocessor = ImagePreprocessor(
            target_size=target_size,
            normalize=True,
            channels=input_shape[-1] if len(input_shape) > 2 else 3
        )
        
        # Process images in batches
        results = []
        total_images = len(image_paths)
        
        for i in range(0, total_images, batch_size):
            batch_paths = image_paths[i:i+batch_size]
            
            # Preprocess batch
            try:
                batch_images = preprocessor.preprocess_batch(batch_paths)
                
                # Make predictions
                predictions = model.predict(batch_images, verbose=0)
                
                # Process each prediction in the batch
                for j, (path, pred) in enumerate(zip(batch_paths, predictions)):
                    try:
                        pred_result = process_single_prediction(pred, class_names)
                        pred_result["image_path"] = path
                        pred_result["batch_index"] = i + j
                        results.append(pred_result)
                    except Exception as e:
                        results.append({
                            "image_path": path,
                            "batch_index": i + j,
                            "error": str(e)
                        })
                
            except Exception as e:
                # Handle batch processing error
                for j, path in enumerate(batch_paths):
                    results.append({
                        "image_path": path,
                        "batch_index": i + j,
                        "error": f"Batch processing failed: {str(e)}"
                    })
        
        # Calculate summary statistics
        successful_predictions = [r for r in results if "predicted_class" in r]
        failed_predictions = [r for r in results if "error" in r]
        
        return {
            "success": True,
            "total_images": total_images,
            "successful_predictions": len(successful_predictions),
            "failed_predictions": len(failed_predictions),
            "results": results,
            "model_info": {
                "model_name": model_name,
                "class_names": class_names
            }
        }
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {str(e)}")
        return {"error": f"Batch prediction failed: {str(e)}"}

def process_single_prediction(prediction, class_names) -> Dict[str, Any]:
    """
    Process a single prediction array into readable results
    
    Args:
        prediction: Model prediction array
        class_names: List of class names
        
    Returns:
        Dictionary with processed prediction
    """
    num_classes = len(class_names) if class_names else 1
    
    if num_classes == 1 or (num_classes == 2 and len(prediction) == 1):
        # Binary classification
        score = float(prediction[0]) if len(prediction) > 0 else 0.5
        
        if len(class_names) == 2:
            if score > 0.5:
                predicted_class = class_names[1]
                confidence = score
            else:
                predicted_class = class_names[0]
                confidence = 1.0 - score
        else:
            predicted_class = class_names[0] if class_names else "positive"
            confidence = score if score > 0.5 else (1.0 - score)
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "raw_score": score
        }
    else:
        # Multi-class classification
        class_idx = np.argmax(prediction)
        confidence = float(prediction[class_idx])
        predicted_class = class_names[class_idx] if class_idx < len(class_names) else f"class_{class_idx}"
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "class_index": int(class_idx),
            "raw_scores": prediction.tolist()
        }

def get_image_info(image_path: str) -> Dict[str, Any]:
    """
    Get basic information about an image file
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image information
    """
    if not Image:
        return {"error": "PIL not available"}
    
    try:
        with Image.open(image_path) as img:
            return {
                "filename": os.path.basename(image_path),
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height
            }
    except Exception as e:
        return {"error": f"Failed to read image info: {str(e)}"}

def list_available_models() -> Dict[str, Any]:
    """
    List all available CNN image models
    
    Returns:
        Dictionary with model information
    """
    try:
        trained_models_dir = "trained_models"
        models = []
        
        if os.path.exists(trained_models_dir):
            import glob
            
            # Look for CNN image models
            pattern = os.path.join(trained_models_dir, "*cnn_image*.keras")
            model_files = glob.glob(pattern)
            
            for model_path in model_files:
                model_name = os.path.splitext(os.path.basename(model_path))[0]
                
                # Get basic info
                model_info = {
                    "name": model_name,
                    "path": model_path,
                    "size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 2),
                    "created": os.path.getctime(model_path)
                }
                
                # Try to load metadata
                metadata_path = model_path.replace('.keras', '_metadata.json')
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        model_info.update({
                            "num_classes": metadata.get("num_classes"),
                            "class_names": metadata.get("class_names"),
                            "input_shape": metadata.get("input_shape")
                        })
                    except:
                        pass
                
                models.append(model_info)
        
        return {
            "success": True,
            "models": models,
            "total": len(models)
        }
        
    except Exception as e:
        return {"error": f"Failed to list models: {str(e)}"}