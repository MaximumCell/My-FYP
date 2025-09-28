# Qdrant Vector Database Deployment
FROM qdrant/qdrant:latest

# Expose the default Qdrant ports
EXPOSE 6333
EXPOSE 6334

# Set environment variables for Render deployment
ENV QDRANT__SERVICE__HTTP_PORT=6333
ENV QDRANT__SERVICE__GRPC_PORT=6334
ENV QDRANT__SERVICE__HOST=0.0.0.0

# Configure storage (Render provides persistent storage)
ENV QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage

# Enable CORS for web access
ENV QDRANT__SERVICE__ENABLE_CORS=true

# Set log level
ENV QDRANT__LOG_LEVEL=INFO

# Create storage directory
RUN mkdir -p /qdrant/storage

# Start Qdrant
CMD ["./qdrant"]