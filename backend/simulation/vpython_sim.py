"""Generate embeddable VPython (GlowScript) HTML simulations.

Supported modes:
- 'vector': show a 3D arrow at the origin with optional animation.
- 'orbit': simple two-body orbit demo (runs client-side in VPython).

This module returns saved HTML file path and a download URL when a host_url
is provided.
"""
from typing import Dict, Any
from .utils import unique_path, ensure_plots_dir
import json
import os


# Preferred local static copy, but the generated HTML will try several fallbacks
# Prefer loading GlowScript from a CDN in the browser (more likely to be reachable
# from developer machines). Fall back to local `/static/glow.js` if CDN is blocked
# or not reachable.
GLOWSCRIPT_CDN = "https://cdn.jsdelivr.net/gh/glowscript/glow@1.5.0/glow.js"
GLOWSCRIPT_FALLBACKS = [
    # try CDN first so the browser downloads the runtime directly
    "https://cdn.jsdelivr.net/gh/glowscript/glow@1.5.0/glow.js",
    "https://www.glowscript.org/lib/glow/v1.5.0/glow.js",
    # local static file as last-resort
    "/static/glow.js",
]

# Safety limits to avoid generating extremely heavy pages
MAX_GRID = 8
MAX_STREAMLINES = 40
MAX_CHARGES = 8
MAX_PARTICLE_TRAJ = 4
MIN_STRENGTH = 0.001
MAX_STRENGTH = 100.0


def _clamp_val(name, val, lo, hi, warnings):
    try:
        v = float(val)
    except Exception:
        warnings.append(f"Invalid value for {name}; using {lo}")
        return lo
    if v < lo:
        warnings.append(f"{name} too small; clamped to {lo}")
        return lo
    if v > hi:
        warnings.append(f"{name} too large; clamped to {hi}")
        return hi
    return v


def _vector_sim_code(vx: float, vy: float, vz: float, animate: bool) -> str:
    code = f"""
from vpython import scene, arrow, vector, color, rate
scene.title = 'Vector visualization'
vec = vector({vx}, {vy}, {vz})
arr = arrow(pos=vector(0,0,0), axis=vec, shaftwidth=max(0.05, vec.mag*0.05), color=color.cyan)
"""
    if animate:
        code += """
theta = 0
import math
while True:
    rate(60)
    theta += 0.02
    rot = vector(math.cos(theta), math.sin(theta), 0)
    arr.axis = vec.rotate(angle=theta, axis=rot)
"""
    return code


def _orbit_sim_code(rx, ry, rz, vx, vy, vz, G=1, M=1000, dt=0.01):
    # GlowScript VPython code for a simple central-force orbit demo
    code = f"""
from vpython import sphere, vector, color, rate, mag
scene.title = 'Orbit demo (client-side)'
sun = sphere(pos=vector(0,0,0), radius=1.5, color=color.yellow)
planet = sphere(pos=vector({rx}, {ry}, {rz}), radius=0.4, color=color.blue, make_trail=True)
planet.mass = 1
v = vector({vx}, {vy}, {vz})
G = {G}
M = {M}
dt = {dt}
while True:
    rate(100)
    r = planet.pos - sun.pos
    a = -G * M * r / mag(r)**3
    v = v + a*dt
    planet.pos = planet.pos + v*dt
"""
    return code


def generate_vpython_html(data: Dict[str, Any], host_url: str = '') -> Dict[str, Any]:
    """Create an interactive physics simulation HTML file and return paths.

    This now generates interactive 3D physics simulations instead of static VPython code.
    
    Expected data keys:
    - preset: 'electric', 'magnetic', 'pendulum', etc.
    - mode: 'vector' or 'orbit' (for legacy compatibility)
    - Various experiment-specific parameters
    """
    ensure_plots_dir()
    
    # Determine the experiment type
    preset = (data.get('preset') or '').lower()
    mode = (data.get('mode') or 'vector').lower()
    
    # Map inputs to our new system
    experiment_type = 'electric_field'  # default
    initial_params = {}
    
    if preset == 'electric':
        experiment_type = 'electric_field'
        initial_params = {
            'charge_strength': data.get('E_strength', 2.0),
            'grid_size': data.get('grid', 5),
            'show_field_lines': True
        }
    elif preset == 'magnetic':
        experiment_type = 'magnetic_field'
        initial_params = {
            'magnetic_strength': data.get('B_strength', 1.0),
            'particle_velocity': 1.5,
            'show_magnetic_lines': True
        }
    elif preset in ['pendulum', 'gravity']:
        experiment_type = 'pendulum'
        initial_params = {
            'pendulum_length': data.get('length', 2.0),
            'initial_angle': 30,
            'gravity': data.get('gravity', 9.8)
        }
    elif mode == 'vector':
        experiment_type = 'electric_field'  # Use electric field for vector visualization
        initial_params = {
            'charge_strength': 2.0,
            'grid_size': 4,
            'show_field_lines': True
        }
    elif mode == 'orbit':
        experiment_type = 'pendulum'  # Use pendulum for orbital-like motion
        initial_params = {
            'pendulum_length': 3.0,
            'initial_angle': 45,
            'gravity': 9.8
        }
    
    # Generate the interactive HTML
    html_code = generate_interactive_html(experiment_type, initial_params)
    
    out_path = unique_path('vpython_sim', 'html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_code)

    filename = os.path.basename(out_path)
    result = {'html_path': out_path}
    if host_url:
        result['html_url'] = f"{host_url}/simulation/download/{filename}"
    return result


def generate_interactive_html(experiment_type: str, params: Dict[str, Any]) -> str:
    """Generate HTML for interactive 3D physics simulations with integrated controls."""
    
    # Convert params to JavaScript initialization
    params_js = json.dumps(params)
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"> 
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Physics Simulation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
            color: #ffffff;
        }}
        
        .simulation-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: row;
            position: relative;
            overflow: hidden;
        }}
        
        #physics-simulation {{
            flex: 1;
            position: relative;
            background: radial-gradient(circle at 50% 50%, #001122 0%, #000000 100%);
            min-width: 0;
            min-height: 0;
            overflow: hidden;
        }}
        
        canvas {{
            display: block;
            width: 100%;
            height: 100%;
            border: none;
            cursor: crosshair;
        }}
        
        @media (max-width: 768px) {{
            .simulation-container {{
                flex-direction: column;
            }}
            
            .controls-panel {{
                width: 100% !important;
                min-width: auto !important;
                max-width: none !important;
                height: auto !important;
                max-height: 200px !important;
                order: 2;
            }}
            
            #physics-simulation {{
                order: 1;
                flex: 1;
            }}
        }}
        
        .controls-panel {{
            width: 280px;
            min-width: 280px;
            max-width: 280px;
            background: rgba(5, 10, 20, 0.98);
            backdrop-filter: blur(15px);
            border-left: 1px solid rgba(0, 122, 204, 0.3);
            padding: 15px;
            overflow-y: auto;
            box-shadow: -5px 0 25px rgba(0, 0, 0, 0.6);
            flex-shrink: 0;
            position: relative;
        }}
        
        .panel-header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(0, 122, 204, 0.4);
        }}
        
        .panel-title {{
            font-size: 16px;
            font-weight: 700;
            color: #00ccff;
            margin-bottom: 4px;
            text-shadow: 0 0 8px rgba(0, 204, 255, 0.4);
        }}
        
        .panel-subtitle {{
            font-size: 11px;
            color: #88aacc;
            text-transform: uppercase;
            letter-spacing: 1.2px;
        }}
        
        .control-group {{
            margin-bottom: 18px;
            background: rgba(255, 255, 255, 0.02);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        .control-label {{
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #ccddff;
            margin-bottom: 8px;
            text-transform: capitalize;
        }}
        
        .slider-container {{
            position: relative;
            margin-bottom: 12px;
        }}
        
        .slider {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
            outline: none;
            -webkit-appearance: none;
            appearance: none;
            transition: all 0.3s ease;
        }}
        
        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00ccff 0%, #0088cc 100%);
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 204, 255, 0.6);
            transition: all 0.2s ease;
        }}
        
        .slider::-webkit-slider-thumb:hover {{
            transform: scale(1.1);
            box-shadow: 0 0 15px rgba(0, 204, 255, 0.9);
        }}
        
        .value-display {{
            position: absolute;
            right: 0;
            top: -22px;
            background: rgba(0, 204, 255, 0.15);
            color: #00ccff;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 700;
            border: 1px solid rgba(0, 204, 255, 0.3);
            min-width: 35px;
            text-align: center;
        }}
        
        .button-group {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 15px;
        }}
        
        .control-button {{
            padding: 8px 10px;
            background: linear-gradient(135deg, #004466 0%, #006699 100%);
            color: white;
            border: 1px solid rgba(0, 204, 255, 0.4);
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 600;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .control-button:hover {{
            background: linear-gradient(135deg, #0066aa 0%, #0088cc 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }}
        
        .control-button.primary {{
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            border-color: rgba(255, 107, 53, 0.5);
        }}
        
        .control-button.primary:hover {{
            background: linear-gradient(135deg, #ff8c42 0%, #ffa726 100%);
        }}
        
        .interactive-controls {{
            background: rgba(0, 50, 100, 0.1);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(0, 122, 204, 0.2);
            margin-bottom: 15px;
        }}
        
        .instructions {{
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 6px;
            border-left: 3px solid #00ccff;
            margin-bottom: 15px;
        }}
        
        .instructions h4 {{
            color: #00ccff;
            font-size: 12px;
            margin-bottom: 6px;
            font-weight: 600;
        }}
        
        .instructions ul {{
            list-style: none;
            font-size: 10px;
            line-height: 1.4;
            color: #ccddff;
        }}
        
        .instructions li {{
            margin-bottom: 3px;
            padding-left: 12px;
            position: relative;
        }}
        
        .instructions li:before {{
            content: "•";
            color: #00ccff;
            position: absolute;
            left: 0;
        }}
        
        .stats-display {{
            background: rgba(0, 0, 0, 0.3);
            padding: 8px;
            border-radius: 6px;
            font-size: 10px;
            color: #88aacc;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
            margin-bottom: 15px;
        }}
        
        .slider {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: linear-gradient(90deg, #333 0%, #666 100%);
            outline: none;
            -webkit-appearance: none;
            appearance: none;
            transition: all 0.3s ease;
        }}
        
        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00ccff 0%, #0088cc 100%);
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 204, 255, 0.5);
            transition: all 0.2s ease;
        }}
        
        .slider::-webkit-slider-thumb:hover {{
            transform: scale(1.2);
            box-shadow: 0 0 15px rgba(0, 204, 255, 0.8);
        }}
        
        .slider::-moz-range-thumb {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00ccff 0%, #0088cc 100%);
            cursor: pointer;
            border: none;
            box-shadow: 0 0 10px rgba(0, 204, 255, 0.5);
        }}
        
        .value-display {{
            position: absolute;
            right: 0;
            top: -25px;
            background: rgba(0, 204, 255, 0.2);
            color: #00ccff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid rgba(0, 204, 255, 0.3);
        }}
        
        .checkbox-container {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            cursor: pointer;
        }}
        
        .checkbox {{
            width: 16px;
            height: 16px;
            margin-right: 10px;
            accent-color: #00ccff;
        }}
        
        .button-group {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .control-button {{
            padding: 8px 12px;
            background: linear-gradient(135deg, #004466 0%, #006699 100%);
            color: white;
            border: 1px solid rgba(0, 204, 255, 0.3);
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .control-button:hover {{
            background: linear-gradient(135deg, #0066aa 0%, #0088cc 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }}
        
        .coordinate-info {{
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(0, 20, 40, 0.9);
            color: #00ff88;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            font-family: 'Courier New', monospace;
            border: 1px solid rgba(0, 255, 136, 0.3);
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
        }}
        
        .experiment-info {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(0, 40, 80, 0.9);
            color: #00ccff;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid rgba(0, 204, 255, 0.3);
            box-shadow: 0 0 15px rgba(0, 204, 255, 0.2);
            text-align: center;
            max-width: 200px;
        }}
        
        .physics-equation {{
            position: absolute;
            bottom: 15px;
            left: 15px;
            background: rgba(40, 20, 0, 0.9);
            color: #ffaa00;
            padding: 10px;
            border-radius: 6px;
            font-size: 12px;
            font-family: 'Courier New', monospace;
            border: 1px solid rgba(255, 170, 0, 0.3);
            box-shadow: 0 0 15px rgba(255, 170, 0, 0.2);
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 0.8; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.8; }}
        }}
        
        .status-indicator {{
            animation: pulse 2s ease-in-out infinite;
        }}
        
        /* Responsive design */
        @media (max-width: 1024px) {{
            .simulation-container {{
                flex-direction: column;
                height: 100vh;
            }}
            
            #physics-simulation {{
                flex: 1;
                border-right: none;
                border-bottom: 2px solid rgba(0, 122, 204, 0.3);
                min-height: 60vh;
            }}
            
            .controls-panel {{
                width: 100%;
                min-width: auto;
                max-width: none;
                height: auto;
                max-height: 40vh;
                border-left: none;
                border-top: 2px solid rgba(0, 122, 204, 0.3);
                padding: 15px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                overflow-x: auto;
            }}
        }}
    </style>
    <script src="/static/glow.js"></script>
</head>
<body>
    <div class="simulation-container">
        <div id="physics-simulation">
            <canvas id="simulation-canvas"></canvas>
        </div>
        
        <div class="controls-panel">
            <div class="panel-header">
                <div class="panel-title">Interactive Physics</div>
                <div class="panel-subtitle">Real-time Simulation</div>
            </div>
            
            <div class="instructions">
                <h4>How to Interact:</h4>
                <ul>
                    <li>Click to add charges (+/-)</li>
                    <li>Drag charges to move them</li>
                    <li>Right-click to remove charges</li>
                    <li>Watch field lines flow!</li>
                </ul>
            </div>
            
            <div class="interactive-controls">
                <div class="control-group">
                    <label class="control-label">Grid Density</label>
                    <div class="slider-container">
                        <input type="range" class="slider" id="gridDensity" min="8" max="20" value="15" step="1">
                        <div class="value-display" id="gridDensity-value">15</div>
                    </div>
                </div>
                
                <div class="control-group">
                    <label class="control-label">Field Strength</label>
                    <div class="slider-container">
                        <input type="range" class="slider" id="fieldStrength" min="0.5" max="5.0" value="2.0" step="0.1">
                        <div class="value-display" id="fieldStrength-value">2.0</div>
                    </div>
                </div>
                
                <div class="control-group">
                    <label class="control-label">Show Field Lines</label>
                    <input type="checkbox" class="checkbox" id="showFieldLines" checked>
                </div>
                
                <div class="control-group">
                    <label class="control-label">Show Forces</label>
                    <input type="checkbox" class="checkbox" id="showForces" checked>
                </div>
                
                <div class="control-group">
                    <label class="control-label">Animate Fields</label>
                    <input type="checkbox" class="checkbox" id="animateFields" checked>
                </div>
            </div>
            
            <div class="button-group">
                <button class="control-button primary" onclick="addRandomCharge()">Add Random</button>
                <button class="control-button" onclick="clearAllCharges()">Clear All</button>
            </div>
            
            <div class="button-group">
                <button class="control-button" onclick="setupExperiment('dipole')">Dipole</button>
                <button class="control-button" onclick="setupExperiment('quadrupole')">Quadrupole</button>
            </div>
            
            <div class="button-group">
                <button class="control-button" onclick="resetSimulation()">Reset</button>
                <button class="control-button" onclick="toggleAnimation()">Play/Pause</button>
            </div>
            
            <div class="stats-display" id="stats">
                <div>Charges: <span id="charge-count">0</span></div>
                <div>Field Lines: <span id="fieldline-count">0</span></div>
                <div>Grid Points: <span id="grid-count">0</span></div>
            </div>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof initializeSimulation === 'function') {{
                // Initialize simulation
                initializeSimulation();
                
                // Setup control event listeners
                setupControlListeners();
                
                // Start with electric field experiment
                setupExperiment('electric_field');
                
                console.log('Interactive simulation ready!');
            }} else {{
                console.error('Physics simulation engine not loaded');
                document.body.innerHTML = '<div style="color: #ff4444; text-align: center; padding: 50px; font-family: monospace;">Loading physics simulation engine...</div>';
            }}
        }});
        
        function setupControlListeners() {{
            // Grid density slider
            const gridSlider = document.getElementById('gridDensity');
            const gridValue = document.getElementById('gridDensity-value');
            if (gridSlider && gridValue) {{
                gridSlider.addEventListener('input', function() {{
                    gridValue.textContent = this.value;
                    updateSimulation('gridDensity', parseInt(this.value));
                }});
            }}
            
            // Field strength slider
            const strengthSlider = document.getElementById('fieldStrength');
            const strengthValue = document.getElementById('fieldStrength-value');
            if (strengthSlider && strengthValue) {{
                strengthSlider.addEventListener('input', function() {{
                    strengthValue.textContent = parseFloat(this.value).toFixed(1);
                    updateSimulation('fieldStrength', parseFloat(this.value));
                }});
            }}
            
            // Checkboxes
            const checkboxes = ['showFieldLines', 'showForces', 'animateFields'];
            checkboxes.forEach(id => {{
                const checkbox = document.getElementById(id);
                if (checkbox) {{
                    checkbox.addEventListener('change', function() {{
                        updateSimulation(id, this.checked);
                    }});
                }}
            }});
            
            // Update stats periodically
            setInterval(updateStats, 1000);
        }}
        
        function updateStats() {{
            // This will be called by the simulation engine
            if (window.charges && window.fieldLines && window.fieldVectors) {{
                document.getElementById('charge-count').textContent = window.charges.length || 0;
                document.getElementById('fieldline-count').textContent = window.fieldLines.length || 0;
                document.getElementById('grid-count').textContent = window.fieldVectors.length || 0;
            }}
        }}
        
        // Make control functions globally available
        window.updateSimulation = window.updateSimulation || function() {{}};
        window.resetSimulation = window.resetSimulation || function() {{}};
        window.toggleAnimation = window.toggleAnimation || function() {{}};
        window.addRandomCharge = window.addRandomCharge || function() {{}};
        window.clearAllCharges = window.clearAllCharges || function() {{}};
        window.setupExperiment = window.setupExperiment || function() {{}};
    </script>
        
        function setupDynamicControls(experimentType, params) {{
            const controlsContainer = document.getElementById('dynamic-controls');
            const equationDisplay = document.getElementById('equation-display');
            
            // Clear existing controls
            controlsContainer.innerHTML = '';
            
            // Generate controls based on experiment type
            if (experimentType === 'electric_field' || experimentType === 'electric') {{
                setupElectricFieldControls(controlsContainer, params);
                equationDisplay.innerHTML = 'E = k·q/r² <br>F = q·E';
            }} else if (experimentType === 'magnetic_field' || experimentType === 'magnetic') {{
                setupMagneticFieldControls(controlsContainer, params);
                equationDisplay.innerHTML = 'B = μ₀·I/(2πr) <br>F = q(v × B)';
            }} else if (experimentType === 'pendulum') {{
                setupPendulumControls(controlsContainer, params);
                equationDisplay.innerHTML = 'T = 2π√(L/g) <br>F = -mg·sin(θ)';
            }} else {{
                setupDefaultControls(controlsContainer, params);
                equationDisplay.innerHTML = 'F = ma <br>v = dx/dt';
            }}
        }}
        
        function setupElectricFieldControls(container, params) {{
            createSlider(container, 'Charge Strength', 'charge_strength', params.charge_strength || 2.0, 0.1, 10.0, 0.1);
            createSlider(container, 'Grid Size', 'grid_size', params.grid_size || 3, 1, 8, 1);
            createCheckbox(container, 'Show Field Lines', 'show_field_lines', params.show_field_lines || true);
            createSlider(container, 'Arrow Scale', 'arrow_scale', params.arrow_scale || 0.5, 0.1, 2.0, 0.1);
        }}
        
        function setupMagneticFieldControls(container, params) {{
            createSlider(container, 'Magnetic Strength', 'magnetic_strength', params.magnetic_strength || 1.0, 0.1, 5.0, 0.1);
            createSlider(container, 'Particle Velocity', 'particle_velocity', params.particle_velocity || 2.0, 0.5, 10.0, 0.5);
            createSlider(container, 'Field Density', 'field_density', params.field_density || 5, 3, 10, 1);
            createCheckbox(container, 'Show Trajectory', 'show_trajectory', params.show_trajectory || true);
        }}
        
        function setupPendulumControls(container, params) {{
            createSlider(container, 'Pendulum Length', 'length', params.length || 5.0, 1.0, 10.0, 0.5);
            createSlider(container, 'Initial Angle', 'angle', params.angle || 30, 5, 90, 5);
            createSlider(container, 'Gravity', 'gravity', params.gravity || 9.81, 1.0, 20.0, 0.1);
            createSlider(container, 'Damping', 'damping', params.damping || 0.01, 0.0, 0.1, 0.01);
        }}
        
        function setupDefaultControls(container, params) {{
            createSlider(container, 'X Vector', 'vx', params.vx || 1.0, -5.0, 5.0, 0.1);
            createSlider(container, 'Y Vector', 'vy', params.vy || 0.0, -5.0, 5.0, 0.1);
            createSlider(container, 'Z Vector', 'vz', params.vz || 0.0, -5.0, 5.0, 0.1);
            createCheckbox(container, 'Animate', 'animate', params.animate || true);
        }}
        
        function createSlider(container, label, id, value, min, max, step) {{
            const group = document.createElement('div');
            group.className = 'control-group';
            
            const labelEl = document.createElement('label');
            labelEl.className = 'control-label';
            labelEl.textContent = label;
            
            const sliderContainer = document.createElement('div');
            sliderContainer.className = 'slider-container';
            
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.className = 'slider';
            slider.id = id;
            slider.min = min;
            slider.max = max;
            slider.step = step;
            slider.value = value;
            
            const valueDisplay = document.createElement('div');
            valueDisplay.className = 'value-display';
            valueDisplay.textContent = value.toFixed(step < 1 ? 1 : 0);
            
            slider.addEventListener('input', function() {{
                const val = parseFloat(this.value);
                valueDisplay.textContent = val.toFixed(step < 1 ? 1 : 0);
                updateSimulation(id, val);
            }});
            
            sliderContainer.appendChild(slider);
            sliderContainer.appendChild(valueDisplay);
            group.appendChild(labelEl);
            group.appendChild(sliderContainer);
            container.appendChild(group);
        }}
        
        function createCheckbox(container, label, id, checked) {{
            const group = document.createElement('div');
            group.className = 'control-group';
            
            const checkboxContainer = document.createElement('label');
            checkboxContainer.className = 'checkbox-container';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'checkbox';
            checkbox.id = id;
            checkbox.checked = checked;
            
            checkbox.addEventListener('change', function() {{
                updateSimulation(id, this.checked);
            }});
            
            const labelText = document.createElement('span');
            labelText.textContent = label;
            
            checkboxContainer.appendChild(checkbox);
            checkboxContainer.appendChild(labelText);
            group.appendChild(checkboxContainer);
            container.appendChild(group);
        }}
        
        function updateSimulation(parameter, value) {{
            if (window.updateSimulation) {{
                window.updateSimulation(parameter, value);
            }}
        }}
        
        function resetSimulation() {{
            if (window.resetSimulation) {{
                window.resetSimulation();
            }}
        }}
        
        function toggleAnimation() {{
            if (window.toggleAnimation) {{
                window.toggleAnimation();
            }}
        }}
    </script>
</body>
</html>"""
    
    return html_template
    
