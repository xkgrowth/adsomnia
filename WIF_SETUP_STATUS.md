# Workload Identity Federation Setup Status

## Current Situation

✅ **Google Cloud SDK**: Installed and configured  
✅ **Authentication**: Authenticated as `xennith@blablabuild.com`  
✅ **Project**: Set to `p-power-up-ai`  
✅ **Service Account**: `github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com` exists  
❌ **Workload Identity Pool**: Does not exist yet  
❌ **Permission**: Current account lacks `iam.workloadIdentityPools.create` permission  

## Required Permissions

To create the Workload Identity Pool, you need one of these roles:
- `roles/owner` (Project Owner)
- `roles/iam.workloadIdentityPoolAdmin`
- `roles/iam.admin`

**Current roles**: `roles/editor`, `roles/resourcemanager.projectIamAdmin`

## Next Steps

### Option 1: Request Permission (Recommended)

Ask a project owner or IAM admin to run the setup script:

```bash
export PATH=/opt/homebrew/share/google-cloud-sdk/bin:"$PATH"
./setup_wif.sh
```

Or they can run the commands manually:

```bash
# 1. Enable API
gcloud services enable iamcredentials.googleapis.com --project=p-power-up-ai

# 2. Create Workload Identity Pool
gcloud iam workload-identity-pools create github-actions \
    --location="global" \
    --project=p-power-up-ai \
    --display-name="GitHub Actions Pool"

# 3. Create OIDC Provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
    --project=p-power-up-ai

# 4. Get project number
PROJECT_NUMBER=$(gcloud projects describe p-power-up-ai --format="value(projectNumber)")

# 5. Bind service account
gcloud iam service-accounts add-iam-policy-binding github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/xkgrowth/adsomnia" \
    --project=p-power-up-ai

# 6. Get WIF Provider value
gcloud iam workload-identity-pools providers describe github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --project=p-power-up-ai \
    --format="value(name)"
```

### Option 2: Use Existing Service Account Key

If you have access to the existing service account key (created on 2025-12-23T17:49:48Z), you can:

1. Add it to GitHub Secrets as `GCP_SA_KEY`
2. The workflows will use it (they already support this)

**Note**: The key file cannot be retrieved if you don't have it - keys can only be downloaded when created.

### Option 3: Update Workflows to Support WIF

Once the Workload Identity Pool is created, update the GitHub Actions workflows to use WIF. The workflows need to be modified to check for `WIF_PROVIDER` first.

## Workflow Updates Needed

After WIF is set up, the workflows (`.github/workflows/deploy-backend.yml` and `.github/workflows/deploy-frontend.yml`) should be updated to:

1. Check for `WIF_PROVIDER` secret first
2. Use Workload Identity Federation if available
3. Fall back to `GCP_SA_KEY` if WIF is not available

Example authentication step:
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com
```

## Summary

**What's Done:**
- ✅ Setup script created (`setup_wif.sh`)
- ✅ Authentication configured
- ✅ Service account verified

**What's Needed:**
- ⚠️ Project owner/IAM admin to create Workload Identity Pool
- ⚠️ Add `WIF_PROVIDER` secret to GitHub after pool is created
- ⚠️ Update workflows to use WIF (optional, but recommended)

---

**Date**: December 24, 2024  
**Authenticated User**: xennith@blablabuild.com  
**Project**: p-power-up-ai

