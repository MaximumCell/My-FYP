import React, { useRef, useEffect, useState } from 'react'
import * as THREE from 'three'

interface Props {
    parameters: {
        amplitude: number
        frequency: number
        wavelength: number
        speed: number
        direction: string
        phase?: number
        polarization?: string
        showElectric?: boolean
        showMagnetic?: boolean
        showPoynting?: boolean
    }
}

const ThreeEMWaveInteractive: React.FC<Props> = ({ parameters }) => {
    const mountRef = useRef<HTMLDivElement>(null)
    const sceneRef = useRef<THREE.Scene>()
    const rendererRef = useRef<THREE.WebGLRenderer>()
    const cameraRef = useRef<THREE.PerspectiveCamera>()
    const animationIdRef = useRef<number>()

    // Camera control state using refs to avoid stale closures
    const isMouseDownRef = useRef(false)
    const isDoubleClickRef = useRef(false)
    const mousePositionRef = useRef({ x: 0, y: 0 })
    const cameraPositionRef = useRef({
        radius: 12,
        theta: Math.PI / 4,
        phi: Math.PI / 3
    })

    // State for UI updates
    const [uiCameraPosition, setUiCameraPosition] = useState(cameraPositionRef.current)
    const [isInteracting, setIsInteracting] = useState(false)

    // Field visualization refs
    const electricFieldRef = useRef<THREE.Group>()
    const magneticFieldRef = useRef<THREE.Group>()
    const energyFlowRef = useRef<THREE.Group>()
    const waveParticlesRef = useRef<THREE.Points>()

    useEffect(() => {
        if (!mountRef.current) return

        // Scene setup with dark space theme
        const scene = new THREE.Scene()
        scene.background = new THREE.Color(0x000011)
        scene.fog = new THREE.Fog(0x000011, 15, 50)
        sceneRef.current = scene

        // Get the container size dynamically
        const containerWidth = mountRef.current.clientWidth || 800
        const containerHeight = mountRef.current.clientHeight || 600

        // Camera setup
        const camera = new THREE.PerspectiveCamera(75, containerWidth / containerHeight, 0.1, 100)
        cameraRef.current = camera

        // Renderer setup with enhanced quality
        const renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: "high-performance"
        })

        renderer.setSize(containerWidth, containerHeight)
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
        renderer.shadowMap.enabled = true
        renderer.shadowMap.type = THREE.PCFSoftShadowMap
        renderer.outputColorSpace = THREE.SRGBColorSpace

        // Ensure canvas takes full container space and is interactive
        renderer.domElement.style.width = '100%'
        renderer.domElement.style.height = '100%'
        renderer.domElement.style.display = 'block'
        renderer.domElement.style.position = 'absolute'
        renderer.domElement.style.top = '0'
        renderer.domElement.style.left = '0'
        renderer.domElement.style.cursor = 'grab'
        renderer.domElement.style.userSelect = 'none'
        renderer.domElement.style.touchAction = 'none'

        rendererRef.current = renderer
        mountRef.current.appendChild(renderer.domElement)

        console.log('Three.js scene initialized')

        // Dramatic lighting setup
        const ambientLight = new THREE.AmbientLight(0x1a1a2e, 0.3)
        scene.add(ambientLight)

        const keyLight = new THREE.DirectionalLight(0x4a9eff, 1.5)
        keyLight.position.set(10, 10, 5)
        keyLight.castShadow = true
        scene.add(keyLight)

        const fillLight = new THREE.DirectionalLight(0xff4a9e, 0.8)
        fillLight.position.set(-10, -5, -10)
        scene.add(fillLight)

        const rimLight = new THREE.DirectionalLight(0x9eff4a, 0.6)
        rimLight.position.set(0, 15, 0)
        scene.add(rimLight)

        // Create enhanced coordinate system
        createCoordinateSystem(scene)

        // Initialize field groups
        electricFieldRef.current = new THREE.Group()
        magneticFieldRef.current = new THREE.Group()
        energyFlowRef.current = new THREE.Group()

        scene.add(electricFieldRef.current)
        scene.add(magneticFieldRef.current)
        scene.add(energyFlowRef.current)

        // Create the electromagnetic field visualization
        createInteractiveEMField()

        // Mouse interaction state
        let isDragging = false
        let previousMousePosition = { x: 0, y: 0 }
        let doubleClickActive = false

        // Mouse event handlers for interactive camera control
        const handleMouseDown = (event: MouseEvent) => {
            event.preventDefault()
            event.stopPropagation()
            isDragging = true
            previousMousePosition = { x: event.clientX, y: event.clientY }
            isMouseDownRef.current = true
            mousePositionRef.current = { x: event.clientX, y: event.clientY }
            setIsInteracting(true)

            // Visual feedback
            renderer.domElement.style.cursor = 'grabbing'
            console.log('Mouse down detected')

            // Check for double click
            if (event.detail === 2) {
                doubleClickActive = true
                isDoubleClickRef.current = true
                console.log('Double-click mode activated')
            }
        }

        const handleMouseMove = (event: MouseEvent) => {
            if (!isDragging) return

            event.preventDefault()
            event.stopPropagation()

            const deltaX = event.clientX - previousMousePosition.x
            const deltaY = event.clientY - previousMousePosition.y

            console.log('Mouse move delta:', deltaX, deltaY)

            // Update camera position ref
            cameraPositionRef.current = {
                radius: cameraPositionRef.current.radius,
                theta: cameraPositionRef.current.theta - deltaX * 0.01,
                phi: Math.max(0.1, Math.min(Math.PI - 0.1, cameraPositionRef.current.phi + deltaY * 0.01))
            }

            // Update UI state
            setUiCameraPosition({ ...cameraPositionRef.current })

            previousMousePosition = { x: event.clientX, y: event.clientY }
            mousePositionRef.current = { x: event.clientX, y: event.clientY }
        }

        const handleMouseUp = (event: MouseEvent) => {
            event.preventDefault()
            isDragging = false
            isMouseDownRef.current = false
            setIsInteracting(false)

            // Visual feedback
            renderer.domElement.style.cursor = 'grab'
            console.log('Mouse up detected')

            // Keep double-click active for continuous rotation
            setTimeout(() => {
                doubleClickActive = false
                isDoubleClickRef.current = false
            }, 100)
        }

        const handleWheel = (event: WheelEvent) => {
            event.preventDefault()
            cameraPositionRef.current = {
                ...cameraPositionRef.current,
                radius: Math.max(5, Math.min(25, cameraPositionRef.current.radius + event.deltaY * 0.02))
            }
            setUiCameraPosition({ ...cameraPositionRef.current })
        }

        // Add event listeners to both canvas and container
        const canvas = renderer.domElement
        const container = mountRef.current

        canvas.addEventListener('mousedown', handleMouseDown, { passive: false })
        canvas.addEventListener('mousemove', handleMouseMove, { passive: false })
        canvas.addEventListener('mouseup', handleMouseUp, { passive: false })
        canvas.addEventListener('wheel', handleWheel, { passive: false })

        container.addEventListener('mousedown', handleMouseDown, { passive: false })
        container.addEventListener('mousemove', handleMouseMove, { passive: false })
        container.addEventListener('mouseup', handleMouseUp, { passive: false })
        container.addEventListener('wheel', handleWheel, { passive: false })

        // Global mouse up to handle mouse leaving the area
        document.addEventListener('mouseup', handleMouseUp)

        // Animation loop
        const animate = () => {
            animationIdRef.current = requestAnimationFrame(animate)

            // Update camera position smoothly
            const { radius, theta, phi } = cameraPositionRef.current
            camera.position.setFromSphericalCoords(radius, phi, theta)
            camera.lookAt(0, 0, 0)

            // Animate electromagnetic field
            animateEMField()

            renderer.render(scene, camera)
        }
        animate()

        // Cleanup
        return () => {
            if (animationIdRef.current) {
                cancelAnimationFrame(animationIdRef.current)
            }

            // Remove event listeners from canvas
            const canvas = renderer.domElement
            canvas.removeEventListener('mousedown', handleMouseDown)
            canvas.removeEventListener('mousemove', handleMouseMove)
            canvas.removeEventListener('mouseup', handleMouseUp)
            canvas.removeEventListener('wheel', handleWheel)

            // Remove event listeners from container
            if (container) {
                container.removeEventListener('mousedown', handleMouseDown)
                container.removeEventListener('mousemove', handleMouseMove)
                container.removeEventListener('mouseup', handleMouseUp)
                container.removeEventListener('wheel', handleWheel)
            }

            // Remove global event listener
            document.removeEventListener('mouseup', handleMouseUp)

            if (mountRef.current && renderer.domElement) {
                mountRef.current.removeChild(renderer.domElement)
            }
            renderer.dispose()
        }
    }, []) // Remove dependencies to prevent recreation

    // Separate useEffect for camera updates
    useEffect(() => {
        // Camera updates are handled in the animation loop
    }, [uiCameraPosition])

    // Update field when parameters change
    useEffect(() => {
        if (electricFieldRef.current && magneticFieldRef.current && energyFlowRef.current) {
            createInteractiveEMField()
        }
    }, [parameters])

    const createCoordinateSystem = (scene: THREE.Scene) => {
        // Glowing coordinate axes
        const axesHelper = new THREE.AxesHelper(8)
        scene.add(axesHelper)

        // Create glowing grid
        const gridMaterial = new THREE.LineBasicMaterial({
            color: 0x333366,
            transparent: true,
            opacity: 0.4
        })

        const gridGeometry = new THREE.BufferGeometry()
        const gridPoints = []

        // Grid lines
        for (let i = -10; i <= 10; i++) {
            gridPoints.push(new THREE.Vector3(i, 0, -10))
            gridPoints.push(new THREE.Vector3(i, 0, 10))
            gridPoints.push(new THREE.Vector3(-10, 0, i))
            gridPoints.push(new THREE.Vector3(10, 0, i))
        }

        gridGeometry.setFromPoints(gridPoints)
        const grid = new THREE.LineSegments(gridGeometry, gridMaterial)
        scene.add(grid)

        // Propagation direction indicator
        const propagationGeometry = new THREE.ConeGeometry(0.2, 1, 8)
        const propagationMaterial = new THREE.MeshPhongMaterial({
            color: 0xffff00,
            transparent: true,
            opacity: 0.8,
            emissive: 0x444400
        })
        const propagationCone = new THREE.Mesh(propagationGeometry, propagationMaterial)
        propagationCone.position.set(0, 0, -6)
        propagationCone.rotation.x = Math.PI / 2
        scene.add(propagationCone)
    }

    const createInteractiveEMField = () => {
        if (!electricFieldRef.current || !magneticFieldRef.current || !energyFlowRef.current) return

        // Clear existing fields
        electricFieldRef.current.clear()
        magneticFieldRef.current.clear()
        energyFlowRef.current.clear()

        const { amplitude, showElectric = true, showMagnetic = true, showPoynting = false } = parameters
        const numVectors = 40
        const spacing = 0.3

        // Create 3D electric field vectors with glow effect
        if (showElectric) {
            for (let i = 0; i < numVectors; i++) {
                const z = (i - numVectors / 2) * spacing

                // Multiple radial positions for true 3D visualization
                for (let j = 0; j < 8; j++) {
                    const angle = (j / 8) * Math.PI * 2
                    const radius = 0.2 + (j % 3) * 0.15
                    const x = Math.cos(angle) * radius
                    const y = Math.sin(angle) * radius

                    // Electric field vector (glowing red)
                    const eGeometry = new THREE.ConeGeometry(0.05, amplitude * 0.6, 6)
                    const eMaterial = new THREE.MeshPhongMaterial({
                        color: 0xff3366,
                        transparent: true,
                        opacity: 0.8,
                        emissive: 0x441122
                    })
                    const eVector = new THREE.Mesh(eGeometry, eMaterial)
                    eVector.position.set(x, y, z)
                    eVector.userData = { basePos: { x, y, z }, type: 'electric', phase: i }
                    electricFieldRef.current.add(eVector)

                    // Electric field stem
                    const eStemGeometry = new THREE.CylinderGeometry(0.01, 0.01, amplitude * 0.4)
                    const eStem = new THREE.Mesh(eStemGeometry, eMaterial)
                    eStem.position.set(x, y - amplitude * 0.2, z)
                    eStem.userData = { basePos: { x, y, z }, type: 'electricStem', phase: i }
                    electricFieldRef.current.add(eStem)
                }
            }
        }

        // Create 3D magnetic field vectors with glow effect
        if (showMagnetic) {
            for (let i = 0; i < numVectors; i++) {
                const z = (i - numVectors / 2) * spacing

                // Multiple radial positions for true 3D visualization
                for (let j = 0; j < 8; j++) {
                    const angle = (j / 8) * Math.PI * 2
                    const radius = 0.2 + (j % 3) * 0.15
                    const x = Math.cos(angle) * radius
                    const y = Math.sin(angle) * radius

                    // Magnetic field vector (glowing blue)
                    const bGeometry = new THREE.ConeGeometry(0.05, amplitude * 0.6, 6)
                    const bMaterial = new THREE.MeshPhongMaterial({
                        color: 0x3366ff,
                        transparent: true,
                        opacity: 0.8,
                        emissive: 0x112244
                    })
                    const bVector = new THREE.Mesh(bGeometry, bMaterial)
                    bVector.position.set(x, y, z)
                    bVector.rotation.z = Math.PI / 2
                    bVector.userData = { basePos: { x, y, z }, type: 'magnetic', phase: i }
                    magneticFieldRef.current.add(bVector)

                    // Magnetic field stem
                    const bStemGeometry = new THREE.CylinderGeometry(0.01, 0.01, amplitude * 0.4)
                    const bStem = new THREE.Mesh(bStemGeometry, bMaterial)
                    bStem.position.set(x - amplitude * 0.2, y, z)
                    bStem.rotation.z = Math.PI / 2
                    bStem.userData = { basePos: { x, y, z }, type: 'magneticStem', phase: i }
                    magneticFieldRef.current.add(bStem)
                }
            }
        }

        // Create energy flow visualization (Poynting vector)
        for (let i = 0; i < 30; i++) {
            const angle = (i / 30) * Math.PI * 2
            const radius = 1 + Math.random() * 2

            const energyGeometry = new THREE.SphereGeometry(0.02, 8, 6)
            const energyMaterial = new THREE.MeshPhongMaterial({
                color: 0xffaa00,
                transparent: true,
                opacity: 0.7,
                emissive: 0x442200
            })
            const energyParticle = new THREE.Mesh(energyGeometry, energyMaterial)

            energyParticle.position.set(
                Math.cos(angle) * radius,
                Math.sin(angle) * radius,
                -6 + Math.random() * 12
            )
            energyParticle.userData = {
                baseAngle: angle,
                baseRadius: radius,
                speed: 0.1 + Math.random() * 0.05
            }
            energyFlowRef.current.add(energyParticle)
        }

        // Create wave surface particles
        const particleCount = 2000
        const particleGeometry = new THREE.BufferGeometry()
        const positions = new Float32Array(particleCount * 3)
        const colors = new Float32Array(particleCount * 3)

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 15
            positions[i * 3 + 1] = (Math.random() - 0.5) * 15
            positions[i * 3 + 2] = (Math.random() - 0.5) * 15

            const color = new THREE.Color()
            color.setHSL(0.7 + Math.random() * 0.3, 0.8, 0.5)
            colors[i * 3] = color.r
            colors[i * 3 + 1] = color.g
            colors[i * 3 + 2] = color.b
        }

        particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
        particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

        const particleMaterial = new THREE.PointsMaterial({
            size: 0.05,
            transparent: true,
            opacity: 0.6,
            vertexColors: true,
            blending: THREE.AdditiveBlending
        })

        waveParticlesRef.current = new THREE.Points(particleGeometry, particleMaterial)
        sceneRef.current?.add(waveParticlesRef.current)
    }

    const animateEMField = () => {
        if (!electricFieldRef.current || !magneticFieldRef.current || !energyFlowRef.current) return

        const time = Date.now() * 0.001
        const { amplitude, frequency, wavelength, phase = 0, showElectric = true, showMagnetic = true, showPoynting = false } = parameters
        const k = 2 * Math.PI / wavelength
        const omega = 2 * Math.PI * frequency
        const phaseShift = (phase || 0) * Math.PI / 180



        // Animate electric field vectors (only if showElectric is true)
        if (showElectric) {
            electricFieldRef.current.children.forEach((child) => {
                if (child.userData && child.userData.type === 'electric') {
                    const { basePos, phase } = child.userData
                    const fieldPhase = k * basePos.z - omega * time + phaseShift
                    const fieldStrength = amplitude * Math.sin(fieldPhase)

                    child.scale.y = Math.abs(fieldStrength) + 0.2
                    child.position.y = basePos.y + fieldStrength * 0.8

                    // Dynamic color intensity
                    const material = (child as THREE.Mesh).material as THREE.MeshPhongMaterial
                    const intensity = Math.abs(fieldStrength) / amplitude
                    material.emissive.setRGB(0.4 * intensity, 0.1 * intensity, 0.2 * intensity)
                }

                if (child.userData && child.userData.type === 'electricStem') {
                    const { basePos, phase } = child.userData
                    const fieldPhase = k * basePos.z - omega * time + phaseShift
                    const fieldStrength = amplitude * Math.sin(fieldPhase)

                    child.scale.y = Math.abs(fieldStrength) + 0.2
                    child.position.y = basePos.y + fieldStrength * 0.4
                }
            })
        }

        // Animate magnetic field vectors (only if showMagnetic is true)
        if (showMagnetic) {
            magneticFieldRef.current.children.forEach((child) => {
                if (child.userData && child.userData.type === 'magnetic') {
                    const { basePos, phase } = child.userData
                    const fieldPhase = k * basePos.z - omega * time + phaseShift + Math.PI / 2 // 90° phase shift
                    const fieldStrength = amplitude * Math.sin(fieldPhase)

                    child.scale.y = Math.abs(fieldStrength) + 0.2
                    child.position.x = basePos.x + fieldStrength * 0.8

                    const material = (child as THREE.Mesh).material as THREE.MeshPhongMaterial
                    const intensity = Math.abs(fieldStrength) / amplitude
                    material.emissive.setRGB(0.1 * intensity, 0.2 * intensity, 0.4 * intensity)
                }

                if (child.userData && child.userData.type === 'magneticStem') {
                    const { basePos, phase } = child.userData
                    const fieldPhase = k * basePos.z - omega * time + phaseShift + Math.PI / 2
                    const fieldStrength = amplitude * Math.sin(fieldPhase)

                    child.scale.y = Math.abs(fieldStrength) + 0.2
                    child.position.x = basePos.x + fieldStrength * 0.4
                }
            })
        }

        // Animate energy flow particles
        energyFlowRef.current.children.forEach((particle) => {
            if (particle.userData) {
                const { baseAngle, baseRadius, speed } = particle.userData
                particle.position.z += speed

                if (particle.position.z > 6) {
                    particle.position.z = -6
                }

                // Pulsing effect
                const pulse = Math.sin(time * 3 + baseAngle) * 0.3 + 0.7
                particle.scale.setScalar(pulse)
            }
        })

        // Animate wave particles
        if (waveParticlesRef.current) {
            const positions = waveParticlesRef.current.geometry.attributes.position
            for (let i = 0; i < positions.count; i++) {
                const x = positions.getX(i)
                const z = positions.getZ(i)
                const distance = Math.sqrt(x * x + z * z)
                const wave = Math.sin(distance * 0.5 - time * 2) * 0.5
                positions.setY(i, wave)
            }
            positions.needsUpdate = true
        }
    }

    return (
        <div className="w-full h-full relative overflow-hidden">
            <div
                ref={mountRef}
                className="w-full h-full cursor-grab active:cursor-grabbing"
                style={{ position: 'absolute', top: 0, left: 0, zIndex: 1 }}
            />

            {/* Enhanced control panel */}
            <div className="absolute top-4 left-4 bg-gradient-to-br from-purple-900/90 to-blue-900/90 backdrop-blur-sm text-white p-4 rounded-xl shadow-2xl border border-purple-500/30" style={{ zIndex: 10 }}>
                <div className="mb-3 font-bold text-xl text-cyan-300 flex items-center">
                    <div className="w-3 h-3 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
                    3D Electromagnetic Wave
                </div>
                <div className="space-y-2 text-sm">
                    <div className="flex items-center">
                        <div className="w-4 h-2 bg-gradient-to-r from-red-500 to-pink-500 rounded mr-3"></div>
                        <span>Electric Field (E)</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-4 h-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded mr-3"></div>
                        <span>Magnetic Field (B)</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-4 h-2 bg-gradient-to-r from-yellow-500 to-orange-500 rounded mr-3"></div>
                        <span>Energy Flow (S)</span>
                    </div>
                </div>
                <div className="mt-4 text-xs text-cyan-200 space-y-1">
                    <div className="font-semibold">Interactive Controls:</div>
                    <div>• Click & Drag: Rotate view</div>
                    <div>• Double-click & Hold: Free rotation</div>
                    <div>• Mouse Wheel: Zoom in/out</div>
                    <div className={`${isDoubleClickRef.current ? 'text-yellow-300 font-bold' : ''}`}>
                        {isDoubleClickRef.current ? '🔥 Double-click mode active!' : ''}
                    </div>
                </div>
            </div>

            {/* Wave parameters */}
            <div className="absolute top-4 right-4 bg-gradient-to-br from-indigo-900/90 to-purple-900/90 backdrop-blur-sm text-white p-4 rounded-xl shadow-2xl border border-indigo-500/30" style={{ zIndex: 10 }}>
                <div className="font-bold mb-3 text-cyan-300 text-lg">Wave Parameters</div>
                <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                        <span>Amplitude:</span>
                        <span className="text-yellow-300 font-mono">{parameters.amplitude.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                        <span>Frequency:</span>
                        <span className="text-yellow-300 font-mono">{parameters.frequency.toFixed(1)} Hz</span>
                    </div>
                    <div className="flex justify-between">
                        <span>Wavelength:</span>
                        <span className="text-yellow-300 font-mono">{parameters.wavelength.toFixed(1)} m</span>
                    </div>
                    <div className="flex justify-between">
                        <span>Speed:</span>
                        <span className="text-yellow-300 font-mono">{parameters.speed.toFixed(0)} m/s</span>
                    </div>
                </div>
            </div>

            {/* Physics info */}
            <div className="absolute bottom-4 left-4 bg-gradient-to-br from-gray-900/90 to-black/90 backdrop-blur-sm text-white p-4 rounded-xl shadow-2xl border border-gray-500/30 max-w-sm" style={{ zIndex: 10 }}>
                <div className="text-cyan-300 font-bold mb-2 text-sm">Electromagnetic Wave Physics:</div>
                <div className="text-xs space-y-1 text-gray-300">
                    <div>• <span className="text-red-400">E</span> ⊥ <span className="text-blue-400">B</span> ⊥ <span className="text-yellow-400">k</span> (mutually perpendicular)</div>
                    <div>• Energy density: u = ½(ε₀E² + B²/μ₀)</div>
                    <div>• Poynting vector: <span className="text-orange-400">S</span> = E × B/μ₀</div>
                    <div>• Wave equation: E = E₀ sin(kz - ωt)</div>
                    <div>• Speed: c = ω/k = 1/√(ε₀μ₀)</div>
                </div>
            </div>

            {/* Camera position indicator */}
            <div className="absolute bottom-4 right-4 bg-gradient-to-br from-green-900/90 to-teal-900/90 backdrop-blur-sm text-white p-3 rounded-xl shadow-2xl border border-green-500/30" style={{ zIndex: 10 }}>
                <div className="text-green-300 font-bold mb-2 text-sm">Camera View</div>
                <div className="text-xs space-y-1">
                    <div>Distance: {uiCameraPosition.radius.toFixed(1)}m</div>
                    <div>Angle θ: {(uiCameraPosition.theta * 180 / Math.PI).toFixed(0)}°</div>
                    <div>Angle φ: {(uiCameraPosition.phi * 180 / Math.PI).toFixed(0)}°</div>
                </div>
            </div>
        </div>
    )
}

export default ThreeEMWaveInteractive