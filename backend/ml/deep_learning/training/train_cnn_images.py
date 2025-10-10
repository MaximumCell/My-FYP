"""
CNN Image Training Module
Handles training CNN models with ZIP files containing organized image datasets
"""

import os
import time
import tempfile
import json
from typing import Dict, Any, Tuple, Optional
import logging

from utils.lazy_tf import tf, is_available as tf_is_available
import numpy as np

HAS_DEPS = tf_is_available()

import sys
import os

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from ml.deep_learning.models.cnn import get_model
from ml.deep_learning.image_processing import ImageDatasetGenerator, AUGMENTATION_PRESETS
from utils.image_processor import create_image_dataset

logger = logging.getLogger(__name__)

def train_cnn_with_images(zip_file,
                         epochs: int = 10,
                         batch_size: int = 32,
                         target_size: Tuple[int, int] = (224, 224),
                         augment: bool = True,
                         validation_split: float = 0.2,
                         config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Train a CNN model with images from a ZIP file
    
    Args:
        zip_file: Uploaded ZIP file object
        epochs: Number of training epochs
        batch_size: Batch size for training
        target_size: Target image size (width, height)
        augment: Whether to apply data augmentation
        validation_split: Fraction of data for validation
        config: Additional model configuration
        
    Returns:
        Dictionary with training results and model information
    """
    if not HAS_DEPS:
        return {"error": "Required dependencies not available: tensorflow, numpy"}
    
    # Save uploaded file to temporary location
    temp_zip_path = None
    extracted_dir = None
    
    try:
        # Create temporary file for ZIP
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            zip_file.save(temp_file.name)
            temp_zip_path = temp_file.name
        
        logger.info(f"Processing ZIP file for CNN training: {zip_file.filename}")
        
        # Process images from ZIP file
        dataset_info = create_image_dataset(
            zip_file_path=temp_zip_path,
            target_size=target_size,
            normalize=True,
            cleanup=True  # Will cleanup extracted directory
        )
        
        # Extract dataset components
        images = dataset_info['images']
        labels = dataset_info['labels']
        class_names = dataset_info['dataset_info']['classes']
        num_classes = dataset_info['num_classes']
        
        logger.info(f"Dataset loaded: {len(images)} images, {num_classes} classes")
        logger.info(f"Classes: {class_names}")
        
        # Split data into train and validation
        if validation_split > 0:
            from sklearn.model_selection import train_test_split
            
            X_train, X_val, y_train, y_val = train_test_split(
                images, labels,
                test_size=validation_split,
                stratify=labels,
                random_state=42
            )
        else:
            X_train, y_train = images, labels
            X_val, y_val = None, None
        
        # Prepare augmentation configuration
        augment_config = None
        if augment:
            augment_preset = config.get('augmentation_preset', 'medium') if config else 'medium'
            if augment_preset in AUGMENTATION_PRESETS:
                augment_config = AUGMENTATION_PRESETS[augment_preset]
            else:
                augment_config = AUGMENTATION_PRESETS['medium']
        
        # Create dataset generator
        dataset_generator = ImageDatasetGenerator(
            target_size=target_size,
            channels=3,
            normalize=True,
            augmentation_config=augment_config if augment else None
        )
        
        # Convert to TensorFlow datasets
        train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
        
        if augment and augment_config:
            # Apply augmentation
            augmentation_layer = dataset_generator.augmentation.create_tf_augmentation_layer()
            train_dataset = train_dataset.map(
                lambda x, y: (augmentation_layer(x, training=True), y),
                num_parallel_calls=tf.data.AUTOTUNE
            )
        
        train_dataset = train_dataset.shuffle(1000).batch(batch_size).prefetch(tf.data.AUTOTUNE)
        
        val_dataset = None
        if X_val is not None:
            val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val))
            val_dataset = val_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
        
        # Prepare model configuration
        model_config = config.copy() if config else {}
        
        # Set appropriate loss function and final activation
        if num_classes == 1:
            # Binary classification
            model_config['final_activation'] = 'sigmoid'
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
        elif num_classes == 2:
            # Binary classification with 2 classes
            model_config['final_activation'] = 'sigmoid'
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
            num_classes = 1  # Use single output for binary
        else:
            # Multi-class classification
            model_config['final_activation'] = 'softmax'
            loss = 'sparse_categorical_crossentropy'
            metrics = ['accuracy']
        
        # Create and compile model
        input_shape = (*target_size, 3)
        model = get_model(
            input_shape=input_shape,
            num_classes=num_classes,
            config=model_config
        )
        
        model.compile(
            optimizer=model_config.get('optimizer', 'adam'),
            loss=loss,
            metrics=metrics
        )
        
        logger.info(f"Model created with input shape: {input_shape}")
        logger.info(f"Model summary: {model.count_params()} parameters")
        
        # Prepare callbacks
        callbacks = []
        
        # Early stopping
        if epochs > 5:
            early_stopping = tf.keras.callbacks.EarlyStopping(
                monitor='val_loss' if val_dataset else 'loss',
                patience=max(3, epochs // 10),
                restore_best_weights=True
            )
            callbacks.append(early_stopping)
        
        # Reduce learning rate on plateau
        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss' if val_dataset else 'loss',
            factor=0.2,
            patience=max(2, epochs // 15),
            min_lr=0.0001
        )
        callbacks.append(reduce_lr)
        
        # Train model
        logger.info(f"Starting training for {epochs} epochs...")
        
        history = model.fit(
            train_dataset,
            epochs=epochs,
            validation_data=val_dataset,
            callbacks=callbacks,
            verbose=1
        )
        
        # Generate model name and save
        timestamp = int(time.time())
        model_name = f"cnn_image_{timestamp}"
        
        # Create trained_models directory if it doesn't exist
        os.makedirs("trained_models", exist_ok=True)
        
        model_path = os.path.join("trained_models", f"{model_name}.keras")
        model.save(model_path)
        
        # Save metadata
        metadata = {
            "model_name": model_name,
            "model_type": "cnn_image",
            "num_classes": len(class_names),
            "class_names": class_names,
            "input_shape": input_shape,
            "target_size": target_size,
            "training_params": {
                "epochs": epochs,
                "batch_size": batch_size,
                "validation_split": validation_split,
                "augmentation_enabled": augment,
                "total_images": len(images),
                "training_images": len(X_train),
                "validation_images": len(X_val) if X_val is not None else 0
            },
            "training_history": {
                "final_loss": float(history.history['loss'][-1]),
                "final_accuracy": float(history.history['accuracy'][-1]) if 'accuracy' in history.history else None,
                "final_val_loss": float(history.history['val_loss'][-1]) if 'val_loss' in history.history else None,
                "final_val_accuracy": float(history.history['val_accuracy'][-1]) if 'val_accuracy' in history.history else None,
                "epochs_trained": len(history.history['loss'])
            },
            "dataset_info": dataset_info['dataset_info'],
            "created_at": timestamp
        }
        
        metadata_path = os.path.join("trained_models", f"{model_name}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to: {model_path}")
        
        # Prepare response
        result = {
            "success": True,
            "model_name": model_name,
            "model_path": model_path,
            "metadata": metadata,
            "training_summary": {
                "total_epochs": len(history.history['loss']),
                "final_loss": metadata["training_history"]["final_loss"],
                "final_accuracy": metadata["training_history"]["final_accuracy"],
                "final_val_loss": metadata["training_history"]["final_val_loss"],
                "final_val_accuracy": metadata["training_history"]["final_val_accuracy"],
                "num_classes": len(class_names),
                "class_names": class_names,
                "total_images": len(images)
            }
        }
        
        # Add training history for plotting
        result["history"] = {
            "loss": history.history['loss'],
            "accuracy": history.history.get('accuracy', []),
            "val_loss": history.history.get('val_loss', []),
            "val_accuracy": history.history.get('val_accuracy', [])
        }
        
        return result
        
    except Exception as e:
        logger.error(f"CNN image training failed: {str(e)}")
        return {"error": f"Training failed: {str(e)}"}
    
    finally:
        # Cleanup temporary files
        if temp_zip_path and os.path.exists(temp_zip_path):
            try:
                os.unlink(temp_zip_path)
            except:
                pass
        
        if extracted_dir and os.path.exists(extracted_dir):
            try:
                import shutil
                shutil.rmtree(extracted_dir)
            except:
                pass

def get_training_recommendations(dataset_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide training recommendations based on dataset characteristics
    
    Args:
        dataset_info: Information about the dataset
        
    Returns:
        Dictionary with training recommendations
    """
    total_images = dataset_info['dataset_info']['total_images']
    num_classes = dataset_info['dataset_info']['num_classes']
    class_counts = dataset_info['dataset_info']['class_counts']
    
    recommendations = {
        "batch_size": 32,
        "epochs": 20,
        "augmentation": "medium",
        "validation_split": 0.2,
        "notes": []
    }
    
    # Adjust based on dataset size
    if total_images < 100:
        recommendations["batch_size"] = 16
        recommendations["epochs"] = 50
        recommendations["augmentation"] = "heavy"
        recommendations["notes"].append("Small dataset: using heavy augmentation and more epochs")
    elif total_images < 500:
        recommendations["batch_size"] = 32
        recommendations["epochs"] = 30
        recommendations["augmentation"] = "medium"
        recommendations["notes"].append("Medium dataset: using moderate augmentation")
    else:
        recommendations["batch_size"] = 64
        recommendations["epochs"] = 20
        recommendations["augmentation"] = "light"
        recommendations["notes"].append("Large dataset: using light augmentation")
    
    # Check class balance
    min_count = min(class_counts.values())
    max_count = max(class_counts.values())
    
    if max_count > min_count * 3:
        recommendations["notes"].append("Imbalanced dataset: consider class weights or resampling")
    
    # Adjust for number of classes
    if num_classes > 10:
        recommendations["epochs"] += 10
        recommendations["notes"].append("Many classes: increased epochs recommended")
    
    return recommendations