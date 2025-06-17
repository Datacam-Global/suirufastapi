#!/bin/bash

# Configuration helper script for Docker Hub deployment
# This script helps you update the necessary files with your Docker Hub username

set -e

echo "🔧 Docker Hub Deployment Configuration Helper"
echo "=============================================="
echo ""

# Get Docker Hub username
read -p "Enter your Docker Hub username: " DOCKER_HUB_USERNAME

if [[ -z "$DOCKER_HUB_USERNAME" ]]; then
    echo "❌ Docker Hub username cannot be empty!"
    exit 1
fi

DOCKER_HUB_REPO="$DOCKER_HUB_USERNAME/content-analysis-fastapi"

echo ""
echo "📝 Updating configuration files..."

# Update GitHub workflow
if [[ -f ".github/workflows/docker-build-push.yml" ]]; then
    sed -i "s/your-dockerhub-username\/content-analysis-fastapi/$DOCKER_HUB_REPO/g" .github/workflows/docker-build-push.yml
    echo "✅ Updated GitHub workflow: .github/workflows/docker-build-push.yml"
else
    echo "⚠️  GitHub workflow file not found: .github/workflows/docker-build-push.yml"
fi

# Update deployment script
if [[ -f "deploy-dockerhub.sh" ]]; then
    sed -i "s/your-dockerhub-username\/content-analysis-fastapi/$DOCKER_HUB_REPO/g" deploy-dockerhub.sh
    echo "✅ Updated deployment script: deploy-dockerhub.sh"
else
    echo "⚠️  Deployment script not found: deploy-dockerhub.sh"
fi

echo ""
echo "✅ Configuration completed!"
echo ""
echo "📋 Next steps:"
echo "1. Create a Docker Hub repository named 'content-analysis-fastapi'"
echo "2. Create a Docker Hub access token"
echo "3. Add GitHub secrets:"
echo "   - DOCKER_HUB_USERNAME: $DOCKER_HUB_USERNAME"
echo "   - DOCKER_HUB_ACCESS_TOKEN: [your access token]"
echo "4. Push your code to GitHub (main branch)"
echo "5. Run: ./deploy-dockerhub.sh"
echo ""
echo "🔗 Useful links:"
echo "- Docker Hub: https://hub.docker.com"
echo "- Create repository: https://hub.docker.com/repository/create"
echo "- Access tokens: https://hub.docker.com/settings/security"
echo "- GitHub secrets: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
