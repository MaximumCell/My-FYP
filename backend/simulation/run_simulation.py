import os
from .plot_2d import plot_equation_2d, plot_from_csv_columns
from .plot_3d import plot_surface, plot_parametric
from .utils import ensure_plots_dir


PREDEFINED_EQUATIONS = {
    "Projectile Motion (y = v*x - 0.5*g*x^2)": "v*x - 0.5*g*x**2",
    "Simple Harmonic Motion (y = A*sin(w*x))": "A * sin(w * x)",
    "Exponential Decay (y = A*e^(-k*x))": "A * exp(-k*x)",
    "Damped Oscillation (y = A*e^(-b*x) * cos(w*x))": "A * exp(-b*x) * cos(w*x)",
    "Linear Motion (y = m*x + c)": "m*x + c"
}


def run_simulation(data, files=None, host_url=''):
    """Unified entry for simulation requests.

    data: dict of parameters
    files: dict-like for uploaded files (Flask request.files)
    host_url: base URL (optional) to prefix returned HTML paths
    """
    ensure_plots_dir()
    mode = data.get('mode', 'equation')
    try:
        if mode == 'equation':
            eq = data.get('equation')
            x_min = float(data.get('x_min', -10))
            x_max = float(data.get('x_max', 10))
            res = int(data.get('resolution', 1000))
            # support predefined
            if eq in PREDEFINED_EQUATIONS:
                eq = PREDEFINED_EQUATIONS[eq]
            out = plot_equation_2d(eq, x_min=x_min, x_max=x_max, resolution=res)
            # prefix host if provided
            if host_url:
                out['html_url'] = host_url + '/simulation/download/' + os.path.basename(out['html_path'])
                out['png_url'] = host_url + '/simulation/download/' + os.path.basename(out['png_path']) if out['png_path'] else None
            return out

        if mode == 'csv':
            # files expected
            if not files or 'file' not in files:
                return {'error': 'CSV file required for csv plotting'}
            header, rows = None, None
            from .utils import read_csv_file
            header, rows = read_csv_file(files['file'])
            x_col = data.get('x_col')
            y_col = data.get('y_col')
            out = plot_from_csv_columns(header, rows, x_col, y_col)
            if host_url:
                out['html_url'] = host_url + '/simulation/download/' + os.path.basename(out['html_path'])
                out['png_url'] = host_url + '/simulation/download/' + os.path.basename(out['png_path']) if out['png_path'] else None
            return out

        if mode == '3d_surface':
            eq = data.get('equation')
            x_min = float(data.get('x_min', -5))
            x_max = float(data.get('x_max', 5))
            y_min = float(data.get('y_min', -5))
            y_max = float(data.get('y_max', 5))
            res = int(data.get('resolution', 100))
            out = plot_surface(eq, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, resolution=res)
            if host_url:
                out['html_url'] = host_url + '/simulation/download/' + os.path.basename(out['html_path'])
            return out

        if mode == '3d_param':
            x_expr = data.get('x_expr')
            y_expr = data.get('y_expr')
            z_expr = data.get('z_expr')
            t_min = float(data.get('t_min', 0))
            t_max = float(data.get('t_max', 10))
            res = int(data.get('resolution', 200))
            out = plot_parametric(x_expr, y_expr, z_expr, t_min=t_min, t_max=t_max, resolution=res)
            if host_url:
                out['html_url'] = host_url + '/simulation/download/' + os.path.basename(out['html_path'])
            return out

        return {'error': 'Unsupported simulation mode'}
    except Exception as e:
        return {'error': str(e)}