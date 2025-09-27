"""
Simulation Management Routes for PhysicsLab Application
Handles simulation save, listing, viewing, and deletion with Cloudinary integration
"""
from flask import Blueprint, request, jsonify, redirect
from werkzeug.utils import secure_filename
import os
from typing import Optional
import logging
import json
import base64

# Import our models and utilities
from models.simulation import SimulationService, SimulationCreate, SimulationUpdate, SimulationType, SimulationConfig
from models.user import UserService
from utils.cloudinary_upload import CloudinaryUploadManager, CloudinaryUploadError
from utils.error_handler import CloudinaryErrorHandler, ErrorCode
from utils.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
simulation_bp = Blueprint('simulations', __name__, url_prefix='/api/simulations')

# Initialize services
db = get_database()
simulation_service = SimulationService(db)
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

@simulation_bp.route('/save', methods=['POST'])
def save_simulation():
    """
    Save a simulation result with HTML plot
    POST /api/simulations/save
    
    JSON body:
    {
        "simulation_name": "My Physics Simulation",
        "simulation_type": "plot2d",
        "description": "Optional description",
        "tags": ["physics", "plot"],
        "config": {
            "equation": "x**2 + y**2",
            "parameters": {"param1": "value1"},
            "variables": ["x", "y"],
            "plot_type": "surface",
            "x_range": [-10, 10],
            "y_range": [-10, 10]
        },
        "execution_time": 2.5,
        "plot_title": "My Plot",
        "x_label": "X axis",
        "y_label": "Y axis",
        "z_label": "Z axis",
        "is_public": false,
        "plot_html": "<html>...</html>",
        "plot_thumbnail": "data:image/png;base64,..."  // Optional PNG thumbnail
    }
    """
    try:
        # Get current user
        user_id = get_current_user_id()
        
        # Get JSON data
        data = request.get_json()
        if not data:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "No JSON data provided"
            ), 400
        
        # Extract required fields
        simulation_name = data.get('simulation_name')
        simulation_type = data.get('simulation_type')
        config_data = data.get('config', {})
        execution_time = data.get('execution_time')
        plot_html = data.get('plot_html')
        
        # Required fields validation
        if not all([simulation_name, simulation_type, config_data, execution_time is not None, plot_html]):
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "Missing required fields: simulation_name, simulation_type, config, execution_time, plot_html"
            ), 400
        
        try:
            execution_time_float = float(execution_time)
        except (ValueError, TypeError):
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "execution_time must be a valid number"
            ), 400
        
        # Optional fields
        description = data.get('description')
        tags = data.get('tags', [])
        plot_title = data.get('plot_title')
        x_label = data.get('x_label')
        y_label = data.get('y_label')
        z_label = data.get('z_label')
        is_public = data.get('is_public', False)
        plot_thumbnail = data.get('plot_thumbnail')  # Base64 encoded PNG
        
        # Create configuration object
        try:
            config = SimulationConfig(**config_data)
        except Exception as e:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                f"Invalid config data: {str(e)}"
            ), 400
        
        # Create simulation data object
        try:
            simulation_create_data = SimulationCreate(
                simulation_name=simulation_name,
                simulation_type=SimulationType(simulation_type),
                description=description,
                tags=[tag.strip() for tag in tags if tag.strip()] if tags else [],
                config=config,
                execution_time=execution_time_float,
                plot_title=plot_title,
                x_label=x_label,
                y_label=y_label,
                z_label=z_label,
                is_public=is_public
            )
        except Exception as e:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                f"Invalid simulation data: {str(e)}"
            ), 400
        
        # Upload HTML plot to Cloudinary
        html_filename = f"{simulation_name.replace(' ', '_')}.html"
        html_upload_result = upload_manager.upload_simulation_file(
            file_data=plot_html,
            filename=html_filename,
            user_id=user_id,
            simulation_name=simulation_name,
            file_type='html'
        )
        
        # Upload thumbnail if provided
        thumbnail_upload_result = None
        if plot_thumbnail:
            try:
                # Decode base64 thumbnail
                if plot_thumbnail.startswith('data:image/png;base64,'):
                    thumbnail_data = base64.b64decode(plot_thumbnail.split(',')[1])
                else:
                    thumbnail_data = base64.b64decode(plot_thumbnail)
                
                thumbnail_filename = f"{simulation_name.replace(' ', '_')}.png"
                thumbnail_upload_result = upload_manager.upload_simulation_file(
                    file_data=thumbnail_data,
                    filename=thumbnail_filename,
                    user_id=user_id,
                    simulation_name=f"{simulation_name}_thumbnail",
                    file_type='png'
                )
            except Exception as e:
                logger.warning(f"Failed to upload thumbnail: {str(e)}")
                # Continue without thumbnail - it's optional
        
        # Save simulation metadata to database
        created_simulation = simulation_service.create_simulation(
            user_id=user_id,
            simulation_data=simulation_create_data,
            file_info=html_upload_result,
            thumbnail_info=thumbnail_upload_result
        )
        
        if not created_simulation:
            # If database save failed, clean up Cloudinary files
            upload_manager.delete_file(html_upload_result['public_id'])
            if thumbnail_upload_result:
                upload_manager.delete_file(thumbnail_upload_result['public_id'])
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Failed to save simulation metadata"
            ), 500
        
        # Update user analytics
        user_service.update_usage_analytics(
            user_id, 
            {'total_simulations_run': 1}  # This would increment the existing count
        )
        
        return CloudinaryErrorHandler.format_success_response(
            created_simulation.model_dump(),
            "Simulation saved successfully"
        ), 201
        
    except CloudinaryUploadError as e:
        return CloudinaryErrorHandler.handle_upload_error(str(e)), 400
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Simulation save error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@simulation_bp.route('', methods=['GET'])
def list_simulations():
    """
    Get paginated list of user's simulations
    GET /api/simulations?page=1&page_size=10&simulation_type=plot2d&search=query
    """
    try:
        user_id = get_current_user_id()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        simulation_type = request.args.get('simulation_type')
        search_query = request.args.get('search')
        
        # Validate parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # Get simulations
        result = simulation_service.get_user_simulations(
            user_id=user_id,
            page=page,
            page_size=page_size,
            simulation_type=simulation_type,
            search_query=search_query
        )
        
        return CloudinaryErrorHandler.format_success_response(
            result.model_dump(),
            "Simulations retrieved successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"List simulations error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@simulation_bp.route('/<simulation_id>', methods=['GET'])
def get_simulation(simulation_id):
    """
    Get specific simulation details
    GET /api/simulations/{simulation_id}
    """
    try:
        user_id = get_current_user_id()
        
        simulation = simulation_service.get_simulation_by_id(simulation_id, user_id)
        if not simulation:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Simulation not found"
            ), 404
        
        return CloudinaryErrorHandler.format_success_response(
            simulation.model_dump(),
            "Simulation retrieved successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Get simulation error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@simulation_bp.route('/<simulation_id>/view', methods=['GET'])
def view_simulation(simulation_id):
    """
    View HTML simulation plot
    GET /api/simulations/{simulation_id}/view
    
    This endpoint redirects to the Cloudinary-hosted HTML file for direct viewing
    """
    try:
        # Allow viewing public simulations without authentication
        user_id = None
        try:
            user_id = get_current_user_id()
        except:
            pass  # No authentication for public simulations
        
        # Get simulation info
        simulation = simulation_service.get_simulation_by_id(simulation_id, user_id)
        if not simulation:
            # If not found with user_id, try to get as public simulation
            if user_id is None:
                simulation = simulation_service.get_simulation_by_id(simulation_id)
                if not simulation or not simulation.is_public:
                    return CloudinaryErrorHandler.format_error_response(
                        ErrorCode.FILE_NOT_FOUND,
                        "Simulation not found or not public"
                    ), 404
            else:
                return CloudinaryErrorHandler.format_error_response(
                    ErrorCode.FILE_NOT_FOUND,
                    "Simulation not found"
                ), 404
        
        # Check if user has access (owner or public)
        if user_id and simulation.user_id != user_id and not simulation.is_public:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "Access denied to private simulation"
            ), 403
        
        # Generate view URL (no expiration for HTML viewing)
        view_url = upload_manager.get_download_url(
            simulation.plot_public_id,
            expiration=86400  # 24 hours for HTML viewing
        )
        
        # Return the URL or redirect directly
        view_mode = request.args.get('mode', 'redirect')
        if view_mode == 'url':
            return CloudinaryErrorHandler.format_success_response(
                {
                    "view_url": view_url,
                    "simulation_name": simulation.simulation_name,
                    "plot_title": simulation.plot_title,
                    "expires_in": 86400
                },
                "View URL generated successfully"
            ), 200
        else:
            # Direct redirect to HTML plot
            return redirect(view_url, code=302)
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"View simulation error: {str(e)}")
        return CloudinaryErrorHandler.handle_download_error(str(e)), 500

@simulation_bp.route('/<simulation_id>', methods=['PUT'])
def update_simulation(simulation_id):
    """
    Update simulation metadata
    PUT /api/simulations/{simulation_id}
    
    JSON body can include:
    - simulation_name
    - description
    - tags
    - is_public
    """
    try:
        user_id = get_current_user_id()
        
        # Check if simulation exists and belongs to user
        existing_simulation = simulation_service.get_simulation_by_id(simulation_id, user_id)
        if not existing_simulation:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Simulation not found"
            ), 404
        
        # Get update data
        update_data = request.get_json()
        if not update_data:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "No update data provided"
            ), 400
        
        # Create update object
        simulation_update = SimulationUpdate(**update_data)
        
        # Update simulation
        updated_simulation = simulation_service.update_simulation(simulation_id, user_id, simulation_update)
        if not updated_simulation:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Failed to update simulation"
            ), 500
        
        return CloudinaryErrorHandler.format_success_response(
            updated_simulation.model_dump(),
            "Simulation updated successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Update simulation error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@simulation_bp.route('/<simulation_id>', methods=['DELETE'])
def delete_simulation(simulation_id):
    """
    Delete simulation and cleanup associated files
    DELETE /api/simulations/{simulation_id}
    """
    try:
        user_id = get_current_user_id()
        
        # Get simulation info before deletion
        simulation = simulation_service.get_simulation_by_id(simulation_id, user_id)
        if not simulation:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Simulation not found"
            ), 404
        
        # Delete HTML file from Cloudinary
        html_deleted = upload_manager.delete_file(simulation.plot_public_id)
        if not html_deleted:
            logger.warning(f"Failed to delete Cloudinary HTML file: {simulation.plot_public_id}")
        
        # Delete thumbnail file from Cloudinary if exists
        if simulation.plot_thumbnail_public_id:
            thumbnail_deleted = upload_manager.delete_file(simulation.plot_thumbnail_public_id)
            if not thumbnail_deleted:
                logger.warning(f"Failed to delete Cloudinary thumbnail file: {simulation.plot_thumbnail_public_id}")
        
        # Delete from database
        db_deleted = simulation_service.delete_simulation(simulation_id, user_id)
        if not db_deleted:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Failed to delete simulation from database"
            ), 500
        
        return CloudinaryErrorHandler.format_success_response(
            {"deleted_simulation_id": simulation_id},
            "Simulation deleted successfully"
        ), 200
        
    except ValueError as e:
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.VALIDATION_ERROR,
            str(e)
        ), 400
    except Exception as e:
        logger.error(f"Delete simulation error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

@simulation_bp.route('/public', methods=['GET'])
def list_public_simulations():
    """
    Get paginated list of public simulations
    GET /api/simulations/public?page=1&page_size=10
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
        
        # Get public simulations
        result = simulation_service.get_public_simulations(
            page=page,
            page_size=page_size
        )
        
        return CloudinaryErrorHandler.format_success_response(
            result.model_dump(),
            "Public simulations retrieved successfully"
        ), 200
        
    except Exception as e:
        logger.error(f"List public simulations error: {str(e)}")
        return CloudinaryErrorHandler.handle_generic_error(str(e)), 500

# Error handlers for the blueprint
@simulation_bp.errorhandler(400)
def bad_request(error):
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.VALIDATION_ERROR,
        "Bad request"
    ), 400

@simulation_bp.errorhandler(404)
def not_found(error):
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.FILE_NOT_FOUND,
        "Resource not found"
    ), 404

@simulation_bp.errorhandler(500)
def internal_error(error):
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.INTERNAL_ERROR,
        "Internal server error"
    ), 500