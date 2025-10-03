"""
Phase 7.3 Physics AI Routes - Advanced Response Generation
"""
from flask import Blueprint, request, jsonify, current_app
import asyncio
from datetime import datetime
import threading
from functools import wraps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try package imports first
try:
    from backend.ai.enhanced_physics_tutor import EnhancedPhysicsAITutor
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    from pathlib import Path
    backend_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(backend_dir))
    from ai.enhanced_physics_tutor import EnhancedPhysicsAITutor

physics_bp = Blueprint('physics_advanced', __name__, url_prefix='/api/physics')

# Global tutor instance and event loop
tutor_instance = None
event_loop = None
loop_thread = None

def get_or_create_event_loop():
    """Get or create a persistent event loop in a separate thread"""
    global event_loop, loop_thread
    
    if event_loop is None or event_loop.is_closed():
        def run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        event_loop = asyncio.new_event_loop()
        loop_thread = threading.Thread(target=run_loop, args=(event_loop,), daemon=True)
        loop_thread.start()
    
    return event_loop

def run_async(coro):
    """Run an async coroutine using the persistent event loop"""
    loop = get_or_create_event_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=120)  # Increased timeout to 120 seconds

def get_tutor():
    """Get or create tutor instance with Qdrant client"""
    global tutor_instance
    if tutor_instance is None:
        # Import and create Qdrant client
        try:
            import os
            # Try package import first
            try:
                from backend.qdrant_client import create_physics_vector_db
            except ImportError:
                # Fallback for direct execution
                from qdrant_client import create_physics_vector_db
            
            qdrant_url = os.getenv('QDRANT_URL', 'https://my-fyp-hcom.onrender.com')
            qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
            
            # Create Qdrant client for vector search
            qdrant_client = create_physics_vector_db(qdrant_url, qdrant_api_key)
            
            # Initialize tutor with Qdrant client
            tutor_instance = EnhancedPhysicsAITutor(qdrant_client=qdrant_client)
            current_app.logger.info(f"✅ Enhanced Physics Tutor initialized with Qdrant at {qdrant_url}")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not initialize Qdrant client: {e}")
            # Fall back to tutor without Qdrant
            tutor_instance = EnhancedPhysicsAITutor()
    
    return tutor_instance


@physics_bp.route('/ask', methods=['POST'])
def ask_physics_question():
    """
    Phase 7.3: Ask physics question with advanced features
    
    Request JSON:
    {
        "question": str,
        "user_id": str,
        "session_id": str (optional),
        "preferences": {
            "length": "short|medium|long",
            "level": "beginner|intermediate|advanced"
        }
    }
    """
    try:
        data = request.json or {}
        question = data.get('question')
        user_id = data.get('user_id') or request.headers.get('X-User-ID')
        session_id = data.get('session_id') or f"session_{datetime.now().timestamp()}"
        preferences = data.get('preferences', {})
        
        if not question:
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID is required'}), 400
        
        # Get tutor and generate response
        tutor = get_tutor()
        
        # Run async function using persistent event loop
        response = run_async(
            tutor.generate_enhanced_response(
                query=question,
                user_id=user_id,
                session_id=session_id,
                preferences=preferences
            )
        )
        
        return jsonify(response), 200 if response.get('success') else 500
        
    except Exception as e:
        current_app.logger.exception('Physics question error')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@physics_bp.route('/quick-ask', methods=['POST'])
def quick_ask():
    """
    Quick physics question without advanced features (faster)
    
    Request JSON:
    {
        "question": str,
        "length": "short|medium|long" (optional)
    }
    """
    try:
        data = request.json or {}
        question = data.get('question')
        response_length = data.get('length', 'medium')
        user_id = data.get('user_id') or request.headers.get('X-User-ID')
        
        if not question:
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        tutor = get_tutor()
        
        # Simple response without all enhancements
        response = run_async(
            tutor.ask_physics_question(
                question=question,
                response_length=response_length,
                use_rag=True,
                max_context_items=3,
                user_id=user_id
            )
        )
        
        return jsonify(response), 200 if response.get('success') else 500
        
    except Exception as e:
        current_app.logger.exception('Quick ask error')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@physics_bp.route('/derivation', methods=['POST'])
def request_derivation():
    """
    Request step-by-step derivation
    
    Request JSON:
    {
        "concept": str,
        "user_id": str,
        "level": "beginner|intermediate|advanced" (optional)
    }
    """
    try:
        data = request.json or {}
        concept = data.get('concept')
        user_id = data.get('user_id') or request.headers.get('X-User-ID')
        level = data.get('level', 'intermediate')
        
        if not concept:
            return jsonify({'success': False, 'error': 'Concept is required'}), 400
        
        # Formulate derivation query
        derivation_query = f"Derive {concept} step by step"
        
        tutor = get_tutor()
        
        response = run_async(
            tutor.generate_enhanced_response(
                query=derivation_query,
                user_id=user_id or 'anonymous',
                session_id=f"deriv_{datetime.now().timestamp()}",
                preferences={'length': 'long', 'level': level}
            )
        )
        
        return jsonify(response), 200 if response.get('success') else 500
        
    except Exception as e:
        current_app.logger.exception('Derivation error')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@physics_bp.route('/explain', methods=['POST'])
def explain_concept():
    """
    Explain physics concept at different levels
    
    Request JSON:
    {
        "concept": str,
        "level": "beginner|intermediate|advanced"
    }
    """
    try:
        data = request.json or {}
        concept = data.get('concept')
        level = data.get('level', 'intermediate')
        
        if not concept:
            return jsonify({'success': False, 'error': 'Concept is required'}), 400
        
        query = f"Explain {concept}"
        tutor = get_tutor()
        
        response = run_async(
            tutor.generate_enhanced_response(
                query=query,
                user_id='anonymous',
                session_id=f"explain_{datetime.now().timestamp()}",
                preferences={'length': 'medium', 'level': level}
            )
        )
        
        return jsonify(response), 200 if response.get('success') else 500
        
    except Exception as e:
        current_app.logger.exception('Explain concept error')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@physics_bp.route('/stats', methods=['GET'])
def get_tutor_stats():
    """Get physics tutor statistics"""
    try:
        tutor = get_tutor()
        stats = tutor.get_enhanced_stats()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@physics_bp.route('/generate-diagram', methods=['POST'])
def generate_diagram():
    """
    Generate physics diagrams using AI
    
    Request JSON:
    {
        "description": str (required) - What to draw
        "diagram_type": str (optional) - force, circuit, wave, energy, motion, field, vector, graph, general
        "style": str (optional) - educational, technical, sketch, colorful, minimal
        "include_labels": bool (optional) - Whether to include labels
        "session_id": str (optional) - For conversation context
    }
    
    Response:
    {
        "success": bool,
        "image_base64": str - Base64 encoded image,
        "image_url": str - URL to access image,
        "explanation": str - Text explanation of the diagram,
        "diagram_type": str,
        "style": str,
        "timestamp": str
    }
    """
    try:
        data = request.json or {}
        description = data.get('description')
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'Description is required'
            }), 400
        
        diagram_type = data.get('diagram_type', 'general')
        style = data.get('style', 'educational')
        include_labels = data.get('include_labels', True)
        session_id = data.get('session_id')
        
        tutor = get_tutor()
        
        # Run async diagram generation
        response = run_async(
            tutor.generate_physics_diagram(
                description=description,
                diagram_type=diagram_type,
                style=style,
                include_labels=include_labels,
                session_id=session_id
            )
        )
        
        return jsonify(response), 200 if response.get('success') else 500
        
    except Exception as e:
        current_app.logger.exception('Diagram generation error')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
