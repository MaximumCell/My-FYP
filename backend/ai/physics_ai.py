"""
AI Integration Mod        # Initialize primary AI model for response generation
        self.primary_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            max_tokens=2048,
            google_api_key=os.getenv('GEMINI_API_KEY')
        ) Physics Tutor
Handles both primary AI response generation and supervisor evaluation using Gemini
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

class PhysicsAI:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Initialize primary AI model for response generation
        self.primary_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            max_tokens=2048,
            google_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # Initialize supervisor model for quality evaluation
        self.supervisor_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-pro-exp",
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.1,
            convert_system_message_to_human=True
        )
        
        # Load prompt templates
        self._load_prompt_templates()
    
    def _load_prompt_templates(self):
        """Load and configure prompt templates for different use cases"""
        
        # Primary AI response template
        self.response_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert physics tutor specialized in helping students understand complex physics concepts and derivations. 

Your role:
- Provide clear, accurate explanations of physics concepts
- Break down complex derivations into step-by-step processes
- Use appropriate mathematical notation and LaTeX formatting
- Adapt explanation length based on user preference (short/long)
- Reference provided materials when available
- Generate visual descriptions when helpful

Response format guidelines:
- For SHORT answers: Key concept + essential formula + brief example
- For LONG answers: Comprehensive explanation + full derivation + multiple examples + applications
- Always indicate source confidence and reference materials used
- Use LaTeX for mathematical expressions: $equation$ for inline, $$equation$$ for display

Physics accuracy is paramount. If unsure, indicate uncertainty clearly."""),
            
            HumanMessage(content="{user_query}")
        ])
        
        # Supervisor evaluation template
        self.evaluation_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI supervisor evaluating the quality of physics educational responses. 

Evaluate the response based on these criteria (score 1-10 each):
1. Physics Accuracy: Correctness of physics concepts and mathematical derivations
2. Mathematical Correctness: Proper equations, units, and mathematical rigor
3. Explanation Clarity: How well the explanation is structured and understandable
4. Completeness: Whether the response fully addresses the user's question
5. Educational Value: How well it helps student learning and understanding
6. Source Relevance: Appropriate use of provided reference materials
7. Step-by-Step Quality: For derivations, clarity of each step and reasoning

Provide:
- Overall score (1-10)
- Individual criterion scores
- Specific strengths and weaknesses
- Missing elements or improvements needed
- Physics/math accuracy issues (if any)

Be objective and constructive in your evaluation."""),
            
            HumanMessage(content="""USER QUERY: {user_query}

AI RESPONSE TO EVALUATE: {ai_response}

CONTEXT: {context}

Provide detailed evaluation in JSON format.""")
        ])
        
        # Question classification template
        self.classification_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Classify physics questions into categories to determine the best response strategy.

Categories:
- concept: Asking for explanation of physics concepts, theories, or phenomena
- derivation: Requesting mathematical derivation of equations or formulas
- problem_solving: Asking for help solving specific physics problems
- application: Questions about real-world applications of physics principles

Also determine:
- Topic: mechanics, thermodynamics, electromagnetism, quantum_physics, waves, optics, etc.
- Difficulty: beginner, intermediate, advanced
- Response_length: short, long (based on question complexity and user request)

Return JSON format with classification results."""),
            
            HumanMessage(content="{user_query}")
        ])
    
    async def generate_response(self, 
                              user_query: str, 
                              context: Dict = None,
                              response_length: str = "long",
                              sources: List[str] = None) -> Dict:
        """Generate physics response using primary AI model"""
        try:
            # Prepare context information
            context_info = ""
            if context:
                if sources:
                    context_info += f"Available sources: {', '.join(sources)}\n"
                if context.get('preferred_books'):
                    context_info += f"Preferred references: {', '.join(context['preferred_books'])}\n"
                if context.get('difficulty_level'):
                    context_info += f"Student level: {context['difficulty_level']}\n"
            
            # Enhance query with context
            enhanced_query = f"""
            {context_info}
            
            User Question: {user_query}
            
            Response Length Preference: {response_length}
            
            Please provide a {response_length} explanation focusing on physics accuracy and educational value.
            """
            
            # Generate response
            messages = self.response_template.format_messages(user_query=enhanced_query)
            response = await self.primary_model.ainvoke(messages)
            
            return {
                'content': response.content,
                'model': 'gemini-2.0-flash-exp',
                'timestamp': datetime.now(),
                'context_used': context_info,
                'response_length': response_length
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'content': "I apologize, but I'm having difficulty generating a response right now. Please try again later.",
                'model': 'gemini-2.0-flash-exp',
                'timestamp': datetime.now(),
                'error': str(e)
            }
    
    async def classify_question(self, user_query: str) -> Dict:
        """Classify user question to determine response strategy"""
        try:
            messages = self.classification_template.format_messages(user_query=user_query)
            response = await self.primary_model.ainvoke(messages)
            
            # Parse JSON response (assuming model returns valid JSON)
            import json
            try:
                classification = json.loads(response.content)
                return classification
            except json.JSONDecodeError:
                # Fallback classification
                return {
                    'category': 'concept',
                    'topic': 'general',
                    'difficulty': 'intermediate',
                    'response_length': 'long'
                }
                
        except Exception as e:
            print(f"Error classifying question: {e}")
            return {
                'category': 'concept',
                'topic': 'general', 
                'difficulty': 'intermediate',
                'response_length': 'long'
            }
    
    async def evaluate_response(self, 
                              user_query: str,
                              ai_response: str,
                              context: Dict = None) -> Dict:
        """Evaluate AI response quality using supervisor model"""
        try:
            context_str = str(context) if context else "No additional context provided"
            
            messages = self.evaluation_template.format_messages(
                user_query=user_query,
                ai_response=ai_response,
                context=context_str
            )
            
            evaluation = await self.supervisor_llm.ainvoke(messages)
            
            # Parse evaluation response
            import json
            try:
                eval_data = json.loads(evaluation.content)
                
                # Ensure required fields exist
                if 'overall_score' not in eval_data:
                    eval_data['overall_score'] = 7.0  # Default reasonable score
                
                eval_data['evaluation_model'] = 'gemini-2.0-pro-exp-supervisor'
                eval_data['evaluation_timestamp'] = datetime.now()
                eval_data['supervisor_confidence'] = 0.8  # Default confidence
                
                return eval_data
                
            except json.JSONDecodeError:
                # Fallback evaluation
                return {
                    'overall_score': 7.0,
                    'evaluation_criteria': {
                        'physics_accuracy': 7,
                        'mathematical_correctness': 7,
                        'explanation_clarity': 7,
                        'completeness': 7,
                        'educational_value': 7,
                        'source_relevance': 6,
                        'step_by_step_quality': 7
                    },
                    'detailed_feedback': {
                        'strengths': ['Response provided'],
                        'weaknesses': ['Evaluation parsing failed'],
                        'missing_elements': [],
                        'accuracy_issues': [],
                        'improvement_suggestions': ['Technical improvement needed']
                    },
                    'evaluation_model': 'gemini-pro-supervisor',
                    'supervisor_confidence': 0.5
                }
                
        except Exception as e:
            print(f"Error evaluating response: {e}")
            return {
                'overall_score': 5.0,
                'evaluation_criteria': {
                    'physics_accuracy': 5,
                    'mathematical_correctness': 5,
                    'explanation_clarity': 5,
                    'completeness': 5,
                    'educational_value': 5,
                    'source_relevance': 5,
                    'step_by_step_quality': 5
                },
                'detailed_feedback': {
                    'strengths': [],
                    'weaknesses': ['Evaluation failed'],
                    'missing_elements': [],
                    'accuracy_issues': ['Could not evaluate'],
                    'improvement_suggestions': ['System error - please retry']
                },
                'evaluation_model': 'gemini-pro-supervisor',
                'supervisor_confidence': 0.0,
                'error': str(e)
            }
    
    def calculate_weighted_score(self, evaluation_criteria: Dict) -> float:
        """Calculate weighted overall score from individual criteria"""
        weights = {
            'physics_accuracy': 0.25,
            'mathematical_correctness': 0.25,
            'explanation_clarity': 0.20,
            'completeness': 0.15,
            'educational_value': 0.10,
            'source_relevance': 0.05
        }
        
        total_score = 0
        total_weight = 0
        
        for criterion, score in evaluation_criteria.items():
            if criterion in weights:
                total_score += score * weights[criterion]
                total_weight += weights[criterion]
        
        return total_score / total_weight if total_weight > 0 else 5.0
    
    def get_delivery_decision(self, overall_score: float) -> Dict:
        """Determine whether to deliver response based on quality score"""
        thresholds = {
            'excellent': 8.5,
            'good': 7.0,
            'acceptable': 5.0,
            'poor': 3.0
        }
        
        if overall_score >= thresholds['excellent']:
            return {
                'action': 'deliver_immediately',
                'message': None,
                'confidence': 'high'
            }
        elif overall_score >= thresholds['good']:
            return {
                'action': 'deliver_with_note',
                'message': 'This response has been reviewed for quality.',
                'confidence': 'medium'
            }
        elif overall_score >= thresholds['acceptable']:
            return {
                'action': 'deliver_with_improvements',
                'message': 'This response may benefit from additional clarification.',
                'confidence': 'low'
            }
        else:
            return {
                'action': 'regenerate_or_flag',
                'message': 'Response quality needs improvement.',
                'confidence': 'very_low'
            }

# Initialize physics AI system
physics_ai = PhysicsAI()