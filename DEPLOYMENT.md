# PhysicsLab Backend Deployment

This repository contains the backend for the PhysicsLab application, optimized for deployment on Render free tier.

## 🚀 Deployment to Render

### Prerequisites

- Render account
- Environment variables configured

### Required Environment Variables

Set these in your Render service configuration:

```bash
# Required for AI features
GEMINI_API_KEY=your_gemini_api_key_here

# Required for database
MONGODB_URI=your_mongodb_connection_string

# Optional - for vector search
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key

# Optional - for file uploads
CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

### Deploy Steps

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use the following settings:
   - **Environment**: Docker
   - **Build Command**: (leave empty - handled by Dockerfile)
   - **Start Command**: (leave empty - handled by Dockerfile)
   - **Plan**: Free
4. Add environment variables in the Render dashboard
5. Deploy!

## 🔧 Local Development

### Setup

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run the application
python app.py
```

### Docker Development

```bash
# Build the container
docker build -t physicslab-backend .

# Run locally
docker run -p 10000:10000 --env-file .env physicslab-backend
```

## 📊 Health Check

Once deployed, you can check the health of your service:

- Health endpoint: `https://your-service-url.onrender.com/health`
- Error stats: `https://your-service-url.onrender.com/api/system/errors`
- Performance stats: `https://your-service-url.onrender.com/api/system/performance`

## 🐛 Troubleshooting

### Common Issues

1. **Module Import Errors**

   - Check that all dependencies are in `requirements-prod.txt`
   - Verify environment variables are set correctly

2. **Timeout Errors**

   - Render free tier has a 60-second request timeout
   - Large AI requests may need optimization

3. **Memory Issues**

   - Free tier has 512MB RAM limit
   - Monitor memory usage and optimize if needed

4. **Database Connection Issues**
   - Verify MongoDB URI is correct
   - Check network connectivity

### Logs

- View logs in Render dashboard
- Health check: `/health`
- Error statistics: `/api/system/errors`

## 📁 Project Structure

```
backend/
├── app.py                  # Main Flask application
├── requirements-prod.txt   # Production dependencies
├── gunicorn.conf.py       # Gunicorn configuration
├── start.sh              # Startup script
├── routes/               # API route blueprints
├── ai/                   # AI and ML modules
├── utils/                # Utility functions
└── models/              # Data models
```

## 🔒 Security Notes

- Never commit sensitive environment variables
- Use environment variables for all secrets
- The application runs as non-root user in container
- CORS is configured for production use
