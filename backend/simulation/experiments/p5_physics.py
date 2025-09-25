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
    
    # Generate default positions based on charge count
    charge_count = params.get('charges', 4)
    default_positions = []
    
    # Create positions in a grid pattern
    if charge_count == 2:
        default_positions = [
            {'x': 300, 'y': 300, 'charge': 1},
            {'x': 500, 'y': 300, 'charge': -1}
        ]
    elif charge_count == 3:
        default_positions = [
            {'x': 250, 'y': 250, 'charge': 1},
            {'x': 550, 'y': 250, 'charge': -1},
            {'x': 400, 'y': 400, 'charge': 1}
        ]
    elif charge_count == 4:
        default_positions = [
            {'x': 200, 'y': 200, 'charge': 1},
            {'x': 600, 'y': 200, 'charge': -1},
            {'x': 200, 'y': 400, 'charge': 1},
            {'x': 600, 'y': 400, 'charge': -1}
        ]
    elif charge_count == 5:
        default_positions = [
            {'x': 150, 'y': 200, 'charge': 1},
            {'x': 350, 'y': 200, 'charge': -1},
            {'x': 550, 'y': 200, 'charge': 1},
            {'x': 250, 'y': 400, 'charge': -1},
            {'x': 450, 'y': 400, 'charge': 1}
        ]
    elif charge_count == 6:
        default_positions = [
            {'x': 150, 'y': 180, 'charge': 1},
            {'x': 350, 'y': 180, 'charge': -1},
            {'x': 550, 'y': 180, 'charge': 1},
            {'x': 150, 'y': 380, 'charge': -1},
            {'x': 350, 'y': 380, 'charge': 1},
            {'x': 550, 'y': 380, 'charge': -1}
        ]
    elif charge_count == 7:
        default_positions = [
            {'x': 120, 'y': 160, 'charge': 1},
            {'x': 280, 'y': 160, 'charge': -1},
            {'x': 440, 'y': 160, 'charge': 1},
            {'x': 600, 'y': 160, 'charge': -1},
            {'x': 200, 'y': 320, 'charge': 1},
            {'x': 360, 'y': 320, 'charge': -1},
            {'x': 520, 'y': 320, 'charge': 1}
        ]
    else:  # 8 charges
        default_positions = [
            {'x': 120, 'y': 150, 'charge': 1},
            {'x': 280, 'y': 150, 'charge': -1},
            {'x': 440, 'y': 150, 'charge': 1},
            {'x': 600, 'y': 150, 'charge': -1},
            {'x': 120, 'y': 300, 'charge': -1},
            {'x': 280, 'y': 300, 'charge': 1},
            {'x': 440, 'y': 300, 'charge': -1},
            {'x': 600, 'y': 300, 'charge': 1}
        ]
    
    return {
        'type': 'electric_field',
        'config': {
            'charges': {
                'count': charge_count,
                'minCharge': -2,
                'maxCharge': 2,
                'defaultPositions': default_positions
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
            'charges': {'min': 2, 'max': 8, 'value': charge_count},
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
    
    # Generate particle arrays based on particle count
    particle_count = params.get('particleCount', 3)
    charges = []
    masses = []
    velocities = []
    initial_positions = []
    
    # Predefined configurations for different particle counts
    base_configs = [
        # 1 particle
        [{'charge': 1, 'mass': 1, 'vel': {'x': 2, 'y': 0}, 'pos': {'x': 400, 'y': 300}}],
        # 2 particles
        [
            {'charge': 1, 'mass': 1, 'vel': {'x': 2, 'y': 0}, 'pos': {'x': 300, 'y': 250}},
            {'charge': -1, 'mass': 1, 'vel': {'x': -1.5, 'y': 1}, 'pos': {'x': 500, 'y': 350}}
        ],
        # 3 particles
        [
            {'charge': 1, 'mass': 1, 'vel': {'x': 2, 'y': 0}, 'pos': {'x': 100, 'y': 300}},
            {'charge': -1, 'mass': 1, 'vel': {'x': -1.5, 'y': 1}, 'pos': {'x': 400, 'y': 150}},
            {'charge': 1, 'mass': 1, 'vel': {'x': 0, 'y': -2}, 'pos': {'x': 700, 'y': 450}}
        ],
        # 4 particles
        [
            {'charge': 1, 'mass': 1, 'vel': {'x': 2, 'y': 0}, 'pos': {'x': 150, 'y': 200}},
            {'charge': -1, 'mass': 1, 'vel': {'x': -1.5, 'y': 1}, 'pos': {'x': 350, 'y': 150}},
            {'charge': 1, 'mass': 1, 'vel': {'x': 0, 'y': -2}, 'pos': {'x': 550, 'y': 400}},
            {'charge': -1, 'mass': 1, 'vel': {'x': 1, 'y': 1.5}, 'pos': {'x': 650, 'y': 300}}
        ],
        # 5 particles
        [
            {'charge': 1, 'mass': 1, 'vel': {'x': 2, 'y': 0}, 'pos': {'x': 120, 'y': 180}},
            {'charge': -1, 'mass': 1, 'vel': {'x': -1.5, 'y': 1}, 'pos': {'x': 300, 'y': 120}},
            {'charge': 1, 'mass': 1, 'vel': {'x': 0, 'y': -2}, 'pos': {'x': 480, 'y': 350}},
            {'charge': -1, 'mass': 1, 'vel': {'x': 1, 'y': 1.5}, 'pos': {'x': 600, 'y': 250}},
            {'charge': 1, 'mass': 1, 'vel': {'x': -1, 'y': -1}, 'pos': {'x': 200, 'y': 450}}
        ]
    ]
    
    # Use the appropriate configuration
    config_index = min(particle_count - 1, len(base_configs) - 1)
    selected_config = base_configs[config_index][:particle_count]
    
    for particle in selected_config:
        charges.append(particle['charge'])
        masses.append(particle['mass'])
        velocities.append(particle['vel'])
        initial_positions.append(particle['pos'])
    
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
                'count': particle_count,
                'charges': charges,
                'masses': masses,
                'velocities': velocities,
                'initialPositions': initial_positions
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
            'particleCount': {'min': 1, 'max': 5, 'value': particle_count},
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
    
    # Generate oscillator arrays based on count
    oscillator_count = params.get('oscillatorCount', 3)
    natural_frequencies = []
    amplitudes = []
    phases = []
    positions = []
    
    # Base frequency and amplitude ranges
    base_frequency = 1.0
    base_amplitude = 60
    
    for i in range(oscillator_count):
        # Generate slightly different frequencies for interesting beating patterns
        freq_variation = 0.2 * (i - oscillator_count/2) / oscillator_count
        natural_frequencies.append(base_frequency + freq_variation)
        
        # Generate amplitudes with some variation
        amp_variation = 20 * (0.5 - abs(i - oscillator_count/2) / oscillator_count)
        amplitudes.append(base_amplitude + amp_variation)
        
        # Generate phases
        phases.append(i * 0.5)
        
        # Generate positions in a line
        spacing = 600 / (oscillator_count + 1)
        x_pos = 100 + (i + 1) * spacing
        positions.append({'x': x_pos, 'y': 300})
    
    return {
        'type': 'oscillation',
        'config': {
            'oscillators': {
                'count': oscillator_count,
                'naturalFrequencies': natural_frequencies,
                'amplitudes': amplitudes,
                'phases': phases,
                'positions': positions
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
            'oscillatorCount': {'min': 2, 'max': 5, 'value': oscillator_count},
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