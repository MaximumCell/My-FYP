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


ALLOWED_EXT = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff'}


def allowed_filename(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXT


@materials_bp.route('/api/materials/upload', methods=['POST'])
def upload_material():
    """Upload a user material, run OCR and save metadata to DB."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    filename = secure_filename(f.filename)
    if not allowed_filename(filename):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400

    user_id = request.headers.get('X-User-ID') or request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Missing user id'}), 400

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
    try:
        # Only attempt background indexing if function is available
        if 'process_and_index_text' in globals() and process_and_index_text:
            import concurrent.futures
            import asyncio

            text_to_index = doc.get('content', '')
            # Note: we don't await this; run in executor to avoid blocking HTTP response
            loop = asyncio.get_event_loop()

            def _run_index():
                try:
                    asyncio.run(process_and_index_text(text_to_index, qdrant_client=None))
                except Exception:
                    current_app.logger.exception('Background indexing failed')

            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(_run_index)

    except Exception:
        current_app.logger.exception('Failed to start background indexing')

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
        
        # Trigger background processing
        if process_and_index_text:
            import concurrent.futures
            import asyncio
            
            text_to_index = material.get('content', '')
            
            def _run_index():
                try:
                    asyncio.run(process_and_index_text(text_to_index, qdrant_client=None))
                    # Update processing status
                    col.update_one(
                        {'_id': ObjectId(material_id)},
                        {'$set': {'upload_metadata.processing_status': 'completed'}}
                    )
                except Exception:
                    current_app.logger.exception('Background indexing failed')
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
