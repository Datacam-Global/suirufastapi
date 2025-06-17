#!/bin/bash

# Startup script for Azure Web App
echo "Starting FastAPI application..."

# Set Python path
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Install dependencies if requirements.txt exists and packages are not installed
if [ -f requirements.txt ]; then
    echo "Checking if dependencies are installed..."
    if ! python -c "import uvicorn" 2>/dev/null; then
        echo "Installing requirements..."
        pip install --no-cache-dir -r requirements.txt
    else
        echo "Dependencies already installed."
    fi
fi

# Get the port from Azure environment variable, default to 8000
PORT=${PORT:-8000}

echo "Python version: $(python --version)"
echo "Python path: $(which python)"
echo "Uvicorn version: $(python -c 'import uvicorn; print(uvicorn.__version__)' 2>/dev/null || echo 'Not found')"

# Start the FastAPI application
echo "Starting uvicorn server on port $PORT..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
