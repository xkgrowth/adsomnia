# Vercel Environment Variables

This document lists all environment variables needed for Vercel deployment.

## Required Variables

### Frontend (Next.js) - Public Variables

These variables are exposed to the browser and must have the `NEXT_PUBLIC_` prefix:

```env
# Backend API Configuration
NEXT_PUBLIC_API_URL=https://your-backend-api-url.com
NEXT_PUBLIC_API_KEY=your-secret-api-key-here
```

**Notes:**
- `NEXT_PUBLIC_API_URL`: The URL where your backend API is hosted (e.g., `https://api.adsomnia.com` or a Railway/Render URL)
- `NEXT_PUBLIC_API_KEY`: Must match the `API_KEY` set in your backend API server

### Optional Frontend Variables

These are optional and only needed if you want to manually override entity IDs:

```env
# Manual Override: Real Affiliate IDs (if Everflow API is not working)
# Format: JSON array, e.g., [{"id": 123, "name": "Partner Name"}, {"id": 456, "name": "Another Partner"}]
NEXT_PUBLIC_AFFILIATE_IDS=

# Manual Override: Real Offer IDs (if Everflow API is not working)
# Format: JSON array, e.g., [{"id": 1001, "name": "Summer Promo"}, {"id": 1002, "name": "Holiday Special"}]
NEXT_PUBLIC_OFFER_IDS=
```

## Backend API Variables

**Important:** These variables are NOT set in Vercel. They must be set in your backend API server environment (wherever you're hosting the FastAPI backend - e.g., Railway, Render, AWS, etc.).

### Required Backend Variables

```env
# API Authentication
API_KEY=your-secret-api-key-here

# Google Gemini API (for LLM agent)
GEMINI_KEY=AIzaSyCyQZSu3xR_nmXSypcs66m7mQHpEv7npz0
# OR
GOOGLE_API_KEY=AIzaSyCyQZSu3xR_nmXSypcs66m7mQHpEv7npz0

# Everflow API
EVERFLOW_API_KEY=UfaeyR2GQYC7Rc5gweKAQ
EVERFLOW_BASE_URL=https://api.eflow.team
EVERFLOW_TIMEZONE_ID=67
```

### Optional Backend Variables

```env
# Gemini Model (defaults to gemini-2.5-flash-lite if not set)
GEMINI_MODEL=google_genai:gemini-2.5-flash-lite

# LangSmith Tracing (optional, for debugging)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your-langsmith-key
```

## Vercel Setup Instructions

1. **Go to your Vercel project settings**
   - Navigate to: Settings → Environment Variables

2. **Add the required variables:**
   - `NEXT_PUBLIC_API_URL` - Your backend API URL
   - `NEXT_PUBLIC_API_KEY` - Your API key (must match backend)

3. **Set environment for each variable:**
   - Production: ✅ (for production deployments)
   - Preview: ✅ (for preview deployments)
   - Development: ✅ (optional, for local dev)

4. **Redeploy after adding variables:**
   - Vercel will automatically redeploy, or you can trigger a manual redeploy

## Important Notes

### Security
- **Never commit `.env` files** to git
- `NEXT_PUBLIC_*` variables are exposed to the browser - don't put secrets there
- Keep `API_KEY` secure and rotate it regularly
- Backend API keys (`EVERFLOW_API_KEY`, `GEMINI_KEY`) should never be in Vercel - only in your backend server

### Backend API Hosting
If you're hosting the backend separately (recommended):
- Set backend variables in your backend hosting platform (Railway, Render, etc.)
- Set `NEXT_PUBLIC_API_URL` in Vercel to point to your backend URL
- Ensure CORS is configured in your backend to allow requests from your Vercel domain

### Testing
After deployment, test that:
1. Frontend can connect to backend API
2. Example questions load with real affiliate/offer names
3. Chat endpoint returns responses
4. API authentication works correctly

## Example Vercel Configuration

```
Environment Variables in Vercel:
┌─────────────────────────────┬─────────────────────────────────────┐
│ Variable                    │ Value                               │
├─────────────────────────────┼─────────────────────────────────────┤
│ NEXT_PUBLIC_API_URL         │ https://api.adsomnia.com           │
│ NEXT_PUBLIC_API_KEY         │ your-secret-api-key-here            │
└─────────────────────────────┴─────────────────────────────────────┘

Backend API Server (Railway/Render/etc.):
┌─────────────────────────────┬─────────────────────────────────────┐
│ Variable                    │ Value                               │
├─────────────────────────────┼─────────────────────────────────────┤
│ API_KEY                     │ your-secret-api-key-here            │
│ GEMINI_KEY                  │ AIzaSyCyQZSu3xR_nmXSypcs66m7mQHp... │
│ EVERFLOW_API_KEY            │ UfaeyR2GQYC7Rc5gweKAQ               │
│ EVERFLOW_BASE_URL           │ https://api.eflow.team              │
│ EVERFLOW_TIMEZONE_ID        │ 67                                  │
└─────────────────────────────┴─────────────────────────────────────┘
```

