"""
Response adaptation system for different answer lengths and complexity levels
"""
from typing import Dict, Any, Optional
import re


class ResponseAdapter:
    """Adapt physics responses based on user preferences"""
    
    def __init__(self):
        self.short_max_words = 150
        self.long_min_words = 300
    
    def adapt_length(self, response: str, preference: str = 'medium') -> str:
        """Adapt response length based on user preference"""
        if preference == 'short':
            return self._create_short_answer(response)
        elif preference == 'long':
            return self._create_long_answer(response)
        return response
    
    def _create_short_answer(self, response: str) -> str:
        """Create concise answer"""
        # Extract key points
        lines = response.split('\n')
        key_points = []
        
        # Look for main concepts (lines with formulas or key statements)
        for line in lines:
            if any(marker in line for marker in ['=', 'is', 'means', 'represents', '$']):
                key_points.append(line.strip())
                if len(' '.join(key_points).split()) >= self.short_max_words:
                    break
        
        if not key_points:
            # Just take first paragraph
            paragraphs = response.split('\n\n')
            return paragraphs[0] if paragraphs else response[:500]
        
        return '\n'.join(key_points)
    
    def _create_long_answer(self, response: str) -> str:
        """Ensure comprehensive answer"""
        # If already long enough, return as is
        if len(response.split()) >= self.long_min_words:
            return response
        
        # Add supplementary sections
        additions = [
            "\n\n**Additional Context:**\nThis concept is fundamental in physics...",
            "\n\n**Practical Applications:**\nThis principle is used in various real-world scenarios...",
            "\n\n**Common Misconceptions:**\nStudents often confuse this with..."
        ]
        
        return response + additions[0]  # Add at least one section
    
    def adapt_complexity(self, response: str, level: str = 'intermediate') -> Dict[str, Any]:
        """Adapt response complexity for different levels"""
        if level == 'beginner':
            return self._simplify_for_beginner(response)
        elif level == 'advanced':
            return self._enhance_for_advanced(response)
        
        return {'content': response, 'level': 'intermediate'}
    
    def _simplify_for_beginner(self, response: str) -> Dict[str, Any]:
        """Simplify for beginner level"""
        # Remove complex math notation
        simplified = re.sub(r'\$\$.*?\$\$', '[Mathematical Equation]', response, flags=re.DOTALL)
        simplified = re.sub(r'\$.*?\$', '[formula]', simplified)
        
        # Add beginner-friendly intro
        intro = "**Simple Explanation:**\n"
        
        return {
            'content': intro + simplified,
            'level': 'beginner',
            'note': 'Simplified explanation with reduced mathematical notation'
        }
    
    def _enhance_for_advanced(self, response: str) -> Dict[str, Any]:
        """Enhance for advanced level"""
        # Add technical depth markers
        enhancements = [
            "\n\n**Mathematical Rigor:**\nConsidering the formal treatment...",
            "\n\n**Advanced Considerations:**\nFrom a more rigorous perspective..."
        ]
        
        return {
            'content': response,  # Keep original technical content
            'level': 'advanced',
            'note': 'Full technical explanation with mathematical rigor'
        }
    
    def generate_follow_ups(self, topic: str, query: str) -> list:
        """Generate follow-up questions based on context"""
        follow_ups = []
        
        # Topic-based follow-ups
        topic_questions = {
            'mechanics': [
                "How does this apply to rotational motion?",
                "What happens in non-inertial reference frames?",
                "Can you derive this from first principles?"
            ],
            'quantum': [
                "How does the uncertainty principle apply here?",
                "What is the classical limit of this quantum effect?",
                "How does this relate to wave-particle duality?"
            ],
            'thermodynamics': [
                "What is the entropy change in this process?",
                "How does this relate to the second law?",
                "What about reversible vs irreversible processes?"
            ],
            'electromagnetism': [
                "How does this change in different media?",
                "What is the relationship with Maxwell's equations?",
                "How does relativity affect this phenomenon?"
            ]
        }
        
        # Find matching topic
        topic_lower = topic.lower()
        for key, questions in topic_questions.items():
            if key in topic_lower:
                follow_ups.extend(questions[:2])  # Add 2 questions
                break
        
        # Generic follow-ups if no match
        if not follow_ups:
            follow_ups = [
                "Can you explain this with a practical example?",
                "What are the real-world applications?",
                "How does this concept relate to other physics topics?"
            ]
        
        return follow_ups[:3]  # Return max 3 follow-ups
    
    def extract_key_concepts(self, response: str) -> list:
        """Extract key physics concepts from response"""
        # Simple keyword extraction
        physics_keywords = [
            'force', 'energy', 'momentum', 'velocity', 'acceleration',
            'electric', 'magnetic', 'field', 'wave', 'particle',
            'quantum', 'relativity', 'entropy', 'temperature', 'pressure'
        ]
        
        concepts = []
        response_lower = response.lower()
        
        for keyword in physics_keywords:
            if keyword in response_lower:
                concepts.append(keyword)
        
        return list(set(concepts))[:5]  # Return max 5 unique concepts
