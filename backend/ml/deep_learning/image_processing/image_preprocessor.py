"""
Image Preprocessing Module
Handles image loading, resizing, normalization, and augmentation for CNN training
"""

import os
from typing import Tuple, Optional, Dict, Any
import logging

try:
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
except ImportError:
    HAS_DEPS = False
    np = None
    Image = None
    tf = None

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """
    Main image preprocessing class for CNN training
    """
    
    def __init__(self, 
                 target_size: Tuple[int, int] = (224, 224),
                 normalize: bool = True,
                 channels: int = 3):
        """
        Initialize the preprocessor
        
        Args:
            target_size: Target image size (width, height)
            normalize: Whether to normalize pixel values to [0, 1]
            channels: Number of color channels (3 for RGB, 1 for grayscale)
        """
        if not HAS_DEPS:
            raise ImportError("Required dependencies not available: numpy, PIL, tensorflow")
        
        self.target_size = target_size
        self.normalize = normalize
        self.channels = channels
        self.input_shape = (*target_size, channels)
        
    def preprocess_single_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess a single image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image array
        """
        try:
            # Load image
            with Image.open(image_path) as img:
                # Convert to appropriate mode
                if self.channels == 3 and img.mode != 'RGB':
                    img = img.convert('RGB')
                elif self.channels == 1 and img.mode != 'L':
                    img = img.convert('L')
                
                # Resize image
                img = img.resize(self.target_size, Image.Resampling.LANCZOS)
                
                # Convert to numpy array
                img_array = np.array(img, dtype=np.float32)
                
                # Ensure correct shape for grayscale
                if self.channels == 1 and len(img_array.shape) == 2:
                    img_array = np.expand_dims(img_array, axis=-1)
                
                # Normalize if requested
                if self.normalize:
                    img_array = img_array / 255.0
                
                return img_array
                
        except Exception as e:
            logger.error(f"Failed to preprocess image {image_path}: {str(e)}")
            raise
    
    def preprocess_batch(self, image_paths: list) -> np.ndarray:
        """
        Preprocess a batch of images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Batch of preprocessed images as numpy array
        """
        processed_images = []
        
        for image_path in image_paths:
            try:
                processed_img = self.preprocess_single_image(image_path)
                processed_images.append(processed_img)
            except Exception as e:
                logger.warning(f"Skipping image {image_path}: {str(e)}")
                continue
        
        if not processed_images:
            raise ValueError("No images could be processed successfully")
        
        return np.array(processed_images)
    
    def create_tf_dataset(self, 
                         image_paths: list, 
                         labels: list, 
                         batch_size: int = 32,
                         shuffle: bool = True,
                         augment: bool = False) -> "tf.data.Dataset":
        """
        Create a TensorFlow dataset from image paths and labels
        
        Args:
            image_paths: List of image file paths
            labels: List of corresponding labels
            batch_size: Batch size for the dataset
            shuffle: Whether to shuffle the dataset
            augment: Whether to apply data augmentation
            
        Returns:
            TensorFlow Dataset object
        """
        if not tf:
            raise ImportError("TensorFlow is required for dataset creation")
        
        # Create dataset from paths and labels
        dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels))
        
        # Map preprocessing function
        dataset = dataset.map(
            lambda path, label: self._tf_preprocess_image(path, label),
            num_parallel_calls=tf.data.AUTOTUNE
        )
        
        # Apply augmentation if requested
        if augment:
            dataset = dataset.map(
                lambda image, label: (self._augment_image(image), label),
                num_parallel_calls=tf.data.AUTOTUNE
            )
        
        # Shuffle if requested
        if shuffle:
            dataset = dataset.shuffle(buffer_size=1000)
        
        # Batch and prefetch
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset
    
    def _tf_preprocess_image(self, image_path: "tf.Tensor", label: "tf.Tensor") -> Tuple["tf.Tensor", "tf.Tensor"]:
        """
        TensorFlow preprocessing function for use with tf.data.Dataset
        
        Args:
            image_path: TensorFlow tensor containing image path
            label: TensorFlow tensor containing label
            
        Returns:
            Tuple of (preprocessed_image, label)
        """
        # Read image file
        image = tf.io.read_file(image_path)
        
        # Decode image
        if self.channels == 3:
            image = tf.image.decode_image(image, channels=3)
        else:
            image = tf.image.decode_image(image, channels=1)
        
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
    
    def _augment_image(self, image: "tf.Tensor") -> "tf.Tensor":
        """
        Apply data augmentation to an image tensor
        
        Args:
            image: Input image tensor
            
        Returns:
            Augmented image tensor
        """
        # Random horizontal flip
        image = tf.image.random_flip_left_right(image)
        
        # Random rotation (small angle)
        image = tf.image.rot90(image, k=tf.random.uniform([], 0, 4, dtype=tf.int32))
        
        # Random brightness adjustment
        image = tf.image.random_brightness(image, max_delta=0.1)
        
        # Random contrast adjustment
        image = tf.image.random_contrast(image, lower=0.9, upper=1.1)
        
        # Random saturation adjustment (only for RGB images)
        if self.channels == 3:
            image = tf.image.random_saturation(image, lower=0.9, upper=1.1)
        
        # Ensure values are still in valid range
        image = tf.clip_by_value(image, 0.0, 1.0 if self.normalize else 255.0)
        
        return image
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """
        Get current preprocessing configuration
        
        Returns:
            Dictionary with preprocessing parameters
        """
        return {
            'target_size': self.target_size,
            'normalize': self.normalize,
            'channels': self.channels,
            'input_shape': self.input_shape
        }

def create_train_val_split(image_paths: list, 
                          labels: list, 
                          val_split: float = 0.2,
                          stratify: bool = True,
                          random_state: int = 42) -> Tuple[list, list, list, list]:
    """
    Split image paths and labels into training and validation sets
    
    Args:
        image_paths: List of image file paths
        labels: List of corresponding labels
        val_split: Fraction of data to use for validation
        stratify: Whether to maintain class distribution in splits
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (train_paths, val_paths, train_labels, val_labels)
    """
    if not HAS_DEPS:
        raise ImportError("Required dependencies not available")
    
    try:
        from sklearn.model_selection import train_test_split
        
        if stratify:
            return train_test_split(
                image_paths, labels, 
                test_size=val_split, 
                stratify=labels, 
                random_state=random_state
            )
        else:
            return train_test_split(
                image_paths, labels, 
                test_size=val_split, 
                random_state=random_state
            )
    except ImportError:
        # Fallback to simple random split if sklearn not available
        np.random.seed(random_state)
        indices = np.random.permutation(len(image_paths))
        
        val_size = int(len(image_paths) * val_split)
        val_indices = indices[:val_size]
        train_indices = indices[val_size:]
        
        train_paths = [image_paths[i] for i in train_indices]
        val_paths = [image_paths[i] for i in val_indices]
        train_labels = [labels[i] for i in train_indices]
        val_labels = [labels[i] for i in val_indices]
        
        return train_paths, val_paths, train_labels, val_labels

def estimate_memory_usage(num_images: int, 
                         image_size: Tuple[int, int], 
                         channels: int = 3,
                         batch_size: int = 32) -> Dict[str, float]:
    """
    Estimate memory usage for image dataset
    
    Args:
        num_images: Total number of images
        image_size: Image dimensions (width, height)
        channels: Number of color channels
        batch_size: Batch size for training
        
    Returns:
        Dictionary with memory usage estimates in MB
    """
    # Calculate size per image in bytes (float32 = 4 bytes per pixel)
    pixels_per_image = image_size[0] * image_size[1] * channels
    bytes_per_image = pixels_per_image * 4  # float32
    
    # Calculate various memory usage scenarios
    single_image_mb = bytes_per_image / (1024 * 1024)
    batch_mb = (bytes_per_image * batch_size) / (1024 * 1024)
    full_dataset_mb = (bytes_per_image * num_images) / (1024 * 1024)
    
    return {
        'single_image_mb': single_image_mb,
        'batch_mb': batch_mb,
        'full_dataset_mb': full_dataset_mb,
        'recommended_batch_size': min(batch_size, max(1, int(1000 / single_image_mb)))
    }