"""
Workflow Tools for LangChain Agent.
Replaces SQL tools with Everflow workflow tools (WF1-WF6).
"""
from typing import Optional, Literal
from langchain.tools import tool
from datetime import datetime, timedelta
import json


# Workflow Tool Descriptions for LLM
WORKFLOW_DESCRIPTIONS = {
    "wf1_generate_tracking_link": """
    Generate a tracking link for an affiliate/partner on a specific offer.
    This may require approving the affiliate for the offer first (requires user confirmation).
    
    Required parameters:
    - affiliate_id: The affiliate/partner ID (integer)
    - offer_id: The offer ID (integer)
    
    Returns a tracking URL if successful.
    """,
    
    "wf2_identify_top_lps": """
    Find the top performing landing pages for an offer.
    
    Required parameters:
    - offer_id: The offer ID (integer or name)
    
    Optional parameters:
    - country_code: ISO country code (e.g., "US", "DE", "FR")
    - days: Number of days to analyze (default: 30)
    - min_leads: Minimum conversions for significance (default: 20)
    - top_n: Number of results to return (default: 3)
    
    Returns top N landing pages sorted by conversion rate.
    """,
    
    "wf3_export_report": """
    Export a CSV report for various data types (fraud, conversions, stats, scrub, variance).
    
    Required parameters:
    - report_type: Type of report ("fraud", "conversions", "stats", "scrub", "variance")
    - date_range: Natural language date range (e.g., "last week", "December 2024")
    
    Optional parameters:
    - columns: List of specific columns to include
    - filters: Additional filters (offer_id, affiliate_id, etc.)
    
    Returns a download URL for the CSV file.
    """,
    
    "wf4_check_default_lp_alert": """
    Check for traffic to default landing pages (scheduled alert workflow).
    This is typically run automatically, but can be triggered manually.
    
    Optional parameters:
    - date: Specific date to check (default: yesterday)
    - click_threshold: Minimum clicks to alert (default: 50)
    
    Returns list of alerts for default LP traffic.
    """,
    
    "wf5_check_paused_partners": """
    Identify partners with significant volume drops (scheduled alert workflow).
    Compares current period vs previous period.
    
    Optional parameters:
    - analysis_days: Number of days to compare (default: 3)
    - drop_threshold: Percentage drop to alert (default: -50%)
    
    Returns list of partners with critical volume drops.
    """,
    
    "wf6_generate_weekly_summary": """
    Generate a weekly performance summary by country or offer.
    Filters by Advertiser_Internal label as required.
    
    Optional parameters:
    - days: Number of days to analyze (default: 7)
    - group_by: Group by "country" or "offer" (default: "country")
    
    Returns aggregated performance data with text summary.
    """,
}


@tool
def wf1_generate_tracking_link(affiliate_id: int, offer_id: int) -> str:
    """
    Generate a tracking link for an affiliate on an offer.
    May require approval confirmation if affiliate is not already approved.
    
    Args:
        affiliate_id: The affiliate/partner ID
        offer_id: The offer ID
    
    Returns:
        Tracking URL or confirmation request
    """
    # TODO: Implement actual Everflow API call
    # This is a placeholder that shows the structure
    return json.dumps({
        "status": "success",
        "tracking_link": f"https://tracking.everflow.io/aff_c?offer_id={offer_id}&aff_id={affiliate_id}",
        "message": f"Tracking link generated for Partner {affiliate_id} on Offer {offer_id}"
    })


@tool
def wf2_identify_top_lps(
    offer_id: int,
    country_code: Optional[str] = None,
    days: int = 30,
    min_leads: int = 20,
    top_n: int = 3
) -> str:
    """
    Find top performing landing pages for an offer.
    
    Args:
        offer_id: The offer ID
        country_code: Optional ISO country code (US, DE, FR, etc.)
        days: Number of days to analyze (default: 30)
        min_leads: Minimum conversions for significance (default: 20)
        top_n: Number of results to return (default: 3)
    
    Returns:
        JSON string with top N landing pages
    """
    # TODO: Implement actual Everflow API call
    # Return structured data - agent will format as table
    return json.dumps({
        "status": "success",
        "offer_id": offer_id,
        "country_code": country_code,
        "period_days": days,
        "top_lps": [
            {
                "offer_url_name": "Summer Sale LP v2",
                "conversion_rate": 4.85,
                "clicks": 12450,
                "conversions": 604
            },
            {
                "offer_url_name": "Summer Sale LP v1",
                "conversion_rate": 3.92,
                "clicks": 8230,
                "conversions": 323
            },
            {
                "offer_url_name": "Generic Offer Page",
                "conversion_rate": 2.15,
                "clicks": 5100,
                "conversions": 110
            }
        ],
        "_format_hint": "table"  # Hint for agent to format as table
    })


@tool
def wf3_export_report(
    report_type: str,
    date_range: str,
    columns: Optional[str] = None,  # Changed to str to avoid schema issues, will parse JSON
    filters: Optional[str] = None  # Changed to str to avoid schema issues, will parse JSON
) -> str:
    """
    Export a CSV report (fraud, conversions, stats, scrub, variance).
    
    Args:
        report_type: Type of report ("fraud", "conversions", "stats", "scrub", "variance")
        date_range: Natural language date range (e.g., "last week", "December 2024")
        columns: Optional JSON string of column names (e.g., '["sub1", "sub2", "affiliate"]')
        filters: Optional JSON string of filters (e.g., '{"offer_id": 123}')
    
    Returns:
        Download URL for the CSV file
    """
    # Parse columns and filters if provided
    columns_list = None
    filters_dict = None
    
    if columns:
        try:
            columns_list = json.loads(columns) if isinstance(columns, str) else columns
        except:
            pass
    
    if filters:
        try:
            filters_dict = json.loads(filters) if isinstance(filters, str) else filters
        except:
            pass
    
    # TODO: Implement actual Everflow API call and date parsing
    return json.dumps({
        "status": "success",
        "report_type": report_type,
        "date_range": date_range,
        "columns": columns_list,
        "filters": filters_dict,
        "download_url": f"https://api.everflow.io/exports/{report_type}_report_123.csv",
        "expires_in": "24 hours"
    })


@tool
def wf4_check_default_lp_alert(
    date: Optional[str] = None,
    click_threshold: int = 50
) -> str:
    """
    Check for traffic to default landing pages (alert workflow).
    
    Args:
        date: Specific date to check (YYYY-MM-DD, default: yesterday)
        click_threshold: Minimum clicks to alert (default: 50)
    
    Returns:
        List of alerts for default LP traffic
    """
    # TODO: Implement actual Everflow API call
    return json.dumps({
        "status": "success",
        "alerts": [],
        "message": "No default LP traffic detected above threshold"
    })


@tool
def wf5_check_paused_partners(
    analysis_days: int = 3,
    drop_threshold: float = -50.0
) -> str:
    """
    Identify partners with significant volume drops.
    
    Args:
        analysis_days: Number of days to compare (default: 3)
        drop_threshold: Percentage drop to alert (default: -50.0)
    
    Returns:
        List of partners with critical volume drops
    """
    # TODO: Implement actual Everflow API call
    return json.dumps({
        "status": "success",
        "alerts": [],
        "message": "No partners with significant volume drops detected"
    })


@tool
def wf6_generate_weekly_summary(
    days: int = 7,
    group_by: Literal["country", "offer"] = "country"
) -> str:
    """
    Generate weekly performance summary by country or offer.
    Filters by Advertiser_Internal label.
    
    Args:
        days: Number of days to analyze (default: 7)
        group_by: Group by "country" or "offer" (default: "country")
    
    Returns:
        Aggregated performance data with text summary
    """
    # TODO: Implement actual Everflow API call
    # Return structured data - agent will format as table
    return json.dumps({
        "status": "success",
        "period_days": days,
        "group_by": group_by,
        "total_revenue": 45230.00,
        "total_conversions": 1856,
        "data": [
            {
                "name": "United States",
                "revenue": 18500.00,
                "conversions": 756,
                "clicks": 45230
            },
            {
                "name": "Germany",
                "revenue": 12300.00,
                "conversions": 489,
                "clicks": 28100
            },
            {
                "name": "United Kingdom",
                "revenue": 6800.00,
                "conversions": 278,
                "clicks": 15400
            }
        ],
        "_format_hint": "table"  # Hint for agent to format as table
    })


def get_workflow_tools():
    """
    Get all workflow tools for the agent.
    
    Returns:
        List of LangChain tools for workflows WF1-WF6
    """
    return [
        wf1_generate_tracking_link,
        wf2_identify_top_lps,
        wf3_export_report,
        wf4_check_default_lp_alert,
        wf5_check_paused_partners,
        wf6_generate_weekly_summary,
    ]

