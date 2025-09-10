# Simulation Routes
from flask import Blueprint, request, jsonify, send_file, current_app, url_for
from simulation.run_simulation import run_simulation
import os
from simulation.pygame_sim import run_particle_simulation
from simulation.vpython_sim import generate_vpython_html

simulation_bp = Blueprint('simulation', __name__)


@simulation_bp.route('/plot2d', methods=['POST'])
def simulation_plot2d():
    # JSON body expected or form-data with file
    data = request.form.to_dict() if request.form else request.json or {}
    files = request.files or None
    host = request.host_url.rstrip('/')
    result = run_simulation(data, files=files, host_url=host)
    return jsonify(result)


@simulation_bp.route('/plot3d', methods=['POST'])
def simulation_plot3d():
    data = request.json or request.form.to_dict() or {}
    host = request.host_url.rstrip('/')
    result = run_simulation(data, files=None, host_url=host)
    return jsonify(result)


@simulation_bp.route('/plot_csv', methods=['POST'])
def simulation_plot_csv():
    data = request.form.to_dict() if request.form else {}
    files = request.files or None
    host = request.host_url.rstrip('/')
    result = run_simulation(data, files=files, host_url=host)
    return jsonify(result)


@simulation_bp.route('/download/<path:filename>', methods=['GET'])
def simulation_download(filename):
    plots_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    path = os.path.abspath(os.path.join(plots_dir, filename))
    # Prevent directory traversal
    if not path.startswith(os.path.abspath(plots_dir)):
        return jsonify({'error': 'Invalid filename'}), 400
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    # let Flask guess mimetype and serve
    return send_file(path)


@simulation_bp.route('/pygame', methods=['POST'])
def simulation_pygame():
    data = request.json or request.form.to_dict() or {}
    host = request.host_url.rstrip('/')
    result = run_particle_simulation(data, host_url=host)
    return jsonify(result)


@simulation_bp.route('/vpython', methods=['POST'])
def simulation_vpython():
    data = request.json or request.form.to_dict() or {}
    host = request.host_url.rstrip('/')
    result = generate_vpython_html(data, host_url=host)
    return jsonify(result)


@simulation_bp.route('/vpython/list', methods=['GET'])
def simulation_vpython_list():
    # list generated vpython html files in plots dir
    plots_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    plots_dir = os.path.abspath(plots_dir)
    files = []
    if os.path.exists(plots_dir):
        for fn in sorted(os.listdir(plots_dir)):
            if fn.startswith('vpython_sim_') and fn.endswith('.html'):
                files.append({
                    'filename': fn,
                    'url': f"{request.host_url.rstrip('/')}/simulation/download/{fn}"
                })
    return jsonify({'files': files})


@simulation_bp.route('/vpython/preview/<path:filename>', methods=['GET'])
def simulation_vpython_preview(filename):
    # serve the HTML directly with text/html so it can be embedded in iframes
    plots_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    path = os.path.abspath(os.path.join(plots_dir, filename))
    if not path.startswith(os.path.abspath(plots_dir)):
        return jsonify({'error': 'Invalid filename'}), 400
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(path, mimetype='text/html')


@simulation_bp.route('/vpython/presets', methods=['GET'])
def simulation_vpython_presets():
    presets = [
        {
            'name': 'electric',
            'description': 'Point charge electric field arrows (grid)',
            'params': {'E_strength': 1.0, 'grid': 5}
        },
        {
            'name': 'magnetic',
            'description': 'Uniform B field with a moving charged particle',
            'params': {'B_strength': 1.0, 'grid': 5}
        },
        {
            'name': 'gravity',
            'description': 'Central gravity orbit demo',
            'params': {'mass': 10.0}
        }
    ]
    return jsonify({'presets': presets})

