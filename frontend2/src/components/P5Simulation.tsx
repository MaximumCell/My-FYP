'use client'

import React, { useEffect, useRef, useState } from 'react'
import p5 from 'p5'

interface P5SimulationProps {
    simulationType: string
    onParameterChange?: (parameter: string, value: number) => void
}

export default function P5Simulation({ simulationType, onParameterChange }: P5SimulationProps) {
    const canvasRef = useRef<HTMLDivElement>(null)
    const p5InstanceRef = useRef<p5 | null>(null)
    const [isPaused, setIsPaused] = useState(false)
    const [showField, setShowField] = useState(true)
    const [config, setConfig] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    // User customizable parameters
    const [userParams, setUserParams] = useState<any>({
        // Electric field parameters
        chargeStrength: 1,
        numCharges: 3,
        fieldDensity: 20,
        // Magnetic field parameters
        magneticStrength: 0.5,
        particleSpeed: 2,
        // Wave parameters
        frequency: 1,
        amplitude: 50,
        wavelength: 100,
        // Oscillation parameters
        oscillationFreq: 1,
        damping: 0.01
    })

    // Fetch simulation config
    useEffect(() => {
        const fetchConfig = async () => {
            try {
                setLoading(true)
                const response = await fetch(`http://localhost:5000/simulation/api/simulation/p5`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        type: simulationType,
                        parameters: userParams
                    })
                })

                if (!response.ok) {
                    throw new Error('Failed to fetch simulation config')
                }

                const data = await response.json()
                setConfig(data.simulation)  // Use data.simulation instead of data
                setError(null)
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error')
            } finally {
                setLoading(false)
            }
        }

        fetchConfig()
    }, [simulationType, userParams])

    useEffect(() => {
        if (!canvasRef.current || !config) return

        // Clean up previous p5 instance
        if (p5InstanceRef.current) {
            p5InstanceRef.current.remove()
        }

        // Create new p5 sketch
        const sketch = (p: p5) => {
            let simulation: any = {}

            p.setup = () => {
                const canvas = p.createCanvas(
                    config.config.display.width,
                    config.config.display.height
                )
                canvas.parent(canvasRef.current!)

                // Initialize simulation based on type
                switch (config.type) {
                    case 'electric_field':
                        setupElectricField(p, simulation, config.config)
                        break
                    case 'magnetic_field':
                        setupMagneticField(p, simulation, config.config)
                        break
                    case 'wave_motion':
                        setupWaveMotion(p, simulation, config.config)
                        break
                    case 'oscillation':
                        setupOscillation(p, simulation, config.config)
                        break
                    case 'em_wave':
                        setupEMWave(p, simulation, config.config)
                        break
                }
            }

            p.draw = () => {
                if (isPaused) return

                p.background(config.config.display.backgroundColor || 20)

                // Draw simulation based on type
                switch (config.type) {
                    case 'electric_field':
                        drawElectricField(p, simulation, config.config)
                        break
                    case 'magnetic_field':
                        drawMagneticField(p, simulation, config.config)
                        break
                    case 'wave_motion':
                        drawWaveMotion(p, simulation, config.config)
                        break
                    case 'oscillation':
                        drawOscillation(p, simulation, config.config)
                        break
                    case 'em_wave':
                        drawEMWave(p, simulation, config.config)
                        break
                }
            }

            p.mousePressed = () => {
                // Handle mouse interactions for different simulations
                if (config.type === 'electric_field') {
                    addCharge(p, simulation, p.mouseX, p.mouseY)
                }
            }
        }

        // Create p5 instance
        p5InstanceRef.current = new p5(sketch)

        return () => {
            if (p5InstanceRef.current) {
                p5InstanceRef.current.remove()
            }
        }
    }, [config, isPaused])

    // Electric Field Simulation Functions
    const setupElectricField = (p: p5, sim: any, config: any) => {
        sim.charges = config.charges.defaultPositions.map((pos: any) => ({
            x: pos.x,
            y: pos.y,
            charge: pos.charge,
            dragging: false
        }))
        sim.testCharge = null
        sim.fieldLines = []
    }

    const drawElectricField = (p: p5, sim: any, config: any) => {
        // Draw field lines if enabled
        if (config.field.showFieldLines && showField) {
            drawFieldLines(p, sim, config)
        }

        // Draw charges
        sim.charges.forEach((charge: any) => {
            p.fill(charge.charge > 0 ? '#ff4444' : '#4444ff')
            p.stroke(255)
            p.strokeWeight(2)
            p.circle(charge.x, charge.y, Math.abs(charge.charge) * 20)

            // Draw charge symbol
            p.fill(255)
            p.textAlign(p.CENTER, p.CENTER)
            p.textSize(16)
            p.text(charge.charge > 0 ? '+' : '-', charge.x, charge.y)
        })

        // Draw info
        drawElectricFieldInfo(p, sim, config)
    }

    const drawFieldLines = (p: p5, sim: any, config: any) => {
        const gridSize = config.field.gridSize

        for (let x = gridSize; x < config.display.width; x += gridSize) {
            for (let y = gridSize; y < config.display.height; y += gridSize) {
                const field = calculateElectricField(x, y, sim.charges)
                const magnitude = Math.sqrt(field.x * field.x + field.y * field.y)

                if (magnitude > 0.01) {
                    // Draw field vector
                    p.stroke(255, 255, 0, 150)
                    p.strokeWeight(1)

                    const length = Math.min(magnitude * config.field.vectorScale * 100, gridSize * 0.8)
                    const angle = Math.atan2(field.y, field.x)

                    const endX = x + Math.cos(angle) * length
                    const endY = y + Math.sin(angle) * length

                    p.line(x, y, endX, endY)

                    // Draw arrowhead
                    p.push()
                    p.translate(endX, endY)
                    p.rotate(angle)
                    p.line(0, 0, -5, -2)
                    p.line(0, 0, -5, 2)
                    p.pop()
                }
            }
        }
    }

    const calculateElectricField = (x: number, y: number, charges: any[]) => {
        let Ex = 0, Ey = 0
        const k = 8.99e9 // Coulomb's constant (scaled)

        charges.forEach(charge => {
            const dx = x - charge.x
            const dy = y - charge.y
            const distance = Math.sqrt(dx * dx + dy * dy)

            if (distance > 10) {
                const field = k * charge.charge / (distance * distance) * 0.001
                Ex += field * dx / distance
                Ey += field * dy / distance
            }
        })

        return { x: Ex, y: Ey }
    }

    const drawElectricFieldInfo = (p: p5, sim: any, config: any) => {
        p.fill(255)
        p.textAlign(p.LEFT, p.TOP)
        p.textSize(14)
        p.text(`Charges: ${sim.charges.length}`, 10, 10)
        p.text('Click to add charges', 10, 30)
        p.text('Drag charges to move them', 10, 50)
    }

    const addCharge = (p: p5, sim: any, x: number, y: number) => {
        const newCharge = Math.random() > 0.5 ? 1 : -1
        sim.charges.push({ x, y, charge: newCharge, dragging: false })
    }

    // Magnetic Field Simulation Functions
    const setupMagneticField = (p: p5, sim: any, config: any) => {
        sim.particles = config.particles.initialPositions.map((pos: any, index: number) => ({
            x: pos.x,
            y: pos.y,
            vx: config.particles.velocities[index].x,
            vy: config.particles.velocities[index].y,
            charge: config.particles.charges[index],
            mass: config.particles.masses[index],
            trail: []
        }))
        sim.time = 0
    }

    const drawMagneticField = (p: p5, sim: any, config: any) => {
        sim.time += 0.016 // 60fps

        // Draw magnetic field indicators
        if (config.magneticField.showFieldLines && showField) {
            drawMagneticFieldLines(p, config)
        }

        // Update and draw particles
        sim.particles.forEach((particle: any) => {
            // Calculate Lorentz force: F = q(v × B)
            const B = config.magneticField.strength
            const lorentzForceX = particle.charge * particle.vy * B
            const lorentzForceY = -particle.charge * particle.vx * B

            // Update velocity (F = ma)
            particle.vx += lorentzForceX / particle.mass * 0.1
            particle.vy += lorentzForceY / particle.mass * 0.1

            // Update position
            particle.x += particle.vx
            particle.y += particle.vy

            // Add to trail
            particle.trail.push({ x: particle.x, y: particle.y })
            if (particle.trail.length > config.display.trailLength) {
                particle.trail.shift()
            }

            // Draw trail
            if (config.display.showTrails) {
                p.stroke(particle.charge > 0 ? '#ff4444' : '#4444ff')
                p.strokeWeight(2)
                p.noFill()
                p.beginShape()
                particle.trail.forEach((point: any) => {
                    p.vertex(point.x, point.y)
                })
                p.endShape()
            }

            // Draw particle
            p.fill(particle.charge > 0 ? '#ff4444' : '#4444ff')
            p.stroke(255)
            p.strokeWeight(1)
            p.circle(particle.x, particle.y, 8)

            // Boundary conditions
            if (particle.x < 0 || particle.x > config.display.width ||
                particle.y < 0 || particle.y > config.display.height) {
                particle.x = config.particles.initialPositions[sim.particles.indexOf(particle)].x
                particle.y = config.particles.initialPositions[sim.particles.indexOf(particle)].y
                particle.trail = []
            }
        })

        drawMagneticFieldInfo(p, sim, config)
    }

    const drawMagneticFieldLines = (p: p5, config: any) => {
        // Draw field into/out of page indicators
        p.fill(config.magneticField.direction === 'into_page' ? 255 : 0)
        p.stroke(255)
        p.strokeWeight(1)

        for (let x = 40; x < config.display.width; x += 60) {
            for (let y = 40; y < config.display.height; y += 60) {
                if (config.magneticField.direction === 'into_page') {
                    // X symbol for into page
                    p.line(x - 5, y - 5, x + 5, y + 5)
                    p.line(x - 5, y + 5, x + 5, y - 5)
                } else {
                    // Dot symbol for out of page
                    p.circle(x, y, 6)
                }
            }
        }
    }

    const drawMagneticFieldInfo = (p: p5, sim: any, config: any) => {
        p.fill(255)
        p.textAlign(p.LEFT, p.TOP)
        p.textSize(14)
        p.text(`Magnetic Field: ${config.magneticField.strength.toFixed(1)} T`, 10, 10)
        p.text(`Direction: ${config.magneticField.direction.replace('_', ' ')}`, 10, 30)
        p.text('Particles follow cyclotron motion', 10, 50)
    }

    // Wave Motion Simulation Functions
    const setupWaveMotion = (p: p5, sim: any, config: any) => {
        sim.time = 0
        sim.wavePoints = []
        for (let x = 0; x <= config.display.width; x += 5) {
            sim.wavePoints.push(x)
        }
    }

    const drawWaveMotion = (p: p5, sim: any, config: any) => {
        sim.time += 0.05

        // Draw wave
        p.stroke(0, 255, 255)
        p.strokeWeight(3)
        p.noFill()

        p.beginShape()
        sim.wavePoints.forEach((x: number) => {
            const k = 2 * Math.PI / config.wave.wavelength
            const omega = 2 * Math.PI * config.wave.frequency
            const y = config.display.height / 2 +
                config.wave.amplitude * Math.sin(k * x - omega * sim.time + config.wave.phase)
            p.vertex(x, y)
        })
        p.endShape()

        // Draw wave properties
        drawWaveInfo(p, sim, config)
    }

    const drawWaveInfo = (p: p5, sim: any, config: any) => {
        p.fill(255)
        p.textAlign(p.LEFT, p.TOP)
        p.textSize(14)
        p.text(`Frequency: ${config.wave.frequency.toFixed(1)} Hz`, 10, 10)
        p.text(`Wavelength: ${config.wave.wavelength.toFixed(0)} px`, 10, 30)
        p.text(`Amplitude: ${config.wave.amplitude.toFixed(0)} px`, 10, 50)
        p.text(`Speed: ${config.wave.speed.toFixed(0)} px/s`, 10, 70)
    }

    // Oscillation Simulation Functions
    const setupOscillation = (p: p5, sim: any, config: any) => {
        sim.oscillators = config.oscillators.positions.map((pos: any, index: number) => ({
            x: pos.x,
            y: pos.y,
            baseY: pos.y,
            displacement: 0,
            velocity: 0,
            frequency: config.oscillators.naturalFrequencies[index],
            amplitude: config.oscillators.amplitudes[index],
            phase: config.oscillators.phases[index]
        }))
        sim.time = 0
    }

    const drawOscillation = (p: p5, sim: any, config: any) => {
        sim.time += 0.016

        // Update oscillators
        sim.oscillators.forEach((osc: any, index: number) => {
            // Simple harmonic motion with coupling
            let force = -config.oscillators.naturalFrequencies[index] * osc.displacement

            // Add coupling forces from neighbors
            sim.oscillators.forEach((other: any, otherIndex: number) => {
                if (otherIndex !== index) {
                    const distance = Math.abs(otherIndex - index)
                    if (distance <= 1) { // Only couple to nearest neighbors
                        force += config.coupling.strength * (other.displacement - osc.displacement) / distance
                    }
                }
            })

            // Apply damping
            force -= config.damping.coefficient * osc.velocity

            // Update motion
            osc.velocity += force * 0.1
            osc.displacement += osc.velocity
            osc.y = osc.baseY + osc.displacement
        })

        // Draw oscillators
        sim.oscillators.forEach((osc: any, index: number) => {
            p.fill(255, 100, 100)
            p.stroke(255)
            p.strokeWeight(2)
            p.circle(osc.x, osc.y, 20)

            // Draw equilibrium line
            p.stroke(100)
            p.strokeWeight(1)
            p.line(osc.x - 30, osc.baseY, osc.x + 30, osc.baseY)
        })

        // Draw coupling connections
        if (config.coupling.showConnections) {
            p.stroke(0, 255, 0, 100)
            p.strokeWeight(1)
            for (let i = 0; i < sim.oscillators.length - 1; i++) {
                p.line(
                    sim.oscillators[i].x, sim.oscillators[i].y,
                    sim.oscillators[i + 1].x, sim.oscillators[i + 1].y
                )
            }
        }

        drawOscillationInfo(p, sim, config)
    }

    const drawOscillationInfo = (p: p5, sim: any, config: any) => {
        p.fill(255)
        p.textAlign(p.LEFT, p.TOP)
        p.textSize(14)
        p.text(`Oscillators: ${sim.oscillators.length}`, 10, 10)
        p.text(`Coupling: ${config.coupling.strength.toFixed(2)}`, 10, 30)
        p.text(`Damping: ${config.damping.coefficient.toFixed(3)}`, 10, 50)
    }

    // EM Wave Simulation Functions
    const setupEMWave = (p: p5, sim: any, config: any) => {
        sim.time = 0
        sim.waveLength = config.wave.wavelength
    }

    const drawEMWave = (p: p5, sim: any, config: any) => {
        sim.time += 0.05

        const centerY = config.display.height / 2

        // Draw electric field (red)
        if (config.fields.showElectric) {
            p.stroke(255, 0, 0)
            p.strokeWeight(2)
            p.noFill()

            p.beginShape()
            for (let x = 0; x <= config.display.width; x += 5) {
                const k = 2 * Math.PI / config.wave.wavelength
                const omega = 2 * Math.PI * config.wave.frequency
                const E = config.wave.amplitude * 50 * Math.sin(k * x - omega * sim.time)
                p.vertex(x, centerY + E)
            }
            p.endShape()
        }

        // Draw magnetic field (green)
        if (config.fields.showMagnetic) {
            p.stroke(0, 255, 0)
            p.strokeWeight(2)
            p.noFill()

            // Magnetic field is perpendicular (represented as dots/crosses)
            for (let x = 0; x <= config.display.width; x += 20) {
                const k = 2 * Math.PI / config.wave.wavelength
                const omega = 2 * Math.PI * config.wave.frequency
                const B = config.wave.amplitude * Math.sin(k * x - omega * sim.time)

                if (B > 0) {
                    // Out of page (dot)
                    p.fill(0, 255, 0)
                    p.circle(x, centerY, 4)
                } else if (B < 0) {
                    // Into page (cross)
                    p.line(x - 3, centerY - 3, x + 3, centerY + 3)
                    p.line(x - 3, centerY + 3, x + 3, centerY - 3)
                }
            }
        }

        drawEMWaveInfo(p, sim, config)
    }

    const drawEMWaveInfo = (p: p5, sim: any, config: any) => {
        p.fill(255)
        p.textAlign(p.LEFT, p.TOP)
        p.textSize(14)
        p.text(`Frequency: ${config.wave.frequency.toFixed(1)} Hz`, 10, 10)
        p.text(`Wavelength: ${config.wave.wavelength.toFixed(0)} units`, 10, 30)
        p.text(`Speed: ${config.wave.speed.toFixed(0)} units/s`, 10, 50)
        p.text('Red: Electric Field, Green: Magnetic Field', 10, 70)
    }

    const togglePause = () => {
        setIsPaused(!isPaused)
    }

    const resetSimulation = () => {
        window.location.reload()
    }

    const updateParameter = (paramName: string, value: number) => {
        setUserParams(prev => ({
            ...prev,
            [paramName]: value
        }))
    }

    const getParametersForSimulation = () => {
        switch (simulationType) {
            case 'electric_field':
                return [
                    { name: 'chargeStrength', label: 'Charge Strength', value: userParams.chargeStrength, min: 0.1, max: 3, step: 0.1 },
                    { name: 'numCharges', label: 'Number of Charges', value: userParams.numCharges, min: 1, max: 8, step: 1 },
                    { name: 'fieldDensity', label: 'Field Line Density', value: userParams.fieldDensity, min: 10, max: 50, step: 5 }
                ]
            case 'magnetic_field':
                return [
                    { name: 'magneticStrength', label: 'Magnetic Strength', value: userParams.magneticStrength, min: 0.1, max: 2, step: 0.1 },
                    { name: 'particleSpeed', label: 'Particle Speed', value: userParams.particleSpeed, min: 0.5, max: 5, step: 0.5 }
                ]
            case 'wave_motion':
                return [
                    { name: 'frequency', label: 'Frequency', value: userParams.frequency, min: 0.1, max: 3, step: 0.1 },
                    { name: 'amplitude', label: 'Amplitude', value: userParams.amplitude, min: 10, max: 100, step: 10 },
                    { name: 'wavelength', label: 'Wavelength', value: userParams.wavelength, min: 50, max: 200, step: 10 }
                ]
            case 'oscillation':
                return [
                    { name: 'oscillationFreq', label: 'Frequency', value: userParams.oscillationFreq, min: 0.1, max: 3, step: 0.1 },
                    { name: 'damping', label: 'Damping', value: userParams.damping, min: 0, max: 0.05, step: 0.005 }
                ]
            case 'em_wave':
                return [
                    { name: 'frequency', label: 'Frequency', value: userParams.frequency, min: 0.5, max: 3, step: 0.1 },
                    { name: 'amplitude', label: 'Amplitude', value: userParams.amplitude, min: 20, max: 80, step: 10 }
                ]
            default:
                return []
        }
    }

    if (loading) {
        return (
            <div className="w-full h-96 bg-gray-900 rounded-lg flex items-center justify-center">
                <div className="text-white text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4 mx-auto"></div>
                    <p>Loading simulation...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="w-full h-96 bg-gray-900 rounded-lg flex items-center justify-center">
                <div className="text-red-400 text-center">
                    <p className="text-lg font-semibold mb-2">Error loading simulation</p>
                    <p className="text-sm">{error}</p>
                </div>
            </div>
        )
    }

    if (!config) {
        return (
            <div className="w-full h-96 bg-gray-900 rounded-lg flex items-center justify-center">
                <div className="text-gray-400 text-center">
                    <p>No simulation configuration available</p>
                </div>
            </div>
        )
    }

    return (
        <>
            <style jsx>{`
                .slider::-webkit-slider-thumb {
                    appearance: none;
                    height: 16px;
                    width: 16px;
                    border-radius: 50%;
                    background: #8b5cf6;
                    cursor: pointer;
                }
                .slider::-moz-range-thumb {
                    height: 16px;
                    width: 16px;
                    border-radius: 50%;
                    background: #8b5cf6;
                    cursor: pointer;
                    border: none;
                }
            `}</style>
            <div className="w-full h-full bg-gray-900 rounded-lg overflow-hidden">
                {/* Simulation Title and Description */}
                <div className="bg-gray-800 p-4 border-b border-gray-700">
                    <h3 className="text-xl font-bold text-white mb-2">
                        {config.metadata?.title || 'Physics Simulation'}
                    </h3>
                    <p className="text-gray-300 text-sm mb-3">
                        {config.metadata?.description || 'Interactive physics simulation'}
                    </p>

                    {/* Physics Concepts */}
                    <div className="flex flex-wrap gap-2 mb-3">
                        {config.metadata?.physics_concepts?.map((concept: string, index: number) => (
                            <span
                                key={index}
                                className="px-2 py-1 bg-purple-600 text-white text-xs rounded-full"
                            >
                                {concept}
                            </span>
                        ))}
                    </div>

                    {/* Controls */}
                    <div className="flex gap-2">
                        <button
                            onClick={togglePause}
                            className={`px-4 py-2 rounded text-sm font-medium ${isPaused
                                ? 'bg-green-600 hover:bg-green-700 text-white'
                                : 'bg-yellow-600 hover:bg-yellow-700 text-white'
                                }`}
                        >
                            {isPaused ? '▶ Play' : '⏸ Pause'}
                        </button>

                        <button
                            onClick={resetSimulation}
                            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm font-medium"
                        >
                            🔄 Reset
                        </button>

                        <button
                            onClick={() => setShowField(!showField)}
                            className={`px-4 py-2 rounded text-sm font-medium ${showField
                                ? 'bg-purple-600 hover:bg-purple-700 text-white'
                                : 'bg-gray-600 hover:bg-gray-700 text-white'
                                }`}
                        >
                            {showField ? '🔬 Hide Field' : '🔬 Show Field'}
                        </button>
                    </div>

                    {/* Parameter Controls */}
                    <div className="mt-4">
                        <h4 className="text-white font-semibold mb-3">Customize Parameters</h4>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {getParametersForSimulation().map((param) => (
                                <div key={param.name} className="flex flex-col">
                                    <label className="text-gray-300 text-sm mb-1">
                                        {param.label}
                                    </label>
                                    <input
                                        type="range"
                                        min={param.min}
                                        max={param.max}
                                        step={param.step}
                                        value={param.value}
                                        onChange={(e) => updateParameter(param.name, parseFloat(e.target.value))}
                                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <span className="text-gray-400 text-xs mt-1 text-center">
                                        {param.value}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Simulation Canvas */}
                <div ref={canvasRef} className="w-full bg-gray-900" />

                {/* Educational Notes */}
                {config.metadata?.educational_notes && (
                    <div className="bg-gray-800 p-4 border-t border-gray-700">
                        <p className="text-gray-300 text-sm">
                            💡 <strong>Physics Note:</strong> {config.metadata.educational_notes}
                        </p>
                    </div>
                )}
            </div>
        </>
    )
}