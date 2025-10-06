"""
Dataset Generator Module
Creates TensorFlow datasets from organized image data for CNN training
"""

import os
from typing import Dict, List, Tuple, Optional, Any
import logging

try:
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    # Lazy-import tensorflow proxy
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
except ImportError:
    HAS_DEPS = False
    tf = None
    np = None
    train_test_split = None
    LabelEncoder = None

from .image_preprocessor import ImagePreprocessor
from .data_augmentation import DataAugmentation

logger = logging.getLogger(__name__)

class ImageDatasetGenerator:
    """
    Generates TensorFlow datasets from image files for CNN training
    """
    
    def __init__(self, 
                 target_size: Tuple[int, int] = (224, 224),
                 channels: int = 3,
                 normalize: bool = True,
                 augmentation_config: Optional[Dict] = None):
        """
        Initialize the dataset generator
        
        Args:
            target_size: Target image size (width, height)
            channels: Number of color channels
            normalize: Whether to normalize pixel values
            augmentation_config: Configuration for data augmentation
        """
        if not HAS_DEPS:
            raise ImportError("Required dependencies not available")
        
        self.target_size = target_size
        self.channels = channels
        self.normalize = normalize
        
        # Initialize preprocessor
        self.preprocessor = ImagePreprocessor(
            target_size=target_size,
            normalize=normalize,
            channels=channels
        )
        
        # Initialize augmentation if config provided
        self.augmentation = None
        if augmentation_config:
            self.augmentation = DataAugmentation(augmentation_config)
    
    def create_dataset_from_organized_images(self,
                                           organized_images: Dict[str, List[str]],
                                           batch_size: int = 32,
                                           validation_split: float = 0.2,
                                           shuffle: bool = True,
                                           augment_training: bool = True,
                                           random_state: int = 42) -> Dict[str, Any]:
        """
        Create training and validation datasets from organized images
        
        Args:
            organized_images: Dictionary mapping class names to image file paths
            batch_size: Batch size for the datasets
            validation_split: Fraction of data to use for validation
            shuffle: Whether to shuffle the training data
            augment_training: Whether to apply augmentation to training data
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary containing datasets and metadata
        """
        # Prepare image paths and labels
        image_paths = []
        labels = []
        class_names = list(organized_images.keys())
        
        for class_idx, class_name in enumerate(class_names):
            class_images = organized_images[class_name]
            image_paths.extend(class_images)
            labels.extend([class_idx] * len(class_images))
        
        # Convert to numpy arrays
        image_paths = np.array(image_paths)
        labels = np.array(labels)
        
        # Create train/validation split
        if validation_split > 0:
            train_paths, val_paths, train_labels, val_labels = train_test_split(
                image_paths, labels,
                test_size=validation_split,
                stratify=labels,
                random_state=random_state
            )
        else:
            train_paths, val_paths = image_paths, np.array([])
            train_labels, val_labels = labels, np.array([])
        
        # Create datasets
        train_dataset = self._create_tf_dataset(
            train_paths, train_labels, batch_size, shuffle, 
            augment=augment_training and self.augmentation is not None
        )
        
        val_dataset = None
        if len(val_paths) > 0:
            val_dataset = self._create_tf_dataset(
                val_paths, val_labels, batch_size, False, augment=False
            )
        
        # Calculate dataset statistics
        num_classes = len(class_names)
        train_size = len(train_paths)
        val_size = len(val_paths) if len(val_paths) > 0 else 0
        
        # Calculate class distribution
        train_class_counts = np.bincount(train_labels, minlength=num_classes)
        val_class_counts = np.bincount(val_labels, minlength=num_classes) if len(val_labels) > 0 else np.zeros(num_classes)
        
        return {
            'train_dataset': train_dataset,
            'validation_dataset': val_dataset,
            'metadata': {
                'num_classes': num_classes,
                'class_names': class_names,
                'train_size': train_size,
                'validation_size': val_size,
                'batch_size': batch_size,
                'image_shape': (*self.target_size, self.channels),
                'train_class_counts': train_class_counts.tolist(),
                'validation_class_counts': val_class_counts.tolist(),
                'augmentation_enabled': augment_training and self.augmentation is not None
            }
        }
    
    def create_dataset_from_directory(self,
                                    directory_path: str,
                                    batch_size: int = 32,
                                    validation_split: float = 0.2,
                                    shuffle: bool = True,
                                    augment_training: bool = True) -> Dict[str, Any]:
        """
        Create datasets directly from directory structure
        
        Args:
            directory_path: Path to directory containing class subdirectories
            batch_size: Batch size for datasets
            validation_split: Fraction for validation split
            shuffle: Whether to shuffle training data
            augment_training: Whether to apply augmentation to training data
            
        Returns:
            Dictionary containing datasets and metadata
        """
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Use TensorFlow's built-in dataset creation for efficiency
        if validation_split > 0:
            # Create training dataset
            train_dataset = tf.keras.utils.image_dataset_from_directory(
                directory_path,
                validation_split=validation_split,
                subset="training",
                seed=42,
                image_size=self.target_size,
                batch_size=batch_size,
                shuffle=shuffle
            )
            
            # Create validation dataset
            val_dataset = tf.keras.utils.image_dataset_from_directory(
                directory_path,
                validation_split=validation_split,
                subset="validation",
                seed=42,
                image_size=self.target_size,
                batch_size=batch_size,
                shuffle=False
            )
        else:
            # Create full dataset as training
            train_dataset = tf.keras.utils.image_dataset_from_directory(
                directory_path,
                seed=42,
                image_size=self.target_size,
                batch_size=batch_size,
                shuffle=shuffle
            )
            val_dataset = None
        
        # Get class names
        class_names = train_dataset.class_names
        
        # Apply preprocessing
        train_dataset = train_dataset.map(
            lambda x, y: (self._preprocess_batch(x), y),
            num_parallel_calls=tf.data.AUTOTUNE
        )
        
        if val_dataset is not None:
            val_dataset = val_dataset.map(
                lambda x, y: (self._preprocess_batch(x), y),
                num_parallel_calls=tf.data.AUTOTUNE
            )
        
        # Apply augmentation to training data if requested
        if augment_training and self.augmentation is not None:
            augmentation_layer = self.augmentation.create_tf_augmentation_layer()
            train_dataset = train_dataset.map(
                lambda x, y: (augmentation_layer(x, training=True), y),
                num_parallel_calls=tf.data.AUTOTUNE
            )
        
        # Optimize dataset performance
        train_dataset = train_dataset.cache().prefetch(tf.data.AUTOTUNE)
        if val_dataset is not None:
            val_dataset = val_dataset.cache().prefetch(tf.data.AUTOTUNE)
        
        # Calculate sizes (approximate)
        train_size = sum(1 for _ in train_dataset.unbatch())
        val_size = sum(1 for _ in val_dataset.unbatch()) if val_dataset is not None else 0
        
        return {
            'train_dataset': train_dataset,
            'validation_dataset': val_dataset,
            'metadata': {
                'num_classes': len(class_names),
                'class_names': class_names,
                'train_size': train_size,
                'validation_size': val_size,
                'batch_size': batch_size,
                'image_shape': (*self.target_size, self.channels),
                'augmentation_enabled': augment_training and self.augmentation is not None
            }
        }
    
    def _create_tf_dataset(self,
                          image_paths: np.ndarray,
                          labels: np.ndarray,
                          batch_size: int,
                          shuffle: bool,
                          augment: bool = False) -> "tf.data.Dataset":
        """
        Create TensorFlow dataset from paths and labels
        
        Args:
            image_paths: Array of image file paths
            labels: Array of corresponding labels
            batch_size: Batch size
            shuffle: Whether to shuffle the dataset
            augment: Whether to apply data augmentation
            
        Returns:
            TensorFlow Dataset
        """
        # Create dataset from tensors
        dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels))
        
        # Shuffle if requested
        if shuffle:
            dataset = dataset.shuffle(buffer_size=1000, seed=42)
        
        # Map preprocessing function
        dataset = dataset.map(
            lambda path, label: self._load_and_preprocess_image(path, label),
            num_parallel_calls=tf.data.AUTOTUNE
        )
        
        # Apply augmentation if requested
        if augment:
            augmentation_layer = self.augmentation.create_tf_augmentation_layer()
            dataset = dataset.map(
                lambda image, label: (augmentation_layer(image, training=True), label),
                num_parallel_calls=tf.data.AUTOTUNE
            )
        
        # Batch and prefetch
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset
    
    def _load_and_preprocess_image(self, image_path: "tf.Tensor", label: "tf.Tensor") -> Tuple["tf.Tensor", "tf.Tensor"]:
        """
        Load and preprocess a single image using TensorFlow operations
        
        Args:
            image_path: TensorFlow tensor containing image path
            label: TensorFlow tensor containing label
            
        Returns:
            Tuple of (preprocessed_image, label)
        """
        # Read and decode image
        image = tf.io.read_file(image_path)
        image = tf.image.decode_image(image, channels=self.channels, expand_animations=False)
        
        # Convert to float32
        image = tf.cast(image, tf.float32)
        
        # Resize image
        image = tf.image.resize(image, self.target_size)
        
        # Normalize if requested
        if self.normalize:
            image = image / 255.0
        
        # Ensure correct shape
        image.set_shape((*self.target_size, self.channels))
        
        return image, label
    
    def _preprocess_batch(self, images: "tf.Tensor") -> "tf.Tensor":
        """
        Preprocess a batch of images
        
        Args:
            images: Batch of images tensor
            
        Returns:
            Preprocessed batch tensor
        """
        # Convert to float32 if needed
        if images.dtype != tf.float32:
            images = tf.cast(images, tf.float32)
        
        # Normalize if requested
        if self.normalize:
            images = images / 255.0
        
        return images
    
    def create_test_dataset(self,
                           test_images: List[str],
                           batch_size: int = 32) -> "tf.data.Dataset":
        """
        Create dataset for testing/inference (no labels)
        
        Args:
            test_images: List of test image paths
            batch_size: Batch size for processing
            
        Returns:
            TensorFlow Dataset for testing
        """
        # Create dataset from image paths
        dataset = tf.data.Dataset.from_tensor_slices(test_images)
        
        # Map preprocessing function (no labels)
        dataset = dataset.map(
            lambda path: self._load_and_preprocess_image_no_label(path),
            num_parallel_calls=tf.data.AUTOTUNE
        )
        
        # Batch and prefetch
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset
    
    def _load_and_preprocess_image_no_label(self, image_path: "tf.Tensor") -> "tf.Tensor":
        """
        Load and preprocess image without label (for testing)
        
        Args:
            image_path: TensorFlow tensor containing image path
            
        Returns:
            Preprocessed image tensor
        """
        image, _ = self._load_and_preprocess_image(image_path, tf.constant(0))
        return image
    
    def get_dataset_info(self, dataset: tf.data.Dataset) -> Dict[str, Any]:
        """
        Get information about a TensorFlow dataset
        
        Args:
            dataset: TensorFlow Dataset
            
        Returns:
            Dictionary with dataset information
        """
        # Get element spec
        element_spec = dataset.element_spec
        
        info = {
            'element_spec': str(element_spec),
            'batch_size': None,
            'image_shape': None,
            'num_classes': None
        }
        
        # Try to extract batch size and shapes from element spec
        if isinstance(element_spec, tuple) and len(element_spec) == 2:
            image_spec, label_spec = element_spec
            if hasattr(image_spec, 'shape'):
                info['batch_size'] = image_spec.shape[0]
                info['image_shape'] = image_spec.shape[1:].as_list()
            if hasattr(label_spec, 'shape'):
                # For sparse categorical, labels are scalars
                info['num_classes'] = "unknown (sparse categorical)"
        
        return info