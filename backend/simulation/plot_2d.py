import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.io as pio
import sympy as sp
from .utils import unique_path, ensure_plots_dir


ALLOWED_FUNCS = {
    # basic trig
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    # hyperbolic
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
    'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh,
    # exponentials / logs / roots
    'exp': sp.exp, 'log': sp.log, 'ln': sp.log, 'sqrt': sp.sqrt,
    # special functions
    'erf': sp.erf, 'erfc': sp.erfc, 'gamma': sp.gamma,
    # absolute
    'abs': sp.Abs, 'Abs': sp.Abs,
    # constants
    'pi': sp.pi, 'E': sp.E,
}


def safe_sympify(expr_str: str):
    return sp.sympify(expr_str, locals=ALLOWED_FUNCS)


def plot_equation_2d(equation: str, x_min: float = -10, x_max: float = 10, resolution: int = 1000):
    """Return dict with 'html_path' and 'png_path' of plotted equation z=f(x)."""
    ensure_plots_dir()
    x = sp.symbols('x')
    expr = safe_sympify(equation)
    f = sp.lambdify(x, expr, 'numpy')
    xs = np.linspace(x_min, x_max, resolution)
    ys = f(xs)

    # Plotly interactive
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines'))
    fig.update_layout(title=f"y = {equation}", xaxis_title='x', yaxis_title='y')

    html_path = unique_path('plot2d', 'html')
    pio.write_html(fig, file=html_path, auto_open=False, include_plotlyjs='cdn')

    # PNG fallback (matplotlib)
    png_path = unique_path('plot2d', 'png')
    plt.figure(figsize=(8, 5))
    plt.plot(xs, ys)
    plt.title(f"y = {equation}")
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.savefig(png_path, bbox_inches='tight')
    plt.close()

    return {'html_path': html_path, 'png_path': png_path}


def plot_from_csv_columns(header, rows, x_col: str, y_col: str):
    ensure_plots_dir()
    if x_col not in header or y_col not in header:
        return {'error': 'Columns not found'}
    xi = header.index(x_col)
    yi = header.index(y_col)
    xs = np.array([r[xi] for r in rows], dtype=float)
    ys = np.array([r[yi] for r in rows], dtype=float)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers+lines'))
    html_path = unique_path('plot2d_csv', 'html')
    pio.write_html(fig, file=html_path, auto_open=False, include_plotlyjs='cdn')

    png_path = unique_path('plot2d_csv', 'png')
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8,5))
    plt.plot(xs, ys, marker='o')
    plt.savefig(png_path, bbox_inches='tight')
    plt.close()
    return {'html_path': html_path, 'png_path': png_path}
