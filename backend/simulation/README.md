Simulation subsystem

Endpoints

- POST /simulation/plot2d : form or JSON { mode: 'equation', equation: 'sin(x)', x_min, x_max, resolution } returns { html_path, png_path, html_url, png_url }
- POST /simulation/plot_csv : form-data file=@data.csv, x_col, y_col returns interactive html and png
- POST /simulation/plot3d : JSON { mode: '3d_surface' | '3d_param', ... } returns html
- GET /simulation/download/<filename> : download generated asset

Notes

- Interactive HTML uses Plotly and is saved under backend/plots. PNG fallbacks are provided for 2D.
- For production, consider cleaning old plots and using signed URLs.

## Pygame particle simulation

- POST /simulation/pygame with JSON form-data:
  - n: number of particles (default 10)
  - steps: frames to simulate (default 120)
  - width, height: canvas size
  - radius: particle radius
  - save_gif: boolean (default true)

Return:

- JSON with `frames` (list of generated PNG paths) and optional `gif` (path) and `gif_url` if host available.

Note: Requires `pygame` (and `imageio` for GIF). Install with `pip install pygame imageio`.
