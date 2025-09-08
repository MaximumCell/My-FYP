# Main App Entry Point
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from routes.ml_routes import ml_bp
from routes.simulation_routes import simulation_bp
from routes.ai_routes import ai_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(ml_bp, url_prefix='/ml')
app.register_blueprint(simulation_bp, url_prefix='/simulation')
app.register_blueprint(ai_bp, url_prefix='/ai')

if __name__ == '__main__':
    app.run(debug=True)
