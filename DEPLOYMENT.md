# Azure Container Instances Deployment Guide

This guide will help you deploy your FastAPI Content Analysis application to Azure Container Instances using Docker Hub and GitHub Actions for automated CI/CD.

## Prerequisites

1. **Azure CLI**: Install and login to Azure CLI
   ```bash
   # Install Azure CLI (if not already installed)
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Login to Azure
   az login
   ```

2. **Docker Hub Account**: Create an account at [hub.docker.com](https://hub.docker.com)

3. **GitHub Repository**: Your code should be in a GitHub repository

4. **Docker Hub Access Token**: Create a personal access token in Docker Hub
   - Go to Account Settings → Security → New Access Token
   - Name it "GitHub Actions" and save the token

## Setup GitHub Actions CI/CD

### Step 1: Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `DOCKER_HUB_USERNAME`: Your Docker Hub username
- `DOCKER_HUB_ACCESS_TOKEN`: The access token you created

### Step 2: Update Workflow Configuration

Edit `.github/workflows/docker-build-push.yml` and update the `DOCKER_HUB_REPOSITORY` variable:

```yaml
env:
  DOCKER_HUB_REPOSITORY: your-dockerhub-username/content-analysis-fastapi
```

Replace `your-dockerhub-username` with your actual Docker Hub username.

### Step 3: Push to GitHub

When you push to the `main` or `master` branch, GitHub Actions will automatically:
- Build your Docker image
- Push it to Docker Hub with tags: `latest`, branch name, and commit SHA
- Support multi-platform builds (AMD64 and ARM64)

## Deployment Options

### Option 1: Automated Deployment with Docker Hub (Recommended)

The easiest way to deploy is using the Docker Hub deployment script after setting up GitHub Actions:

```bash
./deploy-dockerhub.sh
```

This script will:
- Create a resource group
- Deploy the container from your Docker Hub repository to Azure Container Instances
- Provide you with the public URL

**Prerequisites**: Your Docker image should already be built and pushed to Docker Hub via GitHub Actions

### Option 2: Manual Docker Hub Deployment

If you prefer manual control:

```bash
# Update the script with your Docker Hub image name
./deploy-dockerhub.sh

# Or deploy directly with Azure CLI
az container create \
    --resource-group content-analysis-rg \
    --name content-analysis-api \
    --image your-dockerhub-username/content-analysis-fastapi:latest \
    --dns-name-label content-analysis-api-$(date +%s) \
    --ports 8000 \
    --cpu 2 \
    --memory 4 \
    --environment-variables PYTHONUNBUFFERED=1 \
    --restart-policy Always
```

### Option 3: Legacy ACR Deployment

If you prefer to use Azure Container Registry (more complex but more secure):

```bash
./deploy-azure.sh
```

#### Step 1: Create Azure Resources

```bash
# Create resource group
az group create --name content-analysis-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group content-analysis-rg \
    --name contentanalysisacr \
    --sku Basic \
    --admin-enabled true
```

#### Step 2: Build and Push Docker Image

```bash
# Login to ACR
az acr login --name contentanalysisacr

# Build image
docker build -t content-analysis-fastapi:latest .

# Tag for ACR
docker tag content-analysis-fastapi:latest contentanalysisacr.azurecr.io/content-analysis-fastapi:latest

# Push to ACR
docker push contentanalysisacr.azurecr.io/content-analysis-fastapi:latest
```

#### Step 3: Deploy to Container Instances

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name contentanalysisacr --resource-group content-analysis-rg --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name contentanalysisacr --resource-group content-analysis-rg --query "passwords[0].value" --output tsv)

# Deploy container
az container create \
    --resource-group content-analysis-rg \
    --name content-analysis-api \
    --image contentanalysisacr.azurecr.io/content-analysis-fastapi:latest \
    --registry-login-server contentanalysisacr.azurecr.io \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label content-analysis-api-$(date +%s) \
    --ports 8000 \
    --cpu 2 \
    --memory 4 \
    --environment-variables PYTHONUNBUFFERED=1 \
    --restart-policy Always
```

### Option 4: Using ARM Template

Use the provided ARM template for Infrastructure as Code:

```bash
./deploy-template.sh
```

## Local Testing

Before deploying to Azure, test your container locally:

```bash
# Using Docker directly
docker build -t content-analysis-fastapi:latest .
docker run -p 8000:8000 content-analysis-fastapi:latest

# Using Docker Compose
docker-compose up --build
```

Visit `http://localhost:8000/docs` to see the API documentation.

## Monitoring and Management

### Check Deployment Status

```bash
az container show --resource-group content-analysis-rg --name content-analysis-api
```

### View Container Logs

```bash
az container logs --resource-group content-analysis-rg --name content-analysis-api --follow
```

### Get Public URL

```bash
az container show --resource-group content-analysis-rg --name content-analysis-api --query "ipAddress.fqdn" --output tsv
```

### Restart Container

```bash
az container restart --resource-group content-analysis-rg --name content-analysis-api
```

## API Endpoints

Once deployed, your API will be available at:

- **Root**: `http://<your-fqdn>:8000/`
- **API Documentation**: `http://<your-fqdn>:8000/docs`
- **Health Check**: `http://<your-fqdn>:8000/health`
- **Hate Speech Analysis**: `http://<your-fqdn>:8000/hate-speech/analyze`
- **Misinformation Analysis**: `http://<your-fqdn>:8000/misinformation/analyze`
- **General Content Analysis**: `http://<your-fqdn>:8000/content/analyze`

## Configuration

### Environment Variables

You can set additional environment variables during deployment:

```bash
--environment-variables KEY1=value1 KEY2=value2
```

### Resource Scaling

Adjust CPU and memory based on your needs:

```bash
--cpu 1-4     # CPU cores
--memory 1-16 # Memory in GB
```

### Custom Domain (Optional)

To use a custom domain, you'll need to:
1. Configure Azure DNS or your DNS provider
2. Point your domain to the container's public IP
3. Consider using Azure Application Gateway for SSL termination

## Cost Optimization

- **CPU/Memory**: Start with smaller resources (1 CPU, 2GB RAM) and scale up if needed
- **Auto-shutdown**: Consider using Azure Automation to stop containers during off-hours
- **Monitoring**: Use Azure Monitor to track usage and optimize resources

## Troubleshooting

### Common Issues

1. **Image Pull Errors**: Ensure ACR credentials are correct
2. **Port Issues**: Make sure port 8000 is exposed and accessible
3. **Memory Issues**: Increase memory allocation if the app crashes
4. **Model Loading**: Ensure model files are included in the Docker image

### Debug Commands

```bash
# Check container status
az container show --resource-group content-analysis-rg --name content-analysis-api --query "instanceView.state"

# Get detailed logs
az container logs --resource-group content-analysis-rg --name content-analysis-api

# Execute commands in running container
az container exec --resource-group content-analysis-rg --name content-analysis-api --exec-command "/bin/bash"
```

## Cleanup

To remove all created resources:

```bash
az group delete --name content-analysis-rg --yes --no-wait
```

## Security Considerations

1. **Network Security**: Consider using virtual networks for internal communication
2. **Secrets Management**: Use Azure Key Vault for sensitive configuration
3. **Authentication**: Implement API keys or OAuth for production use
4. **HTTPS**: Use Azure Application Gateway or Azure Front Door for SSL termination
5. **Container Security**: Regularly update base images and scan for vulnerabilities
