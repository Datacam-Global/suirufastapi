#!/bin/bash

# Azure Web App deployment script for Python FastAPI
set -e

echo "Starting Azure Web App deployment for FastAPI..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Make sure you're in the project root directory."
    exit 1
fi

# Set environment variables for Azure Web Apps
export PYTHONPATH="/home/site/wwwroot"
export WEBSITE_PYTHON_VERSION="3.12"
export SCM_DO_BUILD_DURING_DEPLOYMENT="true"
export ENABLE_ORYX_BUILD="true"

echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"

# Install dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install --no-cache-dir -r requirements.txt

# Verify critical dependencies
echo "Verifying FastAPI installation..."
python3 -c "import fastapi; print('FastAPI version:', fastapi.__version__)"

echo "Verifying Uvicorn installation..."
python3 -c "import uvicorn; print('Uvicorn version:', uvicorn.__version__)"

# Test application startup (quick test)
echo "Testing application import..."
python3 -c "from app.main import app; print('Application imported successfully')"

echo "Azure deployment preparation completed successfully!"
echo "Application will be available at: https://fastapis.azurewebsites.net"
