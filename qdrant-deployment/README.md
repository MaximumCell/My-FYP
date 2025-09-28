# Qdrant Vector Database on Render

## Simple Vector Search for Physics AI Tutor

This service provides vector search capabilities using Qdrant deployed on Render's free tier.

## Features

- ✅ Free deployment (Render free tier)
- ✅ Persistent vector storage
- ✅ REST API for easy integration
- ✅ CORS enabled for web access
- ✅ No complex dependencies

## Quick Deploy to Render

1. **Create GitHub Repository** for this Qdrant deployment:

   ```bash
   git add .
   git commit -m "Add Qdrant deployment for Render"
   git push origin main
   ```

2. **Deploy on Render**:

   - Go to https://render.com/
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Choose this directory: `/qdrant-deployment`
   - Runtime: Docker
   - Plan: Free (512MB RAM, sufficient for development)

3. **Configuration**:
   - Build Command: (leave empty, uses Dockerfile)
   - Start Command: (leave empty, uses Dockerfile CMD)
   - Port: 6333
   - Environment: (no additional variables needed)

## Usage

Once deployed, you'll get a URL like: `https://your-qdrant-service.onrender.com`

### Create Collection

```bash
curl -X PUT "https://your-qdrant-service.onrender.com/collections/physics_knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'
```

### Add Vector

```bash
curl -X PUT "https://your-qdrant-service.onrender.com/collections/physics_knowledge/points" \
  -H "Content-Type: application/json" \
  -d '{
    "points": [
      {
        "id": 1,
        "vector": [0.1, 0.2, 0.3, ...],
        "payload": {
          "title": "Newton's First Law",
          "topic": "mechanics",
          "content": "An object at rest stays at rest..."
        }
      }
    ]
  }'
```

### Search Vectors

```bash
curl -X POST "https://your-qdrant-service.onrender.com/collections/physics_knowledge/points/search" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3, ...],
    "limit": 5,
    "with_payload": true
  }'
```

## Integration with Physics AI

Your backend will connect to this Qdrant instance for vector operations while using MongoDB for metadata.

## Render Free Tier Limits

- 512MB RAM
- 1 CPU
- Sleeps after 15 minutes of inactivity
- 750 hours/month (enough for development)
- Persistent disk storage included

## Cost

- **Development**: $0/month (Render free tier)
- **Production**: $7/month (Render Starter plan for always-on service)
