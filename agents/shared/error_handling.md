# Error Handling Guidelines

> Standardized error handling patterns for the Talk-to-Data agent.

## Error Categories

### 1. API Errors

Errors from Everflow API calls.

| Error Code | Cause | User Message | Action |
|------------|-------|--------------|--------|
| 401 | Invalid API key | "I'm having authentication issues. Please contact support." | Log, alert admin |
| 400 | Bad request params | "I couldn't process that request. Could you rephrase?" | Log, show details |
| 404 | Resource not found | "I couldn't find [resource]. Can you verify the ID?" | Suggest alternatives |
| 429 | Rate limited | "I'm processing too many requests. Give me a moment." | Exponential backoff |
| 500 | Server error | "The data service is temporarily unavailable." | Retry 3x, then fail |
| Timeout | Network timeout | "The request is taking longer than expected..." | Retry with longer timeout |

### 2. Validation Errors

Errors from input validation.

| Error Type | Example | User Message |
|------------|---------|--------------|
| Missing required entity | No offer ID | "Which offer would you like me to analyze?" |
| Invalid entity format | offer_id = "abc" | "Offer ID should be a number. Did you mean Offer 123?" |
| Invalid date range | "next month" | "I can only analyze historical data. Try 'last month' instead." |
| Future date | from > today | "I can't see into the future! Let me check historical data." |

### 3. Business Logic Errors

Errors from workflow logic.

| Error Type | Cause | User Message |
|------------|-------|--------------|
| Insufficient data | < 20 conversions | "Not enough data yet for reliable analysis. Need X more conversions." |
| No results | Empty dataset | "No data found for those criteria. Try expanding the date range." |
| Permission denied | Affiliate blocked | "This partner's account is currently restricted." |
| Duplicate action | Already approved | "Good news - Partner X is already approved for this offer!" |

### 4. System Errors

Internal application errors.

| Error Type | Cause | User Message |
|------------|-------|--------------|
| Unhandled exception | Bug in code | "Something went wrong on my end. I've logged the issue." |
| Configuration error | Missing env var | "I'm not properly configured. Please contact support." |
| Scheduler failure | Job failed | [Admin alert only, not user-facing] |

---

## Error Response Structure

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ErrorCategory(Enum):
    API = "api"
    VALIDATION = "validation"
    BUSINESS = "business"
    SYSTEM = "system"

class ErrorSeverity(Enum):
    LOW = "low"           # User can retry or rephrase
    MEDIUM = "medium"     # Needs different approach
    HIGH = "high"         # Requires admin attention
    CRITICAL = "critical" # System failure

@dataclass
class AgentError:
    category: ErrorCategory
    severity: ErrorSeverity
    code: str
    user_message: str
    internal_message: str
    suggestions: Optional[list[str]] = None
    retry_allowed: bool = True
    
    def to_user_response(self) -> str:
        response = self.user_message
        if self.suggestions:
            response += "\n\nYou could try:\n"
            for suggestion in self.suggestions:
                response += f"• {suggestion}\n"
        return response
```

---

## Error Handling Patterns

### Pattern 1: Graceful Degradation

```python
async def get_top_lps_with_fallback(offer_id: int, country: str = None):
    """Try with country filter, fall back to all countries."""
    try:
        # Try specific query
        return await get_top_lps(offer_id, country)
    except NoDataError:
        if country:
            # Fall back to broader query
            return await get_top_lps(offer_id, country=None)
        raise
```

### Pattern 2: Retry with Backoff

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    *args, **kwargs
) -> T:
    """Retry function with exponential backoff."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except (TimeoutError, RateLimitError) as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
    
    raise last_error
```

### Pattern 3: User-Friendly Validation

```python
def validate_and_suggest(offer_id: str) -> int:
    """Validate offer ID with helpful suggestions."""
    
    # Try to parse as integer
    try:
        return int(offer_id)
    except ValueError:
        pass
    
    # Maybe it's an offer name?
    matches = search_offers_by_name(offer_id)
    if matches:
        suggestions = [f"Offer {m['id']}: {m['name']}" for m in matches[:3]]
        raise ValidationError(
            user_message=f"'{offer_id}' doesn't look like an offer ID.",
            suggestions=suggestions
        )
    
    raise ValidationError(
        user_message=f"I couldn't find an offer matching '{offer_id}'.",
        suggestions=["Check the offer ID in Everflow", "Try the exact offer name"]
    )
```

### Pattern 4: Contextual Error Messages

```python
def format_api_error(error: APIError, context: dict) -> str:
    """Format API error with context."""
    
    base_messages = {
        404: "I couldn't find {resource_type} {resource_id}.",
        429: "I'm being rate limited. Please wait {retry_after} seconds.",
        500: "The Everflow service is having issues.",
    }
    
    message = base_messages.get(error.status_code, "An unexpected error occurred.")
    return message.format(**context, **error.details)
```

---

## Logging Standards

### What to Log

```python
# ✅ DO log:
logger.error(
    "API call failed",
    extra={
        "workflow": "WF2",
        "operation": "get_entity_report",
        "status_code": 500,
        "duration_ms": 2340,
        "offer_id": 123,  # IDs are OK
        "error_type": "ServerError",
    }
)

# ❌ DON'T log:
logger.error(
    "API call failed",
    extra={
        "response_body": response.json(),  # May contain PII
        "affiliate_name": "John Doe",       # PII
        "revenue": 5230.50,                 # Sensitive business data
        "api_key": api_key,                 # Credentials!
    }
)
```

### Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| DEBUG | Development details | Request/response structure |
| INFO | Normal operations | "Workflow WF2 completed in 1.2s" |
| WARNING | Recoverable issues | "Rate limit approaching, slowing down" |
| ERROR | Failed operations | "API call failed after 3 retries" |
| CRITICAL | System failures | "Database connection lost" |

---

## User-Facing Error Templates

### Template: Resource Not Found

```
I couldn't find {resource_type} {identifier}.

This could mean:
• The {resource_type} ID is incorrect
• The {resource_type} was archived or deleted
• You might not have access to this {resource_type}

Would you like me to search for {resource_type}s by name instead?
```

### Template: Insufficient Data

```
I found {resource_type} {identifier}, but there isn't enough data yet 
for reliable analysis.

Current data:
• {metric}: {current_value} (minimum needed: {required_value})

Options:
1. Expand the date range to include more data
2. Lower the minimum threshold (results may be less reliable)
3. Check back in a few days when more data is available
```

### Template: Rate Limited

```
I'm processing a lot of requests right now and need to slow down 
for a moment.

⏳ Please wait about {seconds} seconds...

[Auto-retry in progress]
```

### Template: System Error

```
Something unexpected happened while processing your request. 
I've logged the issue for the technical team.

In the meantime, you could:
• Try your request again
• Rephrase your question
• Contact support if this keeps happening

Error reference: {error_id}
```

---

## Recovery Strategies

### For API Failures

```
1. Timeout (30s) → Retry with 60s timeout
2. Rate limit → Exponential backoff (1s, 2s, 4s)
3. Server error → Retry 3x, then fail gracefully
4. Auth error → Alert admin, stop retrying
```

### For Validation Failures

```
1. Missing entity → Ask clarifying question
2. Ambiguous input → Show options
3. Invalid format → Suggest correct format
4. Out of range → Suggest valid range
```

### For Business Logic Failures

```
1. No data → Suggest broader criteria
2. Insufficient data → Offer alternatives
3. Permission denied → Explain limitation
4. Already done → Confirm current state
```

---

## Testing Error Handling

### Unit Tests

```python
def test_api_timeout_retry():
    """Verify retry behavior on timeout."""
    mock_api.timeout_first_n_calls(2)
    result = await retry_with_backoff(api_call)
    assert result is not None
    assert mock_api.call_count == 3

def test_validation_error_message():
    """Verify user-friendly validation error."""
    error = validate_offer_id("not-a-number")
    assert "doesn't look like an offer ID" in error.user_message
    assert error.suggestions is not None
```

### Integration Tests

```python
def test_graceful_degradation():
    """Verify fallback to broader query."""
    # No data for US specifically
    mock_api.return_empty_for(country="US")
    
    result = await get_top_lps(offer_id=123, country="US")
    
    # Should fall back to all countries
    assert result is not None
    assert result.note == "Showing results for all countries"
```

---

## Monitoring & Alerts

### Error Rate Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| API error rate | > 5% | > 20% |
| Timeout rate | > 10% | > 30% |
| Validation error rate | > 30% | N/A |
| Unhandled exceptions | > 0.1% | > 1% |

### Admin Alerts

```python
# Alert on critical errors
if error.severity == ErrorSeverity.CRITICAL:
    await send_admin_alert(
        channel="slack",
        message=f"🚨 Critical error in {error.code}",
        details=error.internal_message
    )
```

