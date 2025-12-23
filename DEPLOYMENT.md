# 🚀 Google Cloud Deployment Guide

This guide will help you deploy the Adsomnia backend to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Access to `daniel@blablabuild.com`
2. **gcloud CLI**: Install from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Required for building images
4. **Billing Enabled**: Ensure your GCP project has billing enabled

## Quick Start

### 1. Authenticate with Google Cloud

```bash
gcloud auth login daniel@blablabuild.com
```

### 2. Set Up GCP Project

```bash
# Set your project ID
gcloud config set project blablabuild

# Or create a new project if needed
gcloud projects create blablabuild --name="Blablabuild Adsomnia"
gcloud config set project blablabuild
```

### 3. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 4. Create Secrets in Secret Manager

Before deploying, create the required secrets:

```bash
# API Key for authentication
echo -n "your-secret-api-key-here" | gcloud secrets create API_KEY --data-file=-

# Everflow API Key
echo -n "your-everflow-api-key" | gcloud secrets create EVERFLOW_API_KEY --data-file=-

# Google Gemini API Key
echo -n "your-gemini-api-key" | gcloud secrets create GEMINI_KEY --data-file=-
```

**To update existing secrets:**
```bash
echo -n "new-value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

**To view secret (without revealing value):**
```bash
gcloud secrets describe SECRET_NAME
```

### 5. Deploy Using the Script

```bash
# Make the script executable
chmod +x deploy.sh

# Deploy (defaults to project: blablabuild, region: us-central1)
./deploy.sh

# Or specify project and region
./deploy.sh blablabuild us-central1
```

### 6. Manual Deployment (Alternative)

If you prefer manual steps:

```bash
# Build and push image
gcloud builds submit --tag gcr.io/blablabuild/adsomnia-backend

# Deploy to Cloud Run
gcloud run deploy adsomnia-backend \
    --image gcr.io/blablabuild/adsomnia-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "EVERFLOW_BASE_URL=https://api.eflow.team,EVERFLOW_TIMEZONE_ID=67" \
    --update-secrets API_KEY=API_KEY:latest,EVERFLOW_API_KEY=EVERFLOW_API_KEY:latest,GEMINI_KEY=GEMINI_KEY:latest
```

## Configuration

### Environment Variables

The following environment variables are automatically set:
- `EVERFLOW_BASE_URL=https://api.eflow.team`
- `EVERFLOW_TIMEZONE_ID=67`
- `PORT=8080` (set by Cloud Run)

### Secrets (from Secret Manager)

The following secrets are mounted from Secret Manager:
- `API_KEY` - API authentication key
- `EVERFLOW_API_KEY` - Everflow API key
- `GEMINI_KEY` - Google Gemini API key

### Resource Limits

- **Memory**: 512 MiB
- **CPU**: 1 vCPU
- **Timeout**: 300 seconds (5 minutes)
- **Max Instances**: 10 (auto-scales down to 0 when not in use)

## Accessing Your Service

After deployment, you'll get a service URL like:
```
https://adsomnia-backend-xxxxx-uc.a.run.app
```

### Test Endpoints

```bash
# Health check
curl https://adsomnia-backend-xxxxx-uc.a.run.app/health

# API documentation
open https://adsomnia-backend-xxxxx-uc.a.run.app/docs

# Example API call (with API key)
curl -X POST https://adsomnia-backend-xxxxx-uc.a.run.app/api/workflows/wf1/tracking-link \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"affiliate_id": 12345, "offer_id": 1001}'
```

## Updating Secrets

To update a secret after deployment:

```bash
# Update the secret in Secret Manager
echo -n "new-value" | gcloud secrets versions add SECRET_NAME --data-file=-

# Redeploy to pick up the new secret version (optional, Cloud Run can use latest)
gcloud run services update adsomnia-backend \
    --region us-central1 \
    --update-secrets SECRET_NAME=SECRET_NAME:latest
```

## Updating the Service

To redeploy with code changes:

```bash
# Simply run the deploy script again
./deploy.sh
```

Or manually:

```bash
# Build and push new image
gcloud builds submit --tag gcr.io/blablabuild/adsomnia-backend

# Update the service
gcloud run services update adsomnia-backend \
    --image gcr.io/blablabuild/adsomnia-backend \
    --region us-central1
```

## Viewing Logs

```bash
# View recent logs
gcloud run services logs read adsomnia-backend --region us-central1

# Stream logs in real-time
gcloud run services logs tail adsomnia-backend --region us-central1
```

## Monitoring

Access monitoring in the [Google Cloud Console](https://console.cloud.google.com/run):
- Service metrics
- Request logs
- Error rates
- Latency

## Troubleshooting

### Service won't start

1. **Check logs**: `gcloud run services logs read adsomnia-backend --region us-central1`
2. **Verify secrets**: `gcloud secrets list`
3. **Check Dockerfile**: Ensure all dependencies are installed

### 401 Unauthorized

- Verify `API_KEY` secret is set correctly
- Check that the API key in your request matches the secret

### Environment variables not working

- Secrets are mounted as environment variables automatically
- Verify secrets exist: `gcloud secrets list`
- Check service configuration: `gcloud run services describe adsomnia-backend --region us-central1`

### Build fails

- Ensure Dockerfile is correct
- Check that all files are present (requirements.txt, backend/, etc.)
- Verify `.gcloudignore` isn't excluding necessary files

## Cost Considerations

Google Cloud Run pricing:
- **Pay per use**: Only charged when handling requests
- **Memory**: $0.00000250 per GiB-second
- **CPU**: $0.00002400 per vCPU-second
- **Requests**: $0.40 per million requests

With typical usage, costs should be minimal due to auto-scaling to zero.

## Security Best Practices

1. ✅ Secrets stored in Secret Manager (not in code or env vars)
2. ✅ HTTPS enabled by default
3. ✅ CORS configured (adjust `allow_origins` in production)
4. ⚠️ Consider adding authentication if needed
5. ⚠️ Review API key security in production

## Next Steps

- [ ] Configure custom domain
- [ ] Set up Cloud CDN for better performance
- [ ] Configure monitoring alerts
- [ ] Set up CI/CD pipeline
- [ ] Review and restrict CORS origins in production

