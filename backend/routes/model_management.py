"""
ML Model Management Routes for PhysicsLab Application
Handles ML model upload, download, listing, and deletion with Cloudinary integration
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from typing import Optional
import logging

# Import our models and utilities
from models.ml_model import MLModelService, MLModelCreate, MLModelUpdate, ModelType, DatasetInfo, PerformanceMetrics
from models.user import UserService
from utils.cloudinary_upload import CloudinaryUploadManager, CloudinaryUploadError
from utils.error_handler import CloudinaryErrorHandler, ErrorCode
from utils.database import get_database
from utils.analytics_tracker import track_activity, get_analytics_tracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
model_bp = Blueprint('models', __name__, url_prefix='/api/models')

# Initialize services
db = get_database()
model_service = MLModelService(db)
user_service = UserService(db)
upload_manager = CloudinaryUploadManager()

def get_current_user_id():
    """
    Extract user ID from request headers and get the corresponding MongoDB user ID
    In production, this would integrate with Clerk authentication
    """
    # Get Clerk user ID from header
    clerk_user_id = request.headers.get('X-Clerk-User-ID')
    if not clerk_user_id:
        # Fallback to direct MongoDB user ID for testing
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            raise ValueError("User authentication required")
        return user_id
    
    # Find the user in database by Clerk ID
    user = user_service.get_user_by_clerk_id(clerk_user_id)
    if not user:
        raise ValueError("User not found")
    
    return str(user.id)

def validate_model_file(file):
    """Validate uploaded model file"""
    if not file:
        raise ValueError("No file provided")
    
    if file.filename == '':
        raise ValueError("No file selected")
    
    # Check file extension - allow both .pkl and .keras files
    allowed_extensions = ['.pkl', '.keras', '.h5']
    filename_lower = file.filename.lower()
    if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
        raise ValueError(f"Only {', '.join(allowed_extensions)} files are allowed for model upload")
    
    return True

@model_bp.route('/upload', methods=['POST'])
def upload_model():
    """
    Upload a trained ML model
    POST /api/models/upload
    
    Form data:
    - file: .pkl model file
    - model_name: User-friendly model name
    - model_type: regression/classification/clustering/other
    - dataset_info: JSON with dataset information
    - performance_metrics: JSON with model metrics
    - training_time: Training time in seconds
    - description: Optional model description
    - tags: Optional comma-separated tags
    - algorithm_name: Optional algorithm name
    - hyperparameters: Optional JSON with hyperparameters
    - is_public: Optional boolean for sharing
    """
    try:
        # Get current user
        user_id = get_current_user_id()
        
        # Validate file upload
        if 'file' not in request.files:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "No file uploaded"
            ), 400
        
        file = request.files['file']
        validate_model_file(file)
        
        # Get form data
        model_name = request.form.get('model_name')
        model_type = request.form.get('model_type')
        dataset_info_json = request.form.get('dataset_info')
        performance_metrics_json = request.form.get('performance_metrics')
        training_time = request.form.get('training_time')
        
        # Required fields validation
        if not all([model_name, model_type, dataset_info_json, performance_metrics_json, training_time]):
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "Missing required fields: model_name, model_type, dataset_info, performance_metrics, training_time"
            ), 400
        
        # Parse JSON data
        import json
        try:
            dataset_info_data = json.loads(dataset_info_json)
            performance_metrics_data = json.loads(performance_metrics_json)
            training_time_float = float(training_time)
        except (json.JSONDecodeError, ValueError) as e:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                f"Invalid JSON data or training_time format: {str(e)}"
            ), 400
        
        # Optional fields
        description = request.form.get('description')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        algorithm_name = request.form.get('algorithm_name')
        hyperparameters = json.loads(request.form.get('hyperparameters', '{}'))
        is_public = request.form.get('is_public', 'false').lower() == 'true'
        
        # Create model data objects
        dataset_info = DatasetInfo(**dataset_info_data)
        performance_metrics = PerformanceMetrics(**performance_metrics_data)
        
        model_create_data = MLModelCreate(
            model_name=model_name,
            model_type=ModelType(model_type),
            dataset_info=dataset_info,
            performance_metrics=performance_metrics,
            training_time=training_time_float,
            description=description,
            tags=[tag.strip() for tag in tags if tag.strip()],
            algorithm_name=algorithm_name,
            hyperparameters=hyperparameters,
            is_public=is_public
        )
        
        # Upload file to Cloudinary
        file_data = file.read()
        upload_result = upload_manager.upload_model_file(
            file_data=file_data,
            filename=file.filename,
            user_id=user_id,
            model_name=model_name
        )
        
        # Save model metadata to database
        created_model = model_service.create_model(
            user_id=user_id,
            model_data=model_create_data,
            file_info=upload_result
        )
        
        if not created_model:
            # If database save failed, clean up Cloudinary file
            upload_manager.delete_file(upload_result['public_id'])
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Failed to save model metadata"
            ), 500
        
        # Track model training activity
        clerk_user_id = request.headers.get('X-Clerk-User-ID')
        if clerk_user_id:
            tracker = get_analytics_tracker()
            if tracker:
                model_data = {
                    "model_id": str(created_model.id),
                    "model_type": model_type,
                    "performance_metrics": performance_metrics_data
                }
                tracker.track_model_training(clerk_user_id, training_time_float, model_data)
                
                # Track file upload size
                file_size = len(file_data) if file_data else 0
                tracker.track_file_upload(clerk_user_id, file_size, "model")
        
        return CloudinaryErrorHandler.format_success_response(
            created_model.model_dump(),
            "Model uploaded successfully"
        ), 201
        
    except CloudinaryUploadError as e:
        return CloudinaryErrorHandler.handle_upload_error(str(e)), 400
    except ValueError as e:
        return CloudinaryErrorHandler.handle_file_validation_error(str(e)), 400
    except Exception as e:
        logger.error(f"Model upload error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@model_bp.route('', methods=['GET'])
def list_models():
    """
    Get paginated list of user's models
    GET /api/models?page=1&page_size=10&model_type=regression&search=query
    """
    try:
        user_id = get_current_user_id()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        model_type = request.args.get('model_type')
        search_query = request.args.get('search')
        
        # Validate parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # Get models
        result = model_service.get_user_models(
            user_id=user_id,
            page=page,
            page_size=page_size,
            model_type=model_type,
            search_query=search_query
        )
        
        return CloudinaryErrorHandler.format_success_response(
            result.model_dump(),
            "Models retrieved successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"List models error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@model_bp.route('/<model_id>', methods=['GET'])
def get_model(model_id):
    """
    Get specific model details
    GET /api/models/{model_id}
    """
    try:
        user_id = get_current_user_id()
        
        model = model_service.get_model_by_id(model_id, user_id)
        if not model:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Model not found"
            ), 404
        
        return CloudinaryErrorHandler.format_success_response(
            model.model_dump(),
            "Model retrieved successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Get model error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@model_bp.route('/<model_id>/download', methods=['GET'])
def download_model(model_id):
    """
    Generate secure download URL for model file
    GET /api/models/{model_id}/download
    """
    try:
        user_id = get_current_user_id()
        
        # Get model info
        model = model_service.get_model_by_id(model_id, user_id)
        if not model:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Model not found"
            ), 404
        
        # Generate download URL
        download_url = upload_manager.get_download_url(
            model.file_public_id,
            expiration=3600  # 1 hour
        )
        
        return CloudinaryErrorHandler.format_success_response(
            {
                "download_url": download_url,
                "model_name": model.model_name,
                "file_size": model.file_size,
                "expires_in": 3600
            },
            "Download URL generated successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Download model error: {str(e)}")
        return CloudinaryErrorHandler.handle_download_error(str(e)), 500

@model_bp.route('/<model_id>', methods=['PUT'])
def update_model(model_id):
    """
    Update model metadata
    PUT /api/models/{model_id}
    
    JSON body can include:
    - model_name
    - description
    - tags
    - is_public
    """
    try:
        user_id = get_current_user_id()
        
        # Check if model exists and belongs to user
        existing_model = model_service.get_model_by_id(model_id, user_id)
        if not existing_model:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Model not found"
            ), 404
        
        # Get update data
        update_data = request.get_json()
        if not update_data:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "No update data provided"
            ), 400
        
        # Create update object
        model_update = MLModelUpdate(**update_data)
        
        # Update model
        updated_model = model_service.update_model(model_id, user_id, model_update)
        if not updated_model:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Failed to update model"
            ), 500
        
        return CloudinaryErrorHandler.format_success_response(
            updated_model.model_dump(),
            "Model updated successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Update model error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@model_bp.route('/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """
    Delete model and cleanup associated files
    DELETE /api/models/{model_id}
    """
    try:
        user_id = get_current_user_id()
        
        # Get model info before deletion
        model = model_service.get_model_by_id(model_id, user_id)
        if not model:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Model not found"
            ), 404
        
        # Delete from Cloudinary first
        cloudinary_deleted = upload_manager.delete_file(model.file_public_id)
        if not cloudinary_deleted:
            logger.warning(f"Failed to delete Cloudinary file: {model.file_public_id}")
            # Continue with database deletion even if Cloudinary deletion fails
        
        # Delete from database
        db_deleted = model_service.delete_model(model_id, user_id)
        if not db_deleted:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Failed to delete model from database"
            ), 500
        
        return CloudinaryErrorHandler.format_success_response(
            {"deleted_model_id": model_id},
            "Model deleted successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Delete model error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@model_bp.route('/public', methods=['GET'])
def list_public_models():
    """
    Get paginated list of public models
    GET /api/models/public?page=1&page_size=10
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        # Validate parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # Get public models
        result = model_service.get_public_models(
            page=page,
            page_size=page_size
        )
        
        return CloudinaryErrorHandler.format_success_response(
            result.model_dump(),
            "Public models retrieved successfully"
        ), 200
        
    except Exception as e:
        logger.error(f"List public models error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

# Error handlers for the blueprint
@model_bp.errorhandler(400)
def bad_request(error):
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.VALIDATION_ERROR,
        "Bad request"
    ), 400

@model_bp.errorhandler(404)
def not_found(error):
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.FILE_NOT_FOUND,
        "Resource not found"
    ), 404

@model_bp.errorhandler(500)
def internal_error(error):
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.INTERNAL_ERROR,
        "Internal server error"
    ), 500