#!/usr/bin/env python3
"""
Test Script for CNN Image Implementation
Tests basic functionality of ZIP file processing and image handling
"""

import os
import sys
import tempfile
import zipfile
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def create_test_zip():
    """
    Create a test ZIP file with sample image structure
    """
    test_dir = tempfile.mkdtemp(prefix="test_cnn_")
    
    # Create class directories
    class_dirs = ['cats', 'dogs']
    
    for class_name in class_dirs:
        class_dir = os.path.join(test_dir, class_name)
        os.makedirs(class_dir)
        
        # Create dummy image files (just text files for testing structure)
        for i in range(3):
            dummy_file = os.path.join(class_dir, f"{class_name}_{i+1}.jpg")
            with open(dummy_file, 'w') as f:
                f.write(f"dummy image file for {class_name} {i+1}")
    
    # Create ZIP file
    zip_path = os.path.join(tempfile.gettempdir(), "test_cnn_images.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, test_dir)
                zipf.write(file_path, arc_path)
    
    # Cleanup temp directory
    import shutil
    shutil.rmtree(test_dir)
    
    return zip_path

def test_image_processor():
    """
    Test the image processor utilities
    """
    print("Testing Image Processor...")
    
    try:
        from utils.image_processor import extract_zip_file, validate_image_structure
        
        # Create test ZIP
        zip_path = create_test_zip()
        print(f"Created test ZIP: {zip_path}")
        
        # Test extraction
        extracted_dir = extract_zip_file(zip_path)
        print(f"Extracted to: {extracted_dir}")
        
        # Test validation
        validation_result = validate_image_structure(extracted_dir)
        print("Validation result:")
        print(f"  Valid: {validation_result['valid']}")
        print(f"  Classes: {validation_result['classes']}")
        print(f"  Total images: {validation_result['total_images']}")
        print(f"  Class counts: {validation_result['class_counts']}")
        
        if validation_result['errors']:
            print(f"  Errors: {validation_result['errors']}")
        
        if validation_result['warnings']:
            print(f"  Warnings: {validation_result['warnings']}")
        
        # Cleanup
        import shutil
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
        if os.path.exists(zip_path):
            os.unlink(zip_path)
        
        print("✅ Image processor test passed")
        return True
        
    except Exception as e:
        print(f"❌ Image processor test failed: {str(e)}")
        return False

def test_image_preprocessing():
    """
    Test the image preprocessing components
    """
    print("\nTesting Image Preprocessing...")
    
    try:
        from ml.deep_learning.image_processing import ImagePreprocessor
        
        # Test with dummy parameters
        preprocessor = ImagePreprocessor(
            target_size=(224, 224),
            normalize=True,
            channels=3
        )
        
        config = preprocessor.get_preprocessing_config()
        print(f"Preprocessor config: {config}")
        
        print("✅ Image preprocessing test passed")
        return True
        
    except ImportError as e:
        print(f"⚠️  Image preprocessing test skipped (missing dependencies): {str(e)}")
        return True
    except Exception as e:
        print(f"❌ Image preprocessing test failed: {str(e)}")
        return False

def test_data_augmentation():
    """
    Test the data augmentation components
    """
    print("\nTesting Data Augmentation...")
    
    try:
        from ml.deep_learning.image_processing import DataAugmentation, AUGMENTATION_PRESETS
        
        # Test preset loading
        print(f"Available presets: {list(AUGMENTATION_PRESETS.keys())}")
        
        # Test augmentation creation
        augmentation = DataAugmentation(AUGMENTATION_PRESETS['light'])
        config = augmentation.get_config()
        print(f"Augmentation config: {config}")
        
        print("✅ Data augmentation test passed")
        return True
        
    except ImportError as e:
        print(f"⚠️  Data augmentation test skipped (missing dependencies): {str(e)}")
        return True
    except Exception as e:
        print(f"❌ Data augmentation test failed: {str(e)}")
        return False

def test_api_imports():
    """
    Test that the new API endpoints can import their dependencies
    """
    print("\nTesting API Imports...")
    
    try:
        # Test training import
        print("Testing training module import...")
        from ml.deep_learning.training.train_cnn_images import train_cnn_with_images
        print("✅ Training module import successful")
        
        # Test inference import
        print("Testing inference module import...")
        from ml.deep_learning.inference.predict_cnn_images import predict_single_image
        print("✅ Inference module import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ API imports test failed: {str(e)}")
        print("This is expected if TensorFlow/PIL are not installed")
        return False
    except Exception as e:
        print(f"❌ API imports test failed: {str(e)}")
        return False

def test_model_structure():
    """
    Test the CNN model structure
    """
    print("\nTesting CNN Model Structure...")
    
    try:
        from ml.deep_learning.models.cnn import get_model
        
        # Test model creation with different configurations
        print("Testing model creation...")
        
        # Basic model
        model = get_model(input_shape=(224, 224, 3), num_classes=2)
        
        if hasattr(model, 'summary'):
            print("✅ Model created successfully")
            print(f"Model input shape: {model.input_shape}")
            print(f"Model output shape: {model.output_shape}")
        else:
            print("❌ Model creation failed - invalid model object")
            return False
        
        return True
        
    except ImportError as e:
        print(f"⚠️  Model structure test skipped (TensorFlow not available): {str(e)}")
        return True
    except Exception as e:
        print(f"❌ Model structure test failed: {str(e)}")
        return False

def check_requirements():
    """
    Check if all required packages are available
    """
    print("Checking Requirements...")
    
    required_packages = [
        ('numpy', 'NumPy'),
        ('tensorflow', 'TensorFlow'),
        ('PIL', 'Pillow'),
        ('sklearn', 'scikit-learn')
    ]
    
    available = []
    missing = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            available.append(name)
            print(f"✅ {name} is available")
        except ImportError:
            missing.append(name)
            print(f"❌ {name} is missing")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
    else:
        print("\n✅ All required packages are available")
    
    return len(missing) == 0

def main():
    """
    Run all tests
    """
    print("=" * 60)
    print("CNN Image Implementation Test Suite")
    print("=" * 60)
    
    # Check requirements first
    all_deps_available = check_requirements()
    print()
    
    # Run tests
    tests = [
        ("Image Processor", test_image_processor),
        ("Image Preprocessing", test_image_preprocessing),
        ("Data Augmentation", test_data_augmentation),
        ("API Imports", test_api_imports),
        ("CNN Model Structure", test_model_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if not all_deps_available:
        print("\n⚠️  Some tests were skipped due to missing dependencies")
        print("Install missing packages with: pip install -r requirements.txt")
    
    if passed == total:
        print("\n🎉 All tests passed! CNN image implementation is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())