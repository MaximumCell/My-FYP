'use client'

import React, { useEffect, useRef, useState } from 'react'
import { Engine, Render, Runner, Bodies, Composite, Constraint, Mouse, MouseConstraint, Body } from 'matter-js'

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
        // Pendulum parameters
        length: 200,
        mass: 10,
        gravity: 1,
        damping: 0.02,
        // Collision parameters
        ballCount: 5,
        ballRadius: 20,
        restitution: 0.8,
        // Spring parameters
        springStiffness: 0.02,
        springRestLength: 100,
        // Projectile parameters
        angle: 45,
        velocity: 15,
        targetDistance: 400
    })

    // Fetch simulation config
    useEffect(() => {
        const fetchConfig = async () => {
            try {
                setLoading(true)
                const response = await fetch(`http://localhost:5000/simulation/api/simulation/matter`, {
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

        // Create anchor
        const anchor = Bodies.circle(spring.anchorX, spring.anchorY, 5, {
            isStatic: true,
            render: { fillStyle: '#ffffff' }
        })

        // Create mass
        const mass = Bodies.circle(
            massConfig.initialX,
            massConfig.initialY,
            massConfig.radius,
            {
                mass: massConfig.mass,
                render: { fillStyle: '#FF5722' },
                frictionAir: 1 - spring.damping
            }
        )

        // Create spring constraint
        const springConstraint = Constraint.create({
            bodyA: anchor,
            bodyB: mass,
            length: spring.restLength,
            stiffness: spring.stiffness,
            damping: spring.damping,
            render: {
                type: 'line',
                strokeStyle: '#4CAF50',
                lineWidth: 3
            }
        })

        Composite.add(engine.world, [anchor, mass, springConstraint])
    }

    const createProjectileSimulation = (engine: Engine, config: any) => {
        const { projectile, world, target } = config

        // Create ground
        const ground = Bodies.rectangle(
            400, 550, 800, 50,
            { isStatic: true, render: { fillStyle: '#8BC34A' } }
        )

        // Create launcher
        const launcher = Bodies.rectangle(
            projectile.launchX, projectile.launchY, 30, 10,
            { isStatic: true, render: { fillStyle: '#FFC107' } }
        )

        // Create target
        const targetBody = Bodies.circle(target.x, target.y, target.radius, {
            isStatic: true,
            render: { fillStyle: '#F44336' }
        })

        // Create projectile
        const velocityX = projectile.velocity * Math.cos(projectile.angle)
        const velocityY = -projectile.velocity * Math.sin(projectile.angle)

        const projectileBody = Bodies.circle(
            projectile.launchX, projectile.launchY - 20, projectile.radius,
            {
                mass: projectile.mass,
                restitution: projectile.restitution,
                render: { fillStyle: '#2196F3' }
            }
        )

        // Set initial velocity
        engine.world.gravity.y = world.gravity
        Body.setVelocity(projectileBody, { x: velocityX, y: velocityY })

        Composite.add(engine.world, [ground, launcher, targetBody, projectileBody])
    }

    const togglePause = () => {
        if (!runnerRef.current) return

        if (isPaused) {
            Runner.start(runnerRef.current, engineRef.current!)
        } else {
            Runner.stop(runnerRef.current)
        }
        setIsPaused(!isPaused)
    }

    const resetSimulation = () => {
        // Trigger re-render by forcing config update
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
            case 'pendulum':
                return [
                    { name: 'length', label: 'Length (px)', value: userParams.length, min: 50, max: 400, step: 10 },
                    { name: 'mass', label: 'Mass', value: userParams.mass, min: 1, max: 50, step: 1 },
                    { name: 'gravity', label: 'Gravity', value: userParams.gravity, min: 0.1, max: 3, step: 0.1 },
                    { name: 'damping', label: 'Damping', value: userParams.damping, min: 0, max: 0.1, step: 0.005 }
                ]
            case 'collision':
                return [
                    { name: 'ballCount', label: 'Ball Count', value: userParams.ballCount, min: 2, max: 10, step: 1 },
                    { name: 'ballRadius', label: 'Ball Radius', value: userParams.ballRadius, min: 10, max: 50, step: 5 },
                    { name: 'restitution', label: 'Bounciness', value: userParams.restitution, min: 0, max: 1, step: 0.1 }
                ]
            case 'spring':
                return [
                    { name: 'springStiffness', label: 'Stiffness', value: userParams.springStiffness, min: 0.001, max: 0.1, step: 0.005 },
                    { name: 'springRestLength', label: 'Rest Length', value: userParams.springRestLength, min: 50, max: 200, step: 10 },
                    { name: 'mass', label: 'Mass', value: userParams.mass, min: 1, max: 50, step: 1 }
                ]
            case 'projectile':
                return [
                    { name: 'angle', label: 'Launch Angle (°)', value: userParams.angle, min: 0, max: 90, step: 5 },
                    { name: 'velocity', label: 'Initial Velocity', value: userParams.velocity, min: 5, max: 30, step: 1 },
                    { name: 'targetDistance', label: 'Target Distance', value: userParams.targetDistance, min: 200, max: 600, step: 50 }
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