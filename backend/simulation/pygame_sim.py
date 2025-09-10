"""Headless Pygame-based 2D particle simulation.

This module provides a function `run_particle_simulation` which can be used
by the Flask route to run a short particle / collisions simulation and
export either a sequence of PNG frames or an animated GIF (if imageio available).

The implementation runs without an X display by creating Surfaces directly.
If `pygame` is not installed the function returns an error dict explaining how
to install it.
"""
import os
import time
import math
import random
from typing import Dict, Any

try:
    import pygame
except Exception:
    pygame = None

try:
    import imageio
except Exception:
    imageio = None

from .utils import ensure_plots_dir, unique_path


def _elastic_collision(p1, p2):
    # p: dict with x,y,vx,vy,r
    dx = p2['x'] - p1['x']
    dy = p2['y'] - p1['y']
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    nx = dx / dist
    ny = dy / dist
    # relative velocity
    dvx = p1['vx'] - p2['vx']
    dvy = p1['vy'] - p2['vy']
    rel = dvx * nx + dvy * ny
    if rel > 0:
        return
    # simple equal-mass impulse
    impulse = -2 * rel / 2
    p1['vx'] += impulse * nx
    p1['vy'] += impulse * ny
    p2['vx'] -= impulse * nx
    p2['vy'] -= impulse * ny


def run_particle_simulation(params: Dict[str, Any], host_url: str = '') -> Dict[str, Any]:
    """Run a simple particle simulation.

    params (dict):
      - n: number of particles (default 10)
      - steps: number of frames (default 120)
      - width, height: canvas size
      - radius: particle radius
      - save_gif: bool

    Returns dict with 'frames' (list of filenames) and optional 'gif' key.
    """
    if pygame is None:
        return {'error': "pygame is not installed. Install it with 'pip install pygame' to run simulations."}

    n = int(params.get('n', 10))
    steps = int(params.get('steps', 120))
    width = int(params.get('width', 640))
    height = int(params.get('height', 480))
    radius = int(params.get('radius', 6))
    save_gif = bool(params.get('save_gif', True))
    bg_color = tuple(params.get('bg_color', (20, 20, 30)))

    ensure_plots_dir()
    prefix = f'pygame_sim'
    frame_paths = []

    # Initialize particles
    particles = []
    for i in range(n):
        particles.append({
            'x': random.uniform(radius, width - radius),
            'y': random.uniform(radius, height - radius),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'r': radius,
            'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        })

    # Use an off-screen surface
    surface = pygame.Surface((width, height))

    for t in range(steps):
        # update
        for p in particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            # bounce walls
            if p['x'] - p['r'] <= 0:
                p['x'] = p['r']
                p['vx'] *= -1
            if p['x'] + p['r'] >= width:
                p['x'] = width - p['r']
                p['vx'] *= -1
            if p['y'] - p['r'] <= 0:
                p['y'] = p['r']
                p['vy'] *= -1
            if p['y'] + p['r'] >= height:
                p['y'] = height - p['r']
                p['vy'] *= -1

        # collisions
        for i in range(n):
            for j in range(i + 1, n):
                p1 = particles[i]
                p2 = particles[j]
                dx = p2['x'] - p1['x']
                dy = p2['y'] - p1['y']
                dist = math.hypot(dx, dy)
                if dist < p1['r'] + p2['r']:
                    # simple correction
                    overlap = 0.5 * (p1['r'] + p2['r'] - dist + 1e-6)
                    if dist > 0:
                        nx = dx / dist
                        ny = dy / dist
                    else:
                        nx, ny = 1.0, 0.0
                    p1['x'] -= nx * overlap
                    p1['y'] -= ny * overlap
                    p2['x'] += nx * overlap
                    p2['y'] += ny * overlap
                    _elastic_collision(p1, p2)

        # draw
        surface.fill(bg_color)
        for p in particles:
            pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), p['r'])

        # save frame
        frame_path = unique_path(prefix, 'png')
        try:
            pygame.image.save(surface, frame_path)
            frame_paths.append(frame_path)
        except Exception as e:
            return {'error': f'Failed to save frame: {e}'}

    gif_path = None
    if save_gif:
        if imageio is None:
            # return frames only
            return {'frames': frame_paths}
        try:
            imgs = [imageio.imread(p) for p in frame_paths]
            gif_path = unique_path(prefix, 'gif')
            imageio.mimsave(gif_path, imgs, fps=24)
        except Exception as e:
            return {'error': f'Failed to write gif: {e}', 'frames': frame_paths}

    out = {'frames': frame_paths}
    if gif_path:
        out['gif'] = gif_path
        if host_url:
            out['gif_url'] = host_url + '/simulation/download/' + os.path.basename(gif_path)
    return out
