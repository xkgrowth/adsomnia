# WF5: Identify Partners Who Paused + Alert

> **Phase:** 3 - The Alerter (Monitor & Alert)  
> **Type:** Scheduled Job (Comparative Analysis)  
> **Week:** 3

## Objective

Spot partners whose volume dropped significantly week-over-week. This is a comparative analysis job that calculates variance between current and previous period, alerting on significant drops.

## Trigger

- **Schedule:** Configurable (recommended: daily or every 3 days)
- **Analysis Window:** Last 3 days vs. same 3 days previous week
- **Type:** Automated/Proactive (not user-initiated)

## Alert Criteria

Alert is triggered when:
- `volume_delta` < **-50%** (drop greater than 50%)

Where: `volume_delta = (current_revenue - previous_revenue) / previous_revenue * 100`

## API Endpoint

```
POST /v1/networks/reporting/entity
```

Called **twice**: once for current period, once for previous period.

## Payload Construction

### Current Period (Last 3 Days)
```json
{
  "columns": ["affiliate"],
  "query": {
    "filters": []
  },
  "from": "CURRENT_START",
  "to": "CURRENT_END",
  "timezone_id": 67
}
```

### Previous Period (Same 3 Days Last Week)
```json
{
  "columns": ["affiliate"],
  "query": {
    "filters": []
  },
  "from": "PREVIOUS_START",
  "to": "PREVIOUS_END",
  "timezone_id": 67
}
```

## Workflow Logic

```python
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

# Configuration
CONFIG = {
    "schedule": "0 8 * * *",       # Daily at 8:00 AM
    "analysis_days": 3,             # Compare 3-day windows
    "drop_threshold": -50,          # Alert if drop > 50%
    "min_previous_revenue": 100,    # Minimum baseline revenue to compare
}


async def check_paused_partners() -> list[dict]:
    """
    Comparative analysis to identify partners with significant volume drops.
    
    Logic:
    1. Fetch current period data (last 3 days)
    2. Fetch previous period data (same 3 days last week)
    3. Compare revenue/conversions per affiliate
    4. Alert on drops > 50%
    
    Returns:
        List of partners with critical drops
    """
    
    # Calculate date ranges
    today = datetime.now()
    
    # Current period: last 3 days (excluding today)
    current_end = today - timedelta(days=1)
    current_start = current_end - timedelta(days=CONFIG["analysis_days"] - 1)
    
    # Previous period: same 3 days last week
    previous_end = current_end - timedelta(days=7)
    previous_start = current_start - timedelta(days=7)
    
    # Fetch data for both periods
    current_data = await fetch_affiliate_performance(
        current_start.strftime("%Y-%m-%d"),
        current_end.strftime("%Y-%m-%d")
    )
    
    previous_data = await fetch_affiliate_performance(
        previous_start.strftime("%Y-%m-%d"),
        previous_end.strftime("%Y-%m-%d")
    )
    
    # Compare and identify drops
    alerts = compare_periods(current_data, previous_data)
    
    # Send alerts if any found
    if alerts:
        await send_paused_partner_alerts(alerts)
    
    return alerts


async def fetch_affiliate_performance(from_date: str, to_date: str) -> dict:
    """Fetch affiliate performance data for a date range."""
    
    payload = {
        "columns": ["affiliate"],
        "query": {"filters": []},
        "from": from_date,
        "to": to_date,
        "timezone_id": 67
    }
    
    response = await everflow_client.post_entity_report(payload)
    
    # Convert to dict keyed by affiliate_id
    result = {}
    for row in response.get("table", []):
        affiliate_id = row.get("affiliate_id")
        result[affiliate_id] = {
            "affiliate_id": affiliate_id,
            "affiliate_name": row.get("affiliate_name"),
            "revenue": row.get("revenue", 0),
            "conversions": row.get("conversions", 0),
            "clicks": row.get("clicks", 0),
        }
    
    return result


def compare_periods(current: dict, previous: dict) -> list[dict]:
    """
    Compare current vs previous period and identify significant drops.
    
    Returns:
        List of affiliates with drops exceeding threshold
    """
    
    alerts = []
    
    for affiliate_id, prev_data in previous.items():
        prev_revenue = prev_data.get("revenue", 0)
        
        # Skip affiliates with minimal baseline
        if prev_revenue < CONFIG["min_previous_revenue"]:
            continue
        
        # Get current data (default to 0 if not present)
        curr_data = current.get(affiliate_id, {
            "revenue": 0,
            "conversions": 0,
            "clicks": 0
        })
        curr_revenue = curr_data.get("revenue", 0)
        
        # Calculate percentage change
        if prev_revenue > 0:
            delta_pct = ((curr_revenue - prev_revenue) / prev_revenue) * 100
        else:
            delta_pct = 0
        
        # Check if drop exceeds threshold
        if delta_pct <= CONFIG["drop_threshold"]:
            alerts.append({
                "affiliate_id": affiliate_id,
                "affiliate_name": prev_data.get("affiliate_name"),
                "previous_revenue": prev_revenue,
                "current_revenue": curr_revenue,
                "delta_percentage": round(delta_pct, 1),
                "previous_conversions": prev_data.get("conversions", 0),
                "current_conversions": curr_data.get("conversions", 0),
            })
    
    # Sort by delta (most severe drops first)
    alerts.sort(key=lambda x: x["delta_percentage"])
    
    return alerts


async def send_paused_partner_alerts(alerts: list[dict]) -> None:
    """Send notifications for partners with significant drops."""
    
    message = format_paused_partner_alert(alerts)
    
    await notification_service.send(
        channel="chat",
        message=message,
        priority="high",
        alert_type="paused_partner"
    )


def format_paused_partner_alert(alerts: list[dict]) -> str:
    """Format alerts into a user-friendly message."""
    
    if len(alerts) == 1:
        a = alerts[0]
        return (
            f"🚨 **Partner Volume Drop Alert**\n\n"
            f"Partner **{a['affiliate_name']}** (ID: {a['affiliate_id']}) "
            f"has dropped by **{abs(a['delta_percentage'])}%** week-over-week.\n\n"
            f"**Previous 3 days:** ${a['previous_revenue']:,.2f} ({a['previous_conversions']} conv)\n"
            f"**Current 3 days:** ${a['current_revenue']:,.2f} ({a['current_conversions']} conv)\n\n"
            f"⚠️ This partner may have paused or is experiencing issues."
        )
    else:
        # Multiple alerts
        lines = [f"🚨 **Partner Volume Drop Alert** - {len(alerts)} Partners Affected\n"]
        lines.append("The following partners have significant week-over-week drops:\n")
        
        for i, a in enumerate(alerts[:10], 1):  # Limit to top 10
            lines.append(
                f"{i}. **{a['affiliate_name']}** (ID: {a['affiliate_id']})\n"
                f"   • Drop: **{abs(a['delta_percentage'])}%**\n"
                f"   • Previous: ${a['previous_revenue']:,.2f} → Current: ${a['current_revenue']:,.2f}\n"
            )
        
        if len(alerts) > 10:
            lines.append(f"\n... and {len(alerts) - 10} more partners with drops.\n")
        
        lines.append("\n⚠️ These partners may have paused campaigns or are experiencing issues.")
        
        return "\n".join(lines)
```

## Alert Templates

### Single Partner Drop
```
🚨 Partner Volume Drop Alert

Partner SuperAffiliate (ID: 123) has dropped by 75% week-over-week.

**Previous 3 days:** $5,230.00 (156 conversions)
**Current 3 days:** $1,307.50 (39 conversions)

⚠️ This partner may have paused or is experiencing issues.

Would you like me to:
• Show their recent campaign history?
• Check if any offers they promote were paused?
```

### Multiple Partners Drop
```
🚨 Partner Volume Drop Alert - 5 Partners Affected

The following partners have significant week-over-week drops:

1. **Partner A** (ID: 123)
   • Drop: 85%
   • Previous: $8,500.00 → Current: $1,275.00

2. **Partner B** (ID: 456)
   • Drop: 72%
   • Previous: $3,200.00 → Current: $896.00

3. **Partner C** (ID: 789)
   • Drop: 68%
   • Previous: $2,100.00 → Current: $672.00

4. **Partner D** (ID: 101)
   • Drop: 55%
   • Previous: $1,800.00 → Current: $810.00

5. **Partner E** (ID: 102)
   • Drop: 52%
   • Previous: $1,500.00 → Current: $720.00

**Total Revenue Impact:** -$12,647.00

⚠️ These partners may have paused campaigns or are experiencing issues.
```

### No Issues Detected (Internal Log)
```
✅ Paused Partner Check Complete

Date: December 16, 2024
Analysis Period: Dec 13-15 vs Dec 6-8
Partners Analyzed: 128
Partners with >50% drop: 0

Next check: December 17, 2024 at 08:00 AM
```

## Configuration Options

```python
WF5_CONFIG = {
    # Schedule
    "schedule_hour": 8,
    "schedule_minute": 0,
    "schedule_days": ["mon", "wed", "fri"],  # Or daily
    "timezone": "Europe/Amsterdam",
    
    # Analysis
    "analysis_days": 3,              # Days in each comparison window
    "week_offset": 7,                # Days between comparison periods
    
    # Thresholds
    "drop_threshold_percent": -50,   # Alert if drop > 50%
    "min_baseline_revenue": 100,     # Minimum revenue to consider
    "min_baseline_conversions": 5,   # Alternative: minimum conversions
    
    # Notifications
    "notification_channels": ["chat"],
    "max_alerts_per_message": 10,    # Aggregate limit
    
    # Exclusions
    "exclude_affiliates": [],        # IDs to ignore (e.g., test partners)
    "exclude_new_partners_days": 14, # Ignore partners < 14 days old
}
```

## Comparison Logic Detail

```
┌─────────────────────────────────────────────────────────┐
│                    Timeline                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Previous Week                    Current Week          │
│  ┌─────────────┐                  ┌─────────────┐      │
│  │ Dec 6-8     │   7 days gap     │ Dec 13-15   │      │
│  │ (Set B)     │◄────────────────►│ (Set A)     │      │
│  └─────────────┘                  └─────────────┘      │
│                                           │             │
│                                           ▼             │
│                                    Today: Dec 16        │
│                                                         │
│  Comparison:                                            │
│  Delta = (Set A - Set B) / Set B × 100%                │
│                                                         │
│  Alert if: Delta < -50%                                 │
└─────────────────────────────────────────────────────────┘
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| New partner (no previous data) | Skip, exclude from comparison |
| Partner had $0 previous week | Skip (avoid division by zero) |
| Partner went from $10 to $0 | Alert (100% drop) |
| Seasonal expected drop | Consider exclusion list |
| Weekend vs weekday comparison | 7-day offset maintains day alignment |
| Partner blocked/terminated | Alert (may indicate issue or intentional) |

## Monitoring & Logging

### Job Execution Log
```json
{
  "job": "WF5",
  "execution_time": "2024-12-16T08:00:22Z",
  "duration_ms": 4520,
  "status": "completed",
  "current_period": "2024-12-13 to 2024-12-15",
  "previous_period": "2024-12-06 to 2024-12-08",
  "partners_analyzed": 128,
  "partners_with_drops": 5,
  "alerts_sent": true,
  "next_run": "2024-12-17T08:00:00Z"
}
```

## Testing Checklist

- [ ] Job runs at scheduled time
- [ ] Date calculation is correct (3-day windows, 7-day offset)
- [ ] Percentage calculation is accurate
- [ ] Threshold filtering works (only >50% drops)
- [ ] Minimum baseline filtering works
- [ ] New partners are excluded
- [ ] Multiple alerts aggregate correctly
- [ ] Division by zero is handled
- [ ] API errors are handled gracefully

## Integration with Other Workflows

### Potential Follow-up Questions
After receiving a WF5 alert, users might ask:

- "Why did Partner X drop?" → Could trigger analysis query
- "What offers does Partner X promote?" → Entity report filtered by affiliate
- "When did they last convert?" → Conversion report query

### Automated Investigation (Future Enhancement)
```python
async def investigate_drop(affiliate_id: int) -> dict:
    """
    Automated investigation of why a partner dropped.
    
    Checks:
    1. Did any of their offers get paused?
    2. Did their top LP change/break?
    3. Did their conversion rate drop?
    """
    # Future enhancement
    pass
```






