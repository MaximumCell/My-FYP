import os
import tempfile
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from typing import Dict

import importlib.util
from pathlib import Path

# Try package imports first (works when repo root is on sys.path)
try:
    from backend.ai.ocr_processor import ocr_file
    from backend.models.materials import create_material, list_materials_for_user
    # content extractor (for indexing) — optional
    from backend.ai.content_extractor import process_and_index_text
except Exception:
    # Robust file-based fallback: load modules by path so the routes work when
    # running `python app.py` from the backend/ directory (no package context).
    base = Path(__file__).resolve().parent.parent

    # Load ocr_processor.py
    ocr_path = base / 'ai' / 'ocr_processor.py'
    spec = importlib.util.spec_from_file_location('ocr_processor_local', str(ocr_path))
    ocr_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ocr_mod)
    ocr_file = getattr(ocr_mod, 'ocr_file')

    # Load models/materials.py
    mats_path = base / 'models' / 'materials.py'
    spec2 = importlib.util.spec_from_file_location('materials_model_local', str(mats_path))
    mats_mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mats_mod)
    create_material = getattr(mats_mod, 'create_material')
    list_materials_for_user = getattr(mats_mod, 'list_materials_for_user')
    # Try to load content_extractor too (best-effort)
    try:
        ce_path = base / 'ai' / 'content_extractor.py'
        spec3 = importlib.util.spec_from_file_location('content_extractor_local', str(ce_path))
        ce_mod = importlib.util.module_from_spec(spec3)
        spec3.loader.exec_module(ce_mod)
        process_and_index_text = getattr(ce_mod, 'process_and_index_text')
    except Exception:
        process_and_index_text = None

materials_bp = Blueprint('materials_bp', __name__)


ALLOWED_EXT = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.docx', '.pptx'}


def allowed_filename(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXT


@materials_bp.route('/api/materials/upload', methods=['POST'])
def upload_material():
    """Upload a user material, run OCR and save metadata to DB."""
    if 'file' not in request.files:
        current_app.logger.error('Upload failed: No file part in request')
        return jsonify({'success': False, 'error': 'No file part'}), 400

    f = request.files['file']
    if f.filename == '':
        current_app.logger.error('Upload failed: No filename provided')
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    filename = secure_filename(f.filename)
    if not allowed_filename(filename):
        current_app.logger.error(f'Upload failed: Invalid file type - {filename}')
        return jsonify({'success': False, 'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXT)}'}), 400

    user_id = request.headers.get('X-User-ID') or request.form.get('user_id')
    if not user_id:
        current_app.logger.error('Upload failed: Missing user_id')
        return jsonify({'success': False, 'error': 'Missing user id'}), 400
    
    current_app.logger.info(f'Processing upload: {filename} for user {user_id}')

    # Save to temporary file
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, filename)
    f.save(path)

    # Run OCR synchronously (simple pipeline)
    try:
        ocr_result = ocr_file(path)
        processing_status = 'completed'
    except Exception as e:
        current_app.logger.exception('OCR failed')
        ocr_result = {'pages': [], 'text': ''}
        processing_status = 'failed'

    doc: Dict = {
        'user_id': user_id,
        'title': request.form.get('title') or filename,
        'material_type': request.form.get('material_type') or 'unknown',
        'upload_metadata': {
            'file_name': filename,
            'file_path': path,
            'file_type': os.path.splitext(filename)[1].lower(),
            'processing_status': processing_status
        },
        'content': ocr_result.get('text', ''),
        'processed_content': {
            'pages': ocr_result.get('pages', [])
        }
    }

    try:
        inserted_id = create_material(doc)
    except Exception as e:
        current_app.logger.exception('DB insert failed')
        return jsonify({'success': False, 'error': 'DB insert failed'}), 500

    # Fire-and-forget indexing: process OCR text and index chunks in background
    # Use a thread pool to run async indexing without blocking the response
    text_to_index = doc.get('content', '')
    
    if text_to_index and text_to_index.strip():
        try:
            if 'process_and_index_text' in globals() and process_and_index_text:
                import concurrent.futures
                import asyncio
                import threading

                # Prepare material metadata for better search results
                material_metadata = {
                    'title': doc.get('title'),
                    'material_type': doc.get('material_type'),
                    'user_id': user_id,
                    'file_name': filename,
                    'material_id': inserted_id
                }

                def _run_index():
                    """Run indexing in a new event loop in a separate thread"""
                    try:
                        # Create a new event loop for this thread
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        
                        # Run the async function with metadata
                        new_loop.run_until_complete(
                            process_and_index_text(
                                text_to_index, 
                                qdrant_client=None,
                                material_metadata=material_metadata
                            )
                        )
                        
                        new_loop.close()
                        current_app.logger.info(f'✅ Background indexing completed for material {inserted_id}')
                    except Exception as e:
                        current_app.logger.exception(f'❌ Background indexing failed for material {inserted_id}')

                # Submit to thread pool
                executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                executor.submit(_run_index)
                current_app.logger.info(f'🔄 Background indexing started for material {inserted_id}')
            else:
                current_app.logger.warning('⚠️ Content extractor not available - skipping indexing')
        except Exception as e:
            current_app.logger.exception('Failed to start background indexing')
    else:
        current_app.logger.warning(f'⚠️ No text content to index for material {inserted_id}')

    return jsonify({'success': True, 'id': inserted_id, 'processing_status': processing_status}), 201


@materials_bp.route('/api/materials/list', methods=['GET'])
def list_materials():
    user_id = request.headers.get('X-User-ID') or request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Missing user id'}), 400

    try:
        docs = list_materials_for_user(user_id)
        return jsonify({'success': True, 'materials': docs}), 200
    except Exception as e:
        current_app.logger.exception('DB query failed')
        return jsonify({'success': False, 'error': 'DB query failed'}), 500


@materials_bp.route('/api/materials/<material_id>', methods=['GET'])
def get_material(material_id):
    """Get a specific material by ID."""
    user_id = request.headers.get('X-User-ID') or request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Missing user id'}), 400

    try:
        from utils.database import get_database
        from bson.objectid import ObjectId
        
        db = get_database()
        col = db.get_collection('user_materials')
        
        # Find material and verify ownership
        material = col.find_one({'_id': ObjectId(material_id), 'user_id': user_id})
        
        if not material:
            return jsonify({'success': False, 'error': 'Material not found'}), 404
        
        # Convert ObjectId to string
        material['id'] = str(material['_id'])
        del material['_id']
        
        return jsonify({'success': True, 'material': material}), 200
    except Exception as e:
        current_app.logger.exception('Failed to get material')
        return jsonify({'success': False, 'error': str(e)}), 500


@materials_bp.route('/api/materials/<material_id>', methods=['DELETE'])
def delete_material(material_id):
    """Delete a user material by ID."""
    user_id = request.headers.get('X-User-ID') or request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Missing user id'}), 400

    try:
        from utils.database import get_database
        from bson.objectid import ObjectId
        
        db = get_database()
        col = db.get_collection('user_materials')
        
        # Find material and verify ownership
        material = col.find_one({'_id': ObjectId(material_id), 'user_id': user_id})
        
        if not material:
            return jsonify({'success': False, 'error': 'Material not found'}), 404
        
        # Delete the material
        result = col.delete_one({'_id': ObjectId(material_id), 'user_id': user_id})
        
        if result.deleted_count == 0:
            return jsonify({'success': False, 'error': 'Failed to delete material'}), 500
        
        # TODO: Also delete associated chunks from vector DB if needed
        
        return jsonify({'success': True, 'message': 'Material deleted successfully'}), 200
    except Exception as e:
        current_app.logger.exception('Failed to delete material')
        return jsonify({'success': False, 'error': str(e)}), 500


@materials_bp.route('/api/materials/<material_id>/process', methods=['POST'])
def process_material(material_id):
    """Re-process a material for indexing."""
    user_id = request.headers.get('X-User-ID') or request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Missing user id'}), 400

    try:
        from utils.database import get_database
        from bson.objectid import ObjectId
        
        db = get_database()
        col = db.get_collection('user_materials')
        
        # Find material and verify ownership
        material = col.find_one({'_id': ObjectId(material_id), 'user_id': user_id})
        
        if not material:
            return jsonify({'success': False, 'error': 'Material not found'}), 404
        
        # Trigger background processing with new event loop pattern
        text_to_index = material.get('content', '')
        
        if not text_to_index or not text_to_index.strip():
            return jsonify({'success': False, 'error': 'No content to process'}), 400
        
        if process_and_index_text:
            import concurrent.futures
            import asyncio
            
            # Prepare material metadata
            material_metadata = {
                'title': material.get('title'),
                'material_type': material.get('material_type'),
                'user_id': user_id,
                'file_name': material.get('upload_metadata', {}).get('file_name', ''),
                'material_id': material_id
            }
            
            def _run_index():
                try:
                    # Create new event loop for this thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    
                    new_loop.run_until_complete(
                        process_and_index_text(
                            text_to_index, 
                            qdrant_client=None,
                            material_metadata=material_metadata
                        )
                    )
                    
                    new_loop.close()
                    current_app.logger.info(f'✅ Reprocessing completed for material {material_id}')
                    
                    # Update processing status to completed
                    col.update_one(
                        {'_id': ObjectId(material_id)},
                        {'$set': {'upload_metadata.processing_status': 'completed'}}
                    )
                except Exception as e:
                    current_app.logger.exception(f'❌ Reprocessing failed for material {material_id}')
                    # Update processing status to failed
                    col.update_one(
                        {'_id': ObjectId(material_id)},
                        {'$set': {'upload_metadata.processing_status': 'failed'}}
                    )
            
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(_run_index)
            
            return jsonify({'success': True, 'message': 'Processing started', 'material_id': material_id}), 202
        else:
            return jsonify({'success': False, 'error': 'Processing function not available'}), 500
            
    except Exception as e:
        current_app.logger.exception('Failed to process material')
        return jsonify({'success': False, 'error': str(e)}), 500
