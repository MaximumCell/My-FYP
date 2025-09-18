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


def plot_equation_2d(equation: str, x_min: float = -10, x_max: float = 10, resolution: int = 1000, **kwargs):
    """Return dict with 'html_path' and 'png_path' of plotted equation z=f(x).
    
    Customization options:
    - width, height: plot dimensions in pixels
    - dpi: resolution for raster formats (150, 300, 600)
    - format: output format ('png', 'svg', 'pdf')
    - style: matplotlib style ('default', 'seaborn', 'ggplot', 'dark_background', 'bmh')
    - line_color: color for the plot line (hex string)
    - background_color: background color (hex string)
    - line_width: width of the plot line
    - marker_style: marker style ('none', 'o', 's', '^', 'D', '*')
    - marker_size: size of markers
    - font_size: font size for labels
    - title: custom plot title
    - xlabel, ylabel: axis labels
    - grid: show grid (boolean)
    - grid_alpha: grid transparency (0-1)
    """
    ensure_plots_dir()
    
    # Extract customization parameters
    width = kwargs.get('width', 800)
    height = kwargs.get('height', 600)
    dpi = kwargs.get('dpi', 150)
    fmt = kwargs.get('format', 'png')
    style = kwargs.get('style', 'default')
    line_color = kwargs.get('line_color', '#2563eb')
    bg_color = kwargs.get('background_color', '#ffffff')
    line_width = kwargs.get('line_width', 2)
    marker_style = kwargs.get('marker_style', 'none')
    marker_size = kwargs.get('marker_size', 6)
    font_size = kwargs.get('font_size', 12)
    title = kwargs.get('title', f"y = {equation}")
    xlabel = kwargs.get('xlabel', 'x')
    ylabel = kwargs.get('ylabel', 'y')
    show_grid = kwargs.get('grid', True)
    grid_alpha = kwargs.get('grid_alpha', 0.3)
    
    x = sp.symbols('x')
    expr = safe_sympify(equation)
    f = sp.lambdify(x, expr, 'numpy')
    xs = np.linspace(x_min, x_max, resolution)
    ys = f(xs)

    # Plotly interactive
    fig = go.Figure()
    marker_dict = {} if marker_style == 'none' else {'symbol': marker_style, 'size': marker_size}
    mode = 'lines' if marker_style == 'none' else 'lines+markers'
    
    fig.add_trace(go.Scatter(
        x=xs, y=ys, 
        mode=mode,
        line=dict(color=line_color, width=line_width),
        marker=marker_dict,
        name='y = f(x)',
        hovertemplate='x: %{x:.4f}<br>y: %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=font_size + 4)),
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        font=dict(size=font_size),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        showlegend=False,
        width=width,
        height=height,
        margin=dict(l=60, r=60, t=80, b=60),
        hovermode='closest',
        # Enable responsive behavior
        autosize=True
    )
    
    # Enhanced interactivity
    fig.update_layout(
        xaxis=dict(
            showgrid=show_grid,
            gridwidth=1,
            gridcolor='rgba(128,128,128,' + str(grid_alpha) + ')',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(0,0,0,0.5)',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot'
        ),
        yaxis=dict(
            showgrid=show_grid,
            gridwidth=1,
            gridcolor='rgba(128,128,128,' + str(grid_alpha) + ')',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(0,0,0,0.5)',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot'
        )
    )

    html_path = unique_path('plot2d', 'html')
    
    # Enhanced Plotly config for better interactivity
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
        'responsive': True,
        'scrollZoom': True,
        'doubleClick': 'reset+autosize',
        'showTips': True
    }
    
    pio.write_html(
        fig, 
        file=html_path, 
        auto_open=False, 
        include_plotlyjs='cdn',
        config=config,
        div_id="plotly-plot",
        full_html=True
    )

    # Enhanced matplotlib plot
    if style != 'default':
        try:
            plt.style.use(style)
        except:
            pass  # fallback to default if style not found
    
    fig_inches_w = width / dpi
    fig_inches_h = height / dpi
    plt.figure(figsize=(fig_inches_w, fig_inches_h), dpi=dpi, facecolor=bg_color)
    
    # Plot with customization
    plot_kwargs = {'color': line_color, 'linewidth': line_width}
    if marker_style != 'none':
        plot_kwargs['marker'] = marker_style
        plot_kwargs['markersize'] = marker_size
    
    plt.plot(xs, ys, **plot_kwargs)
    plt.title(title, fontsize=font_size)
    plt.xlabel(xlabel, fontsize=font_size)
    plt.ylabel(ylabel, fontsize=font_size)
    
    if show_grid:
        plt.grid(True, alpha=grid_alpha)
    
    # Set background color
    plt.gca().set_facecolor(bg_color)
    
    # Save in requested format
    output_path = unique_path('plot2d', fmt)
    try:
        plt.savefig(output_path, bbox_inches='tight', dpi=dpi, facecolor=bg_color)
    except Exception as e:
        print(f"Error saving plot: {e}")
        # fallback to PNG if other format fails
        output_path = unique_path('plot2d', 'png')
        plt.savefig(output_path, bbox_inches='tight', dpi=dpi, facecolor=bg_color)
    plt.close()

    return {'html_path': html_path, 'png_path': output_path}


def plot_from_csv_columns(header, rows, x_col: str, y_col: str, **kwargs):
    """Plot CSV data with advanced customization options.
    
    Customization options:
    - width, height: plot dimensions in pixels
    - dpi: resolution for raster formats (150, 300, 600)
    - format: output format ('png', 'svg', 'pdf')
    - style: matplotlib style ('default', 'seaborn', 'ggplot', 'dark_background', 'bmh')
    - line_color: color for the plot line (hex string)
    - background_color: background color (hex string)
    - line_width: width of the plot line
    - marker_style: marker style ('none', 'o', 's', '^', 'D', '*')
    - marker_size: size of markers
    - font_size: font size for labels
    - title: custom plot title
    - xlabel, ylabel: axis labels
    - grid: show grid (boolean)
    - grid_alpha: grid transparency (0-1)
    """
    ensure_plots_dir()
    
    # Extract customization parameters
    width = kwargs.get('width', 800)
    height = kwargs.get('height', 600)
    dpi = kwargs.get('dpi', 150)
    fmt = kwargs.get('format', 'png')
    style = kwargs.get('style', 'default')
    line_color = kwargs.get('line_color', '#2563eb')
    bg_color = kwargs.get('background_color', '#ffffff')
    line_width = kwargs.get('line_width', 2)
    marker_style = kwargs.get('marker_style', 'o')  # default to markers for CSV data
    marker_size = kwargs.get('marker_size', 6)
    font_size = kwargs.get('font_size', 12)
    title = kwargs.get('title', f'{y_col} vs {x_col}')
    xlabel = kwargs.get('xlabel', x_col)
    ylabel = kwargs.get('ylabel', y_col)
    show_grid = kwargs.get('grid', True)
    grid_alpha = kwargs.get('grid_alpha', 0.3)
    
    if not header:
        return {'error': 'CSV header not found or CSV is empty'}
    if x_col not in header or y_col not in header:
        return {'error': f"Columns not found. Available columns: {header}"}
    xi = header.index(x_col)
    yi = header.index(y_col)
    if not rows:
        return {'error': 'CSV contains no data rows'}

    xs_list = []
    ys_list = []
    for ridx, r in enumerate(rows, start=1):
        # ensure row has enough columns
        if xi >= len(r) or yi >= len(r):
            return {'error': f'Row {ridx} is missing columns for x/y'}
        xv = r[xi]
        yv = r[yi]
        try:
            xv_f = float(xv)
        except Exception:
            return {'error': f"Non-numeric value '{xv}' in column '{x_col}' at row {ridx}"}
        try:
            yv_f = float(yv)
        except Exception:
            return {'error': f"Non-numeric value '{yv}' in column '{y_col}' at row {ridx}"}
        xs_list.append(xv_f)
        ys_list.append(yv_f)

    xs = np.array(xs_list, dtype=float)
    ys = np.array(ys_list, dtype=float)

    # Plotly interactive
    fig = go.Figure()
    marker_dict = {} if marker_style == 'none' else {'symbol': marker_style, 'size': marker_size}
    mode = 'lines' if marker_style == 'none' else 'lines+markers'
    
    fig.add_trace(go.Scatter(
        x=xs, y=ys, 
        mode=mode,
        line=dict(color=line_color, width=line_width),
        marker=marker_dict,
        name=f'{y_col} vs {x_col}',
        hovertemplate=f'{x_col}: %{{x:.4f}}<br>{y_col}: %{{y:.4f}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=font_size + 4)),
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        font=dict(size=font_size),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        showlegend=False,
        width=width,
        height=height,
        margin=dict(l=60, r=60, t=80, b=60),
        hovermode='closest',
        # Enable responsive behavior
        autosize=True
    )
    
    # Enhanced interactivity
    fig.update_layout(
        xaxis=dict(
            showgrid=show_grid,
            gridwidth=1,
            gridcolor='rgba(128,128,128,' + str(grid_alpha) + ')',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(0,0,0,0.5)',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot'
        ),
        yaxis=dict(
            showgrid=show_grid,
            gridwidth=1,
            gridcolor='rgba(128,128,128,' + str(grid_alpha) + ')',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(0,0,0,0.5)',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikedash='dot'
        )
    )

    html_path = unique_path('plot2d_csv', 'html')
    
    # Enhanced Plotly config for better interactivity
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
        'responsive': True,
        'scrollZoom': True,
        'doubleClick': 'reset+autosize',
        'showTips': True
    }
    
    pio.write_html(
        fig, 
        file=html_path, 
        auto_open=False, 
        include_plotlyjs='cdn',
        config=config,
        div_id="plotly-csv-plot",
        full_html=True
    )

    # Enhanced matplotlib plot
    if style != 'default':
        try:
            plt.style.use(style)
        except:
            pass  # fallback to default if style not found
    
    fig_inches_w = width / dpi
    fig_inches_h = height / dpi
    plt.figure(figsize=(fig_inches_w, fig_inches_h), dpi=dpi, facecolor=bg_color)
    
    # Plot with customization
    plot_kwargs = {'color': line_color, 'linewidth': line_width}
    if marker_style != 'none':
        plot_kwargs['marker'] = marker_style
        plot_kwargs['markersize'] = marker_size
    
    plt.plot(xs, ys, **plot_kwargs)
    plt.title(title, fontsize=font_size)
    plt.xlabel(xlabel, fontsize=font_size)
    plt.ylabel(ylabel, fontsize=font_size)
    
    if show_grid:
        plt.grid(True, alpha=grid_alpha)
    
    # Set background color
    plt.gca().set_facecolor(bg_color)
    
    # Save in requested format
    output_path = unique_path('plot2d_csv', fmt)
    try:
        plt.savefig(output_path, bbox_inches='tight', dpi=dpi, facecolor=bg_color)
    except Exception as e:
        print(f"Error saving CSV plot: {e}")
        # fallback to PNG if other format fails
        output_path = unique_path('plot2d_csv', 'png')
        plt.savefig(output_path, bbox_inches='tight', dpi=dpi, facecolor=bg_color)
    plt.close()
    
    return {'html_path': html_path, 'png_path': output_path}
