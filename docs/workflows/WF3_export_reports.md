# WF3: Search, Compile, and Export Reports

> **Phase:** 1 - The Analyst (Read-Only)  
> **Type:** Read Operation  
> **Week:** 1

## Objective

Automate the manual "Export to CSV" task for various datasets (Fraud, Scrub, General Stats). The agent maps natural language to timestamps and generates a direct download link.

## User Intent Examples

- "Export fraud report for last week"
- "Download conversion data for December"
- "Get me a CSV of all conversions with sub1, sub2, affiliate for last month"
- "Export stats for Offer 123 from November 1st to 15th"
- "Pull a scrub analysis report for the past 7 days"
- "Download variance report for this week"

## Report Types

| Report Type | Use Case | API Endpoint |
|-------------|----------|--------------|
| General Stats | Overall performance metrics | `/reporting/entity/table/export` |
| Conversions | Individual conversion records | `/reporting/conversions/export` |
| Fraud | Suspicious activity data | `/reporting/conversions/export` (filtered) |
| Scrub | Quality analysis by sub params | `/reporting/conversions/export` |
| Variance | Performance fluctuations | `/reporting/entity/table/export` |

## Required Entities

| Entity | Required | Example | Extraction Notes |
|--------|----------|---------|------------------|
| `report_type` | ✅ | "fraud", "conversions", "stats" | Infer from context |
| `date_range` | ✅ | "last week", "November 2024" | Map to timestamps |
| `columns` | ❌ Optional | ["sub1", "sub2", "affiliate"] | Report-specific defaults |
| `filters` | ❌ Optional | offer_id, affiliate_id | Narrow scope |

## API Endpoints

### General Stats Export
```
POST /v1/networks/reporting/entity/table/export
```

### Conversions/Fraud Export
```
POST /v1/networks/reporting/conversions/export
```

## Date Mapping Logic

The LLM must translate natural language dates to `YYYY-MM-DD` format:

```python
from datetime import datetime, timedelta

def parse_date_range(natural_language: str) -> tuple[str, str]:
    """
    Map natural language to date range.
    
    Examples:
        "last week" -> (7 days ago, yesterday)
        "this month" -> (1st of month, today)
        "November 2024" -> (2024-11-01, 2024-11-30)
        "past 30 days" -> (30 days ago, today)
    """
    today = datetime.now()
    
    mappings = {
        "today": (today, today),
        "yesterday": (today - timedelta(days=1), today - timedelta(days=1)),
        "last week": (today - timedelta(days=7), today - timedelta(days=1)),
        "this week": (today - timedelta(days=today.weekday()), today),
        "last month": (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1) - timedelta(days=1)
        ),
        "this month": (today.replace(day=1), today),
        "last 7 days": (today - timedelta(days=7), today),
        "last 30 days": (today - timedelta(days=30), today),
        "last 90 days": (today - timedelta(days=90), today),
    }
    
    # Return as YYYY-MM-DD strings
    from_date, to_date = mappings.get(natural_language.lower(), (today - timedelta(days=7), today))
    return from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")
```

## Payload Examples

### General Stats Export
```json
{
  "columns": ["offer", "affiliate", "country"],
  "query": {
    "filters": []
  },
  "from": "2024-12-01",
  "to": "2024-12-16",
  "format": "csv",
  "timezone_id": 67
}
```

### Conversions Export with Sub Params (Scrub Analysis)
```json
{
  "columns": ["sub1", "sub2", "sub3", "affiliate", "offer", "payout"],
  "query": {
    "filters": [
      {
        "resource_type": "offer",
        "filter_id_value": "123"
      }
    ]
  },
  "from": "2024-12-09",
  "to": "2024-12-16",
  "format": "csv",
  "timezone_id": 67
}
```

### Fraud Report Export
```json
{
  "columns": ["affiliate", "offer", "click_ip", "conversion_ip", "sub1", "is_fraud"],
  "query": {
    "filters": [
      {
        "filter_type": "is_fraud",
        "filter_value": true
      }
    ]
  },
  "from": "2024-12-09",
  "to": "2024-12-16",
  "format": "csv",
  "timezone_id": 67
}
```

## Workflow Logic

```python
from enum import Enum
from typing import Optional

class ReportType(Enum):
    GENERAL_STATS = "general"
    CONVERSIONS = "conversions"
    FRAUD = "fraud"
    SCRUB = "scrub"
    VARIANCE = "variance"


# Default columns per report type
REPORT_COLUMNS = {
    ReportType.GENERAL_STATS: ["offer", "affiliate", "country", "clicks", "conversions", "revenue"],
    ReportType.CONVERSIONS: ["conversion_id", "affiliate", "offer", "sub1", "sub2", "payout", "created_at"],
    ReportType.FRAUD: ["affiliate", "offer", "click_ip", "conversion_ip", "sub1", "is_fraud", "fraud_reason"],
    ReportType.SCRUB: ["sub1", "sub2", "sub3", "affiliate", "offer", "payout", "status"],
    ReportType.VARIANCE: ["offer", "affiliate", "clicks", "conversions", "revenue", "date"],
}


async def export_report(
    report_type: ReportType,
    from_date: str,
    to_date: str,
    columns: Optional[list] = None,
    filters: Optional[list] = None
) -> dict:
    """
    Generate and return a CSV export download link.
    
    Args:
        report_type: Type of report to generate
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        columns: Optional custom columns (uses defaults if not provided)
        filters: Optional filters (offer_id, affiliate_id, etc.)
    
    Returns:
        Download URL for the CSV file
    """
    
    # Determine endpoint based on report type
    if report_type in [ReportType.GENERAL_STATS, ReportType.VARIANCE]:
        endpoint = "/v1/networks/reporting/entity/table/export"
    else:
        endpoint = "/v1/networks/reporting/conversions/export"
    
    # Use default columns if not specified
    if columns is None:
        columns = REPORT_COLUMNS[report_type]
    
    # Build query filters
    query_filters = filters or []
    
    # Add fraud filter for fraud reports
    if report_type == ReportType.FRAUD:
        query_filters.append({
            "filter_type": "is_fraud",
            "filter_value": True
        })
    
    # Construct payload
    payload = {
        "columns": columns,
        "query": {"filters": query_filters},
        "from": from_date,
        "to": to_date,
        "format": "csv",
        "timezone_id": 67
    }
    
    # Execute API call
    response = await everflow_client.post(endpoint, payload)
    
    # Extract download URL
    download_url = response.get("download_url") or response.get("url")
    
    return {
        "status": "success",
        "download_url": download_url,
        "report_type": report_type.value,
        "date_range": f"{from_date} to {to_date}",
        "columns": columns
    }
```

## Response Templates

### Success Response
```
📥 Your report is ready!

**Report:** Fraud Analysis
**Period:** Dec 9, 2024 - Dec 16, 2024
**Columns:** affiliate, offer, click_ip, conversion_ip, sub1, is_fraud

[📄 Download CSV](https://api.everflow.io/exports/abc123.csv)

The link will expire in 24 hours.
```

### Success with Custom Columns
```
📥 Export Complete!

**Report:** Scrub Analysis
**Period:** Last 7 days
**Custom Columns:** sub1, sub2, sub3, affiliate, payout

[📄 Download CSV](https://api.everflow.io/exports/xyz789.csv)

Tip: Open in Excel or Google Sheets for easy analysis.
```

### Processing Large Report
```
⏳ Generating your report...

This is a large dataset (90 days of conversions). It may take a minute.

I'll provide the download link as soon as it's ready.

---

✅ Done! Here's your report:
[📄 Download CSV](https://api.everflow.io/exports/large123.csv)
```

### Error: Invalid Date Range
```
I couldn't understand the date range "next month" - I can only export historical data.

Try something like:
• "last week"
• "December 2024"  
• "from November 1st to November 30th"
```

### Error: No Data
```
The export completed, but there's no data matching your criteria.

**Period:** Dec 1-7, 2024
**Report Type:** Fraud

This means no fraud was detected during this period - that's good news! 🎉

Would you like to try a different date range or report type?
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Very large date range (>90 days) | Warn user, may take longer |
| Future dates requested | Reject, explain limitation |
| Ambiguous date ("last month" in January) | Clarify December vs current |
| No data in range | Return success with note |
| Invalid column requested | Ignore invalid, use valid ones |
| Export timeout | Retry once, then report error |

## Column Reference

### Available Columns by Report Type

**Entity Reports:**
- `offer`, `affiliate`, `country`, `offer_url`
- `clicks`, `conversions`, `revenue`, `payout`, `profit`
- `cvr`, `epc`, `rpc`

**Conversion Reports:**
- `conversion_id`, `click_id`, `affiliate_id`, `offer_id`
- `sub1`, `sub2`, `sub3`, `sub4`, `sub5`
- `click_ip`, `conversion_ip`, `user_agent`
- `payout`, `revenue`, `status`, `created_at`
- `is_fraud`, `fraud_reason`

## Testing Checklist

- [ ] Basic export: "Export conversions for last week"
- [ ] With specific columns: "Export sub1, sub2 for last month"
- [ ] Fraud report filtering
- [ ] Custom date range parsing
- [ ] Large date range handling
- [ ] Download link validity
- [ ] Empty result handling

## Security Notes

- Download links should be **time-limited** (typically 24 hours)
- Links should not be logged in plain text
- User must be authenticated to request exports






