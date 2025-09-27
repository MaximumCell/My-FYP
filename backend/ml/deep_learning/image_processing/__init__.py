"""
Image Processing Package for Deep Learning
Provides utilities for handling image data in CNN training pipelines
"""

from .image_preprocessor import ImagePreprocessor, create_train_val_split, estimate_memory_usage
from .data_augmentation import DataAugmentation, AUGMENTATION_PRESETS
from .dataset_generator import ImageDatasetGenerator

__all__ = [
    'ImagePreprocessor',
    'DataAugmentation',
    'ImageDatasetGenerator',
    'create_train_val_split',
    'estimate_memory_usage',
    'AUGMENTATION_PRESETS'
]