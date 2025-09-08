# Simulation Routes
from flask import Blueprint, request, jsonify, send_file
from simulation.run_simulation import run_simulation

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/simulation', methods=['POST'])
def simulation():
    data = request.json
    result = run_simulation(data)
    return jsonify(result)

@simulation_bp.route('/download_plot', methods=['GET'])
def download_plot_route():
    plot_path = "plots/simulation_plot.png"
    return send_file(plot_path, mimetype='image/png', as_attachment=True)
