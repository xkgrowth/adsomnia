# 🚀 GitHub Actions Deployment Setup (Workload Identity Federation)

## Setup Workload Identity Federation (More Secure!)

Since the project doesn't allow service account keys, we'll use Workload Identity Federation (WIF) - which is actually more secure!

### Run These Commands:

```bash
# 1. Enable IAM API
gcloud services enable iamcredentials.googleapis.com --project=p-power-up-ai

# 2. Create Workload Identity Pool
gcloud iam workload-identity-pools create github-actions \
    --location="global" \
    --project=p-power-up-ai \
    --display-name="GitHub Actions Pool"

# 3. Create Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
    --project=p-power-up-ai

# 4. Allow GitHub Actions to impersonate the service account
# Replace YOUR_GITHUB_USERNAME and YOUR_REPO_NAME with actual values
gcloud iam service-accounts add-iam-policy-binding \
    github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/189514741256/locations/global/workloadIdentityPools/github-actions/attribute.repository/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME" \
    --project=p-power-up-ai

# 5. Get the Workload Identity Provider resource name
gcloud iam workload-identity-pools providers describe github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --project=p-power-up-ai \
    --format="value(name)"
```

### Add GitHub Secret

After running command #5, copy the output (it will look like):
```
projects/189514741256/locations/global/workloadIdentityPools/github-actions/providers/github-provider
```

Then add it to GitHub:
1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **New repository secret**
3. Name: `WIF_PROVIDER`
4. Value: Paste the output from command #5
5. Click **Add secret**

### Push to GitHub

```bash
cd /Users/danieldevos/Documents/BLABLABUILD/adsomnia

git add .
git commit -m "Add GitHub Actions deployment with Workload Identity Federation"
git push
```

### Done!

Every push to `main` will now automatically deploy to Cloud Run!

---

## What's Your GitHub Repository?

To complete step #4, I need:
- Your GitHub username
- Your repository name

For example: `danieldevos/adsomnia`

