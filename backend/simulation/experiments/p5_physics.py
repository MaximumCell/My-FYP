"""
p5.js Physics Simulations
Backend endpoints for electromagnetic and wave physics using p5.js
Includes: Electric Fields, Magnetic Fields, Wave Motion, Oscillations
"""

def generate_electric_field_config(params=None):
    """Generate configuration for electric field simulation"""
    if params is None:
        params = {
            'charges': 4,
            'fieldStrength': 1.0,
            'showField': True,
            'showForces': True
        }
    
    return {
        'type': 'electric_field',
        'config': {
            'charges': {
                'count': params.get('charges', 4),
                'minCharge': -2,
                'maxCharge': 2,
                'defaultPositions': [
                    {'x': 200, 'y': 200, 'charge': 1},
                    {'x': 600, 'y': 200, 'charge': -1},
                    {'x': 200, 'y': 400, 'charge': 1},
                    {'x': 600, 'y': 400, 'charge': -1}
                ]
            },
            'field': {
                'strength': params.get('fieldStrength', 1.0),
                'gridSize': 40,
                'vectorScale': 0.5,
                'showFieldLines': params.get('showField', True),
                'showEquipotential': params.get('showEquipotential', False)
            },
            'testCharge': {
                'charge': 0.1,
                'mass': 1,
                'showForces': params.get('showForces', True),
                'showTrail': params.get('showTrail', True)
            },
            'display': {
                'width': 800,
                'height': 600,
                'backgroundColor': 20
            }
        },
        'controls': {
            'charges': {'min': 2, 'max': 8, 'value': params.get('charges', 4)},
            'fieldStrength': {'min': 0.1, 'max': 3, 'value': params.get('fieldStrength', 1.0)},
            'showField': {'value': params.get('showField', True)},
            'showForces': {'value': params.get('showForces', True)}
        }
    }

def generate_magnetic_field_config(params=None):
    """Generate configuration for magnetic field simulation"""
    if params is None:
        params = {
            'fieldStrength': 1.0,
            'particleCount': 3,
            'showFieldLines': True,
            'cyclotronMotion': True
        }
    
    return {
        'type': 'magnetic_field',
        'config': {
            'magneticField': {
                'strength': params.get('fieldStrength', 1.0),
                'direction': 'into_page',  # 'into_page' or 'out_of_page'
                'uniform': True,
                'showFieldLines': params.get('showFieldLines', True)
            },
            'particles': {
                'count': params.get('particleCount', 3),
                'charges': [1, -1, 1],  # Mix of positive and negative
                'masses': [1, 1, 1],
                'velocities': [
                    {'x': 2, 'y': 0},
                    {'x': -1.5, 'y': 1},
                    {'x': 0, 'y': -2}
                ],
                'initialPositions': [
                    {'x': 100, 'y': 300},
                    {'x': 400, 'y': 150},
                    {'x': 700, 'y': 450}
                ]
            },
            'physics': {
                'cyclotronMotion': params.get('cyclotronMotion', True),
                'showLorentzForce': params.get('showForce', True),
                'radiusFormula': True  # Show r = mv/(qB)
            },
            'display': {
                'width': 800,
                'height': 600,
                'showTrails': params.get('showTrails', True),
                'trailLength': 100
            }
        },
        'controls': {
            'fieldStrength': {'min': 0.1, 'max': 2, 'value': params.get('fieldStrength', 1.0)},
            'particleCount': {'min': 1, 'max': 5, 'value': params.get('particleCount', 3)},
            'showFieldLines': {'value': params.get('showFieldLines', True)},
            'cyclotronMotion': {'value': params.get('cyclotronMotion', True)}
        }
    }

def generate_wave_motion_config(params=None):
    """Generate configuration for wave motion simulation"""
    if params is None:
        params = {
            'waveType': 'sine',
            'frequency': 1.0,
            'amplitude': 50,
            'wavelength': 100,
            'waveSpeed': 200
        }
    
    return {
        'type': 'wave_motion',
        'config': {
            'wave': {
                'type': params.get('waveType', 'sine'),  # 'sine', 'square', 'triangle'
                'frequency': params.get('frequency', 1.0),
                'amplitude': params.get('amplitude', 50),
                'wavelength': params.get('wavelength', 100),
                'speed': params.get('waveSpeed', 200),
                'phase': 0
            },
            'interference': {
                'enabled': params.get('interference', False),
                'source2Offset': 200,
                'phaseShift': 0
            },
            'medium': {
                'showParticles': params.get('showParticles', True),
                'particleCount': 50,
                'damping': 0.98
            },
            'display': {
                'width': 800,
                'height': 600,
                'showWaveform': True,
                'showEnvelope': params.get('showEnvelope', False)
            }
        },
        'controls': {
            'frequency': {'min': 0.1, 'max': 3, 'value': params.get('frequency', 1.0)},
            'amplitude': {'min': 10, 'max': 100, 'value': params.get('amplitude', 50)},
            'wavelength': {'min': 50, 'max': 200, 'value': params.get('wavelength', 100)},
            'waveSpeed': {'min': 50, 'max': 400, 'value': params.get('waveSpeed', 200)}
        }
    }

def generate_oscillation_config(params=None):
    """Generate configuration for oscillation simulation"""
    if params is None:
        params = {
            'oscillatorCount': 3,
            'coupling': 0.1,
            'damping': 0.02,
            'drivingForce': 0
        }
    
    return {
        'type': 'oscillation',
        'config': {
            'oscillators': {
                'count': params.get('oscillatorCount', 3),
                'naturalFrequencies': [1.0, 1.2, 0.8],
                'amplitudes': [60, 50, 70],
                'phases': [0, 0.5, 1.0],
                'positions': [
                    {'x': 200, 'y': 300},
                    {'x': 400, 'y': 300},
                    {'x': 600, 'y': 300}
                ]
            },
            'coupling': {
                'strength': params.get('coupling', 0.1),
                'type': 'spring',  # 'spring', 'electromagnetic'
                'showConnections': True
            },
            'driving': {
                'force': params.get('drivingForce', 0),
                'frequency': 1.0,
                'phase': 0
            },
            'damping': {
                'coefficient': params.get('damping', 0.02),
                'type': 'velocity'  # 'velocity', 'displacement'
            },
            'display': {
                'width': 800,
                'height': 600,
                'showPhaseSpace': params.get('showPhaseSpace', False),
                'showBeats': params.get('showBeats', True)
            }
        },
        'controls': {
            'oscillatorCount': {'min': 2, 'max': 5, 'value': params.get('oscillatorCount', 3)},
            'coupling': {'min': 0, 'max': 0.5, 'value': params.get('coupling', 0.1)},
            'damping': {'min': 0, 'max': 0.1, 'value': params.get('damping', 0.02)},
            'drivingForce': {'min': 0, 'max': 1, 'value': params.get('drivingForce', 0)}
        }
    }

def generate_electromagnetic_wave_config(params=None):
    """Generate configuration for electromagnetic wave simulation"""
    if params is None:
        params = {
            'frequency': 1.0,
            'amplitude': 1.0,
            'polarization': 'linear',
            'showComponents': True
        }
    
    return {
        'type': 'em_wave',
        'config': {
            'wave': {
                'frequency': params.get('frequency', 1.0),
                'amplitude': params.get('amplitude', 1.0),
                'wavelength': 300 / params.get('frequency', 1.0),  # c = λf (scaled)
                'speed': 300,  # Speed of light (scaled)
                'polarization': params.get('polarization', 'linear')  # 'linear', 'circular', 'elliptical'
            },
            'fields': {
                'showElectric': params.get('showElectric', True),
                'showMagnetic': params.get('showMagnetic', True),
                'showPoynting': params.get('showPoynting', False),
                'electricColor': [255, 0, 0],
                'magneticColor': [0, 255, 0]
            },
            'display': {
                'width': 800,
                'height': 600,
                'perspective': '3D',
                'showComponents': params.get('showComponents', True)
            }
        },
        'controls': {
            'frequency': {'min': 0.1, 'max': 3, 'value': params.get('frequency', 1.0)},
            'amplitude': {'min': 0.1, 'max': 2, 'value': params.get('amplitude', 1.0)},
            'showElectric': {'value': params.get('showElectric', True)},
            'showMagnetic': {'value': params.get('showMagnetic', True)}
        }
    }

# Main simulation generator
def generate_p5_simulation(simulation_type, params=None):
    """Generate p5.js simulation configuration"""
    
    generators = {
        'electric_field': generate_electric_field_config,
        'magnetic_field': generate_magnetic_field_config,
        'wave_motion': generate_wave_motion_config,
        'oscillation': generate_oscillation_config,
        'em_wave': generate_electromagnetic_wave_config
    }
    
    if simulation_type not in generators:
        raise ValueError(f"Unknown simulation type: {simulation_type}")
    
    config = generators[simulation_type](params)
    
    # Add common metadata
    config['metadata'] = {
        'title': f"{simulation_type.replace('_', ' ').title()} Simulation",
        'description': get_simulation_description(simulation_type),
        'physics_concepts': get_physics_concepts(simulation_type),
        'educational_notes': get_educational_notes(simulation_type)
    }
    
    return config

def get_simulation_description(sim_type):
    """Get description for simulation type"""
    descriptions = {
        'electric_field': "Interactive electric field visualization showing field lines, equipotential surfaces, and charge interactions.",
        'magnetic_field': "Magnetic field simulation demonstrating Lorentz force and cyclotron motion of charged particles.",
        'wave_motion': "Wave propagation simulation showing interference, superposition, and wave properties.",
        'oscillation': "Coupled oscillator system demonstrating normal modes, beats, and resonance phenomena.",
        'em_wave': "Electromagnetic wave simulation showing the relationship between electric and magnetic field components."
    }
    return descriptions.get(sim_type, "Physics simulation")

def get_physics_concepts(sim_type):
    """Get key physics concepts for simulation"""
    concepts = {
        'electric_field': ["Coulomb's Law", "Electric Field", "Field Lines", "Equipotential", "Electric Force"],
        'magnetic_field': ["Lorentz Force", "Cyclotron Motion", "Magnetic Field", "Charged Particle Motion", "Right-Hand Rule"],
        'wave_motion': ["Wave Equation", "Interference", "Superposition", "Wavelength", "Frequency", "Wave Speed"],
        'oscillation': ["Simple Harmonic Motion", "Normal Modes", "Beats", "Resonance", "Coupled Oscillators"],
        'em_wave': ["Maxwell's Equations", "Electromagnetic Radiation", "Polarization", "Wave-Particle Duality", "Poynting Vector"]
    }
    return concepts.get(sim_type, [])

def get_educational_notes(sim_type):
    """Get educational notes for simulation"""
    notes = {
        'electric_field': "Electric field points away from positive charges and toward negative charges. Field strength follows inverse square law.",
        'magnetic_field': "Magnetic force is perpendicular to both velocity and field. Radius of curvature: r = mv/(qB).",
        'wave_motion': "Wave speed v = fλ. Constructive interference occurs when waves are in phase.",
        'oscillation': "Coupled oscillators can transfer energy between each other. Normal modes are special oscillation patterns.",
        'em_wave': "Electric and magnetic fields are perpendicular to each other and to the direction of propagation."
    }
    return notes.get(sim_type, "")