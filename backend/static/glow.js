// Interactive Dynamic Physics Simulation Engine
console.log("Loading Interactive Physics Simulation Engine...");

// Global simulation state
let canvas, ctx, animationId;
let currentExperiment = "electric_field";
let simulationParams = {
  showFieldLines: true,
  showForces: true,
  animateFields: true,
  fieldStrength: 2.0,
  gridDensity: 15,
};
let isAnimating = true;
let mousePos = { x: 0, y: 0 };
let isDragging = false;
let selectedCharge = null;

// Physics objects
let charges = [];
let fieldLines = [];
let testCharges = [];
let fieldVectors = [];

// Animation state
let animationTime = 0;
let fieldLineAnimation = 0;

// Color scheme
const colors = {
  positive: "#ff4444",
  negative: "#4444ff",
  neutral: "#44ff44",
  fieldLine: "#00ffff",
  fieldVector: "#ffff00",
  background: "#000011",
  ui: "#ffffff",
};

// Initialize simulation with responsive design
function initializeSimulation() {
  console.log("Initializing interactive physics simulation...");

  // Find canvas
  canvas =
    document.querySelector("canvas") ||
    document.getElementById("simulation-canvas");
  if (!canvas) {
    canvas = document.createElement("canvas");
    canvas.id = "simulation-canvas";
    const container =
      document.getElementById("physics-simulation") || document.body;
    container.appendChild(canvas);
  }

  // Make canvas responsive
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  ctx = canvas.getContext("2d");
  if (!ctx) {
    console.error("Failed to get canvas context");
    return;
  }

  // Setup interaction
  setupInteraction();

  // Initialize with sample charges
  initializeDefaultScene();

  // Start animation
  startAnimation();

  console.log("Interactive physics simulation ready!");
}

function resizeCanvas() {
  const container = canvas.parentElement;
  if (container) {
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width || 800;
    canvas.height = rect.height || 600;
    canvas.style.width = "100%";
    canvas.style.height = "100%";
  } else {
    canvas.width = window.innerWidth * 0.7;
    canvas.height = window.innerHeight * 0.8;
  }
}

function setupInteraction() {
  // Mouse/touch events for adding charges
  canvas.addEventListener("click", onCanvasClick);
  canvas.addEventListener("mousedown", onMouseDown);
  canvas.addEventListener("mousemove", onMouseMove);
  canvas.addEventListener("mouseup", onMouseUp);
  canvas.addEventListener("contextmenu", onRightClick);

  // Touch events for mobile
  canvas.addEventListener("touchstart", onTouchStart);
  canvas.addEventListener("touchmove", onTouchMove);
  canvas.addEventListener("touchend", onTouchEnd);
}

function onCanvasClick(event) {
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  // Scale to canvas coordinates
  const canvasX = (x / rect.width) * canvas.width;
  const canvasY = (y / rect.height) * canvas.height;

  // Add new charge (alternating positive/negative)
  const charge = charges.length % 2 === 0 ? 2.0 : -2.0;
  addCharge(canvasX, canvasY, charge);

  // Regenerate field
  generateElectricField();
}

function onMouseDown(event) {
  const rect = canvas.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * canvas.width;
  const y = ((event.clientY - rect.top) / rect.height) * canvas.height;

  // Check if clicking on existing charge
  selectedCharge = findChargeAt(x, y);
  if (selectedCharge) {
    isDragging = true;
    canvas.style.cursor = "grabbing";
  }
}

function onMouseMove(event) {
  const rect = canvas.getBoundingClientRect();
  mousePos.x = ((event.clientX - rect.left) / rect.width) * canvas.width;
  mousePos.y = ((event.clientY - rect.top) / rect.height) * canvas.height;

  if (isDragging && selectedCharge) {
    selectedCharge.x = mousePos.x;
    selectedCharge.y = mousePos.y;
    generateElectricField();
  }

  // Update cursor
  const hoverCharge = findChargeAt(mousePos.x, mousePos.y);
  canvas.style.cursor = hoverCharge ? "grab" : "crosshair";
}

function onMouseUp(event) {
  isDragging = false;
  selectedCharge = null;
  canvas.style.cursor = "crosshair";
}

function onRightClick(event) {
  event.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * canvas.width;
  const y = ((event.clientY - rect.top) / rect.height) * canvas.height;

  // Remove charge at this position
  removeChargeAt(x, y);
  generateElectricField();
}

// Touch events
function onTouchStart(event) {
  event.preventDefault();
  const touch = event.touches[0];
  onMouseDown({ clientX: touch.clientX, clientY: touch.clientY });
}

function onTouchMove(event) {
  event.preventDefault();
  const touch = event.touches[0];
  onMouseMove({ clientX: touch.clientX, clientY: touch.clientY });
}

function onTouchEnd(event) {
  event.preventDefault();
  onMouseUp({});
}

function findChargeAt(x, y) {
  for (let charge of charges) {
    const dx = x - charge.x;
    const dy = y - charge.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < charge.radius + 10) {
      return charge;
    }
  }
  return null;
}

function removeChargeAt(x, y) {
  for (let i = charges.length - 1; i >= 0; i--) {
    const charge = charges[i];
    const dx = x - charge.x;
    const dy = y - charge.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < charge.radius + 10) {
      charges.splice(i, 1);
      break;
    }
  }
}

function addCharge(x, y, charge) {
  charges.push({
    x: x,
    y: y,
    charge: charge,
    radius: Math.abs(charge) * 8 + 12,
    color: charge > 0 ? colors.positive : colors.negative,
    velocity: { x: 0, y: 0 },
    fixed: false,
  });
}

function initializeDefaultScene() {
  charges = [];

  // Add sample charges
  addCharge(canvas.width * 0.3, canvas.height * 0.5, 3.0);
  addCharge(canvas.width * 0.7, canvas.height * 0.5, -2.0);

  generateElectricField();
}

function generateElectricField() {
  fieldVectors = [];
  fieldLines = [];

  if (currentExperiment !== "electric_field") return;

  // Generate field vectors on grid
  const gridSpacing = Math.max(30, canvas.width / simulationParams.gridDensity);

  for (let x = gridSpacing; x < canvas.width - gridSpacing; x += gridSpacing) {
    for (
      let y = gridSpacing;
      y < canvas.height - gridSpacing;
      y += gridSpacing
    ) {
      const field = calculateElectricField(x, y);
      const magnitude = Math.sqrt(field.x * field.x + field.y * field.y);

      if (magnitude > 0.01 && magnitude < 50) {
        fieldVectors.push({
          x: x,
          y: y,
          Ex: field.x,
          Ey: field.y,
          magnitude: magnitude,
        });
      }
    }
  }

  // Generate field lines from positive charges
  if (simulationParams.showFieldLines) {
    generateFieldLines();
  }
}

function calculateElectricField(x, y) {
  let Ex = 0,
    Ey = 0;
  const k = 200; // Coulomb constant (scaled)

  for (let charge of charges) {
    const dx = x - charge.x;
    const dy = y - charge.y;
    const r2 = dx * dx + dy * dy;
    const r = Math.sqrt(r2);

    if (r > charge.radius) {
      // Don't calculate field inside charge
      const E = (k * charge.charge) / (r2 + 1); // +1 to prevent singularity
      Ex += (E * dx) / r;
      Ey += (E * dy) / r;
    }
  }

  return { x: Ex, y: Ey };
}

function generateFieldLines() {
  fieldLines = [];

  for (let charge of charges) {
    if (charge.charge > 0) {
      // Start field lines from positive charges
      const numLines = Math.floor(Math.abs(charge.charge) * 8);

      for (let i = 0; i < numLines; i++) {
        const angle = (2 * Math.PI * i) / numLines;
        const startX = charge.x + Math.cos(angle) * (charge.radius + 5);
        const startY = charge.y + Math.sin(angle) * (charge.radius + 5);

        const line = traceFieldLine(startX, startY, true);
        if (line.length > 3) {
          fieldLines.push(line);
        }
      }
    }
  }
}

function traceFieldLine(startX, startY, forward) {
  const line = [];
  let x = startX,
    y = startY;
  const stepSize = 3;
  const maxSteps = 200;

  for (let step = 0; step < maxSteps; step++) {
    const field = calculateElectricField(x, y);
    const magnitude = Math.sqrt(field.x * field.x + field.y * field.y);

    if (magnitude < 0.1) break; // Field too weak

    line.push({ x: x, y: y, magnitude: magnitude });

    // Normalize and step
    const direction = forward ? 1 : -1;
    x += direction * (field.x / magnitude) * stepSize;
    y += direction * (field.y / magnitude) * stepSize;

    // Check bounds
    if (x < 0 || x > canvas.width || y < 0 || y > canvas.height) break;

    // Check if we hit a charge
    for (let charge of charges) {
      const dx = x - charge.x;
      const dy = y - charge.y;
      if (Math.sqrt(dx * dx + dy * dy) < charge.radius) {
        return line;
      }
    }
  }

  return line;
}

function startAnimation() {
  function animate() {
    if (!isAnimating) return;

    animationTime += 0.02;
    fieldLineAnimation += 0.05;

    // Clear canvas
    ctx.fillStyle = colors.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Render simulation
    renderBackground();
    renderFieldLines();
    renderFieldVectors();
    renderCharges();
    renderUI();

    animationId = requestAnimationFrame(animate);
  }

  animate();
}

function renderBackground() {
  // Subtle grid
  ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
  ctx.lineWidth = 1;

  const gridSize = 50;
  for (let x = 0; x < canvas.width; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }

  for (let y = 0; y < canvas.height; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
}

function renderFieldLines() {
  if (!simulationParams.showFieldLines) return;

  ctx.lineWidth = 2;

  fieldLines.forEach((line, lineIndex) => {
    if (line.length < 2) return;

    // Animated flow effect
    const animOffset = (fieldLineAnimation + lineIndex * 0.3) % 1;

    ctx.beginPath();
    ctx.moveTo(line[0].x, line[0].y);

    for (let i = 1; i < line.length; i++) {
      ctx.lineTo(line[i].x, line[i].y);
    }

    // Gradient stroke with animation
    const gradient = ctx.createLinearGradient(
      line[0].x,
      line[0].y,
      line[line.length - 1].x,
      line[line.length - 1].y
    );

    const alpha = 0.6 + 0.4 * Math.sin(animOffset * Math.PI * 2);
    gradient.addColorStop(0, `rgba(0, 255, 255, ${alpha})`);
    gradient.addColorStop(0.5, `rgba(0, 200, 255, ${alpha * 0.8})`);
    gradient.addColorStop(1, `rgba(0, 150, 255, ${alpha * 0.6})`);

    ctx.strokeStyle = gradient;
    ctx.stroke();

    // Animated flow particles
    if (simulationParams.animateFields) {
      renderFlowParticles(line, animOffset);
    }
  });
}

function renderFlowParticles(line, animOffset) {
  const numParticles = 3;

  for (let p = 0; p < numParticles; p++) {
    const progress = (animOffset + p / numParticles) % 1;
    const index = Math.floor(progress * (line.length - 1));

    if (index < line.length - 1) {
      const t = progress * (line.length - 1) - index;
      const point1 = line[index];
      const point2 = line[index + 1];

      const x = point1.x + (point2.x - point1.x) * t;
      const y = point1.y + (point2.y - point1.y) * t;

      // Draw flowing particle
      ctx.fillStyle = `rgba(255, 255, 0, ${0.8 - progress * 0.6})`;
      ctx.shadowBlur = 10;
      ctx.shadowColor = "#ffff00";
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }
}

function renderFieldVectors() {
  if (!simulationParams.showForces) return;

  fieldVectors.forEach((vector) => {
    const scale = Math.min(25, vector.magnitude * 0.8);
    const alpha = Math.min(1, vector.magnitude / 10);

    // Vector shaft
    ctx.strokeStyle = `rgba(255, 255, 0, ${alpha})`;
    ctx.lineWidth = 2;

    const endX = vector.x + (vector.Ex / vector.magnitude) * scale;
    const endY = vector.y + (vector.Ey / vector.magnitude) * scale;

    ctx.beginPath();
    ctx.moveTo(vector.x, vector.y);
    ctx.lineTo(endX, endY);
    ctx.stroke();

    // Arrowhead
    const angle = Math.atan2(vector.Ey, vector.Ex);
    const headSize = 6;

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
  });
}

function renderCharges() {
  charges.forEach((charge) => {
    // Glow effect
    ctx.shadowBlur = 20;
    ctx.shadowColor = charge.color;

    // Main charge body
    ctx.fillStyle = charge.color;
    ctx.beginPath();
    ctx.arc(charge.x, charge.y, charge.radius, 0, 2 * Math.PI);
    ctx.fill();

    // Inner highlight
    ctx.shadowBlur = 0;
    ctx.fillStyle = charge.charge > 0 ? "#ffaaaa" : "#aaaaff";
    ctx.beginPath();
    ctx.arc(
      charge.x - charge.radius / 3,
      charge.y - charge.radius / 3,
      charge.radius / 3,
      0,
      2 * Math.PI
    );
    ctx.fill();

    // Charge symbol
    ctx.fillStyle = "#ffffff";
    ctx.font = `bold ${Math.max(16, charge.radius / 2)}px Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(charge.charge > 0 ? "+" : "−", charge.x, charge.y);

    // Selection highlight
    if (charge === selectedCharge) {
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 3;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.arc(charge.x, charge.y, charge.radius + 5, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  });
}

function renderUI() {
  // Instructions
  ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
  ctx.fillRect(10, 10, 280, 120);

  ctx.fillStyle = colors.ui;
  ctx.font = "14px Arial";
  ctx.textAlign = "left";
  ctx.fillText("Interactive Electric Field Simulation", 20, 30);

  ctx.font = "12px Arial";
  ctx.fillText("• Click to add charges (alternating +/−)", 20, 50);
  ctx.fillText("• Drag charges to move them", 20, 65);
  ctx.fillText("• Right-click to remove charges", 20, 80);
  ctx.fillText("• Watch field lines flow in real-time!", 20, 95);
  ctx.fillText(
    `Charges: ${charges.length} | Field lines: ${fieldLines.length}`,
    20,
    115
  );

  // Hover info
  const hoverCharge = findChargeAt(mousePos.x, mousePos.y);
  if (hoverCharge) {
    const field = calculateElectricField(mousePos.x, mousePos.y);
    const magnitude = Math.sqrt(field.x * field.x + field.y * field.y);

    ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
    ctx.fillRect(mousePos.x + 10, mousePos.y - 40, 150, 30);

    ctx.fillStyle = colors.ui;
    ctx.font = "11px Arial";
    ctx.fillText(
      `Charge: ${hoverCharge.charge.toFixed(1)}μC`,
      mousePos.x + 15,
      mousePos.y - 25
    );
    ctx.fillText(
      `Field: ${magnitude.toFixed(1)} N/C`,
      mousePos.x + 15,
      mousePos.y - 10
    );
  }
}

// Control functions
function updateSimulation(parameter, value) {
  simulationParams[parameter] = value;

  if (parameter === "gridDensity" || parameter === "fieldStrength") {
    generateElectricField();
  }
}

function resetSimulation() {
  charges = [];
  fieldLines = [];
  fieldVectors = [];
  initializeDefaultScene();
}

function toggleAnimation() {
  isAnimating = !isAnimating;
  if (isAnimating) startAnimation();
}

function addRandomCharge() {
  const x = Math.random() * (canvas.width - 100) + 50;
  const y = Math.random() * (canvas.height - 100) + 50;
  const charge = (Math.random() > 0.5 ? 1 : -1) * (1 + Math.random() * 3);
  addCharge(x, y, charge);
  generateElectricField();
}

function clearAllCharges() {
  charges = [];
  fieldLines = [];
  fieldVectors = [];
}

// Setup different experiments
function setupExperiment(experiment) {
  currentExperiment = experiment;
  clearAllCharges();

  switch (experiment) {
    case "electric_field":
      initializeDefaultScene();
      break;
    case "dipole":
      addCharge(canvas.width * 0.4, canvas.height * 0.5, 2.0);
      addCharge(canvas.width * 0.6, canvas.height * 0.5, -2.0);
      generateElectricField();
      break;
    case "quadrupole":
      addCharge(canvas.width * 0.3, canvas.height * 0.3, 1.5);
      addCharge(canvas.width * 0.7, canvas.height * 0.3, -1.5);
      addCharge(canvas.width * 0.3, canvas.height * 0.7, -1.5);
      addCharge(canvas.width * 0.7, canvas.height * 0.7, 1.5);
      generateElectricField();
      break;
  }
}

// Make functions globally available
window.initializeSimulation = initializeSimulation;
window.updateSimulation = updateSimulation;
window.resetSimulation = resetSimulation;
window.toggleAnimation = toggleAnimation;
window.addRandomCharge = addRandomCharge;
window.clearAllCharges = clearAllCharges;
window.setupExperiment = setupExperiment;

// Expose simulation data for stats
window.charges = charges;
window.fieldLines = fieldLines;
window.fieldVectors = fieldVectors;

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

console.log("Interactive Physics Simulation Engine loaded successfully!");
