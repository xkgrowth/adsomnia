# 🚀 Deployment Complete

## Services Deployed

### Backend API
- **URL**: https://adsomnia-backend-3naijkhxba-uc.a.run.app
- **API Docs**: https://adsomnia-backend-3naijkhxba-uc.a.run.app/docs
- **Health Check**: https://adsomnia-backend-3naijkhxba-uc.a.run.app/health
- **Region**: us-central1
- **Platform**: Google Cloud Run

### Frontend Application
- **URL**: https://adsomnia-frontend-3naijkhxba-uc.a.run.app
- **Region**: us-central1
- **Platform**: Google Cloud Run

## Deployment Method

Both services are deployed using:
- **Google Cloud Build** - Automated Docker image building
- **Artifact Registry** - Docker image storage
- **Cloud Run** - Serverless container hosting

## GitHub Actions CI/CD

Automated deployment workflows are configured:

### Backend Workflow
- **File**: `.github/workflows/deploy-backend.yml`
- **Triggers**: 
  - Push to `main` branch (when backend files change)
  - Manual workflow dispatch
- **Configuration**: Uses `cloudbuild-sa.yaml` for Cloud Build

### Frontend Workflow
- **File**: `.github/workflows/deploy-frontend.yml`
- **Triggers**: 
  - Push to `main` branch (when frontend files change)
  - Manual workflow dispatch
- **Configuration**: Uses `cloudbuild-frontend.yaml` for Cloud Build

## Setup Instructions

### 1. Enable GitHub Actions

To enable automatic deployment via GitHub Actions, add the `GCP_SA_KEY` secret:

1. Go to: https://github.com/xkgrowth/adsomnia/settings/secrets/actions
2. Click "New repository secret"
3. **Name**: `GCP_SA_KEY`
4. **Value**: Service account JSON key (see below)

### 2. Create Service Account Key

Run these commands to create a service account with proper permissions:

```bash
# Create service account
gcloud iam service-accounts create github-actions-deploy \
  --project=p-power-up-ai \
  --display-name="GitHub Actions Deployer"

# Grant Cloud Build permissions
gcloud projects add-iam-policy-binding p-power-up-ai \
  --member="serviceAccount:github-actions-deploy@p-power-up-ai.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

# Grant Cloud Run permissions
gcloud projects add-iam-policy-binding p-power-up-ai \
  --member="serviceAccount:github-actions-deploy@p-power-up-ai.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Artifact Registry permissions
gcloud projects add-iam-policy-binding p-power-up-ai \
  --member="serviceAccount:github-actions-deploy@p-power-up-ai.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-deploy@p-power-up-ai.iam.gserviceaccount.com \
  --project=p-power-up-ai

# Copy the contents of github-actions-key.json to GitHub secret
cat github-actions-key.json
```

**⚠️ Important**: Delete the key file after adding it to GitHub secrets:
```bash
rm github-actions-key.json
```

## Manual Deployment

If you need to deploy manually without GitHub Actions:

### Deploy Backend
```bash
gcloud builds submit --config=cloudbuild-sa.yaml \
  --project=p-power-up-ai \
  --timeout=20m
```

### Deploy Frontend
```bash
gcloud builds submit --config=cloudbuild-frontend.yaml \
  --project=p-power-up-ai \
  --timeout=30m \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)
```

## Environment Variables & Secrets

All secrets are stored in Google Secret Manager and automatically injected into Cloud Run:

- `API_KEY` - API authentication key
- `EVERFLOW_API_KEY` - Everflow API credentials
- `GEMINI_KEY` - Google Gemini API key

Environment variables:
- `EVERFLOW_BASE_URL=https://api.eflow.team`
- `EVERFLOW_TIMEZONE_ID=67`
- `NEXT_PUBLIC_API_URL=https://adsomnia-backend-3naijkhxba-uc.a.run.app` (frontend only)

## Service Configuration

### Backend
- **Memory**: 512Mi
- **CPU**: 1
- **Timeout**: 300 seconds
- **Max Instances**: 10
- **Port**: 8080

### Frontend
- **Memory**: 512Mi
- **CPU**: 1
- **Timeout**: 300 seconds
- **Max Instances**: 10
- **Port**: 3000

## Monitoring & Logs

View logs in Google Cloud Console:
- **Backend**: https://console.cloud.google.com/run/detail/us-central1/adsomnia-backend/logs?project=p-power-up-ai
- **Frontend**: https://console.cloud.google.com/run/detail/us-central1/adsomnia-frontend/logs?project=p-power-up-ai

## Troubleshooting

### Check Service Status
```bash
# Backend
gcloud run services describe adsomnia-backend \
  --region=us-central1 \
  --project=p-power-up-ai

# Frontend
gcloud run services describe adsomnia-frontend \
  --region=us-central1 \
  --project=p-power-up-ai
```

### View Recent Logs
```bash
# Backend
gcloud run services logs read adsomnia-backend \
  --region=us-central1 \
  --project=p-power-up-ai \
  --limit=50

# Frontend
gcloud run services logs read adsomnia-frontend \
  --region=us-central1 \
  --project=p-power-up-ai \
  --limit=50
```

### Update API Key
```bash
./set_api_key.sh YOUR_NEW_API_KEY
# Then redeploy backend to pick up new secret version
```

## Next Steps

1. ✅ Add `GCP_SA_KEY` secret to GitHub for automated deployments
2. ✅ Test both services are working correctly
3. ✅ Set up monitoring/alerts if needed
4. ✅ Configure custom domain (optional)

## Date Deployed
December 23, 2024

