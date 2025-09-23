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
            
            # Extract customization parameters
            customization_params = {}
            if 'width' in data and data['width']:
                customization_params['width'] = int(data['width'])
            if 'height' in data and data['height']:
                customization_params['height'] = int(data['height'])
            if 'dpi' in data and data['dpi']:
                customization_params['dpi'] = int(data['dpi'])
            if 'format' in data and data['format']:
                customization_params['format'] = data['format']
            if 'style' in data and data['style']:
                customization_params['style'] = data['style']
            if 'line_color' in data and data['line_color']:
                customization_params['line_color'] = data['line_color']
            if 'background_color' in data and data['background_color']:
                customization_params['background_color'] = data['background_color']
            if 'line_width' in data and data['line_width']:
                customization_params['line_width'] = float(data['line_width'])
            if 'marker_style' in data and data['marker_style']:
                customization_params['marker_style'] = data['marker_style']
            if 'marker_size' in data and data['marker_size']:
                customization_params['marker_size'] = float(data['marker_size'])
            if 'font_size' in data and data['font_size']:
                customization_params['font_size'] = int(data['font_size'])
            if 'title' in data and data['title']:
                customization_params['title'] = data['title']
            if 'xlabel' in data and data['xlabel']:
                customization_params['xlabel'] = data['xlabel']
            if 'ylabel' in data and data['ylabel']:
                customization_params['ylabel'] = data['ylabel']
            if 'grid' in data:
                customization_params['grid'] = str(data['grid']).lower() == 'true'
            if 'grid_alpha' in data and data['grid_alpha']:
                customization_params['grid_alpha'] = float(data['grid_alpha'])
            
            # support predefined
            if eq in PREDEFINED_EQUATIONS:
                eq = PREDEFINED_EQUATIONS[eq]
            out = plot_equation_2d(eq, x_min=x_min, x_max=x_max, resolution=res, **customization_params)
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
            if not x_col or not y_col:
                return {'error': 'x_col and y_col must be provided for CSV plotting', 'available_columns': header}
            
            # Extract customization parameters
            customization_params = {}
            if 'width' in data and data['width']:
                customization_params['width'] = int(data['width'])
            if 'height' in data and data['height']:
                customization_params['height'] = int(data['height'])
            if 'dpi' in data and data['dpi']:
                customization_params['dpi'] = int(data['dpi'])
            if 'format' in data and data['format']:
                customization_params['format'] = data['format']
            if 'style' in data and data['style']:
                customization_params['style'] = data['style']
            if 'line_color' in data and data['line_color']:
                customization_params['line_color'] = data['line_color']
            if 'background_color' in data and data['background_color']:
                customization_params['background_color'] = data['background_color']
            if 'line_width' in data and data['line_width']:
                customization_params['line_width'] = float(data['line_width'])
            if 'marker_style' in data and data['marker_style']:
                customization_params['marker_style'] = data['marker_style']
            if 'marker_size' in data and data['marker_size']:
                customization_params['marker_size'] = float(data['marker_size'])
            if 'font_size' in data and data['font_size']:
                customization_params['font_size'] = int(data['font_size'])
            if 'title' in data and data['title']:
                customization_params['title'] = data['title']
            if 'xlabel' in data and data['xlabel']:
                customization_params['xlabel'] = data['xlabel']
            if 'ylabel' in data and data['ylabel']:
                customization_params['ylabel'] = data['ylabel']
            if 'grid' in data:
                customization_params['grid'] = str(data['grid']).lower() == 'true'
            if 'grid_alpha' in data and data['grid_alpha']:
                customization_params['grid_alpha'] = float(data['grid_alpha'])
                
            z_col = data.get('z_col')
            if z_col:
                # 3D CSV plotting with customization
                from .plot_3d import plot_from_csv_xyz
                
                # Extract 3D customization parameters
                customization_params = {}
                if 'width' in data and data['width']:
                    customization_params['width'] = int(data['width'])
                if 'height' in data and data['height']:
                    customization_params['height'] = int(data['height'])
                if 'dpi' in data and data['dpi']:
                    customization_params['dpi'] = int(data['dpi'])
                if 'format' in data and data['format']:
                    customization_params['format'] = data['format']
                if 'style' in data and data['style']:
                    customization_params['style'] = data['style']
                if 'background_color' in data and data['background_color']:
                    customization_params['background_color'] = data['background_color']
                if 'font_size' in data and data['font_size']:
                    customization_params['font_size'] = int(data['font_size'])
                if 'title' in data and data['title']:
                    customization_params['title'] = data['title']
                if 'xlabel' in data and data['xlabel']:
                    customization_params['xlabel'] = data['xlabel']
                if 'ylabel' in data and data['ylabel']:
                    customization_params['ylabel'] = data['ylabel']
                if 'zlabel' in data and data['zlabel']:
                    customization_params['zlabel'] = data['zlabel']
                if 'grid' in data:
                    customization_params['grid'] = str(data['grid']).lower() == 'true'
                if 'colormap' in data and data['colormap']:
                    customization_params['colormap'] = data['colormap']
                if 'marker_style' in data and data['marker_style']:
                    customization_params['marker_style'] = data['marker_style']
                if 'marker_size' in data and data['marker_size']:
                    customization_params['marker_size'] = float(data['marker_size'])
                
                out = plot_from_csv_xyz(header, rows, x_col, y_col, z_col, **customization_params)
            else:
                out = plot_from_csv_columns(header, rows, x_col, y_col, **customization_params)
            if host_url and 'html_path' in out:
                out['html_url'] = host_url + '/simulation/download/' + os.path.basename(out['html_path'])
                if 'png_path' in out and out['png_path']:
                    out['png_url'] = host_url + '/simulation/download/' + os.path.basename(out['png_path'])
            return out

        if mode == '3d_surface':
            eq = data.get('equation')
            x_min = float(data.get('x_min', -5))
            x_max = float(data.get('x_max', 5))
            y_min = float(data.get('y_min', -5))
            y_max = float(data.get('y_max', 5))
            res = int(data.get('resolution', 100))
            
            # Extract 3D customization parameters
            customization_params = {}
            if 'width' in data and data['width']:
                customization_params['width'] = int(data['width'])
            if 'height' in data and data['height']:
                customization_params['height'] = int(data['height'])
            if 'dpi' in data and data['dpi']:
                customization_params['dpi'] = int(data['dpi'])
            if 'format' in data and data['format']:
                customization_params['format'] = data['format']
            if 'style' in data and data['style']:
                customization_params['style'] = data['style']
            if 'background_color' in data and data['background_color']:
                customization_params['background_color'] = data['background_color']
            if 'font_size' in data and data['font_size']:
                customization_params['font_size'] = int(data['font_size'])
            if 'title' in data and data['title']:
                customization_params['title'] = data['title']
            if 'xlabel' in data and data['xlabel']:
                customization_params['xlabel'] = data['xlabel']
            if 'ylabel' in data and data['ylabel']:
                customization_params['ylabel'] = data['ylabel']
            if 'zlabel' in data and data['zlabel']:
                customization_params['zlabel'] = data['zlabel']
            if 'grid' in data:
                customization_params['grid'] = str(data['grid']).lower() == 'true'
            if 'colormap' in data and data['colormap']:
                customization_params['colormap'] = data['colormap']
            
            out = plot_surface(eq, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, resolution=res, **customization_params)
            if host_url and 'html_path' in out:
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