import os
import numpy as np
import sympy as sp
import plotly.graph_objs as go
import plotly.io as pio
from .utils import unique_path, ensure_plots_dir


def convert_marker_style_3d(matplotlib_marker):
    """Convert matplotlib marker symbols to Plotly 3D symbols"""
    marker_mapping = {
        'o': 'circle',
        's': 'square', 
        '^': 'triangle-up',
        'v': 'triangle-down',
        '<': 'triangle-left',
        '>': 'triangle-right',
        'D': 'diamond',
        'd': 'diamond-tall',
        '*': 'star',
        '+': 'cross',
        'x': 'x',
        '|': 'line-ns',
        '_': 'line-ew',
        'none': 'circle'  # default for 3D
    }
    return marker_mapping.get(matplotlib_marker, 'circle')  # default to circle if unknown


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


def plot_surface(equation: str, x_min: float=-5, x_max: float=5, y_min: float=-5, y_max: float=5, resolution: int=100, **kwargs):
    """Plot 3D surface with comprehensive customization options.
    
    Customization options:
    - width, height: plot dimensions in pixels
    - dpi: resolution for raster formats (150, 300, 600)
    - format: output format ('png', 'svg', 'pdf')
    - style: plot style theme
    - background_color: background color (hex string)
    - font_size: font size for labels
    - title: custom plot title
    - xlabel, ylabel, zlabel: axis labels
    - grid: show grid (boolean)
    - colormap: color scheme for surface
    """
    ensure_plots_dir()
    
    # Extract customization parameters
    width = kwargs.get('width', 1200)
    height = kwargs.get('height', 800)
    dpi = kwargs.get('dpi', 300)
    fmt = kwargs.get('format', 'png')
    bg_color = kwargs.get('background_color', '#ffffff')
    font_size = kwargs.get('font_size', 12)
    title = kwargs.get('title', f"z = {equation}")
    xlabel = kwargs.get('xlabel', 'x')
    ylabel = kwargs.get('ylabel', 'y')
    zlabel = kwargs.get('zlabel', 'z')
    show_grid = kwargs.get('grid', True)
    colormap = kwargs.get('colormap', 'viridis')
    
    x, y = sp.symbols('x y')
    expr = safe_sympify(equation)
    f = sp.lambdify((x, y), expr, 'numpy')
    xs = np.linspace(x_min, x_max, resolution)
    ys = np.linspace(y_min, y_max, resolution)
    X, Y = np.meshgrid(xs, ys)
    Z = f(X, Y)

    fig = go.Figure(data=[go.Surface(
        z=Z, x=X, y=Y,
        colorscale=colormap,
        showscale=True,
        hovertemplate=f'{xlabel}: %{{x:.4f}}<br>{ylabel}: %{{y:.4f}}<br>{zlabel}: %{{z:.4f}}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=font_size + 4)),
        font=dict(size=font_size),
        paper_bgcolor=bg_color,
        width=width,
        height=height,
        margin=dict(l=60, r=60, t=80, b=60),
        scene=dict(
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            zaxis_title=zlabel,
            xaxis=dict(
                showgrid=show_grid,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)' if show_grid else 'rgba(0,0,0,0)',
                showbackground=True,
                backgroundcolor=bg_color
            ),
            yaxis=dict(
                showgrid=show_grid,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)' if show_grid else 'rgba(0,0,0,0)',
                showbackground=True,
                backgroundcolor=bg_color
            ),
            zaxis=dict(
                showgrid=show_grid,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)' if show_grid else 'rgba(0,0,0,0)',
                showbackground=True,
                backgroundcolor=bg_color
            ),
            bgcolor=bg_color
        ),
        autosize=True
    )

    html_path = unique_path('plot3d_surface', 'html')
    
    # Enhanced Plotly config for better 3D interactivity
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'responsive': True,
        'doubleClick': 'reset+autosize',
        'showTips': True
    }
    
    pio.write_html(
        fig, 
        file=html_path, 
        auto_open=False, 
        include_plotlyjs='cdn',
        config=config,
        div_id="plotly-3d-surface",
        full_html=True
    )

    png_path = unique_path('plot3d_surface', 'png')
    # Note: 3D static rendering may require additional setup
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


def plot_from_csv_xyz(header, rows, x_col: str, y_col: str, z_col: str, **kwargs):
    """Create a 3D plot from CSV columns x,y,z with comprehensive customization options.

    header: list of header names
    rows: list of rows (parsed to floats where possible) as returned by read_csv_file
    
    Customization options:
    - width, height: plot dimensions in pixels
    - dpi: resolution for raster formats (150, 300, 600)
    - format: output format ('png', 'svg', 'pdf')
    - style: plot style theme
    - background_color: background color (hex string)
    - font_size: font size for labels
    - title: custom plot title
    - xlabel, ylabel, zlabel: axis labels
    - grid: show grid (boolean)
    - colormap: color scheme for surface/markers
    - marker_style: marker style for scatter plots
    - marker_size: size of markers
    """
    ensure_plots_dir()
    
    # Extract customization parameters
    width = kwargs.get('width', 1200)
    height = kwargs.get('height', 800)
    dpi = kwargs.get('dpi', 300)
    fmt = kwargs.get('format', 'png')
    bg_color = kwargs.get('background_color', '#ffffff')
    font_size = kwargs.get('font_size', 12)
    title = kwargs.get('title', f'3D Plot: {z_col} vs {x_col}, {y_col}')
    xlabel = kwargs.get('xlabel', x_col)
    ylabel = kwargs.get('ylabel', y_col)
    zlabel = kwargs.get('zlabel', z_col)
    show_grid = kwargs.get('grid', True)
    colormap = kwargs.get('colormap', 'viridis')
    marker_style = kwargs.get('marker_style', 'circle')
    marker_size = kwargs.get('marker_size', 6)
    
    if x_col not in header or y_col not in header or z_col not in header:
        return {'error': f'Columns not found for 3D plot. Available: {header}'}
    xi = header.index(x_col)
    yi = header.index(y_col)
    zi = header.index(z_col)
    
    # Parse data with error checking
    xs_list = []
    ys_list = []
    zs_list = []
    for ridx, r in enumerate(rows, start=1):
        if xi >= len(r) or yi >= len(r) or zi >= len(r):
            return {'error': f'Row {ridx} is missing columns for x/y/z'}
        try:
            xv_f = float(r[xi])
            yv_f = float(r[yi])
            zv_f = float(r[zi])
            xs_list.append(xv_f)
            ys_list.append(yv_f)
            zs_list.append(zv_f)
        except Exception as e:
            return {'error': f"Non-numeric value in row {ridx}: {e}"}
    
    xs = np.array(xs_list, dtype=float)
    ys = np.array(ys_list, dtype=float)
    zs = np.array(zs_list, dtype=float)

    fig = go.Figure()
    plot_type = "scatter"  # Default plot type
    
    # Try to detect grid data (unique x * unique y == npoints) and build a Surface
    ux = np.unique(xs)
    uy = np.unique(ys)
    is_grid = (ux.size * uy.size == xs.size)
    
    if is_grid:
        # Build Z grid by mapping (x,y) -> z
        ux_sorted = np.sort(ux)
        uy_sorted = np.sort(uy)
        # build lookup with rounding to avoid float equality issues
        lookup = {(round(float(x), 8), round(float(y), 8)): float(z) for x, y, z in zip(xs, ys, zs)}
        Z = np.empty((uy_sorted.size, ux_sorted.size), dtype=float)
        ok = True
        for i_y, yv in enumerate(uy_sorted):
            for i_x, xv in enumerate(ux_sorted):
                key = (round(float(xv), 8), round(float(yv), 8))
                if key in lookup:
                    Z[i_y, i_x] = lookup[key]
                else:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            fig.add_trace(go.Surface(
                x=ux_sorted, y=uy_sorted, z=Z, 
                colorscale=colormap, 
                showscale=True,
                hovertemplate=f'{xlabel}: %{{x:.4f}}<br>{ylabel}: %{{y:.4f}}<br>{zlabel}: %{{z:.4f}}<extra></extra>'
            ))
            plot_type = "surface"
        else:
            is_grid = False
    
    if not is_grid:
        # Fallback: use scatter plot with optional mesh
        try:
            # Try mesh first for better 3D visualization
            fig.add_trace(go.Mesh3d(
                x=xs, y=ys, z=zs, 
                intensity=zs, 
                colorscale=colormap, 
                showscale=True, 
                opacity=0.6, 
                flatshading=False,
                hovertemplate=f'{xlabel}: %{{x:.4f}}<br>{ylabel}: %{{y:.4f}}<br>{zlabel}: %{{z:.4f}}<extra></extra>'
            ))
        except Exception:
            # Mesh may fail for scattered points; ignore and continue to scatter only
            pass
        
        # Add scatter points
        plotly_marker_style = convert_marker_style_3d(marker_style)
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs, 
            mode='markers', 
            marker=dict(
                size=marker_size, 
                color=zs, 
                colorscale=colormap, 
                showscale=True,
                symbol=plotly_marker_style
            ),
            name='Data Points',
            hovertemplate=f'{xlabel}: %{{x:.4f}}<br>{ylabel}: %{{y:.4f}}<br>{zlabel}: %{{z:.4f}}<extra></extra>'
        ))
        plot_type = "scatter"
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=font_size + 4)),
        font=dict(size=font_size),
        paper_bgcolor=bg_color,
        width=width,
        height=height,
        margin=dict(l=60, r=60, t=80, b=60),
        scene=dict(
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            zaxis_title=zlabel,
            xaxis=dict(
                showgrid=show_grid,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)' if show_grid else 'rgba(0,0,0,0)',
                showbackground=True,
                backgroundcolor=bg_color
            ),
            yaxis=dict(
                showgrid=show_grid,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)' if show_grid else 'rgba(0,0,0,0)',
                showbackground=True,
                backgroundcolor=bg_color
            ),
            zaxis=dict(
                showgrid=show_grid,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.3)' if show_grid else 'rgba(0,0,0,0)',
                showbackground=True,
                backgroundcolor=bg_color
            ),
            bgcolor=bg_color
        ),
        autosize=True
    )

    html_path = unique_path(f'plot3d_csv_{plot_type}', 'html')
    
    # Enhanced Plotly config for better 3D interactivity
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'responsive': True,
        'doubleClick': 'reset+autosize',
        'showTips': True
    }
    
    pio.write_html(
        fig, 
        file=html_path, 
        auto_open=False, 
        include_plotlyjs='cdn',
        config=config,
        div_id=f"plotly-3d-csv-{plot_type}",
        full_html=True
    )
    
    return {'html_path': html_path, 'png_path': None}
