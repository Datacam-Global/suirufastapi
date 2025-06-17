#!/bin/bash

# Simple startup script for Azure Web App
echo "Starting FastAPI application..."

# Get the port from Azure environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting uvicorn server on port $PORT..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
