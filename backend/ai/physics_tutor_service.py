"""
Physics Tutor Service
Main service that orchestrates AI responses, quality evaluation, and learning management
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ai.physics_ai import physics_ai
from ai.latex_renderer import latex_renderer
from models.physics_knowledge import physics_knowledge_db
from models.response_evaluation import response_evaluation_db, ResponseEvaluation, UserQuery, AIResponse, SupervisorEvaluation, EvaluationMetadata, EvaluationCriteria, DetailedFeedback
from models.physics_chat_session import physics_chat_session_db, PhysicsChatSession, ConversationMessage, LearningContext, MessageMetadata


class PhysicsTutorService:
    def __init__(self):
        self.ai = physics_ai
        self.latex_renderer = latex_renderer
        self.knowledge_db = physics_knowledge_db
        self.evaluation_db = response_evaluation_db
        self.chat_session_db = physics_chat_session_db
        
        # Quality thresholds from environment
        import os
        self.quality_min = float(os.getenv('QUALITY_THRESHOLD_MIN', 5.0))
        self.quality_high = float(os.getenv('QUALITY_THRESHOLD_HIGH', 8.0))
        self.evaluation_timeout = int(os.getenv('EVALUATION_TIMEOUT', 10))
        self.supervisor_enabled = os.getenv('ENABLE_AI_SUPERVISOR', 'true').lower() == 'true'
    
    async def create_chat_session(self, user_id: str, learning_context: Dict = None) -> Dict:
        """Create new physics learning chat session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create learning context
            context = LearningContext()
            if learning_context:
                context.difficulty_preference = learning_context.get('difficulty_preference', 'intermediate')
                context.response_length_preference = learning_context.get('response_length_preference', 'long')
                context.preferred_books = learning_context.get('preferred_books', [])
                context.learning_goals = learning_context.get('learning_goals', [])
            
            # Create chat session
            session = PhysicsChatSession(
                user_id=user_id,
                session_id=session_id,
                learning_context=context
            )
            
            # Save to database
            session_doc_id = self.chat_session_db.create_session(session)
            
            if session_doc_id:
                return {
                    'success': True,
                    'session_id': session_id,
                    'learning_context': context.dict(),
                    'message': 'Physics learning session created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create chat session',
                    'message': 'Database error occurred'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error creating chat session'
            }
    
    async def process_physics_question(self, 
                                     session_id: str,
                                     user_question: str,
                                     response_length: str = None,
                                     sources: List[str] = None) -> Dict:
        """Process physics question with AI response generation and quality evaluation"""
        start_time = time.time()
        
        try:
            # Get chat session
            session = self.chat_session_db.get_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found',
                    'message': 'Invalid session ID'
                }
            
            user_id = session['user_id']
            learning_context = session.get('learning_context', {})
            
            # Use session preference if response_length not specified
            if not response_length:
                response_length = learning_context.get('response_length_preference', 'long')
            
            # Step 1: Classify the question
            question_classification = await self.ai.classify_question(user_question)
            
            # Step 2: Generate AI response
            context = {
                'preferred_books': learning_context.get('preferred_books', []),
                'difficulty_level': learning_context.get('difficulty_preference', 'intermediate'),
                'current_topic': learning_context.get('current_topic')
            }
            
            ai_response = await self.ai.generate_response(
                user_question, 
                context=context,
                response_length=response_length,
                sources=sources
            )
            
            if 'error' in ai_response:
                return {
                    'success': False,
                    'error': ai_response['error'],
                    'message': 'AI response generation failed'
                }
            
            # Step 3: Process LaTeX equations in response
            equation_processing = self.latex_renderer.process_response_equations(
                ai_response['content']
            )
            
            # Step 4: Parallel AI supervisor evaluation (if enabled)
            evaluation_result = None
            if self.supervisor_enabled:
                try:
                    # Run evaluation with timeout
                    evaluation_task = asyncio.create_task(
                        self.ai.evaluate_response(
                            user_question, 
                            ai_response['content'], 
                            context
                        )
                    )
                    evaluation_result = await asyncio.wait_for(
                        evaluation_task, 
                        timeout=self.evaluation_timeout
                    )
                except asyncio.TimeoutError:
                    evaluation_result = {
                        'overall_score': 6.0,  # Default acceptable score
                        'evaluation_model': 'timeout',
                        'supervisor_confidence': 0.0,
                        'timeout': True
                    }
                except Exception as e:
                    evaluation_result = {
                        'overall_score': 6.0,
                        'evaluation_model': 'error',
                        'supervisor_confidence': 0.0,
                        'error': str(e)
                    }
            
            # Step 5: Determine delivery decision
            delivery_decision = {'action': 'deliver_immediately', 'confidence': 'high'}
            if evaluation_result:
                overall_score = evaluation_result.get('overall_score', 6.0)
                delivery_decision = self.ai.get_delivery_decision(overall_score)
            
            # Step 6: Create message metadata
            message_metadata = MessageMetadata(
                question_type=question_classification.get('category'),
                sources_used=sources or [],
                confidence_level=evaluation_result.get('supervisor_confidence') if evaluation_result else None,
                visual_aids_generated=[eq['original'] for eq in equation_processing.get('equations', []) if eq.get('success')],
                response_length=response_length,
                book_reference_used=learning_context.get('preferred_books', [None])[0] if learning_context.get('preferred_books') else None
            )
            
            # Step 7: Add messages to conversation history
            message_id = str(uuid.uuid4())
            
            # User message
            user_message = ConversationMessage(
                role='user',
                content=user_question,
                message_metadata=MessageMetadata()
            )
            
            # AI response message
            ai_message = ConversationMessage(
                role='assistant',
                content=ai_response['content'],
                message_metadata=message_metadata
            )
            
            # Add messages to session
            self.chat_session_db.add_message(session_id, user_message)
            self.chat_session_db.add_message(session_id, ai_message)
            
            # Step 8: Save evaluation to database (if supervisor enabled)
            if evaluation_result and self.supervisor_enabled:
                try:
                    # Create evaluation record
                    user_query_obj = UserQuery(
                        original_question=user_question,
                        question_type=question_classification.get('category', 'concept'),
                        difficulty_level=learning_context.get('difficulty_preference', 'intermediate'),
                        topic=question_classification.get('topic', 'general')
                    )
                    
                    ai_response_obj = AIResponse(
                        response_content=ai_response['content'],
                        sources_used=sources or [],
                        response_length=response_length,
                        visual_aids_included=message_metadata.visual_aids_generated
                    )
                    
                    # Create evaluation criteria from result
                    criteria = evaluation_result.get('evaluation_criteria', {})
                    evaluation_criteria = EvaluationCriteria(
                        physics_accuracy=criteria.get('physics_accuracy', 7),
                        mathematical_correctness=criteria.get('mathematical_correctness', 7),
                        explanation_clarity=criteria.get('explanation_clarity', 7),
                        completeness=criteria.get('completeness', 7),
                        educational_value=criteria.get('educational_value', 7),
                        source_relevance=criteria.get('source_relevance', 6),
                        step_by_step_quality=criteria.get('step_by_step_quality', 7)
                    )
                    
                    # Create detailed feedback
                    feedback_data = evaluation_result.get('detailed_feedback', {})
                    detailed_feedback = DetailedFeedback(
                        strengths=feedback_data.get('strengths', []),
                        weaknesses=feedback_data.get('weaknesses', []),
                        missing_elements=feedback_data.get('missing_elements', []),
                        accuracy_issues=feedback_data.get('accuracy_issues', []),
                        improvement_suggestions=feedback_data.get('improvement_suggestions', [])
                    )
                    
                    supervisor_eval = SupervisorEvaluation(
                        overall_score=evaluation_result['overall_score'],
                        evaluation_criteria=evaluation_criteria,
                        detailed_feedback=detailed_feedback,
                        supervisor_confidence=evaluation_result.get('supervisor_confidence', 0.8),
                        evaluation_model=evaluation_result.get('evaluation_model', 'gemini-pro'),
                        alternative_response_suggested=False
                    )
                    
                    eval_metadata = EvaluationMetadata(
                        evaluation_time=time.time() - start_time,
                        response_improvement_needed=evaluation_result['overall_score'] < self.quality_min,
                        flagged_for_review=evaluation_result['overall_score'] < 4.0
                    )
                    
                    evaluation = ResponseEvaluation(
                        user_id=user_id,
                        session_id=session_id,
                        message_id=message_id,
                        user_query=user_query_obj,
                        ai_response=ai_response_obj,
                        supervisor_evaluation=supervisor_eval,
                        evaluation_metadata=eval_metadata
                    )
                    
                    # Save evaluation
                    self.evaluation_db.insert_evaluation(evaluation)
                    
                except Exception as e:
                    print(f"Error saving evaluation: {e}")
            
            # Step 9: Prepare response
            processing_time = time.time() - start_time
            
            response_data = {
                'success': True,
                'message_id': message_id,
                'response': ai_response['content'],
                'question_classification': question_classification,
                'equations': equation_processing.get('equations', []),
                'delivery_decision': delivery_decision,
                'processing_time': processing_time,
                'response_length': response_length
            }
            
            # Add quality information if supervisor enabled
            if evaluation_result:
                response_data['quality_score'] = evaluation_result['overall_score']
                response_data['evaluation_summary'] = {
                    'confidence': evaluation_result.get('supervisor_confidence'),
                    'model': evaluation_result.get('evaluation_model'),
                    'flagged': evaluation_result.get('overall_score', 10) < 4.0
                }
            
            return response_data
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error processing physics question',
                'processing_time': time.time() - start_time
            }
    
    async def regenerate_response(self, session_id: str, message_id: str, 
                                new_length: str = None) -> Dict:
        """Regenerate AI response with different parameters"""
        try:
            # Get conversation history
            history = self.chat_session_db.get_conversation_history(session_id)
            
            # Find the user question for the given message
            user_question = None
            for i, msg in enumerate(history):
                if msg['role'] == 'assistant' and i > 0:
                    user_question = history[i-1]['content']
                    break
            
            if not user_question:
                return {
                    'success': False,
                    'error': 'Original question not found',
                    'message': 'Cannot regenerate without original question'
                }
            
            # Process with new parameters
            return await self.process_physics_question(
                session_id, 
                user_question, 
                response_length=new_length
            )
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error regenerating response'
            }
    
    def get_session_analytics(self, session_id: str) -> Dict:
        """Get learning analytics for a session"""
        try:
            session = self.chat_session_db.get_session(session_id)
            if not session:
                return {'success': False, 'error': 'Session not found'}
            
            # Get evaluations for this session
            evaluations = self.evaluation_db.get_session_evaluations(session_id)
            
            # Calculate analytics
            total_interactions = len(session.get('conversation_history', [])) // 2  # User + AI pairs
            avg_quality = sum(eval.get('supervisor_evaluation', {}).get('overall_score', 0) 
                            for eval in evaluations) / max(len(evaluations), 1)
            
            topics_discussed = list(set([
                eval.get('user_query', {}).get('topic', 'general') 
                for eval in evaluations
            ]))
            
            return {
                'success': True,
                'session_id': session_id,
                'analytics': {
                    'total_interactions': total_interactions,
                    'average_quality_score': avg_quality,
                    'topics_discussed': topics_discussed,
                    'session_duration': session.get('updated_at', session.get('created_at')),
                    'learning_context': session.get('learning_context', {})
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error getting session analytics'
            }


# Initialize physics tutor service
physics_tutor_service = PhysicsTutorService()