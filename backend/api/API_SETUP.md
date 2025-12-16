# API Setup Complete ✅

All workflow functions have been converted to REST API endpoints using FastAPI.

## What Was Created

### 1. FastAPI Application Structure
```
backend/api/
├── __init__.py
├── main.py              # FastAPI app entry point
├── models.py            # Pydantic request/response models for all workflows
├── deps.py              # Authentication dependency
├── routes/
│   ├── __init__.py
│   ├── workflows.py     # All 6 workflow endpoints (WF1-WF6)
│   └── health.py        # Health check endpoint
├── README.md            # Complete API documentation
├── test_api.py          # Test script for all endpoints
├── start_server.sh      # Quick start script
└── API_SETUP.md         # This file
```

### 2. API Endpoints Created

| Endpoint | Method | Workflow | Description |
|----------|--------|----------|-------------|
| `/api/workflows/wf1/tracking-link` | POST | WF1 | Generate tracking link |
| `/api/workflows/wf2/top-landing-pages` | POST | WF2 | Get top landing pages |
| `/api/workflows/wf3/export-report` | POST | WF3 | Export CSV report |
| `/api/workflows/wf4/default-lp-alert` | POST | WF4 | Check default LP alerts |
| `/api/workflows/wf5/paused-partners` | POST | WF5 | Check paused partners |
| `/api/workflows/wf6/weekly-summary` | POST | WF6 | Get weekly summary |
| `/health` | GET | - | Health check |
| `/` | GET | - | API info |

### 3. Features

✅ **Authentication**: API key authentication via `X-API-Key` header  
✅ **Request Validation**: Pydantic models validate all inputs  
✅ **Response Models**: Structured JSON responses  
✅ **Error Handling**: Proper HTTP status codes and error messages  
✅ **CORS**: Configured for cross-origin requests  
✅ **Auto Documentation**: Swagger UI at `/docs` and ReDoc at `/redoc`  
✅ **Type Safety**: Full type hints throughout  

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install FastAPI and dependencies
pip install -r requirements.txt
```

### 2. Set API Key

Add to your `.env` file:

```env
API_KEY=your-secret-api-key-here
```

### 3. Start the Server

**Option 1: Using the start script**
```bash
./backend/api/start_server.sh
```

**Option 2: Using uvicorn directly**
```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: Using Python module**
```bash
python -m backend.api.main
```

### 4. Access the API

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Using the Test Script

```bash
# Update API_KEY in test_api.py first
python backend/api/test_api.py
```

### Using cURL

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# WF1 - Generate tracking link
curl -X POST http://localhost:8000/api/workflows/wf1/tracking-link \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"affiliate_id": 12345, "offer_id": 1001}'
```

### Using the Interactive Docs

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Enter your API key
4. Test endpoints directly in the browser

## Example Requests

### WF1 - Generate Tracking Link
```json
POST /api/workflows/wf1/tracking-link
{
  "affiliate_id": 12345,
  "offer_id": 1001
}
```

### WF2 - Top Landing Pages
```json
POST /api/workflows/wf2/top-landing-pages
{
  "offer_id": 1001,
  "country_code": "US",
  "days": 30,
  "min_leads": 20,
  "top_n": 3
}
```

### WF3 - Export Report
```json
POST /api/workflows/wf3/export-report
{
  "report_type": "fraud",
  "date_range": "last week",
  "columns": ["sub1", "sub2", "affiliate"],
  "filters": {"offer_id": 1001}
}
```

## Integration with Existing Code

The API endpoints use the same workflow functions from `backend/sql_agent/workflow_tools.py`:

- `wf1_generate_tracking_link()` → `/api/workflows/wf1/tracking-link`
- `wf2_identify_top_lps()` → `/api/workflows/wf2/top-landing-pages`
- `wf3_export_report()` → `/api/workflows/wf3/export-report`
- `wf4_check_default_lp_alert()` → `/api/workflows/wf4/default-lp-alert`
- `wf5_check_paused_partners()` → `/api/workflows/wf5/paused-partners`
- `wf6_generate_weekly_summary()` → `/api/workflows/wf6/weekly-summary`

This means:
- ✅ All existing workflow logic is reused
- ✅ When you implement real Everflow API calls, they'll work in both the agent and API
- ✅ Consistent behavior across both interfaces

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set API key**: Add `API_KEY` to `.env`
3. **Start server**: Run `./backend/api/start_server.sh`
4. **Test endpoints**: Use `/docs` or `test_api.py`
5. **Integrate with frontend**: Update Next.js app to call these endpoints

## Security Notes

- 🔒 API key authentication is required for all workflow endpoints
- 🌐 CORS is currently open - restrict in production
- 🔐 Use HTTPS in production
- ⚡ Consider adding rate limiting for production use

## Documentation

Full API documentation is available at:
- **README.md**: Complete endpoint documentation with examples
- **Interactive Docs**: http://localhost:8000/docs (when server is running)

