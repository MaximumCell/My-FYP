import React, { useRef, useEffect, useState } from 'react'
import * as THREE from 'three'

// Orbit controls for smooth camera interaction
class OrbitControls {
    private camera: THREE.PerspectiveCamera
    private domElement: HTMLElement
    private enabled = true
    private target = new THREE.Vector3()
    private minDistance = 2
    private maxDistance = 20
    private minPolarAngle = 0
    private maxPolarAngle = Math.PI
    private minAzimuthAngle = -Infinity
    private maxAzimuthAngle = Infinity
    private enableDamping = true
    private dampingFactor = 0.05
    private enableZoom = true
    private zoomSpeed = 1.0
    private enableRotate = true
    private rotateSpeed = 1.0
    private enablePan = true
    private panSpeed = 1.0
    private autoRotate = false
    private autoRotateSpeed = 2.0

    private spherical = new THREE.Spherical()
    private sphericalDelta = new THREE.Spherical()
    private scale = 1
    private panOffset = new THREE.Vector3()
    private zoomChanged = false

    private rotateStart = new THREE.Vector2()
    private rotateEnd = new THREE.Vector2()
    private rotateDelta = new THREE.Vector2()

    private panStart = new THREE.Vector2()
    private panEnd = new THREE.Vector2()
    private panDelta = new THREE.Vector2()

    private dollyStart = new THREE.Vector2()
    private dollyEnd = new THREE.Vector2()
    private dollyDelta = new THREE.Vector2()

    private state = {
        NONE: -1,
        ROTATE: 0,
        DOLLY: 1,
        PAN: 2,
        TOUCH_ROTATE: 3,
        TOUCH_PAN: 4,
        TOUCH_DOLLY_PAN: 5,
        TOUCH_DOLLY_ROTATE: 6
    }
    private currentState = this.state.NONE

    constructor(camera: THREE.PerspectiveCamera, domElement: HTMLElement) {
        this.camera = camera
        this.domElement = domElement
        this.domElement.style.touchAction = 'none'

        this.addEventListeners()
        this.update()
    }

    private addEventListeners() {
        this.domElement.addEventListener('contextmenu', this.onContextMenu.bind(this))
        this.domElement.addEventListener('pointerdown', this.onPointerDown.bind(this))
        this.domElement.addEventListener('pointercancel', this.onPointerUp.bind(this))
        this.domElement.addEventListener('wheel', this.onMouseWheel.bind(this))
    }

    private onContextMenu(event: Event) {
        if (!this.enabled) return
        event.preventDefault()
    }

    private onPointerDown(event: PointerEvent) {
        if (!this.enabled) return

        if (event.pointerType === 'touch') {
            this.onTouchStart(event)
        } else {
            this.onMouseDown(event)
        }
    }

    private onPointerUp(event: PointerEvent) {
        if (!this.enabled) return

        if (event.pointerType === 'touch') {
            this.onTouchEnd()
        } else {
            this.onMouseUp()
        }
    }

    private onMouseDown(event: MouseEvent) {
        if (event.button === 0) {
            this.currentState = this.state.ROTATE
            this.rotateStart.set(event.clientX, event.clientY)
        } else if (event.button === 1) {
            this.currentState = this.state.DOLLY
            this.dollyStart.set(event.clientX, event.clientY)
        } else if (event.button === 2) {
            this.currentState = this.state.PAN
            this.panStart.set(event.clientX, event.clientY)
        }

        this.domElement.addEventListener('pointermove', this.onPointerMove.bind(this))
        this.domElement.addEventListener('pointerup', this.onPointerUp.bind(this))
    }

    private onMouseUp() {
        this.domElement.removeEventListener('pointermove', this.onPointerMove.bind(this))
        this.domElement.removeEventListener('pointerup', this.onPointerUp.bind(this))
        this.currentState = this.state.NONE
    }

    private onPointerMove(event: PointerEvent) {
        if (!this.enabled) return

        if (event.pointerType === 'touch') {
            this.onTouchMove(event)
        } else {
            this.onMouseMove(event)
        }
    }

    private onMouseMove(event: MouseEvent) {
        if (this.currentState === this.state.ROTATE) {
            this.rotateEnd.set(event.clientX, event.clientY)
            this.rotateDelta.subVectors(this.rotateEnd, this.rotateStart).multiplyScalar(this.rotateSpeed)

            const element = this.domElement
            this.rotateLeft(2 * Math.PI * this.rotateDelta.x / element.clientHeight)
            this.rotateUp(2 * Math.PI * this.rotateDelta.y / element.clientHeight)

            this.rotateStart.copy(this.rotateEnd)
            this.update()
        }
    }

    private onMouseWheel(event: WheelEvent) {
        if (!this.enabled || !this.enableZoom) return

        event.preventDefault()

        if (event.deltaY < 0) {
            this.dollyOut(this.getZoomScale())
        } else if (event.deltaY > 0) {
            this.dollyIn(this.getZoomScale())
        }

        this.update()
    }

    private onTouchStart(event: PointerEvent) {
        // Touch handling implementation
    }

    private onTouchEnd() {
        // Touch end implementation
    }

    private onTouchMove(event: PointerEvent) {
        // Touch move implementation
    }

    private rotateLeft(angle: number) {
        this.sphericalDelta.theta -= angle
    }

    private rotateUp(angle: number) {
        this.sphericalDelta.phi -= angle
    }

    private dollyOut(dollyScale: number) {
        this.scale /= dollyScale
    }

    private dollyIn(dollyScale: number) {
        this.scale *= dollyScale
    }

    private getZoomScale() {
        return Math.pow(0.95, this.zoomSpeed)
    }

    update() {
        const offset = new THREE.Vector3()
        const quat = new THREE.Quaternion().setFromUnitVectors(this.camera.up, new THREE.Vector3(0, 1, 0))
        const quatInverse = quat.clone().invert()

        const lastPosition = new THREE.Vector3()
        const lastQuaternion = new THREE.Quaternion()

        const twoPI = 2 * Math.PI

        return () => {
            const position = this.camera.position

            offset.copy(position).sub(this.target)
            offset.applyQuaternion(quat)

            this.spherical.setFromVector3(offset)

            if (this.autoRotate && this.currentState === this.state.NONE) {
                this.rotateLeft(this.getAutoRotationAngle())
            }

            if (this.enableDamping) {
                this.spherical.theta += this.sphericalDelta.theta * this.dampingFactor
                this.spherical.phi += this.sphericalDelta.phi * this.dampingFactor
            } else {
                this.spherical.theta += this.sphericalDelta.theta
                this.spherical.phi += this.sphericalDelta.phi
            }

            this.spherical.theta = Math.max(this.minAzimuthAngle, Math.min(this.maxAzimuthAngle, this.spherical.theta))
            this.spherical.phi = Math.max(this.minPolarAngle, Math.min(this.maxPolarAngle, this.spherical.phi))
            this.spherical.makeSafe()

            this.spherical.radius *= this.scale

            this.spherical.radius = Math.max(this.minDistance, Math.min(this.maxDistance, this.spherical.radius))

            this.target.add(this.panOffset)

            offset.setFromSpherical(this.spherical)
            offset.applyQuaternion(quatInverse)

            position.copy(this.target).add(offset)

            this.camera.lookAt(this.target)

            if (this.enableDamping === true) {
                this.sphericalDelta.theta *= (1 - this.dampingFactor)
                this.sphericalDelta.phi *= (1 - this.dampingFactor)
            } else {
                this.sphericalDelta.set(0, 0, 0)
            }

            this.scale = 1
            this.panOffset.set(0, 0, 0)

            if (this.zoomChanged ||
                lastPosition.distanceToSquared(this.camera.position) > 1e-6 ||
                8 * (1 - lastQuaternion.dot(this.camera.quaternion)) > 1e-6) {

                lastPosition.copy(this.camera.position)
                lastQuaternion.copy(this.camera.quaternion)
                this.zoomChanged = false

                return true
            }

            return false
        }
    }

    private getAutoRotationAngle() {
        return 2 * Math.PI / 60 / 60 * this.autoRotateSpeed
    }

    setAutoRotate(value: boolean) {
        this.autoRotate = value
    }

    dispose() {
        this.domElement.removeEventListener('contextmenu', this.onContextMenu.bind(this))
        this.domElement.removeEventListener('pointerdown', this.onPointerDown.bind(this))
        this.domElement.removeEventListener('pointercancel', this.onPointerUp.bind(this))
        this.domElement.removeEventListener('wheel', this.onMouseWheel.bind(this))
    }
}

interface ThreeEMWaveProps {
    config: {
        wave: {
            frequency: number
            amplitude: number
            wavelength: number
        }
        fields: {
            showElectric: boolean
            showMagnetic: boolean
            showPoynting: boolean
        }
        display: {
            width: number
            height: number
        }
    }
    isPaused: boolean
}

const ThreeEMWave: React.FC<ThreeEMWaveProps> = ({ config, isPaused }) => {
    const mountRef = useRef<HTMLDivElement>(null)
    const sceneRef = useRef<THREE.Scene>()
    const rendererRef = useRef<THREE.WebGLRenderer>()
    const cameraRef = useRef<THREE.PerspectiveCamera>()
    const timeRef = useRef(0)
    const animationRef = useRef<number>()

    // Wave components
    const electricFieldRef = useRef<THREE.Group>()
    const magneticFieldRef = useRef<THREE.Group>()
    const poyntingFieldRef = useRef<THREE.Group>()
    const axesRef = useRef<THREE.Group>()

    const [showVectors, setShowVectors] = useState(true)
    const [cameraControls, setCameraControls] = useState({
        autoRotate: true,
        angle: 0,
        distance: 8
    })

    useEffect(() => {
        if (!mountRef.current) return

        // Scene setup
        const scene = new THREE.Scene()
        scene.background = new THREE.Color(0x0a0f1a)
        sceneRef.current = scene

        // Camera setup
        const camera = new THREE.PerspectiveCamera(
            75,
            config.display.width / config.display.height,
            0.1,
            1000
        )
        camera.position.set(8, 3, 8)
        camera.lookAt(0, 0, 0)
        cameraRef.current = camera

        // Renderer setup
        const renderer = new THREE.WebGLRenderer({ antialias: true })
        renderer.setSize(config.display.width, config.display.height)
        renderer.setClearColor(0x0a0f1a)
        mountRef.current.appendChild(renderer.domElement)
        rendererRef.current = renderer

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
        scene.add(ambientLight)

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
        directionalLight.position.set(10, 10, 5)
        scene.add(directionalLight)

        // Create coordinate axes
        const axesGroup = new THREE.Group()

        // X-axis (propagation) - Red
        const xGeometry = new THREE.CylinderGeometry(0.02, 0.02, 10, 8)
        const xMaterial = new THREE.MeshPhongMaterial({ color: 0xff6666 })
        const xAxis = new THREE.Mesh(xGeometry, xMaterial)
        xAxis.rotation.z = Math.PI / 2
        axesGroup.add(xAxis)

        // X-axis arrow
        const xArrowGeometry = new THREE.ConeGeometry(0.1, 0.3, 8)
        const xArrow = new THREE.Mesh(xArrowGeometry, xMaterial)
        xArrow.position.set(5.15, 0, 0)
        xArrow.rotation.z = -Math.PI / 2
        axesGroup.add(xArrow)

        // Y-axis (electric field) - Green
        const yGeometry = new THREE.CylinderGeometry(0.02, 0.02, 8, 8)
        const yMaterial = new THREE.MeshPhongMaterial({ color: 0x66ff66 })
        const yAxis = new THREE.Mesh(yGeometry, yMaterial)
        axesGroup.add(yAxis)

        // Y-axis arrow
        const yArrow = new THREE.Mesh(xArrowGeometry, yMaterial)
        yArrow.position.set(0, 4.15, 0)
        axesGroup.add(yArrow)

        // Z-axis (magnetic field) - Blue
        const zGeometry = new THREE.CylinderGeometry(0.02, 0.02, 8, 8)
        const zMaterial = new THREE.MeshPhongMaterial({ color: 0x6666ff })
        const zAxis = new THREE.Mesh(zGeometry, zMaterial)
        zAxis.rotation.x = Math.PI / 2
        axesGroup.add(zAxis)

        // Z-axis arrow
        const zArrow = new THREE.Mesh(xArrowGeometry, zMaterial)
        zArrow.position.set(0, 0, 4.15)
        zArrow.rotation.x = -Math.PI / 2
        axesGroup.add(zArrow)

        scene.add(axesGroup)
        axesRef.current = axesGroup

        // Create field groups
        const electricGroup = new THREE.Group()
        const magneticGroup = new THREE.Group()
        const poyntingGroup = new THREE.Group()

        scene.add(electricGroup)
        scene.add(magneticGroup)
        scene.add(poyntingGroup)

        electricFieldRef.current = electricGroup
        magneticFieldRef.current = magneticGroup
        poyntingFieldRef.current = poyntingGroup

        // Create wave vectors
        createWaveVectors()

        // Mouse controls
        let mouseDown = false
        let mouseX = 0
        let mouseY = 0

        const handleMouseDown = (event: MouseEvent) => {
            mouseDown = true
            mouseX = event.clientX
            mouseY = event.clientY
            setCameraControls(prev => ({ ...prev, autoRotate: false }))
        }

        const handleMouseMove = (event: MouseEvent) => {
            if (!mouseDown) return

            const deltaX = event.clientX - mouseX
            const deltaY = event.clientY - mouseY

            setCameraControls(prev => ({
                ...prev,
                angle: prev.angle + deltaX * 0.01,
                distance: Math.max(3, Math.min(15, prev.distance + deltaY * 0.01))
            }))

            mouseX = event.clientX
            mouseY = event.clientY
        }

        const handleMouseUp = () => {
            mouseDown = false
        }

        const handleWheel = (event: WheelEvent) => {
            setCameraControls(prev => ({
                ...prev,
                distance: Math.max(3, Math.min(15, prev.distance + event.deltaY * 0.01))
            }))
        }

        renderer.domElement.addEventListener('mousedown', handleMouseDown)
        renderer.domElement.addEventListener('mousemove', handleMouseMove)
        renderer.domElement.addEventListener('mouseup', handleMouseUp)
        renderer.domElement.addEventListener('wheel', handleWheel)

        // Keyboard controls
        const handleKeyPress = (event: KeyboardEvent) => {
            switch (event.key.toLowerCase()) {
                case 'v':
                    setShowVectors(prev => !prev)
                    break
                case 'r':
                    setCameraControls(prev => ({ ...prev, autoRotate: !prev.autoRotate }))
                    break
                case ' ':
                    event.preventDefault()
                    // Toggle pause would be handled by parent component
                    break
            }
        }

        window.addEventListener('keydown', handleKeyPress)

        // Animation loop
        const animate = () => {
            if (!isPaused) {
                timeRef.current += 0.03
            }

            // Update camera
            if (cameraControls.autoRotate) {
                setCameraControls(prev => ({ ...prev, angle: prev.angle + 0.01 }))
            }

            if (cameraRef.current) {
                cameraRef.current.position.x = cameraControls.distance * Math.cos(cameraControls.angle)
                cameraRef.current.position.z = cameraControls.distance * Math.sin(cameraControls.angle)
                cameraRef.current.lookAt(0, 0, 0)
            }

            updateWave()

            if (rendererRef.current && sceneRef.current && cameraRef.current) {
                rendererRef.current.render(sceneRef.current, cameraRef.current)
            }

            animationRef.current = requestAnimationFrame(animate)
        }

        animate()

        // Cleanup
        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current)
            }

            renderer.domElement.removeEventListener('mousedown', handleMouseDown)
            renderer.domElement.removeEventListener('mousemove', handleMouseMove)
            renderer.domElement.removeEventListener('mouseup', handleMouseUp)
            renderer.domElement.removeEventListener('wheel', handleWheel)
            window.removeEventListener('keydown', handleKeyPress)

            if (mountRef.current && renderer.domElement) {
                mountRef.current.removeChild(renderer.domElement)
            }

            renderer.dispose()
        }
    }, [config])

    const createWaveVectors = () => {
        if (!electricFieldRef.current || !magneticFieldRef.current || !poyntingFieldRef.current) return

        // Clear existing vectors
        electricFieldRef.current.clear()
        magneticFieldRef.current.clear()
        poyntingFieldRef.current.clear()

        const numVectors = 40
        const waveLength = 8

        for (let i = 0; i < numVectors; i++) {
            const x = (i / (numVectors - 1)) * waveLength - waveLength / 2

            // Electric field vector (red, Y direction)
            if (config.fields.showElectric) {
                const eGroup = new THREE.Group()

                // Vector shaft
                const eGeometry = new THREE.CylinderGeometry(0.015, 0.015, 1, 8)
                const eMaterial = new THREE.MeshPhongMaterial({ color: 0xff4444 })
                const eVector = new THREE.Mesh(eGeometry, eMaterial)
                eGroup.add(eVector)

                // Vector arrowhead
                const eArrowGeometry = new THREE.ConeGeometry(0.05, 0.15, 8)
                const eArrow = new THREE.Mesh(eArrowGeometry, eMaterial)
                eArrow.position.y = 0.575
                eGroup.add(eArrow)

                eGroup.position.x = x
                electricFieldRef.current.add(eGroup)
            }

            // Magnetic field vector (green, Z direction)
            if (config.fields.showMagnetic) {
                const bGroup = new THREE.Group()

                // Vector shaft
                const bGeometry = new THREE.CylinderGeometry(0.015, 0.015, 1, 8)
                const bMaterial = new THREE.MeshPhongMaterial({ color: 0x44ff44 })
                const bVector = new THREE.Mesh(bGeometry, bMaterial)
                bVector.rotation.x = Math.PI / 2
                bGroup.add(bVector)

                // Vector arrowhead
                const bArrowGeometry = new THREE.ConeGeometry(0.05, 0.15, 8)
                const bArrow = new THREE.Mesh(bArrowGeometry, bMaterial)
                bArrow.position.z = 0.575
                bArrow.rotation.x = -Math.PI / 2
                bGroup.add(bArrow)

                bGroup.position.x = x
                magneticFieldRef.current.add(bGroup)
            }

            // Poynting vector (yellow, X direction)
            if (config.fields.showPoynting) {
                const sGroup = new THREE.Group()

                // Vector shaft
                const sGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.5, 8)
                const sMaterial = new THREE.MeshPhongMaterial({ color: 0xffff44 })
                const sVector = new THREE.Mesh(sGeometry, sMaterial)
                sVector.rotation.z = Math.PI / 2
                sGroup.add(sVector)

                // Vector arrowhead
                const sArrowGeometry = new THREE.ConeGeometry(0.06, 0.2, 8)
                const sArrow = new THREE.Mesh(sArrowGeometry, sMaterial)
                sArrow.position.x = 0.35
                sArrow.rotation.z = -Math.PI / 2
                sGroup.add(sArrow)

                sGroup.position.x = x
                poyntingFieldRef.current.add(sGroup)
            }
        }
    }

    const updateWave = () => {
        if (!electricFieldRef.current || !magneticFieldRef.current || !poyntingFieldRef.current) return

        const k = 2 * Math.PI / config.wave.wavelength
        const omega = 2 * Math.PI * config.wave.frequency
        const amplitude = config.wave.amplitude

        // Update electric field vectors
        if (config.fields.showElectric) {
            electricFieldRef.current.children.forEach((eGroup, index) => {
                const group = eGroup as THREE.Group
                const x = group.position.x
                const E_y = amplitude * Math.sin(k * x - omega * timeRef.current)

                group.scale.y = Math.abs(E_y) * 2 + 0.1
                group.position.y = E_y * 1.5

                // Update material opacity based on field strength
                const vector = group.children[0] as THREE.Mesh
                const arrow = group.children[1] as THREE.Mesh
                const material = vector.material as THREE.MeshPhongMaterial
                material.opacity = Math.abs(E_y) * 0.8 + 0.3
                    ; (arrow.material as THREE.MeshPhongMaterial).opacity = material.opacity
            })
        }

        // Update magnetic field vectors
        if (config.fields.showMagnetic) {
            magneticFieldRef.current.children.forEach((bGroup, index) => {
                const group = bGroup as THREE.Group
                const x = group.position.x
                const B_z = amplitude * Math.sin(k * x - omega * timeRef.current)

                group.scale.z = Math.abs(B_z) * 2 + 0.1
                group.position.z = B_z * 1.5

                // Update material opacity
                const vector = group.children[0] as THREE.Mesh
                const arrow = group.children[1] as THREE.Mesh
                const material = vector.material as THREE.MeshPhongMaterial
                material.opacity = Math.abs(B_z) * 0.8 + 0.3
                    ; (arrow.material as THREE.MeshPhongMaterial).opacity = material.opacity
            })
        }

        // Update Poynting vectors
        if (config.fields.showPoynting) {
            poyntingFieldRef.current.children.forEach((sGroup, index) => {
                const group = sGroup as THREE.Group
                const x = group.position.x
                const E_strength = amplitude * Math.sin(k * x - omega * timeRef.current)
                const B_strength = amplitude * Math.sin(k * x - omega * timeRef.current)
                const S_magnitude = Math.abs(E_strength * B_strength)

                group.scale.x = S_magnitude * 3 + 0.2
                group.visible = S_magnitude > 0.1

                // Update material opacity
                if (group.visible) {
                    const vector = group.children[0] as THREE.Mesh
                    const arrow = group.children[1] as THREE.Mesh
                    const material = vector.material as THREE.MeshPhongMaterial
                    material.opacity = S_magnitude * 0.9 + 0.4
                        ; (arrow.material as THREE.MeshPhongMaterial).opacity = material.opacity
                }
            })
        }
    }

    // Re-create vectors when config changes
    useEffect(() => {
        createWaveVectors()
    }, [config.fields])

    return (
        <div className="relative">
            <div ref={mountRef} className="border border-gray-300 rounded" />

            {/* Control panel */}
            <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white p-3 rounded text-sm">
                <h3 className="font-bold text-yellow-300 mb-2">3D EM Wave</h3>
                <div className="space-y-1">
                    <div>Frequency: {config.wave.frequency.toFixed(2)} Hz</div>
                    <div>Wavelength: {config.wave.wavelength.toFixed(1)} units</div>
                    <div>Amplitude: {config.wave.amplitude.toFixed(2)}</div>
                </div>

                <div className="mt-3 text-xs text-gray-300">
                    <div><strong>Mouse:</strong> Drag to rotate, Scroll to zoom</div>
                    <div><strong>V:</strong> Toggle vectors | <strong>R:</strong> Auto-rotate</div>
                    <div><strong>Red:</strong> E-field | <strong>Green:</strong> B-field | <strong>Yellow:</strong> Energy</div>
                </div>
            </div>
        </div>
    )
}

export default ThreeEMWave