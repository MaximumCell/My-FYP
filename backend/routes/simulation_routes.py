"""
Modern Physics Simulation Routes
Flask routes for Matter.js and p5.js physics simulations + legacy plotting routes
"""

from flask import Blueprint, request, jsonify, send_file
from simulation.experiments.matter_physics import generate_matter_simulation
from simulation.experiments.p5_physics import generate_p5_simulation
from simulation.plot_2d import plot_equation_2d, plot_from_csv_columns
from simulation.plot_3d import plot_surface, plot_parametric, plot_from_csv_xyz
from simulation.pygame_sim import run_particle_simulation
import os

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/api/simulation/matter', methods=['POST', 'OPTIONS'])
def matter_simulation():
    """Generate Matter.js simulation configuration"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    try:
        data = request.get_json()
        simulation_type = data.get('type', 'pendulum')
        params = data.get('parameters', data.get('params', {}))  # Accept both 'parameters' and 'params'
        
        # Validate simulation type
        valid_types = ['pendulum', 'collision', 'spring', 'projectile']
        if simulation_type not in valid_types:
            return jsonify({
                'error': f'Invalid simulation type. Must be one of: {valid_types}'
            }), 400
        
        # Generate simulation configuration
        config = generate_matter_simulation(simulation_type, params)
        
        return jsonify({
            'success': True,
            'simulation': config
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@simulation_bp.route('/api/simulation/p5', methods=['POST', 'OPTIONS'])
def p5_simulation():
    """Generate p5.js simulation configuration"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    try:
        data = request.get_json()
        simulation_type = data.get('type', 'electric_field')
        # Accept both 'params' and 'parameters' for flexibility
        params = data.get('parameters', data.get('params', {}))
        
        # Validate simulation type
        valid_types = ['electric_field', 'magnetic_field', 'wave_motion', 'oscillation', 'em_wave']
        if simulation_type not in valid_types:
            return jsonify({
                'error': f'Invalid simulation type. Must be one of: {valid_types}'
            }), 400
        
        # Generate simulation configuration
        config = generate_p5_simulation(simulation_type, params)
        
        return jsonify({
            'success': True,
            'simulation': config
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@simulation_bp.route('/api/simulation/types', methods=['GET'])
def get_simulation_types():
    """Get available simulation types"""
    return jsonify({
        'matter_js': {
            'category': 'Mechanical Physics',
            'simulations': [
                {
                    'id': 'pendulum',
                    'name': 'Pendulum',
                    'description': 'Simple pendulum with adjustable parameters',
                    'concepts': ['Periodic Motion', 'Energy Conservation', 'SHM']
                },
                {
                    'id': 'collision',
                    'name': 'Collisions',
                    'description': 'Multi-ball collision system',
                    'concepts': ['Momentum Conservation', 'Kinetic Energy', 'Elastic Collisions']
                },
                {
                    'id': 'spring',
                    'name': 'Spring-Mass System',
                    'description': 'Spring oscillator with damping',
                    'concepts': ['Hooke\'s Law', 'SHM', 'Damped Oscillations']
                },
                {
                    'id': 'projectile',
                    'name': 'Projectile Motion',
                    'description': 'Projectile with air resistance',
                    'concepts': ['Kinematics', 'Gravity', 'Air Resistance']
                }
            ]
        },
        'p5_js': {
            'category': 'Electromagnetic & Wave Physics',
            'simulations': [
                {
                    'id': 'electric_field',
                    'name': 'Electric Field',
                    'description': 'Electric field visualization and interactions',
                    'concepts': ['Coulomb\'s Law', 'Electric Field', 'Field Lines']
                },
                {
                    'id': 'magnetic_field',
                    'name': 'Magnetic Field',
                    'description': 'Charged particle motion in magnetic fields',
                    'concepts': ['Lorentz Force', 'Cyclotron Motion', 'Magnetic Field']
                },
                {
                    'id': 'wave_motion',
                    'name': 'Wave Motion',
                    'description': 'Wave propagation and interference',
                    'concepts': ['Wave Equation', 'Interference', 'Superposition']
                },
                {
                    'id': 'oscillation',
                    'name': 'Coupled Oscillators',
                    'description': 'System of coupled harmonic oscillators',
                    'concepts': ['Normal Modes', 'Beats', 'Resonance']
                },
                {
                    'id': 'em_wave',
                    'name': 'Electromagnetic Wave',
                    'description': 'EM wave with electric and magnetic components',
                    'concepts': ['Maxwell\'s Equations', 'Polarization', 'EM Radiation']
                }
            ]
        }
    })

@simulation_bp.route('/api/simulation/presets/<simulation_type>', methods=['GET'])
def get_simulation_presets(simulation_type):
    """Get preset configurations for a simulation type"""
    
    presets = {
        # Matter.js presets
        'pendulum': {
            'simple': {'length': 150, 'mass': 1, 'gravity': 0.8, 'angle': 30},
            'heavy': {'length': 200, 'mass': 2.5, 'gravity': 0.8, 'angle': 45},
            'long': {'length': 300, 'mass': 1, 'gravity': 0.8, 'angle': 60},
            'low_gravity': {'length': 200, 'mass': 1, 'gravity': 0.3, 'angle': 45}
        },
        'collision': {
            'few_balls': {'ballCount': 4, 'restitution': 0.9, 'friction': 0.05},
            'many_balls': {'ballCount': 12, 'restitution': 0.8, 'friction': 0.1},
            'inelastic': {'ballCount': 6, 'restitution': 0.4, 'friction': 0.2},
            'frictionless': {'ballCount': 8, 'restitution': 1.0, 'friction': 0.0}
        },
        'spring': {
            'soft': {'springConstant': 0.02, 'mass': 1, 'damping': 0.99},
            'stiff': {'springConstant': 0.08, 'mass': 1.5, 'damping': 0.98},
            'heavy_mass': {'springConstant': 0.05, 'mass': 3, 'damping': 0.97},
            'overdamped': {'springConstant': 0.05, 'mass': 1.5, 'damping': 0.9}
        },
        'projectile': {
            'optimal_angle': {'velocity': 15, 'angle': 45, 'gravity': 0.5},
            'high_trajectory': {'velocity': 20, 'angle': 75, 'gravity': 0.5},
            'low_trajectory': {'velocity': 18, 'angle': 15, 'gravity': 0.5},
            'with_air_resistance': {'velocity': 15, 'angle': 45, 'gravity': 0.5, 'airResistance': 0.05}
        },
        
        # p5.js presets
        'electric_field': {
            'dipole': {'charges': 2, 'fieldStrength': 1.5, 'showField': True},
            'quadrupole': {'charges': 4, 'fieldStrength': 1.0, 'showField': True},
            'many_charges': {'charges': 6, 'fieldStrength': 0.8, 'showField': True},
            'strong_field': {'charges': 2, 'fieldStrength': 2.5, 'showField': True}
        },
        'magnetic_field': {
            'single_particle': {'particleCount': 1, 'fieldStrength': 1.0, 'showFieldLines': True},
            'multiple_particles': {'particleCount': 4, 'fieldStrength': 1.2, 'showFieldLines': True},
            'strong_field': {'particleCount': 2, 'fieldStrength': 2.0, 'showFieldLines': True},
            'weak_field': {'particleCount': 3, 'fieldStrength': 0.5, 'showFieldLines': True}
        },
        'wave_motion': {
            'low_frequency': {'frequency': 0.5, 'amplitude': 60, 'wavelength': 150},
            'high_frequency': {'frequency': 2.0, 'amplitude': 40, 'wavelength': 80},
            'large_amplitude': {'frequency': 1.0, 'amplitude': 80, 'wavelength': 120},
            'short_wavelength': {'frequency': 1.5, 'amplitude': 50, 'wavelength': 60}
        },
        'oscillation': {
            'two_oscillators': {'oscillatorCount': 2, 'coupling': 0.15, 'damping': 0.01},
            'three_oscillators': {'oscillatorCount': 3, 'coupling': 0.1, 'damping': 0.02},
            'weak_coupling': {'oscillatorCount': 3, 'coupling': 0.05, 'damping': 0.01},
            'strong_coupling': {'oscillatorCount': 2, 'coupling': 0.3, 'damping': 0.02}
        },
        'em_wave': {
            'linear_polarization': {'frequency': 1.0, 'amplitude': 1.0, 'polarization': 'linear'},
            'circular_polarization': {'frequency': 1.2, 'amplitude': 1.0, 'polarization': 'circular'},
            'high_frequency': {'frequency': 2.5, 'amplitude': 0.8, 'polarization': 'linear'},
            'low_frequency': {'frequency': 0.5, 'amplitude': 1.2, 'polarization': 'linear'}
        }
    }
    
    if simulation_type not in presets:
        return jsonify({'error': 'Simulation type not found'}), 404
    
    return jsonify(presets[simulation_type])

# Legacy plotting routes for backward compatibility
@simulation_bp.route('/plot2d', methods=['POST', 'OPTIONS'])
def simulation_plot2d():
    """2D plotting endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    try:
        data = request.get_json()
        mode = data.get('mode', 'equation')
        
        if mode == 'equation':
            equation = data.get('equation', 'sin(x)')
            x_min = data.get('x_min', -10)
            x_max = data.get('x_max', 10)
            resolution = data.get('resolution', 200)
            
            # Extract additional parameters for customization
            kwargs = {}
            if 'format' in data:
                kwargs['format'] = data['format']
            if 'width' in data:
                kwargs['width'] = data['width']
            if 'height' in data:
                kwargs['height'] = data['height']
            if 'dpi' in data:
                kwargs['dpi'] = data['dpi']
            if 'style' in data:
                kwargs['style'] = data['style']
            
            result = plot_equation_2d(equation, x_min, x_max, resolution, **kwargs)
            
            # Convert file paths to URLs
            base_url = request.host_url.rstrip('/')
            if 'html_path' in result:
                html_filename = os.path.basename(result['html_path'])
                result['html_url'] = f"{base_url}/simulation/download/{html_filename}"
            if 'png_path' in result:
                png_filename = os.path.basename(result['png_path'])
                result['png_url'] = f"{base_url}/simulation/download/{png_filename}"
            
            return jsonify(result)
            
        elif mode == 'csv':
            csv_data = data.get('csv_data', '')
            x_column = data.get('x_column', 0)
            y_column = data.get('y_column', 1)
            
            # Parse CSV data
            import csv
            import io
            
            csv_reader = csv.reader(io.StringIO(csv_data))
            rows = list(csv_reader)
            if not rows:
                return jsonify({'error': 'No CSV data provided'}), 400
                
            header = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            
            # Convert column indices to column names if numeric
            x_col = header[x_column] if isinstance(x_column, int) and x_column < len(header) else str(x_column)
            y_col = header[y_column] if isinstance(y_column, int) and y_column < len(header) else str(y_column)
            
            # Extract additional parameters for customization
            kwargs = {}
            if 'format' in data:
                kwargs['format'] = data['format']
            if 'width' in data:
                kwargs['width'] = data['width']
            if 'height' in data:
                kwargs['height'] = data['height']
            
            result = plot_from_csv_columns(header, data_rows, x_col, y_col, **kwargs)
            
            # Convert file paths to URLs
            base_url = request.host_url.rstrip('/')
            if 'html_path' in result:
                html_filename = os.path.basename(result['html_path'])
                result['html_url'] = f"{base_url}/simulation/download/{html_filename}"
            if 'png_path' in result:
                png_filename = os.path.basename(result['png_path'])
                result['png_url'] = f"{base_url}/simulation/download/{png_filename}"
            
            return jsonify(result)
            
        else:
            return jsonify({'error': 'Invalid mode. Use "equation" or "csv"'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simulation_bp.route('/plot3d', methods=['POST', 'OPTIONS'])  
def simulation_plot3d():
    """3D plotting endpoint - supports both JSON and form data for CSV uploads"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    try:
        # Check if this is a CSV upload (multipart form data) or JSON request
        if 'file' in request.files:
            # Handle CSV file upload
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            # Get form parameters for CSV 3D plot
            x_column = request.form.get('x_col', 'x')
            y_column = request.form.get('y_col', 'y')
            z_column = request.form.get('z_col', 'z')
            
            # Read and parse CSV content
            csv_content = file.read().decode('utf-8')
            lines = csv_content.strip().split('\n')
            header = [col.strip() for col in lines[0].split(',')]
            data_rows = [line.split(',') for line in lines[1:] if line.strip()]
            
            # Extract additional parameters
            kwargs = {}
            if request.form.get('width'):
                kwargs['width'] = int(request.form.get('width'))
            if request.form.get('height'):
                kwargs['height'] = int(request.form.get('height'))
            if request.form.get('title'):
                kwargs['title'] = request.form.get('title')
            if request.form.get('xlabel'):
                kwargs['xlabel'] = request.form.get('xlabel')
            if request.form.get('ylabel'):
                kwargs['ylabel'] = request.form.get('ylabel')
            if request.form.get('zlabel'):
                kwargs['zlabel'] = request.form.get('zlabel')
            
            result = plot_from_csv_xyz(header, data_rows, x_column, y_column, z_column, **kwargs)
            
            # Convert file paths to URLs
            base_url = request.host_url.rstrip('/')
            if 'html_path' in result:
                html_filename = os.path.basename(result['html_path'])
                result['html_url'] = f"{base_url}/simulation/download/{html_filename}"
            
            return jsonify(result)
        
        else:
            # Handle JSON requests for equation/parametric plots
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
                
            mode = data.get('mode', 'equation')
            
            if mode == 'equation':
                equation = data.get('equation', 'sin(sqrt(x**2 + y**2))')
                x_min = data.get('x_min', -5)
                x_max = data.get('x_max', 5)
                y_min = data.get('y_min', -5)
                y_max = data.get('y_max', 5)
                resolution = data.get('resolution', 50)
                output_format = data.get('format', 'html')
                
                result = plot_surface(equation, x_min, x_max, y_min, y_max, resolution, format=output_format)
                
                # Convert file paths to URLs for consistency with CSV mode
                base_url = request.host_url.rstrip('/')
                if 'html_path' in result:
                    html_filename = os.path.basename(result['html_path'])
                    result['html_url'] = f"{base_url}/simulation/download/{html_filename}"
                if 'png_path' in result and result['png_path']:
                    png_filename = os.path.basename(result['png_path'])
                    result['png_url'] = f"{base_url}/simulation/download/{png_filename}"
                
                return jsonify(result)
                
            elif mode == 'parametric':
                x_eq = data.get('x_equation', 'cos(t)')
                y_eq = data.get('y_equation', 'sin(t)')  
                z_eq = data.get('z_equation', 't')
                t_min = data.get('t_min', 0)
                t_max = data.get('t_max', 6.28)
                resolution = data.get('resolution', 100)
                
                result = plot_parametric(x_eq, y_eq, z_eq, t_min, t_max, resolution)
                
                # Convert file paths to URLs for consistency
                base_url = request.host_url.rstrip('/')
                if 'html_path' in result:
                    html_filename = os.path.basename(result['html_path'])
                    result['html_url'] = f"{base_url}/simulation/download/{html_filename}"
                if 'png_path' in result and result['png_path']:
                    png_filename = os.path.basename(result['png_path'])
                    result['png_url'] = f"{base_url}/simulation/download/{png_filename}"
                
                return jsonify(result)
                
            else:
                return jsonify({'error': 'Invalid mode. Use "equation" or "parametric"'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simulation_bp.route('/pygame', methods=['POST', 'OPTIONS'])
def simulation_pygame():
    """Pygame particle simulation endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    try:
        data = request.get_json()
        params = {
            'n': data.get('n', 50),  # Use 'n' directly as frontend sends it
            'steps': data.get('steps', 120),  # Use 'steps' directly as frontend sends it
            'width': data.get('width', 800),
            'height': data.get('height', 600),
            'radius': data.get('radius', 5),
            'save_gif': data.get('save_gif', False)
        }
        
        result = run_particle_simulation(params)
        
        # Convert file paths to URLs so frontend can access them
        base_url = request.host_url.rstrip('/')
        if 'frames' in result:
            frame_urls = []
            for frame_path in result['frames']:
                if frame_path:  # Skip None or empty paths
                    frame_filename = os.path.basename(frame_path)
                    frame_url = f"{base_url}/simulation/download/{frame_filename}"
                    frame_urls.append(frame_url)
            result['frames'] = frame_urls
            
        if 'gif' in result and result['gif']:
            gif_filename = os.path.basename(result['gif'])
            result['gif_url'] = f"{base_url}/simulation/download/{gif_filename}"
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simulation_bp.route('/plot_csv', methods=['POST', 'OPTIONS'])
def plot_csv():
    """CSV plotting endpoint - handles multipart form data with file upload"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
        
    try:
        # Check if file is uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Get form parameters
        x_column = request.form.get('x_col', '0')
        y_column = request.form.get('y_col', '1')
        output_format = request.form.get('format', 'html')
        
        # Read CSV file content
        csv_content = file.read().decode('utf-8')
        
        # Parse CSV data
        import csv
        import io
        
        csv_reader = csv.reader(io.StringIO(csv_content))
        rows = list(csv_reader)
        if not rows:
            return jsonify({'error': 'CSV file is empty'}), 400
            
        header = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        # Convert column indices to column names if numeric
        try:
            x_idx = int(x_column)
            x_col = header[x_idx] if x_idx < len(header) else str(x_column)
        except ValueError:
            x_col = str(x_column)
            
        try:
            y_idx = int(y_column)
            y_col = header[y_idx] if y_idx < len(header) else str(y_column)
        except ValueError:
            y_col = str(y_column)
        
        # Extract additional parameters for customization
        kwargs = {}
        if output_format:
            kwargs['format'] = output_format
        if request.form.get('width'):
            kwargs['width'] = int(request.form.get('width'))
        if request.form.get('height'):
            kwargs['height'] = int(request.form.get('height'))
        
        result = plot_from_csv_columns(header, data_rows, x_col, y_col, **kwargs)
        
        # Convert file paths to URLs
        base_url = request.host_url.rstrip('/')
        if 'html_path' in result:
            html_filename = os.path.basename(result['html_path'])
            result['html_url'] = f"{base_url}/simulation/download/{html_filename}"
        if 'png_path' in result:
            png_filename = os.path.basename(result['png_path'])
            result['png_url'] = f"{base_url}/simulation/download/{png_filename}"
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simulation_bp.route('/download/<path:filename>', methods=['GET'])
def simulation_download(filename):
    plots_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    path = os.path.abspath(os.path.join(plots_dir, filename))
    # Prevent directory traversal
    if not path.startswith(os.path.abspath(plots_dir)):
        return jsonify({'error': 'Invalid filename'}), 400
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(path)

