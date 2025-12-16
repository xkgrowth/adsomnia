# WF2: Identify Top-Performing Landing Pages

> **Phase:** 1 - The Analyst (Read-Only)  
> **Type:** Read Operation  
> **Week:** 1 (Pilot Core)

## Objective

Find the best converting Landing Page (Offer URL) for a specific Offer or Geo, answering questions like: *"Which LP is best for Offer X?"*

## User Intent Examples

- "Which LP is best for Offer 123?"
- "What's the top performing landing page for the US?"
- "Show me the best converting pages for the Summer Promo offer"
- "Which landing pages work best in Germany for Offer ABC?"
- "Top 3 LPs for offer ID 456 in France"

## Required Entities

| Entity | Required | Example | Extraction Notes |
|--------|----------|---------|------------------|
| `offer_id` | ✅ (or name) | 123, "Summer Promo" | Primary filter |
| `country_code` | ❌ Optional | "US", "DE", "FR" | Secondary filter |
| `date_range` | ❌ Optional | "last 30 days" | Default: 30 days |
| `min_leads` | ❌ Optional | 20 | Default: 20 (statistical significance) |
| `top_n` | ❌ Optional | 3 | Default: 3 results |

## API Endpoint

```
POST /v1/networks/reporting/entity
```

## Payload Construction

```json
{
  "columns": ["offer_url", "offer"],
  "query": {
    "filters": [
      {
        "resource_type": "offer",
        "filter_id_value": "OFFER_ID_HERE"
      }
    ]
  },
  "from": "2024-11-16",
  "to": "2024-12-16",
  "timezone_id": 67
}
```

### With Country Filter

```json
{
  "columns": ["offer_url", "offer", "country"],
  "query": {
    "filters": [
      {
        "resource_type": "offer",
        "filter_id_value": "OFFER_ID_HERE"
      },
      {
        "resource_type": "country",
        "filter_id_value": "US"
      }
    ]
  },
  "from": "2024-11-16",
  "to": "2024-12-16",
  "timezone_id": 67
}
```

## Workflow Logic

```python
from typing import Optional
from datetime import datetime, timedelta

async def identify_top_lps(
    offer_id: int,
    country_code: Optional[str] = None,
    days: int = 30,
    min_leads: int = 20,
    top_n: int = 3
) -> dict:
    """
    Identify top-performing landing pages for an offer.
    
    Args:
        offer_id: The Everflow offer ID
        country_code: Optional ISO country code (US, DE, etc.)
        days: Number of days to analyze (default 30)
        min_leads: Minimum leads for statistical significance (default 20)
        top_n: Number of top results to return (default 3)
    
    Returns:
        Top N landing pages sorted by conversion rate
    """
    
    # Step 1: Build date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    # Step 2: Construct filters
    filters = [
        {"resource_type": "offer", "filter_id_value": str(offer_id)}
    ]
    
    if country_code:
        filters.append({
            "resource_type": "country",
            "filter_id_value": country_code.upper()
        })
    
    # Step 3: Build payload
    columns = ["offer_url", "offer"]
    if country_code:
        columns.append("country")
    
    payload = {
        "columns": columns,
        "query": {"filters": filters},
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "timezone_id": 67
    }
    
    # Step 4: Execute API call
    response = await everflow_client.post_entity_report(payload)
    
    # Step 5: Post-process results
    results = process_lp_results(response, min_leads, top_n)
    
    return results


def process_lp_results(
    response: dict,
    min_leads: int,
    top_n: int
) -> list:
    """
    Process API response to extract top performing LPs.
    
    Logic:
    1. Filter: Exclude rows where leads < min_leads
    2. Calculate: conversion_rate = (conversions / clicks) * 100
    3. Sort: Descending by conversion_rate
    4. Return: Top N results
    """
    
    rows = response.get("table", [])
    processed = []
    
    for row in rows:
        clicks = row.get("clicks", 0)
        conversions = row.get("event_conversion", 0)  # leads
        
        # Filter: Must have minimum leads for significance
        if conversions < min_leads:
            continue
        
        # Calculate conversion rate
        if clicks > 0:
            cvr = (conversions / clicks) * 100
        else:
            cvr = 0
        
        processed.append({
            "offer_url_id": row.get("offer_url_id"),
            "offer_url_name": row.get("offer_url_name"),
            "clicks": clicks,
            "conversions": conversions,
            "conversion_rate": round(cvr, 2)
        })
    
    # Sort by conversion rate (descending)
    processed.sort(key=lambda x: x["conversion_rate"], reverse=True)
    
    # Return top N
    return processed[:top_n]
```

## Response Templates

### Success Response
```
📊 Top 3 Landing Pages for Offer 123 (Last 30 Days)

1. **Summer Sale LP v2** 
   • Conversion Rate: 4.85%
   • Clicks: 12,450 | Conversions: 604

2. **Summer Sale LP v1**
   • Conversion Rate: 3.92%
   • Clicks: 8,230 | Conversions: 323

3. **Generic Offer Page**
   • Conversion Rate: 2.15%
   • Clicks: 5,100 | Conversions: 110

💡 Recommendation: Route more traffic to "Summer Sale LP v2" for best results.
```

### Success with Country Filter
```
📊 Top 3 Landing Pages for Offer 123 in Germany (Last 30 Days)

1. **DE Localized LP** 
   • Conversion Rate: 5.12%
   • Clicks: 3,200 | Conversions: 164

[... etc]

💡 The German localized page outperforms generic pages by 2.1x.
```

### No Results (Insufficient Data)
```
I found landing pages for Offer 123, but none of them have enough data yet (minimum 20 conversions needed for reliable analysis).

Current stats:
• LP A: 15 conversions (need 5 more)
• LP B: 8 conversions (need 12 more)

Would you like me to:
1. Lower the minimum threshold?
2. Expand the date range?
```

### Error: Offer Not Found
```
I couldn't find Offer 123 in the system. 

This could mean:
• The offer ID is incorrect
• The offer might be archived
• The offer hasn't received any traffic yet

Can you verify the offer ID or tell me the offer name so I can search for it?
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| No LPs meet minimum threshold | Offer to lower threshold or expand date range |
| Offer has no traffic | Report clearly, suggest checking offer status |
| All LPs have same CVR | Report as tie, show click volumes for differentiation |
| Single LP only | Report it, note lack of comparison data |
| Very recent offer | Suggest waiting for more data or shorter time window |

## Configuration Defaults

```python
DEFAULT_CONFIG = {
    "days": 30,           # Default lookback period
    "min_leads": 20,      # Minimum conversions for inclusion
    "top_n": 3,           # Number of results to return
    "timezone_id": 67,    # Everflow timezone setting
}
```

## Testing Checklist

- [ ] Basic query: "Top LPs for Offer X"
- [ ] With country filter: "Top LPs for Offer X in US"
- [ ] Custom date range: "Top LPs for Offer X last week"
- [ ] Low traffic offer handling
- [ ] Invalid offer ID handling
- [ ] Multiple LPs with identical CVR
- [ ] Edge case: Single LP only

## Performance Notes

- API call typically returns in < 2 seconds
- Post-processing is O(n log n) due to sorting
- Large offers (100+ LPs) may take slightly longer

