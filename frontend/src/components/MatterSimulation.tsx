'use client'

import React, { useEffect, useRef, useState } from 'react'
import { Engine, Render, Runner, Bodies, Composite, Constraint, Mouse, MouseConstraint, Body, Events } from 'matter-js'

interface MatterSimulationProps {
    simulationType: string
    onParameterChange?: (parameter: string, value: number) => void
}

export default function MatterSimulation({ simulationType, onParameterChange }: MatterSimulationProps) {
    const sceneRef = useRef<HTMLDivElement>(null)
    const engineRef = useRef<Engine | null>(null)
    const renderRef = useRef<Render | null>(null)
    const runnerRef = useRef<Runner | null>(null)
    const [isPaused, setIsPaused] = useState(false)
    const [showTrails, setShowTrails] = useState(true)
    const [config, setConfig] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    // User customizable parameters
    const [userParams, setUserParams] = useState<any>({
        // Pendulum parameters (matching backend expectations)
        length: 200,
        mass: 1,
        gravity: 0.8,
        damping: 0.99,
        angle: 45,
        // Collision parameters
        ballCount: 8,
        restitution: 0.8,
        friction: 0.1,
        airResistance: 0.01,
        // Spring parameters
        springConstant: 0.05,
        springMass: 1.5,
        initialDisplacement: 100,
        // Projectile parameters
        velocity: 15,
        projectileAngle: 45,
        projectileGravity: 0.5,
        projectileAirResistance: 0.02,
        launchHeight: 200
    })

    // Fetch simulation config
    useEffect(() => {
        const fetchConfig = async () => {
            try {
                setLoading(true)

                // Map frontend parameter names to backend expectations
                let mappedParams = { ...userParams }
                if (simulationType === 'spring') {
                    mappedParams = {
                        ...userParams,
                        mass: userParams.springMass, // Map springMass to mass for backend
                    }
                    delete mappedParams.springMass // Remove the frontend-only property
                } else if (simulationType === 'projectile') {
                    mappedParams = {
                        ...userParams,
                        angle: userParams.projectileAngle, // Map projectileAngle to angle
                        gravity: userParams.projectileGravity, // Map projectileGravity to gravity
                        airResistance: userParams.projectileAirResistance, // Map projectileAirResistance to airResistance
                    }
                    // Remove frontend-only properties
                    delete mappedParams.projectileAngle
                    delete mappedParams.projectileGravity
                    delete mappedParams.projectileAirResistance
                }

                console.log('Fetching config for:', simulationType, 'with params:', mappedParams) // Debug log
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
                const response = await fetch(`${apiUrl}/simulation/api/simulation/matter`, {
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
                console.log('Received config:', data.simulation) // Debug log
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
        if (!sceneRef.current || !config) return

        // Clean up previous simulation
        if (engineRef.current) {
            Render.stop(renderRef.current!)
            Runner.stop(runnerRef.current!)
            Engine.clear(engineRef.current)
            renderRef.current!.canvas.remove()
        }

        // Create engine
        const engine = Engine.create()
        engine.world.gravity.y = config.config.world?.gravity || 1

        // Create renderer
        const render = Render.create({
            element: sceneRef.current,
            engine: engine,
            options: {
                width: config.config.display.width,
                height: config.config.display.height,
                wireframes: false,
                background: '#1a1a1a',
                showAngleIndicator: true,
                showVelocity: config.config.display.showVelocityVectors || false,
            }
        })

        // Create simulation based on type
        switch (config.type) {
            case 'pendulum':
                createPendulumSimulation(engine, config.config)
                break
            case 'collision':
                createCollisionSimulation(engine, config.config)
                break
            case 'spring':
                createSpringSimulation(engine, config.config)
                break
            case 'projectile':
                createProjectileSimulation(engine, config.config)
                break
        }

        // Add mouse control
        const mouse = Mouse.create(render.canvas)
        const mouseConstraint = MouseConstraint.create(engine, {
            mouse: mouse,
            constraint: {
                stiffness: 0.2,
                render: {
                    visible: false
                }
            }
        })
        Composite.add(engine.world, mouseConstraint)

        // Add trail tracking for projectiles - draw directly on render canvas
        if (config.type === 'projectile') {
            // Track projectile position and draw trail directly on render canvas
            const afterRender = () => {
                const bodies = Composite.allBodies(engine.world)
                const projectile = bodies.find((body: any) => body.isProjectile)

                if (projectile && showTrails) {
                    const trail = (projectile as any).trail

                    // Add current position to trail (record every few frames for better spacing)
                    const frameCount = (engine as any).frameCount || 0
                    if (frameCount % 3 === 0) { // Record every 3rd frame for better dot spacing
                        trail.push({
                            x: projectile.position.x,
                            y: projectile.position.y,
                            timestamp: Date.now()
                        })
                    }

                    // Limit trail length to prevent memory issues
                    if (trail.length > 100) {
                        trail.shift()
                    }

                    // Draw dotted trail directly on the render canvas
                    const renderContext = render.canvas.getContext('2d')!
                    if (trail.length > 0) {
                        // Draw dotted trail - each dot represents a position in time
                        trail.forEach((point: any, index: number) => {
                            const alpha = Math.max(0.4, (index / trail.length)) // Fade older dots
                            const dotSize = Math.max(1.5, 3 * (index / trail.length)) // Larger dots for recent positions

                            renderContext.fillStyle = `rgba(33, 150, 243, ${alpha})`
                            renderContext.beginPath()
                            renderContext.arc(point.x, point.y, dotSize, 0, Math.PI * 2)
                            renderContext.fill()

                            // Add white outline for better visibility
                            renderContext.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.3})`
                            renderContext.lineWidth = 1
                            renderContext.stroke()
                        })
                    }

                    // Increment frame counter
                    ; (engine as any).frameCount = frameCount + 1
                }
            }

            // Add the event listener for trail tracking - use afterRender to draw on canvas
            Events.on(render, 'afterRender', afterRender)
        }

        // Start the engine and renderer
        const runner = Runner.create()
        Runner.run(runner, engine)
        Render.run(render)

        // Store references
        engineRef.current = engine
        renderRef.current = render
        runnerRef.current = runner

        return () => {
            if (render.canvas) {
                Render.stop(render)
                render.canvas.remove()
            }
            Runner.stop(runner)
            Engine.clear(engine)
        }
    }, [config])

    const createPendulumSimulation = (engine: Engine, config: any) => {
        const { pendulum, world } = config

        // Create anchor point
        const anchor = Bodies.circle(pendulum.anchorX, pendulum.anchorY, 5, {
            isStatic: true,
            render: { fillStyle: '#ffffff' }
        })

        // Create pendulum bob
        const bob = Bodies.circle(
            pendulum.anchorX + pendulum.length * Math.sin(pendulum.initialAngle),
            pendulum.anchorY + pendulum.length * Math.cos(pendulum.initialAngle),
            pendulum.bobRadius,
            {
                mass: pendulum.mass,
                render: { fillStyle: '#4CAF50' },
                frictionAir: 1 - world.damping
            }
        )

        // Create constraint (string)
        const constraint = Constraint.create({
            bodyA: anchor,
            bodyB: bob,
            length: pendulum.length,
            stiffness: 1,
            render: {
                strokeStyle: '#ffffff',
                lineWidth: 2
            }
        })

        Composite.add(engine.world, [anchor, bob, constraint])
    }

    const createCollisionSimulation = (engine: Engine, config: any) => {
        const { balls, world } = config

        // Create boundaries
        const ground = Bodies.rectangle(
            world.bounds.width / 2,
            world.bounds.height - world.bounds.wallThickness / 2,
            world.bounds.width,
            world.bounds.wallThickness,
            { isStatic: true, render: { fillStyle: '#666' } }
        )

        const leftWall = Bodies.rectangle(
            world.bounds.wallThickness / 2,
            world.bounds.height / 2,
            world.bounds.wallThickness,
            world.bounds.height,
            { isStatic: true, render: { fillStyle: '#666' } }
        )

        const rightWall = Bodies.rectangle(
            world.bounds.width - world.bounds.wallThickness / 2,
            world.bounds.height / 2,
            world.bounds.wallThickness,
            world.bounds.height,
            { isStatic: true, render: { fillStyle: '#666' } }
        )

        // Create balls
        const ballBodies = []
        for (let i = 0; i < balls.count; i++) {
            const radius = balls.minRadius + Math.random() * (balls.maxRadius - balls.minRadius)
            const x = radius + Math.random() * (world.bounds.width - 2 * radius)
            const y = radius + Math.random() * (world.bounds.height / 2)

            const ball = Bodies.circle(x, y, radius, {
                restitution: balls.restitution,
                friction: balls.friction,
                density: balls.density,
                render: {
                    fillStyle: `hsl(${Math.random() * 360}, 70%, 60%)`
                }
            })

            ballBodies.push(ball)
        }

        Composite.add(engine.world, [ground, leftWall, rightWall, ...ballBodies])
    }

    const createSpringSimulation = (engine: Engine, config: any) => {
        const { spring, mass: massConfig, world } = config

        // Create anchor point (bigger and more visible)
        const anchor = Bodies.circle(spring.anchorX, spring.anchorY, 8, {
            isStatic: true,
            render: {
                fillStyle: '#ffffff',
                strokeStyle: '#cccccc',
                lineWidth: 2
            }
        })

        // Create mass (with better visual feedback)
        const mass = Bodies.circle(
            massConfig.initialX,
            massConfig.initialY,
            massConfig.radius,
            {
                mass: massConfig.mass,
                render: {
                    fillStyle: '#FF5722',
                    strokeStyle: '#D32F2F',
                    lineWidth: 2
                },
                frictionAir: 0.001, // Very low air resistance for better oscillation
                restitution: 0.8 // Some bounciness
            }
        )

        // Create spring constraint with enhanced visuals
        const springConstraint = Constraint.create({
            bodyA: anchor,
            bodyB: mass,
            length: spring.restLength,
            stiffness: spring.stiffness * 5, // Much higher stiffness for visible oscillation
            damping: 0.001, // Even lower damping
            render: {
                type: 'line',
                strokeStyle: '#4CAF50',
                lineWidth: 4,
                visible: true
            }
        })

        // Create equilibrium line (visual reference)
        const equilibriumY = spring.anchorY + spring.restLength
        const equilibriumLine = Bodies.rectangle(
            spring.anchorX, equilibriumY, 100, 2,
            {
                isStatic: true,
                render: {
                    fillStyle: '#FFC107',
                    strokeStyle: '#FF8F00',
                    lineWidth: 1
                },
                isSensor: true // Doesn't interfere with physics
            }
        )

        // Add initial impulse to start vertical oscillation
        setTimeout(() => {
            if (mass) {
                Body.applyForce(mass, mass.position, { x: 0, y: 0.05 }) // Only vertical force for spring motion
            }
        }, 100)

        // Add initial strong impulse to start oscillation immediately
        setTimeout(() => {
            if (mass) {
                Body.applyForce(mass, mass.position, { x: 0, y: 0.1 }) // Strong vertical force
            }
        }, 50) // Very quick start

            // Store mass reference for external force application
            ; (mass as any).isSpringMass = true

        Composite.add(engine.world, [anchor, mass, springConstraint, equilibriumLine])
    }

    const createProjectileSimulation = (engine: Engine, config: any) => {
        const { projectile, world, target } = config

        // Create ground
        const ground = Bodies.rectangle(
            400, 550, 800, 50,
            { isStatic: true, render: { fillStyle: '#8BC34A' } }
        )

        // Create launcher (yellow bar - adjustable height)
        const launcher = Bodies.rectangle(
            projectile.launchX, projectile.launchY, 40, 8,
            {
                isStatic: true,
                render: {
                    fillStyle: '#FFC107',
                    strokeStyle: '#FF8F00',
                    lineWidth: 2
                }
            }
        )

        // Create target with enhanced visuals
        const targetBody = Bodies.circle(target.x, target.y, target.radius, {
            isStatic: true,
            render: {
                fillStyle: '#F44336',
                strokeStyle: '#D32F2F',
                lineWidth: 2
            }
        })

        // Create projectile with trail tracking
        const velocityX = projectile.velocity * Math.cos(projectile.angle)
        const velocityY = -projectile.velocity * Math.sin(projectile.angle)

        const projectileBody = Bodies.circle(
            projectile.launchX, projectile.launchY - 20, projectile.radius,
            {
                mass: projectile.mass,
                restitution: projectile.restitution,
                render: {
                    fillStyle: '#2196F3',
                    strokeStyle: '#1976D2',
                    lineWidth: 2
                }
            }
        )

            // Initialize trail array for the projectile
            ; (projectileBody as any).trail = []
            ; (projectileBody as any).isProjectile = true

        // Set initial velocity
        engine.world.gravity.y = world.gravity
        Body.setVelocity(projectileBody, { x: velocityX, y: velocityY })

        Composite.add(engine.world, [ground, launcher, targetBody, projectileBody])
    }

    const togglePause = () => {
        if (!runnerRef.current || !engineRef.current) return

        if (isPaused) {
            Runner.run(runnerRef.current, engineRef.current) // Use Runner.run to resume
        } else {
            Runner.stop(runnerRef.current) // Use Runner.stop to pause
        }
        setIsPaused(!isPaused)
    }

    const resetSimulation = () => {
        if (!engineRef.current || !renderRef.current || !runnerRef.current) return

        // Stop the current simulation
        Runner.stop(runnerRef.current)
        Render.stop(renderRef.current)

        // Clear the world
        Composite.clear(engineRef.current.world, false)
        Engine.clear(engineRef.current)

        // Remove the canvas
        if (renderRef.current.canvas) {
            renderRef.current.canvas.remove()
        }

        // Reset pause state
        setIsPaused(false)

        // Force re-render by updating a key state
        setConfig((prevConfig: typeof config) => ({
            ...prevConfig!,
            // Add a timestamp to force re-render
            resetTimestamp: Date.now()
        }))
    }

    const applySpringForce = () => {
        if (!engineRef.current) return

        // Find the spring mass body
        const bodies = Composite.allBodies(engineRef.current.world)
        const springMass = bodies.find((body: any) => body.isSpringMass)

        if (springMass) {
            // Apply only vertical force for proper spring oscillation (no horizontal swing)
            const forceY = (Math.random() - 0.5) * 0.08 // Random vertical force between -0.04 and +0.04

            Body.applyForce(springMass, springMass.position, {
                x: 0, // No horizontal force - keep it vertical
                y: forceY
            })

            console.log(`Applied vertical spring force: y=${forceY.toFixed(3)}`)
        }
    }

    const resetTrail = () => {
        if (!engineRef.current) return

        // Find the projectile body and clear its trail
        const bodies = Composite.allBodies(engineRef.current.world)
        const projectile = bodies.find((body: any) => body.isProjectile)

        if (projectile) {
            ; (projectile as any).trail = []
            console.log('Trail reset for projectile')
        }
    }

    const updateParameter = (paramName: string, value: number) => {
        setUserParams((prev: any) => ({
            ...prev,
            [paramName]: value
        }))
    }

    const getParametersForSimulation = () => {
        switch (simulationType) {
            case 'pendulum':
                return [
                    { name: 'length', label: 'Length (px)', value: userParams.length, min: 50, max: 400, step: 10 },
                    { name: 'mass', label: 'Mass', value: userParams.mass, min: 0.5, max: 3, step: 0.1 },
                    { name: 'gravity', label: 'Gravity', value: userParams.gravity, min: 0.1, max: 2, step: 0.1 },
                    { name: 'damping', label: 'Damping', value: userParams.damping, min: 0.95, max: 1, step: 0.005 },
                    { name: 'angle', label: 'Start Angle (°)', value: userParams.angle, min: 5, max: 85, step: 5 }
                ]
            case 'collision':
                return [
                    { name: 'ballCount', label: 'Ball Count', value: userParams.ballCount, min: 3, max: 15, step: 1 },
                    { name: 'restitution', label: 'Bounciness', value: userParams.restitution, min: 0.1, max: 1, step: 0.1 },
                    { name: 'friction', label: 'Friction', value: userParams.friction, min: 0, max: 0.5, step: 0.05 },
                    { name: 'airResistance', label: 'Air Resistance', value: userParams.airResistance, min: 0, max: 0.05, step: 0.005 }
                ]
            case 'spring':
                return [
                    { name: 'springConstant', label: 'Spring Constant', value: userParams.springConstant, min: 0.01, max: 0.1, step: 0.005 },
                    { name: 'springMass', label: 'Mass', value: userParams.springMass, min: 0.5, max: 3, step: 0.1 },
                    { name: 'damping', label: 'Damping', value: userParams.damping, min: 0.9, max: 1, step: 0.005 },
                    { name: 'initialDisplacement', label: 'Initial Displacement', value: userParams.initialDisplacement, min: 50, max: 200, step: 10 }
                ]
            case 'projectile':
                return [
                    { name: 'projectileAngle', label: 'Launch Angle (°)', value: userParams.projectileAngle, min: 15, max: 75, step: 5 },
                    { name: 'velocity', label: 'Initial Velocity', value: userParams.velocity, min: 5, max: 25, step: 1 },
                    { name: 'projectileGravity', label: 'Gravity', value: userParams.projectileGravity, min: 0.1, max: 1, step: 0.1 },
                    { name: 'projectileAirResistance', label: 'Air Resistance', value: userParams.projectileAirResistance, min: 0, max: 0.05, step: 0.005 },
                    { name: 'launchHeight', label: 'Launch Height', value: userParams.launchHeight, min: 100, max: 400, step: 25 }
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
                    background: #3b82f6;
                    cursor: pointer;
                }
                .slider::-moz-range-thumb {
                    height: 16px;
                    width: 16px;
                    border-radius: 50%;
                    background: #3b82f6;
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
                                className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full"
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
                            onClick={() => setShowTrails(!showTrails)}
                            className={`px-4 py-2 rounded text-sm font-medium ${showTrails
                                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                                : 'bg-gray-600 hover:bg-gray-700 text-white'
                                }`}
                        >
                            {showTrails ? '👁 Hide Trails' : '👁 Show Trails'}
                        </button>

                        {/* Spring Force Button - only show for spring simulation */}
                        {simulationType === 'spring' && (
                            <button
                                onClick={applySpringForce}
                                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded text-sm font-medium"
                            >
                                ⚡ Apply Force
                            </button>
                        )}

                        {/* Reset Trail Button - only show for projectile simulation */}
                        {simulationType === 'projectile' && (
                            <button
                                onClick={resetTrail}
                                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm font-medium"
                            >
                                🎯 Reset Trail
                            </button>
                        )}
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
                <div ref={sceneRef} className="w-full h-full bg-gray-900" />

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