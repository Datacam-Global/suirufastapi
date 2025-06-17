#!/bin/bash

# Azure App Service Deployment Script
echo "🚀 Preparing FastAPI app for Azure deployment..."

# Check if required files exist
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

if [ ! -f "app/main.py" ]; then
    echo "❌ app/main.py not found!"
    exit 1
fi

# Clean up unnecessary files
echo "🧹 Cleaning up unnecessary files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache .coverage htmlcov

# Create deployment package
echo "📦 Creating deployment package..."
zip -r deployment.zip . \
    -x "*.git*" \
    -x "*.vscode*" \
    -x "*.idea*" \
    -x "*.DS_Store*" \
    -x "docker-compose*.yml" \
    -x "*.md" \
    -x "deployment.zip"

echo "✅ Deployment package created: deployment.zip"
echo "📋 Next steps:"
echo "1. Upload deployment.zip to Azure App Service"
echo "2. Or use NEW Azure CLI command: az webapp deploy --resource-group sui-ru --name fastapis --src-path deployment.zip --type zip"
echo "3. Monitor deployment logs in Azure Portal"
echo "4. Test the health endpoint: /health"
echo ""
echo "🔧 Deployment command (copy and run):"
echo "az webapp deploy --resource-group sui-ru --name fastapis --src-path deployment.zip --type zip"

# Exit on any error
set -e

echo "Starting deployment..."

# Create virtual environment
python3.12 -m venv antenv

# Activate virtual environment
source antenv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies with verbose output and timeout
pip install -r requirements.txt --timeout=300 --verbose

echo "Deployment completed successfully"
