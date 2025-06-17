#!/bin/bash

# Manual Azure Web App Deployment Script
# Use this script as a workaround while setting up GitHub Actions secrets

set -e

echo "🚀 Starting manual Azure Web App deployment for FastAPI..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Installing..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please login to Azure..."
    az login
fi

# Set variables
APP_NAME="fastapis"
RESOURCE_GROUP="your-resource-group"  # Update this with your actual resource group
LOCATION="East US"  # Update this with your preferred location
RUNTIME="PYTHON:3.12"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Make sure you're in the project root directory."
    exit 1
fi

if [ ! -f "app/main.py" ]; then
    echo "❌ Error: app/main.py not found. Make sure you're in the project root directory."
    exit 1
fi

echo "📦 Current directory: $(pwd)"
echo "🔍 Checking application files..."
ls -la app/

echo "🔧 Installing dependencies locally to verify..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Testing application import..."
python -c "from app.main import app; print('✅ Application imported successfully')"

echo "☁️ Deploying to Azure Web App..."
echo "   App Name: $APP_NAME"
echo "   Runtime: $RUNTIME"

# Deploy using Azure CLI
az webapp up \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --runtime $RUNTIME \
    --sku B1 \
    --logs

echo "🔧 Configuring application settings..."

# Set application settings for optimal performance
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true \
    WEBSITE_PYTHON_VERSION=3.12 \
    PYTHONPATH=/home/site/wwwroot \
    WEBSITE_STARTUP_FILE=startup.sh

echo "📝 Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.sh"

echo "🔄 Restarting the web app..."
az webapp restart \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME

echo "✅ Deployment completed!"
echo "🌐 Your application should be available at: https://$APP_NAME.azurewebsites.net"
echo "📊 You can view logs at: https://$APP_NAME.scm.azurewebsites.net/api/logstream"

echo "🧪 Testing the deployment..."
sleep 10
if curl -f "https://$APP_NAME.azurewebsites.net" > /dev/null 2>&1; then
    echo "✅ Application is responding!"
else
    echo "⚠️  Application might still be starting up. Check the logs if it doesn't respond in a few minutes."
fi

echo "📋 To check logs, run:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"

echo "🔧 To update settings, run:"
echo "   az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings KEY=VALUE"
