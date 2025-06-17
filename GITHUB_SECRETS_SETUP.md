# GitHub Secrets Setup Guide for Azure Deployment

## Required Secrets for Azure Web App Deployment

You need to set up one of the following authentication methods in your GitHub repository secrets:

### Option 1: Azure Publish Profile (Recommended)

1. **Download Publish Profile from Azure Portal:**
   - Go to your Azure Web App in the Azure Portal
   - Navigate to your "fastapis" app service
   - Click "Get publish profile" in the Overview section
   - Download the `.publishsettings` file

2. **Add to GitHub Secrets:**
   - Go to your GitHub repository
   - Navigate to Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Copy and paste the entire content of the `.publishsettings` file

### Option 2: Azure Service Principal Credentials

1. **Create Azure Service Principal:**
   ```bash
   # Login to Azure
   az login
   
   # Create service principal
   az ad sp create-for-rbac --name "GitHubActions-FastAPI" \
     --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group-name} \
     --sdk-auth
   ```

2. **Add to GitHub Secrets:**
   - Name: `AZURE_CREDENTIALS`
   - Value: The JSON output from the above command

### Option 3: Manual Deployment (Temporary Solution)

If you can't set up secrets immediately, you can deploy manually:

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Deploy the app
cd /home/nyuydine/Documents/Skye8/suirufastapi
az webapp up --name fastapis --resource-group <your-resource-group> --runtime "PYTHON:3.12"
```

## Current Status

The GitHub Actions workflow is currently failing because the required secrets are not configured. You need to:

1. Choose one of the authentication methods above
2. Set up the corresponding secret in your GitHub repository
3. Re-run the GitHub Actions workflow

## Verification

After setting up the secrets, you can verify they work by:

1. Going to Actions tab in your GitHub repository
2. Re-running the failed workflow
3. Checking the deployment logs for successful authentication

## Troubleshooting

- **"No credentials found"**: The secret is not set up or has the wrong name
- **"Invalid publish profile"**: The publish profile content is incorrect or corrupted
- **"Access denied"**: The service principal doesn't have sufficient permissions

## Next Steps

1. Set up the `AZURE_WEBAPP_PUBLISH_PROFILE` secret (recommended)
2. Push any changes to trigger the workflow
3. Monitor the deployment in the Actions tab
