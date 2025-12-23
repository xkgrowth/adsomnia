"""
Workflow Tools for LangChain Agent.
Replaces SQL tools with Everflow workflow tools (WF1-WF6).
"""
from typing import Optional, Literal, Union
from langchain.tools import tool
from datetime import datetime, timedelta
import json
from .entity_resolver import get_resolver


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
      * IMPORTANT: If user specifies "year to date" or "YTD", calculate days from January 1st of current year to today
      * If user specifies "last week", use 7 days
      * If user specifies "last month", use ~30 days
      * Always parse date ranges from the user query and calculate the days parameter
    - min_leads: Minimum conversions for significance (default: 20)
    - top_n: Number of results to return (default: 10)
    - label: Optional label filter (e.g., "Advertiser_Internal")
    - metrics: Optional JSON string of specific metrics to include (e.g., '["cv", "cvr", "revenue"]')
      * Available metrics: ["cv", "cvr", "epc", "rpc", "payout", "revenue", "clicks", "profit"]
      * Default (if not specified): ["cv", "cvr", "epc", "rpc", "payout"]
      * Analyze user query to determine which metrics are most relevant
    
    Returns top N landing pages sorted by conversion rate (or most relevant metric if CVR not available).
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
    
    "wf3_fetch_conversions": """
    Fetch conversion data for viewing (not exporting). Use this when users want to VIEW conversion reports, especially for fraud detection.
    
    Required parameters:
    - report_type: Type of report ("fraud" or "conversions")
    - date_range: Natural language date range (e.g., "last week", "last month", "year to date")
    
    Optional parameters:
    - filters: JSON string of filters. Supports both IDs and names - names will be automatically resolved to IDs.
      * Example with IDs: '{"offer_id": 123, "affiliate_id": 456, "source_id": 134505}'
      * Example with names: '{"offer_name": "Papoaolado - BR - DOI - (Responsive)", "affiliate_name": "iMonetizeIt", "source_id": 134505}'
      * Supported filter keys: offer_id, offer_name, affiliate_id, affiliate_name, source_id
      * If using names, the tool will automatically resolve them to IDs
    - page: Page number (default: 1)
    - page_size: Results per page (default: 50, max: 100)
    
    Returns conversion data with summary statistics for viewing in the UI.
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
def wf1_generate_tracking_link(
    affiliate_id: Union[int, str],
    offer_id: Union[int, str]
) -> str:
    """
    Generate a tracking link for an affiliate on an offer.
    May require approval confirmation if affiliate is not already approved.
    
    Args:
        affiliate_id: The affiliate/partner ID (int) or name (str)
        offer_id: The offer ID (int) or name (str)
    
    Returns:
        Tracking URL or confirmation request
    """
    resolver = get_resolver()
    
    # Resolve names to IDs
    resolved_aff_id = resolver.resolve_affiliate(affiliate_id)
    resolved_offer_id = resolver.resolve_offer(offer_id)
    
    if resolved_aff_id is None:
        return json.dumps({
            "status": "error",
            "message": f"Could not find affiliate: {affiliate_id}. Please provide a valid affiliate ID or name."
        })
    
    if resolved_offer_id is None:
        return json.dumps({
            "status": "error",
            "message": f"Could not find offer: {offer_id}. Please provide a valid offer ID or name."
        })
    
    # TODO: Implement actual Everflow API call
    # This is a placeholder that shows the structure
    return json.dumps({
        "status": "success",
        "tracking_link": f"https://tracking.everflow.io/aff_c?offer_id={resolved_offer_id}&aff_id={resolved_aff_id}",
        "message": f"Tracking link generated for Partner {resolved_aff_id} on Offer {resolved_offer_id}"
    })


@tool
def wf2_identify_top_lps(
    offer_id: Union[int, str],
    country_code: Optional[Union[str, int]] = None,
    days: int = 30,
    min_leads: int = 20,
    top_n: int = 10,
    label: Optional[str] = None,
    metrics: Optional[str] = None  # JSON string of requested metrics: ["cv", "cvr", "epc", "rpc", "payout", "revenue", "clicks", "profit"]
) -> str:
    """
    Find top performing landing pages for an offer.
    
    Args:
        offer_id: The offer ID (int) or name (str)
        country_code: Optional ISO country code (US, DE, FR, etc.) or country name
        days: Number of days to analyze (default: 30)
        min_leads: Minimum conversions for significance (default: 20)
        top_n: Number of results to return (default: 10)
        label: Optional label filter (e.g., "Advertiser_Internal")
        metrics: Optional JSON string of specific metrics to include. 
                Available: ["cv", "cvr", "epc", "rpc", "payout", "revenue", "clicks", "profit"]
                If not provided, returns all default metrics (cv, cvr, epc, rpc, payout)
                Examples: '["cv", "cvr", "revenue"]' or '["clicks", "conversions", "cvr"]'
    
    Returns:
        JSON string with top N landing pages
    """
    resolver = get_resolver()
    
    # Resolve offer name to ID with suggestions
    resolved_offer_id, suggestions = resolver.resolve_offer(offer_id, return_suggestions=True)
    
    # Debug logging
    print(f"🔍 Resolver returned: offer_id={resolved_offer_id}, suggestions_count={len(suggestions) if suggestions else 0}")
    if suggestions:
        for i, sug in enumerate(suggestions[:3]):
            print(f"   Suggestion {i+1}: {sug.get('offer_name')} (ID: {sug.get('offer_id')}, similarity: {sug.get('similarity')})")
    
    # Auto-use good matches (similarity >= 85%) from suggestions if resolver didn't find one
    if resolved_offer_id is None and suggestions:
        # Check if there's a good match (>= 85% similarity)
        # Handle both float (85.0) and int (85) similarity values
        for sug in suggestions:
            similarity = sug.get("similarity", 0)
            # Convert to float if needed
            if isinstance(similarity, (int, float)):
                similarity_float = float(similarity)
            else:
                similarity_float = 0.0
            
            if similarity_float >= 85.0:
                resolved_offer_id = sug.get("offer_id")
                print(f"✅ Auto-using good match: {sug.get('offer_name')} (ID: {resolved_offer_id}, {similarity_float}% match)")
                break
    
    if resolved_offer_id is None:
        # Build error message with suggestions
        # Only say "couldn't find" if there are no suggestions at all
        if not suggestions:
            error_msg = f"Could not find offer: {offer_id}. Please provide a valid offer ID or name."
        else:
            # If we have suggestions, be more helpful
            best_match = suggestions[0] if suggestions else None
            best_similarity = best_match.get("similarity", 0) if best_match else 0
            
            if best_similarity >= 85.0:
                # This shouldn't happen (should have been auto-used), but handle it gracefully
                error_msg = f"Found similar offer: {best_match.get('offer_name')} (ID: {best_match.get('offer_id')}, {best_similarity}% match)."
            else:
                error_msg = f"Could not find exact match for '{offer_id}'. Did you mean one of these?\n"
                for sug in suggestions[:5]:
                    similarity = sug.get("similarity", 0)
                    error_msg += f"* {sug.get('offer_name', 'Unknown')} (ID: {sug.get('offer_id')}, {similarity}% match)\n"
                error_msg += "\nPlease provide the correct offer ID or name."
        
        return json.dumps({
            "status": "error",
            "message": error_msg
        })
    
    # Resolve country name to code
    resolved_country = None
    if country_code:
        resolved_country = resolver.resolve_country(country_code)
        if resolved_country is None and isinstance(country_code, str) and len(country_code) > 3:
            # If it's a name that wasn't found, return error
            return json.dumps({
                "status": "error",
                "message": f"Could not find country: {country_code}. Please provide a valid country code (e.g., US, DE) or name."
            })
        # If it's already a code, use it
        if resolved_country is None:
            resolved_country = country_code.upper() if isinstance(country_code, str) else str(country_code)
    
    # Implement actual Everflow API call
    try:
        from .everflow_client import EverflowClient
        from datetime import datetime, timedelta
        
        client = EverflowClient()
        
        # Calculate date range
        to_date = datetime.now()
        
        # Special handling for "year to date" - if days is very large (>= 300), 
        # it's likely a year-to-date request, so use January 1st of current year
        if days >= 300:
            # Year to date: from January 1st of current year to today
            from_date = datetime(to_date.year, 1, 1)
        else:
            # Regular date range: go back N days
            from_date = to_date - timedelta(days=days)
        
        # Build columns - must be objects with "column" key
        columns = [
            {"column": "offer_url"},
            {"column": "offer"}
        ]
        if resolved_country:
            columns.append({"column": "country"})
        
        # Build filters
        filters = [
            {
                "resource_type": "offer",
                "filter_id_value": str(resolved_offer_id)
            }
        ]
        
        if resolved_country:
            filters.append({
                "resource_type": "country",
                "filter_id_value": resolved_country
            })
        
        if label:
            filters.append({
                "resource_type": "label",
                "filter_id_value": label
            })
        
        # Build payload
        # Note: currency_id is required for entity reporting endpoint
        payload = {
            "columns": columns,
            "query": {"filters": filters},
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "timezone_id": client.timezone_id,
            "currency_id": "EUR"  # Required field for entity reporting
        }
        
        # Debug: Print payload for troubleshooting
        print(f"🔍 WF2 API Payload: {json.dumps(payload, indent=2)}")
        
        # Make API call
        try:
            response = client._request("POST", "/v1/networks/reporting/entity", data=payload)
            table = response.get("table", [])
            print(f"✅ API Response: {len(table)} rows returned")
        except Exception as api_error:
            error_msg = str(api_error)
            # Try to get more details from the exception
            if hasattr(api_error, 'response'):
                if hasattr(api_error.response, 'status_code'):
                    error_msg += f" (Status: {api_error.response.status_code})"
                if hasattr(api_error.response, 'text'):
                    try:
                        error_json = api_error.response.json()
                        error_msg += f"\nAPI Error Details: {json.dumps(error_json, indent=2)}"
                    except:
                        error_msg += f"\nAPI Response: {api_error.response.text}"
            print(f"❌ API Error: {error_msg}")
            print(f"❌ Payload sent: {json.dumps(payload, indent=2)}")
            
            # Return user-friendly error message
            if "400" in error_msg or "Bad Request" in error_msg:
                # Check if it's an "Internal error" from the API (server-side issue)
                if "Internal error" in error_msg:
                    return json.dumps({
                        "status": "error",
                        "message": "The Everflow API entity reporting endpoint is currently returning an internal error. This appears to be an issue with the Everflow API service itself, not your request. Please:\n1. Try again in a few moments\n2. Check if your Everflow account has access to the entity reporting endpoint\n3. Contact Everflow support if the issue persists\n\nNote: The API key is working (other endpoints respond correctly), but the entity reporting endpoint specifically has an issue."
                    })
                return json.dumps({
                    "status": "error",
                    "message": f"Invalid request to Everflow API. Please check the offer name and date range. Error details: {error_msg}"
                })
            return json.dumps({
                "status": "error",
                "message": f"Failed to fetch landing page data from Everflow API: {error_msg}"
            })
        
        # Parse requested metrics (if provided)
        requested_metrics = None
        if metrics:
            try:
                requested_metrics = json.loads(metrics) if isinstance(metrics, str) else metrics
                if not isinstance(requested_metrics, list):
                    requested_metrics = None
            except:
                requested_metrics = None
        
        # Default metrics if none specified (standard WF2 columns)
        default_metrics = ["cv", "cvr", "epc", "rpc", "payout"]
        if requested_metrics is None:
            requested_metrics = default_metrics
        
        # Normalize metric names (handle aliases)
        metric_aliases = {
            "conversions": "cv",
            "conversion_rate": "cvr",
            "earnings_per_click": "epc",
            "revenue_per_click": "rpc",
            "total_payout": "payout",
            "total_revenue": "revenue",
            "total_clicks": "clicks"
        }
        normalized_metrics = [metric_aliases.get(m.lower(), m.lower()) for m in requested_metrics]
        
        # Process results
        # Note: Everflow API returns data in a nested structure:
        # - row["columns"] contains column data (offer_url, offer, etc.)
        # - row["reporting"] contains metrics (clicks, conversions, cvr, etc.)
        processed_lps = []
        for row in table:
            # Extract reporting metrics
            reporting = row.get("reporting", {})
            clicks = reporting.get("total_click", 0) or reporting.get("clicks", 0) or 0
            conversions = reporting.get("cv", 0) or reporting.get("total_cv", 0) or reporting.get("conversions", 0) or 0
            revenue = reporting.get("revenue", 0.0) or 0.0
            payout = reporting.get("payout", 0.0) or 0.0
            profit = reporting.get("profit", 0.0) or (revenue - payout)
            # CVR is already calculated by API (as percentage, e.g., 1.003 = 1.003%)
            cvr = reporting.get("cvr", 0.0) or 0.0
            
            # Filter by minimum conversions
            if conversions < min_leads:
                continue
            
            # Calculate EPC (Earnings Per Click) = Payout / Clicks
            epc = round(payout / clicks, 4) if clicks > 0 else 0.0
            
            # Calculate RPC (Revenue Per Click) = Revenue / Clicks
            rpc = round(revenue / clicks, 4) if clicks > 0 else 0.0
            
            # Extract offer info from columns array
            offer_id = None
            offer_name = "Unknown Offer"
            
            # Extract landing page info from columns array
            lp_id = None
            lp_name = "Unknown Landing Page"
            
            columns = row.get("columns", [])
            for col in columns:
                col_type = col.get("column_type")
                if col_type == "offer":
                    offer_id = col.get("id")
                    offer_name = col.get("label", f"Offer {offer_id}")
                elif col_type == "offer_url":
                    lp_id = col.get("id")
                    lp_name = col.get("label", f"LP {lp_id}")
            
            # Fallback: try to get from row directly if not found in columns
            if not offer_id:
                offer_id = row.get("offer_id")
                offer_name = row.get("offer_name") or row.get("advertiser_name") or row.get("offer") or f"Offer {offer_id or 'Unknown'}"
            
            if not lp_id:
                lp_id = row.get("offer_url_id")
                lp_name = row.get("offer_url_name") or row.get("offer_url") or f"LP {lp_id or 'Unknown'}"
            
            # Build result dict with all available metrics
            lp_data = {
                "offer_id": offer_id,
                "offer_name": offer_name,
                "offer_url_id": lp_id,
                "offer_url_name": lp_name,
                "cv": int(conversions),  # CV = Conversions
                "cvr": round(cvr, 2),  # CVR = Conversion Rate (as percentage)
                "epc": epc,  # EPC = Earnings Per Click (Payout / Clicks)
                "rpc": rpc,  # RPC = Revenue Per Click (Revenue / Clicks)
                "payout": round(payout, 2),
                "revenue": round(revenue, 2),
                "profit": round(profit, 2),
                "clicks": int(clicks),
                # Keep these for backwards compatibility and sorting
                "conversions": int(conversions),
                "conversion_rate": round(cvr, 2)
            }
            
            # Filter to only include requested metrics (plus always-include fields)
            # Always include: offer_name, offer_url_name (these are identifiers, not metrics)
            filtered_data = {
                "offer_id": lp_data["offer_id"],
                "offer_name": lp_data["offer_name"],
                "offer_url_id": lp_data["offer_url_id"],
                "offer_url_name": lp_data["offer_url_name"]
            }
            
            # Add requested metrics
            for metric in normalized_metrics:
                if metric in lp_data:
                    filtered_data[metric] = lp_data[metric]
            
            processed_lps.append(filtered_data)
        
        # Sort by conversion rate (descending) if available, otherwise by CV, otherwise by first available metric
        def get_sort_key(x):
            # Try conversion_rate first (for backwards compatibility)
            if "conversion_rate" in x:
                return x["conversion_rate"]
            # Try cvr (new format)
            if "cvr" in x:
                return x["cvr"]
            # Try cv/conversions
            if "cv" in x:
                return x["cv"]
            if "conversions" in x:
                return x["conversions"]
            # Fallback to first numeric metric
            for key in ["revenue", "payout", "clicks", "epc", "rpc"]:
                if key in x:
                    return x[key]
            return 0
        
        processed_lps.sort(key=get_sort_key, reverse=True)
        
        # Return top N (or all if top_n is very large, meaning "show all")
        if top_n >= 1000:
            # User requested "all results" - return everything
            top_lps = processed_lps
        else:
            # Return top N
            top_lps = processed_lps[:top_n]
        
        if not top_lps:
            return json.dumps({
                "status": "error",
                "message": f"No landing pages found for Offer {resolved_offer_id} with at least {min_leads} conversions in the last {days} days."
            })
        
        return json.dumps({
            "status": "success",
            "offer_id": resolved_offer_id,
            "country_code": resolved_country,
            "period_days": days,
            "top_lps": top_lps,
            "_format_hint": "table"  # Hint for agent to format as table
        })
        
    except Exception as e:
        print(f"Error fetching landing pages from Everflow API: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to fetch landing page data from Everflow API: {str(e)}"
        })


@tool
def query_top_offers(
    days: int = 30,
    min_leads: int = 0,
    top_n: int = 10,
    country_code: Optional[Union[str, int]] = None,
    label: Optional[str] = None,
    sort_by: str = "cv"  # "cv", "revenue", "payout", "cvr"
) -> str:
    """
    Query top offers by aggregating offer-level metrics.
    Use this when users ask for "top offers", "best performing offers", "offers with highest conversions", etc.
    
    Args:
        days: Number of days to analyze (default: 30)
        min_leads: Minimum conversions for significance (default: 0)
        top_n: Number of results to return (default: 10)
        country_code: Optional ISO country code (US, DE, FR, etc.) or country name
        label: Optional label filter (e.g., "Advertiser_Internal")
        sort_by: Metric to sort by - "cv" (conversions), "revenue", "payout", "cvr" (conversion rate)
    
    Returns:
        JSON string with top N offers
    """
    try:
        from .everflow_client import EverflowClient
        from datetime import datetime, timedelta
        
        client = EverflowClient()
        
        # Calculate date range
        to_date = datetime.now()
        if days >= 300:
            # Year to date
            from_date = datetime(to_date.year, 1, 1)
        else:
            from_date = to_date - timedelta(days=days)
        
        # Build columns - query by offer (not offer_url)
        columns = [
            {"column": "offer"}
        ]
        if country_code:
            columns.append({"column": "country"})
        
        # Build filters
        filters = []
        if country_code:
            resolver = get_resolver()
            resolved_country = resolver.resolve_country(country_code)
            if resolved_country:
                filters.append({
                    "resource_type": "country",
                    "filter_id_value": resolved_country
                })
        
        if label:
            filters.append({
                "resource_type": "label",
                "filter_id_value": label
            })
        
        # Build payload
        payload = {
            "columns": columns,
            "query": {"filters": filters} if filters else {},
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "timezone_id": client.timezone_id,
            "currency_id": "EUR"
        }
        
        # Make API call
        response = client._request("POST", "/v1/networks/reporting/entity", data=payload)
        table = response.get("table", [])
        
        # Process and aggregate results by offer
        processed_offers = []
        for row in table:
            reporting = row.get("reporting", {})
            clicks = reporting.get("total_click", 0) or reporting.get("clicks", 0) or 0
            conversions = reporting.get("cv", 0) or reporting.get("total_cv", 0) or reporting.get("conversions", 0) or 0
            revenue = reporting.get("revenue", 0.0) or 0.0
            payout = reporting.get("payout", 0.0) or 0.0
            cvr = reporting.get("cvr", 0.0) or 0.0
            
            # Filter by minimum conversions
            if conversions < min_leads:
                continue
            
            # Extract offer info
            offer_id = None
            offer_name = "Unknown Offer"
            
            columns_data = row.get("columns", [])
            for col in columns_data:
                if col.get("column_type") == "offer":
                    offer_id = col.get("id")
                    offer_name = col.get("label", f"Offer {offer_id}")
                    break
            
            if not offer_id:
                offer_id = row.get("offer_id")
                offer_name = row.get("offer_name") or row.get("advertiser_name") or row.get("offer") or f"Offer {offer_id or 'Unknown'}"
            
            # Calculate metrics
            epc = round(payout / clicks, 4) if clicks > 0 else 0.0
            rpc = round(revenue / clicks, 4) if clicks > 0 else 0.0
            profit = revenue - payout
            
            processed_offers.append({
                "offer_id": offer_id,
                "offer_name": offer_name,
                "cv": int(conversions),
                "cvr": round(cvr, 2),
                "revenue": round(revenue, 2),
                "payout": round(payout, 2),
                "profit": round(profit, 2),
                "clicks": int(clicks),
                "epc": epc,
                "rpc": rpc
            })
        
        # Sort by requested metric
        sort_key_map = {
            "cv": "cv",
            "conversions": "cv",
            "revenue": "revenue",
            "payout": "payout",
            "cvr": "cvr",
            "conversion_rate": "cvr"
        }
        sort_key = sort_key_map.get(sort_by.lower(), "cv")
        
        processed_offers.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
        
        # Return top N
        top_offers = processed_offers[:top_n]
        
        if not top_offers:
            return json.dumps({
                "status": "error",
                "message": f"No offers found with at least {min_leads} conversions in the last {days} days."
            })
        
        return json.dumps({
            "status": "success",
            "period_days": days,
            "sort_by": sort_by,
            "top_offers": top_offers,
            "_format_hint": "table"
        })
        
    except Exception as e:
        print(f"Error querying top offers: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to query offers: {str(e)}"
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
        filters: Optional JSON string of filters (e.g., '{"offer_id": 123, "offer_name": "Summer Promo"}')
    
    Returns:
        Download URL for the CSV file
    """
    resolver = get_resolver()
    
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
    
    # Resolve entity names in filters using centralized resolver (workflow-agnostic)
    if filters_dict:
        try:
            filters_dict = resolver.resolve_filters(filters_dict)
        except ValueError as e:
            # Return error if entity resolution failed
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
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
def wf3_fetch_conversions(
    report_type: str,
    date_range: str,
    filters: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> str:
    """
    Fetch conversion data for viewing (not exporting). Use this when users want to VIEW conversion reports, especially for fraud detection.
    
    This tool returns a PRE-FORMATTED markdown response that should be passed through directly to the user without modification.
    """
    print(f"🔍 wf3_fetch_conversions called with: report_type={report_type}, date_range={date_range}, filters={filters}, page={page}, page_size={page_size}")
    """
    Fetch conversion data for viewing (not exporting).
    Use this when the user wants to VIEW conversion data, especially for fraud detection.
    For exporting to CSV, use wf3_export_report instead.
    
    Args:
        report_type: Type of report ("fraud", "conversions")
        date_range: Natural language date range (e.g., "last week", "last month", "year to date")
        filters: Optional JSON string of filters. Supports both IDs and names:
            - IDs: '{"offer_id": 123, "affiliate_id": 456, "source_id": 134505}'
            - Names (will be resolved automatically): '{"offer_name": "Papoaolado - BR - DOI", "affiliate_name": "iMonetizeIt", "source_id": 134505}'
            - Supported keys: offer_id, offer_name, affiliate_id, affiliate_name, source_id
        page: Page number (default: 1)
        page_size: Results per page (default: 50, max: 100)
    
    Returns:
        JSON string with conversion data, summary statistics, and pagination info
    """
    resolver = get_resolver()
    
    # Parse filters if provided
    filters_dict = None
    if filters:
        try:
            filters_dict = json.loads(filters) if isinstance(filters, str) else filters
        except:
            pass
    
    # Resolve entity names in filters using centralized resolver (workflow-agnostic)
    if filters_dict:
        try:
            filters_dict = resolver.resolve_filters(filters_dict)
        except ValueError as e:
            # Return error if entity resolution failed
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    # Parse date range
    from datetime import datetime, timedelta
    today = datetime.now()
    
    date_mappings = {
        "last week": (today - timedelta(days=7), today - timedelta(days=1)),
        "this week": (today - timedelta(days=today.weekday()), today),
        "last month": (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1) - timedelta(days=1)
        ),
        "this month": (today.replace(day=1), today),
        "last 7 days": (today - timedelta(days=7), today),
        "last 30 days": (today - timedelta(days=30), today),
    }
    
    # Check for "year to date"
    if "year to date" in date_range.lower() or "ytd" in date_range.lower():
        from_date = datetime(today.year, 1, 1)
        to_date = today
    elif date_range.lower() in date_mappings:
        from_date, to_date = date_mappings[date_range.lower()]
    else:
        # Default to last 30 days
        from_date = today - timedelta(days=30)
        to_date = today
    
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    
    # Build API filters
    api_filters = []
    
    if filters_dict:
        if "offer_id" in filters_dict:
            api_filters.append({
                "resource_type": "offer",
                "filter_id_value": str(filters_dict["offer_id"])
            })
        if "affiliate_id" in filters_dict:
            api_filters.append({
                "resource_type": "affiliate",
                "filter_id_value": str(filters_dict["affiliate_id"])
            })
        if "source_id" in filters_dict:
            api_filters.append({
                "resource_type": "source",
                "filter_id_value": str(filters_dict["source_id"])
            })
    
    # Add fraud filter if report_type is "fraud"
    # Note: According to Everflow API docs, fraud filtering might need to be done differently
    # The API supports filters but "is_fraud" might not be a filter_type
    # We'll try using it, but if it fails, we may need to filter client-side
    if report_type.lower() == "fraud":
        # Try adding fraud filter - this might need adjustment based on actual API response
        # The API might have a different way to filter fraud conversions
        api_filters.append({
            "filter_type": "is_fraud",
            "filter_value": True
        })
    
    # Default columns for conversion reports
    # These columns are available in the conversions/export endpoint
    # Matching Everflow table columns: Status | Date | Click Date | Sub1 | Offer | Partner | Delta | Payout | Conversion IP | Transaction ID | Adv1 | Adv2 | Conversion ID | Event Name
    default_columns = [
        "conversion_id", "click_id", "status", "date", "click_date",
        "sub1", "affiliate", "partner", "offer", "delta", "payout", "revenue",
        "conversion_ip", "transaction_id", "adv1", "adv2", "event_name",
        "is_fraud", "fraud_reason", "offer_events"
    ]
    
    # Note: source_id filter significantly narrows results, so month-long queries should be fine
    # The API is optimized when proper filters (offer, affiliate, source_id) are provided
    
    try:
        from .everflow_client import EverflowClient
        client = EverflowClient()
        
        # Debug logging
        print(f"🔍 wf3_fetch_conversions called with:")
        print(f"   report_type: {report_type}")
        print(f"   date_range: {date_range}")
        print(f"   from_date: {from_date_str}, to_date: {to_date_str}")
        print(f"   filters_dict: {filters_dict}")
        print(f"   api_filters: {json.dumps(api_filters, indent=2)}")
        print(f"   page: {page}, page_size: {page_size}")
        
        # Verify source_id is in filters (critical for performance)
        has_source_filter = any(f.get("resource_type") == "source" for f in api_filters)
        if has_source_filter:
            source_filter = next((f for f in api_filters if f.get("resource_type") == "source"), None)
            print(f"✅ Source ID filter active: {source_filter.get('filter_id_value') if source_filter else 'N/A'}")
        else:
            print(f"⚠️  No source_id filter - query may be slower")
        
        # Fetch conversions with timeout handling
        import time
        start_time = time.time()
        print(f"⏱️  Starting API call (timeout: 30 seconds)...")
        try:
            response = client.fetch_conversions(
                columns=default_columns,
                filters=api_filters,
                from_date=from_date_str,
                to_date=to_date_str,
                page=page,
                page_size=page_size
            )
            elapsed = time.time() - start_time
            print(f"✅ API call completed in {elapsed:.2f} seconds")
        except Exception as api_error:
            error_msg = str(api_error)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return json.dumps({
                    "status": "error",
                    "message": f"The query timed out. The date range '{date_range}' may be too large or return too much data. Try a shorter date range (e.g., 'last week' or 'last 7 days') or add more filters to narrow the results.",
                    "error_type": "timeout"
                })
            raise  # Re-raise if not a timeout
        
        # Process response to extract summary statistics
        raw_conversions = response.get("table", []) or response.get("conversions", [])
        paging = response.get("paging", {})
        
        print(f"📊 Processing {len(raw_conversions)} conversions...")
        print(f"📊 Total count from API: {paging.get('total_count', len(raw_conversions))}")
        
        # Log if source_id filter is working (should significantly reduce results)
        if has_source_filter and len(raw_conversions) > 0:
            print(f"✅ Source ID filter working - returned {len(raw_conversions)} conversions")
        
        # Filter for fraud conversions if report_type is "fraud"
        # Apply client-side filtering since API filter might not work correctly
        original_count = len(raw_conversions)
        if report_type.lower() == "fraud":
            raw_conversions = [conv for conv in raw_conversions if conv.get("is_fraud") == True]
            print(f"🔍 Fraud filter applied: {len(raw_conversions)} fraud conversions (from {original_count} total)")
            if len(raw_conversions) == 0 and original_count > 0:
                print(f"⚠️  Warning: No fraud conversions found in {original_count} total conversions")
        
        # Process and normalize all conversion records with ALL fields
        # Extract nested relationship data and flatten it for easier frontend access
        conversions = []
        for conv in raw_conversions:
            # Extract offer name from various locations
            offer_name = None
            if conv.get("offer"):
                offer_name = conv.get("offer")
            elif conv.get("relationship", {}).get("offer", {}).get("name"):
                offer_name = conv.get("relationship", {}).get("offer", {}).get("name")
            
            # Extract affiliate/partner name from various locations
            partner_name = None
            if conv.get("partner"):
                partner_name = conv.get("partner")
            elif conv.get("affiliate"):
                partner_name = conv.get("affiliate")
            elif conv.get("relationship", {}).get("affiliate", {}).get("name"):
                partner_name = conv.get("relationship", {}).get("affiliate", {}).get("name")
            
            # Format dates
            date_str = None
            if conv.get("date"):
                date_str = conv.get("date")
            elif conv.get("conversion_unix_timestamp"):
                from datetime import datetime
                try:
                    ts = int(conv.get("conversion_unix_timestamp"))
                    date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                except:
                    pass
            
            click_date_str = None
            if conv.get("click_date"):
                click_date_str = conv.get("click_date")
            elif conv.get("click_unix_timestamp"):
                from datetime import datetime
                try:
                    ts = int(conv.get("click_unix_timestamp"))
                    click_date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                except:
                    pass
            
            # Build normalized conversion record with ALL fields
            normalized_conv = {
                "conversion_id": conv.get("conversion_id"),
                "click_id": conv.get("click_id"),
                "status": conv.get("status"),
                "date": date_str or conv.get("date"),
                "click_date": click_date_str or conv.get("click_date"),
                "sub1": conv.get("sub1"),
                "sub2": conv.get("sub2"),
                "sub3": conv.get("sub3"),
                "sub4": conv.get("sub4"),
                "sub5": conv.get("sub5"),
                "offer": offer_name or conv.get("offer"),
                "partner": partner_name or conv.get("partner") or conv.get("affiliate"),
                "affiliate": partner_name or conv.get("affiliate"),
                "delta": conv.get("delta"),
                "payout": conv.get("payout"),
                "revenue": conv.get("revenue"),
                "conversion_ip": conv.get("conversion_user_ip") or conv.get("conversion_ip") or conv.get("session_user_ip"),
                "transaction_id": conv.get("transaction_id"),
                "adv1": conv.get("adv1"),
                "adv2": conv.get("adv2"),
                "adv3": conv.get("adv3"),
                "adv4": conv.get("adv4"),
                "adv5": conv.get("adv5"),
                "event_name": conv.get("event") or conv.get("event_name"),
                "offer_events": conv.get("offer_events"),
                "is_fraud": conv.get("is_fraud"),
                "fraud_reason": conv.get("fraud_reason"),
                # Include all other fields from the API response
                **{k: v for k, v in conv.items() if k not in [
                    "relationship", "offer", "affiliate", "partner", 
                    "date", "click_date", "conversion_unix_timestamp", "click_unix_timestamp",
                    "conversion_user_ip", "session_user_ip", "event"
                ]}
            }
            conversions.append(normalized_conv)
        
        # Calculate summary statistics
        # For fraud reports, use actual filtered count (not API total_count which includes all conversions)
        # For regular reports, use API total_count if available (may be paginated)
        if report_type.lower() == "fraud":
            # Fraud reports are filtered client-side, so use actual filtered count
            total = len(conversions)
            print(f"📊 Summary: Using filtered count ({total}) for fraud report")
        else:
            # Regular reports: use API total_count if available, otherwise count current page
            total = paging.get("total_count", len(conversions))
            if total != len(conversions) and len(conversions) < total:
                print(f"📊 Summary: Using API total_count ({total}), current page has {len(conversions)} records")
        
        status_counts = {}
        total_payout = 0
        total_revenue = 0
        total_gross_sales = 0
        
        for conv in conversions:
            status = conv.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            payout = float(conv.get("payout", 0) or 0)
            revenue = float(conv.get("revenue", 0) or 0)
            gross_sales = float(conv.get("gross_sales", 0) or 0)
            
            total_payout += payout
            total_revenue += revenue
            total_gross_sales += gross_sales
        
        summary = {
            "total": total,
            "approved": status_counts.get("approved", 0),
            "invalid": status_counts.get("invalid", 0),
            "pending": status_counts.get("pending", 0),
            "rejected_manual": status_counts.get("rejected_manual", 0),
            "rejected_throttle": status_counts.get("rejected_throttle", 0),
            "payout": round(total_payout, 2),
            "revenue": round(total_revenue, 2),
            "gross_sales": round(total_gross_sales, 2)
        }
        
        # Format conversions for table display
        # Preview columns (key columns for chat preview): Status, Date, Offer, Partner, Payout, Conversion ID
        # Full columns (all columns for modal): Status, Date, Click Date, Sub1, Offer, Partner, Delta, Payout, Conversion IP, Transaction ID, Adv1, Adv2, Conversion ID, Event Name
        
        # Prepare preview data (first 10 records) - only include essential fields for preview
        preview_conversions = []
        if conversions:
            for conv in conversions[:10]:
                # Extract offer name from various possible locations
                offer_name = None
                if conv.get("offer"):
                    offer_name = conv.get("offer")
                elif conv.get("relationship", {}).get("offer", {}).get("name"):
                    offer_name = conv.get("relationship", {}).get("offer", {}).get("name")
                
                # Extract affiliate/partner name from various possible locations
                partner_name = None
                if conv.get("partner"):
                    partner_name = conv.get("partner")
                elif conv.get("affiliate"):
                    partner_name = conv.get("affiliate")
                elif conv.get("relationship", {}).get("affiliate", {}).get("name"):
                    partner_name = conv.get("relationship", {}).get("affiliate", {}).get("name")
                
                # Format date
                date_str = None
                if conv.get("date"):
                    date_str = conv.get("date")
                elif conv.get("conversion_unix_timestamp"):
                    from datetime import datetime
                    try:
                        ts = int(conv.get("conversion_unix_timestamp"))
                        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    except:
                        pass
                
                # Only include key fields for preview to reduce JSON size
                preview_conv = {
                    "conversion_id": conv.get("conversion_id"),
                    "status": conv.get("status"),
                    "date": date_str,
                    "offer": offer_name,
                    "partner": partner_name,
                    "payout": conv.get("payout")
                }
                preview_conversions.append(preview_conv)
        
        # Build the JSON data for frontend extraction
        import time
        json_start = time.time()
        # Update pagination to reflect filtered count for fraud reports
        if report_type.lower() == "fraud":
            # For fraud reports, pagination should reflect filtered count
            filtered_total = len(conversions)
            pagination_info = {
                "page": 1,  # Fraud reports are filtered client-side, so we show all on one "page"
                "page_size": filtered_total,  # All filtered results
                "total_count": filtered_total,  # Use filtered count
                "total_pages": 1  # All results shown
            }
            print(f"📊 Pagination updated for fraud report: {filtered_total} fraud conversions")
        else:
            # For regular reports, use API pagination info
            pagination_info = {
                "page": paging.get("current_page", page),
                "page_size": paging.get("page_size", page_size),
                "total_count": paging.get("total_count", total),
                "total_pages": paging.get("total_pages", 1)
            }
        
        result_data = {
            "status": "success",
            "report_type": report_type,
            "date_range": f"{from_date_str} to {to_date_str}",
            "summary": summary,
            "conversions": conversions,  # Full data for modal
            "preview_conversions": preview_conversions,  # First 10 for preview table (minimal fields)
            "pagination": pagination_info,
            "filters": filters_dict or {},
        }
        result_json = json.dumps(result_data)
        json_time = time.time() - json_start
        print(f"⏱️  JSON serialization took {json_time:.2f} seconds")
        
        # Pre-format the markdown table to avoid LLM processing delay
        # This way the agent just passes it through without formatting
        report_title = "Conversion Report for Fraud Detection" if report_type.lower() == "fraud" else "Conversion Report"
        
        markdown_response = f"""📊 **{report_title}**

**Summary:**
• Total Conversions: {summary['total']}
• Approved: {summary['approved']}
• Rejected (Manual): {summary['rejected_manual']}
• Rejected (Throttle): {summary['rejected_throttle']}
• Total Payout: €{summary['payout']:.2f}

"""
        
        # Only add table if there are conversions
        if len(preview_conversions) > 0:
            markdown_response += "| Status | Date | Offer | Partner | Payout | Conversion ID |\n"
            markdown_response += "| :----- | :--- | :---- | :------ | :----: | :------------ |\n"
            
            # Add preview rows (max 10)
            preview_count = min(len(preview_conversions), 10)
            for conv in preview_conversions[:preview_count]:
                status = conv.get("status", "unknown")
                date = conv.get("date", "N/A")
                offer = conv.get("offer", "N/A") or "N/A"
                partner = conv.get("partner", "N/A") or "N/A"
                payout = conv.get("payout", 0) or 0
                conv_id = conv.get("conversion_id", "N/A") or "N/A"
                # Truncate long IDs
                if conv_id and len(conv_id) > 20:
                    conv_id = conv_id[:20] + "..."
                
                # Format payout
                payout_str = f"€{float(payout):.2f}" if payout else "€0.00"
                
                markdown_response += f"| {status} | {date} | {offer[:30]} | {partner[:20]} | {payout_str} | {conv_id} |\n"
            
            # Add hint if there are more than 10 records
            total_count = summary['total']  # Use summary total which is already filtered for fraud
            if total_count > 10:
                markdown_response += f"\n*Showing {preview_count} of {total_count} records. Click 'View Full Report' to see all records with all columns.*\n"
        else:
            # No conversions found
            markdown_response += f"\n*No conversions found matching your criteria for the date range {from_date_str} to {to_date_str}.*\n"
        
        # Add JSON code block for frontend extraction
        markdown_response += f"\n```json\n{result_json}\n```"
        
        print(f"✅ Pre-formatted markdown response ({len(markdown_response)} chars) - agent can pass through without formatting")
        print(f"📊 Response preview (first 200 chars): {markdown_response[:200]}")
        
        # Validate response is not empty
        if not markdown_response or len(markdown_response.strip()) == 0:
            print(f"❌ ERROR: Markdown response is empty!")
            return "❌ **Error**: Failed to generate conversion report. The response was empty. Please try again."
        
        return markdown_response
        
    except Exception as e:
        import traceback
        error_details = str(e)
        traceback_str = traceback.format_exc()
        print(f"❌ Error in wf3_fetch_conversions: {error_details}")
        print(f"❌ Traceback: {traceback_str}")
        
        # Return a user-friendly error message that the agent can pass through
        error_message = f"""❌ **Error Fetching Conversion Report**

Failed to fetch conversion data: {error_details}

**Possible causes:**
- The date range might be too large
- The Everflow API might be experiencing issues
- Invalid filters or parameters

**Suggestions:**
- Try a shorter date range (e.g., "last week" instead of "last month")
- Verify the offer name, affiliate name, and source ID are correct
- Check if the Everflow API is accessible

Please try again with a different query or contact support if the issue persists."""
        
        return error_message


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
        "message": "No default LP traffic detected above threshold",
        "_format_hint": "table"  # Format as table if alerts exist
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
        "message": "No partners with significant volume drops detected",
        "_format_hint": "table"  # Format as table if alerts exist
    })


@tool
def wf6_generate_weekly_summary(
    days: int = 7,
    group_by: Literal["country", "offer"] = "country",
    country: Optional[Union[str, int]] = None
) -> str:
    """
    Generate weekly performance summary by country or offer.
    Filters by Advertiser_Internal label.
    
    Args:
        days: Number of days to analyze (default: 7)
        group_by: Group by "country" or "offer" (default: "country")
        country: Optional country code or name to filter by
    
    Returns:
        Aggregated performance data with text summary
    """
    resolver = get_resolver()
    
    # Resolve country if provided
    resolved_country = None
    if country:
        resolved_country = resolver.resolve_country(country)
        if resolved_country is None and isinstance(country, str) and len(country) > 3:
            return json.dumps({
                "status": "error",
                "message": f"Could not find country: {country}. Please provide a valid country code (e.g., US, DE) or name."
            })
        if resolved_country is None:
            resolved_country = country.upper() if isinstance(country, str) else str(country)
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
        List of LangChain tools for workflows WF1-WF6 plus utility tools
    """
    return [
        wf1_generate_tracking_link,
        wf2_identify_top_lps,
        query_top_offers,  # Utility tool for querying top offers
        wf3_export_report,
        wf3_fetch_conversions,  # For viewing conversion reports (fraud detection)
        wf4_check_default_lp_alert,
        wf5_check_paused_partners,
        wf6_generate_weekly_summary,
    ]

