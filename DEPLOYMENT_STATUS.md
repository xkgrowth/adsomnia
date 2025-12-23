# ⚠️ Deployment Status Summary

## Current Situation

Direct CLI deployment to Cloud Run is blocked due to permission restrictions in the `p-power-up-ai` project:

1. ❌ Service account key creation is disabled (security policy)
2. ❌ Workload Identity Pool creation requires Owner permissions
3. ❌ Artifact Registry write permissions require higher access

Your account (`daniel@blablabuild.com`) has **Editor** role, but needs **Owner** role for these operations.

## ✅ What's Ready

All deployment code and configuration is complete and pushed to GitHub:
- ✅ Dockerfile created
- ✅ GitHub Actions workflow configured  
- ✅ Service account created (`github-actions-adsomnia`)
- ✅ Artifact Registry repository created (`adsomnia`)
- ✅ Secrets already in Secret Manager (API_KEY, EVERFLOW_API_KEY, GEMINI_KEY)
- ✅ Code pushed to: https://github.com/xkgrowth/adsomnia

## 🚀 To Complete Deployment (5 Minutes)

Ask the project owner **jdolieslager@harlemnext.com** to run:

```bash
cd /path/to/adsomnia
./setup_github_actions.sh
```

When prompted, enter:
- GitHub username: `xkgrowth`
- Repository name: `adsomnia`

The script will output a `WIF_PROVIDER` value.

### Then Add GitHub Secret

1. Go to: https://github.com/xkgrowth/adsomnia/settings/secrets/actions
2. Click "New repository secret"
3. Name: `WIF_PROVIDER`
4. Value: (paste the output from script)
5. Click "Add secret"

### Deploy!

Push any change to trigger deployment:
```bash
git commit --allow-empty -m "Deploy to Cloud Run"
git push
```

Or trigger manually:
1. Go to: https://github.com/xkgrowth/adsomnia/actions
2. Click "Deploy to Cloud Run" workflow
3. Click "Run workflow"
4. Select `main` branch  
5. Click "Run workflow"

## 🎯 After Deployment

Your backend will be live at:
```
https://adsomnia-backend-xxxxx-uc.a.run.app
```

Test it:
```bash
# Health check
curl https://adsomnia-backend-xxxxx-uc.a.run.app/health

# API docs
open https://adsomnia-backend-xxxxx-uc.a.run.app/docs
```

## 🔄 Future Deployments

Once set up, every push to `main` automatically deploys! No manual intervention needed.

## 📧 Quick Email to Owner

Hi,

Can you help set up auto-deployment for the Adsomnia backend? It's a 2-minute task:

1. Clone the repo: `git clone https://github.com/xkgrowth/adsomnia`
2. Run: `./setup_github_actions.sh`
3. Enter: `xkgrowth` / `adsomnia` when prompted
4. Send me the `WIF_PROVIDER` value it outputs

After that, all code pushes will automatically deploy to Cloud Run!

Thanks!

---

## Alternative: Manual Setup by Owner

If the owner prefers manual commands:

```bash
# 1. Create Workload Identity Pool
gcloud iam workload-identity-pools create github-actions \
    --location="global" \
    --project=p-power-up-ai \
    --display-name="GitHub Actions Pool"

# 2. Create Provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --project=p-power-up-ai

# 3. Bind Service Account
PROJECT_NUMBER=$(gcloud projects describe p-power-up-ai --format="value(projectNumber)")
gcloud iam service-accounts add-iam-policy-binding \
    github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/xkgrowth/adsomnia" \
    --project=p-power-up-ai

# 4. Get WIF Provider (send this to Daniel)
gcloud iam workload-identity-pools providers describe github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --project=p-power-up-ai \
    --format="value(name)"
```

