#!/bin/bash

# Startup script for Azure Web App
echo "Starting FastAPI application..."

# Install dependencies if needed
if [ -f requirements.txt ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Get the port from Azure environment variable, default to 8000
PORT=${PORT:-8000}

# Start the FastAPI application
echo "Starting uvicorn server on port $PORT..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
