"""
Phase 7.3 Physics AI Routes - Advanced Response Generation
"""
from flask import Blueprint, request, jsonify, current_app
import asyncio
from datetime import datetime

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

# Global tutor instance
tutor_instance = None

def get_tutor():
    """Get or create tutor instance"""
    global tutor_instance
    if tutor_instance is None:
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
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                tutor.generate_enhanced_response(
                    query=question,
                    user_id=user_id,
                    session_id=session_id,
                    preferences=preferences
                )
            )
        finally:
            loop.close()
        
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
        
        if not question:
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        tutor = get_tutor()
        
        # Simple response without all enhancements
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                tutor.ask_physics_question(
                    question=question,
                    response_length=response_length,
                    use_rag=True,
                    max_context_items=3
                )
            )
        finally:
            loop.close()
        
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
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                tutor.generate_enhanced_response(
                    query=derivation_query,
                    user_id=user_id or 'anonymous',
                    session_id=f"deriv_{datetime.now().timestamp()}",
                    preferences={'length': 'long', 'level': level}
                )
            )
        finally:
            loop.close()
        
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
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                tutor.generate_enhanced_response(
                    query=query,
                    user_id='anonymous',
                    session_id=f"explain_{datetime.now().timestamp()}",
                    preferences={'length': 'medium', 'level': level}
                )
            )
        finally:
            loop.close()
        
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
