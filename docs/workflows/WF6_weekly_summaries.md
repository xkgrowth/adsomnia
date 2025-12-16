# WF6: Weekly Performance Summaries

> **Phase:** 2 - The Watchdog (Monitoring & Create)  
> **Type:** Read Operation (Aggregation)  
> **Week:** 2

## Objective

Generate high-level snapshots of volumes per Geo/Offer, specifically filtered by the 'Advertiser_Internal' label. Provides text summaries for quick performance overview.

## User Intent Examples

- "Give me the weekly performance summary"
- "What's our top performing geo this week?"
- "Show me a summary of internal advertiser performance"
- "Weekly snapshot by country"
- "How did we do last week by geography?"

## Key Filter Requirement

⚠️ **Important:** This workflow specifically filters by the `Advertiser_Internal` label as per the SOW specification. This ensures only internal advertiser data is summarized.

## Required Entities

| Entity | Required | Example | Extraction Notes |
|--------|----------|---------|------------------|
| `date_range` | ❌ Optional | "last week", "this week" | Default: last 7 days |
| `group_by` | ❌ Optional | "country", "offer" | Default: country |

## API Endpoint

```
POST /v1/networks/reporting/entity
```

## Payload Construction

```json
{
  "columns": ["country", "offer"],
  "query": {
    "filters": [
      {
        "resource_type": "label",
        "filter_id_value": "Advertiser_Internal"
      }
    ]
  },
  "from": "2024-12-09",
  "to": "2024-12-16",
  "timezone_id": 67
}
```

## Workflow Logic

```python
from datetime import datetime, timedelta
from typing import Optional, Literal
from collections import defaultdict

# Configuration
CONFIG = {
    "default_days": 7,
    "label_filter": "Advertiser_Internal",
    "currency_symbol": "$",
    "top_n": 5,  # Number of top geos/offers to highlight
}


async def generate_weekly_summary(
    days: int = 7,
    group_by: Literal["country", "offer"] = "country"
) -> dict:
    """
    Generate a weekly performance summary.
    
    Args:
        days: Number of days to analyze (default 7)
        group_by: Primary grouping dimension (country or offer)
    
    Returns:
        Aggregated performance data with text summary
    """
    
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    # Build payload with required Advertiser_Internal filter
    payload = {
        "columns": ["country", "offer"],
        "query": {
            "filters": [
                {
                    "resource_type": "label",
                    "filter_id_value": CONFIG["label_filter"]
                }
            ]
        },
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "timezone_id": 67
    }
    
    # Execute API call
    response = await everflow_client.post_entity_report(payload)
    
    # Process and aggregate results
    summary = aggregate_performance(response, group_by)
    
    # Generate text summary
    text_summary = generate_text_summary(summary, group_by, days)
    
    return {
        "status": "success",
        "period": f"{from_date.strftime('%b %d')} - {to_date.strftime('%b %d, %Y')}",
        "data": summary,
        "text_summary": text_summary
    }


def aggregate_performance(response: dict, group_by: str) -> list[dict]:
    """
    Aggregate raw data by the specified dimension.
    
    Groups data by country or offer and sums:
    - conversions
    - revenue
    - clicks
    """
    
    rows = response.get("table", [])
    aggregated = defaultdict(lambda: {
        "conversions": 0,
        "revenue": 0,
        "clicks": 0,
        "offers": set() if group_by == "country" else None,
        "countries": set() if group_by == "offer" else None,
    })
    
    for row in rows:
        if group_by == "country":
            key = row.get("country_code", "Unknown")
            key_name = row.get("country_name", key)
        else:
            key = row.get("offer_id", "Unknown")
            key_name = row.get("offer_name", f"Offer {key}")
        
        aggregated[key]["name"] = key_name
        aggregated[key]["id"] = key
        aggregated[key]["conversions"] += row.get("conversions", 0)
        aggregated[key]["revenue"] += row.get("revenue", 0)
        aggregated[key]["clicks"] += row.get("clicks", 0)
        
        # Track unique offers/countries for context
        if group_by == "country" and row.get("offer_id"):
            aggregated[key]["offers"].add(row.get("offer_id"))
        elif group_by == "offer" and row.get("country_code"):
            aggregated[key]["countries"].add(row.get("country_code"))
    
    # Convert to sorted list
    result = []
    for key, data in aggregated.items():
        entry = {
            "id": data["id"],
            "name": data["name"],
            "conversions": data["conversions"],
            "revenue": data["revenue"],
            "clicks": data["clicks"],
        }
        if data.get("offers"):
            entry["offer_count"] = len(data["offers"])
        if data.get("countries"):
            entry["country_count"] = len(data["countries"])
        result.append(entry)
    
    # Sort by revenue descending
    result.sort(key=lambda x: x["revenue"], reverse=True)
    
    return result


def generate_text_summary(data: list, group_by: str, days: int) -> str:
    """Generate a natural language summary of the performance data."""
    
    if not data:
        return f"No data found for the last {days} days with the Advertiser_Internal label."
    
    total_revenue = sum(d["revenue"] for d in data)
    total_conversions = sum(d["conversions"] for d in data)
    
    # Top performers
    top_items = data[:CONFIG["top_n"]]
    
    dimension = "Geo" if group_by == "country" else "Offer"
    
    lines = [
        f"📊 **Weekly Performance Summary** (Last {days} days)\n",
        f"**Total Revenue:** ${total_revenue:,.2f}",
        f"**Total Conversions:** {total_conversions:,}\n",
        f"**Top {dimension}s by Revenue:**\n"
    ]
    
    for i, item in enumerate(top_items, 1):
        pct_of_total = (item["revenue"] / total_revenue * 100) if total_revenue > 0 else 0
        lines.append(
            f"{i}. **{item['name']}** - ${item['revenue']:,.2f} "
            f"({pct_of_total:.1f}% of total, {item['conversions']:,} conv)"
        )
    
    # Add insight
    if len(data) > 1 and data[0]["revenue"] > 0:
        top_pct = (data[0]["revenue"] / total_revenue * 100) if total_revenue > 0 else 0
        lines.append(
            f"\n💡 **Insight:** {data[0]['name']} leads with {top_pct:.1f}% of total revenue."
        )
    
    return "\n".join(lines)
```

## Response Templates

### Standard Summary
```
📊 Weekly Performance Summary (Last 7 days)

**Total Revenue:** $45,230.00
**Total Conversions:** 1,856

**Top Geos by Revenue:**

1. **United States** - $18,500.00 (40.9% of total, 756 conv)
2. **Germany** - $12,300.00 (27.2% of total, 489 conv)
3. **United Kingdom** - $6,800.00 (15.0% of total, 278 conv)
4. **France** - $4,200.00 (9.3% of total, 198 conv)
5. **Netherlands** - $3,430.00 (7.6% of total, 135 conv)

💡 Insight: United States leads with 40.9% of total revenue.
```

### Summary by Offer
```
📊 Weekly Performance Summary (Last 7 days)

**Total Revenue:** $45,230.00
**Total Conversions:** 1,856

**Top Offers by Revenue:**

1. **Summer Promo 2024** - $22,000.00 (48.6% of total, 890 conv)
   Active in 12 countries

2. **Holiday Special** - $15,500.00 (34.3% of total, 620 conv)
   Active in 8 countries

3. **Evergreen Offer A** - $4,800.00 (10.6% of total, 210 conv)
   Active in 15 countries

💡 Insight: Summer Promo 2024 dominates with nearly half of all revenue.
```

### Comparative Summary (Week over Week)
```
📊 Weekly Performance Summary

**This Week (Dec 9-15):** $45,230.00 revenue
**Last Week (Dec 2-8):** $42,100.00 revenue
**Change:** +$3,130.00 (+7.4%) ✅

**Top Geos This Week:**
1. 🇺🇸 United States - $18,500 (+12% vs last week)
2. 🇩🇪 Germany - $12,300 (+5% vs last week)
3. 🇬🇧 United Kingdom - $6,800 (-3% vs last week)

💡 US growth is driving overall performance improvement.
```

### No Data Available
```
📊 Weekly Performance Summary

No performance data found for the last 7 days with the Advertiser_Internal label.

This could mean:
• No traffic was tagged with this label
• The label filter might need adjustment
• There may be a data sync delay

Would you like me to check without the label filter?
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| No data for period | Return helpful message, suggest alternatives |
| Single geo/offer only | Still show summary, note limited data |
| Very small numbers | Show actuals, note sample size |
| Missing label | Clear error about missing Advertiser_Internal tag |
| Tie in top positions | Show both, note the tie |

## Configuration

```python
WF6_CONFIG = {
    # Default settings
    "default_days": 7,
    "default_group_by": "country",
    
    # Filter requirement (from SOW)
    "required_label": "Advertiser_Internal",
    
    # Display
    "top_n_results": 5,
    "currency_symbol": "$",
    "show_percentages": True,
    
    # Optional comparison
    "enable_wow_comparison": True,  # Week-over-week
}
```

## Label Filter Explanation

The `Advertiser_Internal` label filter is a **requirement** from the SOW:

> *"Specifically filters by the 'Advertiser_Internal' label to generate text summaries."*

This ensures:
1. Only internal advertiser data is included
2. External/third-party data is excluded
3. Summaries reflect the client's core business

If users ask for summaries without this filter, clarify and confirm before proceeding.

## Testing Checklist

- [ ] Basic summary generation
- [ ] Group by country works
- [ ] Group by offer works
- [ ] Label filter is applied correctly
- [ ] Empty data handling
- [ ] Percentage calculations are accurate
- [ ] Top N limiting works
- [ ] Date range parsing works
- [ ] Week-over-week comparison (if enabled)

## Future Enhancements

- Scheduled weekly email digest
- Comparison with previous period
- Trend indicators (↑↓→)
- Export summary to PDF
- Slack integration for weekly posts






