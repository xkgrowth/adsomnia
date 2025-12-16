# Vercel Environment Variables - Quick Guide

## ✅ All Variables to Set in Vercel

Since you're using **Next.js API routes (serverless functions)** instead of a separate backend, set ALL these variables in Vercel:

### Required Variables

```env
# Everflow API (for data fetching)
EVERFLOW_API_KEY=UfaeyR2GQYC7Rc5gweKAQ
EVERFLOW_BASE_URL=https://api.eflow.team
EVERFLOW_TIMEZONE_ID=67

# Google Gemini (for LLM processing)
GEMINI_KEY=AIzaSyCyQZSu3xR_nmXSypcs66m7mQHpEv7npz0
# OR use GOOGLE_API_KEY (both work)
GOOGLE_API_KEY=AIzaSyCyQZSu3xR_nmXSypcs66m7mQHpEv7npz0

# Context7 (for documentation)
CONTEXT7_API_KEY=ctx7sk-192ab289-7fe3-47f9-b8ea-b7c4cb7eaf9a

# Optional: Gemini Model (defaults to gemini-2.5-flash-lite)
GEMINI_MODEL=google_genai:gemini-2.5-flash-lite
```

### Optional Variables

```env
# LangSmith Tracing (optional, for debugging)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your-langsmith-key-if-using
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│  Vercel (Next.js App)               │
│                                     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │  Frontend   │  │  API Routes  │ │
│  │  (React)    │→ │  (Serverless)│ │
│  └─────────────┘  └──────┬───────┘ │
│                          │          │
│  All Environment         │          │
│  Variables Set Here      │          │
└──────────────────────────┼──────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼────┐      ┌──────▼──────┐   ┌──────▼──────┐
    │ Everflow│      │   Gemini    │   │  Context7   │
    │   API   │      │     API     │   │     API     │
    └─────────┘      └─────────────┘   └─────────────┘
```

## Setup Steps

### 1. Set All Variables in Vercel

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. Add each variable:
   - `EVERFLOW_API_KEY`
   - `EVERFLOW_BASE_URL`
   - `EVERFLOW_TIMEZONE_ID`
   - `GEMINI_KEY` (or `GOOGLE_API_KEY`)
   - `CONTEXT7_API_KEY`
   - `GEMINI_MODEL` (optional)

3. **Important**: Set environment scope:
   - ✅ **Production**
   - ✅ **Preview** 
   - ✅ **Development** (optional)

### 2. No Separate Backend Needed

- All API logic runs in Next.js API routes (serverless functions)
- No need for Railway, Render, or other backend hosting
- Everything runs on Vercel's serverless infrastructure

### 3. Redeploy

- Vercel will automatically redeploy after adding variables
- Or trigger a manual redeploy from the dashboard

## Important Notes

### Security
- ✅ These variables are **server-side only** (not `NEXT_PUBLIC_*`)
- ✅ They're only accessible in Next.js API routes, not in the browser
- ✅ Never expose these keys in client-side code

### How It Works
- Frontend calls Next.js API routes (e.g., `/api/chat/query`)
- API routes use these environment variables to call:
  - Everflow API (for data)
  - Gemini API (for LLM)
  - Context7 API (for docs)
- All processing happens server-side in Vercel's serverless functions

### No Database Needed
- All data is fetched on-demand from Everflow API
- No data storage required
- Stateless architecture

## Testing

After deployment, verify:
1. Frontend loads at your Vercel URL
2. Example questions appear with real affiliate/offer names
3. Clicking an example question returns a response
4. Check browser console for any errors
5. Check Vercel function logs for API call issues

