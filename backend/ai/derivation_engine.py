"""
Simple step-by-step derivation engine for physics problems
"""
from typing import List, Dict, Any
import re


def break_into_steps(derivation_text: str) -> List[Dict[str, Any]]:
    """Break a derivation into logical steps"""
    # Simple step detection based on common physics patterns
    steps = []
    
    # Split by numbered steps or "Step" keywords
    step_patterns = [
        r'(?:Step\s*\d+[:.]?\s*)',
        r'(?:^\d+\.\s*)',
        r'(?:First|Second|Third|Then|Next|Finally)[,:]?\s*',
    ]
    
    # Try to split intelligently
    lines = derivation_text.split('\n')
    current_step = []
    step_number = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line starts a new step
        is_new_step = any(re.match(pattern, line, re.IGNORECASE) for pattern in step_patterns)
        
        if is_new_step and current_step:
            # Save previous step
            steps.append({
                'step_number': step_number,
                'content': ' '.join(current_step),
                'type': 'derivation'
            })
            step_number += 1
            current_step = [line]
        else:
            current_step.append(line)
    
    # Add last step
    if current_step:
        steps.append({
            'step_number': step_number,
            'content': ' '.join(current_step),
            'type': 'derivation'
        })
    
    # If no steps detected, create a single step
    if not steps:
        steps.append({
            'step_number': 1,
            'content': derivation_text,
            'type': 'explanation'
        })
    
    return steps


def format_derivation(steps: List[Dict[str, Any]], include_explanation: bool = True) -> str:
    """Format steps into readable derivation"""
    formatted = []
    
    for step in steps:
        step_text = f"**Step {step['step_number']}:**\n{step['content']}\n"
        formatted.append(step_text)
    
    return '\n'.join(formatted)


def simplify_for_level(text: str, level: str = 'intermediate') -> str:
    """Simplify explanation based on level"""
    if level == 'beginner':
        # Remove complex mathematical notation
        text = re.sub(r'\$.*?\$', '[equation]', text)
        # Add more basic language markers
        text = "In simple terms: " + text
    elif level == 'advanced':
        # Keep all technical details
        pass
    
    return text


def extract_key_equations(text: str) -> List[str]:
    """Extract LaTeX equations from text"""
    # Find equations between $ or $$
    equations = []
    
    # Inline equations
    inline = re.findall(r'\$(.*?)\$', text)
    equations.extend(inline)
    
    # Display equations
    display = re.findall(r'\$\$(.*?)\$\$', text, re.DOTALL)
    equations.extend(display)
    
    return equations


def generate_prerequisites(topic: str) -> List[str]:
    """Generate prerequisite topics (simplified)"""
    prerequisites_map = {
        'quantum': ['classical_mechanics', 'waves', 'linear_algebra'],
        'thermodynamics': ['classical_mechanics', 'calculus'],
        'electromagnetism': ['vectors', 'calculus', 'classical_mechanics'],
        'relativity': ['classical_mechanics', 'electromagnetism'],
        'mechanics': ['algebra', 'basic_physics'],
        'waves': ['trigonometry', 'mechanics'],
    }
    
    # Simple topic matching
    topic_lower = topic.lower()
    for key, prereqs in prerequisites_map.items():
        if key in topic_lower:
            return prereqs
    
    return ['basic_physics', 'mathematics']
