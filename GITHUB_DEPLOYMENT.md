# 🚀 GitHub Actions Deployment to Google Cloud Run

This guide shows you how to set up automatic deployment to Google Cloud Run using GitHub Actions.

## Why GitHub Actions?

- ✅ **Automatic deployment** on every push to main
- ✅ **No permission issues** - runs in GitHub's environment
- ✅ **CI/CD built-in** - test and deploy automatically
- ✅ **Version control** - every deployment is tracked
- ✅ **Easy rollback** - revert to any previous commit

## Setup Steps

### 1. Create Artifact Registry Repository

First, create an Artifact Registry repository (more modern than Container Registry):

```bash
# Make sure you're authenticated
gcloud auth list

# Create Artifact Registry repository
gcloud artifacts repositories create adsomnia \
    --repository-format=docker \
    --location=us-central1 \
    --project=p-power-up-ai \
    --description="Docker repository for Adsomnia backend"
```

### 2. Create Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions-adsomnia \
    --display-name="GitHub Actions - Adsomnia" \
    --project=p-power-up-ai

# Grant necessary permissions
gcloud projects add-iam-policy-binding p-power-up-ai \
    --member="serviceAccount:github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding p-power-up-ai \
    --member="serviceAccount:github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding p-power-up-ai \
    --member="serviceAccount:github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Allow access to Secret Manager
gcloud projects add-iam-policy-binding p-power-up-ai \
    --member="serviceAccount:github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 3. Create and Download Service Account Key

```bash
# Create key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com \
    --project=p-power-up-ai

# Display the key (copy this entire JSON output)
cat github-actions-key.json

# IMPORTANT: Delete the local key file after copying
rm github-actions-key.json
```

### 4. Add Secret to GitHub Repository

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GCP_SA_KEY`
5. Value: Paste the entire JSON content from the previous step
6. Click **Add secret**

### 5. Push to GitHub

Now, push your code to GitHub:

```bash
cd /Users/danieldevos/Documents/BLABLABUILD/adsomnia

# Initialize git if not already done
git init

# Add files
git add .

# Commit
git commit -m "Add Cloud Run deployment via GitHub Actions"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/adsomnia.git

# Push to main branch
git push -u origin main
```

### 6. Watch the Deployment

1. Go to your GitHub repository
2. Click on **Actions** tab
3. You'll see the deployment workflow running
4. Click on the workflow to see real-time logs
5. Once complete, you'll see the deployed service URL in the logs

## Manual Deployment

You can also trigger deployment manually without pushing code:

1. Go to **Actions** tab in GitHub
2. Click on **Deploy to Cloud Run** workflow
3. Click **Run workflow** button
4. Select branch (usually `main`)
5. Click **Run workflow**

## Viewing Deployment Status

### In GitHub
- Go to **Actions** tab to see all deployments
- Click on any deployment to see logs
- Green checkmark = successful deployment
- Red X = failed deployment

### In Google Cloud Console
- Visit [Cloud Run Console](https://console.cloud.google.com/run?project=p-power-up-ai)
- Click on `adsomnia-backend` service
- View metrics, logs, and revisions

## What Gets Deployed

Every time you push to `main` branch:
1. ✅ GitHub Actions builds your Docker image
2. ✅ Pushes image to Artifact Registry
3. ✅ Deploys to Cloud Run
4. ✅ Uses secrets from Secret Manager
5. ✅ Service URL is displayed in logs

## Environment Variables & Secrets

The workflow automatically:
- Sets `EVERFLOW_BASE_URL` and `EVERFLOW_TIMEZONE_ID` as environment variables
- Mounts `API_KEY`, `EVERFLOW_API_KEY`, and `GEMINI_KEY` from Secret Manager

To update secrets:
```bash
# Update a secret
echo -n "new-value" | gcloud secrets versions add SECRET_NAME \
    --data-file=- \
    --project=p-power-up-ai
```

The next deployment will automatically use the new secret version.

## Rollback to Previous Version

If something goes wrong:

```bash
# List all revisions
gcloud run revisions list \
    --service=adsomnia-backend \
    --region=us-central1 \
    --project=p-power-up-ai

# Rollback to a specific revision
gcloud run services update-traffic adsomnia-backend \
    --to-revisions=REVISION_NAME=100 \
    --region=us-central1 \
    --project=p-power-up-ai
```

Or use the Google Cloud Console:
1. Go to Cloud Run service
2. Click on **Revisions** tab
3. Select a previous revision
4. Click **Manage traffic**
5. Route 100% traffic to that revision

## Monitoring

### View Logs
```bash
# Real-time logs
gcloud run services logs tail adsomnia-backend \
    --region=us-central1 \
    --project=p-power-up-ai

# Recent logs
gcloud run services logs read adsomnia-backend \
    --region=us-central1 \
    --project=p-power-up-ai \
    --limit=100
```

### View Metrics
Visit: https://console.cloud.google.com/run/detail/us-central1/adsomnia-backend/metrics?project=p-power-up-ai

## Troubleshooting

### Build Fails
- Check the GitHub Actions logs
- Verify Dockerfile syntax
- Ensure all dependencies in `requirements.txt`

### Deployment Fails
- Verify service account has necessary permissions
- Check that secrets exist in Secret Manager
- Verify project ID is correct

### Service Errors
- Check Cloud Run logs: `gcloud run services logs read adsomnia-backend --region=us-central1 --project=p-power-up-ai`
- Verify environment variables are set correctly
- Test locally with Docker first

### GitHub Secret Issues
- Verify `GCP_SA_KEY` secret is set in GitHub repository settings
- Ensure the JSON is valid and complete
- Service account must have all necessary roles

## Cost Optimization

Cloud Run pricing:
- **No traffic = $0** (scales to zero)
- **Per request**: $0.40 per million requests
- **Memory**: $0.00000250 per GiB-second
- **CPU**: $0.00002400 per vCPU-second

Estimated cost for moderate usage: **$5-20/month**

## Next Steps

- [ ] Set up branch protection rules
- [ ] Add testing step before deployment
- [ ] Configure custom domain
- [ ] Set up monitoring alerts
- [ ] Add staging environment

## Quick Reference

```bash
# View service
gcloud run services describe adsomnia-backend --region=us-central1 --project=p-power-up-ai

# Update service manually
gcloud run services update adsomnia-backend --region=us-central1 --project=p-power-up-ai

# Delete service
gcloud run services delete adsomnia-backend --region=us-central1 --project=p-power-up-ai

# View all revisions
gcloud run revisions list --service=adsomnia-backend --region=us-central1 --project=p-power-up-ai
```

