#!/bin/bash
# Deploy Adsomnia backend to p-power-up-ai project
# This script requires daniel@blablabuild.com authentication

set -e

PROJECT_ID="p-power-up-ai"
REGION="us-central1"
SERVICE_NAME="adsomnia-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Deploying Adsomnia Backend to p-power-up-ai${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""

# Check current authentication
echo -e "${YELLOW}📋 Checking authentication...${NC}"
CURRENT_ACCOUNT=$(gcloud config get-value account 2>/dev/null)
echo "   Current account: ${CURRENT_ACCOUNT}"

if [[ "$CURRENT_ACCOUNT" != "daniel@blablabuild.com" ]]; then
    echo -e "${RED}⚠️  You need to authenticate with daniel@blablabuild.com${NC}"
    echo ""
    echo "Please run:"
    echo -e "${BLUE}   gcloud auth login daniel@blablabuild.com${NC}"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo -e "${GREEN}✓ Authenticated as daniel@blablabuild.com${NC}"
echo ""

# Set project
echo -e "${YELLOW}🎯 Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}🔌 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Check if secrets exist
echo -e "${YELLOW}🔑 Checking secrets...${NC}"
SECRETS_MISSING=false

for SECRET in API_KEY EVERFLOW_API_KEY GEMINI_KEY; do
    if gcloud secrets describe $SECRET --project=${PROJECT_ID} >/dev/null 2>&1; then
        echo -e "${GREEN}   ✓ $SECRET exists${NC}"
    else
        echo -e "${RED}   ✗ $SECRET missing${NC}"
        SECRETS_MISSING=true
    fi
done

if [ "$SECRETS_MISSING" = true ]; then
    echo ""
    echo -e "${YELLOW}📝 Creating missing secrets...${NC}"
    echo ""
    
    # Create API_KEY if missing
    if ! gcloud secrets describe API_KEY --project=${PROJECT_ID} >/dev/null 2>&1; then
        echo -e "${BLUE}Creating API_KEY...${NC}"
        echo -n "adsomnia-api-key-$(date +%s)" | gcloud secrets create API_KEY --data-file=- --project=${PROJECT_ID}
        echo -e "${GREEN}✓ API_KEY created (change this later for production)${NC}"
    fi
    
    # Create GEMINI_KEY if missing
    if ! gcloud secrets describe GEMINI_KEY --project=${PROJECT_ID} >/dev/null 2>&1; then
        echo -e "${BLUE}Creating GEMINI_KEY from .env...${NC}"
        echo -n "AIzaSyCR_BMYds80o8lHHt1sTyQIheDKhqmKgzc" | gcloud secrets create GEMINI_KEY --data-file=- --project=${PROJECT_ID}
        echo -e "${GREEN}✓ GEMINI_KEY created${NC}"
    fi
    
    # Check for EVERFLOW_API_KEY
    if ! gcloud secrets describe EVERFLOW_API_KEY --project=${PROJECT_ID} >/dev/null 2>&1; then
        echo -e "${RED}⚠️  EVERFLOW_API_KEY not found${NC}"
        echo ""
        echo "Please create it manually with:"
        echo -e "${BLUE}   echo -n 'YOUR_EVERFLOW_KEY' | gcloud secrets create EVERFLOW_API_KEY --data-file=- --project=${PROJECT_ID}${NC}"
        echo ""
        read -p "Press Enter when you've created the EVERFLOW_API_KEY secret..."
    fi
fi

echo ""
echo -e "${GREEN}✓ All secrets ready${NC}"
echo ""

# Configure Docker
echo -e "${YELLOW}🐳 Configuring Docker authentication...${NC}"
gcloud auth configure-docker --quiet

# Build and submit
echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME} --project=${PROJECT_ID}

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "EVERFLOW_BASE_URL=https://api.eflow.team,EVERFLOW_TIMEZONE_ID=67" \
    --update-secrets API_KEY=API_KEY:latest,EVERFLOW_API_KEY=EVERFLOW_API_KEY:latest,GEMINI_KEY=GEMINI_KEY:latest \
    --project=${PROJECT_ID}

# Get service URL
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --project=${PROJECT_ID} --format 'value(status.url)')
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo ""
echo -e "${BLUE}📚 API Documentation: ${SERVICE_URL}/docs${NC}"
echo -e "${BLUE}❤️  Health Check: ${SERVICE_URL}/health${NC}"
echo ""
echo -e "${YELLOW}Test it:${NC}"
echo -e "   curl ${SERVICE_URL}/health"
echo ""

