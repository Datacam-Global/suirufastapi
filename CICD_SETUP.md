# GitHub Actions CI/CD Setup Guide

This guide will help you set up automated Docker builds and Azure deployments using GitHub Actions and Docker Hub.

## 🚀 Quick Start

1. **Fork/Clone this repository** to your GitHub account

2. **Create Docker Hub repository**:
   - Go to [hub.docker.com](https://hub.docker.com)
   - Create a new repository named `content-analysis-fastapi` (or your preferred name)

3. **Configure GitHub Secrets**:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `DOCKER_HUB_USERNAME`: Your Docker Hub username
     - `DOCKER_HUB_ACCESS_TOKEN`: Your Docker Hub access token

4. **Update configuration**:
   - Edit `.github/workflows/docker-build-push.yml`
   - Change `your-dockerhub-username` to your actual Docker Hub username
   - Edit `deploy-dockerhub.sh` and update the `DOCKER_HUB_IMAGE` variable

5. **Push to main branch** - GitHub Actions will automatically build and push your Docker image

6. **Deploy to Azure**:
   ```bash
   ./deploy-dockerhub.sh
   ```

## 📋 Detailed Setup

### Step 1: Docker Hub Setup

1. **Create Docker Hub Account**: Sign up at [hub.docker.com](https://hub.docker.com)

2. **Create Repository**:
   - Click "Create Repository"
   - Name: `content-analysis-fastapi` (or your choice)
   - Visibility: Public (free) or Private (paid)

3. **Create Access Token**:
   - Go to Account Settings → Security
   - Click "New Access Token"
   - Name: "GitHub Actions"
   - Permissions: Read, Write, Delete
   - **Save the token securely** - you won't see it again!

### Step 2: GitHub Repository Setup

1. **Add Repository Secrets**:
   ```
   Repository → Settings → Secrets and variables → Actions → New repository secret
   ```
   
   Add these secrets:
   - **Name**: `DOCKER_HUB_USERNAME`
     **Value**: Your Docker Hub username
   
   - **Name**: `DOCKER_HUB_ACCESS_TOKEN`
     **Value**: The access token you created

2. **Update Workflow File**:
   Edit `.github/workflows/docker-build-push.yml`:
   ```yaml
   env:
     DOCKER_HUB_REPOSITORY: nyuydinebill/content-analysis-fastapi
   ```

### Step 3: Update Deployment Script

Edit `deploy-dockerhub.sh` and change:
```bash
DOCKER_HUB_IMAGE="your-dockerhub-username/content-analysis-fastapi"
```
to:
```bash
DOCKER_HUB_IMAGE="nyuydinebill/content-analysis-fastapi"
```

### Step 4: Test the Pipeline

1. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Setup CI/CD pipeline"
   git push origin main
   ```

2. **Monitor GitHub Actions**:
   - Go to your repository → Actions tab
   - Watch the build process
   - Check for any errors

3. **Verify Docker Hub**:
   - Check your Docker Hub repository
   - Confirm the image was pushed with tags: `latest`, `main-<sha>`

## 🔄 Workflow Explained

### When Does It Run?
- **Push to main/master branch**: Builds and pushes with `latest` tag
- **Push to other branches**: Builds and pushes with branch name tag
- **Pull Requests**: Builds but doesn't push (security)

### What Tags Are Created?
- `latest`: For main/master branch pushes
- `main-a1b2c3d`: Branch name + commit SHA
- `feature-auth-a1b2c3d`: Feature branch + commit SHA

### Multi-Platform Support
The workflow builds for both:
- `linux/amd64` (Intel/AMD processors)
- `linux/arm64` (ARM processors, Apple Silicon)

## 🚀 Deployment Workflow

### Automated Deployment
1. **Code Change** → Push to GitHub
2. **GitHub Actions** → Build & Push to Docker Hub
3. **Manual Deploy** → Run `./deploy-dockerhub.sh`
4. **Azure Container Instances** → Pull from Docker Hub

### Manual Deployment Steps
```bash
# Ensure you're logged into Azure
az login

# Deploy using the script
./deploy-dockerhub.sh

# Or deploy manually
az container create \
    --resource-group content-analysis-rg \
    --name content-analysis-api \
    --image nyuydinebill/content-analysis-fastapi:latest \
    --dns-name-label content-analysis-api-$(date +%s) \
    --ports 8000 \
    --cpu 2 \
    --memory 4
```

## 🔧 Troubleshooting

### Common Issues

1. **Build Fails - Docker Hub Login**:
   - Check if `DOCKER_HUB_USERNAME` and `DOCKER_HUB_ACCESS_TOKEN` are set correctly
   - Verify the access token has Read/Write permissions

2. **Image Not Found During Deployment**:
   - Ensure the Docker Hub repository name matches in both workflow and deployment script
   - Check if the image was actually pushed to Docker Hub

3. **Azure Deployment Fails**:
   - Verify you're logged into Azure CLI: `az login`
   - Check if you have permissions to create resources in your Azure subscription

4. **Container Startup Issues**:
   - Check container logs: `az container logs --resource-group content-analysis-rg --name content-analysis-api`
   - Verify the Docker image works locally: `docker run -p 8000:8000 YOUR_USERNAME/content-analysis-fastapi:latest`

### Debug Commands

```bash
# Check GitHub Actions logs
# Go to: Repository → Actions → Select workflow run → View logs

# Test Docker image locally
docker pull nyuydinebill/content-analysis-fastapi:latest
docker run -p 8000:8000 nyuydinebill/content-analysis-fastapi:latest

# Check Azure container status
az container show --resource-group content-analysis-rg --name content-analysis-api

# View container logs
az container logs --resource-group content-analysis-rg --name content-analysis-api --follow

# Restart container
az container restart --resource-group content-analysis-rg --name content-analysis-api
```

## 🔒 Security Best Practices

1. **Use Access Tokens**: Never use passwords for GitHub Actions
2. **Limit Token Permissions**: Give minimum required permissions
3. **Private Repositories**: Consider using private Docker Hub repositories for production
4. **Environment Variables**: Store sensitive config in Azure Container Instance environment variables
5. **Regular Updates**: Keep base Docker images updated for security patches

## 💰 Cost Optimization

1. **Container Resources**: Start with 1 CPU, 2GB RAM and scale up if needed
2. **Auto-scaling**: Consider Azure Container Apps for automatic scaling
3. **Scheduled Shutdown**: Use Azure Automation to stop containers during off-hours
4. **Monitoring**: Set up Azure Monitor to track resource usage

## 📊 Monitoring

### Azure Monitor Setup
```bash
# Enable logging (optional)
az container create \
    --resource-group content-analysis-rg \
    --name content-analysis-api \
    --image YOUR_USERNAME/content-analysis-fastapi:latest \
    --log-analytics-workspace /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.OperationalInsights/workspaces/{workspace-name}
```

### Health Checks
- API Health: `http://your-container-url:8000/health`
- API Docs: `http://your-container-url:8000/docs`
- Container Status: `az container show --resource-group content-analysis-rg --name content-analysis-api --query "instanceView.state"`

## 🧹 Cleanup

### Remove Container
```bash
az container delete --resource-group content-analysis-rg --name content-analysis-api --yes
```

### Remove Resource Group (removes everything)
```bash
az group delete --name content-analysis-rg --yes --no-wait
```

### Remove Docker Images (local)
```bash
docker rmi YOUR_USERNAME/content-analysis-fastapi:latest
```
