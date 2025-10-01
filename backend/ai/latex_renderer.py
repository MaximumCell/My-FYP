"""
LaTeX Equation Rendering Service for Physics AI Tutor

This module provides comprehensive LaTeX equation rendering capabilities including:
- Text-based LaTeX to multiple output formats (PNG, SVG, MathML, HTML)
- Physics equation generation and formatting
- Integration with matplotlib for high-quality rendering
- SymPy integration for symbolic mathematics
- Caching and optimization for performance

Author: Physics AI Tutor Team
Date: September 28, 2025
"""

import os
import io
import re
import hashlib
import logging
import base64
import time
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Core dependencies
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib.mathtext as mathtext
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# LaTeX processing
try:
    from latex2mathml.converter import convert as latex_to_mathml
except ImportError:
    latex_to_mathml = None

# Local imports
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger('ai.latex_renderer')

@dataclass
class LatexRenderConfig:
    """Configuration for LaTeX rendering operations"""
    dpi: int = 300
    font_size: int = 14
    figure_size: Tuple[float, float] = (8, 2)
    background_color: str = 'white'
    text_color: str = 'black'
    format_type: str = 'png'  # png, svg, pdf, mathml, html
    quality: str = 'high'  # low, medium, high
    cache_enabled: bool = True
    max_expression_length: int = 1000

@dataclass
class LatexRenderResult:
    """Result of LaTeX rendering operation"""
    success: bool
    content: Optional[str] = None  # Base64 encoded or raw content
    content_type: str = 'image/png'
    width: int = 0
    height: int = 0
    file_size: int = 0
    render_time: float = 0.0
    cache_hit: bool = False
    error_message: Optional[str] = None
    latex_source: str = ''
    format_type: str = 'png'

class PhysicsLatexRenderer:
    """
    Advanced LaTeX equation renderer specifically designed for physics content.
    
    Features:
    - Multiple output formats (PNG, SVG, MathML, HTML)
    - Physics-specific equation templates
    - High-quality rendering with matplotlib
    - Intelligent caching system
    - Async processing capabilities
    - Integration with SymPy for symbolic math
    """
    
    def __init__(self, config: Optional[LatexRenderConfig] = None, cache_enabled: bool = True):
        """
        Initialize the LaTeX renderer with configuration.
        
        Args:
            config: Rendering configuration options
            cache_enabled: Enable/disable caching system
        """
        self.config = config or LatexRenderConfig()
        self.cache_enabled = cache_enabled
        self.render_cache = {} if cache_enabled else None
        self.cache_max_size = 1000
        self.cache_ttl = timedelta(hours=24)
        
        # Statistics tracking
        self.stats = {
            'total_renders': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'total_render_time': 0.0,
            'formats_rendered': {},
            'most_common_equations': {},
            'service_start_time': datetime.now()
        }
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Physics equation templates
        self.physics_templates = self._load_physics_templates()
        
        # Initialize matplotlib settings
        self._setup_matplotlib()
        
        logger.info("✅ LaTeX renderer initialized with high-quality physics equation rendering")

    def _setup_matplotlib(self):
        """Configure matplotlib for optimal equation rendering"""
        plt.rcParams.update({
            'font.size': self.config.font_size,
            'text.usetex': False,  # Use mathtext instead of LaTeX for better compatibility
            'font.family': 'serif',
            'font.serif': ['Computer Modern Roman', 'Times', 'serif'],
            'mathtext.fontset': 'cm',  # Computer Modern fonts
            'figure.facecolor': self.config.background_color,
            'savefig.facecolor': self.config.background_color,
            'savefig.dpi': self.config.dpi,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1
        })

    def _load_physics_templates(self) -> Dict[str, str]:
        """Load common physics equation templates"""
        return {
            # Classical Mechanics
            'newton_second': r'F = ma',
            'kinetic_energy': r'K = \frac{1}{2}mv^2',
            'potential_energy_gravity': r'U = mgh',
            'work_energy': r'W = \Delta K = K_f - K_i',
            'momentum': r'p = mv',
            'impulse': r'J = \Delta p = F \Delta t',
            'angular_momentum': r'L = I\omega',
            'rotational_kinetic': r'K_{rot} = \frac{1}{2}I\omega^2',
            
            # Electromagnetism
            'coulombs_law': r"F = k\frac{q_1 q_2}{r^2}",
            'electric_field': r'E = \frac{F}{q}',
            'gauss_law': r'\oint \vec{E} \cdot d\vec{A} = \frac{Q_{enc}}{\epsilon_0}',
            'magnetic_force': r'\vec{F} = q(\vec{v} \times \vec{B})',
            'faradays_law': r'\varepsilon = -\frac{d\Phi_B}{dt}',
            'ohms_law': r'V = IR',
            'power_electrical': r'P = IV = I^2R = \frac{V^2}{R}',
            
            # Thermodynamics
            'ideal_gas_law': r'PV = nRT',
            'first_law_thermo': r'\Delta U = Q - W',
            'entropy': r'dS = \frac{dQ_{rev}}{T}',
            'efficiency': r'\eta = 1 - \frac{T_c}{T_h}',
            
            # Waves and Optics
            'wave_equation': r'y = A\sin(kx - \omega t + \phi)',
            'wave_speed': r'v = f\lambda',
            'snells_law': r'n_1\sin\theta_1 = n_2\sin\theta_2',
            'lens_equation': r'\frac{1}{f} = \frac{1}{d_o} + \frac{1}{d_i}',
            
            # Quantum Mechanics
            'schrodinger': r'i\hbar\frac{\partial\psi}{\partial t} = \hat{H}\psi',
            'uncertainty': r'\Delta x \Delta p \geq \frac{\hbar}{2}',
            'de_broglie': r'\lambda = \frac{h}{p}',
            'planck_energy': r'E = hf = \hbar\omega',
            
            # Relativity
            'time_dilation': r"\Delta t = \frac{\Delta t_0}{\sqrt{1-\frac{v^2}{c^2}}}",
            'mass_energy': r'E = mc^2',
            'lorentz_factor': r"\gamma = \frac{1}{\sqrt{1-\frac{v^2}{c^2}}}",
            
            # Mathematical Physics
            'gradient': r'\nabla f = \frac{\partial f}{\partial x}\hat{i} + \frac{\partial f}{\partial y}\hat{j} + \frac{\partial f}{\partial z}\hat{k}',
            'divergence': r'\nabla \cdot \vec{F} = \frac{\partial F_x}{\partial x} + \frac{\partial F_y}{\partial y} + \frac{\partial F_z}{\partial z}',
            'curl': r'\nabla \times \vec{F} = \left(\frac{\partial F_z}{\partial y} - \frac{\partial F_y}{\partial z}\right)\hat{i} + \left(\frac{\partial F_x}{\partial z} - \frac{\partial F_z}{\partial x}\right)\hat{j} + \left(\frac{\partial F_y}{\partial x} - \frac{\partial F_x}{\partial y}\right)\hat{k}',
            'laplacian': r'\nabla^2 f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2} + \frac{\partial^2 f}{\partial z^2}'
        }
    
    def render_latex(self, latex_expression: str, output_format: str = 'png') -> LatexRenderResult:
        """
        Main method to render LaTeX expressions in various formats
        
        Args:
            latex_expression: LaTeX string to render
            output_format: Output format ('png', 'svg', 'html', 'mathml')
            
        Returns:
            LatexRenderResult with rendered content
        """
        try:
            # Clean and validate input
            clean_latex = self._preprocess_latex(latex_expression)
            validation = self.validate_latex(clean_latex)
            
            if not validation.get('valid', False):
                return LatexRenderResult(
                    success=False,
                    error_message=f"Invalid LaTeX: {validation.get('error', 'Unknown validation error')}",
                    latex_source=latex_expression,
                    format_type=output_format
                )
            
            # Check cache
            cache_key = self._get_cache_key(clean_latex, output_format)
            if self.cache_enabled and self.render_cache and cache_key in self.render_cache:
                cached_result, timestamp = self.render_cache[cache_key]
                if datetime.now() - timestamp < self.cache_ttl:
                    self.stats['cache_hits'] += 1
                    return cached_result
            
            # Clean expired cache entries periodically
            if self.stats['total_renders'] % 100 == 0:
                self._clean_expired_cache()
            
            # Route to appropriate render method
            if output_format.lower() == 'png':
                result = self._render_to_png(clean_latex)
            elif output_format.lower() == 'svg':
                result = self._render_to_svg(clean_latex)
            elif output_format.lower() == 'html':
                result = self._render_to_html(clean_latex)
            elif output_format.lower() == 'mathml':
                result = self._render_to_mathml(clean_latex)
            else:
                return LatexRenderResult(
                    success=False,
                    error_message=f"Unsupported output format: {output_format}",
                    latex_source=latex_expression,
                    format_type=output_format
                )
            
            # Update statistics
            self.stats['total_renders'] += 1
            if result.success:
                if self.cache_enabled and self.render_cache is not None:
                    self.render_cache[cache_key] = (result, datetime.now())
                self.stats['cache_misses'] += 1
                self.stats['total_render_time'] += result.render_time or 0
                format_count = self.stats['formats_rendered'].get(output_format, 0)
                self.stats['formats_rendered'][output_format] = format_count + 1
            else:
                self.stats['errors'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Render error: {e}")
            self.stats['errors'] += 1
            return LatexRenderResult(
                success=False,
                error_message=f"Rendering failed: {str(e)}",
                latex_source=latex_expression,
                format_type=output_format
            )
    
    def _generate_cache_key(self, latex_expression: str, config: LatexRenderConfig) -> str:
        """Generate a unique cache key for the equation and config"""
        content = f"{latex_expression}_{config.format_type}_{config.dpi}_{config.font_size}_{config.quality}"
        return hashlib.md5(content.encode()).hexdigest()

    def _clean_expired_cache(self):
        """Remove expired entries from cache"""
        if not self.cache_enabled or not self.render_cache:
            return
            
        current_time = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.render_cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        for key in expired_keys:
            del self.render_cache[key]
        
        # Also limit cache size
        if len(self.render_cache) > self.cache_max_size:
            # Remove oldest entries
            sorted_items = sorted(self.render_cache.items(), key=lambda x: x[1][1])
            for key, _ in sorted_items[:len(self.render_cache) - self.cache_max_size]:
                del self.render_cache[key]

    def _preprocess_latex(self, latex_expression: str) -> str:
        """
        Preprocess LaTeX expression for optimal rendering
        
        Args:
            latex_expression: Raw LaTeX string
            
        Returns:
            Processed LaTeX string
        """
        # Remove common LaTeX document commands that aren't needed
        latex_expression = re.sub(r'\\documentclass.*?\n', '', latex_expression)
        latex_expression = re.sub(r'\\begin\{document\}', '', latex_expression)
        latex_expression = re.sub(r'\\end\{document\}', '', latex_expression)
        latex_expression = re.sub(r'\\usepackage.*?\n', '', latex_expression)
        
        # Ensure math mode
        latex_expression = latex_expression.strip()
        if not (latex_expression.startswith('$') or latex_expression.startswith('\\[')):
            if '\\begin{' in latex_expression or '\\end{' in latex_expression:
                # Already in display mode
                latex_expression = f'$${latex_expression}$$'
            else:
                # Inline math mode
                latex_expression = f'${latex_expression}$'
        
        # Clean up common issues
        latex_expression = latex_expression.replace('\\\\', '\\')  # Remove double backslashes
        latex_expression = re.sub(r'\s+', ' ', latex_expression)  # Normalize whitespace
        
        return latex_expression

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
    
    def _render_to_png(self, latex_expression: str) -> LatexRenderResult:
        """
        Render LaTeX expression to PNG format using matplotlib
        
        Args:
            latex_expression: LaTeX string to render
            
        Returns:
            LatexRenderResult with PNG data
        """
        try:
            start_time = datetime.now()
            
            # Create figure with appropriate size
            fig, ax = plt.subplots(figsize=self.config.figure_size)
            ax.axis('off')
            
            # Render the equation
            ax.text(0.5, 0.5, latex_expression, 
                   fontsize=self.config.font_size,
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   color=self.config.text_color)
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=self.config.dpi, 
                       bbox_inches='tight', pad_inches=0.1,
                       facecolor=self.config.background_color)
            plt.close(fig)
            
            buffer.seek(0)
            image_data = buffer.getvalue()
            
            # Get image dimensions
            with Image.open(io.BytesIO(image_data)) as img:
                width, height = img.size
            
            # Encode to base64
            encoded_data = base64.b64encode(image_data).decode('utf-8')
            
            render_time = (datetime.now() - start_time).total_seconds()
            
            return LatexRenderResult(
                success=True,
                content=encoded_data,
                content_type='image/png',
                width=width,
                height=height,
                file_size=len(image_data),
                render_time=render_time,
                latex_source=latex_expression,
                format_type='png'
            )
            
        except Exception as e:
            logger.error(f"PNG rendering failed: {e}")
            return LatexRenderResult(
                success=False,
                error_message=f"PNG rendering error: {str(e)}",
                latex_source=latex_expression,
                format_type='png'
            )

    def _render_to_svg(self, latex_expression: str) -> LatexRenderResult:
        """
        Render LaTeX expression to SVG format
        
        Args:
            latex_expression: LaTeX string to render
            
        Returns:
            LatexRenderResult with SVG data
        """
        try:
            start_time = datetime.now()
            
            # Create figure
            fig, ax = plt.subplots(figsize=self.config.figure_size)
            ax.axis('off')
            
            # Render the equation
            ax.text(0.5, 0.5, latex_expression,
                   fontsize=self.config.font_size,
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   color=self.config.text_color)
            
            # Save to SVG buffer
            buffer = io.StringIO()
            plt.savefig(buffer, format='svg', bbox_inches='tight',
                       facecolor=self.config.background_color)
            plt.close(fig)
            
            svg_content = buffer.getvalue()
            render_time = (datetime.now() - start_time).total_seconds()
            
            return LatexRenderResult(
                success=True,
                content=svg_content,
                content_type='image/svg+xml',
                file_size=len(svg_content.encode('utf-8')),
                render_time=render_time,
                latex_source=latex_expression,
                format_type='svg'
            )
            
        except Exception as e:
            logger.error(f"SVG rendering failed: {e}")
            return LatexRenderResult(
                success=False,
                error_message=f"SVG rendering error: {str(e)}",
                latex_source=latex_expression,
                format_type='svg'
            )

    def _render_to_mathml(self, latex_expression: str) -> LatexRenderResult:
        """
        Convert LaTeX expression to MathML format
        
        Args:
            latex_expression: LaTeX string to convert
            
        Returns:
            LatexRenderResult with MathML data
        """
        if not latex_to_mathml:
            return LatexRenderResult(
                success=False,
                error_message="latex2mathml package not available",
                latex_source=latex_expression,
                format_type='mathml'
            )
            
        try:
            start_time = datetime.now()
            
            # Clean the expression for MathML conversion
            clean_latex = latex_expression.strip('$')
            
            # Convert to MathML
            mathml_content = latex_to_mathml(clean_latex)
            
            render_time = (datetime.now() - start_time).total_seconds()
            
            return LatexRenderResult(
                success=True,
                content=mathml_content,
                content_type='application/mathml+xml',
                file_size=len(mathml_content.encode('utf-8')),
                render_time=render_time,
                latex_source=latex_expression,
                format_type='mathml'
            )
            
        except Exception as e:
            logger.error(f"MathML conversion failed: {e}")
            return LatexRenderResult(
                success=False,
                error_message=f"MathML conversion error: {str(e)}",
                latex_source=latex_expression,
                format_type='mathml'
            )

    def _render_to_html(self, latex_expression: str) -> LatexRenderResult:
        """
        Create HTML with MathJax for LaTeX expression
        
        Args:
            latex_expression: LaTeX string to embed
            
        Returns:
            LatexRenderResult with HTML data
        """
        try:
            start_time = datetime.now()
            
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Physics Equation</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }}
        }};
    </script>
    <style>
        body {{
            font-family: 'Computer Modern', serif;
            background-color: {self.config.background_color};
            color: {self.config.text_color};
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .equation {{
            font-size: {self.config.font_size * 1.2}px;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            background: white;
        }}
    </style>
</head>
<body>
    <div class="equation">
        {latex_expression}
    </div>
</body>
</html>
"""
            
            render_time = (datetime.now() - start_time).total_seconds()
            
            return LatexRenderResult(
                success=True,
                content=html_template,
                content_type='text/html',
                file_size=len(html_template.encode('utf-8')),
                render_time=render_time,
                latex_source=latex_expression,
                format_type='html'
            )
            
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            return LatexRenderResult(
                success=False,
                error_message=f"HTML generation error: {str(e)}",
                latex_source=latex_expression,
                format_type='html'
            )
    
    def validate_latex(self, latex_expression: str) -> Dict[str, Any]:
        """
        Validate LaTeX syntax and physics notation
        
        Args:
            latex_expression: LaTeX string to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Clean the expression
            clean_expr = latex_expression.strip().strip('$')
            
            # Check for balanced delimiters
            braces = clean_expr.count('{') - clean_expr.count('}')
            parentheses = clean_expr.count('(') - clean_expr.count(')')
            brackets = clean_expr.count('[') - clean_expr.count(']')
            
            if braces != 0:
                return {
                    'valid': False,
                    'error': 'Unbalanced braces',
                    'details': f'Difference: {braces}'
                }
            
            if parentheses != 0:
                return {
                    'valid': False,
                    'error': 'Unbalanced parentheses',
                    'details': f'Difference: {parentheses}'
                }
            
            if brackets != 0:
                return {
                    'valid': False,
                    'error': 'Unbalanced brackets',
                    'details': f'Difference: {brackets}'
                }
            
            # Try to parse with SymPy if it's a mathematical expression
            sympy_valid = False
            try:
                from sympy import sympify
                expr = sympify(clean_expr, evaluate=False)
                sympy_valid = True
            except ImportError:
                # SymPy not available
                pass
            except Exception:
                # Invalid expression
                pass
            
            # Check for physics-specific notation
            physics_commands = [
                r'\\vec', r'\\hat', r'\\dot', r'\\ddot', r'\\partial',
                r'\\nabla', r'\\Delta', r'\\hbar', r'\\epsilon_0',
                r'\\mu_0', r'\\sigma', r'\\rho', r'\\omega', r'\\lambda'
            ]
            
            has_physics = any(cmd in clean_expr for cmd in physics_commands)
            
            return {
                'valid': True,
                'sympy_compatible': sympy_valid,
                'has_physics_notation': has_physics,
                'cleaned_expression': clean_expr
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation failed: {str(e)}'
            }

    def create_physics_equation(self, equation_type: str, **parameters) -> LatexRenderResult:
        """
        Create physics equation from template
        
        Args:
            equation_type: Type of physics equation
            **parameters: Parameters for the template
            
        Returns:
            LatexRenderResult with rendered equation
        """
        try:
            if equation_type not in self.physics_templates:
                return LatexRenderResult(
                    success=False,
                    error_message=f"Unknown equation type: {equation_type}",
                    format_type='template_error'
                )
            
            # Get template
            template = self.physics_templates[equation_type]
            
            # Substitute parameters only if template has placeholders
            if '{' in template and '}' in template:
                latex_expression = template.format(**parameters)
            else:
                # Template is fixed - no parameters needed
                latex_expression = template
            
            # Render using default format
            return self.render_latex(latex_expression)
            
        except KeyError as e:
            return LatexRenderResult(
                success=False,
                error_message=f"Missing parameter: {str(e)}",
                format_type='parameter_error'
            )
        except Exception as e:
            return LatexRenderResult(
                success=False,
                error_message=f"Template error: {str(e)}",
                format_type='template_error'
            )

    def process_response_equations(self, response_text: str) -> Dict[str, Any]:
        """
        Process and render equations found in AI response text
        
        Args:
            response_text: AI response containing LaTeX equations
            
        Returns:
            Dictionary with processed equations and metadata
        """
        import re
        
        try:
            # Find LaTeX expressions in response text (between $ symbols or \\[ \\] blocks)
            latex_patterns = [
                r'\$\$([^$]+)\$\$',  # Display math $$...$$
                r'\$([^$]+)\$',      # Inline math $...$
                r'\\\\?\[([^\]]+)\\\\?\]',  # Display math \[...\] or \\[...\\]
                r'\\\\?\(([^)]+)\\\\?\)',   # Inline math \(...\) or \\(...\\)
            ]
            
            equations_found = []
            rendered_equations = {}
            
            for i, pattern in enumerate(latex_patterns):
                matches = re.finditer(pattern, response_text, re.MULTILINE | re.DOTALL)
                for match in matches:
                    equation = match.group(1).strip()
                    if equation and equation not in [eq['original'] for eq in equations_found]:
                        equations_found.append({
                            'original': equation,
                            'type': 'display' if i in [0, 2] else 'inline',
                            'match_text': match.group(0)
                        })
            
            # Render found equations
            successful_renders = 0
            for j, eq_info in enumerate(equations_found):
                equation = eq_info['original']
                result = self.render_latex(equation, output_format='png')
                
                rendered_equations[f"equation_{j}"] = {
                    'original_latex': equation,
                    'type': eq_info['type'],
                    'match_text': eq_info['match_text'],
                    'render_result': result,
                    'success': result.success
                }
                
                if result.success:
                    successful_renders += 1
            
            # Generate processing summary
            processing_summary = {
                'equations_found': len(equations_found),
                'successful_renders': successful_renders,
                'processing_time': time.time(),
                'success_rate': successful_renders / len(equations_found) if equations_found else 1.0
            }
            
            return {
                'success': True,
                'equations': rendered_equations,
                'summary': processing_summary,
                'processed_text': response_text  # Could modify text to include rendered images
            }
            
        except Exception as e:
            logger.error(f"Error processing response equations: {e}")
            return {
                'success': False,
                'error_message': str(e),
                'equations': {},
                'summary': {'equations_found': 0, 'successful_renders': 0}
            }

    def batch_render(self, expressions: List[str], 
                    output_format: str = 'png') -> Dict[str, LatexRenderResult]:
        """
        Render multiple LaTeX expressions efficiently
        
        Args:
            expressions: List of LaTeX expressions
            output_format: Output format for all expressions
            
        Returns:
            Dictionary mapping expressions to results
        """
        results = {}
        start_time = datetime.now()
        
        logger.info(f"Starting batch render of {len(expressions)} expressions")
        
        for i, expr in enumerate(expressions):
            try:
                result = self.render_latex(expr, output_format)
                results[f"expr_{i}"] = result
                
                if result.success and self.cache_enabled:
                    # Cache successful renders
                    cache_key = self._get_cache_key(expr, output_format)
                    self.render_cache[cache_key] = result
                    
            except Exception as e:
                logger.error(f"Batch render failed for expression {i}: {e}")
                results[f"expr_{i}"] = LatexRenderResult(
                    success=False,
                    error_message=str(e),
                    latex_source=expr,
                    format_type=output_format
                )
        
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Batch render completed in {total_time:.2f}s")
        
        return results

    def get_render_stats(self) -> Dict[str, Any]:
        """
        Get rendering performance statistics
        
        Returns:
            Dictionary with performance metrics
        """
        cache_size = len(self.render_cache) if self.cache_enabled else 0
        
        return {
            'cache_enabled': self.cache_enabled,
            'cache_size': cache_size,
            'supported_formats': ['png', 'svg', 'mathml', 'html'],
            'physics_templates': len(self.physics_templates),
            'available_templates': list(self.physics_templates.keys()),
            'config': {
                'dpi': self.config.dpi,
                'font_size': self.config.font_size,
                'figure_size': self.config.figure_size
            }
        }

    def clear_cache(self) -> bool:
        """
        Clear the rendering cache
        
        Returns:
            True if cache was cleared successfully
        """
        try:
            if self.cache_enabled:
                cleared_items = len(self.render_cache)
                self.render_cache.clear()
                logger.info(f"Cleared {cleared_items} items from render cache")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def _get_cache_key(self, latex_expression: str, output_format: str) -> str:
        """Generate cache key for LaTeX expression and format"""
        content = f"{latex_expression}:{output_format}:{self.config.dpi}:{self.config.font_size}"
        return hashlib.md5(content.encode()).hexdigest()

# Factory function for easy instantiation
def create_physics_latex_renderer(cache_enabled: bool = True,
                                dpi: int = 300,
                                font_size: int = 14) -> PhysicsLatexRenderer:
    """
    Factory function to create a configured PhysicsLatexRenderer
    
    Args:
        cache_enabled: Enable rendering cache
        dpi: Resolution for image rendering
        font_size: Base font size for equations
        
    Returns:
        Configured PhysicsLatexRenderer instance
    """
    config = LatexRenderConfig(dpi=dpi, font_size=font_size)
    return PhysicsLatexRenderer(config=config, cache_enabled=cache_enabled)

# Initialize global renderer instance
physics_latex_renderer = create_physics_latex_renderer()

# Convenience functions for backward compatibility and easy usage
def render_physics_equation(latex_expression: str, output_format: str = 'png') -> LatexRenderResult:
    """Convenience function to render a physics equation"""
    return physics_latex_renderer.render_latex(latex_expression, output_format)

def create_physics_template(equation_type: str, **parameters) -> LatexRenderResult:
    """Convenience function to create physics equation from template"""
    return physics_latex_renderer.create_physics_equation(equation_type, **parameters)