#!/bin/bash
# Deployment script for Adsomnia backend to Google Cloud Run
# Usage: ./deploy.sh [project-id] [region]

set -e

# Configuration
PROJECT_ID=${1:-"blablabuild"}
REGION=${2:-"us-central1"}
SERVICE_NAME="adsomnia-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Deploying Adsomnia Backend to Google Cloud Run${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install it first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Project ID: ${PROJECT_ID}"
echo "   Region: ${REGION}"
echo "   Service Name: ${SERVICE_NAME}"
echo "   Image: ${IMAGE_NAME}"
echo ""

# Authenticate with Google Cloud
echo -e "${YELLOW}🔐 Authenticating with Google Cloud...${NC}"
gcloud auth login daniel@blablabuild.com

# Set the project
echo -e "${YELLOW}🎯 Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}🔌 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Configure Docker to use gcloud as credential helper
echo -e "${YELLOW}🐳 Configuring Docker authentication...${NC}"
gcloud auth configure-docker

# Build and push the Docker image
echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME}

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
    --update-secrets API_KEY=API_KEY:latest,EVERFLOW_API_KEY=EVERFLOW_API_KEY:latest,GEMINI_KEY=GEMINI_KEY:latest

# Get the service URL
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo ""
echo -e "${YELLOW}📚 API Documentation: ${SERVICE_URL}/docs${NC}"
echo -e "${YELLOW}❤️  Health Check: ${SERVICE_URL}/health${NC}"
echo ""
echo -e "${YELLOW}💡 Note: Make sure secrets are configured in Secret Manager:${NC}"
echo "   - API_KEY"
echo "   - EVERFLOW_API_KEY"
echo "   - GEMINI_KEY"
echo ""

