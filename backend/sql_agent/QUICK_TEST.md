# Quick Test Guide

## Running Tests

### 1. Test Workflow Tools (No LLM Required)

This test verifies all 6 workflow tools are properly configured:

```bash
source venv/bin/activate
python -m backend.sql_agent.test_workflow_tools
```

**Expected Output:**
- ✅ All 6 workflow tools loaded
- ✅ All tools can be executed
- ✅ Returns placeholder JSON data

### 2. Test Full Agent (Requires Azure OpenAI)

Once you've added Azure OpenAI credentials to `.env`:

```bash
source venv/bin/activate
python -m backend.sql_agent.test_agent
```

**Expected Output:**
- ✅ Environment variables validated
- ✅ Agent built successfully
- ✅ Test queries executed

### 3. Interactive Testing

Run example queries:

```bash
source venv/bin/activate
python -m backend.sql_agent.main
```

## Environment Variables Required

### For Workflow Tools Only:
- `EVERFLOW_API_KEY` ✅ (you have this)
- `EVERFLOW_BASE_URL` ✅ (you have this)

### For Full Agent:
- `AZURE_OPENAI_API_KEY` ⚠️ (needed)
- `AZURE_OPENAI_ENDPOINT` ⚠️ (needed)
- `AZURE_OPENAI_DEPLOYMENT_NAME` ⚠️ (needed)
- `OPENAI_API_VERSION` (optional, defaults to 2025-03-01-preview)

## Current Status

✅ **Workflow Tools:** All 6 tools working  
⏳ **Full Agent:** Waiting for Azure OpenAI setup  
⏳ **API Integration:** Placeholder data (needs Everflow API implementation)

