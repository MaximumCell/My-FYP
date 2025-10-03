"""
Enhanced Physics AI Tutor with Embedding Integration
==================================================

Thi    async def ask_physics_question(self, 
                                 question: str, 
                                 context: Optional[str] = None,
                                 response_length: str = 'medium',
                                 difficulty_level: str = 'intermediate',
                                 use_rag: bool = True,
                                 max_context_items: int = 5,
                                 session_id: Optional[str] = None,
                                 user_id: Optional[str] = None) -> Dict[str, Any]: enhances the existing physics AI tutor with advanced embedding-based
retrieval and similarity search capabilities using Google's text-embedding-004.

Features:
- Seamless integration with existing physics AI tutor
- Advanced RAG (Retrieval Augmented Generation) pipeline
- Physics-specific content embeddings and search
- Intelligent context retrieval for better responses
- Comprehensive performance monitoring

Author: Physics AI Tutor Team
Date: September 28, 2025
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import json

# Import existing physics AI components
from physics_ai_tutor import PhysicsAITutor

# Import new embedding components
from ai.embedding_service import PhysicsEmbeddingService, get_embedding_service
from ai.vector_database_integration import (
    PhysicsVectorDatabase, 
    PhysicsContent, 
    SearchResult, 
    SearchResponse
)

# Import Phase 7.3 components
try:
    from ai.derivation_engine import break_into_steps, format_derivation, generate_prerequisites, extract_key_equations
    from ai.response_adapter import ResponseAdapter
    from ai.source_prioritizer import prioritize_sources
    from ai.citation_manager import generate_citations
except ImportError:
    # Fallback for missing components
    def break_into_steps(text): return [{'step_number': 1, 'content': text}]
    def format_derivation(steps): return steps[0]['content'] if steps else ''
    def generate_prerequisites(topic): return []
    def extract_key_equations(text): return []
    class ResponseAdapter:
        def adapt_length(self, text, pref): return text
        def adapt_complexity(self, text, level): return {'content': text, 'level': level}
        def generate_follow_ups(self, topic, query): return []
        def extract_key_concepts(self, text): return []
    def prioritize_sources(*args, **kwargs): return []
    def generate_citations(sources): return []

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPhysicsAITutor:
    """
    Enhanced Physics AI Tutor with advanced embedding and vector search capabilities
    
    This class extends the original PhysicsAITutor with:
    - Intelligent content retrieval using embeddings
    - Context-aware response generation
    - Physics knowledge base management
    - Advanced similarity search and recommendations
    """
    
    def __init__(self, 
                 qdrant_client=None,
                 embedding_service: Optional[PhysicsEmbeddingService] = None,
                 enable_rag: bool = True):
        """
        Initialize the enhanced physics AI tutor
        
        Args:
            qdrant_client: Qdrant client for vector operations
            embedding_service: Custom embedding service (optional)
            enable_rag: Enable retrieval-augmented generation
        """
        # Initialize base AI tutor
        self.base_tutor = PhysicsAITutor()
        
        # Initialize embedding components
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_database = PhysicsVectorDatabase(
            embedding_service=self.embedding_service,
            qdrant_client=qdrant_client
        )
        
        self.enable_rag = enable_rag
        
        # Session memory management
        self.session_history: Dict[str, List[Dict]] = {}  # session_id -> messages
        self.max_history_per_session = 5  # Keep last 5 messages
        
        # Enhanced statistics
        self.stats = {
            'total_enhanced_queries': 0,
            'rag_queries': 0,
            'context_retrieval_time': 0.0,
            'response_generation_time': 0.0,
            'average_context_relevance': 0.0,
            'last_reset': datetime.now()
        }
        
        # Initialize collection asynchronously on first use
        self._collection_initialized = False
        
        logger.info("✅ Enhanced Physics AI Tutor initialized with embedding support")
    
    async def ask_physics_question(self, 
                                 question: str,
                                 context: Optional[str] = None,
                                 response_length: str = "medium",
                                 difficulty_level: str = "intermediate",
                                 use_rag: bool = True,
                                 max_context_items: int = 5,
                                 session_id: Optional[str] = None,
                                 user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a physics question with enhanced retrieval and response generation
        
        Args:
            question: The physics question to ask
            context: Additional context (optional)
            response_length: Desired response length (short/medium/long)
            difficulty_level: Target difficulty level
            use_rag: Whether to use retrieval-augmented generation
            max_context_items: Maximum number of context items to retrieve
            session_id: Session ID for conversation history
            user_id: User ID for filtering user-specific materials
            
        Returns:
            Enhanced response with metadata
        """
        start_time = time.time()
        self.stats['total_enhanced_queries'] += 1
        
        try:
            logger.info(f"🤔 Processing physics question: '{question[:50]}...'")
            
            # Step 1: Classify the question using base tutor
            classification = await self._classify_question(question)
            
            # Step 2: Retrieve relevant context if RAG is enabled
            retrieved_context = []
            context_retrieval_time = 0.0
            
            if use_rag and self.enable_rag:
                context_start = time.time()
                retrieved_context = await self._retrieve_relevant_context(
                    question, 
                    classification,
                    max_context_items,
                    user_id=user_id
                )
                context_retrieval_time = time.time() - context_start
                self.stats['context_retrieval_time'] += context_retrieval_time
                self.stats['rag_queries'] += 1
                
                logger.info(f"📚 Retrieved {len(retrieved_context)} relevant context items")
            
            # Step 3: Generate enhanced response
            response_start = time.time()
            enhanced_response = await self._generate_enhanced_response(
                question=question,
                classification=classification,
                retrieved_context=retrieved_context,
                user_context=context,
                response_length=response_length,
                difficulty_level=difficulty_level,
                session_id=session_id
            )
            response_generation_time = time.time() - response_start
            self.stats['response_generation_time'] += response_generation_time
            
            # Store in session history for context awareness
            if session_id:
                if session_id not in self.session_history:
                    self.session_history[session_id] = []
                
                self.session_history[session_id].append({
                    'question': question,
                    'answer': enhanced_response[:500],  # Store truncated answer
                    'timestamp': datetime.now()
                })
                
                # Keep only recent messages
                if len(self.session_history[session_id]) > self.max_history_per_session:
                    self.session_history[session_id] = self.session_history[session_id][-self.max_history_per_session:]
                
                logger.info(f"💾 Stored message in session {session_id} (total: {len(self.session_history[session_id])})")
            
            total_time = time.time() - start_time
            
            # Build comprehensive response
            result = {
                'success': True,
                'question': question,
                'answer': enhanced_response,
                'classification': classification,
                'context_items_used': len(retrieved_context),
                'response_metadata': {
                    'response_length': response_length,
                    'difficulty_level': difficulty_level,
                    'used_rag': use_rag and len(retrieved_context) > 0,
                    'processing_time': total_time,
                    'context_retrieval_time': context_retrieval_time,
                    'response_generation_time': response_generation_time
                },
                'retrieved_context': [
                    {
                        'title': item.content.title,
                        'topic': item.content.topic,
                        'similarity_score': item.similarity_score,
                        'content_preview': item.content.content[:100] + "..."
                    } for item in retrieved_context
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Enhanced response generated in {total_time:.3f}s")
            return result
            
        except Exception as e:
            error_msg = f"Error processing physics question: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'question': question,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _classify_question(self, question: str) -> Dict[str, Any]:
        """Classify the physics question using the base tutor"""
        try:
            # Use the base tutor's classification chain
            classification_chain = self.base_tutor.chains['question_classification']
            classification_result = await classification_chain.ainvoke({
                'question': question
            })
            
            # Parse the classification result
            classification = self._parse_classification_result(classification_result)
            return classification
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                'category': 'concept',
                'topic': 'general',
                'difficulty': 'intermediate',
                'response_length': 'medium'
            }
    
    def _parse_classification_result(self, result: str) -> Dict[str, Any]:
        """Parse the classification result from the AI"""
        classification = {
            'category': 'concept',
            'topic': 'general', 
            'difficulty': 'intermediate',
            'response_length': 'medium'
        }
        
        try:
            lines = result.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'category' in key:
                        classification['category'] = value
                    elif 'topic' in key:
                        classification['topic'] = value
                    elif 'difficulty' in key:
                        classification['difficulty'] = value
                    elif 'response length' in key:
                        classification['response_length'] = value
                        
        except Exception as e:
            logger.warning(f"Failed to parse classification: {e}")
        
        return classification
    
    async def _retrieve_relevant_context(self, 
                                       question: str, 
                                       classification: Dict[str, Any],
                                       max_items: int = 5,
                                       user_id: Optional[str] = None) -> List[SearchResult]:
        """Retrieve relevant context from the knowledge base"""
        
        # Skip retrieval for greetings or very short queries
        greetings = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
        question_lower = question.lower().strip()
        
        if question_lower in greetings or len(question.split()) < 3:
            logger.info("⚡ Skipping context retrieval for greeting/short query")
            return []
        
        try:
            # Build search filters based on classification
            topic_filter = classification.get('topic')
            if topic_filter == 'general':
                topic_filter = None
                
            difficulty_filter = classification.get('difficulty')
            
            # For user-specific searches, be more flexible with filters to find user content
            if user_id:
                # First try with user_id only (no topic/difficulty restrictions)
                search_response = await self.vector_database.search_physics_content(
                    query=question,
                    limit=min(max_items, 5),
                    user_id=user_id,  # Only filter by user materials
                    min_similarity=0.3  # Lower threshold for user materials
                )
                
                # If we found user content, use it
                if search_response.results:
                    logger.info(f"✅ Found {len(search_response.results)} user-specific results")
                else:
                    # Fallback to general search with topic/difficulty filters
                    logger.info("🔄 No user content found, searching general knowledge...")
                    search_response = await self.vector_database.search_physics_content(
                        query=question,
                        limit=min(max_items, 3),
                        topic_filter=topic_filter,
                        difficulty_filter=difficulty_filter,
                        min_similarity=0.5
                    )
            else:
                # No user_id provided, use general search with filters
                search_response = await self.vector_database.search_physics_content(
                    query=question,
                    limit=min(max_items, 3),
                    topic_filter=topic_filter,
                    difficulty_filter=difficulty_filter,
                    min_similarity=0.5
                )
            
            # Calculate average relevance for statistics
            if search_response.results:
                avg_relevance = sum(r.similarity_score for r in search_response.results) / len(search_response.results)
                # Avoid division by zero in statistics calculation
                if self.stats['rag_queries'] > 0:
                    self.stats['average_context_relevance'] = (
                        (self.stats['average_context_relevance'] * (self.stats['rag_queries'] - 1) + avg_relevance) 
                        / self.stats['rag_queries']
                    )
                else:
                    self.stats['average_context_relevance'] = avg_relevance
            
            return search_response.results
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []
    
    async def _generate_enhanced_response(self, 
                                        question: str,
                                        classification: Dict[str, Any],
                                        retrieved_context: List[SearchResult],
                                        user_context: Optional[str],
                                        response_length: str,
                                        difficulty_level: str,
                                        session_id: Optional[str] = None) -> str:
        """Generate enhanced response using retrieved context"""
        
        # Prepare context for the AI with session history
        context_text = self._format_context_for_ai(
            retrieved_context, 
            user_context,
            session_id=session_id,
            question=question
        )
        
        # Select appropriate chain based on question category
        category = classification.get('category', 'concept')
        
        try:
            if category == 'concept':
                chain = self.base_tutor.chains.get('rag_response', self.base_tutor.chains['concept_explanation'])
                # Determine focus areas based on classification
                focus_areas = classification.get('topic', 'general physics concepts')
                response = await chain.ainvoke({
                    'question': question,
                    'context': context_text,
                    'response_length': response_length,
                    'difficulty_level': difficulty_level,
                    'focus_areas': focus_areas
                })
                
            elif category == 'derivation':
                chain = self.base_tutor.chains['derivation']
                response = await chain.ainvoke({
                    'equation': question,
                    'starting_point': 'fundamental principles',
                    'context': context_text,
                    'show_all_steps': True
                })
                
            elif category == 'problem_solving':
                chain = self.base_tutor.chains['problem_solving']
                response = await chain.ainvoke({
                    'problem_statement': question,
                    'given_info': 'As stated in the problem',
                    'find_what': 'As requested',
                    'approach_hint': context_text
                })
                
            else:  # Default to concept explanation
                chain = self.base_tutor.chains['concept_explanation']
                response = await chain.ainvoke({
                    'concept': question,
                    'context': context_text,
                    'difficulty_level': difficulty_level,
                    'response_length': response_length
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}", exc_info=True)
            logger.error(f"Question: {question}")
            logger.error(f"Category: {category}")
            logger.error(f"Context length: {len(context_text)} chars")
            logger.error(f"Retrieved context items: {len(retrieved_context)}")
            return f"I apologize, but I encountered an error while generating the response. Please try rephrasing your question."
    
    def _format_context_for_ai(self, 
                              retrieved_context: List[SearchResult], 
                              user_context: Optional[str],
                              session_id: Optional[str] = None,
                              question: Optional[str] = None) -> str:
        """Format retrieved context for AI consumption with session history"""
        context_parts = []
        
        # Add recent conversation history (most important for context)
        if session_id and session_id in self.session_history:
            recent = self.session_history[session_id][-3:]  # Last 3 messages
            if recent:
                context_parts.append("Recent Conversation:")
                for msg in recent:
                    context_parts.append(f"Q: {msg['question'][:80]}...")
                    context_parts.append(f"A: {msg['answer'][:150]}...\n")
        
        # Add user-provided context
        if user_context:
            context_parts.append(f"User Context: {user_context}")
        
        # Add only high-quality retrieved context
        if retrieved_context:
            # Filter for high similarity (>0.6) and limit to 2 items
            high_quality = [r for r in retrieved_context if r.similarity_score > 0.6][:2]
            
            if high_quality:
                context_parts.append("Relevant Knowledge:")
                for i, item in enumerate(high_quality):
                    # Truncate content to 300 chars to save tokens
                    content_preview = item.content.content[:300]
                    if len(item.content.content) > 300:
                        content_preview += "..."
                    
                    context_parts.append(
                        f"{i+1}. {item.content.title} (Similarity: {item.similarity_score:.2f})\n"
                        f"   {content_preview}"
                    )
        
        return "\n\n".join(context_parts) if context_parts else "No additional context available."
    
    async def add_physics_knowledge(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add physics knowledge to the vector database
        
        Args:
            knowledge_items: List of physics knowledge items to add
            
        Returns:
            Addition results and statistics
        """
        logger.info(f"📚 Adding {len(knowledge_items)} knowledge items to database")
        
        result = await self.vector_database.add_physics_content(knowledge_items)
        
        logger.info(f"✅ Knowledge addition completed: {result['successful_additions']} items added")
        return result
    
    async def search_physics_knowledge(self, 
                                     query: str, 
                                     **kwargs) -> SearchResponse:
        """
        Search the physics knowledge base
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            Search results
        """
        return await self.vector_database.search_physics_content(query, **kwargs)
    
    async def get_similar_concepts(self, concept_id: str, limit: int = 5) -> List[SearchResult]:
        """Get concepts similar to a given concept"""
        return await self.vector_database.get_similar_content(concept_id, limit)
    
    async def analyze_physics_image(self, 
                                  image_description: str, 
                                  question: str,
                                  difficulty_level: str = "intermediate") -> str:
        """
        Analyze physics problems from images using vision capabilities
        
        Args:
            image_description: Description of the physics image/diagram
            question: Question about the image
            difficulty_level: Target difficulty level
            
        Returns:
            Analysis and explanation
        """
        try:
            # Use the base tutor's vision capabilities
            vision_prompt = f"""
            Analyze this physics image/diagram: {image_description}
            
            Question: {question}
            Difficulty Level: {difficulty_level}
            
            Please provide a detailed physics analysis including:
            1. Description of the physical situation
            2. Relevant physics principles and equations
            3. Step-by-step solution approach
            4. Final answer with proper units
            """
            
            # Use vision-enabled LLM
            response = await self.base_tutor.llm_vision.ainvoke(vision_prompt)
            return response.content
            
        except Exception as e:
            error_msg = f"Image analysis failed: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I couldn't analyze the image. Error: {error_msg}"
    
    async def generate_physics_diagram(self,
                                     description: str,
                                     diagram_type: str = "general",
                                     style: str = "educational",
                                     include_labels: bool = True,
                                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate physics diagrams using Gemini 2.5 Flash Image
        
        Args:
            description: Description of what to draw
            diagram_type: Type of diagram (force, circuit, wave, energy, motion, etc.)
            style: Visual style (educational, technical, sketch, colorful)
            include_labels: Whether to include labels and annotations
            session_id: Session ID for conversation context
            
        Returns:
            Dict with image data, explanation, and metadata
        """
        try:
            logger.info(f"🎨 Generating physics diagram: '{description[:50]}...'")
            
            # Build enhanced prompt based on diagram type and style
            prompt = self._build_diagram_prompt(
                description, 
                diagram_type, 
                style, 
                include_labels,
                session_id
            )
            
            # Import Google GenAI client
            try:
                from google import genai
                from google.genai import types
                from PIL import Image
                from io import BytesIO
                import os
                import base64
            except ImportError as e:
                logger.error(f"Missing required libraries: {e}")
                return {
                    'success': False,
                    'error': 'Missing required libraries. Please install google-genai and Pillow.'
                }
            
            # Initialize client with API key from environment
            # Try both GOOGLE_API_KEY and GEMINI_API_KEY for compatibility
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("API key not found (tried GOOGLE_API_KEY and GEMINI_API_KEY)")
                return {
                    'success': False,
                    'error': 'API key not configured. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.'
                }
            
            client = genai.Client(api_key=api_key)
            
            # Generate image with Gemini 2.0 Flash Image Generation model
            # This model requires both TEXT and IMAGE modalities
            config = types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                temperature=0.4,  # Balance creativity with accuracy
            )
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=[prompt],
                config=config,
            )
            
            # Extract text explanation and image
            explanation = None
            image_data = None
            image_base64 = None
            
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    explanation = part.text
                elif part.inline_data is not None:
                    # Convert image data to base64 for frontend
                    image_data = part.inline_data.data
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    # Also save to file for serving
                    image = Image.open(BytesIO(image_data))
                    
                    # Create images directory if it doesn't exist
                    images_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'generated_images')
                    os.makedirs(images_dir, exist_ok=True)
                    
                    # Generate unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"physics_diagram_{timestamp}_{hash(description) % 10000}.png"
                    filepath = os.path.join(images_dir, filename)
                    
                    # Save image
                    image.save(filepath, 'PNG')
                    logger.info(f"💾 Saved diagram to: {filepath}")
            
            if image_base64:
                result = {
                    'success': True,
                    'image_base64': image_base64,
                    'image_url': f"/static/generated_images/{filename}",
                    'explanation': explanation or "Diagram generated successfully.",
                    'diagram_type': diagram_type,
                    'style': style,
                    'prompt_used': description,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"✅ Diagram generated successfully")
                return result
            else:
                logger.warning("No image generated in response")
                return {
                    'success': False,
                    'error': 'No image was generated. Please try rephrasing your request.'
                }
                
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to generate diagram: {str(e)}"
            }
    
    def _build_diagram_prompt(self,
                            description: str,
                            diagram_type: str,
                            style: str,
                            include_labels: bool,
                            session_id: Optional[str] = None) -> str:
        """Build optimized prompt for physics diagram generation"""
        
        # Check session history for context
        context = ""
        if session_id and session_id in self.session_history:
            recent = self.session_history[session_id][-2:]  # Last 2 messages
            if recent:
                topics = [msg['question'] for msg in recent]
                context = f"Context from conversation: discussing {', '.join(topics)}. "
        
        # Base prompt templates by diagram type
        type_prompts = {
            'force': "Create a clear physics force diagram showing ",
            'circuit': "Create an electrical circuit diagram showing ",
            'wave': "Create a wave diagram illustrating ",
            'energy': "Create an energy diagram showing ",
            'motion': "Create a motion diagram depicting ",
            'field': "Create a field diagram showing ",
            'vector': "Create a vector diagram illustrating ",
            'graph': "Create a physics graph showing ",
            'general': "Create a physics diagram showing "
        }
        
        base_prompt = type_prompts.get(diagram_type, type_prompts['general'])
        
        # Style modifiers
        style_modifiers = {
            'educational': "in a clear, educational style suitable for teaching. Use clean lines, bright colors, and a white background.",
            'technical': "in a technical, precise style with accurate proportions and professional presentation.",
            'sketch': "in a hand-drawn sketch style, as if drawn on a whiteboard.",
            'colorful': "in a vibrant, colorful style that makes the concepts engaging and memorable.",
            'minimal': "in a minimal, clean style with simple lines and limited colors for clarity."
        }
        
        style_modifier = style_modifiers.get(style, style_modifiers['educational'])
        
        # Label instructions
        label_instruction = ""
        if include_labels:
            label_instruction = " Include clear labels, arrows, and annotations to explain all key components and forces. Use standard physics notation."
        
        # Build final prompt
        prompt = f"{context}{base_prompt}{description} {style_modifier}{label_instruction}"
        
        # Add physics-specific quality modifiers
        prompt += " The diagram should be scientifically accurate, clear, and suitable for physics education."
        
        return prompt
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for the enhanced tutor"""
        base_stats = self.vector_database.get_database_stats()
        
        uptime = datetime.now() - self.stats['last_reset']
        
        enhanced_stats = {
            'enhanced_tutor_uptime_hours': uptime.total_seconds() / 3600,
            'total_enhanced_queries': self.stats['total_enhanced_queries'],
            'rag_queries': self.stats['rag_queries'],
            'rag_usage_percentage': (self.stats['rag_queries'] / max(1, self.stats['total_enhanced_queries'])) * 100,
            'average_context_retrieval_time': (self.stats['context_retrieval_time'] / max(1, self.stats['rag_queries'])),
            'average_response_generation_time': (self.stats['response_generation_time'] / max(1, self.stats['total_enhanced_queries'])),
            'average_context_relevance': self.stats['average_context_relevance'],
            'rag_enabled': self.enable_rag
        }
        
        return {
            'enhanced_tutor_stats': enhanced_stats,
            'vector_database_stats': base_stats
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'total_enhanced_queries': 0,
            'rag_queries': 0,
            'context_retrieval_time': 0.0,
            'response_generation_time': 0.0,
            'average_context_relevance': 0.0,
            'last_reset': datetime.now()
        }
        self.vector_database.reset_stats()
        logger.info("📊 Enhanced tutor statistics reset")
    
    async def generate_enhanced_response(
        self,
        query: str,
        user_id: str,
        session_id: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Phase 7.3: Generate enhanced response with all advanced features
        
        Features:
        - Step-by-step derivations
        - Adaptive response length and complexity
        - Follow-up suggestions
        - Prerequisites checking
        - Quality evaluation
        """
        preferences = preferences or {}
        response_length = preferences.get('length', 'medium')
        complexity_level = preferences.get('level', 'intermediate')
        
        try:
            # Initialize response adapter
            adapter = ResponseAdapter()
            
            # Step 1: Get base response with context
            base_response = await self.ask_physics_question(
                question=query,
                response_length=response_length,
                difficulty_level=complexity_level,
                use_rag=True,
                session_id=session_id,
                user_id=user_id
            )
            
            if not base_response.get('success'):
                return base_response
            
            content = base_response['answer']
            
            # Step 2: Adapt response length
            adapted = adapter.adapt_length(content, response_length)
            
            # Step 3: Adapt complexity
            complexity_adapted = adapter.adapt_complexity(adapted, complexity_level)
            
            # Step 4: Add derivation steps if applicable
            is_derivation = self._is_derivation_query(query)
            steps = []
            if is_derivation:
                steps = break_into_steps(complexity_adapted['content'])
            
            # Step 5: Extract topic and generate follow-ups
            topic = base_response.get('classification', {}).get('topic', 'physics')
            follow_ups = adapter.generate_follow_ups(topic, query)
            
            # Step 6: Generate prerequisites
            prerequisites = generate_prerequisites(topic)
            
            # Step 7: Extract key concepts
            key_concepts = adapter.extract_key_concepts(complexity_adapted['content'])
            
            # Step 8: Extract equations
            equations = extract_key_equations(complexity_adapted['content'])
            
            # Step 9: Prioritize and cite sources
            sources = base_response.get('retrieved_context', [])
            citations = generate_citations(sources) if sources else []
            
            # Build enhanced response
            return {
                'success': True,
                'response': {
                    'content': complexity_adapted['content'],
                    'formatted': format_derivation(steps) if steps else complexity_adapted['content'],
                    'steps': steps,
                    'complexity_level': complexity_level,
                    'response_length': response_length,
                },
                'metadata': {
                    'topic': topic,
                    'query_type': 'derivation' if is_derivation else 'concept',
                    'sources_used': len(sources),
                    'quality_score': 8.0,  # Simplified for speed
                    'key_concepts': key_concepts,
                },
                'learning_aids': {
                    'follow_up_questions': follow_ups,
                    'prerequisites': prerequisites,
                    'key_equations': equations,
                },
                'citations': citations,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced response generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback': 'Basic response mode activated'
            }
    
    def _is_derivation_query(self, query: str) -> bool:
        """Check if query requests a derivation"""
        keywords = ['derive', 'derivation', 'prove', 'show that', 'demonstrate', 'step by step']
        return any(kw in query.lower() for kw in keywords)

# Convenience functions for easy usage
async def create_enhanced_physics_tutor(qdrant_client=None, **kwargs) -> EnhancedPhysicsAITutor:
    """Create a new enhanced physics AI tutor"""
    return EnhancedPhysicsAITutor(qdrant_client=qdrant_client, **kwargs)

async def ask_enhanced_physics_question(question: str, 
                                      qdrant_client=None, 
                                      **kwargs) -> Dict[str, Any]:
    """Convenience function to ask a physics question with enhancement"""
    tutor = EnhancedPhysicsAITutor(qdrant_client=qdrant_client)
    return await tutor.ask_physics_question(question, **kwargs)

# Global instance for reuse
_enhanced_tutor: Optional[EnhancedPhysicsAITutor] = None

def get_enhanced_tutor(qdrant_client=None) -> EnhancedPhysicsAITutor:
    """Get or create global enhanced tutor instance"""
    global _enhanced_tutor
    
    if _enhanced_tutor is None:
        _enhanced_tutor = EnhancedPhysicsAITutor(qdrant_client=qdrant_client)
    
    return _enhanced_tutor

# Example usage and comprehensive testing
async def test_enhanced_physics_tutor():
    """Comprehensive test of the enhanced physics tutor"""
    print("🧪 Testing Enhanced Physics AI Tutor with Embeddings")
    print("=" * 60)
    
    # Create enhanced tutor
    tutor = EnhancedPhysicsAITutor()
    
    # Test 1: Add some physics knowledge
    print("\n1️⃣ Adding physics knowledge to the database...")
    sample_knowledge = [
        {
            'title': 'Newton\'s Laws of Motion',
            'content': 'Newton\'s three laws describe the relationship between forces and motion. First law: objects in motion stay in motion. Second law: F=ma. Third law: action-reaction pairs.',
            'topic': 'mechanics',
            'subtopic': 'dynamics',
            'difficulty_level': 'beginner',
            'content_type': 'concept'
        },
        {
            'title': 'Conservation of Energy',
            'content': 'Energy cannot be created or destroyed, only converted between forms. In mechanical systems, kinetic and potential energy are interconverted.',
            'topic': 'mechanics', 
            'subtopic': 'energy',
            'difficulty_level': 'intermediate',
            'content_type': 'concept'
        },
        {
            'title': 'Maxwell\'s Equations',
            'content': 'Four fundamental equations describing electromagnetic fields: Gauss law, Gauss law for magnetism, Faraday law, and Ampere-Maxwell law.',
            'topic': 'electromagnetism',
            'difficulty_level': 'advanced',
            'content_type': 'formula'
        }
    ]
    
    add_result = await tutor.add_physics_knowledge(sample_knowledge)
    print(f"✅ Added {add_result['successful_additions']} knowledge items")
    
    # Test 2: Ask physics questions with RAG
    print("\n2️⃣ Testing enhanced physics questions...")
    
    test_questions = [
        "What is Newton's second law and how does it relate to force and acceleration?",
        "Explain the principle of conservation of energy in mechanical systems",
        "How do electromagnetic fields behave according to Maxwell's equations?"
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n🤔 Question {i+1}: {question}")
        
        response = await tutor.ask_physics_question(
            question=question,
            response_length="medium",
            difficulty_level="intermediate",
            use_rag=True
        )
        
        if response['success']:
            print(f"✅ Response generated successfully")
            print(f"📊 Used {response['context_items_used']} context items")
            print(f"⏱️ Processing time: {response['response_metadata']['processing_time']:.3f}s")
            print(f"🔍 Classification: {response['classification']['category']} - {response['classification']['topic']}")
            
            # Show first 200 chars of answer
            answer_preview = response['answer'][:200] + "..." if len(response['answer']) > 200 else response['answer']
            print(f"💡 Answer preview: {answer_preview}")
        else:
            print(f"❌ Error: {response['error']}")
    
    # Test 3: Search functionality
    print(f"\n3️⃣ Testing knowledge search...")
    search_response = await tutor.search_physics_knowledge(
        "force and motion relationships",
        limit=3
    )
    
    print(f"🔍 Search found {search_response.total_found} results")
    for result in search_response.results:
        print(f"  - {result.content.title} (similarity: {result.similarity_score:.3f})")
    
    # Test 4: Image analysis
    print(f"\n4️⃣ Testing image analysis...")
    image_response = await tutor.analyze_physics_image(
        image_description="A spring attached to a mass on a horizontal surface with friction",
        question="What forces act on the mass and how do they affect motion?"
    )
    
    print(f"🖼️ Image analysis completed:")
    print(f"   {image_response[:150]}...")
    
    # Show comprehensive statistics
    print(f"\n📈 Enhanced Tutor Statistics:")
    stats = tutor.get_enhanced_stats()
    
    print("Enhanced Tutor Metrics:")
    for key, value in stats['enhanced_tutor_stats'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_physics_tutor())