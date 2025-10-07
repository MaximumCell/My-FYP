#!/bin/bash

# Render deployment startup script for PhysicsLab Backend
# This script ensures proper environment setup and graceful error handling

set -e

echo "🚀 Starting PhysicsLab Backend..."

# Set default environment variables if not provided
export PYTHONPATH="${PYTHONPATH:-/app}"
export FLASK_APP="${FLASK_APP:-backend.app:app}"
export FLASK_ENV="${FLASK_ENV:-production}"

# Create necessary directories if they don't exist
mkdir -p /app/logs 2>/dev/null || true
mkdir -p /app/temp 2>/dev/null || true

# Set permissions (only if we have write access)
chmod -R 755 /app/backend 2>/dev/null || true
chmod -R 755 /app/logs 2>/dev/null || true

echo "📁 Directory structure set up"

# Check if critical environment variables are set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ Warning: GEMINI_API_KEY not set. AI features may be limited."
fi

if [ -z "$MONGODB_URI" ]; then
    echo "⚠️ Warning: MONGODB_URI not set. Database features may be limited."
fi

echo "🔍 Environment check complete"

# Test Python imports
echo "🐍 Testing Python dependencies..."
python -c "
import sys
print(f'Python version: {sys.version}')

# Test critical imports
try:
    import flask
    print('✅ Flask imported successfully')
except ImportError as e:
    print(f'❌ Flask import failed: {e}')
    sys.exit(1)

try:
    import pymongo
    print('✅ PyMongo imported successfully')
except ImportError as e:
    print(f'⚠️ PyMongo import failed: {e}')

try:
    import langchain
    print('✅ LangChain imported successfully')
except ImportError as e:
    print(f'⚠️ LangChain import failed: {e}')

try:
    import google.generativeai
    print('✅ Google GenAI imported successfully')
except ImportError as e:
    print(f'⚠️ Google GenAI import failed: {e}')

print('🔧 Import test complete')
"

# Start the application with gunicorn
echo "🌟 Starting Gunicorn server..."
exec gunicorn --config gunicorn.conf.py backend.app:app