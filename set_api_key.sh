#!/bin/bash
# Set a new API key in Secret Manager
# Usage: ./set_api_key.sh [API_KEY_VALUE]

PROJECT_ID="p-power-up-ai"
SECRET_NAME="API_KEY"

if [ -z "$1" ]; then
    # Generate a random API key if none provided
    NEW_API_KEY="adsomnia-$(openssl rand -hex 16)"
    echo "No API key provided. Generating random key..."
else
    NEW_API_KEY="$1"
fi

echo "============================================================"
echo "Setting API Key in Secret Manager"
echo "============================================================"
echo "Project: $PROJECT_ID"
echo "Secret: $SECRET_NAME"
echo "New API Key: $NEW_API_KEY"
echo ""

# Update the secret
echo "Updating secret..."
echo -n "$NEW_API_KEY" | gcloud secrets versions add $SECRET_NAME \
    --data-file=- \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ API Key updated successfully!"
    echo ""
    echo "Your API Key: $NEW_API_KEY"
    echo ""
    echo "Use this key to test the API:"
    echo "  ./test_api_endpoints.sh $NEW_API_KEY"
    echo ""
    echo "Or test with curl:"
    echo "  curl -X POST https://adsomnia-backend-3naijkhxba-uc.a.run.app/api/workflows/wf1/tracking-link \\"
    echo "    -H \"X-API-Key: $NEW_API_KEY\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"affiliate_id\": 12345, \"offer_id\": 1001}'"
else
    echo "❌ Failed to update API key. You may need owner permissions."
    echo ""
    echo "Ask the project owner to run:"
    echo "  echo -n '$NEW_API_KEY' | gcloud secrets versions add API_KEY --data-file=- --project=p-power-up-ai"
fi

