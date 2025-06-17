#!/bin/bash

# Azure App Service startup script for FastAPI
echo "========================================"
echo "Starting FastAPI Content Analysis API"
echo "========================================"

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Check Python version and location
echo "Python version: $(python --version)"
echo "Python location: $(which python)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Ensure pip is up to date
echo "Updating pip..."
python -m pip install --upgrade pip --user

# Install dependencies with verbose output
echo "Installing Python dependencies..."
python -m pip install -r requirements.txt --user --no-cache-dir -v

# Verify uvicorn installation
echo "Checking uvicorn installation..."
python -c "import uvicorn; print('✓ uvicorn available at:', uvicorn.__file__)" || echo "❌ uvicorn not found"

# Download NLTK data
echo "Downloading NLTK data..."
python -c "
import nltk
import os
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True) 
    nltk.download('vader_lexicon', quiet=True)
    print('✓ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠ Warning: NLTK download failed: {e}')
"

# Check if required model files exist
echo "Checking for model files..."
if [ -f "twitter_hate_model.joblib" ]; then
    echo "✓ twitter_hate_model.joblib found"
else
    echo "⚠ Warning: twitter_hate_model.joblib not found"
fi

if [ -f "twitter_hate_vectorizer.joblib" ]; then
    echo "✓ twitter_hate_vectorizer.joblib found"
else
    echo "⚠ Warning: twitter_hate_vectorizer.joblib not found"
fi

# Get the port from environment variable
PORT=${PORT:-8000}
echo "Starting server on port: $PORT"

# Start the FastAPI application
echo "========================================"
echo "Launching uvicorn server..."
echo "========================================"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info
