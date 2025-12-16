"""
Formatting helper functions for consistent number and table formatting.
These can be used by workflow tools to ensure consistent output.
"""
from typing import List, Dict, Any, Optional


def format_number(value: Any, decimals: int = 0) -> str:
    """
    Format a number with commas.
    
    Args:
        value: Number to format
        decimals: Number of decimal places (default: 0)
    
    Returns:
        Formatted string with commas
    """
    try:
        num = float(value)
        if decimals == 0:
            return f"{int(num):,}"
        else:
            return f"{num:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: Any, decimals: int = 2) -> str:
    """
    Format a number as a percentage.
    
    Args:
        value: Number to format (can be decimal like 0.0485 or already percentage like 4.85)
        decimals: Number of decimal places (default: 2)
    
    Returns:
        Formatted percentage string
    """
    try:
        num = float(value)
        # If number is less than 1, assume it's a decimal (0.0485 = 4.85%)
        if num < 1:
            num = num * 100
        return f"{num:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_currency(value: Any, symbol: str = "$", decimals: int = 2) -> str:
    """
    Format a number as currency.
    
    Args:
        value: Number to format
        symbol: Currency symbol (default: "$")
        decimals: Number of decimal places (default: 2)
    
    Returns:
        Formatted currency string
    """
    try:
        num = float(value)
        return f"{symbol}{num:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_table(headers: List[str], rows: List[List[Any]], 
                 align_right: Optional[List[bool]] = None) -> str:
    """
    Format data as a markdown table.
    
    Args:
        headers: List of column headers
        rows: List of rows, where each row is a list of values
        align_right: Optional list of booleans indicating which columns to right-align
    
    Returns:
        Markdown table string
    """
    if not headers or not rows:
        return ""
    
    num_cols = len(headers)
    if align_right is None:
        align_right = [False] * num_cols
    
    # Format headers
    header_row = "| " + " | ".join(headers) + " |"
    
    # Format separator with alignment
    separator_parts = []
    for i, right_align in enumerate(align_right):
        if right_align:
            separator_parts.append(":" + "-" * (len(str(headers[i])) + 1))
        else:
            separator_parts.append("-" * (len(str(headers[i])) + 2))
    separator = "|" + "|".join(separator_parts) + "|"
    
    # Format rows
    formatted_rows = []
    for row in rows:
        # Pad row to match header length
        padded_row = row + [""] * (num_cols - len(row))
        formatted_row = "| " + " | ".join(str(cell) for cell in padded_row[:num_cols]) + " |"
        formatted_rows.append(formatted_row)
    
    return "\n".join([header_row, separator] + formatted_rows)


def format_top_lps_table(lps_data: List[Dict[str, Any]]) -> str:
    """
    Format top landing pages data as a table.
    
    Args:
        lps_data: List of landing page dictionaries with keys like:
                  offer_url_name, conversion_rate, clicks, conversions
    
    Returns:
        Formatted markdown table
    """
    if not lps_data:
        return "No landing page data available."
    
    headers = ["Landing Page", "Conversion Rate", "Clicks", "Conversions"]
    rows = []
    
    for lp in lps_data:
        rows.append([
            lp.get("offer_url_name", "Unknown"),
            format_percentage(lp.get("conversion_rate", 0)),
            format_number(lp.get("clicks", 0)),
            format_number(lp.get("conversions", 0))
        ])
    
    return format_table(headers, rows, align_right=[False, True, True, True])


def format_weekly_summary_table(summary_data: List[Dict[str, Any]], 
                                group_by: str = "country") -> str:
    """
    Format weekly summary data as a table.
    
    Args:
        summary_data: List of summary dictionaries
        group_by: "country" or "offer"
    
    Returns:
        Formatted markdown table
    """
    if not summary_data:
        return "No summary data available."
    
    if group_by == "country":
        headers = ["Country", "Revenue", "Conversions", "Clicks"]
        name_key = "name"
    else:
        headers = ["Offer", "Revenue", "Conversions", "Clicks"]
        name_key = "name"
    
    rows = []
    for item in summary_data:
        rows.append([
            item.get(name_key, "Unknown"),
            format_currency(item.get("revenue", 0)),
            format_number(item.get("conversions", 0)),
            format_number(item.get("clicks", 0))
        ])
    
    return format_table(headers, rows, align_right=[False, True, True, True])


def format_report_info(report_data: Dict[str, Any]) -> str:
    """
    Format report information as a table.
    
    Args:
        report_data: Dictionary with keys like report_type, date_range, download_url
    
    Returns:
        Formatted markdown table
    """
    headers = ["Field", "Value"]
    rows = [
        ["Report Type", report_data.get("report_type", "Unknown")],
        ["Period", report_data.get("date_range", "Unknown")],
        ["Download Link", f"[📄 Download CSV]({report_data.get('download_url', '#')})"],
        ["Expires In", report_data.get("expires_in", "24 hours")]
    ]
    
    return format_table(headers, rows, align_right=[False, False])

