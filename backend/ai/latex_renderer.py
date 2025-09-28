"""
LaTeX Equation Rendering System for Physics Tutor
Handles mathematical equation rendering and formula processing
"""

import os
import re
import base64
from typing import List, Dict, Optional, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from io import BytesIO
import sympy as sp
from sympy import latex, sympify, parse_expr
from sympy.parsing.latex import parse_latex
import json

class LaTeXRenderer:
    def __init__(self):
        # Configure matplotlib for LaTeX rendering
        plt.rcParams.update({
            'text.usetex': False,  # Use mathtext instead of LaTeX for compatibility
            'font.family': 'serif',
            'font.serif': ['Computer Modern Roman'],
            'font.size': 12,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
        
        # Common physics symbols and their LaTeX representations
        self.physics_symbols = {
            'velocity': r'v',
            'acceleration': r'a', 
            'force': r'F',
            'mass': r'm',
            'energy': r'E',
            'momentum': r'p',
            'angular_momentum': r'L',
            'torque': r'\tau',
            'power': r'P',
            'voltage': r'V',
            'current': r'I',
            'resistance': r'R',
            'capacitance': r'C',
            'inductance': r'L',
            'frequency': r'f',
            'wavelength': r'\lambda',
            'amplitude': r'A',
            'electric_field': r'E',
            'magnetic_field': r'B',
            'electric_potential': r'\phi',
            'charge': r'q',
            'temperature': r'T',
            'entropy': r'S',
            'pressure': r'P',
            'volume': r'V',
            'gravitational_constant': r'G',
            'planck_constant': r'h',
            'speed_of_light': r'c',
            'boltzmann_constant': r'k_B'
        }
    
    def extract_latex_equations(self, text: str) -> List[Dict]:
        """Extract LaTeX equations from text"""
        equations = []
        
        # Pattern for display equations $$...$$
        display_pattern = r'\$\$(.*?)\$\$'
        display_matches = re.findall(display_pattern, text, re.DOTALL)
        
        for match in display_matches:
            equations.append({
                'type': 'display',
                'latex': match.strip(),
                'original': f'$${match}$$'
            })
        
        # Pattern for inline equations $...$
        inline_pattern = r'\$([^$]+)\$'
        inline_matches = re.findall(inline_pattern, text)
        
        for match in inline_matches:
            # Skip if it's part of a display equation
            if f'$${match}$$' not in text:
                equations.append({
                    'type': 'inline',
                    'latex': match.strip(),
                    'original': f'${match}$'
                })
        
        return equations
    
    def validate_latex(self, latex_code: str) -> Dict:
        """Validate LaTeX syntax and check for common physics notation"""
        try:
            # Try to parse with SymPy (if possible)
            try:
                expr = sympify(latex_code, evaluate=False)
                return {
                    'valid': True,
                    'type': 'mathematical_expression',
                    'sympy_expr': str(expr),
                    'message': 'Valid mathematical expression'
                }
            except:
                pass
            
            # Basic LaTeX syntax validation
            # Check for balanced braces
            open_braces = latex_code.count('{')
            close_braces = latex_code.count('}')
            
            if open_braces != close_braces:
                return {
                    'valid': False,
                    'error': 'Unbalanced braces',
                    'message': f'Found {open_braces} opening braces and {close_braces} closing braces'
                }
            
            # Check for common LaTeX commands
            valid_commands = [
                r'\\frac', r'\\sqrt', r'\\sum', r'\\int', r'\\prod',
                r'\\alpha', r'\\beta', r'\\gamma', r'\\delta', r'\\epsilon',
                r'\\theta', r'\\lambda', r'\\mu', r'\\pi', r'\\sigma',
                r'\\tau', r'\\phi', r'\\psi', r'\\omega',
                r'\\partial', r'\\nabla', r'\\infty', r'\\approx',
                r'\\cdot', r'\\times', r'\\div', r'\\pm', r'\\mp'
            ]
            
            return {
                'valid': True,
                'type': 'latex_expression',
                'message': 'Valid LaTeX syntax'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'message': 'LaTeX validation failed'
            }
    
    def render_equation_to_image(self, latex_code: str, 
                                output_format: str = 'png',
                                dpi: int = 300,
                                font_size: int = 14) -> Dict:
        """Render LaTeX equation to image"""
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.axis('off')
            
            # Render equation
            ax.text(0.5, 0.5, f'${latex_code}$', 
                   fontsize=font_size, 
                   ha='center', va='center',
                   transform=ax.transAxes)
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format=output_format, dpi=dpi, 
                       bbox_inches='tight', pad_inches=0.1,
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            # Encode to base64 for web display
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            
            return {
                'success': True,
                'image_base64': image_base64,
                'image_format': output_format,
                'latex_code': latex_code
            }
            
        except Exception as e:
            plt.close('all')  # Clean up any open figures
            return {
                'success': False,
                'error': str(e),
                'latex_code': latex_code
            }
    
    def create_step_by_step_derivation(self, steps: List[Dict]) -> Dict:
        """Create visual step-by-step derivation"""
        try:
            # Create figure for multi-step derivation
            num_steps = len(steps)
            fig, axes = plt.subplots(num_steps, 1, figsize=(12, 2*num_steps))
            
            if num_steps == 1:
                axes = [axes]
            
            for i, step in enumerate(steps):
                ax = axes[i]
                ax.axis('off')
                
                # Step number and description
                step_text = f"Step {i+1}: {step.get('description', '')}"
                ax.text(0.05, 0.8, step_text, fontsize=12, fontweight='bold',
                       transform=ax.transAxes)
                
                # Equation
                equation = step.get('equation', '')
                ax.text(0.05, 0.4, f'${equation}$', fontsize=14,
                       transform=ax.transAxes)
                
                # Explanation
                explanation = step.get('explanation', '')
                if explanation:
                    ax.text(0.05, 0.1, explanation, fontsize=10,
                           transform=ax.transAxes, wrap=True)
                
                # Add connecting arrow (except for last step)
                if i < num_steps - 1:
                    ax.annotate('', xy=(0.5, -0.1), xytext=(0.5, 0.05),
                               arrowprops=dict(arrowstyle='->', lw=2, color='blue'),
                               transform=ax.transAxes)
            
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, 
                       bbox_inches='tight', pad_inches=0.2,
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            # Encode to base64
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            
            return {
                'success': True,
                'image_base64': image_base64,
                'num_steps': num_steps,
                'derivation_type': 'step_by_step'
            }
            
        except Exception as e:
            plt.close('all')
            return {
                'success': False,
                'error': str(e),
                'num_steps': len(steps)
            }
    
    def format_physics_equation(self, equation: str, 
                              variables: Dict = None,
                              units: Dict = None) -> Dict:
        """Format physics equation with proper notation and units"""
        try:
            # Replace common physics symbols
            formatted_eq = equation
            for symbol, latex_symbol in self.physics_symbols.items():
                formatted_eq = formatted_eq.replace(symbol, latex_symbol)
            
            # Add variable definitions if provided
            definitions = []
            if variables:
                for var, description in variables.items():
                    unit_str = f" ({units[var]})" if units and var in units else ""
                    definitions.append(f"${var}$ = {description}{unit_str}")
            
            return {
                'formatted_equation': formatted_eq,
                'variable_definitions': definitions,
                'original_equation': equation
            }
            
        except Exception as e:
            return {
                'formatted_equation': equation,
                'variable_definitions': [],
                'original_equation': equation,
                'error': str(e)
            }
    
    def create_formula_reference_card(self, formulas: List[Dict]) -> Dict:
        """Create a visual reference card for physics formulas"""
        try:
            num_formulas = len(formulas)
            fig, ax = plt.subplots(figsize=(10, max(6, num_formulas * 1.5)))
            ax.axis('off')
            
            # Title
            ax.text(0.5, 0.95, 'Physics Formula Reference', 
                   fontsize=16, fontweight='bold', ha='center',
                   transform=ax.transAxes)
            
            # Draw formulas
            y_pos = 0.85
            for i, formula in enumerate(formulas):
                # Formula name
                name = formula.get('name', f'Formula {i+1}')
                ax.text(0.05, y_pos, name, fontsize=12, fontweight='bold',
                       transform=ax.transAxes)
                
                # Formula equation
                equation = formula.get('equation', '')
                ax.text(0.05, y_pos - 0.04, f'${equation}$', fontsize=14,
                       transform=ax.transAxes)
                
                # Description
                description = formula.get('description', '')
                if description:
                    ax.text(0.05, y_pos - 0.08, description, fontsize=10,
                           transform=ax.transAxes)
                
                # Add separator line
                if i < num_formulas - 1:
                    ax.axhline(y=y_pos - 0.12, xmin=0.05, xmax=0.95, 
                              color='gray', linestyle='-', alpha=0.5,
                              transform=ax.transAxes)
                
                y_pos -= 0.15
            
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300,
                       bbox_inches='tight', pad_inches=0.2,
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            # Encode to base64
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            
            return {
                'success': True,
                'image_base64': image_base64,
                'num_formulas': num_formulas,
                'reference_type': 'formula_card'
            }
            
        except Exception as e:
            plt.close('all')
            return {
                'success': False,
                'error': str(e),
                'num_formulas': len(formulas)
            }
    
    def process_response_equations(self, response_text: str) -> Dict:
        """Process all equations in a response text"""
        try:
            # Extract equations
            equations = self.extract_latex_equations(response_text)
            
            processed_equations = []
            for eq in equations:
                # Validate equation
                validation = self.validate_latex(eq['latex'])
                
                # Render to image if valid
                if validation['valid']:
                    image_result = self.render_equation_to_image(eq['latex'])
                    eq.update(image_result)
                
                eq['validation'] = validation
                processed_equations.append(eq)
            
            return {
                'success': True,
                'equations': processed_equations,
                'total_equations': len(equations),
                'response_text': response_text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'equations': [],
                'total_equations': 0,
                'response_text': response_text
            }

# Initialize LaTeX renderer
latex_renderer = LaTeXRenderer()


def render_physics_equations(text: str) -> Dict:
    """Convenience function to render all physics equations in text"""
    return latex_renderer.process_response_equations(text)


def create_derivation_visual(steps: List[Dict]) -> Dict:
    """Convenience function to create step-by-step derivation visual"""
    return latex_renderer.create_step_by_step_derivation(steps)


def format_equation_with_units(equation: str, variables: Dict = None, units: Dict = None) -> Dict:
    """Convenience function to format physics equation with proper notation"""
    return latex_renderer.format_physics_equation(equation, variables, units)