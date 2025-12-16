# 🚀 API Server - Quick Start

## ✅ Setup Complete!

All dependencies have been installed and the API is ready to run.

## Start the Server

Run this command in your terminal:

```bash
cd /Users/danieldevos/Documents/BLABLABUILD/adsomnia
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the start script:

```bash
./backend/api/start_server.sh
```

## Access the API

Once the server is running, access:

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Key

The API uses API key authentication. Set in `.env`:

```env
API_KEY=your-secret-api-key-here
```

Or use the default: `your-secret-api-key-here`

## Test Endpoints

### Using cURL

```bash
# Health check (no auth)
curl http://localhost:8000/health

# WF1 - Generate tracking link
curl -X POST http://localhost:8000/api/workflows/wf1/tracking-link \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"affiliate_id": 12345, "offer_id": 1001}'
```

### Using Python Test Script

```bash
# Update API_KEY in test_api.py first
python backend/api/test_api.py
```

### Using Interactive Docs

1. Start server
2. Open http://localhost:8000/docs
3. Click "Authorize" button
4. Enter API key: `your-secret-api-key-here`
5. Test endpoints directly in browser

## All Endpoints

- `POST /api/workflows/wf1/tracking-link` - Generate tracking link
- `POST /api/workflows/wf2/top-landing-pages` - Get top landing pages
- `POST /api/workflows/wf3/export-report` - Export CSV report
- `POST /api/workflows/wf4/default-lp-alert` - Check default LP alerts
- `POST /api/workflows/wf5/paused-partners` - Check paused partners
- `POST /api/workflows/wf6/weekly-summary` - Get weekly summary
- `GET /health` - Health check

## Status

✅ Dependencies installed (FastAPI, Uvicorn, Pydantic)  
✅ API code ready  
✅ All 6 workflow endpoints configured  
✅ Authentication middleware ready  
✅ Auto-documentation enabled  

**Ready to start!** 🎉

