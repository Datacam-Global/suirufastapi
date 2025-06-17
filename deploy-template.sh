#!/bin/bash

# Simple Azure deployment using ARM template
# This script assumes you have already built and pushed your image to ACR

# Configuration
RESOURCE_GROUP="content-analysis-rg"
CONTAINER_NAME="content-analysis-api"
LOCATION="eastus"
DNS_NAME_LABEL="content-analysis-$(date +%s)"
REGISTRY_NAME="contentanalysisacr"

echo "Deploying using ARM template..."

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "passwords[0].value" --output tsv)

# Deploy using ARM template
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-template.json \
    --parameters \
        containerName=$CONTAINER_NAME \
        dnsNameLabel=$DNS_NAME_LABEL \
        registryUsername=$ACR_USERNAME \
        registryPassword=$ACR_PASSWORD

echo "Deployment completed!"
echo "Check the deployment status in the Azure portal or run:"
echo "az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
