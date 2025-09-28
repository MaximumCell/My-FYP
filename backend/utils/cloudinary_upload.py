"""
Cloudinary File Upload Manager with Retry Logic
Handles file uploads to Cloudinary with proper error handling, retry mechanisms and folder structure
"""

import os
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any, Union, BinaryIO, List
import logging
from .cloudinary_config import CloudinaryConfig, ALLOWED_FILE_TYPES, MAX_FILE_SIZE
from .retry_mechanisms import retry_cloudinary_operation, cloudinary_circuit_breaker
import tempfile
import time

logger = logging.getLogger(__name__)


class CloudinaryUploadError(Exception):
    """Custom exception for Cloudinary upload errors"""
    pass


class CloudinaryUploadManager:
    """Manages file uploads to Cloudinary with proper organization"""
    
    def __init__(self):
        self.config = CloudinaryConfig()
    
    @retry_cloudinary_operation(max_attempts=3)
    @cloudinary_circuit_breaker
    def upload_model_file(
        self, 
        file_data: Union[bytes, BinaryIO], 
        filename: str, 
        user_id: str,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Upload ML model file (.pkl) to Cloudinary with retry logic
        
        Args:
            file_data: File data (bytes or file-like object)
            filename: Original filename
            user_id: User's unique identifier
            model_name: User-friendly model name
            
        Returns:
            Dictionary containing upload results and metadata
        """
        temp_file_path = None
        
        try:
            # Validate file
            if isinstance(file_data, bytes):
                file_bytes = file_data
            else:
                file_bytes = file_data.read()
                
            is_valid, error_msg = self.config.validate_file(
                file_bytes, filename, ALLOWED_FILE_TYPES['models']
            )
            
            if not is_valid:
                raise CloudinaryUploadError(error_msg)
            
            # Generate public_id using model_name instead of filename
            public_id = self.config.generate_public_id(user_id, model_name + '.pkl', 'models')
            
            # Create temporary file for upload
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name
            
            # Upload to Cloudinary with enhanced configuration
            upload_result = cloudinary.uploader.upload(
                temp_file_path,
                public_id=public_id,
                resource_type="raw",  # For non-image files
                overwrite=False,  # Don't overwrite existing files
                use_filename=False,  # Use our generated public_id
                tags=["model", f"user_{user_id}", "pkl"],
                timeout=60,  # 60 second timeout
                chunk_size=6000000,  # 6MB chunks for large files
                eager_async=False  # Wait for upload to complete
            )
            
            logger.info(f"Model uploaded successfully: {public_id}")
            
            return {
                'success': True,
                'public_id': upload_result['public_id'],
                'secure_url': upload_result['secure_url'],
                'file_size': upload_result['bytes'],
                'resource_type': upload_result['resource_type'],
                'created_at': upload_result['created_at'],
                'version': upload_result['version'],
                'format': upload_result.get('format', 'pkl'),
                'tags': upload_result.get('tags', [])
            }
                
        except CloudinaryUploadError:
            raise
        except Exception as e:
            logger.error(f"Model upload failed: {str(e)}")
            raise CloudinaryUploadError(f"Upload failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {temp_file_path}: {str(e)}")
    
    @retry_cloudinary_operation(max_attempts=3)
    @cloudinary_circuit_breaker
    def upload_simulation_file(
        self, 
        file_data: Union[bytes, str], 
        filename: str, 
        user_id: str,
        simulation_name: str,
        file_type: str = 'html'
    ) -> Dict[str, Any]:
        """
        Upload simulation file (.html or .png) to Cloudinary with retry logic
        
        Args:
            file_data: File data (bytes for binary files, str for HTML)
            filename: Original filename  
            user_id: User's unique identifier
            simulation_name: User-friendly simulation name
            file_type: Type of file ('html' or 'png')
            
        Returns:
            Dictionary containing upload results and metadata
        """
        temp_file_path = None
        
        try:
            # Convert string to bytes if needed (for HTML content)
            if isinstance(file_data, str):
                file_bytes = file_data.encode('utf-8')
            else:
                file_bytes = file_data
            
            # Validate file
            is_valid, error_msg = self.config.validate_file(
                file_bytes, filename, ALLOWED_FILE_TYPES['simulations']
            )
            
            if not is_valid:
                raise CloudinaryUploadError(error_msg)
            
            # Generate public_id using simulation_name instead of filename
            file_extension = f'.{file_type}'
            public_id = self.config.generate_public_id(
                user_id, simulation_name + file_extension, 'simulations'
            )
            
            # Determine resource type and upload parameters
            if file_type == 'html':
                resource_type = "raw"
                file_suffix = '.html'
            else:  # png
                resource_type = "image"
                file_suffix = '.png'
            
            # Create temporary file for upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name
            
            # Upload to Cloudinary with enhanced configuration
            upload_result = cloudinary.uploader.upload(
                temp_file_path,
                public_id=public_id,
                resource_type=resource_type,
                overwrite=False,
                use_filename=False,
                tags=["simulation", f"user_{user_id}", file_type],
                timeout=60,  # 60 second timeout
                chunk_size=6000000,  # 6MB chunks for large files
                eager_async=False  # Wait for upload to complete
            )
            
            logger.info(f"Simulation uploaded successfully: {public_id}")
            
            return {
                'success': True,
                'public_id': upload_result['public_id'],
                'secure_url': upload_result['secure_url'],
                'file_size': upload_result['bytes'],
                'resource_type': upload_result['resource_type'],
                'created_at': upload_result['created_at'],
                'version': upload_result['version'],
                'format': upload_result.get('format', file_type),
                'tags': upload_result.get('tags', [])
            }
                
        except CloudinaryUploadError:
            raise
        except Exception as e:
            logger.error(f"Simulation upload failed: {str(e)}")
            raise CloudinaryUploadError(f"Upload failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {temp_file_path}: {str(e)}")
    
    def get_download_url(self, public_id: str, expiration: int = 3600) -> str:
        """
        Generate a secure download URL for a file
        
        Args:
            public_id: Cloudinary public_id of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Secure download URL
        """
        try:
            # Determine resource type from public_id
            resource_type = "raw"  # Default for models and HTML files
            if '/simulations/' in public_id and not public_id.endswith('_html'):
                # Check if it's a PNG simulation
                try:
                    # Try to get resource info to determine actual resource type
                    info = cloudinary.api.resource(public_id, resource_type="image")
                    resource_type = "image"
                except:
                    resource_type = "raw"
            
            # Generate signed URL for secure download
            url = cloudinary.utils.cloudinary_url(
                public_id,
                resource_type=resource_type,
                type="upload",
                sign_url=True,
                expires_at=int(time.time()) + expiration
            )[0]
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate download URL: {str(e)}")
            raise CloudinaryUploadError(f"Failed to generate download URL: {str(e)}")
    
    def delete_file(self, public_id: str) -> bool:
        """
        Delete a file from Cloudinary
        
        Args:
            public_id: Cloudinary public_id of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try both resource types since we can't always determine from public_id
            for resource_type in ["raw", "image"]:
                try:
                    result = cloudinary.uploader.destroy(
                        public_id,
                        resource_type=resource_type
                    )
                    
                    if result.get('result') == 'ok':
                        logger.info(f"File deleted successfully: {public_id} (resource_type: {resource_type})")
                        return True
                    elif result.get('result') == 'not found':
                        # Try the other resource type
                        continue
                    else:
                        logger.warning(f"File deletion failed: {public_id}, result: {result}")
                        return False
                        
                except Exception as e:
                    logger.debug(f"Delete attempt failed for {resource_type}: {str(e)}")
                    continue
            
            logger.warning(f"File not found in any resource type: {public_id}")
            return False
            
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return False
    
    def get_file_info(self, public_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file information from Cloudinary
        
        Args:
            public_id: Cloudinary public_id of the file
            
        Returns:
            File information dictionary or None if not found
        """
        try:
            # Try different resource types
            for resource_type in ["raw", "image"]:
                try:
                    result = cloudinary.api.resource(
                        public_id,
                        resource_type=resource_type
                    )
                    
                    return {
                        'public_id': result['public_id'],
                        'secure_url': result['secure_url'],
                        'file_size': result['bytes'],
                        'resource_type': result['resource_type'],
                        'created_at': result['created_at'],
                        'format': result.get('format'),
                        'tags': result.get('tags', []),
                        'version': result['version']
                    }
                    
                except cloudinary.exceptions.NotFound:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Failed to get file info: {str(e)}")
            return None
    
    def list_user_files(self, user_id: str, file_type: str = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        List files for a specific user
        
        Args:
            user_id: User's unique identifier
            file_type: Filter by file type ('models' or 'simulations'), None for all
            max_results: Maximum number of results to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            files = []
            
            # Define search prefixes based on file_type
            if file_type == 'models':
                prefixes = [f"physics-lab/models/user_{user_id}/"]
            elif file_type == 'simulations':
                prefixes = [f"physics-lab/simulations/user_{user_id}/"]
            else:
                prefixes = [
                    f"physics-lab/models/user_{user_id}/",
                    f"physics-lab/simulations/user_{user_id}/"
                ]
            
            for prefix in prefixes:
                try:
                    # Search for raw files (models and HTML simulations)
                    raw_results = cloudinary.api.resources(
                        type="upload",
                        resource_type="raw",
                        prefix=prefix,
                        max_results=max_results
                    )
                    
                    for resource in raw_results.get('resources', []):
                        files.append({
                            'public_id': resource['public_id'],
                            'secure_url': resource['secure_url'],
                            'file_size': resource['bytes'],
                            'resource_type': resource['resource_type'],
                            'created_at': resource['created_at'],
                            'format': resource.get('format'),
                            'tags': resource.get('tags', []),
                            'version': resource['version']
                        })
                    
                    # Search for image files (PNG simulations)
                    if file_type != 'models':  # Models are only raw files
                        image_results = cloudinary.api.resources(
                            type="upload",
                            resource_type="image",
                            prefix=prefix,
                            max_results=max_results
                        )
                        
                        for resource in image_results.get('resources', []):
                            files.append({
                                'public_id': resource['public_id'],
                                'secure_url': resource['secure_url'],
                                'file_size': resource['bytes'],
                                'resource_type': resource['resource_type'],
                                'created_at': resource['created_at'],
                                'format': resource.get('format'),
                                'tags': resource.get('tags', []),
                                'version': resource['version']
                            })
                            
                except cloudinary.exceptions.NotFound:
                    continue
                except Exception as e:
                    logger.warning(f"Error searching prefix {prefix}: {str(e)}")
                    continue
            
            # Sort by creation date (newest first) and limit results
            files.sort(key=lambda x: x['created_at'], reverse=True)
            return files[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to list user files: {str(e)}")
            return []


# Utility functions for easy access
upload_manager = CloudinaryUploadManager()

def upload_model(file_data, filename, user_id, model_name):
    """Convenience function to upload a model file"""
    return upload_manager.upload_model_file(file_data, filename, user_id, model_name)

def upload_simulation(file_data, filename, user_id, simulation_name, file_type='html'):
    """Convenience function to upload a simulation file"""
    return upload_manager.upload_simulation_file(file_data, filename, user_id, simulation_name, file_type)

def get_download_url(public_id, expiration=3600):
    """Convenience function to get download URL"""
    return upload_manager.get_download_url(public_id, expiration)

def delete_file(public_id):
    """Convenience function to delete a file"""
    return upload_manager.delete_file(public_id)