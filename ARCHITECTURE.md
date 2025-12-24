# Architecture Document

## System Overview

The Adsomnia "Talk-to-Data" Agent is a conversational AI system that bridges natural language queries with the Everflow affiliate marketing API. The system processes user intent, executes appropriate API calls, and returns human-readable responses.

## Design Principles

1. **Ephemeral Processing**: No data persistence - all operations are real-time
2. **Security First**: Authentication required, no PII logging
3. **Modular Workflows**: Each workflow is independent and testable
4. **Graceful Degradation**: Clear error messages on failures
5. **Audit Trail**: Log operations (not data) for debugging

## Technology Stack

### Recommended Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js / React | Modern UI, SSR for auth |
| **Backend** | Python (FastAPI) | Strong data processing, LLM libraries |
| **LLM** | Claude / OpenAI | Natural language understanding |
| **Scheduler** | APScheduler / Celery | WF4, WF5 scheduled jobs |
| **Hosting** | Client-provisioned | Full data control |

### Alternative: Full Python Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit / Gradio |
| **Backend** | FastAPI |
| **LLM** | LangChain + Claude/OpenAI |

## Component Architecture

### 1. Chat Interface Layer

```
┌─────────────────────────────────────┐
│           Chat Interface             │
├─────────────────────────────────────┤
│ • Message input/output              │
│ • Conversation history (session)    │
│ • File download handling (WF3)      │
│ • Confirmation dialogs (WF1)        │
│ • Alert notifications (WF4, WF5)    │
└─────────────────────────────────────┘
```

**Responsibilities:**
- Render chat messages
- Handle user authentication
- Display confirmation prompts for write operations
- Present downloadable reports

### 2. LLM Agent Layer

```
┌─────────────────────────────────────┐
│           LLM Agent                  │
├─────────────────────────────────────┤
│ • Intent Classification             │
│ • Entity Extraction                 │
│ • Parameter Validation              │
│ • Response Generation               │
└─────────────────────────────────────┘
```

**Responsibilities:**
- Parse natural language to structured intent
- Extract entities: offer_id, country_code, affiliate_id, date ranges
- Map "last week" → actual timestamps
- Generate human-readable responses from data

**Intent Classification:**

| User Query Pattern | Detected Intent | Workflow |
|-------------------|-----------------|----------|
| "Which LP is best for..." | `analyze_lp_performance` | WF2 |
| "Export fraud report..." | `export_report` | WF3 |
| "Weekly summary for..." | `generate_summary` | WF6 |
| "Get tracking link for..." | `generate_tracking_link` | WF1 |

### 3. Workflow Orchestrator

```
┌─────────────────────────────────────┐
│       Workflow Orchestrator          │
├─────────────────────────────────────┤
│ • Route intent to workflow          │
│ • Manage multi-step operations      │
│ • Handle confirmations              │
│ • Aggregate results                 │
└─────────────────────────────────────┘
```

**Workflow Registry:**

```python
WORKFLOWS = {
    "WF1": GenerateTrackingLinksWorkflow,
    "WF2": TopPerformingLPsWorkflow,
    "WF3": ExportReportsWorkflow,
    "WF4": DefaultLPAlertWorkflow,      # Scheduled
    "WF5": PausedPartnerCheckWorkflow,  # Scheduled
    "WF6": WeeklySummaryWorkflow,
}
```

### 4. Everflow API Wrapper

```
┌─────────────────────────────────────┐
│       Everflow API Wrapper           │
├─────────────────────────────────────┤
│ • Standardized request/response     │
│ • Authentication handling           │
│ • Rate limit management             │
│ • Error translation                 │
└─────────────────────────────────────┘
```

**Core Methods:**

```python
class EverflowClient:
    async def get_entity_report(filters, columns, date_range) -> Report
    async def get_conversion_report(filters) -> Report
    async def export_to_csv(report_type, filters) -> DownloadURL
    async def set_offer_visibility(affiliate_id, offer_id, status) -> bool
    async def generate_tracking_link(affiliate_id, offer_id) -> TrackingURL
```

## Data Flow

### Read Operations (WF2, WF3, WF6)

```
User Query
    │
    ▼
┌─────────────┐
│  LLM Parse  │ ──▶ Extract: offer_id, country, date_range
└─────────────┘
    │
    ▼
┌─────────────┐
│  API Call   │ ──▶ POST /v1/networks/reporting/entity
└─────────────┘
    │
    ▼
┌─────────────┐
│  Process    │ ──▶ Filter, Calculate, Sort (Python)
└─────────────┘
    │
    ▼
┌─────────────┐
│  Format     │ ──▶ Generate natural language response
└─────────────┘
    │
    ▼
User Response
```

### Write Operations (WF1)

```
User Query: "Get link for Partner 123, Offer 456"
    │
    ▼
┌─────────────┐
│  LLM Parse  │ ──▶ Extract: affiliate_id=123, offer_id=456
└─────────────┘
    │
    ▼
┌─────────────┐
│ Check Status│ ──▶ Is partner approved for this offer?
└─────────────┘
    │
    ├── YES ──────────────────────┐
    │                             │
    ▼                             │
┌─────────────┐                   │
│ CONFIRM UI  │ ◀── NO            │
│"Auto-approve│                   │
│  partner?"  │                   │
└─────────────┘                   │
    │                             │
    ▼ (User confirms)             │
┌─────────────┐                   │
│ Approve API │                   │
└─────────────┘                   │
    │                             │
    ▼                             ▼
┌─────────────────────────────────────┐
│        Generate Tracking Link        │
└─────────────────────────────────────┘
    │
    ▼
User Response: "Here's your tracking link: https://..."
```

### Scheduled Jobs (WF4, WF5)

```
┌─────────────────────────────────────┐
│           Scheduler                  │
│  ┌─────────┐        ┌─────────┐    │
│  │ WF4     │        │ WF5     │    │
│  │ 09:00AM │        │ Weekly  │    │
│  └────┬────┘        └────┬────┘    │
└───────┼──────────────────┼─────────┘
        │                  │
        ▼                  ▼
   ┌─────────┐        ┌─────────┐
   │ Execute │        │ Execute │
   │ Check   │        │ Compare │
   └────┬────┘        └────┬────┘
        │                  │
        ▼                  ▼
   ┌─────────┐        ┌─────────┐
   │ Alert?  │        │ Alert?  │
   └────┬────┘        └────┬────┘
        │                  │
        ▼                  ▼
   [Push Alert to UI / Notification]
```

## Security Architecture

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│  Auth    │────▶│  Session │
│  Login   │     │  Layer   │     │  Token   │
└──────────┘     └──────────┘     └──────────┘
                      │
                      ▼
              ┌──────────────┐
              │  Validate    │
              │  on Request  │
              └──────────────┘
```

### API Key Management

```
Environment Variables (Never in code):
├── EVERFLOW_API_KEY
├── LLM_API_KEY (OpenAI/Claude)
├── APP_SECRET_KEY
└── DATABASE_URL (if needed for sessions)
```

### Data Isolation

- **No persistent storage** of Everflow data
- **Session-only** conversation history
- **Logs contain** operation types, timestamps, errors
- **Logs never contain** actual data values, PII, API responses

## Error Handling Strategy

| Error Type | User Message | Internal Action |
|------------|--------------|-----------------|
| API Rate Limit | "I'm processing too many requests. Please wait a moment." | Exponential backoff |
| Invalid Entity | "I couldn't find Offer X. Can you check the ID?" | Log, suggest alternatives |
| Auth Failure | "Session expired. Please log in again." | Clear session, redirect |
| Network Error | "Having trouble connecting. Retrying..." | Auto-retry 3x |

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Client Infrastructure                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Web Server │  │  App Server │  │  Scheduler  │     │
│  │  (Nginx)    │  │  (FastAPI)  │  │  (Celery)   │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          │                              │
│                    ┌─────▼─────┐                        │
│                    │  Redis    │ (Session/Queue)        │
│                    └───────────┘                        │
└─────────────────────────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      [Everflow API]  [LLM API]    [Alert Channel]
```

## Performance Considerations

1. **Response Time Target**: < 5 seconds for read operations
2. **Concurrent Users**: Design for 5-10 simultaneous users
3. **API Caching**: None (per data freshness requirements)
4. **Rate Limits**: Respect Everflow limits, implement backoff

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit Tests | Workflow logic, data processing |
| Integration | API wrapper, LLM parsing |
| E2E | Full conversation flows |
| Load | Concurrent user simulation |

## Future Extensibility

The modular workflow design allows for:
- Adding new workflows without core changes
- Swapping LLM providers
- Adding new alert channels (Slack, Email)
- Extending to additional APIs beyond Everflow









