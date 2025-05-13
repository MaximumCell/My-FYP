import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import os
import re
from flask import jsonify, send_file
import matplotlib
matplotlib.use('Agg')

# Updated predefined physics equations without sp. prefix
PREDEFINED_EQUATIONS = {
    "Projectile Motion (y = v*x - 0.5*g*x^2)": "v*x - 0.5*g*x**2",
    "Simple Harmonic Motion (y = A*sin(w*x))": "A * sin(w * x)",
    "Exponential Decay (y = A*e^(-k*x))": "A * exp(-k*x)",
    "Damped Oscillation (y = A*e^(-b*x) * cos(w*x))": "A * exp(-b*x) * cos(w*x)",
    "Linear Motion (y = m*x + c)": "m*x + c"
}

# Default values for variables
DEFAULT_VALUES = {
    "v": 10.0,
    "g": 9.8,
    "A": 5.0,
    "w": 2.0,
    "k": 0.5,
    "b": 0.2,
    "m": 2.0,
    "c": 3.0
}

def run_simulation(data):
    """
    Process mathematical equations and generate plots,
    handling both predefined and custom equations with variable substitution.
    """
    equation_str = data.get("equation", "")
    x_min = float(data.get("x_min", -10))
    x_max = float(data.get("x_max", 10))
    variables = data.get("variables", {})
    
    if not equation_str:
        return {"error": "No equation provided"}
    
    # Convert empty string values to None
    variables = {k: v for k, v in variables.items() if v is not None and v != ""}
    
    try:
        # If a predefined equation is selected, substitute variables
        if equation_str in PREDEFINED_EQUATIONS:
            equation_template = PREDEFINED_EQUATIONS[equation_str]
            
            # Create a sympy expression with symbolic variables
            x = sp.symbols('x')
            
            # Create symbols for all parameters
            param_symbols = {}
            for var_name in DEFAULT_VALUES:
                param_symbols[var_name] = sp.symbols(var_name)
            
            # Parse the equation template
            expr = sp.sympify(equation_template, locals=param_symbols)
            
            # Substitute values for each parameter
            for var_name in DEFAULT_VALUES:
                # Get the value (user-provided or default)
                if var_name in variables:
                    value = float(variables[var_name])
                else:
                    value = DEFAULT_VALUES[var_name]
                
                # Substitute the value into the expression
                expr = expr.subs(param_symbols[var_name], value)
            
            # Convert back to string for further processing
            equation_str = str(expr)
        
        # Define symbol for x
        x = sp.symbols('x')
        expr = sp.sympify(equation_str)  # Convert string to symbolic expression

        # Convert to a function
        f_lambdified = sp.lambdify(x, expr, "numpy")

        # Generate x values and evaluate function
        x_vals = np.linspace(x_min, x_max, 1000)  # Increased resolution for smoother plots
        
        # Safely evaluate with handling for potential errors
        try:
            y_vals = f_lambdified(x_vals)
            
            # Check for invalid values
            if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)):
                return {"error": "Equation produces invalid values (NaN or Infinity)"}
        except Exception as calc_error:
            return {"error": f"Error calculating values: {str(calc_error)}"}

        # Create and save plot
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, linewidth=2.5, color="#3366CC")
        plt.xlabel("x-axis", fontsize=12)
        plt.ylabel("y-axis", fontsize=12)
        plt.title(f"Plot of: {equation_str}", fontsize=14)
        plt.grid(True, alpha=0.3)
        
        # Add zero axes if they're in the view
        if x_min <= 0 <= x_max:
            plt.axvline(x=0, color='k', linestyle='-', alpha=0.2)
        
        y_min, y_max = plt.ylim()
        if y_min <= 0 <= y_max:
            plt.axhline(y=0, color='k', linestyle='-', alpha=0.2)
        
        # Save the plot - use a consistent filename to match your download_plot route
        os.makedirs("plots", exist_ok=True)
        plot_path = "plots/simulation_plot.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()

        return {
            "message": "Simulation completed", 
            "plot_url": "/download_plot",
            "equation": equation_str
        }

    except Exception as e:
        return {"error": f"Error processing equation: {str(e)}"}

# Assuming you have Flask routes set up to call this function
# Here's a sample route implementation that should be in your main Flask app file:

"""
from flask import Flask, request, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/simulation', methods=['POST'])
def simulation():
    data = request.json
    result = run_simulation(data)
    return jsonify(result)

@app.route('/download_plot')
def download_plot():
    return send_file('plots/simulation_plot.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
"""