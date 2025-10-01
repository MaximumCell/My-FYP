# Quick Qdrant Deployment Guide

## Deploy Vector Database to Render Free Tier in 5 Minutes

---

## 🚀 **Step 1: Deploy Qdrant to Render**

### **Method A: Direct GitHub Deployment (Recommended)**

1. **Create a new repository** (or use a folder in existing repo):

   ```bash
   # In your project root
   mkdir qdrant-render
   cd qdrant-render
   ```

2. **Create Dockerfile** (copy from `/qdrant-deployment/Dockerfile`):

   ```dockerfile
   FROM qdrant/qdrant:latest
   EXPOSE 6333
   ENV QDRANT__SERVICE__HTTP_PORT=6333
   ENV QDRANT__SERVICE__HOST=0.0.0.0
   ENV QDRANT__SERVICE__ENABLE_CORS=true
   CMD ["./qdrant"]
   ```

3. **Deploy on Render**:

   - Go to https://render.com (sign up/login)
   - Click "New" → "Web Service"
   - Connect GitHub → Select repository
   - Settings:
     - **Runtime**: Docker
     - **Plan**: Free (512MB RAM)
     - **Port**: 6333
     - **Build Command**: (leave empty)
     - **Start Command**: (leave empty)

4. **Get your Qdrant URL**:
   - After deployment: `https://your-service-name.onrender.com`

---

## 🔧 **Step 2: Install Minimal Dependencies**

You only need ONE additional package for Qdrant:

```bash
# In your backend directory
pip install httpx
```

That's it! No heavy ML libraries needed.

---

## ⚙️ **Step 3: Configure Environment**

Add to your `/backend/.env`:

```env
# Qdrant Configuration
QDRANT_URL=https://your-qdrant-service.onrender.com
QDRANT_API_KEY=  # Optional, leave empty for free deployment

# Keep your existing MongoDB settings
MONGODB_URI=mongodb+srv://...
DB_NAME=physicslab
```

---

## 🧪 **Step 4: Test Your Deployment**

1. **Quick test script**:

   ```python
   import asyncio
   import httpx
   import os

   async def test_qdrant():
       qdrant_url = "https://your-qdrant-service.onrender.com"

       async with httpx.AsyncClient() as client:
           # Test health
           response = await client.get(f"{qdrant_url}/")
           print(f"Health: {response.status_code}")

           # Create collection
           response = await client.put(
               f"{qdrant_url}/collections/test",
               json={"vectors": {"size": 384, "distance": "Cosine"}}
           )
           print(f"Collection created: {response.status_code}")

   asyncio.run(test_qdrant())
   ```

2. **Run the test**:

   ```bash
   cd /home/itz_sensei/Documents/FypProject/backend
   python -c "
   import asyncio
   import httpx

   async def test():
       url = 'https://your-qdrant-service.onrender.com'
       async with httpx.AsyncClient() as client:
           resp = await client.get(f'{url}/')
           print(f'Qdrant Status: {resp.status_code}')

   asyncio.run(test())
   "
   ```

---

## 📋 **Step 5: Use in Your Physics AI**

Simple integration in your existing code:

```python
from qdrant_client import QdrantClient

# Initialize
qdrant = QdrantClient(
    url="https://your-qdrant-service.onrender.com",
    port=None  # Use URL port
)

# Create physics collection
qdrant.recreate_collection(
    collection_name="physics_knowledge",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Add physics content (with embeddings from any source)
qdrant.upsert(
    collection_name="physics_knowledge",
    points=[
        PointStruct(
            id=1,
            vector=[0.1, 0.2, ...],  # Your embedding
            payload={"title": "Newton's Law", "topic": "mechanics"}
        )
    ]
)

# Search
results = qdrant.search(
    collection_name="physics_knowledge",
    query_vector=[0.1, 0.2, ...],  # Query embedding
    limit=5
)
```

---

## 💡 **Key Advantages**

✅ **No MongoDB upgrade needed** - Keep your free M0 tier  
✅ **No heavy ML dependencies** - Just HTTP requests  
✅ **Free deployment** - Render free tier  
✅ **Production ready** - Easy to scale later  
✅ **Simple integration** - REST API

---

## 🔄 **Architecture Overview**

```
Physics AI Query
      ↓
Generate Embedding (local/API)
      ↓
Search Qdrant (Render)
      ↓
Get Metadata from MongoDB (M0)
      ↓
Return Combined Results
```

**Cost**: $0/month (Qdrant on Render Free + MongoDB M0 Free)

---

## 🚨 **If Deployment Fails**

### **Common Issues & Fixes**

1. **Render deployment timeout**:

   - Use smaller Docker image
   - Check logs in Render dashboard

2. **Port issues**:

   - Ensure PORT 6333 is exposed
   - Check environment variables

3. **CORS issues**:
   - Ensure `QDRANT__SERVICE__ENABLE_CORS=true`

### **Alternative: Railway Deployment**

If Render doesn't work, try Railway:

```dockerfile
# Same Dockerfile works on Railway
FROM qdrant/qdrant:latest
EXPOSE 6333
ENV QDRANT__SERVICE__HTTP_PORT=6333
ENV QDRANT__SERVICE__HOST=0.0.0.0
CMD ["./qdrant"]
```

Deploy: Connect GitHub → Deploy → Get URL

---

## 🎯 **Next Steps**

1. ✅ Deploy Qdrant to Render
2. ✅ Test with simple HTTP requests
3. ✅ Update your `.env` with Qdrant URL
4. ✅ Use `qdrant_client.py` for physics content
5. ✅ Keep MongoDB for user data and metadata

**Ready to deploy? Let's get your Qdrant service running!**
