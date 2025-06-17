#!/bin/bash

# Azure Web App Deployment Script for FastAPI
# This script deploys your FastAPI application to Azure Web App

set -e

# Configuration
RESOURCE_GROUP="content-analysis-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="content-analysis-plan"
WEB_APP_NAME="content-analysis-api-$(date +%s)"
RUNTIME="PYTHON|3.12"

echo "🚀 Starting Azure Web App deployment..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "❌ Please login to Azure first:"
    echo "az login"
    exit 1
fi

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service Plan (Linux, Free tier)
echo "🏗️  Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku F1 \
    --is-linux

# Create Web App
echo "🌐 Creating Web App..."
az webapp create \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime $RUNTIME

# Configure startup command
echo "⚙️  Configuring startup command..."
az webapp config set \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Set environment variables
echo "🔧 Setting environment variables..."
az webapp config appsettings set \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
    PYTHONUNBUFFERED=1 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true

# Deploy from local Git
echo "📤 Setting up deployment from local directory..."
az webapp deployment source config-local-git \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP

# Get deployment credentials
echo "🔑 Getting deployment credentials..."
DEPLOYMENT_USERNAME=$(az webapp deployment list-publishing-credentials --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --query "publishingUserName" --output tsv)
DEPLOYMENT_PASSWORD=$(az webapp deployment list-publishing-credentials --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --query "publishingPassword" --output tsv)

# Get Git URL
GIT_URL=$(az webapp deployment source show --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --query "repoUrl" --output tsv)

echo "✅ Web App created successfully!"
echo ""
echo "🌐 Your API will be available at:"
echo "   https://$WEB_APP_NAME.azurewebsites.net"
echo "   API Documentation: https://$WEB_APP_NAME.azurewebsites.net/docs"
echo "   Health Check: https://$WEB_APP_NAME.azurewebsites.net/health"
echo ""
echo "📤 To deploy your code:"
echo "   git remote add azure $GIT_URL"
echo "   git push azure main"
echo ""
echo "🔐 Deployment credentials:"
echo "   Username: $DEPLOYMENT_USERNAME"
echo "   Password: $DEPLOYMENT_PASSWORD"
echo ""
echo "💡 Useful commands:"
echo "   View logs: az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
echo "   Restart: az webapp restart --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
echo "   Delete: az webapp delete --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
echo "   Cleanup all: az group delete --name $RESOURCE_GROUP --yes --no-wait"
