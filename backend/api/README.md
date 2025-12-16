# Adsomnia Workflow API

FastAPI REST API endpoints for all Everflow workflows (WF1-WF6).

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Add to your `.env` file:

```env
# API Authentication
API_KEY=your-secret-api-key-here

# Everflow API (already configured)
EVERFLOW_API_KEY=your_everflow_api_key
EVERFLOW_BASE_URL=https://api.eflow.team
EVERFLOW_TIMEZONE_ID=67

# Google Gemini (for agent, optional for API)
GEMINI_KEY=your_google_api_key
```

### 3. Run the API Server

```bash
# Option 1: Using Python module
python -m backend.api.main

# Option 2: Using uvicorn directly
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

All workflow endpoints require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secret-api-key-here" http://localhost:8000/api/workflows/...
```

### Workflow Endpoints

#### WF1 - Generate Tracking Link
```bash
POST /api/workflows/wf1/tracking-link
```

**Request:**
```json
{
  "affiliate_id": 12345,
  "offer_id": 1001
}
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

#### WF2 - Top Landing Pages
```bash
POST /api/workflows/wf2/top-landing-pages
```

**Request:**
```json
{
  "offer_id": 1001,
  "country_code": "US",
  "days": 30,
  "min_leads": 20,
  "top_n": 3
}
```

**Response:**
```json
{
  "status": "success",
  "offer_id": 1001,
  "country_code": "US",
  "period_days": 30,
  "top_lps": [
    {
      "offer_url_name": "Summer Sale LP v2",
      "conversion_rate": 4.85,
      "clicks": 12450,
      "conversions": 604
    }
  ]
}
```

#### WF3 - Export Report
```bash
POST /api/workflows/wf3/export-report
```

**Request:**
```json
{
  "report_type": "fraud",
  "date_range": "last week",
  "columns": ["sub1", "sub2", "affiliate"],
  "filters": {
    "offer_id": 1001
  }
}
```

**Response:**
```json
{
  "status": "success",
  "report_type": "fraud",
  "date_range": "last week",
  "download_url": "https://api.everflow.io/exports/fraud_report_123.csv",
  "expires_in": "24 hours"
}
```

#### WF4 - Default LP Alert
```bash
POST /api/workflows/wf4/default-lp-alert
```

**Request:**
```json
{
  "date": "2024-12-15",
  "click_threshold": 50
}
```

**Response:**
```json
{
  "status": "success",
  "alerts": [],
  "message": "No default LP traffic detected above threshold"
}
```

#### WF5 - Paused Partner Check
```bash
POST /api/workflows/wf5/paused-partners
```

**Request:**
```json
{
  "analysis_days": 3,
  "drop_threshold": -50.0
}
```

**Response:**
```json
{
  "status": "success",
  "alerts": [],
  "message": "No partners with significant volume drops detected"
}
```

#### WF6 - Weekly Summary
```bash
POST /api/workflows/wf6/weekly-summary
```

**Request:**
```json
{
  "days": 7,
  "group_by": "country"
}
```

**Response:**
```json
{
  "status": "success",
  "period_days": 7,
  "group_by": "country",
  "total_revenue": 45230.00,
  "total_conversions": 1856,
  "data": [
    {
      "name": "United States",
      "revenue": 18500.00,
      "conversions": 756,
      "clicks": 45230
    }
  ]
}
```

### Health Check

```bash
GET /health
```

No authentication required.

## Example Usage

### Python Example

```python
import requests

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"

headers = {"X-API-Key": API_KEY}

# WF1 - Generate tracking link
response = requests.post(
    f"{API_BASE}/api/workflows/wf1/tracking-link",
    json={"affiliate_id": 12345, "offer_id": 1001},
    headers=headers
)
print(response.json())

# WF2 - Get top landing pages
response = requests.post(
    f"{API_BASE}/api/workflows/wf2/top-landing-pages",
    json={
        "offer_id": 1001,
        "country_code": "US",
        "days": 30,
        "top_n": 3
    },
    headers=headers
)
print(response.json())
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# WF1 - Generate tracking link
curl -X POST http://localhost:8000/api/workflows/wf1/tracking-link \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"affiliate_id": 12345, "offer_id": 1001}'

# WF2 - Top landing pages
curl -X POST http://localhost:8000/api/workflows/wf2/top-landing-pages \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"offer_id": 1001, "country_code": "US", "days": 30, "top_n": 3}'
```

## Project Structure

```
backend/api/
├── __init__.py
├── main.py              # FastAPI app entry point
├── models.py            # Pydantic request/response models
├── deps.py             # Dependencies (auth, etc.)
├── routes/
│   ├── __init__.py
│   ├── workflows.py    # All workflow endpoints (WF1-WF6)
│   └── health.py       # Health check endpoints
└── README.md           # This file
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid API key
- `500 Internal Server Error` - Server error

Error responses follow this format:

```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE"
}
```

## Development

### Running in Development Mode

```bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

Use the interactive API documentation at http://localhost:8000/docs to test endpoints directly in your browser.

## Security Notes

- **API Key**: Set a strong API key in your `.env` file
- **CORS**: Currently allows all origins. Restrict in production
- **HTTPS**: Use HTTPS in production
- **Rate Limiting**: Consider adding rate limiting for production use

