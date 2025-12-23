#!/bin/bash
# Test script for Adsomnia API endpoints
# Usage: ./test_api_endpoints.sh [API_KEY]

SERVICE_URL="https://adsomnia-backend-3naijkhxba-uc.a.run.app"
API_KEY="${1:-YOUR_API_KEY_HERE}"

echo "============================================================"
echo "Testing Adsomnia API Endpoints"
echo "============================================================"
echo "Service URL: $SERVICE_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check (no auth)
echo -e "${YELLOW}1. Health Check (no auth required)${NC}"
RESPONSE=$(curl -s "$SERVICE_URL/health")
echo "$RESPONSE" | python3 -m json.tool
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi
echo ""

# Test 2: API Docs
echo -e "${YELLOW}2. API Documentation${NC}"
echo "   URL: $SERVICE_URL/docs"
echo "   Status: $(curl -s -o /dev/null -w '%{http_code}' $SERVICE_URL/docs)"
echo ""

# Test 3: OpenAPI Schema
echo -e "${YELLOW}3. OpenAPI Schema${NC}"
SCHEMA_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$SERVICE_URL/openapi.json")
echo "   Status: $SCHEMA_STATUS"
if [ "$SCHEMA_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ OpenAPI schema accessible${NC}"
else
    echo -e "${RED}❌ OpenAPI schema failed${NC}"
fi
echo ""

# Test 4: Authentication (should fail without key)
echo -e "${YELLOW}4. Authentication Test (no API key)${NC}"
RESPONSE=$(curl -s -X POST "$SERVICE_URL/api/workflows/wf1/tracking-link" \
    -H "Content-Type: application/json" \
    -d '{"affiliate_id": 12345, "offer_id": 1001}')
echo "$RESPONSE" | python3 -m json.tool
if echo "$RESPONSE" | grep -q "API key required"; then
    echo -e "${GREEN}✅ Authentication properly enforced${NC}"
else
    echo -e "${RED}❌ Authentication not working${NC}"
fi
echo ""

# Test 5: Invalid API Key
echo -e "${YELLOW}5. Invalid API Key Test${NC}"
RESPONSE=$(curl -s -X POST "$SERVICE_URL/api/workflows/wf1/tracking-link" \
    -H "X-API-Key: invalid-key" \
    -H "Content-Type: application/json" \
    -d '{"affiliate_id": 12345, "offer_id": 1001}')
echo "$RESPONSE" | python3 -m json.tool
if echo "$RESPONSE" | grep -q "Invalid API key"; then
    echo -e "${GREEN}✅ Invalid key properly rejected${NC}"
else
    echo -e "${RED}❌ Invalid key not rejected${NC}"
fi
echo ""

# Test 6: WF1 - Generate Tracking Link (with valid API key)
if [ "$API_KEY" != "YOUR_API_KEY_HERE" ]; then
    echo -e "${YELLOW}6. WF1 - Generate Tracking Link${NC}"
    RESPONSE=$(curl -s -X POST "$SERVICE_URL/api/workflows/wf1/tracking-link" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"affiliate_id": 12345, "offer_id": 1001}')
    echo "$RESPONSE" | python3 -m json.tool
    if echo "$RESPONSE" | grep -q "tracking_link\|status"; then
        echo -e "${GREEN}✅ WF1 endpoint working${NC}"
    else
        echo -e "${RED}❌ WF1 endpoint failed${NC}"
    fi
    echo ""
fi

# Test 7: WF2 - Top Landing Pages (with valid API key)
if [ "$API_KEY" != "YOUR_API_KEY_HERE" ]; then
    echo -e "${YELLOW}7. WF2 - Top Landing Pages${NC}"
    RESPONSE=$(curl -s -X POST "$SERVICE_URL/api/workflows/wf2/top-landing-pages" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"offer_id": 1001, "country_code": "US", "days": 30, "min_leads": 5, "top_n": 3}')
    echo "$RESPONSE" | python3 -m json.tool | head -30
    echo ""
fi

# Test 8: Entities - Offers (with valid API key)
if [ "$API_KEY" != "YOUR_API_KEY_HERE" ]; then
    echo -e "${YELLOW}8. Entities - Get Offers${NC}"
    RESPONSE=$(curl -s "$SERVICE_URL/api/entities/offers" \
        -H "X-API-Key: $API_KEY")
    echo "$RESPONSE" | python3 -m json.tool | head -30
    echo ""
fi

echo "============================================================"
echo "Testing Complete"
echo "============================================================"
echo ""
echo "To test with your API key, run:"
echo "  ./test_api_endpoints.sh YOUR_API_KEY"
echo ""
echo "Or get the API key from Secret Manager:"
echo "  gcloud secrets versions access latest --secret=API_KEY --project=p-power-up-ai"

