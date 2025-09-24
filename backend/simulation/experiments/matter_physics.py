"""
Matter.js Physics Simulations
Backend endpoints for mechanical physics using Matter.js
Includes: Pendulum, Collisions, Springs, Projectile Motion
"""

def generate_pendulum_config(params=None):
    """Generate configuration for pendulum simulation"""
    if params is None:
        params = {
            'length': 200,
            'mass': 1,
            'gravity': 0.8,
            'damping': 0.99,
            'angle': 45
        }
    
    return {
        'type': 'pendulum',
        'config': {
            'pendulum': {
                'length': params.get('length', 200),
                'mass': params.get('mass', 1),
                'bobRadius': max(10, params.get('mass', 1) * 10),
                'initialAngle': params.get('angle', 45) * 3.14159 / 180,  # Convert to radians
                'anchorX': 400,
                'anchorY': 50
            },
            'world': {
                'gravity': params.get('gravity', 0.8),
                'damping': params.get('damping', 0.99)
            },
            'display': {
                'width': 800,
                'height': 600,
                'showTrail': params.get('showTrail', True),
                'showForces': params.get('showForces', False)
            }
        },
        'controls': {
            'length': {'min': 50, 'max': 300, 'value': params.get('length', 200)},
            'mass': {'min': 0.5, 'max': 3, 'value': params.get('mass', 1)},
            'gravity': {'min': 0.1, 'max': 2, 'value': params.get('gravity', 0.8)},
            'damping': {'min': 0.95, 'max': 1, 'value': params.get('damping', 0.99)},
            'angle': {'min': 5, 'max': 85, 'value': params.get('angle', 45)}
        }
    }

def generate_collision_config(params=None):
    """Generate configuration for collision simulation"""
    if params is None:
        params = {
            'ballCount': 8,
            'restitution': 0.8,
            'friction': 0.1,
            'airResistance': 0.01
        }
    
    return {
        'type': 'collision',
        'config': {
            'balls': {
                'count': params.get('ballCount', 8),
                'minRadius': 15,
                'maxRadius': 30,
                'restitution': params.get('restitution', 0.8),
                'friction': params.get('friction', 0.1),
                'density': 0.001
            },
            'world': {
                'gravity': 0.8,
                'airResistance': params.get('airResistance', 0.01),
                'bounds': {
                    'width': 800,
                    'height': 600,
                    'wallThickness': 20
                }
            },
            'display': {
                'width': 800,
                'height': 600,
                'showVelocityVectors': params.get('showVectors', False),
                'showTrails': params.get('showTrails', False)
            }
        },
        'controls': {
            'ballCount': {'min': 3, 'max': 15, 'value': params.get('ballCount', 8)},
            'restitution': {'min': 0.1, 'max': 1, 'value': params.get('restitution', 0.8)},
            'friction': {'min': 0, 'max': 0.5, 'value': params.get('friction', 0.1)},
            'airResistance': {'min': 0, 'max': 0.05, 'value': params.get('airResistance', 0.01)}
        }
    }

def generate_spring_config(params=None):
    """Generate configuration for spring-mass system simulation"""
    if params is None:
        params = {
            'springConstant': 0.05,
            'mass': 1.5,
            'damping': 0.98,
            'initialDisplacement': 100
        }
    
    return {
        'type': 'spring',
        'config': {
            'spring': {
                'stiffness': params.get('springConstant', 0.05),
                'damping': params.get('damping', 0.98),
                'restLength': 150,
                'anchorX': 400,
                'anchorY': 100
            },
            'mass': {
                'mass': params.get('mass', 1.5),
                'radius': max(15, params.get('mass', 1.5) * 10),
                'initialX': 400,
                'initialY': 250 + params.get('initialDisplacement', 100)
            },
            'world': {
                'gravity': 0.3,
                'airResistance': 0.001
            },
            'display': {
                'width': 800,
                'height': 600,
                'showEquilibrium': True,
                'showForces': params.get('showForces', True),
                'showVelocityVectors': True,
                'enableInteraction': True
            }
        },
        'controls': {
            'springConstant': {'min': 0.01, 'max': 0.1, 'value': params.get('springConstant', 0.05)},
            'mass': {'min': 0.5, 'max': 3, 'value': params.get('mass', 1.5)},
            'damping': {'min': 0.9, 'max': 1, 'value': params.get('damping', 0.98)},
            'displacement': {'min': 50, 'max': 200, 'value': params.get('initialDisplacement', 100)}
        },
        'metadata': {
            'title': 'Interactive Spring-Mass System',
            'description': 'Observe simple harmonic motion and Hooke\'s law in action. Drag the mass or click "Apply Force" to see oscillation.',
            'physics_concepts': [
                'Hooke\'s Law (F = -kx)',
                'Simple Harmonic Motion',
                'Elastic Potential Energy',
                'Damped Oscillations',
                'Conservation of Energy',
                'Resonance'
            ],
            'educational_notes': 'See how spring force is proportional to displacement. Try different masses and spring constants to observe frequency changes.',
            'instructions': [
                'Drag the orange mass to displace it',
                'Click "Apply Force" to add energy to the system',
                'Adjust spring constant to change oscillation frequency',
                'Increase damping to see energy dissipation',
                'Change mass to observe inertial effects'
            ]
        }
    }

def generate_projectile_config(params=None):
    """Generate configuration for projectile motion simulation"""
    if params is None:
        params = {
            'velocity': 15,
            'angle': 45,
            'gravity': 0.5,
            'airResistance': 0.02,
            'launchHeight': 500
        }
    
    return {
        'type': 'projectile',
        'config': {
            'projectile': {
                'radius': 8,
                'mass': 1,
                'launchX': 50,
                'launchY': 700 - params.get('launchHeight', 200),  # Invert height: higher param = higher position (lower Y)
                'velocity': params.get('velocity', 15),
                'angle': params.get('angle', 45) * 3.14159 / 180,  # Convert to radians
                'restitution': 0.7
            },
            'world': {
                'gravity': params.get('gravity', 0.5),
                'airResistance': params.get('airResistance', 0.02),
                'wind': params.get('wind', 0)
            },
            'target': {
                'x': 700,
                'y': 480,
                'radius': 30
            },
            'display': {
                'width': 800,
                'height': 600,
                'showTrajectory': params.get('showTrajectory', True),
                'showVelocityVector': params.get('showVector', True),
                'showTrails': True
            }
        },
        'controls': {
            'velocity': {'min': 5, 'max': 25, 'value': params.get('velocity', 15)},
            'angle': {'min': 15, 'max': 75, 'value': params.get('angle', 45)},
            'gravity': {'min': 0.1, 'max': 1, 'value': params.get('gravity', 0.5)},
            'airResistance': {'min': 0, 'max': 0.05, 'value': params.get('airResistance', 0.02)},
            'launchHeight': {'min': 100, 'max': 400, 'value': params.get('launchHeight', 200)}
        },
        'metadata': {
            'title': 'Interactive Projectile Motion',
            'description': 'Explore projectile motion with customizable launch parameters and trajectory visualization.',
            'physics_concepts': [
                'Projectile Motion',
                'Kinematic Equations',
                'Gravity Effects',
                'Air Resistance',
                'Trajectory Analysis',
                'Launch Angle Optimization'
            ],
            'educational_notes': 'Observe how launch angle, velocity, height, and gravity affect the projectile\'s trajectory.',
            'instructions': [
                'Adjust launch velocity to change range',
                'Change launch angle to optimize trajectory', 
                'Modify launch height to see elevation effects',
                'Observe trail to analyze projectile path',
                'Try different gravity values to see planetary effects'
            ]
        }
    }

# Main simulation generator
def generate_matter_simulation(simulation_type, params=None):
    """Generate Matter.js simulation configuration"""
    
    generators = {
        'pendulum': generate_pendulum_config,
        'collision': generate_collision_config,
        'spring': generate_spring_config,
        'projectile': generate_projectile_config
    }
    
    if simulation_type not in generators:
        raise ValueError(f"Unknown simulation type: {simulation_type}")
    
    config = generators[simulation_type](params)
    
    # Add common metadata
    config['metadata'] = {
        'title': f"{simulation_type.title()} Simulation",
        'description': get_simulation_description(simulation_type),
        'physics_concepts': get_physics_concepts(simulation_type),
        'educational_notes': get_educational_notes(simulation_type)
    }
    
    return config

def get_simulation_description(sim_type):
    """Get description for simulation type"""
    descriptions = {
        'pendulum': "Interactive pendulum simulation demonstrating periodic motion, energy conservation, and harmonic oscillation.",
        'collision': "Multi-ball collision system showing momentum conservation, elastic/inelastic collisions, and kinetic energy transfer.",
        'spring': "Spring-mass system demonstrating Hooke's law, simple harmonic motion, and damped oscillations.",
        'projectile': "Projectile motion simulation with gravity, air resistance, and trajectory analysis."
    }
    return descriptions.get(sim_type, "Physics simulation")

def get_physics_concepts(sim_type):
    """Get key physics concepts for simulation"""
    concepts = {
        'pendulum': ["Periodic Motion", "Energy Conservation", "Simple Harmonic Motion", "Damping", "Angular Momentum"],
        'collision': ["Momentum Conservation", "Kinetic Energy", "Elastic Collisions", "Coefficient of Restitution", "Impulse"],
        'spring': ["Hooke's Law", "Simple Harmonic Motion", "Elastic Potential Energy", "Damped Oscillations", "Resonance"],
        'projectile': ["Kinematics", "Gravity", "Air Resistance", "Trajectory", "Range and Height"]
    }
    return concepts.get(sim_type, [])

def get_educational_notes(sim_type):
    """Get educational notes for simulation"""
    notes = {
        'pendulum': "Observe how changing length affects period (T = 2π√(L/g)). Notice energy conversion between kinetic and potential.",
        'collision': "Watch momentum conservation: total momentum before collision equals total momentum after collision.",
        'spring': "See Hooke's Law in action: F = -kx. The restoring force is proportional to displacement.",
        'projectile': "Horizontal and vertical motions are independent. Maximum range occurs at 45° angle (in vacuum)."
    }
    return notes.get(sim_type, "")