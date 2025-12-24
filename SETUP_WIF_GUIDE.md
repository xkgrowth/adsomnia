# Workload Identity Federation Setup Guide

## Prerequisites

1. **Google Cloud SDK installed** ✅ (Already installed)
2. **Authenticated with gcloud** ⚠️ (Required - see below)
3. **Project owner or IAM admin permissions** (Required for WIF setup)

## Step 1: Authenticate with Google Cloud

Run this command in your terminal (it will open a browser for authentication):

```bash
export PATH=/opt/homebrew/share/google-cloud-sdk/bin:"$PATH"
gcloud auth login
```

Or if you prefer to use application default credentials:

```bash
gcloud auth application-default login
```

**Note**: You need to be authenticated with an account that has:
- `iam.workloadIdentityPools.create` permission
- `iam.serviceAccounts.setIamPolicy` permission
- Project owner or IAM admin role (recommended)

## Step 2: Set the Project

```bash
gcloud config set project p-power-up-ai
```

## Step 3: Run the Setup Script

Once authenticated, run the setup script:

```bash
export PATH=/opt/homebrew/share/google-cloud-sdk/bin:"$PATH"
./setup_wif.sh
```

The script will:
1. ✅ Enable required APIs
2. ✅ Create Workload Identity Pool (if it doesn't exist)
3. ✅ Create OIDC Provider (if it doesn't exist)
4. ✅ Bind the service account to your GitHub repository
5. ✅ Display the `WIF_PROVIDER` value you need to add to GitHub

## Step 4: Add Secret to GitHub

After the script completes, you'll see a `WIF_PROVIDER` value. Add it to GitHub:

1. Go to: https://github.com/xkgrowth/adsomnia/settings/secrets/actions
2. Click "New repository secret"
3. **Name**: `WIF_PROVIDER`
4. **Value**: (Copy the value from the script output)
5. Click "Add secret"

## What This Does

Workload Identity Federation (WIF) allows GitHub Actions to authenticate to Google Cloud without using service account keys. This is:
- ✅ More secure (no keys to manage)
- ✅ Works with organization policies that disable key creation
- ✅ Recommended by Google Cloud

## Verification

After setup, your GitHub Actions workflows will automatically use WIF for authentication. The workflows check for `WIF_PROVIDER` first, then fall back to `GCP_SA_KEY` if needed.

## Troubleshooting

### Permission Denied Errors

If you get permission errors, ensure your account has:
- Project Owner role, OR
- These specific permissions:
  - `iam.workloadIdentityPools.create`
  - `iam.workloadIdentityPools.get`
  - `iam.workloadIdentityPools.update`
  - `iam.workloadIdentityPoolProviders.create`
  - `iam.serviceAccounts.setIamPolicy`

### Pool Already Exists

If the pool or provider already exists, the script will skip creation and continue. This is safe.

### Service Account Binding Already Exists

If the binding already exists, the script will detect it and skip. This is safe.

## Next Steps

Once `WIF_PROVIDER` is added to GitHub Secrets:
1. ✅ Push any code change to trigger a workflow
2. ✅ Check GitHub Actions to verify deployment works
3. ✅ Monitor Cloud Run logs to ensure services are running

---

**Created**: $(date)
**Repository**: xkgrowth/adsomnia
**Project**: p-power-up-ai

