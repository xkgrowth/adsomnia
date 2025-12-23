# 🚀 Deploy to p-power-up-ai

## Quick Deploy

### Step 1: Authenticate with the Correct Account

```bash
gcloud auth login daniel@blablabuild.com
```

This will open your browser for authentication. Complete the sign-in process.

### Step 2: Run the Deployment Script

```bash
cd /Users/danieldevos/Documents/BLABLABUILD/adsomnia
./deploy_to_power_up.sh
```

The script will:
1. ✅ Verify authentication
2. ✅ Enable required Google Cloud APIs
3. ✅ Create secrets (API_KEY, GEMINI_KEY) automatically
4. ✅ Prompt you to create EVERFLOW_API_KEY manually
5. ✅ Build and deploy to Cloud Run

---

## Manual Steps (if needed)

### Create EVERFLOW_API_KEY Secret

If you need to create the Everflow API key manually:

```bash
# Replace YOUR_EVERFLOW_KEY with your actual key from .env
echo -n 'YOUR_EVERFLOW_KEY' | gcloud secrets create EVERFLOW_API_KEY \
    --data-file=- \
    --project=p-power-up-ai
```

### Update Existing Secrets

To update a secret after deployment:

```bash
# Update API_KEY
echo -n 'new-api-key' | gcloud secrets versions add API_KEY \
    --data-file=- \
    --project=p-power-up-ai

# Update GEMINI_KEY
echo -n 'new-gemini-key' | gcloud secrets versions add GEMINI_KEY \
    --data-file=- \
    --project=p-power-up-ai

# Update EVERFLOW_API_KEY
echo -n 'new-everflow-key' | gcloud secrets versions add EVERFLOW_API_KEY \
    --data-file=- \
    --project=p-power-up-ai
```

---

## After Deployment

Once deployed, you'll get a URL like:
```
https://adsomnia-backend-xxxxx-uc.a.run.app
```

### Test the Deployment

```bash
# Health check
curl https://adsomnia-backend-xxxxx-uc.a.run.app/health

# View API docs
open https://adsomnia-backend-xxxxx-uc.a.run.app/docs

# Test an endpoint
curl -X POST https://adsomnia-backend-xxxxx-uc.a.run.app/api/workflows/wf1/tracking-link \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"affiliate_id": 12345, "offer_id": 1001}'
```

---

## Viewing Logs

```bash
# View recent logs
gcloud run services logs read adsomnia-backend \
    --region us-central1 \
    --project p-power-up-ai

# Stream logs in real-time
gcloud run services logs tail adsomnia-backend \
    --region us-central1 \
    --project p-power-up-ai
```

---

## Troubleshooting

### "does not have permission to access projects"

Make sure you're authenticated with `daniel@blablabuild.com`:

```bash
gcloud auth list
gcloud config set account daniel@blablabuild.com
```

### Build Fails

Check the build logs:
```bash
gcloud builds list --project=p-power-up-ai --limit=5
```

### Secrets Not Found

List all secrets:
```bash
gcloud secrets list --project=p-power-up-ai
```

Create missing secrets as shown above.

---

## Project Configuration

- **Project ID**: `p-power-up-ai`
- **Region**: `us-central1`
- **Service Name**: `adsomnia-backend`
- **Resources**: 512Mi memory, 1 vCPU
- **Auto-scaling**: 0-10 instances

---

## Cost Estimate

Google Cloud Run pricing (pay-per-use):
- **Memory**: $0.00000250 per GiB-second
- **CPU**: $0.00002400 per vCPU-second  
- **Requests**: $0.40 per million requests

Expected cost for low-to-moderate usage: **$5-20/month**

The service automatically scales to zero when not in use, minimizing costs.

