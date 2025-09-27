"""
Image Processing Utilities for CNN ZIP File Upload
Handles ZIP file extraction, validation, and organization for CNN training
"""

import os
import zipfile
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import mimetypes

# Try importing image processing libraries
try:
    from PIL import Image
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None
    np = None

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None

logger = logging.getLogger(__name__)

# Supported image extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}

class ImageProcessorError(Exception):
    """Custom exception for image processing errors"""
    pass

def extract_zip_file(zip_file_path: str, extract_to: str = None) -> str:
    """
    Extract ZIP file to a temporary directory
    
    Args:
        zip_file_path: Path to the ZIP file
        extract_to: Directory to extract to (if None, creates temp directory)
    
    Returns:
        Path to the extracted directory
    """
    if not os.path.exists(zip_file_path):
        raise ImageProcessorError(f"ZIP file not found: {zip_file_path}")
    
    if extract_to is None:
        extract_to = tempfile.mkdtemp(prefix="cnn_images_")
    
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Security check: prevent path traversal attacks
            for member in zip_ref.namelist():
                if os.path.isabs(member) or ".." in member:
                    raise ImageProcessorError(f"Unsafe path in ZIP: {member}")
            
            zip_ref.extractall(extract_to)
            logger.info(f"Extracted ZIP to: {extract_to}")
            return extract_to
    
    except zipfile.BadZipFile:
        raise ImageProcessorError("Invalid or corrupted ZIP file")
    except Exception as e:
        raise ImageProcessorError(f"Failed to extract ZIP file: {str(e)}")

def validate_image_structure(extracted_dir: str) -> Dict:
    """
    Validate the structure of extracted images
    Expected structure: class_folders/image_files
    
    Args:
        extracted_dir: Directory containing extracted images
    
    Returns:
        Dictionary with validation results and class information
    """
    result = {
        'valid': False,
        'classes': [],
        'total_images': 0,
        'class_counts': {},
        'errors': [],
        'warnings': []
    }
    
    if not os.path.exists(extracted_dir):
        result['errors'].append(f"Directory not found: {extracted_dir}")
        return result
    
    # Find all directories (potential classes)
    class_dirs = []
    root_images = []
    
    for item in os.listdir(extracted_dir):
        item_path = os.path.join(extracted_dir, item)
        
        if os.path.isdir(item_path):
            class_dirs.append(item)
        elif _is_image_file(item_path):
            root_images.append(item)
    
    # Check if images are in root directory (single class case)
    if root_images and not class_dirs:
        result['classes'] = ['default']
        result['class_counts']['default'] = len(root_images)
        result['total_images'] = len(root_images)
        result['valid'] = True
        result['warnings'].append("Images found in root directory. Using 'default' as class name.")
        return result
    
    # Check multi-class structure
    if not class_dirs:
        result['errors'].append("No class directories or images found")
        return result
    
    # Validate each class directory
    for class_name in class_dirs:
        class_path = os.path.join(extracted_dir, class_name)
        images = []
        
        for file in os.listdir(class_path):
            file_path = os.path.join(class_path, file)
            if _is_image_file(file_path):
                images.append(file)
        
        if images:
            result['classes'].append(class_name)
            result['class_counts'][class_name] = len(images)
            result['total_images'] += len(images)
        else:
            result['warnings'].append(f"No images found in class directory: {class_name}")
    
    # Validation checks
    if not result['classes']:
        result['errors'].append("No valid class directories with images found")
        return result
    
    if len(result['classes']) < 2:
        result['warnings'].append("Only one class found. Consider binary classification.")
    
    # Check minimum images per class
    min_images_per_class = 5
    for class_name, count in result['class_counts'].items():
        if count < min_images_per_class:
            result['warnings'].append(
                f"Class '{class_name}' has only {count} images. "
                f"Recommend at least {min_images_per_class} images per class."
            )
    
    result['valid'] = True
    return result

def organize_by_classes(extracted_dir: str, validation_result: Dict) -> Dict[str, List[str]]:
    """
    Organize images by classes into a dictionary structure
    
    Args:
        extracted_dir: Directory containing extracted images
        validation_result: Result from validate_image_structure
    
    Returns:
        Dictionary mapping class names to lists of image file paths
    """
    organized_images = {}
    
    if not validation_result['valid']:
        raise ImageProcessorError("Cannot organize invalid image structure")
    
    for class_name in validation_result['classes']:
        class_images = []
        
        if class_name == 'default':
            # Images in root directory
            for file in os.listdir(extracted_dir):
                file_path = os.path.join(extracted_dir, file)
                if _is_image_file(file_path):
                    class_images.append(file_path)
        else:
            # Images in class subdirectory
            class_dir = os.path.join(extracted_dir, class_name)
            for file in os.listdir(class_dir):
                file_path = os.path.join(class_dir, file)
                if _is_image_file(file_path):
                    class_images.append(file_path)
        
        organized_images[class_name] = class_images
    
    return organized_images

def preprocess_images(organized_images: Dict[str, List[str]], 
                     target_size: Tuple[int, int] = (224, 224),
                     normalize: bool = True) -> Dict:
    """
    Preprocess images for CNN training
    
    Args:
        organized_images: Dictionary mapping classes to image file paths
        target_size: Target size for resizing (width, height)
        normalize: Whether to normalize pixel values to [0, 1]
    
    Returns:
        Dictionary with preprocessed images and labels
    """
    if not HAS_PIL:
        raise ImageProcessorError("PIL (Pillow) is required for image preprocessing")
    
    processed_images = []
    labels = []
    class_to_idx = {class_name: idx for idx, class_name in enumerate(organized_images.keys())}
    
    total_images = sum(len(images) for images in organized_images.values())
    processed_count = 0
    
    logger.info(f"Preprocessing {total_images} images to size {target_size}")
    
    for class_name, image_paths in organized_images.items():
        class_idx = class_to_idx[class_name]
        
        for image_path in image_paths:
            try:
                # Load and preprocess image
                image = _load_and_preprocess_image(image_path, target_size, normalize)
                processed_images.append(image)
                labels.append(class_idx)
                
                processed_count += 1
                if processed_count % 100 == 0:
                    logger.info(f"Processed {processed_count}/{total_images} images")
                
            except Exception as e:
                logger.warning(f"Failed to process image {image_path}: {str(e)}")
                continue
    
    if not processed_images:
        raise ImageProcessorError("No images could be processed successfully")
    
    return {
        'images': np.array(processed_images) if np else processed_images,
        'labels': np.array(labels) if np else labels,
        'class_to_idx': class_to_idx,
        'idx_to_class': {idx: class_name for class_name, idx in class_to_idx.items()},
        'num_classes': len(class_to_idx),
        'image_shape': (*target_size, 3)  # Assuming RGB
    }

def create_image_dataset(zip_file_path: str, 
                        target_size: Tuple[int, int] = (224, 224),
                        normalize: bool = True,
                        cleanup: bool = True) -> Dict:
    """
    Complete pipeline to create dataset from ZIP file
    
    Args:
        zip_file_path: Path to the ZIP file containing images
        target_size: Target size for resizing images
        normalize: Whether to normalize pixel values
        cleanup: Whether to cleanup extracted files after processing
    
    Returns:
        Dictionary with processed dataset and metadata
    """
    extracted_dir = None
    
    try:
        # Step 1: Extract ZIP file
        extracted_dir = extract_zip_file(zip_file_path)
        
        # Step 2: Validate structure
        validation_result = validate_image_structure(extracted_dir)
        
        if not validation_result['valid']:
            errors = '; '.join(validation_result['errors'])
            raise ImageProcessorError(f"Invalid image structure: {errors}")
        
        # Step 3: Organize by classes
        organized_images = organize_by_classes(extracted_dir, validation_result)
        
        # Step 4: Preprocess images
        processed_data = preprocess_images(organized_images, target_size, normalize)
        
        # Add validation metadata
        processed_data['validation_result'] = validation_result
        processed_data['dataset_info'] = {
            'total_images': validation_result['total_images'],
            'num_classes': len(validation_result['classes']),
            'classes': validation_result['classes'],
            'class_counts': validation_result['class_counts'],
            'target_size': target_size,
            'normalized': normalize
        }
        
        logger.info(f"Successfully created dataset with {processed_data['dataset_info']['total_images']} images")
        
        return processed_data
    
    except Exception as e:
        logger.error(f"Failed to create image dataset: {str(e)}")
        raise
    
    finally:
        # Cleanup extracted files if requested
        if cleanup and extracted_dir and os.path.exists(extracted_dir):
            try:
                shutil.rmtree(extracted_dir)
                logger.info(f"Cleaned up extracted directory: {extracted_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup directory {extracted_dir}: {str(e)}")

def _is_image_file(file_path: str) -> bool:
    """
    Check if a file is a supported image format
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if file is a supported image format
    """
    if not os.path.isfile(file_path):
        return False
    
    # Check extension
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and not mime_type.startswith('image/'):
        return False
    
    # Try to open with PIL for final validation
    if HAS_PIL:
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify it's a valid image
            return True
        except Exception:
            return False
    
    return True

def _load_and_preprocess_image(image_path: str, 
                              target_size: Tuple[int, int], 
                              normalize: bool = True) -> np.ndarray:
    """
    Load and preprocess a single image
    
    Args:
        image_path: Path to the image file
        target_size: Target size (width, height)
        normalize: Whether to normalize pixel values
    
    Returns:
        Preprocessed image array
    """
    if not HAS_PIL:
        raise ImageProcessorError("PIL (Pillow) is required for image loading")
    
    try:
        # Load image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize image
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            img_array = np.array(img, dtype=np.float32)
            
            # Normalize if requested
            if normalize:
                img_array = img_array / 255.0
            
            return img_array
    
    except Exception as e:
        raise ImageProcessorError(f"Failed to load image {image_path}: {str(e)}")

def get_image_info(image_path: str) -> Dict:
    """
    Get information about an image file
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary with image information
    """
    if not HAS_PIL:
        return {"error": "PIL (Pillow) is required for image info"}
    
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
        return {"error": f"Failed to get image info: {str(e)}"}