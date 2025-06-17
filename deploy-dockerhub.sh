#!/bin/bash

# Azure Container Instances Deployment Script using Docker Hub
# This script deploys your FastAPI application to Azure Container Instances using Docker Hub

set -e

# Configuration
RESOURCE_GROUP="content-analysis-rg"
LOCATION="eastus"
CONTAINER_NAME="content-analysis-api"
DOCKER_HUB_IMAGE="nyuydinebill/content-analysis-fastapi"  # Update this with your Docker Hub username
IMAGE_TAG="latest"
DNS_NAME_LABEL="content-analysis-api-$(date +%s)"

echo "🚀 Starting Azure Container Instances deployment using Docker Hub..."

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

# Prompt for Docker Hub image name if not updated
if [[ "$DOCKER_HUB_IMAGE" == "nyuydinebill/content-analysis-fastapi" ]]; then
    echo "⚠️  Please update the DOCKER_HUB_IMAGE variable in this script with your Docker Hub repository."
    read -p "Enter your Docker Hub image (e.g., username/content-analysis-fastapi): " DOCKER_HUB_IMAGE
fi

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy to Azure Container Instances
echo "🚀 Deploying to Azure Container Instances..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $DOCKER_HUB_IMAGE:$IMAGE_TAG \
    --dns-name-label $DNS_NAME_LABEL \
    --ports 8000 \
    --cpu 2 \
    --memory 4 \
    --environment-variables PYTHONUNBUFFERED=1 \
    --restart-policy Always

# Get the FQDN
echo "⏳ Getting container information..."
FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.fqdn" --output tsv)

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your API is available at:"
echo "   Main URL: http://$FQDN:8000"
echo "   API Documentation: http://$FQDN:8000/docs"
echo "   Health Check: http://$FQDN:8000/health"
echo ""

# Show container status
echo "📊 Container Status:"
az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "instanceView.state" --output tsv

# Show container logs
echo ""
echo "📝 Recent Container Logs:"
az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --tail 50

echo ""
echo "💡 Useful commands:"
echo "   View logs: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --follow"
echo "   Restart: az container restart --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo "   Delete: az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes"
echo "   Cleanup all: az group delete --name $RESOURCE_GROUP --yes --no-wait"
