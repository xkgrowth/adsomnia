#!/bin/bash
# Setup GitHub Actions Deployment for Adsomnia
# Run this script as the project owner (jdolieslager@harlemnext.com)

set -e

PROJECT_ID="p-power-up-ai"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com"

echo "============================================================"
echo "Setting up GitHub Actions for Adsomnia Backend"
echo "============================================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo ""

# Get GitHub repo info
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your repository name (e.g., adsomnia): " GITHUB_REPO

echo ""
echo "Setting up for: $GITHUB_USER/$GITHUB_REPO"
echo ""

# 1. Enable required APIs
echo "📋 Enabling required APIs..."
gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID

# 2. Create Workload Identity Pool
echo "🔐 Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create github-actions \
    --location="global" \
    --project=$PROJECT_ID \
    --display-name="GitHub Actions Pool" || echo "Pool may already exist"

# 3. Create Workload Identity Provider
echo "🔑 Creating Workload Identity Provider..."
gcloud iam workload-identity-pools providers create-oidc github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
    --project=$PROJECT_ID || echo "Provider may already exist"

# 4. Allow GitHub Actions to impersonate the service account
echo "👤 Binding service account to GitHub repository..."
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/$GITHUB_USER/$GITHUB_REPO" \
    --project=$PROJECT_ID

# 5. Get the Workload Identity Provider resource name
echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "📝 Add this secret to GitHub:"
echo ""
echo "Secret Name: WIF_PROVIDER"
echo "Secret Value:"
echo ""
gcloud iam workload-identity-pools providers describe github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --project=$PROJECT_ID \
    --format="value(name)"
echo ""
echo "============================================================"
echo ""
echo "How to add the secret to GitHub:"
echo "1. Go to: https://github.com/$GITHUB_USER/$GITHUB_REPO/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Name: WIF_PROVIDER"
echo "4. Value: (the value printed above)"
echo "5. Click 'Add secret'"
echo ""
echo "Then push your code to GitHub and it will auto-deploy!"
echo ""

