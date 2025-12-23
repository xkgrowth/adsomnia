# 🚀 Quick GitHub Deployment Guide

## Prerequisites
- ✅ Authenticated with `daniel@blablabuild.com`
- ✅ GitHub repository created
- ✅ Secrets already created in Secret Manager

## Step-by-Step (5 minutes)

### 1. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create adsomnia \
    --repository-format=docker \
    --location=us-central1 \
    --project=p-power-up-ai \
    --description="Adsomnia backend Docker images"
```

### 2. Create Service Account & Grant Permissions

```bash
# Create service account
gcloud iam service-accounts create github-actions-adsomnia \
    --display-name="GitHub Actions - Adsomnia" \
    --project=p-power-up-ai

# Grant all necessary roles at once
for ROLE in roles/run.admin roles/iam.serviceAccountUser roles/artifactregistry.writer roles/secretmanager.secretAccessor
do
  gcloud projects add-iam-policy-binding p-power-up-ai \
    --member="serviceAccount:github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com" \
    --role="$ROLE"
done
```

### 3. Create & Download Service Account Key

```bash
# Create key
gcloud iam service-accounts keys create ~/github-actions-key.json \
    --iam-account=github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com \
    --project=p-power-up-ai

# Display key (copy this)
cat ~/github-actions-key.json

# Clean up
rm ~/github-actions-key.json
```

### 4. Add Secret to GitHub

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **New repository secret**
3. Name: `GCP_SA_KEY`
4. Value: Paste the entire JSON from step 3
5. Click **Add secret**

### 5. Push to GitHub

```bash
cd /Users/danieldevos/Documents/BLABLABUILD/adsomnia

# If not a git repo yet
git init
git add .
git commit -m "Initial commit with GitHub Actions deployment"

# Add your GitHub repo
git remote add origin https://github.com/YOUR_USERNAME/adsomnia.git

# Push
git push -u origin main
```

### 6. Done! 🎉

- Go to GitHub Actions tab to watch deployment
- Service will be at: `https://adsomnia-backend-xxxxx-uc.a.run.app`
- Every push to `main` will auto-deploy

## Testing the Service

Once deployed, test it:

```bash
# Get the service URL
gcloud run services describe adsomnia-backend \
    --region=us-central1 \
    --project=p-power-up-ai \
    --format='value(status.url)'

# Test health endpoint
curl https://adsomnia-backend-xxxxx-uc.a.run.app/health

# View API docs
open https://adsomnia-backend-xxxxx-uc.a.run.app/docs
```

## Troubleshooting

### "Repository not found"
Run step 1 again to create the Artifact Registry repository.

### "Permission denied"
Make sure all roles in step 2 were granted successfully.

### "Invalid credentials"
Verify the GitHub secret `GCP_SA_KEY` contains the full JSON key.

## Manual Deployment Trigger

Don't want to push code? Deploy manually:
1. Go to GitHub Actions tab
2. Select "Deploy to Cloud Run"
3. Click "Run workflow"
4. Choose branch and click "Run workflow"

---

**Full documentation**: See `GITHUB_DEPLOYMENT.md`

