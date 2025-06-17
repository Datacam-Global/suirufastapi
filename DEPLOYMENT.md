# Azure App Service Deployment Checklist

## Files Updated/Created:
1. ✅ `startup.sh` - Enhanced with better error handling and logging
2. ✅ `requirements.txt` - Organized and optimized dependencies
3. ✅ `azure-deploy.json` - Updated with proper app settings
4. ✅ `.deployment` - Added build configuration
5. ✅ `requirements-minimal.txt` - Minimal dependencies for faster deployment
6. ✅ `.azure` - Build environment configuration

## Deployment Steps:

### Option 1: Using Azure CLI
```bash
# Login to Azure
az login

# Create resource group (if not exists)
az group create --name your-resource-group --location "East US"

# Deploy using ARM template
az deployment group create \
  --resource-group your-resource-group \
  --template-file azure-deploy.json \
  --parameters webAppName=your-app-name

# Deploy code
az webapp deployment source config-zip \
  --resource-group your-resource-group \
  --name your-app-name \
  --src deployment.zip
```

### Option 2: Using GitHub Actions (Recommended)
1. Push code to GitHub repository
2. In Azure Portal, go to your App Service
3. Select "Deployment Center"
4. Choose "GitHub" as source
5. Configure the repository and branch

## Troubleshooting Common Issues:

### Issue 1: "No module named uvicorn"
**Solution:** The updated `startup.sh` now installs dependencies before starting the app.

### Issue 2: Virtual environment not found
**Solution:** Added `SCM_DO_BUILD_DURING_DEPLOYMENT=true` in deployment configuration.

### Issue 3: Container doesn't respond on port
**Solution:** Updated startup command to use `$PORT` environment variable.

### Issue 4: NLTK data not found
**Solution:** The startup script now downloads required NLTK data.

## Environment Variables to Set in Azure App Service:
- `PYTHONPATH=.`
- `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
- `ENABLE_ORYX_BUILD=true`

## Monitoring:
- Check logs in Azure Portal: App Service > Monitoring > Log stream
- Health check endpoint: `https://your-app.azurewebsites.net/health`
- API documentation: `https://your-app.azurewebsites.net/docs`

## Performance Optimization:
- Consider upgrading from F1 (Free) tier to B1 or higher for production
- Enable Application Insights for monitoring
- Use Azure CDN for static content if needed
