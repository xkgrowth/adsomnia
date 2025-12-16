# Vercel Environment Variables - Quick Guide

## ✅ Variables to Set in Vercel

Based on your `.env` file, here's what you need to set in **Vercel only**:

### Required (Frontend Only)

```env
# Point to where your backend API is hosted
NEXT_PUBLIC_API_URL=https://your-backend-api-url.com

# API key to authenticate frontend requests to backend
# Must match the API_KEY in your backend server
NEXT_PUBLIC_API_KEY=your-secret-api-key-here
```

**That's it!** Only these 2 variables go in Vercel.

## ❌ Variables NOT Set in Vercel

These variables from your `.env` file go in your **backend API server** (Railway, Render, etc.), NOT in Vercel:

```env
# Backend API Server Variables (set where backend is hosted)
EVERFLOW_API_KEY=UfaeyR2GQYC7Rc5gweKAQ
EVERFLOW_BASE_URL=https://api.eflow.team
GEMINI_KEY=AIzaSyCyQZSu3xR_nmXSypcs66m7mQHpEv7npz0
API_KEY=your-secret-api-key-here  # Must match NEXT_PUBLIC_API_KEY
CONTEXT7_API_KEY=ctx7sk-192ab289-7fe3-47f9-b8ea-b7c4cb7eaf9a
```

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐
│  Vercel (Frontend)        │  Backend API     │
│  Next.js App              │  FastAPI Server  │
│                           │  (Railway/etc.)  │
│  Variables:                │  Variables:      │
│  - NEXT_PUBLIC_API_URL    │  - API_KEY       │
│  - NEXT_PUBLIC_API_KEY    │  - GEMINI_KEY    │
│                           │  - EVERFLOW_API_KEY
└────────┬────────┘         └────────┬─────────┘
         │                            │
         │  HTTP Requests              │
         └─────────────────────────────┘
```

## Setup Steps

### 1. Deploy Backend API First
- Deploy your FastAPI backend to Railway, Render, or similar
- Set backend variables there:
  - `API_KEY`
  - `GEMINI_KEY`
  - `EVERFLOW_API_KEY`
  - `EVERFLOW_BASE_URL`
  - `CONTEXT7_API_KEY` (if used)

### 2. Get Backend URL
- Note your backend API URL (e.g., `https://adsomnia-api.railway.app`)

### 3. Set Vercel Variables
- Go to Vercel → Your Project → Settings → Environment Variables
- Add:
  - `NEXT_PUBLIC_API_URL` = your backend URL
  - `NEXT_PUBLIC_API_KEY` = same value as `API_KEY` in backend

### 4. Redeploy
- Vercel will automatically redeploy with new variables

## Why This Setup?

- **Frontend (Vercel)**: Only needs to know where the backend is and how to authenticate
- **Backend (Separate Host)**: Handles all API calls, LLM processing, and secrets
- **No Database**: Everything is stateless - no data storage needed

## Testing

After deployment, verify:
1. Frontend loads at your Vercel URL
2. Example questions appear with real affiliate/offer names
3. Clicking an example question returns a response
4. Check browser console for any API connection errors

