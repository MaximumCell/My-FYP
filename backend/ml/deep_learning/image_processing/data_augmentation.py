"""
Data Augmentation Module
Advanced image augmentation techniques for improving CNN training
"""

import random
from typing import Optional, Dict, Any, Tuple, Union
import logging

try:
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
except ImportError:
    HAS_DEPS = False
    np = None
    Image = None
    tf = None

logger = logging.getLogger(__name__)

class DataAugmentation:
    """
    Data augmentation class with various image transformation techniques
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize data augmentation with configuration
        
        Args:
            config: Dictionary with augmentation parameters
        """
        if not HAS_DEPS:
            raise ImportError("Required dependencies not available: numpy, PIL, tensorflow")
        
        # Default configuration
        default_config = {
            'rotation_range': 15,      # degrees
            'width_shift_range': 0.1,  # fraction of total width
            'height_shift_range': 0.1, # fraction of total height
            'shear_range': 0.1,        # shear intensity
            'zoom_range': 0.1,         # zoom range
            'brightness_range': 0.1,   # brightness variation
            'contrast_range': 0.1,     # contrast variation
            'saturation_range': 0.1,   # saturation variation
            'hue_range': 0.05,         # hue variation
            'horizontal_flip': True,   # enable horizontal flip
            'vertical_flip': False,    # enable vertical flip
            'gaussian_noise': 0.01,    # gaussian noise standard deviation
            'blur_range': 0.5,         # blur kernel size range
            'sharpen_factor': 0.1,     # sharpening intensity
            'probability': 0.5         # probability of applying each augmentation
        }
        
        self.config = {**default_config, **(config or {})}
    
    def augment_image_pil(self, image: "Image.Image") -> "Image.Image":
        """
        Apply augmentation to a PIL Image
        
        Args:
            image: Input PIL Image
            
        Returns:
            Augmented PIL Image
        """
        img = image.copy()
        
        # Geometric transformations
        if random.random() < self.config['probability']:
            img = self._apply_rotation(img)
        
        if random.random() < self.config['probability']:
            img = self._apply_shift(img)
        
        if random.random() < self.config['probability']:
            img = self._apply_shear(img)
        
        if random.random() < self.config['probability']:
            img = self._apply_zoom(img)
        
        # Flipping
        if self.config['horizontal_flip'] and random.random() < self.config['probability']:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        
        if self.config['vertical_flip'] and random.random() < self.config['probability']:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        # Color transformations
        if random.random() < self.config['probability']:
            img = self._apply_brightness(img)
        
        if random.random() < self.config['probability']:
            img = self._apply_contrast(img)
        
        if img.mode == 'RGB':
            if random.random() < self.config['probability']:
                img = self._apply_saturation(img)
            
            if random.random() < self.config['probability']:
                img = self._apply_hue(img)
        
        # Filtering effects
        if random.random() < self.config['probability']:
            img = self._apply_blur(img)
        
        if random.random() < self.config['probability']:
            img = self._apply_sharpen(img)
        
        return img
    
    def augment_array(self, image_array: np.ndarray) -> np.ndarray:
        """
        Apply augmentation to a numpy array image
        
        Args:
            image_array: Input image as numpy array (H, W, C) or (H, W)
            
        Returns:
            Augmented image array
        """
        # Convert to PIL for augmentation
        if len(image_array.shape) == 2:
            # Grayscale
            img = Image.fromarray((image_array * 255).astype(np.uint8), mode='L')
        elif len(image_array.shape) == 3:
            if image_array.shape[-1] == 3:
                # RGB
                img = Image.fromarray((image_array * 255).astype(np.uint8), mode='RGB')
            elif image_array.shape[-1] == 1:
                # Single channel
                img = Image.fromarray((image_array.squeeze() * 255).astype(np.uint8), mode='L')
            else:
                raise ValueError(f"Unsupported number of channels: {image_array.shape[-1]}")
        else:
            raise ValueError(f"Unsupported image shape: {image_array.shape}")
        
        # Apply augmentation
        augmented_img = self.augment_image_pil(img)
        
        # Convert back to array
        augmented_array = np.array(augmented_img, dtype=np.float32) / 255.0
        
        # Restore original shape if needed
        if len(image_array.shape) == 3 and image_array.shape[-1] == 1:
            augmented_array = np.expand_dims(augmented_array, axis=-1)
        
        return augmented_array
    
    def create_tf_augmentation_layer(self) -> "tf.keras.Sequential":
        """
        Create TensorFlow/Keras augmentation layers
        
        Returns:
            Sequential model with augmentation layers
        """
        if not tf:
            raise ImportError("TensorFlow is required for TF augmentation layers")
        
        layers = []
        
        # Random flip
        if self.config['horizontal_flip']:
            layers.append(tf.keras.layers.RandomFlip("horizontal"))
        
        if self.config['vertical_flip']:
            layers.append(tf.keras.layers.RandomFlip("vertical"))
        
        # Random rotation
        if self.config['rotation_range'] > 0:
            layers.append(tf.keras.layers.RandomRotation(
                self.config['rotation_range'] / 180.0  # Convert to fraction
            ))
        
        # Random translation
        if self.config['width_shift_range'] > 0 or self.config['height_shift_range'] > 0:
            layers.append(tf.keras.layers.RandomTranslation(
                height_factor=self.config['height_shift_range'],
                width_factor=self.config['width_shift_range']
            ))
        
        # Random zoom
        if self.config['zoom_range'] > 0:
            layers.append(tf.keras.layers.RandomZoom(self.config['zoom_range']))
        
        # Random contrast
        if self.config['contrast_range'] > 0:
            layers.append(tf.keras.layers.RandomContrast(self.config['contrast_range']))
        
        # Random brightness
        if self.config['brightness_range'] > 0:
            layers.append(tf.keras.layers.RandomBrightness(self.config['brightness_range']))
        
        return tf.keras.Sequential(layers)
    
    def _apply_rotation(self, img: "Image.Image") -> "Image.Image":
        """Apply random rotation"""
        angle = random.uniform(-self.config['rotation_range'], self.config['rotation_range'])
        return img.rotate(angle, fillcolor=(128, 128, 128) if img.mode == 'RGB' else 128)
    
    def _apply_shift(self, img: "Image.Image") -> "Image.Image":
        """Apply random translation"""
        width, height = img.size
        
        dx = int(random.uniform(-self.config['width_shift_range'], self.config['width_shift_range']) * width)
        dy = int(random.uniform(-self.config['height_shift_range'], self.config['height_shift_range']) * height)
        
        return img.transform(img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy))
    
    def _apply_shear(self, img: "Image.Image") -> "Image.Image":
        """Apply random shear transformation"""
        shear = random.uniform(-self.config['shear_range'], self.config['shear_range'])
        return img.transform(img.size, Image.AFFINE, (1, shear, 0, 0, 1, 0))
    
    def _apply_zoom(self, img: "Image.Image") -> "Image.Image":
        """Apply random zoom"""
        zoom = 1 + random.uniform(-self.config['zoom_range'], self.config['zoom_range'])
        
        width, height = img.size
        new_width = int(width * zoom)
        new_height = int(height * zoom)
        
        # Resize and crop/pad to original size
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        if zoom > 1:
            # Crop to original size
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            return resized.crop((left, top, left + width, top + height))
        else:
            # Pad to original size
            new_img = Image.new(img.mode, (width, height), (128, 128, 128) if img.mode == 'RGB' else 128)
            left = (width - new_width) // 2
            top = (height - new_height) // 2
            new_img.paste(resized, (left, top))
            return new_img
    
    def _apply_brightness(self, img: "Image.Image") -> "Image.Image":
        """Apply random brightness adjustment"""
        factor = 1 + random.uniform(-self.config['brightness_range'], self.config['brightness_range'])
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def _apply_contrast(self, img: "Image.Image") -> "Image.Image":
        """Apply random contrast adjustment"""
        factor = 1 + random.uniform(-self.config['contrast_range'], self.config['contrast_range'])
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    def _apply_saturation(self, img: "Image.Image") -> "Image.Image":
        """Apply random saturation adjustment (RGB only)"""
        if img.mode != 'RGB':
            return img
        
        factor = 1 + random.uniform(-self.config['saturation_range'], self.config['saturation_range'])
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(factor)
    
    def _apply_hue(self, img: "Image.Image") -> "Image.Image":
        """Apply random hue shift (RGB only)"""
        if img.mode != 'RGB':
            return img
        
        # Convert to HSV, adjust hue, convert back
        hsv = img.convert('HSV')
        h, s, v = hsv.split()
        
        # Adjust hue
        hue_shift = int(random.uniform(-self.config['hue_range'], self.config['hue_range']) * 255)
        h_array = np.array(h, dtype=np.int16)
        h_array = (h_array + hue_shift) % 256
        h = Image.fromarray(h_array.astype(np.uint8), mode='L')
        
        # Recombine and convert back to RGB
        hsv_adjusted = Image.merge('HSV', (h, s, v))
        return hsv_adjusted.convert('RGB')
    
    def _apply_blur(self, img: "Image.Image") -> "Image.Image":
        """Apply random gaussian blur"""
        radius = random.uniform(0, self.config['blur_range'])
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    def _apply_sharpen(self, img: "Image.Image") -> "Image.Image":
        """Apply random sharpening"""
        if random.random() < self.config['sharpen_factor']:
            return img.filter(ImageFilter.SHARPEN)
        return img
    
    def get_config(self) -> Dict[str, Any]:
        """Get current augmentation configuration"""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update augmentation configuration"""
        self.config.update(new_config)

# Predefined augmentation presets
AUGMENTATION_PRESETS = {
    'light': {
        'rotation_range': 10,
        'width_shift_range': 0.05,
        'height_shift_range': 0.05,
        'zoom_range': 0.05,
        'brightness_range': 0.05,
        'contrast_range': 0.05,
        'horizontal_flip': True,
        'probability': 0.3
    },
    'medium': {
        'rotation_range': 20,
        'width_shift_range': 0.1,
        'height_shift_range': 0.1,
        'zoom_range': 0.1,
        'brightness_range': 0.1,
        'contrast_range': 0.1,
        'saturation_range': 0.1,
        'horizontal_flip': True,
        'probability': 0.5
    },
    'heavy': {
        'rotation_range': 30,
        'width_shift_range': 0.2,
        'height_shift_range': 0.2,
        'shear_range': 0.2,
        'zoom_range': 0.2,
        'brightness_range': 0.2,
        'contrast_range': 0.2,
        'saturation_range': 0.2,
        'hue_range': 0.1,
        'horizontal_flip': True,
        'vertical_flip': False,
        'gaussian_noise': 0.02,
        'blur_range': 1.0,
        'probability': 0.7
    }
}