import os
import numpy as np
import sympy as sp
import plotly.graph_objs as go
import plotly.io as pio
from .utils import unique_path, ensure_plots_dir


ALLOWED_FUNCS = {
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
    'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh,
    'exp': sp.exp, 'log': sp.log, 'ln': sp.log, 'sqrt': sp.sqrt,
    'erf': sp.erf, 'erfc': sp.erfc, 'gamma': sp.gamma,
    'pi': sp.pi, 'E': sp.E,
}


def safe_sympify(expr_str: str):
    return sp.sympify(expr_str, locals=ALLOWED_FUNCS)


def plot_surface(equation: str, x_min: float=-5, x_max: float=5, y_min: float=-5, y_max: float=5, resolution: int=100):
    ensure_plots_dir()
    x, y = sp.symbols('x y')
    expr = safe_sympify(equation)
    f = sp.lambdify((x, y), expr, 'numpy')
    xs = np.linspace(x_min, x_max, resolution)
    ys = np.linspace(y_min, y_max, resolution)
    X, Y = np.meshgrid(xs, ys)
    Z = f(X, Y)

    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
    fig.update_layout(title=f"z = {equation}", scene=dict(xaxis_title='x', yaxis_title='y', zaxis_title='z'))

    html_path = unique_path('plot3d_surface', 'html')
    pio.write_html(fig, file=html_path, auto_open=False, include_plotlyjs='cdn')

    png_path = unique_path('plot3d_surface', 'png')
    # Render static PNG via orca/plotly is not guaranteed; skip PNG generation for 3D for now
    return {'html_path': html_path, 'png_path': None}


def plot_parametric(x_expr: str, y_expr: str, z_expr: str, t_min: float=0, t_max: float=10, resolution: int=200):
    ensure_plots_dir()
    t = sp.symbols('t')
    ex = safe_sympify(x_expr)
    ey = safe_sympify(y_expr)
    ez = safe_sympify(z_expr)
    fx = sp.lambdify(t, ex, 'numpy')
    fy = sp.lambdify(t, ey, 'numpy')
    fz = sp.lambdify(t, ez, 'numpy')
    ts = np.linspace(t_min, t_max, resolution)
    xs = fx(ts)
    ys = fy(ts)
    zs = fz(ts)

    fig = go.Figure(data=[go.Scatter3d(x=xs, y=ys, z=zs, mode='lines')])
    fig.update_layout(title='Parametric 3D curve')

    html_path = unique_path('plot3d_param', 'html')
    pio.write_html(fig, file=html_path, auto_open=False, include_plotlyjs='cdn')
    return {'html_path': html_path, 'png_path': None}
