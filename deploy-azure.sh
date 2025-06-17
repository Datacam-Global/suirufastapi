#!/bin/bash

# Azure Container Instance Deployment Script
# Make sure you have Azure CLI installed and are logged in

# Configuration variables
RESOURCE_GROUP="content-analysis-rg"
CONTAINER_NAME="content-analysis-api"
LOCATION="eastus"
IMAGE_NAME="content-analysis-fastapi"
REGISTRY_NAME="contentanalysisacr"
DNS_NAME_LABEL="content-analysis-api-$(date +%s)"

echo "Starting Azure Container Instance deployment..."

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP \
    --name $REGISTRY_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Login to ACR
echo "Logging into Azure Container Registry..."
az acr login --name $REGISTRY_NAME

# Build and push Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:latest .

echo "Tagging image for ACR..."
docker tag $IMAGE_NAME:latest $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

echo "Pushing image to ACR..."
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "passwords[0].value" --output tsv)

# Deploy to Azure Container Instances
echo "Deploying to Azure Container Instances..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label $DNS_NAME_LABEL \
    --ports 8000 \
    --cpu 2 \
    --memory 4 \
    --environment-variables PYTHONUNBUFFERED=1 \
    --restart-policy Always

# Get the FQDN
FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.fqdn" --output tsv)

echo "Deployment completed!"
echo "Your API is available at: http://$FQDN:8000"
echo "API Documentation: http://$FQDN:8000/docs"
echo "Health Check: http://$FQDN:8000/health"

# Show container logs
echo "Container logs:"
az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME
