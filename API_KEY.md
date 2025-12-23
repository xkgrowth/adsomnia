# 🔑 API Key Information

## Current API Key

**API Key:** `adsomnia-api-1766519149`

**Status:** ✅ Active and tested

**Service URL:** https://adsomnia-backend-3naijkhxba-uc.a.run.app

## Quick Start

### Test the API

```bash
# Health check (no auth required)
curl https://adsomnia-backend-3naijkhxba-uc.a.run.app/health

# Test workflow endpoint
curl -X POST https://adsomnia-backend-3naijkhxba-uc.a.run.app/api/workflows/wf1/tracking-link \
  -H "X-API-Key: adsomnia-api-1766519149" \
  -H "Content-Type: application/json" \
  -d '{"affiliate_id": 12345, "offer_id": 1001}'
```

### Use the Test Script

```bash
./test_api_endpoints.sh adsomnia-api-1766519149
```

### Interactive API Documentation

Visit: https://adsomnia-backend-3naijkhxba-uc.a.run.app/docs

1. Click the **"Authorize"** button
2. Enter API Key: `adsomnia-api-1766519149`
3. Test all endpoints interactively

## API Endpoints

All workflow endpoints require the `X-API-Key` header:

### Workflows

- `POST /api/workflows/wf1/tracking-link` - Generate tracking link
- `POST /api/workflows/wf2/top-landing-pages` - Get top landing pages
- `POST /api/workflows/wf3/export-report` - Export report
- `POST /api/workflows/wf3/fetch-conversions` - Fetch conversions
- `PUT /api/workflows/wf3/conversions/{id}/status` - Update conversion status
- `POST /api/workflows/wf3/conversions/bulk-status` - Bulk status update
- `POST /api/workflows/wf4/default-lp-alert` - Default LP alert
- `POST /api/workflows/wf5/paused-partners` - Paused partners check
- `POST /api/workflows/wf6/weekly-summary` - Weekly summary

### Entities

- `GET /api/entities/affiliates` - Get affiliates
- `GET /api/entities/offers` - Get offers
- `GET /api/entities/all` - Get all entities

### Health & Info

- `GET /health` - Health check (no auth)
- `GET /docs` - Interactive API docs
- `GET /openapi.json` - OpenAPI schema

## Example Requests

### WF1 - Generate Tracking Link

```bash
curl -X POST https://adsomnia-backend-3naijkhxba-uc.a.run.app/api/workflows/wf1/tracking-link \
  -H "X-API-Key: adsomnia-api-1766519149" \
  -H "Content-Type: application/json" \
  -d '{
    "affiliate_id": 12345,
    "offer_id": 1001
  }'
```

**Response:**
```json
{
  "status": "success",
  "tracking_link": "https://tracking.everflow.io/aff_c?offer_id=1001&aff_id=12345",
  "message": "Tracking link generated for Partner 12345 on Offer 1001",
  "requires_approval": false
}
```

### WF2 - Top Landing Pages

```bash
curl -X POST https://adsomnia-backend-3naijkhxba-uc.a.run.app/api/workflows/wf2/top-landing-pages \
  -H "X-API-Key: adsomnia-api-1766519149" \
  -H "Content-Type: application/json" \
  -d '{
    "offer_id": 1001,
    "country_code": "US",
    "days": 30,
    "min_leads": 5,
    "top_n": 3
  }'
```

### WF6 - Weekly Summary

```bash
curl -X POST https://adsomnia-backend-3naijkhxba-uc.a.run.app/api/workflows/wf6/weekly-summary \
  -H "X-API-Key: adsomnia-api-1766519149" \
  -H "Content-Type: application/json" \
  -d '{
    "days": 7,
    "group_by": "country"
  }'
```

## Managing the API Key

### Update the API Key

To set a new API key:

```bash
./set_api_key.sh "your-new-api-key"
```

Or manually:

```bash
echo -n "your-new-api-key" | gcloud secrets versions add API_KEY \
  --data-file=- \
  --project=p-power-up-ai

# Update Cloud Run to use the new key
gcloud run services update adsomnia-backend \
  --region=us-central1 \
  --project=p-power-up-ai \
  --update-secrets API_KEY=API_KEY:latest
```

### Retrieve the API Key

If you have permission:

```bash
gcloud secrets versions access latest --secret=API_KEY --project=p-power-up-ai
```

### View Secret Information

```bash
gcloud secrets describe API_KEY --project=p-power-up-ai
```

## Security Notes

- ✅ API key is stored in Google Secret Manager
- ✅ Never commit API keys to git
- ✅ Rotate keys periodically for security
- ✅ Use different keys for different environments (dev/staging/prod)

## Troubleshooting

### "Invalid API key" Error

1. Verify you're using the correct key: `adsomnia-api-1766519149`
2. Check the `X-API-Key` header is set correctly
3. Ensure Cloud Run service has the latest secret version

### "API key required" Error

Make sure you're including the header:
```bash
-H "X-API-Key: adsomnia-api-1766519149"
```

### Service Not Responding

Check service status:
```bash
gcloud run services describe adsomnia-backend \
  --region=us-central1 \
  --project=p-power-up-ai
```

View logs:
```bash
gcloud run services logs read adsomnia-backend \
  --region=us-central1 \
  --project=p-power-up-ai
```

## Deployment Information

- **Project:** p-power-up-ai
- **Region:** us-central1
- **Service:** adsomnia-backend
- **Service Account:** cursoraiblablabuild@p-power-up-ai.iam.gserviceaccount.com
- **Deployed:** December 23, 2025

## Related Files

- `test_api_endpoints.sh` - Test script for all endpoints
- `set_api_key.sh` - Script to update the API key
- `cloudbuild-sa.yaml` - Cloud Build configuration
- `DEPLOYMENT.md` - Full deployment documentation

