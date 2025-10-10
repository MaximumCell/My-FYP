# 🧬 PhysicsLab - Advanced Physics Simulation & AI-Powered Learning Platform

<div align="center">

![PhysicsLab Banner](https://img.shields.io/badge/PhysicsLab-v2.0.0-blue?style=for-the-badge&logo=atom&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat-square&logo=react&logoColor=white)](https://reactjs.org)
[![Next.js](https://img.shields.io/badge/Next.js-15.3+-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

_Revolutionary physics simulation platform combining cutting-edge machine learning, advanced visualizations, and AI-powered tutoring_

[🚀 Live Demo](https://physics-lab-six.vercel.app/) • [📚 Documentation](https://physics-lab-six.vercel.app/docs) 
</div>

## ✨ Features & Capabilities

### 🤖 **AI-Powered Physics Tutor**

- **Advanced Gemini 2.0 Integration**: Cutting-edge AI for physics problem solving and concept explanation
- **Intelligent Question Classification**: Automatically determines optimal response strategies
- **LaTeX-Rendered Mathematics**: Beautiful mathematical expressions and derivations
- **Vector Database Integration**: Context-aware responses using Qdrant for knowledge retrieval
- **Multi-Modal Understanding**: Support for text, images, and document uploads (PDF, DOCX, PPTX)
- **Adaptive Learning**: Personalized explanations based on difficulty level and learning preferences

### 🔬 **Advanced Physics Simulations**

- **Interactive 2D/3D Visualizations**: Real-time physics simulations with customizable parameters
- **Predefined Physics Models**: Projectile motion, harmonic oscillators, electromagnetic waves, and more
- **Custom Equation Support**: Define and visualize your own mathematical expressions
- **Matter.js Integration**: Realistic physics simulations for collision detection and dynamics
- **Three.js 3D Engine**: Immersive 3D electromagnetic wave visualizations
- **P5.js Creative Coding**: Interactive particle systems and wave animations

### 🧠 **Machine Learning Laboratory**

- **Intelligent Model Recommendations**: AI-powered suggestions based on dataset characteristics
- **Multi-Algorithm Support**: Linear Regression, Random Forest, Gradient Boosting, Neural Networks
- **Real-Time Training Monitoring**: Live progress tracking and performance metrics
- **Model Export/Import**: Save and load trained models with complete reproducibility
- **Deep Learning Pipeline**: TensorFlow/Keras integration for complex neural networks
- **Automated Hyperparameter Tuning**: Optimize model performance automatically

### 📊 **Data Analytics & Visualization**

- **Advanced Plotting Engine**: Matplotlib, Plotly, and Seaborn integration
- **Interactive Dashboards**: Real-time data exploration with Recharts
- **CSV Data Processing**: Upload and analyze experimental datasets
- **Statistical Analysis**: Comprehensive data analysis tools and metrics
- **Export Capabilities**: Generate publication-ready plots and reports

### 🔧 **Developer-Friendly Architecture**

- **Microservices Design**: Modular, scalable backend architecture
- **RESTful API**: Comprehensive API with OpenAPI documentation
- **Real-Time Communication**: WebSocket support for live simulations
- **Docker Containerization**: Easy deployment and scaling
- **Cloud-Ready**: Optimized for AWS, Azure, and Google Cloud deployment

## 🏗️ Project Architecture

```
📦 PhysicsLab/
├── 🎯 backend/                 # Python Backend Services
│   ├── 🤖 ai/                  # AI & Machine Learning Core
│   │   ├── physics_ai.py       # Gemini-powered physics tutor
│   │   ├── embedding_service.py # Vector embeddings for context
│   │   ├── latex_renderer.py   # Mathematical expression rendering
│   │   └── vector_database_integration.py # Qdrant integration
│   ├── 🔬 simulation/          # Physics Simulation Engine
│   │   ├── plot_2d.py         # 2D visualization engine
│   │   ├── plot_3d.py         # 3D surface plotting
│   │   └── run_simulation.py   # Unified simulation controller
│   ├── 🧠 ml/                  # Machine Learning Pipeline
│   │   ├── train_classifier.py # Model training algorithms
│   │   ├── recommend_model.py  # AI model recommendations
│   │   └── deep_learning/      # Neural network implementations
│   ├── 🛣️ routes/              # API Route Definitions
│   │   ├── ai_routes.py       # AI tutor endpoints
│   │   ├── ml_routes.py       # ML training endpoints
│   │   ├── simulation_routes.py # Physics simulation API
│   │   └── physics_advanced_routes.py # Advanced physics features
│   ├── 🗄️ models/              # Data Models & Schemas
│   ├── 🔧 utils/               # Utility Functions & Helpers
│   └── 📊 static/              # Generated plots and assets
├── 🌐 frontend/                # Modern React Frontend
│   ├── 📱 src/app/             # Next.js App Router
│   ├── 🎨 src/components/      # Reusable UI Components
│   │   ├── physics-ai-chat.tsx # AI tutor interface
│   │   ├── simulation/         # Physics simulation components
│   │   ├── ml/                # ML training interfaces
│   │   └── ui/                # Shadcn/ui component library
│   ├── 🪝 src/hooks/           # Custom React hooks
│   ├── 📚 src/lib/             # Utility libraries
│   └── 🎭 src/types/           # TypeScript type definitions
├── 🚢 qdrant-deployment/       # Vector Database Setup
├── 🐳 Dockerfile              # Container configuration
├── ⚙️ gunicorn.conf.py        # Production server config
└── 🚀 start.sh               # Deployment startup script
```

## 🚀 Quick Start Guide

### 🔧 Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm/yarn
- **Docker** (optional, for containerized deployment)
- **Git** for version control

### 🐍 Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/physicslab.git
cd physicslab

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# GEMINI_API_KEY=your_gemini_api_key
# MONGODB_URI=your_mongodb_connection_string
# QDRANT_URL=your_qdrant_instance_url

# Initialize the database
python setup_qdrant_collection.py

# Start the development server
python app.py
```

### ⚛️ Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Configure your environment variables

# Start the development server
npm run dev
```

### 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual containers
docker build -t physicslab-backend .
docker run -p 10000:10000 physicslab-backend
```

## 💡 Usage Examples

### 🤖 AI Physics Tutor

```python
# Ask the AI tutor a physics question
response = await physics_ai.generate_response(
    user_query="Explain quantum tunneling and derive the transmission probability",
    context={"difficulty_level": "advanced", "response_length": "long"},
    sources=["griffiths_quantum", "sakurai_modern_quantum"]
)
```

### 🔬 Physics Simulation

```python
# Create a custom physics simulation
simulation_result = run_simulation({
    'mode': 'equation',
    'equation': 'A * sin(omega * x + phi) * exp(-gamma * x)',
    'x_min': 0,
    'x_max': 10,
    'resolution': 1000,
    'title': 'Damped Wave Propagation'
})
```

### 🧠 Machine Learning Pipeline

```python
# Train a model with intelligent recommendations
model_recommendation = recommend_model(dataset_features)
trained_model = train_classifier(
    data=training_data,
    algorithm=model_recommendation['best_algorithm'],
    hyperparameters=model_recommendation['optimal_params']
)
```

## 🛠️ Advanced Configuration

### 🔑 Environment Variables

```bash
# AI & Machine Learning
GEMINI_API_KEY=your_gemini_2_0_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional alternative

# Database Configuration
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/physicslab
QDRANT_URL=https://your-qdrant-instance.com
QDRANT_API_KEY=your_qdrant_api_key

# External Services
CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret

# Application Settings
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your_secret_key_here
```

### 🎛️ Customization Options

#### Physics Simulation Parameters

- **Resolution**: Control simulation detail (100-10000 points)
- **Time Range**: Set simulation duration and timesteps
- **Visual Styling**: Customize colors, fonts, and layouts
- **Export Formats**: PNG, SVG, PDF, interactive HTML

#### AI Tutor Configuration

- **Model Selection**: Choose between Gemini 2.0 Flash/Pro variants
- **Response Length**: Short explanations vs. detailed derivations
- **Difficulty Adaptation**: Beginner, intermediate, advanced levels
- **Source Prioritization**: Weight different physics textbooks

## 📚 API Documentation

### 🤖 AI Endpoints

```bash
# Chat with physics AI
POST /ai/chat
{
  "question": "What is the Schrödinger equation?",
  "context": {"difficulty": "intermediate"},
  "preferences": {"response_length": "detailed"}
}

# Request physics derivation
POST /ai/derive
{
  "topic": "maxwell_equations",
  "starting_principles": ["gauss_law", "faraday_law"]
}

# Generate physics diagrams
POST /ai/diagram
{
  "description": "Electric field lines around a dipole",
  "style": "educational"
}
```

### 🔬 Simulation Endpoints

```bash
# Run 2D simulation
POST /simulation/2d
{
  "equation": "x**2 + y**2",
  "x_range": [-5, 5],
  "y_range": [-5, 5],
  "resolution": 1000
}

# Upload CSV data for analysis
POST /simulation/csv
Content-Type: multipart/form-data
file: data.csv
x_column: "time"
y_column: "amplitude"
```

### 🧠 ML Endpoints

```bash
# Get model recommendations
POST /ml/recommend
{
  "dataset_info": {
    "samples": 1000,
    "features": 10,
    "task_type": "classification"
  }
}

# Train ML model
POST /ml/train
{
  "algorithm": "random_forest",
  "hyperparameters": {"n_estimators": 100},
  "dataset": "uploaded_file_id"
}
```

## 🧪 Testing & Quality Assurance

### 🔬 Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v --coverage

# Frontend tests
cd frontend
npm test
npm run test:e2e

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### 📊 Performance Monitoring

- **Backend Metrics**: `/api/system/performance`
- **Error Tracking**: `/api/system/errors`
- **Cache Statistics**: `/api/system/cache`
- **Health Checks**: `/health`

## 🚀 Deployment Guide

### ☁️ Cloud Deployment (Recommended)

#### **Render (Free Tier)**

```bash
# Automatic deployment from GitHub
# Configure environment variables in Render dashboard
# Uses provided Dockerfile and start.sh
```

#### **Vercel + Railway**

```bash
# Frontend on Vercel
npm run build
vercel deploy

# Backend on Railway
railway login
railway deploy
```

#### **AWS ECS**

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin
docker build -t physicslab .
docker tag physicslab:latest your-account.dkr.ecr.us-east-1.amazonaws.com/physicslab:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/physicslab:latest
```

### 🔧 Production Optimizations

- **Gunicorn**: Multi-worker WSGI server configuration
- **Redis Caching**: Session and computation result caching
- **CDN Integration**: Static asset delivery optimization
- **Database Indexing**: MongoDB query optimization
- **Vector Search**: Qdrant performance tuning

## 🤝 Contributing

We welcome contributions from the physics and software development community!

### 📋 Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### 🎯 Contribution Areas

- 🧮 **Physics Models**: Add new simulation algorithms
- 🤖 **AI Features**: Enhance the physics tutor capabilities
- 🎨 **UI/UX**: Improve user interface and experience
- 📚 **Documentation**: Expand guides and tutorials
- 🧪 **Testing**: Increase test coverage
- 🌍 **Internationalization**: Add language support

### 📐 Code Standards

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode, proper typing
- **Commits**: Conventional commits format
- **Documentation**: Comprehensive docstrings and comments

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI**: Gemini 2.0 API for advanced physics reasoning
- **Qdrant**: Vector database for semantic search capabilities
- **Shadcn/ui**: Beautiful and accessible UI components
- **Three.js**: 3D visualization and electromagnetic simulations
- **Physics Community**: Inspiration from educational physics resources
---

<div align="center">

**Made with ❤️ by the MaximumCell**

_Advancing physics education through technology_

[![Star on GitHub](https://img.shields.io/github/stars/yourusername/physicslab?style=social)](https://github.com/MaximumCell/physicslab)
</div>
