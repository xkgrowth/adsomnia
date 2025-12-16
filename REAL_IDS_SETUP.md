# Setting Up Real IDs for Example Questions

Since the Everflow API is currently returning errors, you can manually configure real affiliate and offer IDs to use in the example questions.

## Option 1: Environment Variables (Recommended)

Create a `.env.local` file in the project root with your real IDs:

```env
# Real Affiliate IDs (JSON array)
NEXT_PUBLIC_AFFILIATE_IDS=[{"id": 123, "name": "Partner Name"}, {"id": 456, "name": "Another Partner"}]

# Real Offer IDs (JSON array)
NEXT_PUBLIC_OFFER_IDS=[{"id": 1001, "name": "Summer Promo"}, {"id": 1002, "name": "Holiday Special"}]
```

Or use simple number arrays:
```env
NEXT_PUBLIC_AFFILIATE_IDS=[123, 456, 789]
NEXT_PUBLIC_OFFER_IDS=[1001, 1002, 1003]
```

After adding these, restart your Next.js dev server.

## Option 2: Fix Everflow API Connection

The Everflow API is currently returning 400 "Internal error". To fix this:

1. **Check API Key Permissions**: Ensure your Everflow API key has access to reporting endpoints
2. **Verify API Key**: Check that `EVERFLOW_API_KEY` in `.env` is correct
3. **Check Account Status**: Verify your Everflow account is active and has data

Once the API connection is fixed, real IDs will be fetched automatically.

## Current Status

- ✅ Backend API server is running
- ✅ Frontend is calling the entities endpoint
- ❌ Everflow API returns 400 error
- ✅ Frontend falls back to test data (12345, 1001, etc.)

## Testing

Check your browser console (F12) to see:
- `Fetched entities response:` - Shows what the API returned
- `⚠️ No affiliates returned from API` - Confirms fallback is being used

