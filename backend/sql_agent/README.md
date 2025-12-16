# LangChain Workflow Orchestrator Agent

This module implements a workflow orchestrator agent following the [LangChain SQL Agent tutorial pattern](https://docs.langchain.com/oss/python/langchain/sql-agent#azure), adapted to work with Everflow workflows (WF1-WF6) instead of SQL databases.

The agent uses **Google Gemini** (following the LangChain tutorial) and routes natural language queries to the appropriate Everflow workflow.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with:

```env
# Google Gemini Configuration
GEMINI_KEY=your_google_api_key

# Everflow API Configuration
EVERFLOW_API_KEY=your_everflow_api_key
EVERFLOW_BASE_URL=https://api.eflow.team
EVERFLOW_TIMEZONE_ID=67

# Optional: LangSmith Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
```

## Usage

### Basic Agent (Steps 1-5)

Run the basic workflow orchestrator agent:

```bash
python -m backend.sql_agent.main
```

### Agent with Human-in-the-Loop Review (Step 7)

Run the agent with human review middleware (pauses for WF1 approval):

```python
from backend.sql_agent.agent_with_human_review import run_with_human_review, resume_execution

# Ask a question - agent will pause before executing workflow operations
for step in run_with_human_review("Generate tracking link for Partner 123 on Offer 456"):
    if "__interrupt__" in step:
        # Review the workflow operation, then approve or reject
        for step in resume_execution("approve"):
            print(step)
```

### LangGraph Studio (Step 6 - Optional)

To use LangGraph Studio:

1. Install Studio CLI:
```bash
pip install -U langgraph-cli[inmem]>=0.4.0
```

2. Start Studio:
```bash
langgraph dev
```

3. Open Studio in your browser and interact with the agent through the UI.

## Implementation Steps

This implementation follows the LangChain agent pattern, adapted for Everflow workflows:

- ✅ **Step 1**: Azure OpenAI LLM configuration
- ✅ **Step 2**: (Skipped - no database needed, using Everflow API)
- ✅ **Step 3**: Workflow tools setup (WF1-WF6) instead of SQL tools
- ✅ **Step 4**: Agent creation with workflow orchestration system prompt
- ✅ **Step 5**: Main script to run the agent with workflow examples
- ✅ **Step 6**: LangGraph Studio configuration (optional)
- ✅ **Step 7**: Human-in-the-loop review middleware (for WF1 write operations)

## Files Structure

```
backend/sql_agent/
├── __init__.py                    # Module initialization
├── config.py                      # Configuration (Azure OpenAI, Everflow API)
├── workflow_tools.py              # Workflow tools (WF1-WF6) for LangChain
├── workflow_agent.py              # Steps 1-4: Workflow orchestrator agent
├── main.py                        # Step 5: Main execution script
├── agent_with_human_review.py     # Step 7: Human-in-the-loop
├── sql_agent.py                   # Step 6: Studio configuration (legacy)
├── sql_agent_langgraph.py         # Step 6: LangGraph implementation (legacy)
├── agent.py                       # Legacy SQL agent (kept for reference)
├── setup_database.py              # Legacy database setup (kept for reference)
└── README.md                      # This file
```

## Example Queries

- "Which landing page is best for Offer 123?"
- "Export a fraud report for last week"
- "Give me the weekly performance summary"
- "Generate a tracking link for Partner 456 on Offer 789"
- "Show me top performing LPs for Offer 123 in Germany"
- "What partners have paused recently?"

## Security Notes

⚠️ **Important**: The agent interacts with the Everflow API and can perform write operations (WF1 - tracking link generation with approvals).

The agent is configured to:
- Require user confirmation for write operations (WF1)
- Use read-only operations for most workflows (WF2, WF3, WF4, WF5, WF6)
- Support human-in-the-loop review for WF1 operations
- Log all operations for audit purposes
- Never auto-approve affiliates without explicit confirmation

