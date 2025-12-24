#!/bin/bash
# Setup Workload Identity Federation for GitHub Actions
# This script must be run by a project owner (jdolieslager@harlemnext.com)

set -e

PROJECT_ID="p-power-up-ai"
GITHUB_USER="xkgrowth"
GITHUB_REPO="adsomnia"
SERVICE_ACCOUNT="github-actions-adsomnia@p-power-up-ai.iam.gserviceaccount.com"

echo "============================================================"
echo "Setting up Workload Identity Federation for GitHub Actions"
echo "============================================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Repository: $GITHUB_USER/$GITHUB_REPO"
echo "Service Account: $SERVICE_ACCOUNT"
echo ""

# Get project number
echo "📋 Getting project number..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
echo "Project Number: $PROJECT_NUMBER"
echo ""

# 1. Enable required APIs
echo "📋 Enabling required APIs..."
gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID || echo "API may already be enabled"
echo ""

# 2. Create Workload Identity Pool
echo "🔐 Creating Workload Identity Pool..."
if gcloud iam workload-identity-pools describe github-actions \
    --location="global" \
    --project=$PROJECT_ID &>/dev/null; then
    echo "✅ Workload Identity Pool 'github-actions' already exists"
else
    gcloud iam workload-identity-pools create github-actions \
        --location="global" \
        --project=$PROJECT_ID \
        --display-name="GitHub Actions Pool"
    echo "✅ Workload Identity Pool created"
fi
echo ""

# 3. Create Workload Identity Provider
echo "🔑 Creating Workload Identity Provider..."
if gcloud iam workload-identity-pools providers describe github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --project=$PROJECT_ID &>/dev/null; then
    echo "✅ Workload Identity Provider 'github-provider' already exists"
else
    gcloud iam workload-identity-pools providers create-oidc github-provider \
        --location="global" \
        --workload-identity-pool="github-actions" \
        --issuer-uri="https://token.actions.githubusercontent.com" \
        --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
        --project=$PROJECT_ID
    echo "✅ Workload Identity Provider created"
fi
echo ""

# 4. Allow GitHub Actions to impersonate the service account
echo "👤 Binding service account to GitHub repository..."
MEMBER="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/$GITHUB_USER/$GITHUB_REPO"

# Check if binding already exists
EXISTING_BINDING=$(gcloud iam service-accounts get-iam-policy $SERVICE_ACCOUNT \
    --project=$PROJECT_ID \
    --format="value(bindings[].members)" 2>/dev/null | grep -o "$MEMBER" || echo "")

if [ -n "$EXISTING_BINDING" ]; then
    echo "✅ Service account binding already exists"
else
    gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT \
        --role="roles/iam.workloadIdentityUser" \
        --member="$MEMBER" \
        --project=$PROJECT_ID
    echo "✅ Service account binding created"
fi
echo ""

# 5. Get the Workload Identity Provider resource name
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "📝 Add this secret to GitHub:"
echo ""
echo "Secret Name: WIF_PROVIDER"
echo "Secret Value:"
echo ""

WIF_PROVIDER=$(gcloud iam workload-identity-pools providers describe github-provider \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --project=$PROJECT_ID \
    --format="value(name)")

echo "$WIF_PROVIDER"
echo ""
echo "============================================================"
echo ""
echo "How to add the secret to GitHub:"
echo "1. Go to: https://github.com/$GITHUB_USER/$GITHUB_REPO/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Name: WIF_PROVIDER"
echo "4. Value: (copy the value printed above)"
echo "5. Click 'Add secret'"
echo ""
echo "Once added, GitHub Actions will automatically use WIF for authentication!"
echo ""

