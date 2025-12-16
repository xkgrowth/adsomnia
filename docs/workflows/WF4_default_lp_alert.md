# WF4: Alert on Traffic to Default LPs

> **Phase:** 3 - The Alerter (Monitor & Alert)  
> **Type:** Scheduled Job (Automated)  
> **Week:** 3

## Objective

Detect if traffic is being wasted on a "Default" (fallback) landing page, indicating a broken link or misconfiguration. This is a daily scheduled job that runs automatically and alerts proactively.

## Trigger

- **Schedule:** Daily at 09:00 AM (configurable)
- **Lookback:** Previous day's data
- **Type:** Automated/Proactive (not user-initiated)

## Alert Criteria

Alert is triggered when **ALL** conditions are met:
1. `offer_url_name` contains the string `"Default"` (case-insensitive)
2. `clicks` > **50** (threshold, configurable)

## API Endpoint

```
POST /v1/networks/reporting/entity
```

## Payload

```json
{
  "columns": ["offer_url", "affiliate", "offer"],
  "query": {
    "filters": []
  },
  "from": "YESTERDAY",
  "to": "YESTERDAY",
  "timezone_id": 67
}
```

## Workflow Logic

```python
from datetime import datetime, timedelta
from typing import Optional

# Configuration
CONFIG = {
    "schedule": "0 9 * * *",      # Cron: 09:00 AM daily
    "click_threshold": 50,         # Minimum clicks to alert
    "default_keyword": "default",  # Keyword to search in LP name
}


async def check_default_lp_traffic() -> list[dict]:
    """
    Daily scheduled job to detect traffic to Default landing pages.
    
    Returns:
        List of alerts for traffic sent to Default LPs
    """
    
    # Calculate yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    # Build payload
    payload = {
        "columns": ["offer_url", "affiliate", "offer"],
        "query": {"filters": []},
        "from": date_str,
        "to": date_str,
        "timezone_id": 67
    }
    
    # Execute API call
    response = await everflow_client.post_entity_report(payload)
    
    # Process results
    alerts = []
    rows = response.get("table", [])
    
    for row in rows:
        offer_url_name = row.get("offer_url_name", "").lower()
        clicks = row.get("clicks", 0)
        
        # Check alert conditions
        if CONFIG["default_keyword"] in offer_url_name and clicks > CONFIG["click_threshold"]:
            alerts.append({
                "affiliate_id": row.get("affiliate_id"),
                "affiliate_name": row.get("affiliate_name"),
                "offer_id": row.get("offer_id"),
                "offer_name": row.get("offer_name"),
                "offer_url_name": row.get("offer_url_name"),
                "clicks": clicks,
                "date": date_str
            })
    
    # Send alerts if any found
    if alerts:
        await send_alerts(alerts)
    
    return alerts


async def send_alerts(alerts: list[dict]) -> None:
    """
    Send alert notifications for detected issues.
    
    Notification channels:
    - In-app notification (chat interface)
    - Optional: Slack, Email (future enhancement)
    """
    
    for alert in alerts:
        message = format_alert_message(alert)
        await notification_service.send(
            channel="chat",
            message=message,
            priority="high",
            alert_type="default_lp"
        )


def format_alert_message(alert: dict) -> str:
    """Format a single alert into a user-friendly message."""
    return (
        f"🚨 **Default LP Alert**\n\n"
        f"Partner **{alert['affiliate_name']}** (ID: {alert['affiliate_id']}) "
        f"sent **{alert['clicks']:,}** clicks to the Default LP for "
        f"**{alert['offer_name']}** (ID: {alert['offer_id']}) yesterday.\n\n"
        f"**Landing Page:** {alert['offer_url_name']}\n"
        f"**Date:** {alert['date']}\n\n"
        f"⚠️ This usually indicates a broken tracking link or misconfiguration. "
        f"Please check the partner's setup."
    )
```

## Scheduler Setup

### Using APScheduler (Python)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

# Schedule WF4 to run daily at 9:00 AM
scheduler.add_job(
    check_default_lp_traffic,
    CronTrigger(hour=9, minute=0),
    id="wf4_default_lp_check",
    name="Daily Default LP Check",
    replace_existing=True
)

scheduler.start()
```

### Using Celery (Alternative)

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('adsomnia')

app.conf.beat_schedule = {
    'wf4-default-lp-check': {
        'task': 'workflows.wf4.check_default_lp_traffic',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

## Alert Templates

### Single Alert
```
🚨 Default LP Alert

Partner SuperAffiliate (ID: 123) sent 500 clicks to the Default LP for Summer Promo (ID: 456) yesterday.

**Landing Page:** Default Fallback Page
**Date:** December 15, 2024

⚠️ This usually indicates a broken tracking link or misconfiguration. Please check the partner's setup.

[View Partner Details] [View Offer]
```

### Multiple Alerts (Aggregated)
```
🚨 Default LP Alert - 3 Issues Detected

The following partners sent traffic to Default landing pages yesterday:

1. **Partner A** (ID: 123)
   • Offer: Summer Promo | Clicks: 500
   
2. **Partner B** (ID: 456) 
   • Offer: Winter Sale | Clicks: 230

3. **Partner C** (ID: 789)
   • Offer: Summer Promo | Clicks: 150

**Total wasted clicks:** 880

⚠️ Please review these partner configurations.
```

### No Issues Found (Internal Log Only)
```
✅ Daily Default LP Check Complete

Date: December 16, 2024
Status: No issues detected
Partners checked: 245
Offers checked: 89

Next check: December 17, 2024 at 09:00 AM
```

## Configuration Options

```python
WF4_CONFIG = {
    # Schedule
    "schedule_hour": 9,
    "schedule_minute": 0,
    "timezone": "Europe/Amsterdam",
    
    # Thresholds
    "click_threshold": 50,           # Minimum clicks to trigger alert
    "default_keywords": ["default", "fallback"],  # Keywords to match
    
    # Notifications
    "notification_channels": ["chat"],  # Options: chat, slack, email
    "aggregate_alerts": True,           # Combine multiple alerts into one message
    
    # Filtering
    "exclude_affiliates": [],           # Affiliate IDs to ignore
    "exclude_offers": [],               # Offer IDs to ignore
}
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| No traffic yesterday | Log success, no alert |
| All traffic below threshold | Log success, no alert |
| API timeout | Retry up to 3 times, then alert admin |
| Weekend/Holiday | Run as normal (configurable to skip) |
| Multiple Default LPs same affiliate | Aggregate into single alert |
| "Default" in legitimate LP name | Consider exclusion list |

## Monitoring & Logging

### Job Execution Log
```json
{
  "job": "WF4",
  "execution_time": "2024-12-16T09:00:15Z",
  "duration_ms": 2340,
  "status": "completed",
  "rows_processed": 1250,
  "alerts_triggered": 3,
  "next_run": "2024-12-17T09:00:00Z"
}
```

### Alert Log (Do NOT log PII or actual data)
```json
{
  "alert_type": "default_lp",
  "timestamp": "2024-12-16T09:00:15Z",
  "affiliate_count": 3,
  "total_clicks_affected": 880,
  "notification_sent": true,
  "notification_channel": "chat"
}
```

## Testing Checklist

- [ ] Job runs at scheduled time
- [ ] Correctly identifies "Default" in LP names (case-insensitive)
- [ ] Respects click threshold
- [ ] Alert formatting is correct
- [ ] Multiple alerts aggregate properly
- [ ] No false positives on legitimate "Default" names
- [ ] Handles API errors gracefully
- [ ] Retry logic works
- [ ] Exclusion lists work

## Integration Points

### Chat Interface
The alert should appear in the chat as a proactive message:

```
[09:00 AM] 🤖 Agent:

🚨 Default LP Alert

I detected a potential issue during my morning check...
[Alert details]

Would you like me to provide more details or help investigate?
```

### Future Enhancements
- Slack webhook integration
- Email digest for critical alerts
- Dashboard widget showing alert history
- Automatic partner notification option






