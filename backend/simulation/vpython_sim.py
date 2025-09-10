"""Generate embeddable VPython (GlowScript) HTML simulations.

Supported modes:
- 'vector': show a 3D arrow at the origin with optional animation.
- 'orbit': simple two-body orbit demo (runs client-side in VPython).

This module returns saved HTML file path and a download URL when a host_url
is provided.
"""
from typing import Dict, Any
from .utils import unique_path, ensure_plots_dir
import os


GLOWSCRIPT_CDN = "https://www.glowscript.org/lib/glow/v1.5.0/glow.js"

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
    """Create a GlowScript HTML file for the requested sim and return paths.

    Expected data keys:
    - mode: 'vector' or 'orbit'
    For 'vector': vx, vy, vz (floats), animate (bool)
    For 'orbit': rx, ry, rz, vx, vy, vz, G, M, dt
    """
    ensure_plots_dir()
    mode = (data.get('mode') or 'vector').lower()
    preset = (data.get('preset') or '').lower()
    html_code = ''
    warnings = []
    # preset-based scenes
    if preset == 'electric':
        E = _clamp_val('E_strength', data.get('E_strength', 1.0), MIN_STRENGTH, MAX_STRENGTH, warnings)
        grid = int(max(1, min(int(data.get('grid', 5)), MAX_GRID)))
        if grid != int(data.get('grid', 5)):
            warnings.append(f"grid clamped to {grid}")
        sim_py = _electric_field_code(E_strength=E, grid=grid)
    elif preset == 'magnetic':
        B = _clamp_val('B_strength', data.get('B_strength', 1.0), MIN_STRENGTH, MAX_STRENGTH, warnings)
        grid = int(max(1, min(int(data.get('grid', 5)), MAX_GRID)))
        sim_py = _magnetic_field_code(B_strength=B, grid=grid)
    elif preset == 'gravity':
        mass = _clamp_val('mass', data.get('mass', 10.0), 0.1, 1e6, warnings)
        sim_py = _gravity_field_code(mass=mass)
    elif preset == 'dipole' or preset == 'electric_dipole':
        sep = _clamp_val('separation', data.get('separation', 2.0), 0.1, 10.0, warnings)
        q = _clamp_val('charge', data.get('charge', 1.0), -MAX_STRENGTH, MAX_STRENGTH, warnings)
        grid = int(max(1, min(int(data.get('grid', 5)), MAX_GRID)))
        sim_py = _electric_dipole_code(separation=sep, q=q, grid=grid)
    elif preset == 'field_lines':
        k = _clamp_val('strength', data.get('strength', 1.0), MIN_STRENGTH, MAX_STRENGTH, warnings)
        lines = int(max(1, min(int(data.get('lines', 12)), MAX_STREAMLINES)))
        sim_py = _field_lines_code(strength=k, lines=lines)
    elif preset == 'multiple_charges':
        n = int(max(1, min(int(data.get('n_charges', 4)), MAX_CHARGES)))
        q = _clamp_val('charge', data.get('charge', 1.0), -MAX_STRENGTH, MAX_STRENGTH, warnings)
        sim_py = _multiple_charges_code(n=n, q=q)
    elif preset == 'particle_in_eb' or preset == 'charged_particle':
        # Electric and magnetic field strengths and number of trajectories
        E = _clamp_val('E_strength', data.get('E_strength', 0.0), -MAX_STRENGTH, MAX_STRENGTH, warnings)
        B = _clamp_val('B_strength', data.get('B_strength', 1.0), -MAX_STRENGTH, MAX_STRENGTH, warnings)
        traj = int(max(1, min(int(data.get('trajectories', 1)), MAX_PARTICLE_TRAJ)))
        sim_py = _particle_trajectory_code(E=E, B=B, trajectories=traj)
    else:
        # fallback to older mode behavior
        if mode == 'vector':
            vx = float(data.get('vx', 1.0))
            vy = float(data.get('vy', 1.0))
            vz = float(data.get('vz', 0.0))
            animate = str(data.get('animate', 'true')).lower() in ('1', 'true', 'yes')
            sim_py = _vector_sim_code(vx, vy, vz, animate)
        elif mode == 'orbit':
            rx = float(data.get('rx', 10.0))
            ry = float(data.get('ry', 0.0))
            rz = float(data.get('rz', 0.0))
            vx = float(data.get('vx', 0.0))
            vy = float(data.get('vy', 0.7))
            vz = float(data.get('vz', 0.0))
            G = float(data.get('G', 1.0))
            M = float(data.get('M', 1000.0))
            dt = float(data.get('dt', 0.01))
            sim_py = _orbit_sim_code(rx, ry, rz, vx, vy, vz, G=G, M=M, dt=dt)
        else:
            sim_py = "from vpython import scene\nscene.append_to_caption('Unknown mode')\n"

    # wrap into simple HTML using GlowScript
    html_code = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\"> 
  <script src=\"{GLOWSCRIPT_CDN}\"></script>
  <style>body {{margin:0;}}</style>
</head>
<body>
  <script type=\"text/python\">\n{sim_py}\n  </script>
</body>
</html>
"""

    out_path = unique_path('vpython_sim', 'html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_code)

    filename = os.path.basename(out_path)
    result = {'html_path': out_path}
    if host_url:
        result['html_url'] = f"{host_url}/simulation/download/{filename}"
    return result


def _electric_field_code(E_strength=1.0, grid=5):
    """Create arrows representing an electric field of a point charge at origin."""
    s = []
    s.append("from vpython import scene, arrow, vector, color, rate, sphere")
    s.append("scene.title='Electric field (point charge at origin)'")
    s.append("q = sphere(pos=vector(0,0,0), radius=0.5, color=color.yellow)")
    s.append(f"k = {E_strength}")
    rng = range(-grid, grid+1)
    s.append("# arrows grid")
    for x in rng:
        for y in rng:
            for z in (0,):
                s.append(f"p = vector({x}, {y}, {z})")
                s.append("r = p - q.pos")
                s.append("magr = max(0.1, r.mag)")
                s.append("E = k * r / magr**3")
                s.append("arrow(pos=p, axis=E, color=color.cyan, shaftwidth=0.05)")
    return '\n'.join(s)


def _magnetic_field_code(B_strength=1.0, grid=5):
    """Create arrows for a uniform magnetic field along z and a moving charged particle."""
    s = []
    s.append("from vpython import scene, arrow, vector, color, rate, sphere, mag")
    s.append("scene.title='Magnetic field (uniform B along z)'")
    s.append(f"B = vector(0,0,{B_strength})")
    s.append("# static field arrows on xy grid")
    rng = range(-grid, grid+1)
    for x in rng:
        for y in rng:
            s.append(f"arrow(pos=vector({x},{y},0), axis=B*0.5, color=color.green, shaftwidth=0.05)")
    s.append("# moving charged particle experiencing Lorentz force")
    s.append("particle = sphere(pos=vector(-5,0,0), radius=0.3, color=color.red, make_trail=True)")
    s.append("v = vector(0,1.5,0)")
    s.append("q = 1")
    s.append("m = 1")
    s.append("dt = 0.02")
    s.append("while True:")
    s.append("    rate(200)")
    s.append("    F = q * (v.cross(B))")
    s.append("    a = F/m")
    s.append("    v = v + a*dt")
    s.append("    particle.pos = particle.pos + v*dt")
    return '\n'.join(s)


def _gravity_field_code(mass=10.0):
    s = []
    s.append("from vpython import scene, sphere, vector, color, rate")
    s.append("scene.title='Gravity demo (point mass at origin)'")
    s.append(f"M = {mass}")
    s.append("sun = sphere(pos=vector(0,0,0), radius=1.5, color=color.yellow)")
    s.append("planet = sphere(pos=vector(0,8,0), radius=0.4, color=color.blue, make_trail=True)")
    s.append("v = vector(1.2,0,0)")
    s.append("G = 1")
    s.append("dt = 0.01")
    s.append("while True:")
    s.append("    rate(100)")
    s.append("    r = planet.pos - sun.pos")
    s.append("    a = -G * M * r / r.mag**3")
    s.append("    v = v + a*dt")
    s.append("    planet.pos = planet.pos + v*dt")
    return '\n'.join(s)


def _electric_dipole_code(separation=2.0, q=1.0, grid=5):
    s = []
    s.append("from vpython import scene, arrow, vector, color, sphere, mag")
    s.append("scene.title='Electric dipole field'")
    s.append(f"pos_plus = vector({separation/2},0,0)")
    s.append(f"pos_minus = vector({-separation/2},0,0)")
    s.append("p_plus = sphere(pos=pos_plus, radius=0.4, color=color.red)")
    s.append("p_minus = sphere(pos=pos_minus, radius=0.4, color=color.blue)")
    s.append(f"k = {q}")
    s.append("# grid of arrows in the xy plane")
    rng = range(-grid, grid+1)
    for x in rng:
        for y in rng:
            s.append(f"p = vector({x},{y},0)")
            s.append("r = p - pos_plus")
            s.append("r2 = p - pos_minus")
            s.append("E = k * r / max(0.1, r.mag)**3 - k * r2 / max(0.1, r2.mag)**3")
            s.append("arrow(pos=p, axis=E*0.5, color=color.cyan, shaftwidth=0.04)")
    return '\n'.join(s)


def _field_lines_code(strength=1.0, lines=12):
    s = []
    s.append("from vpython import scene, sphere, vector, color, curve, mag, rate")
    s.append("scene.title='Field lines (sample)'")
    s.append("q = sphere(pos=vector(0,0,0), radius=0.4, color=color.yellow)")
    s.append(f"k = {strength}")
    s.append("import math")
    s.append("for i in range(%d):" % lines)
    s.append("    theta = 2*math.pi*i/float(%d)" % lines)
    s.append("    p = vector(1.0*math.cos(theta), 1.0*math.sin(theta), 0)")
    s.append("    pts = []")
    s.append("    for t in range(60):")
    s.append("        r = p - q.pos")
    s.append("        E = k * r / max(0.1, r.mag)**3")
    s.append("        p = p + E*0.1")
    s.append("        pts.append(p)")
    s.append("    curve(pos=pts, radius=0.02, color=color.cyan)")
    return '\n'.join(s)


def _multiple_charges_code(n=4, q=1.0):
    s = []
    s.append("from vpython import scene, sphere, vector, color, arrow, mag")
    s.append("scene.title='Multiple charges (sample)'")
    s.append("positions = []")
    s.append("import math")
    for i in range(n):
        angle = 2*3.14159*i/max(1,n)
        s.append(f"pos{i} = vector({3*'math.cos(angle)'} , 3*math.sin(angle), 0)")
    # fallback simple setup with fixed positions to avoid eval complexity
    s.append("# sample static charges")
    s.append("charges = [ (vector(2,0,0), 1), (vector(-2,0,0), -1) ]")
    s.append("for p,qq in charges:")
    s.append("    sphere(pos=p, radius=0.3, color=(color.red if qq>0 else color.blue))")
    s.append("# show field arrows on a small grid")
    s.append("for x in range(-3,4):")
    s.append("  for y in range(-3,4):")
    s.append("    p = vector(x,y,0)")
    s.append("    E = vector(0,0,0)")
    s.append("    for pc,qq in charges:")
    s.append("        r = p-pc")
    s.append("        E = E + qq * r / max(0.1, r.mag)**3")
    s.append("    arrow(pos=p, axis=E*0.5, color=color.cyan, shaftwidth=0.03)")
    return '\n'.join(s)


def _particle_trajectory_code(E=0.0, B=1.0, trajectories=1):
    s = []
    s.append("from vpython import scene, sphere, vector, color, rate, mag")
    s.append("scene.title='Charged particle in E and B fields'")
    s.append(f"E = vector({E},0,0)")
    s.append(f"B = vector(0,0,{B})")
    s.append("dt = 0.01")
    for i in range(trajectories):
        s.append(f"p{i} = sphere(pos=vector(-4,{i*0.8-0.8},0), radius=0.2, color=color.red, make_trail=True)")
        s.append(f"v{i} = vector(0,1.5,0)")
        s.append(f"q{i} = 1")
        s.append(f"m{i} = 1")
        s.append(f"# trajectory loop for particle {i}")
        s.append("while True:")
        s.append("    rate(200)")
        s.append(f"    F = q{i} * (v{i}.cross(B) + E)")
        s.append(f"    a = F/m{i}")
        s.append(f"    v{i} = v{i} + a*dt")
        s.append(f"    p{i}.pos = p{i}.pos + v{i}*dt")
    return '\n'.join(s)


def _solar_system_code(scale=1.0, speed=1.0, planets='all'):
    """Generate a beautiful, interactive solar system demo using VPython.

    - scale: spatial scale multiplier
    - speed: simulation speed multiplier
    - planets: 'all' or 'inner' (Mercury->Mars)
    """
    s = []
    s.append("from vpython import scene, sphere, vector, color, rate, local_light, label")
    s.append("scene.title='Solar System (sample)'")
    s.append("scene.background = color.black")
    s.append("sun = sphere(pos=vector(0,0,0), radius=1.2, color=color.yellow, emissive=True)")
    s.append("local_light(pos=vector(0,0,0), color=color.white)")
    s.append("GLOB_SCALE = %f" % float(scale))
    s.append("SPEED = %f" % float(speed))
    # simple planet data: name, color, radius (visual), distance (AU-like), period (arbitrary units)
    s.append("planets = []")
    s.append("# name, color, vis_radius, dist, period")
    s.append("planet_data = [")
    s.append("  ('Mercury', color.gray(0.6), 0.2, 1.6, 0.24),")
    s.append("  ('Venus', color.orange, 0.3, 2.8, 0.62),")
    s.append("  ('Earth', color.blue, 0.32, 4.0, 1.0),")
    s.append("  ('Mars', color.red, 0.28, 6.0, 1.88),")
    s.append("  ('Jupiter', color.orange, 0.9, 11.0, 11.86),")
    s.append("  ('Saturn', color.yellow, 0.7, 18.0, 29.46),")
    s.append("  ('Uranus', color.cyan, 0.5, 25.0, 84.01),")
    s.append("  ('Neptune', color.blue, 0.5, 30.0, 164.8)")
    s.append("]")
    s.append("for (name, col, rr, dist, period) in planet_data:")
    s.append("    planets.append({'name':name,'color':col,'radius':rr,'dist':dist,'period':period})")
    s.append("# choose subset")
    s.append("if '%s' == 'inner':" % planets)
    s.append("    planets = planets[:4]")
    s.append("# create visual planets")
    s.append("objs = []")
    s.append("for p in planets:")
    s.append("    obj = sphere(pos=vector(p['dist']*GLOB_SCALE,0,0), radius=p['radius']*GLOB_SCALE*0.4, color=p['color'], make_trail=True, retain=200)")
    s.append("    obj._ang = 0")
    s.append("    objs.append((obj,p))")
    s.append("# optional labels")
    s.append("for o,p in objs:")
    s.append("    label(pos=o.pos, text=p['name'], xoffset=10, yoffset=10, space=30, height=10, border=0)")
    s.append("# simulation loop")
    s.append("while True:")
    s.append("    rate(100)")
    s.append("    for o,p in objs:")
    s.append("        # simple circular motion with period scaling")
    s.append("        o._ang += (2*3.14159/(p['period']*50.0)) * SPEED")
    s.append("        x = p['dist']*GLOB_SCALE * cos(o._ang)")
    s.append("        y = p['dist']*GLOB_SCALE * sin(o._ang)")
    s.append("        o.pos = vector(x,y,0)")
    s.append("        # keep label near planet")
    s.append("        # labels auto-follow if implemented in viewer")
    return '\n'.join(s)

    # wrap into simple HTML using GlowScript
    html_code = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\"> 
  <script src=\"{GLOWSCRIPT_CDN}\"></script>
  <style>body {{margin:0;}}</style>
</head>
<body>
  <script type=\"text/python\">\n{sim_py}\n  </script>
</body>
</html>
"""

    out_path = unique_path('vpython_sim', 'html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_code)

    filename = os.path.basename(out_path)
    result = {'html_path': out_path}
    if host_url:
        result['html_url'] = f"{host_url}/simulation/download/{filename}"
    return result
