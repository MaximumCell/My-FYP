"""
Physics AI Tutor - LangChain + Gemini Integration
=================================================

This module provides the core LangChain integration with Google Gemini
for physics education, including specialized prompt templates and chains.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# LangChain imports
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# Environment
from dotenv import load_dotenv

# Local imports
from qdrant_client import PhysicsVectorDB

load_dotenv()
logger = logging.getLogger(__name__)

class PhysicsAITutor:
    """
    Main Physics AI Tutor class integrating LangChain with Gemini
    """
    
    def __init__(self):
        """Initialize the Physics AI Tutor"""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize vector database
        self.vector_db = None
        self._initialize_vector_db()
        
        # Initialize prompt templates
        self.prompt_templates = self._create_prompt_templates()
        
        # Initialize Gemini models via LangChain
        # Primary model for general physics questions
        self.llm_text = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=self.gemini_api_key,
            temperature=0.3,  # Slightly creative but focused
            convert_system_message_to_human=True
        )
        
        # Vision model for image-based physics questions  
        self.llm_vision = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # Flash model supports vision too
            google_api_key=self.gemini_api_key,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        # AI Supervisor system for response quality evaluation
        self.llm_supervisor = ChatGoogleGenerativeAI(
            model="gemini-2.0-pro",  # Pro model for evaluation
            google_api_key=self.gemini_api_key,
            temperature=0.1,  # Lower temperature for more consistent evaluation
            convert_system_message_to_human=True
        )
        
        # Initialize chains (after LLM models are created)
        self.chains = self._create_chains()
        
        logger.info("✅ Physics AI Tutor initialized with Gemini Flash Latest")
    
    def _initialize_vector_db(self):
        """Initialize vector database connection"""
        try:
            from qdrant_client import create_physics_vector_db
            qdrant_url = os.getenv('QDRANT_URL')
            if qdrant_url:
                self.vector_db = create_physics_vector_db(qdrant_url)
                logger.info("✅ Vector database connected")
            else:
                logger.warning("⚠️ QDRANT_URL not found - vector search disabled")
        except Exception as e:
            logger.error(f"❌ Vector database connection failed: {e}")
    
    def _create_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Create specialized prompt templates for physics education"""
        
        templates = {}
        
        # 1. Concept Explanation Template
        templates['concept_explanation'] = ChatPromptTemplate.from_messages([
            ("system", """You are an expert physics tutor with deep knowledge of undergraduate and graduate physics. 
            Your goal is to provide clear, accurate, and educational explanations of physics concepts.
            
            Guidelines:
            - Always start with the fundamental concept
            - Use step-by-step explanations for complex topics
            - Include relevant equations with proper notation
            - Provide concrete examples when helpful
            - Mention prerequisites if the concept builds on other topics
            - Be mathematically rigorous but accessible
            - Use proper physics terminology
            """),
            ("human", """Explain the physics concept: {concept}
            
            Context: {context}
            Difficulty Level: {difficulty_level}
            Response Length: {response_length}
            
            Please provide a {response_length} explanation appropriate for {difficulty_level} level.""")
        ])
        
        # 2. Derivation Template
        templates['derivation'] = ChatPromptTemplate.from_messages([
            ("system", """You are an expert physics tutor specializing in mathematical derivations.
            Your role is to guide students through physics derivations step-by-step.
            
            Guidelines:
            - Break down derivations into clear, logical steps
            - Explain the reasoning behind each step
            - Highlight key assumptions and approximations
            - Use proper mathematical notation
            - Show intermediate steps clearly
            - Point out common pitfalls or misconceptions
            - Connect the math to physical intuition
            """),
            ("human", """Derive the physics equation or relationship: {equation}
            
            Starting from: {starting_point}
            Context: {context}
            Show all steps: {show_all_steps}
            
            Please provide a complete step-by-step derivation.""")
        ])
        
        # 3. Problem Solving Template
        templates['problem_solving'] = ChatPromptTemplate.from_messages([
            ("system", """You are an expert physics problem-solving tutor.
            Your goal is to guide students through physics problems systematically.
            
            Guidelines:
            - Identify given information and what needs to be found
            - Choose appropriate physics principles and equations
            - Show systematic problem-solving approach
            - Check units and dimensional analysis
            - Verify answers make physical sense
            - Explain the reasoning at each step
            - Suggest alternative approaches when applicable
            """),
            ("human", """Help solve this physics problem: {problem_statement}
            
            Given information: {given_info}
            Find: {find_what}
            Approach: {approach_hint}
            
            Please provide a systematic solution with clear explanations.""")
        ])
        
        # 4. Question Classification Template
        templates['question_classification'] = ChatPromptTemplate.from_messages([
            ("system", """You are a physics education assistant that classifies student questions.
            
            Classify the question into one of these categories:
            - concept: Asking for explanation of a physics concept
            - derivation: Requesting mathematical derivation
            - problem_solving: Need help with a specific physics problem
            - clarification: Follow-up question or clarification
            - application: Real-world application of physics principles
            
            Also identify:
            - Physics topic (mechanics, electromagnetism, thermodynamics, etc.)
            - Difficulty level (beginner, intermediate, advanced)
            - Required response length (short, medium, long)
            """),
            ("human", """Classify this physics question: "{question}"
            
            Provide your classification in this format:
            Category: [category]
            Topic: [physics topic]
            Difficulty: [difficulty level]
            Response Length: [short/medium/long]
            Reasoning: [brief explanation]""")
        ])
        
        # 5. RAG-Enhanced Response Template
        templates['rag_response'] = ChatPromptTemplate.from_messages([
            ("system", """You are an expert physics tutor with access to relevant physics content.
            Use the provided context to enhance your response while maintaining accuracy.
            
            Guidelines:
            - Prioritize information from the provided context
            - If context is insufficient, clearly state limitations
            - Cite sources when using specific information
            - Maintain educational focus
            - Ensure mathematical accuracy
            """),
            ("human", """Question: {question}
            
            Relevant Context from Knowledge Base:
            {context}
            
            User Preferences:
            - Response Length: {response_length}
            - Difficulty Level: {difficulty_level}
            - Focus Areas: {focus_areas}
            
            Please provide a comprehensive response using the context and your physics knowledge.""")
        ])
        
        # 6. Image Analysis Template (for physics diagrams, graphs, equations)
        templates['image_analysis'] = ChatPromptTemplate.from_messages([
            ("system", """You are an expert physics tutor with the ability to analyze physics-related images.
            You can analyze diagrams, graphs, equations, experimental setups, and physics problems.
            
            Guidelines:
            - Describe what you see in the image clearly and accurately
            - Identify physics concepts, principles, or phenomena shown
            - Explain the physics behind what's depicted
            - If it's a problem, help solve it step-by-step
            - If it's a diagram, explain the relationships shown
            - If it's an equation, explain its meaning and applications
            - Point out any errors or misconceptions if present
            - Provide educational context appropriate for the difficulty level
            """),
            ("human", """Analyze this physics-related image: {image_description}
            
            Context: {context}
            Question: {question}
            Difficulty Level: {difficulty_level}
            
            Please provide a detailed analysis focusing on the physics concepts involved.""")
        ])
        
        # 7. AI Supervisor Evaluation Template
        templates['supervisor_evaluation'] = ChatPromptTemplate.from_messages([
            ("system", """You are an AI supervisor specializing in evaluating physics response quality.
            Your role is to assess physics explanations for accuracy, clarity, and educational value.
            
            Evaluation Criteria (1-10 scale for each):
            1. Physics Accuracy: Correctness of physics concepts, laws, and principles
            2. Mathematical Correctness: Accuracy of equations, calculations, and derivations
            3. Educational Quality: Clarity of explanation, appropriate level, learning value
            4. Completeness: How well the response addresses the original question
            5. Source Utilization: Appropriate use of provided context and references
            
            Provide:
            - Overall score (1-10)
            - Individual criterion scores
            - Strengths and weaknesses
            - Specific improvement suggestions
            - Delivery recommendation (deliver/improve/regenerate)
            """),
            ("human", """Evaluate this physics AI response:
            
            Original Question: {original_question}
            Question Type: {question_type}
            Difficulty Level: {difficulty_level}
            
            AI Response:
            {ai_response}
            
            Context Used:
            {context_used}
            
            Please provide a comprehensive evaluation with scores and feedback.""")
        ])
        
        return templates
    
    def _create_chains(self) -> Dict[str, LLMChain]:
        """Create LangChain chains for different physics tasks"""
        
        chains = {}
        
        # Create chains for each prompt template using text model
        for name, template in self.prompt_templates.items():
            chains[name] = template | self.llm_text | StrOutputParser()
        
        # Create vision-specific chains for image analysis
        chains['image_analysis'] = self.prompt_templates.get('image_analysis', self.prompt_templates['concept_explanation']) | self.llm_vision | StrOutputParser()
        
        # Create AI supervisor evaluation chain
        chains['supervisor_evaluation'] = self.prompt_templates.get('supervisor_evaluation') | self.llm_supervisor | StrOutputParser()
        
        return chains
    
    async def classify_question(self, question: str) -> Dict[str, str]:
        """Classify a physics question to determine the best response approach"""
        try:
            response = await self.chains['question_classification'].ainvoke({
                "question": question
            })
            
            # Parse the classification response
            classification = self._parse_classification(response)
            return classification
            
        except Exception as e:
            logger.error(f"Question classification failed: {e}")
            return {
                'category': 'concept',
                'topic': 'general',
                'difficulty': 'intermediate',
                'response_length': 'medium',
                'reasoning': 'Default classification due to parsing error'
            }
    
    def _parse_classification(self, response: str) -> Dict[str, str]:
        """Parse the classification response into structured data"""
        classification = {}
        
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'category':
                    classification['category'] = value
                elif key == 'topic':
                    classification['topic'] = value
                elif key == 'difficulty':
                    classification['difficulty'] = value
                elif key == 'response length':
                    classification['response_length'] = value
                elif key == 'reasoning':
                    classification['reasoning'] = value
        
        return classification
    
    async def answer_concept_question(self, concept: str, context: str = "", 
                                    difficulty_level: str = "intermediate",
                                    response_length: str = "medium") -> str:
        """Answer a conceptual physics question"""
        try:
            # Get relevant context from vector database if available
            if self.vector_db and not context:
                search_results = await self.vector_db.search_physics_content(
                    concept, limit=3
                )
                context = self._format_search_results(search_results)
            
            response = await self.chains['concept_explanation'].ainvoke({
                "concept": concept,
                "context": context,
                "difficulty_level": difficulty_level,
                "response_length": response_length
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Concept explanation failed: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    async def provide_derivation(self, equation: str, starting_point: str = "",
                               context: str = "", show_all_steps: bool = True) -> str:
        """Provide step-by-step physics derivation"""
        try:
            response = await self.chains['derivation'].ainvoke({
                "equation": equation,
                "starting_point": starting_point,
                "context": context,
                "show_all_steps": show_all_steps
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Derivation failed: {e}")
            return "I apologize, but I'm having trouble with the derivation right now. Please try again."
    
    async def solve_problem(self, problem_statement: str, given_info: str = "",
                          find_what: str = "", approach_hint: str = "") -> str:
        """Help solve a physics problem systematically"""
        try:
            response = await self.chains['problem_solving'].ainvoke({
                "problem_statement": problem_statement,
                "given_info": given_info,
                "find_what": find_what,
                "approach_hint": approach_hint
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Problem solving failed: {e}")
            return "I apologize, but I'm having trouble solving this problem right now. Please try again."
    
    async def answer_with_rag(self, question: str, difficulty_level: str = "intermediate",
                            response_length: str = "medium", focus_areas: List[str] = None) -> str:
        """Answer using RAG (Retrieval-Augmented Generation)"""
        try:
            # Search vector database for relevant context
            context = ""
            if self.vector_db:
                search_results = await self.vector_db.search_physics_content(
                    question, limit=5
                )
                context = self._format_search_results(search_results)
            
            # If no focus areas specified, use empty list
            if focus_areas is None:
                focus_areas = []
            
            response = await self.chains['rag_response'].ainvoke({
                "question": question,
                "context": context,
                "difficulty_level": difficulty_level,
                "response_length": response_length,
                "focus_areas": ", ".join(focus_areas)
            })
            
            return response
            
        except Exception as e:
            logger.error(f"RAG response failed: {e}")
            return "I apologize, but I'm having trouble accessing my knowledge base right now. Please try again."
    
    async def add_physics_content(self, content: str, topic: str = "", difficulty: str = "intermediate", title: str = ""):
        """Convenience method to add single physics content item"""
        if not self.vector_db:
            return None
        
        physics_items = [{
            "content": content,
            "topic": topic,
            "difficulty": difficulty,
            "title": title
        }]
        return await self.vector_db.add_physics_content(physics_items)
    
    async def analyze_physics_image(self, image_path: str = None, image_description: str = "", 
                                  question: str = "What physics concepts are shown in this image?",
                                  context: str = "", difficulty_level: str = "intermediate") -> str:
        """Analyze physics-related images using Gemini Vision model"""
        try:
            # If image_path is provided, we would typically encode it as base64
            # For now, we'll work with image descriptions
            if not image_description and image_path:
                image_description = f"Image file: {image_path}"
            elif not image_description:
                image_description = "No image description provided"
            
            response = await self.chains['image_analysis'].ainvoke({
                "image_description": image_description,
                "context": context,
                "question": question,
                "difficulty_level": difficulty_level
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return "I apologize, but I'm having trouble analyzing the image right now. Please try again."
    
    async def evaluate_response_quality(self, 
                                      original_question: str,
                                      ai_response: str,
                                      question_type: str = "concept",
                                      difficulty_level: str = "intermediate",
                                      context_used: str = "") -> Dict[str, Any]:
        """Evaluate AI response quality using supervisor model"""
        try:
            evaluation_response = await self.chains['supervisor_evaluation'].ainvoke({
                "original_question": original_question,
                "question_type": question_type,
                "difficulty_level": difficulty_level,
                "ai_response": ai_response,
                "context_used": context_used
            })
            
            # Parse evaluation response
            evaluation = self._parse_supervisor_evaluation(evaluation_response)
            return evaluation
            
        except Exception as e:
            logger.error(f"Supervisor evaluation failed: {e}")
            return {
                'overall_score': 5.0,  # Neutral score on failure
                'individual_scores': {},
                'strengths': [],
                'weaknesses': ['Evaluation system unavailable'],
                'improvement_suggestions': ['System evaluation failed - manual review recommended'],
                'delivery_recommendation': 'deliver',
                'evaluation_error': str(e)
            }
    
    def _parse_supervisor_evaluation(self, response: str) -> Dict[str, Any]:
        """Parse supervisor evaluation response"""
        evaluation = {
            'overall_score': 5.0,
            'individual_scores': {},
            'strengths': [],
            'weaknesses': [],
            'improvement_suggestions': [],
            'delivery_recommendation': 'deliver'
        }
        
        try:
            lines = response.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if 'overall score' in line.lower():
                    current_section = 'overall'
                elif 'individual' in line.lower() and 'score' in line.lower():
                    current_section = 'individual'
                elif 'strength' in line.lower():
                    current_section = 'strengths'
                elif 'weakness' in line.lower():
                    current_section = 'weaknesses'
                elif 'improvement' in line.lower() or 'suggestion' in line.lower():
                    current_section = 'suggestions'
                elif 'delivery' in line.lower() or 'recommendation' in line.lower():
                    current_section = 'delivery'
                
                # Parse content based on current section
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if current_section == 'overall' and any(word in key.lower() for word in ['overall', 'total', 'score']):
                        try:
                            evaluation['overall_score'] = float(value.split('/')[0])
                        except (ValueError, IndexError):
                            pass
                    elif current_section == 'individual':
                        try:
                            score_value = float(value.split('/')[0])
                            evaluation['individual_scores'][key.lower()] = score_value
                        except (ValueError, IndexError):
                            pass
                    elif current_section == 'delivery' and 'recommend' in key.lower():
                        evaluation['delivery_recommendation'] = value.lower()
                
                # Parse list items
                elif line.startswith('-') or line.startswith('•'):
                    item = line[1:].strip()
                    if current_section == 'strengths':
                        evaluation['strengths'].append(item)
                    elif current_section == 'weaknesses':
                        evaluation['weaknesses'].append(item)
                    elif current_section == 'suggestions':
                        evaluation['improvement_suggestions'].append(item)
        
        except Exception as e:
            logger.warning(f"Failed to parse supervisor evaluation: {e}")
        
        return evaluation
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the models being used"""
        return {
            "primary_model": "gemini-2.0-flash-exp",
            "vision_model": "gemini-2.0-flash-exp",
            "supervisor_model": "gemini-2.0-pro-exp",
            "capabilities": "Text analysis, image analysis, physics problem solving, response evaluation",
            "temperature": "0.3 (primary), 0.1 (supervisor)",
            "vector_db": "Qdrant" if self.vector_db else "None"
        }
    
    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Format vector search results for use in prompts"""
        if not search_results:
            return "No relevant context found in knowledge base."
        
        formatted_context = "Relevant Physics Content:\n\n"
        
        for i, result in enumerate(search_results, 1):
            score = result.get('score', 0)
            title = result.get('payload', {}).get('title', 'Unknown')
            content = result.get('payload', {}).get('content', '')
            
            formatted_context += f"{i}. {title} (relevance: {score:.2f})\n"
            formatted_context += f"   {content}\n\n"
        
        return formatted_context
    
    async def get_response(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main method to get AI response for a physics question"""
        try:
            # Set default context
            if context is None:
                context = {}
            
            # Classify the question
            classification = await self.classify_question(question)
            
            # Extract preferences from context
            difficulty_level = context.get('difficulty_level', classification.get('difficulty', 'intermediate'))
            response_length = context.get('response_length', classification.get('response_length', 'medium'))
            
            # Route to appropriate handler based on classification
            category = classification.get('category', 'concept')
            
            # Check if this is an image analysis request
            if context.get('image_path') or context.get('image_description'):
                response = await self.analyze_physics_image(
                    image_path=context.get('image_path'),
                    image_description=context.get('image_description', ''),
                    question=question,
                    context=context.get('additional_context', ''),
                    difficulty_level=difficulty_level
                )
                category = 'image_analysis'
            elif category == 'concept':
                response = await self.answer_concept_question(
                    question, 
                    context.get('additional_context', ''),
                    difficulty_level,
                    response_length
                )
            elif category == 'derivation':
                response = await self.provide_derivation(
                    question,
                    context.get('starting_point', ''),
                    context.get('additional_context', '')
                )
            elif category == 'problem_solving':
                response = await self.solve_problem(
                    question,
                    context.get('given_info', ''),
                    context.get('find_what', ''),
                    context.get('approach_hint', '')
                )
            else:
                # Default to RAG-enhanced response
                response = await self.answer_with_rag(
                    question,
                    difficulty_level,
                    response_length,
                    context.get('focus_areas', [])
                )
            
            return {
                'response': response,
                'classification': classification,
                'metadata': {
                    'difficulty_level': difficulty_level,
                    'response_length': response_length,
                    'category': category,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again.",
                'classification': {'category': 'error'},
                'metadata': {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            }

    async def add_physics_content(self, 
                                content: str, 
                                topic: str, 
                                title: str = "",
                                **kwargs) -> Dict[str, Any]:
        """
        Convenience method to add physics content with embeddings
        
        Args:
            content: Physics content text
            topic: Physics topic (mechanics, electromagnetism, etc.)
            title: Content title
            **kwargs: Additional metadata
            
        Returns:
            Addition result
        """
        try:
            # Import embedding components locally to avoid circular imports
            from ai.vector_database_integration import PhysicsVectorDatabase
            from ai.embedding_service import get_embedding_service
            
            # Create vector database if not exists
            if not hasattr(self, '_vector_db'):
                embedding_service = get_embedding_service()
                self._vector_db = PhysicsVectorDatabase(
                    embedding_service=embedding_service,
                    qdrant_client=self.vector_db
                )
            
            # Prepare content item
            content_item = {
                'title': title or f"{topic.title()} Concept",
                'content': content,
                'topic': topic,
                'difficulty_level': kwargs.get('difficulty_level', 'intermediate'),
                'content_type': kwargs.get('content_type', 'concept'),
                'source': kwargs.get('source'),
                'metadata': kwargs
            }
            
            # Add to vector database
            result = await self._vector_db.add_physics_content([content_item])
            
            logger.info(f"✅ Added physics content: {title or 'Untitled'}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to add physics content: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    async def search_physics_content(self, 
                                   query: str, 
                                   limit: int = 5,
                                   **kwargs) -> Dict[str, Any]:
        """
        Search physics content using embeddings
        
        Args:
            query: Search query
            limit: Maximum results to return
            **kwargs: Additional search parameters
            
        Returns:
            Search results
        """
        try:
            # Import embedding components locally
            from ai.vector_database_integration import PhysicsVectorDatabase
            from ai.embedding_service import get_embedding_service
            
            # Create vector database if not exists
            if not hasattr(self, '_vector_db'):
                embedding_service = get_embedding_service()
                self._vector_db = PhysicsVectorDatabase(
                    embedding_service=embedding_service,
                    qdrant_client=self.vector_db
                )
            
            # Perform search
            search_response = await self._vector_db.search_physics_content(
                query=query,
                limit=limit,
                **kwargs
            )
            
            # Format results for easier consumption
            results = []
            for result in search_response.results:
                results.append({
                    'title': result.content.title,
                    'content': result.content.content,
                    'topic': result.content.topic,
                    'similarity_score': result.similarity_score,
                    'rank': result.rank
                })
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'total_found': search_response.total_found,
                'search_time': search_response.search_time
            }
            
        except Exception as e:
            error_msg = f"Failed to search physics content: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'results': []
            }

# Factory function for easy initialization
def create_physics_ai_tutor() -> PhysicsAITutor:
    """Create and initialize Physics AI Tutor"""
    return PhysicsAITutor()

# Global instance (optional)
_physics_tutor = None

def get_physics_tutor() -> PhysicsAITutor:
    """Get global Physics AI Tutor instance"""
    global _physics_tutor
    if _physics_tutor is None:
        _physics_tutor = create_physics_ai_tutor()
    return _physics_tutor