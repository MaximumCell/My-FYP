// Interactive 3D Physics Simulation Engine for Education
console.log("Loading Interactive Physics Simulation Engine...");

// Global simulation state
let canvas;
let ctx;
let animationId;
let currentExperiment = "electric_field";
let simulationParams = {};
let isAnimating = true;

// Physics objects and state
let objects = [];
let particles = [];
let fieldLines = [];
let animationState = {
    pendulum: { angle: 0, velocity: 0, time: 0 },
    electricField: { charges: [], fieldVectors: [] },
    magneticField: { fieldVectors: [], particles: [] }
};

// Initialize the simulation with the existing HTML structure
function initializeSimulation(experimentType, params) {
    console.log("Initializing 3D Physics Simulation...", experimentType, params);
    
    currentExperiment = experimentType || "electric_field";
    simulationParams = params || {};
    
    // Find existing canvas or create one
    canvas = document.getElementById('simulation-canvas');
    if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'simulation-canvas';
        
        // Find the physics simulation container
        const container = document.getElementById('physics-simulation');
        if (container) {
            container.appendChild(canvas);
        } else {
            document.body.appendChild(canvas);
        }
    }
    
    // Set up canvas
    canvas.width = canvas.offsetWidth || 800;
    canvas.height = canvas.offsetHeight || 600;
    ctx = canvas.getContext('2d');
    
    // Set up responsive canvas
    function resizeCanvas() {
        const container = canvas.parentElement;
        if (container) {
            canvas.width = container.offsetWidth;
            canvas.height = container.offsetHeight;
        }
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    // Initialize experiment
    setupExperiment(currentExperiment);
    
    // Start animation loop
    startAnimation();
    
    console.log("Physics simulation initialized successfully");
}

// Set up specific experiment
function setupExperiment(experimentType) {
    // Clear previous objects
    objects = [];
    particles = [];
    fieldLines = [];
    
    switch(experimentType) {
        case 'electric_field':
        case 'electric':
            setupElectricField();
            break;
        case 'magnetic_field':
        case 'magnetic':
            setupMagneticField();
            break;
        case 'pendulum':
            setupPendulum();
            break;
        default:
            setupVectorField();
    }
}

// Electric field simulation
function setupElectricField() {
    const charge = simulationParams.charge_strength || 2.0;
    const gridSize = simulationParams.grid_size || 5;
    
    // Create central charge
    objects.push({
        type: 'charge',
        x: canvas.width / 2,
        y: canvas.height / 2,
        charge: charge,
        radius: 15,
        color: charge > 0 ? '#ff4444' : '#4444ff'
    });
    
    // Create field vectors
    const spacing = Math.min(canvas.width, canvas.height) / (gridSize + 2);
    for (let i = 1; i <= gridSize; i++) {
        for (let j = 1; j <= gridSize; j++) {
            const x = (canvas.width / (gridSize + 1)) * i;
            const y = (canvas.height / (gridSize + 1)) * j;
            
            // Skip if too close to charge
            const dx = x - canvas.width / 2;
            const dy = y - canvas.height / 2;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 30) {
                // Calculate field direction
                const fieldStrength = charge / (distance * distance) * 5000;
                const fieldX = (dx / distance) * fieldStrength;
                const fieldY = (dy / distance) * fieldStrength;
                
                objects.push({
                    type: 'field_vector',
                    x: x,
                    y: y,
                    vx: fieldX,
                    vy: fieldY,
                    color: '#00ccff'
                });
            }
        }
    }
}

// Magnetic field simulation
function setupMagneticField() {
    const strength = simulationParams.magnetic_strength || 1.0;
    const density = simulationParams.field_density || 5;
    
    // Create magnetic field vectors (circular pattern)
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    for (let i = 0; i < density; i++) {
        for (let j = 0; j < density; j++) {
            const x = (canvas.width / density) * (i + 0.5);
            const y = (canvas.height / density) * (j + 0.5);
            
            // Create circular magnetic field
            const dx = x - centerX;
            const dy = y - centerY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 20) {
                // Perpendicular to radius for circular field
                const fieldX = -dy * strength * 0.001;
                const fieldY = dx * strength * 0.001;
                
                objects.push({
                    type: 'magnetic_vector',
                    x: x,
                    y: y,
                    vx: fieldX,
                    vy: fieldY,
                    color: '#ff00ff'
                });
            }
        }
    }
    
    // Add moving charged particle
    particles.push({
        type: 'charged_particle',
        x: 100,
        y: canvas.height / 2,
        vx: 2,
        vy: 1,
        charge: 1,
        mass: 1,
        trail: [],
        color: '#ffff00'
    });
}

// Pendulum simulation
function setupPendulum() {
    const length = simulationParams.length || 5;
    const angle = (simulationParams.angle || 30) * Math.PI / 180;
    const gravity = simulationParams.gravity || 9.81;
    
    // Pendulum bob
    objects.push({
        type: 'pendulum',
        x: canvas.width / 2,
        y: 100,
        length: length * 20, // Scale for display
        angle: angle,
        velocity: 0,
        gravity: gravity * 0.01, // Scale for display
        damping: simulationParams.damping || 0.01,
        color: '#ffaa00'
    });
    
    animationState.pendulum = {
        angle: angle,
        velocity: 0,
        time: 0
    };
}

// Vector field simulation
function setupVectorField() {
    const vx = simulationParams.vx || 1.0;
    const vy = simulationParams.vy || 0.0;
    const vz = simulationParams.vz || 0.0;
    
    // Create vector at center
    objects.push({
        type: 'vector',
        x: canvas.width / 2,
        y: canvas.height / 2,
        vx: vx * 30,
        vy: vy * 30,
        vz: vz * 30,
        color: '#00ff88'
    });
}

  // Create main layout
  const mainLayout = document.createElement("div");
  mainLayout.style.cssText = `
        display: flex;
        gap: 20px;
        min-height: 500px;
    `;

  // Create controls panel
  const controlsPanel = createControlsPanel();
  controlsPanel.style.cssText = `
        width: 300px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
    `;

  // Create 3D viewport
  const viewport = create3DViewport();
  viewport.style.cssText = `
        flex: 1;
        background: #000;
        border: 1px solid #ddd;
        border-radius: 8px;
        position: relative;
        min-height: 500px;
    `;

  mainLayout.appendChild(controlsPanel);
  mainLayout.appendChild(viewport);
  simulationContainer.appendChild(mainLayout);

  document.body.appendChild(simulationContainer);

  // Start the simulation
  startSimulation();
}

// Create interactive controls panel
function createControlsPanel() {
  const panel = document.createElement("div");

  // Experiment selector
  const expSelector = document.createElement("div");
  expSelector.innerHTML = `
        <h3 style="color: #333; margin-bottom: 15px;">Choose Experiment:</h3>
        <select id="experiment-select" style="width: 100%; padding: 8px; margin-bottom: 20px; font-size: 14px;">
            <option value="electric_field">Electric Field</option>
            <option value="pendulum">Pendulum</option>
            <option value="magnetic_field">Magnetic Field</option>
            <option value="orbital_motion">Orbital Motion</option>
        </select>
    `;
  panel.appendChild(expSelector);

  // Dynamic controls container
  const controlsContainer = document.createElement("div");
  controlsContainer.id = "dynamic-controls";
  panel.appendChild(controlsContainer);

  // Add event listener for experiment change
  setTimeout(() => {
    const select = document.getElementById("experiment-select");
    if (select) {
      select.addEventListener("change", (e) => {
        currentExperiment = e.target.value;
        updateControls();
        resetSimulation();
      });
      updateControls(); // Initialize controls
    }
  }, 100);

  return panel;
}

// Create 3D visualization viewport
function create3DViewport() {
  const viewport = document.createElement("div");

  // Create canvas for 3D rendering
  canvas = document.createElement("canvas");
  canvas.width = 800;
  canvas.height = 500;
  canvas.style.cssText = `
        width: 100%;
        height: 100%;
        border-radius: 8px;
    `;

  ctx = canvas.getContext("2d");
  viewport.appendChild(canvas);

  // Add coordinate system info
  const coordInfo = document.createElement("div");
  coordInfo.style.cssText = `
        position: absolute;
        top: 10px;
        left: 10px;
        background: rgba(255,255,255,0.9);
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        color: #333;
    `;
  coordInfo.innerHTML = `
        <strong>3D Coordinate System</strong><br>
        X: Red (horizontal) →<br>
        Y: Green (vertical) ↑<br>
        Z: Blue (depth) ⊙
    `;
  viewport.appendChild(coordInfo);

  return viewport;
}

// Update controls based on selected experiment
function updateControls() {
  const container = document.getElementById("dynamic-controls");
  if (!container) return;

  let controlsHTML = "";

  switch (currentExperiment) {
    case "electric_field":
      controlsHTML = `
                <h4 style="color: #333;">Electric Field Parameters:</h4>
                <div style="margin-bottom: 15px;">
                    <label>Charge Strength (Q):</label>
                    <input type="range" id="charge-strength" min="0.1" max="5" step="0.1" value="2" 
                           style="width: 100%; margin: 5px 0;">
                    <span id="charge-value">2.0</span> μC
                </div>
                <div style="margin-bottom: 15px;">
                    <label>Grid Size:</label>
                    <input type="range" id="grid-size" min="3" max="8" step="1" value="5" 
                           style="width: 100%; margin: 5px 0;">
                    <span id="grid-value">5</span> points
                </div>
                <div style="margin-bottom: 15px;">
                    <label>Show Field Lines:</label>
                    <input type="checkbox" id="show-field-lines" checked>
                </div>
                <button id="reset-btn" style="width: 100%; padding: 10px; background: #007acc; color: white; border: none; border-radius: 5px;">
                    Reset Simulation
                </button>
            `;
      break;

    case "pendulum":
      controlsHTML = `
                <h4 style="color: #333;">Pendulum Parameters:</h4>
                <div style="margin-bottom: 15px;">
                    <label>Length (L):</label>
                    <input type="range" id="pendulum-length" min="1" max="5" step="0.1" value="2" 
                           style="width: 100%; margin: 5px 0;">
                    <span id="length-value">2.0</span> m
                </div>
                <div style="margin-bottom: 15px;">
                    <label>Initial Angle:</label>
                    <input type="range" id="initial-angle" min="10" max="60" step="5" value="30" 
                           style="width: 100%; margin: 5px 0;">
                    <span id="angle-value">30</span>°
                </div>
                <div style="margin-bottom: 15px;">
                    <label>Gravity (g):</label>
                    <input type="range" id="gravity" min="5" max="15" step="0.5" value="9.8" 
                           style="width: 100%; margin: 5px 0;">
                    <span id="gravity-value">9.8</span> m/s²
                </div>
                <button id="start-pendulum" style="width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; margin-bottom: 10px;">
                    Start Motion
                </button>
                <button id="reset-btn" style="width: 100%; padding: 10px; background: #007acc; color: white; border: none; border-radius: 5px;">
                    Reset
                </button>
            `;
      break;

    case "magnetic_field":
      controlsHTML = `
                <h4 style="color: #333;">Magnetic Field Parameters:</h4>
                <div style="margin-bottom: 15px;">
                    <label>Field Strength (B):</label>
                    <input type="range" id="magnetic-strength" min="0.1" max="3" step="0.1" value="1" 
                           style="width: 100%; margin: 5px 0;">
                    <span id="magnetic-value">1.0</span> Tesla
                </div>
                <div style="margin-bottom: 15px;">
                    <label>Particle Velocity:</label>
                    <input type="range" id="particle-velocity" min="0.5" max="3" step="0.1" value="1.5" 
                           style="width: 100%; margin: 5px 0;">
                    <span id="velocity-value">1.5</span> m/s
                </div>
                <div style="margin-bottom: 15px;">
                    <label>Show Field Lines:</label>
                    <input type="checkbox" id="show-magnetic-lines" checked>
                </div>
                <button id="launch-particle" style="width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; margin-bottom: 10px;">
                    Launch Particle
                </button>
                <button id="reset-btn" style="width: 100%; padding: 10px; background: #007acc; color: white; border: none; border-radius: 5px;">
                    Reset
                </button>
            `;
      break;
  }

  container.innerHTML = controlsHTML;

  // Add event listeners to controls
  addControlEventListeners();
}

// Add event listeners to controls
function addControlEventListeners() {
  // Common reset button
  const resetBtn = document.getElementById("reset-btn");
  if (resetBtn) {
    resetBtn.addEventListener("click", resetSimulation);
  }

  // Experiment-specific controls
  switch (currentExperiment) {
    case "electric_field":
      const chargeSlider = document.getElementById("charge-strength");
      const gridSlider = document.getElementById("grid-size");
      const fieldLinesCheck = document.getElementById("show-field-lines");

      if (chargeSlider) {
        chargeSlider.addEventListener("input", (e) => {
          document.getElementById("charge-value").textContent = e.target.value;
          updateSimulation();
        });
      }
      if (gridSlider) {
        gridSlider.addEventListener("input", (e) => {
          document.getElementById("grid-value").textContent = e.target.value;
          updateSimulation();
        });
      }
      if (fieldLinesCheck) {
        fieldLinesCheck.addEventListener("change", updateSimulation);
      }
      break;

    case "pendulum":
      const lengthSlider = document.getElementById("pendulum-length");
      const angleSlider = document.getElementById("initial-angle");
      const gravitySlider = document.getElementById("gravity");
      const startBtn = document.getElementById("start-pendulum");

      if (lengthSlider) {
        lengthSlider.addEventListener("input", (e) => {
          document.getElementById("length-value").textContent = e.target.value;
          updateSimulation();
        });
      }
      if (angleSlider) {
        angleSlider.addEventListener("input", (e) => {
          document.getElementById("angle-value").textContent = e.target.value;
          updateSimulation();
        });
      }
      if (gravitySlider) {
        gravitySlider.addEventListener("input", (e) => {
          document.getElementById("gravity-value").textContent = e.target.value;
          updateSimulation();
        });
      }
      if (startBtn) {
        startBtn.addEventListener("click", startPendulumMotion);
      }
      break;
  }
}

// 3D Rendering functions
function project3D(x, y, z) {
  // Simple 3D to 2D projection
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const scale = 60;

  // Isometric projection
  const screenX = centerX + (x - z) * scale * 0.866;
  const screenY = centerY + (y - (x + z) * 0.5) * scale;

  return { x: screenX, y: screenY };
}

function drawSphere(x, y, z, radius, color, label) {
  const pos = project3D(x, y, z);

  ctx.beginPath();
  ctx.arc(pos.x, pos.y, radius * 20, 0, 2 * Math.PI);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 2;
  ctx.stroke();

  if (label) {
    ctx.fillStyle = "#333";
    ctx.font = "12px Arial";
    ctx.fillText(label, pos.x + radius * 25, pos.y - radius * 25);
  }
}

function drawArrow(startX, startY, startZ, endX, endY, endZ, color) {
  const start = project3D(startX, startY, startZ);
  const end = project3D(endX, endY, endZ);

  // Draw arrow line
  ctx.beginPath();
  ctx.moveTo(start.x, start.y);
  ctx.lineTo(end.x, end.y);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();

  // Draw arrowhead
  const angle = Math.atan2(end.y - start.y, end.x - start.x);
  const headLength = 10;

  ctx.beginPath();
  ctx.moveTo(end.x, end.y);
  ctx.lineTo(
    end.x - headLength * Math.cos(angle - Math.PI / 6),
    end.y - headLength * Math.sin(angle - Math.PI / 6)
  );
  ctx.moveTo(end.x, end.y);
  ctx.lineTo(
    end.x - headLength * Math.cos(angle + Math.PI / 6),
    end.y - headLength * Math.sin(angle + Math.PI / 6)
  );
  ctx.stroke();
}

function drawGrid() {
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 1;

  // Draw coordinate axes
  const origin = project3D(0, 0, 0);

  // X-axis (red)
  const xEnd = project3D(3, 0, 0);
  ctx.strokeStyle = "#ff0000";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(origin.x, origin.y);
  ctx.lineTo(xEnd.x, xEnd.y);
  ctx.stroke();

  // Y-axis (green)
  const yEnd = project3D(0, 3, 0);
  ctx.strokeStyle = "#00ff00";
  ctx.beginPath();
  ctx.moveTo(origin.x, origin.y);
  ctx.lineTo(yEnd.x, yEnd.y);
  ctx.stroke();

  // Z-axis (blue)
  const zEnd = project3D(0, 0, 3);
  ctx.strokeStyle = "#0000ff";
  ctx.beginPath();
  ctx.moveTo(origin.x, origin.y);
  ctx.lineTo(zEnd.x, zEnd.y);
  ctx.stroke();
}

// Physics simulation functions
function simulateElectricField() {
  if (!ctx) return;

  // Clear canvas
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  drawGrid();

  // Get parameters
  const charge = parseFloat(
    document.getElementById("charge-strength")?.value || 2
  );
  const gridSize = parseInt(document.getElementById("grid-size")?.value || 5);
  const showLines =
    document.getElementById("show-field-lines")?.checked || true;

  // Draw charge at origin
  drawSphere(0, 0, 0, 0.3, "#ffff00", "Q = +" + charge + "μC");

  // Draw electric field vectors
  const range = Math.floor(gridSize / 2);
  for (let x = -range; x <= range; x++) {
    for (let y = -range; y <= range; y++) {
      if (x === 0 && y === 0) continue; // Skip origin

      const r = Math.sqrt(x * x + y * y);
      const E = charge / (r * r + 0.1); // Electric field magnitude (simplified)

      const Ex = (E * x) / r;
      const Ey = (E * y) / r;

      // Scale for visualization
      const scale = 0.3;
      drawArrow(x, y, 0, x + Ex * scale, y + Ey * scale, 0, "#00ffff");
    }
  }

  // Add field strength indicator
  ctx.fillStyle = "#fff";
  ctx.font = "14px Arial";
  ctx.fillText(`Electric Field Strength: ${charge} μC`, 10, 30);
  ctx.fillText(`Grid: ${gridSize}×${gridSize} points`, 10, 50);
}

function simulatePendulum() {
  if (!ctx) return;

  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  drawGrid();

  const length = parseFloat(
    document.getElementById("pendulum-length")?.value || 2
  );
  const initialAngle =
    (parseFloat(document.getElementById("initial-angle")?.value || 30) *
      Math.PI) /
    180;
  const gravity = parseFloat(document.getElementById("gravity")?.value || 9.8);

  let currentAngle = initialAngle;

  // If animating, calculate current position
  if (animationState.pendulum.isAnimating) {
    const dt = 0.02;
    animationState.pendulum.time += dt;

    // Simple harmonic motion approximation for small angles
    const omega = Math.sqrt(gravity / length);
    currentAngle =
      initialAngle * Math.cos(omega * animationState.pendulum.time);
  }

  // Calculate bob position
  const bobX = length * Math.sin(currentAngle);
  const bobY = -length * Math.cos(currentAngle);

  // Draw string
  drawArrow(0, 0, 0, bobX, bobY, 0, "#ffffff");

  // Draw bob
  drawSphere(bobX, bobY, 0, 0.2, "#ff0000", "Mass");

  // Draw pivot
  drawSphere(0, 0, 0, 0.1, "#888888", "Pivot");

  // Draw trajectory arc if animating
  if (animationState.pendulum.isAnimating) {
    ctx.strokeStyle = "#ffff00";
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);

    const centerPos = project3D(0, 0, 0);
    const radius = length * 60; // Scale for display

    ctx.beginPath();
    const startAngle = Math.PI / 2 - initialAngle;
    const endAngle = Math.PI / 2 + initialAngle;
    ctx.arc(
      centerPos.x,
      centerPos.y + length * 30,
      radius,
      startAngle,
      endAngle
    );
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // Calculate and display physics values
  const period = 2 * Math.PI * Math.sqrt(length / gravity);
  const maxVelocity = initialAngle * Math.sqrt(gravity * length);
  const energy = 0.5 * length * gravity * initialAngle * initialAngle; // Simplified

  ctx.fillStyle = "#fff";
  ctx.font = "14px Arial";
  ctx.fillText(`Length: ${length} m`, 10, 30);
  ctx.fillText(
    `Initial Angle: ${((initialAngle * 180) / Math.PI).toFixed(1)}°`,
    10,
    50
  );
  ctx.fillText(
    `Current Angle: ${((currentAngle * 180) / Math.PI).toFixed(1)}°`,
    10,
    70
  );
  ctx.fillText(`Period: ${period.toFixed(2)} s`, 10, 90);
  ctx.fillText(`Max Velocity: ${maxVelocity.toFixed(2)} m/s`, 10, 110);
  ctx.fillText(`Energy: ${energy.toFixed(3)} J`, 10, 130);
}

function simulateMagneticField() {
  if (!ctx) return;

  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  drawGrid();

  const fieldStrength = parseFloat(
    document.getElementById("magnetic-strength")?.value || 1
  );
  const velocity = parseFloat(
    document.getElementById("particle-velocity")?.value || 1.5
  );
  const showLines =
    document.getElementById("show-magnetic-lines")?.checked || true;

  // Draw magnetic field lines (into the page - represented by X symbols)
  if (showLines) {
    ctx.fillStyle = "#00ff00";
    ctx.font = "16px Arial";
    for (let x = -3; x <= 3; x += 1) {
      for (let y = -2; y <= 2; y += 1) {
        const pos = project3D(x, y, 0);
        ctx.fillText("⊗", pos.x - 8, pos.y + 8); // X symbol for field into page
      }
    }
  }

  // Draw particles and their circular paths
  animationState.particles.forEach((particle, index) => {
    // Update particle position (circular motion in magnetic field)
    if (particle.isMoving) {
      const radius =
        (particle.mass * velocity) / (particle.charge * fieldStrength);
      particle.angle += particle.angularVelocity;

      particle.x = particle.centerX + radius * Math.cos(particle.angle);
      particle.y = particle.centerY + radius * Math.sin(particle.angle);

      // Draw trail
      if (particle.trail.length > 50) particle.trail.shift();
      particle.trail.push({ x: particle.x, y: particle.y });

      // Draw trail
      ctx.strokeStyle = particle.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 1; i < particle.trail.length; i++) {
        const pos1 = project3D(
          particle.trail[i - 1].x,
          particle.trail[i - 1].y,
          0
        );
        const pos2 = project3D(particle.trail[i].x, particle.trail[i].y, 0);
        if (i === 1) ctx.moveTo(pos1.x, pos1.y);
        ctx.lineTo(pos2.x, pos2.y);
      }
      ctx.stroke();
    }

    // Draw particle
    drawSphere(particle.x, particle.y, 0, 0.1, particle.color, `q${index + 1}`);

    // Draw velocity vector
    const vx = -velocity * Math.sin(particle.angle) * 0.3;
    const vy = velocity * Math.cos(particle.angle) * 0.3;
    drawArrow(
      particle.x,
      particle.y,
      0,
      particle.x + vx,
      particle.y + vy,
      0,
      "#ffff00"
    );
  });

  // Display information
  ctx.fillStyle = "#fff";
  ctx.font = "14px Arial";
  ctx.fillText(`Magnetic Field: ${fieldStrength} T (into page)`, 10, 30);
  ctx.fillText(`Particle Velocity: ${velocity} m/s`, 10, 50);
  if (animationState.particles.length > 0) {
    const radius = velocity / fieldStrength; // Simplified
    ctx.fillText(`Cyclotron Radius: ${radius.toFixed(2)} m`, 10, 70);
    const frequency = fieldStrength / (2 * Math.PI); // Simplified
    ctx.fillText(`Cyclotron Frequency: ${frequency.toFixed(2)} Hz`, 10, 90);
  }
}

function updateSimulation() {
  switch (currentExperiment) {
    case "electric_field":
      simulateElectricField();
      break;
    case "pendulum":
      simulatePendulum();
      break;
    case "magnetic_field":
      // TODO: Implement magnetic field simulation
      break;
  }
}

function resetSimulation() {
  objects = [];
  updateSimulation();
}

function animate() {
  updateSimulation();
  animationId = requestAnimationFrame(animate);
}

function startPendulumMotion() {
  const startBtn = document.getElementById("start-pendulum");

  if (!animationState.pendulum.isAnimating) {
    // Start animation
    animationState.pendulum.isAnimating = true;
    animationState.pendulum.time = 0;
    if (startBtn) {
      startBtn.textContent = "Stop Motion";
      startBtn.style.background = "#dc3545";
    }
    console.log("Pendulum animation started");
  } else {
    // Stop animation
    animationState.pendulum.isAnimating = false;
    animationState.pendulum.time = 0;
    if (startBtn) {
      startBtn.textContent = "Start Motion";
      startBtn.style.background = "#28a745";
    }
    console.log("Pendulum animation stopped");
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", initializeSimulation);

// Legacy VPython compatibility (for existing code)
window.scene = {
  title: "",
  append_to_caption: function (text) {
    console.log("VPython caption:", text);
  },
};

window.vector = function (x, y, z) {
  return { x: x || 0, y: y || 0, z: z || 0 };
};

window.sphere = function () {
  return {};
};
window.arrow = function () {
  return {};
};
window.color = {
  red: "#ff0000",
  green: "#00ff00",
  blue: "#0000ff",
  yellow: "#ffff00",
  cyan: "#00ffff",
  magenta: "#ff00ff",
  white: "#ffffff",
  black: "#000000",
};

console.log("Interactive Physics Simulation Engine loaded successfully!");

// Colors
window.color = {
  red: [1, 0, 0],
  green: [0, 1, 0],
  blue: [0, 0, 1],
  yellow: [1, 1, 0],
  cyan: [0, 1, 1],
  magenta: [1, 0, 1],
  orange: [1, 0.5, 0],
  white: [1, 1, 1],
  black: [0, 0, 0],
  gray: function (v) {
    return [v, v, v];
  },
};

// Scene object with enhanced visual display
window.scene = {
  title: "",
  background: [0, 0, 0],
  _objects: [], // Track all VPython objects
  append_to_caption: function (text) {
    console.log("Caption:", text);
    var div = document.createElement("div");
    div.style.padding = "10px";
    div.style.marginBottom = "10px";
    div.style.backgroundColor = "#e8f4f8";
    div.style.border = "1px solid #4CAF50";
    div.style.borderRadius = "5px";
    div.style.fontSize = "14px";
    div.innerHTML = text;
    document.body.appendChild(div);
  },
  set title(val) {
    console.log("Scene title set:", val);
    // Create or update title element
    var titleEl = document.getElementById("scene-title");
    if (!titleEl) {
      titleEl = document.createElement("h1");
      titleEl.id = "scene-title";
      titleEl.style.textAlign = "center";
      titleEl.style.color = "#333";
      titleEl.style.marginBottom = "20px";
      titleEl.style.padding = "15px";
      titleEl.style.backgroundColor = "#f0f8ff";
      titleEl.style.border = "2px solid #007acc";
      titleEl.style.borderRadius = "8px";
      document.body.appendChild(titleEl);
    }
    titleEl.textContent = val;
  },
  addObject: function (obj) {
    this._objects.push(obj);
    this.render();
  },
  render: function () {
    // Create or update the objects container
    var container = document.getElementById("vpython-objects");
    if (!container) {
      container = document.createElement("div");
      container.id = "vpython-objects";
      container.style.padding = "20px";
      container.style.backgroundColor = "#f9f9f9";
      container.style.border = "2px solid #ddd";
      container.style.borderRadius = "10px";
      container.style.margin = "20px 0";
      document.body.appendChild(container);

      var header = document.createElement("h3");
      header.textContent = "3D Objects in Scene:";
      header.style.marginTop = "0";
      header.style.color = "#555";
      container.appendChild(header);
    }

    // Clear previous object displays and re-render all
    var objectsDiv = document.getElementById("objects-list");
    if (objectsDiv) {
      objectsDiv.remove();
    }

    objectsDiv = document.createElement("div");
    objectsDiv.id = "objects-list";
    container.appendChild(objectsDiv);

    this._objects.forEach(function (obj, index) {
      if (obj._render) {
        obj._render(objectsDiv, index);
      }
    });
  },
};

// 3D Objects with visual display
window.sphere = function (opts) {
  opts = opts || {};
  console.log("Creating sphere:", opts);

  var pos = opts.pos || window.vec(0, 0, 0);
  var radius = opts.radius || 1;
  var color = opts.color || window.color.white;
  var make_trail = opts.make_trail || false;

  var obj = {
    pos: pos,
    radius: radius,
    color: color,
    make_trail: make_trail,
    _type: "sphere",
    _render: function (container, index) {
      var div = document.createElement("div");
      div.style.padding = "15px";
      div.style.margin = "10px 0";
      div.style.backgroundColor = "#fff";
      div.style.border = "2px solid #4CAF50";
      div.style.borderRadius = "8px";
      div.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";

      var colorName = getColorName(this.color);
      var trailText = this.make_trail ? " (with trail)" : "";

      // Safe property access with fallbacks
      var posX =
        this.pos && typeof this.pos.x === "number"
          ? this.pos.x.toFixed(2)
          : "0.00";
      var posY =
        this.pos && typeof this.pos.y === "number"
          ? this.pos.y.toFixed(2)
          : "0.00";
      var posZ =
        this.pos && typeof this.pos.z === "number"
          ? this.pos.z.toFixed(2)
          : "0.00";
      var radius =
        typeof this.radius === "number" ? this.radius.toFixed(2) : "1.00";

      div.innerHTML = `
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 24px; margin-right: 10px;">🟡</span>
                    <strong style="color: #2E7D32;">Sphere ${index + 1}</strong>
                </div>
                <div style="font-family: monospace; font-size: 13px; line-height: 1.4;">
                    <div><strong>Position:</strong> (${posX}, ${posY}, ${posZ})</div>
                    <div><strong>Radius:</strong> ${radius}</div>
                    <div><strong>Color:</strong> <span style="color: ${colorName};">${colorName}</span>${trailText}</div>
                </div>
            `;

      container.appendChild(div);
    },
  };

  // Add to scene for rendering
  window.scene.addObject(obj);
  return obj;
};

window.arrow = function (opts) {
  opts = opts || {};
  console.log("Creating arrow:", opts);

  var pos = opts.pos || window.vec(0, 0, 0);
  var axis = opts.axis || window.vec(1, 0, 0);
  var color = opts.color || window.color.white;
  var shaftwidth = opts.shaftwidth || 0.1;

  var obj = {
    pos: pos,
    axis: axis,
    color: color,
    shaftwidth: shaftwidth,
    _type: "arrow",
    _render: function (container, index) {
      var div = document.createElement("div");
      div.style.padding = "15px";
      div.style.margin = "10px 0";
      div.style.backgroundColor = "#fff";
      div.style.border = "2px solid #007acc";
      div.style.borderRadius = "8px";
      div.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";

      var colorName = getColorName(this.color);

      // Safe property access with fallbacks
      var posX =
        this.pos && typeof this.pos.x === "number"
          ? this.pos.x.toFixed(2)
          : "0.00";
      var posY =
        this.pos && typeof this.pos.y === "number"
          ? this.pos.y.toFixed(2)
          : "0.00";
      var posZ =
        this.pos && typeof this.pos.z === "number"
          ? this.pos.z.toFixed(2)
          : "0.00";

      var axisX =
        this.axis && typeof this.axis.x === "number"
          ? this.axis.x.toFixed(2)
          : "1.00";
      var axisY =
        this.axis && typeof this.axis.y === "number"
          ? this.axis.y.toFixed(2)
          : "0.00";
      var axisZ =
        this.axis && typeof this.axis.z === "number"
          ? this.axis.z.toFixed(2)
          : "0.00";

      var length =
        this.axis && window.mag ? window.mag(this.axis).toFixed(2) : "1.00";

      div.innerHTML = `
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 24px; margin-right: 10px;">➡️</span>
                    <strong style="color: #1976D2;">Arrow ${index + 1}</strong>
                </div>
                <div style="font-family: monospace; font-size: 13px; line-height: 1.4;">
                    <div><strong>Start:</strong> (${posX}, ${posY}, ${posZ})</div>
                    <div><strong>Direction:</strong> (${axisX}, ${axisY}, ${axisZ})</div>
                    <div><strong>Length:</strong> ${length}</div>
                    <div><strong>Color:</strong> <span style="color: ${colorName};">${colorName}</span></div>
                </div>
            `;

      container.appendChild(div);
    },
  };

  // Add to scene for rendering
  window.scene.addObject(obj);
  return obj;
};

// Helper function to get color names
function getColorName(color) {
  if (!color) return "white";
  if (color === window.color.red) return "red";
  if (color === window.color.green) return "green";
  if (color === window.color.blue) return "blue";
  if (color === window.color.yellow) return "yellow";
  if (color === window.color.cyan) return "cyan";
  if (color === window.color.magenta) return "magenta";
  if (color === window.color.orange) return "orange";
  if (color === window.color.white) return "white";
  if (color === window.color.black) return "black";
  if (Array.isArray(color)) {
    return `rgb(${Math.round(color[0] * 255)}, ${Math.round(
      color[1] * 255
    )}, ${Math.round(color[2] * 255)})`;
  }
  return "unknown";
}

// Animation and math
window.rate = function (fps) {
  return new Promise((resolve) => setTimeout(resolve, 1000 / (fps || 60)));
};

window.mag = function (v) {
  if (v && v.mag !== undefined) return v.mag;
  if (v && v.x !== undefined)
    return Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
  return 0;
};

// Make available globally for VPython scripts
Object.assign(window, {
  vector: window.vector,
  sphere: window.sphere,
  arrow: window.arrow,
  color: window.color,
  scene: window.scene,
  rate: window.rate,
  mag: window.mag,
});

console.log("GlowScript runtime loaded - VPython ready");

// Add some initial styling to the page
document.addEventListener("DOMContentLoaded", function () {
  document.body.style.fontFamily = "Arial, sans-serif";
  document.body.style.margin = "20px";
  document.body.style.backgroundColor = "#f5f5f5";

  var header = document.createElement("div");
  header.style.textAlign = "center";
  header.style.marginBottom = "20px";
  header.style.padding = "10px";
  header.style.backgroundColor = "#007acc";
  header.style.color = "white";
  header.style.borderRadius = "5px";
  header.innerHTML = "<h2>VPython Simulation Output</h2>";
  document.body.appendChild(header);

  // Execute Python-like scripts after DOM loads
  executePythonScripts();
});

// If DOM is already loaded, apply styles immediately
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", arguments.callee);
} else {
  document.body.style.fontFamily = "Arial, sans-serif";
  document.body.style.margin = "20px";
  document.body.style.backgroundColor = "#f5f5f5";
  executePythonScripts();
}

// Function to execute VPython-like scripts
function executePythonScripts() {
  var scripts = document.querySelectorAll('script[type="text/python"]');
  scripts.forEach(function (script) {
    var code = script.textContent;
    console.log("Executing VPython code:", code);

    // Parse and execute common VPython patterns
    try {
      executeVPythonCode(code);
    } catch (e) {
      console.error("Error executing VPython code:", e);
      window.scene.append_to_caption("Error: " + e.message);
    }
  });
}

// Simple VPython code executor
function executeVPythonCode(code) {
  console.log("Parsing VPython code...");

  // Extract and execute scene.title
  var titleMatch = code.match(/scene\.title\s*=\s*['"]([^'"]+)['"]/);
  if (titleMatch) {
    window.scene.title = titleMatch[1];
  }

  // Extract vector definitions with better regex
  var vectors = {};
  var vectorPattern = /(\w+)\s*=\s*vector\s*\(\s*([^)]+)\s*\)/g;
  var vectorMatch;
  while ((vectorMatch = vectorPattern.exec(code)) !== null) {
    var name = vectorMatch[1];
    var coordsStr = vectorMatch[2];
    try {
      var coords = coordsStr.split(",").map((s) => parseFloat(s.trim()));
      vectors[name] = window.vector(
        coords[0] || 0,
        coords[1] || 0,
        coords[2] || 0
      );
      console.log("Created vector:", name, vectors[name]);
    } catch (e) {
      console.warn("Error parsing vector:", name, e);
    }
  }

  // Extract sphere creation with improved parsing
  var spherePattern = /(?:(\w+)\s*=\s*)?sphere\s*\(\s*([^)]+)\s*\)/g;
  var sphereMatch;
  while ((sphereMatch = spherePattern.exec(code)) !== null) {
    var paramStr = sphereMatch[2];
    try {
      var params = parseFunctionParams(paramStr);
      // Replace vector name references with actual vector objects
      replaceVectorReferences(params, vectors);
      console.log("Creating sphere with params:", params);
      window.sphere(params);
    } catch (e) {
      console.warn("Error creating sphere:", e);
    }
  }

  // Extract arrow creation with improved parsing
  var arrowPattern = /(?:(\w+)\s*=\s*)?arrow\s*\(\s*([^)]+)\s*\)/g;
  var arrowMatch;
  while ((arrowMatch = arrowPattern.exec(code)) !== null) {
    var paramStr = arrowMatch[2];
    try {
      var params = parseFunctionParams(paramStr);
      // Replace vector name references with actual vector objects
      replaceVectorReferences(params, vectors);
      console.log("Creating arrow with params:", params);
      window.arrow(params);
    } catch (e) {
      console.warn("Error creating arrow:", e);
    }
  }

  // Extract scene captions
  var captionPattern = /scene\.append_to_caption\s*\(\s*['"]([^'"]+)['"]\s*\)/g;
  var captionMatch;
  while ((captionMatch = captionPattern.exec(code)) !== null) {
    window.scene.append_to_caption(captionMatch[1]);
  }

  console.log("VPython code execution completed");
}

// Helper function to replace vector name references with actual vector objects
function replaceVectorReferences(params, vectors) {
  for (let key in params) {
    if (typeof params[key] === "string" && vectors[params[key]]) {
      params[key] = vectors[params[key]];
    }
  }
}

// Parse function parameters from string
function parseFunctionParams(paramStr) {
  var params = {};
  var parts = paramStr.split(",");

  for (let part of parts) {
    var pair = part.trim().split("=");
    if (pair.length === 2) {
      var key = pair[0].trim();
      var value = pair[1].trim();

      // Parse different value types
      if (value.startsWith("vector(")) {
        var vectorMatch = value.match(/vector\(([^)]+)\)/);
        if (vectorMatch && vectorMatch[1]) {
          var coords = vectorMatch[1]
            .split(",")
            .map((s) => parseFloat(s.trim()));
          params[key] = window.vector(
            coords[0] || 0,
            coords[1] || 0,
            coords[2] || 0
          );
        }
      } else if (value.includes("color.")) {
        var colorParts = value.split(".");
        if (colorParts.length >= 2) {
          params[key] = window.color[colorParts[1]] || window.color.white;
        }
      } else if (!isNaN(parseFloat(value))) {
        params[key] = parseFloat(value);
      } else if (value === "True" || value === "true") {
        params[key] = true;
      } else if (value === "False" || value === "false") {
        params[key] = false;
      } else {
        params[key] = value.replace(/['"]/g, "");
      }
    }
  }

  return params;
}

// Auto-render scene when objects are added
setTimeout(function () {
  if (
    window.scene &&
    window.scene._objects &&
    window.scene._objects.length === 0
  ) {
    // If no objects were created yet, show a helpful message
    window.scene.append_to_caption(
      "VPython simulation initialized. Objects will appear here when created."
    );
  }
}, 500);

// Additional functions for magnetic field simulation
function launchParticle() {
  const velocity = parseFloat(
    document.getElementById("particle-velocity")?.value || 1.5
  );
  const fieldStrength = parseFloat(
    document.getElementById("magnetic-strength")?.value || 1
  );

  // Create new particle
  const particle = {
    x: -3,
    y: 0,
    z: 0,
    centerX: -3,
    centerY: 0,
    angle: 0,
    angularVelocity: fieldStrength / 1, // Simplified cyclotron frequency
    mass: 1,
    charge: 1,
    color: "#ff4444",
    isMoving: true,
    trail: [],
  };

  animationState.particles.push(particle);
  console.log("Particle launched!");
}

// Main simulation functions
function startSimulation() {
  updateSimulation();
  animate();
}

function updateSimulation() {
  switch (currentExperiment) {
    case "electric_field":
      simulateElectricField();
      break;
    case "pendulum":
      simulatePendulum();
      break;
    case "magnetic_field":
      simulateMagneticField();
      break;
    case "orbital_motion":
      // TODO: Implement orbital motion
      simulateElectricField(); // Fallback for now
      break;
  }
}

function resetSimulation() {
  objects = [];
  animationState.pendulum.isAnimating = false;
  animationState.pendulum.time = 0;
  animationState.particles = [];

  // Reset button states
  const startBtn = document.getElementById("start-pendulum");
  if (startBtn) {
    startBtn.textContent = "Start Motion";
    startBtn.style.background = "#28a745";
  }

  updateSimulation();
}

function animate() {
  updateSimulation();
  animationId = requestAnimationFrame(animate);
}

// Add magnetic field event listeners
setTimeout(() => {
  const launchBtn = document.getElementById("launch-particle");
  if (launchBtn) {
    launchBtn.addEventListener("click", launchParticle);
  }

  const magneticSlider = document.getElementById("magnetic-strength");
  const velocitySlider = document.getElementById("particle-velocity");
  const magneticCheck = document.getElementById("show-magnetic-lines");

  if (magneticSlider) {
    magneticSlider.addEventListener("input", (e) => {
      document.getElementById("magnetic-value").textContent = e.target.value;
      updateSimulation();
    });
  }
  if (velocitySlider) {
    velocitySlider.addEventListener("input", (e) => {
      document.getElementById("velocity-value").textContent = e.target.value;
      updateSimulation();
    });
  }
  if (magneticCheck) {
    magneticCheck.addEventListener("change", updateSimulation);
  }
}, 1000);
