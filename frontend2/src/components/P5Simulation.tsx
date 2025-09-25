'use client'

import React, { useEffect, useRef, useState } from 'react'
import p5 from 'p5'
import ThreeEMWaveInteractive from './ThreeEMWaveInteractive'

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

    // Use refs to store current state values that p5.js can access
    const isPausedRef = useRef(isPaused)
    const showFieldRef = useRef(showField)
    const simulationRef = useRef<any>(null) // Store simulation state

    // Keep refs in sync with state
    useEffect(() => {
        isPausedRef.current = isPaused
    }, [isPaused])

    useEffect(() => {
        showFieldRef.current = showField
    }, [showField])

    // User customizable parameters
    const [userParams, setUserParams] = useState<any>({
        // Electric field parameters
        electricFieldStrength: 1.0,
        charges: 4,
        showField: true,
        showForces: true,

        // Magnetic field parameters
        magneticFieldStrength: 1.0,
        particleCount: 3,
        showFieldLines: true,
        cyclotronMotion: true,

        // Wave motion parameters
        frequency: 1.0,
        amplitude: 50,
        wavelength: 100,
        waveSpeed: 200,
        showParticles: true,
        showEnvelope: false,

        // Oscillation parameters
        oscillatorCount: 3,
        coupling: 0.1,
        damping: 0.02,
        drivingForce: 0,
        showPhaseSpace: false,
        showBeats: true,

        // EM wave parameters
        emFrequency: 1.0,
        emAmplitude: 0.3, // Lower default amplitude
        showElectric: true,
        showMagnetic: true,
        showComponents: true,
        showPoynting: false
    })

    // Fetch simulation config
    useEffect(() => {
        const fetchConfig = async () => {
            try {
                setLoading(true)

                // Map frontend parameter names to backend expectations
                let mappedParams = { ...userParams }
                if (simulationType === 'electric_field') {
                    mappedParams = {
                        ...userParams,
                        fieldStrength: userParams.electricFieldStrength,
                    }
                    delete mappedParams.electricFieldStrength
                } else if (simulationType === 'magnetic_field') {
                    mappedParams = {
                        ...userParams,
                        fieldStrength: userParams.magneticFieldStrength,
                    }
                    delete mappedParams.magneticFieldStrength
                } else if (simulationType === 'wave_motion') {
                    // Backend expects: waveType, frequency, amplitude, wavelength, waveSpeed, interference, showParticles, showEnvelope
                    mappedParams = {
                        ...userParams,
                        frequency: userParams.waveFrequency || userParams.frequency,
                        amplitude: userParams.waveAmplitude || userParams.amplitude,
                    }
                    if ('waveFrequency' in mappedParams) delete mappedParams.waveFrequency
                    if ('waveAmplitude' in mappedParams) delete mappedParams.waveAmplitude
                } else if (simulationType === 'oscillation') {
                    // Backend expects: oscillatorCount, coupling, damping, drivingForce
                    // Parameters should already match - no mapping needed
                } else if (simulationType === 'em_wave') {
                    // Backend expects: frequency, amplitude, polarization, showElectric, showMagnetic, showPoynting, showComponents
                    mappedParams = {
                        ...userParams,
                        frequency: userParams.emFrequency || userParams.frequency,
                        amplitude: userParams.emAmplitude || userParams.amplitude,
                    }
                    if ('emFrequency' in mappedParams) delete mappedParams.emFrequency
                    if ('emAmplitude' in mappedParams) delete mappedParams.emAmplitude
                }

                console.log('Fetching p5 config for:', simulationType, 'with params:', mappedParams)
                const response = await fetch(`http://localhost:5000/simulation/api/simulation/p5`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        type: simulationType,
                        parameters: mappedParams
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
        // Skip p5.js setup for EM waves (handled by Three.js component)
        if (config?.type === 'em_wave') {
            // Clean up any existing p5 instance for EM waves
            if (p5InstanceRef.current) {
                p5InstanceRef.current.remove()
                p5InstanceRef.current = null
            }
            return
        }

        if (!canvasRef.current || !config) return

        // Clean up previous p5 instance
        if (p5InstanceRef.current) {
            p5InstanceRef.current.remove()
        }

        // Create new p5 sketch
        const sketch = (p: p5) => {
            let simulation: any = {}
            simulationRef.current = simulation // Store reference

            p.setup = () => {
                const canvas = p.createCanvas(
                    config.config.display.width,
                    config.config.display.height,
                    config.type === 'em_wave' ? p.WEBGL : undefined
                )
                canvas.parent(canvasRef.current!)

                // Prevent context menu on right-click
                canvas.elt.addEventListener('contextmenu', (e: Event) => e.preventDefault())

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
                        simulationRef.current = simulation // Update ref after setup
                        break
                    case 'em_wave':
                        setupEMWave(p, simulation, config.config)
                        break
                }
            }

            p.draw = () => {
                if (isPausedRef.current) return

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
                    handleElectricFieldMousePressed(p, simulation, p.mouseX, p.mouseY)
                } else if (config.type === 'oscillation') {
                    handleOscillationMousePressed(p, simulation, p.mouseX, p.mouseY)
                }
            }

            p.mouseDragged = () => {
                if (config.type === 'electric_field') {
                    handleElectricFieldMouseDragged(p, simulation, p.mouseX, p.mouseY)
                }
            }

            p.mouseReleased = () => {
                if (config.type === 'electric_field') {
                    handleElectricFieldMouseReleased(p, simulation)
                }
            }

            p.keyPressed = () => {
                if (config.type === 'electric_field') {
                    handleElectricFieldKeyPressed(p, simulation, p.key)
                } else if (config.type === 'em_wave') {
                    handleEMWaveKeyPressed(p, simulation, p.key)
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
    }, [config])

    // Electric Field Simulation Functions
    const setupElectricField = (p: p5, sim: any, config: any) => {
        sim.charges = config.charges.defaultPositions.map((pos: any) => ({
            x: pos.x,
            y: pos.y,
            charge: pos.charge,
            dragging: false,
            lastClickTime: 0
        }))
        sim.testCharge = null
        sim.fieldLines = []
    }

    const drawElectricField = (p: p5, sim: any, config: any) => {
        // Draw field lines if enabled
        if (config.field.showFieldLines && showFieldRef.current) {
            drawFieldLines(p, sim, config)
        }

        // Draw charges
        sim.charges.forEach((charge: any, index: number) => {
            // Highlight charge if being dragged
            if (charge.dragging) {
                p.fill(255, 255, 0, 100) // Yellow highlight
                p.stroke(255, 255, 0)
                p.strokeWeight(3)
                p.circle(charge.x, charge.y, Math.abs(charge.charge) * 25)
            }

            // Draw charge
            p.fill(charge.charge > 0 ? '#ff4444' : '#4444ff')
            p.stroke(255)
            p.strokeWeight(2)
            p.circle(charge.x, charge.y, Math.abs(charge.charge) * 20)

            // Draw charge symbol
            p.fill(255)
            p.textAlign(p.CENTER, p.CENTER)
            p.textSize(16)
            p.text(charge.charge > 0 ? '+' : '-', charge.x, charge.y)

            // Draw index number for identification
            p.fill(200)
            p.textSize(10)
            p.text(index + 1, charge.x, charge.y - 25)
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
        p.text('Double-click charges to flip sign', 10, 70)
        p.text('Press R to remove last charge', 10, 90)
        p.text('Press C to clear added charges', 10, 110)
    }

    const addCharge = (p: p5, sim: any, x: number, y: number) => {
        const newCharge = Math.random() > 0.5 ? 1 : -1
        sim.charges.push({
            x,
            y,
            charge: newCharge,
            dragging: false,
            lastClickTime: 0
        })
    }

    const handleElectricFieldMousePressed = (p: p5, sim: any, mouseX: number, mouseY: number) => {
        // Check if clicking on an existing charge
        let chargeClicked = false
        let clickedChargeIndex = -1

        sim.charges.forEach((charge: any, index: number) => {
            const distance = Math.sqrt((mouseX - charge.x) ** 2 + (mouseY - charge.y) ** 2)
            const radius = Math.abs(charge.charge) * 10 // Clickable radius
            if (distance < radius) {
                chargeClicked = true
                clickedChargeIndex = index

                // Check for double-click (flip charge sign)
                const currentTime = Date.now()
                if (charge.lastClickTime && (currentTime - charge.lastClickTime) < 300) {
                    // Double-click: flip charge sign
                    charge.charge *= -1
                    charge.lastClickTime = 0 // Reset to prevent triple-click
                } else {
                    // Single click: start dragging
                    charge.dragging = true
                    charge.lastClickTime = currentTime
                }
            }
        })

        // If not clicking on a charge, add a new one
        if (!chargeClicked) {
            addCharge(p, sim, mouseX, mouseY)
        }
    }

    const handleElectricFieldMouseDragged = (p: p5, sim: any, mouseX: number, mouseY: number) => {
        // Move any charges that are being dragged
        sim.charges.forEach((charge: any) => {
            if (charge.dragging) {
                charge.x = mouseX
                charge.y = mouseY
            }
        })
    }

    const handleElectricFieldMouseReleased = (p: p5, sim: any) => {
        // Stop dragging all charges
        sim.charges.forEach((charge: any) => {
            charge.dragging = false
        })
    }

    const handleElectricFieldKeyPressed = (p: p5, sim: any, key: string) => {
        if (key === 'r' || key === 'R') {
            // Remove the last charge
            if (sim.charges.length > 0) {
                sim.charges.pop()
            }
        } else if (key === 'c' || key === 'C') {
            // Clear all charges except the first few from config
            const originalCount = Math.min(2, sim.charges.length)
            sim.charges = sim.charges.slice(0, originalCount)
        }
    }

    const handleEMWaveKeyPressed = (p: p5, sim: any, key: string) => {
        if (key === 'v' || key === 'V') {
            // Toggle wave surfaces
            sim.showVectors = !sim.showVectors
        } else if (key === 'p' || key === 'P') {
            // Toggle Poynting vector
            if (config.fields) {
                config.fields.showPoynting = !config.fields.showPoynting
            }
        } else if (key === ' ') {
            // Toggle pause
            togglePause()
        }
    }

    const handleOscillationMousePressed = (p: p5, sim: any, mouseX: number, mouseY: number) => {
        // Find the closest oscillator to the mouse click
        let closestOsc: any = null
        let minDistance = Infinity

        sim.oscillators.forEach((osc: any) => {
            const distance = Math.sqrt((mouseX - osc.x) ** 2 + (mouseY - osc.y) ** 2)
            if (distance < minDistance) {
                minDistance = distance
                closestOsc = osc
            }
        })

        // If clicked close enough to an oscillator, give it a push
        if (closestOsc && minDistance < 50) {
            // Add displacement based on click position relative to equilibrium
            const displacement = (mouseY - closestOsc.baseY) * 0.5
            closestOsc.displacement += displacement

            // Also add some velocity for more dynamic response
            closestOsc.velocity += displacement * 0.1
        }
    }

    const applyOscillationPreset = (presetName: string) => {
        console.log('Applying preset:', presetName)
        const sim = simulationRef.current
        if (!sim || !sim.oscillators) {
            console.log('Simulation not ready or no oscillators found', sim)
            return
        }

        console.log('Found oscillators:', sim.oscillators.length)

        // Reset all oscillators first
        sim.oscillators.forEach((osc: any) => {
            osc.displacement = 0
            osc.velocity = 0
            if (osc.trail) osc.trail = [] // Clear trails
        })

        // Reset time
        sim.time = 0

        switch (presetName) {
            case 'wave':
                // Traveling wave - each oscillator starts with phase delay
                sim.oscillators.forEach((osc: any, index: number) => {
                    osc.displacement = 30 * Math.sin(index * 0.8)
                    osc.velocity = 15 * Math.cos(index * 0.8)
                })
                break

            case 'standing_wave':
                // Standing wave pattern
                sim.oscillators.forEach((osc: any, index: number) => {
                    osc.displacement = 40 * Math.sin((index * Math.PI) / (sim.oscillators.length - 1))
                    osc.velocity = 0
                })
                break

            case 'beats':
                // Two groups with slightly different frequencies for beats
                sim.oscillators.forEach((osc: any, index: number) => {
                    if (index < sim.oscillators.length / 2) {
                        osc.displacement = 35
                        osc.velocity = 0
                    } else {
                        osc.displacement = -35
                        osc.velocity = 0
                    }
                })
                break

            case 'single_pulse':
                // Single oscillator excited - watch energy transfer
                if (sim.oscillators.length > 0) {
                    sim.oscillators[0].displacement = 50
                    sim.oscillators[0].velocity = 20
                }
                break

            case 'resonance':
                // All oscillators in phase - fundamental mode
                sim.oscillators.forEach((osc: any) => {
                    osc.displacement = 40
                    osc.velocity = 0
                })
                break

            case 'anti_phase':
                // Alternating pattern - higher harmonic mode
                sim.oscillators.forEach((osc: any, index: number) => {
                    osc.displacement = index % 2 === 0 ? 40 : -40
                    osc.velocity = 0
                })
                break

            case 'chaos':
                // Random initial conditions
                sim.oscillators.forEach((osc: any) => {
                    osc.displacement = (Math.random() - 0.5) * 80
                    osc.velocity = (Math.random() - 0.5) * 40
                })
                break
        }
    }    // Magnetic Field Simulation Functions
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
        if (config.magneticField.showFieldLines && showFieldRef.current) {
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
        console.log('Setting up oscillation with config:', config.oscillators)
        sim.oscillators = config.oscillators.positions.map((pos: any, index: number) => ({
            x: pos.x,
            y: pos.y,
            baseY: pos.y,
            displacement: 0,
            velocity: 0,
            frequency: config.oscillators.naturalFrequencies[index],
            amplitude: config.oscillators.amplitudes[index],
            phase: config.oscillators.phases[index],
            mass: 1.0,
            springConstant: Math.pow(config.oscillators.naturalFrequencies[index] * 2 * Math.PI, 2),
            trail: [] // Add trail for visualization
        }))
        sim.time = 0
        sim.dt = 0.016 // Smoother animation (60fps)

        // Start with first oscillator displaced to show motion
        if (sim.oscillators.length > 0) {
            sim.oscillators[0].displacement = 40
            sim.oscillators[0].velocity = 10
        }
    }

    const drawOscillation = (p: p5, sim: any, config: any) => {
        sim.time += sim.dt

        // Update oscillators using proper physics
        sim.oscillators.forEach((osc: any, index: number) => {
            // Spring restoring force: F = -kx
            let force = -osc.springConstant * osc.displacement * osc.mass

            // Add coupling forces from neighbors
            if (index > 0) {
                // Coupling to left neighbor
                const leftOsc = sim.oscillators[index - 1]
                const couplingForce = config.coupling.strength * 1000 * (leftOsc.displacement - osc.displacement)
                force += couplingForce
            }
            if (index < sim.oscillators.length - 1) {
                // Coupling to right neighbor  
                const rightOsc = sim.oscillators[index + 1]
                const couplingForce = config.coupling.strength * 1000 * (rightOsc.displacement - osc.displacement)
                force += couplingForce
            }

            // Apply damping: F = -cv
            force -= config.damping.coefficient * 100 * osc.velocity * osc.mass

            // Add driving force if enabled
            if (config.driving.force > 0) {
                const drivingForce = config.driving.force * 50 * Math.sin(config.driving.frequency * 2 * Math.PI * sim.time + config.driving.phase)
                force += drivingForce
            }

            // Update velocity: v = v + (F/m)*dt
            const acceleration = force / osc.mass
            osc.velocity += acceleration * sim.dt

            // Update position: x = x + v*dt
            osc.displacement += osc.velocity * sim.dt

            // Update visual position
            osc.y = osc.baseY + osc.displacement

            // Prevent oscillators from going too far off screen
            if (Math.abs(osc.displacement) > 200) {
                osc.displacement = Math.sign(osc.displacement) * 200
                osc.velocity *= -0.5 // Bounce back with some energy loss
            }
        })

        // Draw oscillator trails
        sim.oscillators.forEach((osc: any, index: number) => {
            // Add current position to trail
            osc.trail.push({ x: osc.x, y: osc.y, time: sim.time })

            // Limit trail length
            if (osc.trail.length > 150) {
                osc.trail.shift()
            }

            // Draw trail
            if (osc.trail.length > 1) {
                p.stroke(255, 255, 0, 100)
                p.strokeWeight(1)
                p.noFill()
                p.beginShape()
                osc.trail.forEach((point: any) => {
                    p.vertex(point.x, point.y)
                })
                p.endShape()
            }
        })

        // Draw oscillators
        sim.oscillators.forEach((osc: any, index: number) => {
            // Draw spring/connection to equilibrium
            p.stroke(150)
            p.strokeWeight(2)
            p.line(osc.x, osc.baseY, osc.x, osc.y)

            // Draw equilibrium line
            p.stroke(100, 100, 100, 150)
            p.strokeWeight(1)
            p.line(osc.x - 30, osc.baseY, osc.x + 30, osc.baseY)

            // Color based on displacement direction and magnitude
            const displacementRatio = Math.abs(osc.displacement) / Math.max(osc.amplitude, 50)
            const intensity = Math.min(255, 100 + displacementRatio * 155)

            if (osc.displacement > 5) {
                p.fill(intensity, 100, 100) // Red for positive displacement
            } else if (osc.displacement < -5) {
                p.fill(100, 100, intensity) // Blue for negative displacement
            } else {
                p.fill(200, 200, 200) // Gray for equilibrium
            }

            p.stroke(255)
            p.strokeWeight(2)
            p.circle(osc.x, osc.y, 25)

            // Draw oscillator number
            p.fill(255)
            p.textAlign(p.CENTER, p.CENTER)
            p.textSize(12)
            p.text(index + 1, osc.x, osc.y)

            // Draw velocity vector (small arrow)
            if (Math.abs(osc.velocity) > 1) {
                p.stroke(0, 255, 0)
                p.strokeWeight(2)
                const velScale = 0.8
                const arrowEnd = osc.y + osc.velocity * velScale
                p.line(osc.x + 20, osc.y, osc.x + 20, arrowEnd)

                // Arrowhead
                if (Math.abs(osc.velocity) > 2) {
                    const arrowDir = osc.velocity > 0 ? 1 : -1
                    p.line(osc.x + 20, arrowEnd, osc.x + 17, arrowEnd - 4 * arrowDir)
                    p.line(osc.x + 20, arrowEnd, osc.x + 23, arrowEnd - 4 * arrowDir)
                }
            }
        })        // Draw coupling connections
        if (config.coupling.showConnections) {
            for (let i = 0; i < sim.oscillators.length - 1; i++) {
                const osc1 = sim.oscillators[i]
                const osc2 = sim.oscillators[i + 1]

                // Color based on relative displacement (tension/compression)
                const relativeDiff = osc2.displacement - osc1.displacement
                const tension = Math.abs(relativeDiff)
                const alpha = Math.min(255, 50 + tension * 10)

                if (relativeDiff > 0) {
                    p.stroke(255, 100, 0, alpha) // Orange for extension
                } else {
                    p.stroke(0, 150, 255, alpha) // Blue for compression
                }

                p.strokeWeight(Math.max(1, tension * 0.1))
                p.line(osc1.x, osc1.y, osc2.x, osc2.y)
            }
        }

        // Draw wave pattern trace
        if (config.display.showBeats && sim.oscillators.length > 0) {
            p.stroke(255, 255, 0, 100)
            p.strokeWeight(1)
            p.noFill()
            p.beginShape()
            sim.oscillators.forEach((osc: any) => {
                p.vertex(osc.x, osc.y)
            })
            p.endShape()
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
        p.text(`Time: ${sim.time.toFixed(1)}s`, 10, 70)

        // Show energy information
        let totalEnergy = 0
        sim.oscillators.forEach((osc: any) => {
            const kineticEnergy = 0.5 * osc.mass * osc.velocity * osc.velocity
            const potentialEnergy = 0.5 * osc.springConstant * osc.displacement * osc.displacement
            totalEnergy += kineticEnergy + potentialEnergy
        })
        p.text(`Total Energy: ${totalEnergy.toFixed(1)}`, 10, 90)

        // Instructions
        p.textSize(12)
        p.fill(200)
        p.text('Red: Positive displacement', 10, 120)
        p.text('Blue: Negative displacement', 10, 135)
        p.text('Green arrows: Velocity vectors', 10, 150)
        p.text('Click to excite oscillators', 10, 165)
        p.text('Use presets below for examples', 10, 180)
    }

    // EM Wave Simulation Functions
    const setupEMWave = (p: p5, sim: any, config: any) => {
        sim.time = 0
        sim.animationSpeed = 0.02
        sim.showVectors = false
    }

    const drawEMWave = (p: p5, sim: any, config: any) => {
        sim.time += sim.animationSpeed

        // Simple dark background
        p.background(20, 25, 40)

        // Basic 3D setup
        p.lights()

        // Simple rotating camera
        const cameraAngle = sim.time * 0.05
        p.camera(
            300 * Math.cos(cameraAngle), -50, 300 * Math.sin(cameraAngle),
            0, 0, 0,
            0, 1, 0
        )

        // Wave parameters
        const wavelength = config.wave.wavelength * 2
        const frequency = config.wave.frequency
        const amplitude = config.wave.amplitude * 60

        // Draw simple coordinate axes
        p.strokeWeight(2)
        p.stroke(100, 100, 100)
        p.line(-100, 0, 0, 100, 0, 0) // X-axis
        p.line(0, -80, 0, 0, 80, 0)   // Y-axis
        p.line(0, 0, -80, 0, 0, 80)   // Z-axis

        // Draw the electromagnetic wave
        const numPoints = 50

        for (let i = 0; i < numPoints; i++) {
            const x = p.map(i, 0, numPoints - 1, -100, 100)
            const wavePhase = (2 * Math.PI * x / wavelength) - (2 * Math.PI * frequency * sim.time)

            // Electric field (red, oscillates in Y direction)
            if (config.fields.showElectric) {
                const E_y = amplitude * Math.sin(wavePhase)

                p.stroke(255, 100, 100)
                p.strokeWeight(3)
                p.line(x, 0, 0, x, E_y, 0)

                // Simple arrowhead
                if (Math.abs(E_y) > 10) {
                    p.push()
                    p.translate(x, E_y, 0)
                    p.fill(255, 150, 150)
                    p.noStroke()
                    p.sphere(2)
                    p.pop()
                }
            }

            // Magnetic field (green, oscillates in Z direction)
            if (config.fields.showMagnetic) {
                const B_z = amplitude * Math.sin(wavePhase)

                p.stroke(100, 255, 100)
                p.strokeWeight(3)
                p.line(x, 0, 0, x, 0, B_z)

                // Simple arrowhead
                if (Math.abs(B_z) > 10) {
                    p.push()
                    p.translate(x, 0, B_z)
                    p.fill(150, 255, 150)
                    p.noStroke()
                    p.sphere(2)
                    p.pop()
                }
            }
        }

        // Draw wave surfaces if vectors are enabled
        if (sim.showVectors) {
            // Electric field surface (red)
            if (config.fields.showElectric) {
                p.noFill()
                p.stroke(255, 100, 100, 150)
                p.strokeWeight(1)

                p.beginShape()
                for (let i = 0; i < numPoints; i++) {
                    const x = p.map(i, 0, numPoints - 1, -100, 100)
                    const wavePhase = (2 * Math.PI * x / wavelength) - (2 * Math.PI * frequency * sim.time)
                    const E_y = amplitude * Math.sin(wavePhase)
                    p.vertex(x, E_y, 0)
                }
                p.endShape()
            }

            // Magnetic field surface (green)
            if (config.fields.showMagnetic) {
                p.noFill()
                p.stroke(100, 255, 100, 150)
                p.strokeWeight(1)

                p.beginShape()
                for (let i = 0; i < numPoints; i++) {
                    const x = p.map(i, 0, numPoints - 1, -100, 100)
                    const wavePhase = (2 * Math.PI * x / wavelength) - (2 * Math.PI * frequency * sim.time)
                    const B_z = amplitude * Math.sin(wavePhase)
                    p.vertex(x, 0, B_z)
                }
                p.endShape()
            }
        }

        // Simple Poynting vector (energy flow)
        if (config.fields.showPoynting) {
            for (let i = 0; i < numPoints; i += 5) {
                const x = p.map(i, 0, numPoints - 1, -100, 100)
                const wavePhase = (2 * Math.PI * x / wavelength) - (2 * Math.PI * frequency * sim.time)
                const energy = Math.abs(Math.sin(wavePhase)) * 20

                if (energy > 5) {
                    p.stroke(255, 255, 100)
                    p.strokeWeight(4)
                    p.line(x - energy / 2, 0, 0, x + energy / 2, 0, 0)

                    // Simple arrow
                    p.push()
                    p.translate(x + energy / 2, 0, 0)
                    p.fill(255, 255, 150)
                    p.noStroke()
                    p.sphere(1.5)
                    p.pop()
                }
            }
        }

        // Reset to 2D for UI
        p.camera()
        drawEMWaveInfo(p, sim, config)
    }

    const drawEMWaveInfo = (p: p5, sim: any, config: any) => {
        // Enhanced info panel with gradient background
        p.fill(0, 10, 30, 200)
        p.stroke(50, 100, 150, 150)
        p.strokeWeight(2)
        p.rect(10, 10, 320, 185, 12)

        // Inner glow effect
        p.fill(20, 40, 80, 100)
        p.noStroke()
        p.rect(12, 12, 316, 181, 10)

        p.textAlign(p.LEFT, p.TOP)
        p.textSize(14)

        let infoY = 25
        const infoX = 20
        const lineHeight = 18

        // Title with glow
        p.fill(150, 200, 255, 255)
        p.textSize(16)
        p.text('3D Electromagnetic Wave', infoX, infoY)
        infoY += lineHeight + 3

        // Wave properties
        p.fill(255, 255, 150, 255)
        p.textSize(13)
        p.text('Wave Properties:', infoX, infoY)
        infoY += lineHeight

        p.fill(255, 255, 255, 230)
        p.textSize(12)
        p.text(`Frequency: ${config.wave.frequency.toFixed(2)} Hz`, infoX + 10, infoY)
        infoY += lineHeight - 2
        p.text(`Wavelength: ${config.wave.wavelength.toFixed(1)} units`, infoX + 10, infoY)
        infoY += lineHeight - 2
        p.text(`Amplitude: ${config.wave.amplitude.toFixed(2)}`, infoX + 10, infoY)
        infoY += lineHeight - 2
        p.text(`Speed: ${(config.wave.frequency * config.wave.wavelength).toFixed(1)} units/s`, infoX + 10, infoY)
        infoY += lineHeight

        // Real-time physics info
        p.fill(150, 255, 150, 255)
        p.textSize(13)
        p.text('Real-time Physics:', infoX, infoY)
        infoY += lineHeight

        p.fill(200, 255, 200, 230)
        p.textSize(12)
        const currentPhase = (sim.time * config.wave.frequency * 2 * Math.PI % (2 * Math.PI))
        p.text(`Phase: ${currentPhase.toFixed(2)} rad`, infoX + 10, infoY)
        infoY += lineHeight - 2

        const energyDensity = Math.sin(currentPhase) * Math.sin(currentPhase) * config.wave.amplitude * config.wave.amplitude
        p.text(`Energy Density: ${energyDensity.toFixed(3)}`, infoX + 10, infoY)
        infoY += lineHeight

        // Field visualization status
        p.fill(255, 200, 100, 255)
        p.textSize(13)
        p.text('Field Visualization:', infoX, infoY)
        infoY += lineHeight

        p.fill(255, 230, 180, 230)
        p.textSize(12)
        const fieldsVisible = []
        if (config.fields.showElectric) fieldsVisible.push('E-field (red)')
        if (config.fields.showMagnetic) fieldsVisible.push('B-field (green)')
        if (config.fields.showPoynting) fieldsVisible.push('Poynting (yellow)')
        if (sim.showVectors) fieldsVisible.push('Vectors ON')

        const fieldsText = fieldsVisible.join(', ') || 'None visible'
        p.text(`Active: ${fieldsText}`, infoX + 10, infoY)
        infoY += lineHeight + 5

        // Simple controls
        p.fill(180, 180, 200, 200)
        p.textSize(11)
        p.text('Controls:', infoX, infoY)
        infoY += 15
        p.fill(200, 200, 220, 180)
        p.textSize(10)
        p.text('V: Toggle wave surfaces  |  P: Toggle Poynting vector', infoX, infoY)
        infoY += 12
        p.text('Space: Pause/Resume  |  Camera: Auto-rotating', infoX, infoY)

        // Physics note
        p.fill(150, 150, 180, 150)
        p.textSize(9)
        p.text('3D EM Wave: E-field (red, Y-axis) ⊥ B-field (green, Z-axis)', infoX, infoY + 15)
    }

    const togglePause = () => {
        const newPausedState = !isPaused
        setIsPaused(newPausedState)
        isPausedRef.current = newPausedState
    }

    const resetSimulation = () => {
        // Reset pause state
        setIsPaused(false)
        isPausedRef.current = false

        // Reset field visibility
        setShowField(true)
        showFieldRef.current = true

        // Reset user parameters to defaults
        setUserParams({
            // Electric field parameters
            electricFieldStrength: 1.0,
            charges: 4,
            showField: true,
            showForces: true,

            // Magnetic field parameters
            magneticFieldStrength: 1.0,
            particleCount: 3,
            showFieldLines: true,
            cyclotronMotion: true,

            // Wave motion parameters
            frequency: 1.0,
            amplitude: 50,
            wavelength: 100,
            waveSpeed: 200,
            showParticles: true,
            showEnvelope: false,

            // Oscillation parameters
            oscillatorCount: 3,
            coupling: 0.1,
            damping: 0.02,
            drivingForce: 0,
            showPhaseSpace: false,
            showBeats: true,

            // EM wave parameters
            emFrequency: 1.0,
            emAmplitude: 0.3,
            emPhase: 0,
            showElectric: true,
            showMagnetic: true,
            showComponents: true,
            showPoynting: false
        })
    }

    const updateParameter = (paramName: string, value: number | boolean) => {
        setUserParams((prev: any) => ({
            ...prev,
            [paramName]: value
        }))

        // Also notify parent component if callback exists
        if (onParameterChange) {
            onParameterChange(paramName, typeof value === 'boolean' ? (value ? 1 : 0) : value)
        }
    }

    const getParametersForSimulation = () => {
        switch (simulationType) {
            case 'electric_field':
                return [
                    { name: 'electricFieldStrength', label: 'Field Strength', value: userParams.electricFieldStrength, min: 0.1, max: 3, step: 0.1 },
                    { name: 'charges', label: 'Number of Charges', value: userParams.charges, min: 2, max: 8, step: 1 },
                    { name: 'showField', label: 'Show Field Lines', value: userParams.showField, type: 'boolean' },
                    { name: 'showForces', label: 'Show Forces', value: userParams.showForces, type: 'boolean' }
                ]
            case 'magnetic_field':
                return [
                    { name: 'magneticFieldStrength', label: 'Magnetic Strength', value: userParams.magneticFieldStrength, min: 0.1, max: 2, step: 0.1 },
                    { name: 'particleCount', label: 'Particle Count', value: userParams.particleCount, min: 1, max: 5, step: 1 },
                    { name: 'showFieldLines', label: 'Show Field Lines', value: userParams.showFieldLines, type: 'boolean' },
                    { name: 'cyclotronMotion', label: 'Cyclotron Motion', value: userParams.cyclotronMotion, type: 'boolean' }
                ]
            case 'wave_motion':
                return [
                    { name: 'frequency', label: 'Frequency', value: userParams.frequency, min: 0.1, max: 3, step: 0.1 },
                    { name: 'amplitude', label: 'Amplitude', value: userParams.amplitude, min: 10, max: 100, step: 10 },
                    { name: 'wavelength', label: 'Wavelength', value: userParams.wavelength, min: 50, max: 200, step: 10 },
                    { name: 'waveSpeed', label: 'Wave Speed', value: userParams.waveSpeed, min: 50, max: 400, step: 25 },
                    { name: 'showParticles', label: 'Show Particles', value: userParams.showParticles, type: 'boolean' },
                    { name: 'showEnvelope', label: 'Show Envelope', value: userParams.showEnvelope, type: 'boolean' }
                ]
            case 'oscillation':
                return [
                    { name: 'oscillatorCount', label: 'Number of Oscillators', value: userParams.oscillatorCount, min: 2, max: 5, step: 1 },
                    { name: 'coupling', label: 'Coupling Strength', value: userParams.coupling, min: 0, max: 0.5, step: 0.05 },
                    { name: 'damping', label: 'Damping', value: userParams.damping, min: 0, max: 0.1, step: 0.01 },
                    { name: 'drivingForce', label: 'Driving Force', value: userParams.drivingForce, min: 0, max: 1, step: 0.1 },
                    { name: 'showPhaseSpace', label: 'Show Phase Space', value: userParams.showPhaseSpace, type: 'boolean' },
                    { name: 'showBeats', label: 'Show Beats', value: userParams.showBeats, type: 'boolean' }
                ]
            case 'em_wave':
                return [
                    { name: 'emFrequency', label: 'Frequency (Hz)', value: userParams.emFrequency, min: 0.1, max: 5, step: 0.1 },
                    { name: 'emAmplitude', label: 'Amplitude', value: userParams.emAmplitude, min: 0.5, max: 5, step: 0.1 },
                    { name: 'emPhase', label: 'Phase (degrees)', value: userParams.emPhase, min: 0, max: 360, step: 10 },
                    { name: 'showElectric', label: 'Show Electric Field', value: userParams.showElectric, type: 'boolean' },
                    { name: 'showMagnetic', label: 'Show Magnetic Field', value: userParams.showMagnetic, type: 'boolean' },
                    { name: 'showComponents', label: 'Show Components', value: userParams.showComponents, type: 'boolean' },
                    { name: 'showPoynting', label: 'Show Poynting Vector', value: userParams.showPoynting, type: 'boolean' }
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
                            onClick={() => {
                                const newShowFieldState = !showField
                                setShowField(newShowFieldState)
                                showFieldRef.current = newShowFieldState
                            }}
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
                                    {param.type === 'boolean' ? (
                                        <div className="flex items-center">
                                            <input
                                                type="checkbox"
                                                checked={param.value}
                                                onChange={(e) => updateParameter(param.name, e.target.checked)}
                                                className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500 focus:ring-2"
                                            />
                                            <span className="ml-2 text-gray-400 text-xs">
                                                {param.value ? 'On' : 'Off'}
                                            </span>
                                        </div>
                                    ) : (
                                        <>
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
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Oscillation Presets */}
                    {simulationType === 'oscillation' && (
                        <div className="mt-4">
                            <h4 className="text-white font-semibold mb-3">Example Oscillation Patterns</h4>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                                <button
                                    onClick={() => {
                                        console.log('Wave button clicked')
                                        applyOscillationPreset('wave')
                                    }}
                                    className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition-colors"
                                >
                                    🌊 Traveling Wave
                                </button>
                                <button
                                    onClick={() => applyOscillationPreset('standing_wave')}
                                    className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition-colors"
                                >
                                    📊 Standing Wave
                                </button>
                                <button
                                    onClick={() => applyOscillationPreset('beats')}
                                    className="px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded text-sm font-medium transition-colors"
                                >
                                    🎵 Beats
                                </button>
                                <button
                                    onClick={() => applyOscillationPreset('single_pulse')}
                                    className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm font-medium transition-colors"
                                >
                                    💥 Energy Transfer
                                </button>
                                <button
                                    onClick={() => applyOscillationPreset('resonance')}
                                    className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm font-medium transition-colors"
                                >
                                    🎯 Resonance
                                </button>
                                <button
                                    onClick={() => applyOscillationPreset('anti_phase')}
                                    className="px-3 py-2 bg-pink-600 hover:bg-pink-700 text-white rounded text-sm font-medium transition-colors"
                                >
                                    ⚡ Anti-Phase
                                </button>
                                <button
                                    onClick={() => applyOscillationPreset('chaos')}
                                    className="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded text-sm font-medium transition-colors"
                                >
                                    🌀 Random
                                </button>
                            </div>
                            <div className="mt-3 text-gray-400 text-xs">
                                <p>💡 <strong>Tips:</strong> Try different coupling strengths with each pattern!</p>
                                <p>• <strong>Low coupling (0.01-0.05):</strong> Oscillators act independently</p>
                                <p>• <strong>Medium coupling (0.1-0.2):</strong> Smooth wave propagation</p>
                                <p>• <strong>High coupling (0.3+):</strong> Synchronized motion</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Simulation Canvas */}
                {config.type === 'em_wave' ? (
                    <div className="w-full h-[600px] relative">
                        <ThreeEMWaveInteractive
                            key={`${userParams.emAmplitude}-${userParams.emFrequency}-${userParams.emPhase}-${userParams.showElectric}-${userParams.showMagnetic}`}
                            parameters={{
                                amplitude: userParams.emAmplitude || userParams.amplitude || config.config.amplitude || 1,
                                frequency: userParams.emFrequency || userParams.frequency || config.config.frequency || 1,
                                wavelength: config.config.wavelength || (3 / (userParams.emFrequency || userParams.frequency || 1)) || 3,
                                speed: config.config.speed || 299792458,
                                direction: config.config.direction || 'positive-z',
                                phase: userParams.emPhase || 0,
                                polarization: 'linear',
                                showElectric: userParams.showElectric,
                                showMagnetic: userParams.showMagnetic,
                                showPoynting: userParams.showPoynting
                            }}
                        />
                    </div>
                ) : (
                    <div ref={canvasRef} className="w-full bg-gray-900" />
                )}

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