// Interactive 3D Physics Simulation Engine
console.log("Loading Physics Simulation Engine...");

// Global simulation state
let canvas, ctx, animationId;
let currentExperiment = "electric_field";
let simulationParams = {};
let isAnimating = true;
let objects = [];
let particles = [];

// Animation state
let animationState = {
  pendulum: { angle: Math.PI / 6, velocity: 0, time: 0, isAnimating: false },
  particles: [],
};

// Initialize simulation
function initializeSimulation() {
  console.log("Initializing physics simulation...");

  // Find or create canvas
  canvas =
    document.querySelector("canvas") ||
    document.getElementById("simulation-canvas");
  if (!canvas) {
    canvas = document.createElement("canvas");
    canvas.id = "simulation-canvas";
    canvas.style.cssText =
      "width: 100%; height: 100%; background: #000011; border-radius: 8px;";

    const container =
      document.getElementById("physics-simulation") || document.body;
    container.appendChild(canvas);
  }

  // Set canvas size
  canvas.width = 800;
  canvas.height = 500;
  ctx = canvas.getContext("2d");

  if (!ctx) {
    console.error("Failed to get canvas context");
    return;
  }

  // Initialize default experiment
  setupExperiment("electric_field");
  startAnimation();

  console.log("Physics simulation initialized successfully");
}

// Setup experiment based on type
function setupExperiment(experiment) {
  currentExperiment = experiment;
  objects = [];
  particles = [];
  animationState.particles = [];

  switch (experiment) {
    case "electric_field":
      setupElectricField();
      break;
    case "magnetic_field":
      setupMagneticField();
      break;
    case "pendulum":
      setupPendulum();
      break;
    default:
      setupElectricField();
  }
}

// Electric field experiment
function setupElectricField() {
  console.log("Setting up electric field visualization");

  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;

  // Central positive charge
  objects.push({
    type: "charge",
    x: centerX,
    y: centerY,
    charge: 2.0,
    radius: 15,
    color: "#ffff00",
  });

  // Electric field vectors
  const gridSize = 7;
  const spacing = 70;

  for (let i = -Math.floor(gridSize / 2); i <= Math.floor(gridSize / 2); i++) {
    for (
      let j = -Math.floor(gridSize / 2);
      j <= Math.floor(gridSize / 2);
      j++
    ) {
      if (i === 0 && j === 0) continue;

      const x = centerX + i * spacing;
      const y = centerY + j * spacing;

      if (x > 30 && x < canvas.width - 30 && y > 30 && y < canvas.height - 30) {
        const r = Math.sqrt(i * i + j * j);
        const fieldMagnitude = 150 / (r * r);

        objects.push({
          type: "field_vector",
          x: x,
          y: y,
          vx: (i / r) * fieldMagnitude,
          vy: (j / r) * fieldMagnitude,
          color: "#00ffff",
        });
      }
    }
  }
}

// Magnetic field experiment
function setupMagneticField() {
  console.log("Setting up magnetic field visualization");

  // Magnetic field points (into page)
  const spacing = 60;
  for (let x = 50; x < canvas.width - 50; x += spacing) {
    for (let y = 50; y < canvas.height - 50; y += spacing) {
      objects.push({
        type: "magnetic_field",
        x: x,
        y: y,
        direction: -1, // into page
        color: "#ff00ff",
      });
    }
  }

  // Charged particle
  particles.push({
    type: "charged_particle",
    x: 100,
    y: canvas.height / 2,
    vx: 3,
    vy: 0,
    charge: 1,
    mass: 1,
    color: "#ff4444",
    trail: [],
  });
}

// Pendulum experiment
function setupPendulum() {
  console.log("Setting up pendulum simulation");

  const centerX = canvas.width / 2;
  const pivotY = 80;
  const length = 200;
  const angle = Math.PI / 6;

  objects.push({
    type: "pendulum",
    pivotX: centerX,
    pivotY: pivotY,
    length: length,
    angle: angle,
    color: "#ff6600",
  });

  animationState.pendulum.angle = angle;
  animationState.pendulum.velocity = 0;
  animationState.pendulum.time = 0;
}

// Animation loop
function startAnimation() {
  function animate() {
    if (!isAnimating) return;

    // Clear canvas
    ctx.fillStyle = "#000011";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Update physics
    updatePhysics();

    // Render all objects
    renderScene();

    animationId = requestAnimationFrame(animate);
  }

  animate();
}

// Update physics simulation
function updatePhysics() {
  const deltaTime = 0.016;

  // Update pendulum
  objects.forEach((obj) => {
    if (obj.type === "pendulum" && animationState.pendulum.isAnimating) {
      const g = 0.02;
      const damping = 0.999;

      const acceleration =
        -(g / obj.length) * Math.sin(animationState.pendulum.angle);
      animationState.pendulum.velocity += acceleration;
      animationState.pendulum.velocity *= damping;
      animationState.pendulum.angle += animationState.pendulum.velocity;

      obj.angle = animationState.pendulum.angle;
    }
  });

  // Update particles in magnetic field
  particles.forEach((particle) => {
    if (particle.type === "charged_particle") {
      const B = 0.02; // Magnetic field strength

      // Lorentz force: F = q(v × B)
      const fx = particle.charge * particle.vy * B;
      const fy = -particle.charge * particle.vx * B;

      particle.vx += fx / particle.mass;
      particle.vy += fy / particle.mass;

      particle.x += particle.vx;
      particle.y += particle.vy;

      // Add to trail
      particle.trail.push({ x: particle.x, y: particle.y });
      if (particle.trail.length > 80) particle.trail.shift();

      // Wrap around boundaries
      if (particle.x < 0) particle.x = canvas.width;
      if (particle.x > canvas.width) particle.x = 0;
      if (particle.y < 0) particle.y = canvas.height;
      if (particle.y > canvas.height) particle.y = 0;
    }
  });
}

// Render the scene
function renderScene() {
  // Render objects
  objects.forEach((obj) => {
    switch (obj.type) {
      case "charge":
        renderCharge(obj);
        break;
      case "field_vector":
        renderFieldVector(obj);
        break;
      case "magnetic_field":
        renderMagneticField(obj);
        break;
      case "pendulum":
        renderPendulum(obj);
        break;
    }
  });

  // Render particles
  particles.forEach((particle) => {
    renderParticle(particle);
  });

  // Render info
  renderInfo();
}

// Render individual objects
function renderCharge(charge) {
  // Glow effect
  ctx.shadowBlur = 15;
  ctx.shadowColor = charge.color;

  // Main charge
  ctx.fillStyle = charge.color;
  ctx.beginPath();
  ctx.arc(charge.x, charge.y, charge.radius, 0, 2 * Math.PI);
  ctx.fill();

  ctx.shadowBlur = 0;

  // Charge symbol
  ctx.fillStyle = "#000000";
  ctx.font = "bold 18px Arial";
  ctx.textAlign = "center";
  ctx.fillText(charge.charge > 0 ? "+" : "-", charge.x, charge.y + 6);
}

function renderFieldVector(vector) {
  const magnitude = Math.sqrt(vector.vx * vector.vx + vector.vy * vector.vy);
  if (magnitude < 0.1) return;

  const scale = Math.min(25, magnitude * 0.3);
  const endX = vector.x + (vector.vx / magnitude) * scale;
  const endY = vector.y + (vector.vy / magnitude) * scale;

  // Vector line
  ctx.strokeStyle = vector.color;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(vector.x, vector.y);
  ctx.lineTo(endX, endY);
  ctx.stroke();

  // Arrowhead
  const angle = Math.atan2(vector.vy, vector.vx);
  const headSize = 8;

  ctx.beginPath();
  ctx.moveTo(endX, endY);
  ctx.lineTo(
    endX - headSize * Math.cos(angle - Math.PI / 6),
    endY - headSize * Math.sin(angle - Math.PI / 6)
  );
  ctx.moveTo(endX, endY);
  ctx.lineTo(
    endX - headSize * Math.cos(angle + Math.PI / 6),
    endY - headSize * Math.sin(angle + Math.PI / 6)
  );
  ctx.stroke();
}

function renderMagneticField(field) {
  ctx.fillStyle = field.color;
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 2;

  // Circle for field point
  ctx.beginPath();
  ctx.arc(field.x, field.y, 4, 0, 2 * Math.PI);
  ctx.fill();

  // X for into page, dot for out of page
  if (field.direction < 0) {
    // X for into page
    ctx.beginPath();
    ctx.moveTo(field.x - 3, field.y - 3);
    ctx.lineTo(field.x + 3, field.y + 3);
    ctx.moveTo(field.x + 3, field.y - 3);
    ctx.lineTo(field.x - 3, field.y + 3);
    ctx.stroke();
  } else {
    // Dot for out of page
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(field.x, field.y, 2, 0, 2 * Math.PI);
    ctx.fill();
  }
}

function renderPendulum(pendulum) {
  const bobX = pendulum.pivotX + Math.sin(pendulum.angle) * pendulum.length;
  const bobY = pendulum.pivotY + Math.cos(pendulum.angle) * pendulum.length;

  // String
  ctx.strokeStyle = "#cccccc";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(pendulum.pivotX, pendulum.pivotY);
  ctx.lineTo(bobX, bobY);
  ctx.stroke();

  // Pivot
  ctx.fillStyle = "#666666";
  ctx.beginPath();
  ctx.arc(pendulum.pivotX, pendulum.pivotY, 6, 0, 2 * Math.PI);
  ctx.fill();

  // Bob with glow
  ctx.shadowBlur = 12;
  ctx.shadowColor = pendulum.color;
  ctx.fillStyle = pendulum.color;
  ctx.beginPath();
  ctx.arc(bobX, bobY, 18, 0, 2 * Math.PI);
  ctx.fill();
  ctx.shadowBlur = 0;
}

function renderParticle(particle) {
  // Trail
  if (particle.trail.length > 1) {
    ctx.strokeStyle = particle.color;
    ctx.lineWidth = 3;
    ctx.globalAlpha = 0.6;

    ctx.beginPath();
    ctx.moveTo(particle.trail[0].x, particle.trail[0].y);
    for (let i = 1; i < particle.trail.length; i++) {
      ctx.lineTo(particle.trail[i].x, particle.trail[i].y);
    }
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  }

  // Particle with glow
  ctx.shadowBlur = 10;
  ctx.shadowColor = particle.color;
  ctx.fillStyle = particle.color;
  ctx.beginPath();
  ctx.arc(particle.x, particle.y, 8, 0, 2 * Math.PI);
  ctx.fill();
  ctx.shadowBlur = 0;
}

function renderInfo() {
  ctx.fillStyle = "#ffffff";
  ctx.font = "16px Arial";
  ctx.textAlign = "left";

  let info = "";
  switch (currentExperiment) {
    case "electric_field":
      info =
        "Electric Field Visualization - Positive charge with field vectors";
      break;
    case "magnetic_field":
      info = "Magnetic Field - Charged particle motion (⊗ = field into page)";
      break;
    case "pendulum":
      const period = 2 * Math.PI * Math.sqrt(200 / 980); // T = 2π√(L/g)
      info = `Pendulum Motion - Period: ${period.toFixed(2)}s`;
      break;
  }

  ctx.fillText(info, 15, 25);
}

// Control functions
function updateSimulation(parameter, value) {
  simulationParams[parameter] = value;
  setupExperiment(currentExperiment);
}

function resetSimulation() {
  setupExperiment(currentExperiment);
  animationState.pendulum.isAnimating = false;
}

function toggleAnimation() {
  isAnimating = !isAnimating;
  if (isAnimating) startAnimation();
}

function startPendulum() {
  animationState.pendulum.isAnimating = true;
  animationState.pendulum.velocity = 0;
}

function stopPendulum() {
  animationState.pendulum.isAnimating = false;
}

// Make functions globally available
window.initializeSimulation = initializeSimulation;
window.updateSimulation = updateSimulation;
window.resetSimulation = resetSimulation;
window.toggleAnimation = toggleAnimation;
window.startPendulum = startPendulum;
window.stopPendulum = stopPendulum;
window.setupExperiment = setupExperiment;

// Legacy VPython compatibility
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

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeSimulation);
} else {
  initializeSimulation();
}

console.log("Physics Simulation Engine loaded successfully!");
