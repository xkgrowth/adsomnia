"""
Everflow API Client for fetching real data.
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from .config import EVERFLOW_API_KEY, EVERFLOW_BASE_URL, EVERFLOW_TIMEZONE_ID
from .everflow_api_validator import get_validator, ValidationResult

logger = logging.getLogger(__name__)


class EverflowClient:
    """Client for interacting with Everflow API."""
    
    def __init__(self):
        self.api_key = EVERFLOW_API_KEY
        self.base_url = EVERFLOW_BASE_URL.rstrip('/')
        self.timezone_id = EVERFLOW_TIMEZONE_ID
        self.headers = {
            "X-Eflow-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _validate_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> ValidationResult:
        """
        Validate API request before making it.
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            data: Request payload
        
        Returns:
            ValidationResult
        """
        validator = get_validator()
        
        # Validate endpoint
        endpoint_result = validator.validate_endpoint(endpoint, method)
        
        if not endpoint_result.valid:
            # For GET requests to known endpoints, be more lenient (just warn, don't block)
            if method.upper() == "GET" and any(known in endpoint for known in ["/v1/networks/affiliates", "/v1/networks/offers"]):
                logger.warning(f"Endpoint validation warning (allowing anyway): {endpoint_result.errors}")
                # Return a valid result with warnings
                return ValidationResult(
                    valid=True,
                    warnings=endpoint_result.errors,
                    suggestions=endpoint_result.suggestions
                )
            logger.warning(f"Endpoint validation failed: {endpoint_result.errors}")
            return endpoint_result
        
        # Validate payload if provided
        if data:
            payload_result = validator.validate_payload(endpoint, data)
            if not payload_result.valid:
                logger.warning(f"Payload validation failed: {payload_result.errors}")
                return payload_result
            
            # Combine results
            return ValidationResult(
                valid=payload_result.valid,
                errors=endpoint_result.errors + payload_result.errors,
                warnings=endpoint_result.warnings + payload_result.warnings,
                suggestions=endpoint_result.suggestions + payload_result.suggestions
            )
        
        return endpoint_result
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make API request with validation.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: JSON body data (for POST requests)
            params: Query parameters (for GET requests)
        """
        # Validate request before making it
        validation = self._validate_request(method, endpoint, data)
        
        # For GET requests to known entity endpoints, be lenient (warn but don't block)
        is_entity_endpoint = any(ep in endpoint for ep in ["/v1/networks/affiliates", "/v1/networks/offers"])
        # For POST requests to known reporting endpoints, also be lenient
        is_reporting_endpoint = any(ep in endpoint for ep in [
            "/v1/networks/reporting/entity",
            "/v1/networks/reporting/entity/table/export",
            "/v1/networks/reporting/conversions",
            "/v1/networks/reporting/conversions/export"
        ])
        
        if not validation.valid:
            if (method.upper() == "GET" and is_entity_endpoint) or (method.upper() == "POST" and is_reporting_endpoint):
                # For known endpoints, just warn but proceed
                logger.warning(f"Endpoint validation warning (proceeding anyway): {validation.errors}")
            else:
                # For unknown endpoints, block if validation fails
                error_msg = "API Request Validation Failed:\n"
                error_msg += "\n".join(f"  - {e}" for e in validation.errors)
                if validation.suggestions:
                    error_msg += "\n\nSuggestions:\n"
                    error_msg += "\n".join(f"  - {s}" for s in validation.suggestions)
                raise ValueError(error_msg)
        
        if validation.warnings:
            for warning in validation.warnings:
                logger.warning(f"API Request Warning: {warning}")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Use longer timeout for reporting endpoints (they can take longer)
            is_reporting_endpoint = any(ep in endpoint for ep in [
                "/v1/networks/reporting/entity",
                "/v1/networks/reporting/entity/table/export",
                "/v1/networks/reporting/conversions",
                "/v1/networks/reporting/conversions/export"
            ])
            timeout_seconds = 30 if is_reporting_endpoint else 10
            
            if method.upper() == "GET":
                # For GET requests, params should be query parameters
                response = requests.get(url, headers=self.headers, params=params or data, timeout=timeout_seconds)
            else:
                # For POST requests, data should be JSON body
                response = requests.post(url, headers=self.headers, json=data, params=params, timeout=timeout_seconds)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Enhanced error handling with Context7 suggestions
            error_msg = f"API Error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                if hasattr(e.response, 'status_code'):
                    error_msg += f" (Status: {e.response.status_code})"
                if hasattr(e.response, 'text'):
                    try:
                        error_json = e.response.json()
                        error_msg += f"\nAPI Error Details: {json.dumps(error_json, indent=2)}"
                        
                        # Try to get suggestions from validator
                        validator = get_validator()
                        suggestion = validator.get_endpoint_suggestion(f"error {e.response.status_code}")
                        if suggestion:
                            error_msg += f"\n\nSuggested endpoint: {suggestion}"
                    except:
                        error_msg += f"\nAPI Response: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def get_affiliates(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get list of affiliates/partners using the correct Everflow API endpoint with full pagination.
        
        Args:
            limit: Maximum number of affiliates to return. If None, fetches ALL affiliates.
        
        Returns:
            List of affiliate dictionaries with full pagination support.
        """
        try:
            all_affiliates = []
            page = 1
            page_size = 50  # Default page size from API
            
            while True:
                # Use pagination - Everflow API supports page parameter
                params = {"page": page}
                
                response = self._request("GET", "/v1/networks/affiliates", params=params)
                data = response.get("affiliates", [])
                paging = response.get("paging", {})
                
                if not data:
                    break  # No more affiliates
                
                # Extract and format affiliates
                for aff in data:
                    aff_id = aff.get("network_affiliate_id")
                    if aff_id:
                        all_affiliates.append({
                            "affiliate_id": aff_id,
                            "affiliate_name": aff.get("name", f"Partner {aff_id}"),
                            # Include additional fields for reference
                            "account_status": aff.get("account_status"),
                            "_raw": aff  # Store full response for debugging
                        })
                        
                        # Stop if we've reached the limit
                        if limit and len(all_affiliates) >= limit:
                            break
                
                # Check if we've reached the limit
                if limit and len(all_affiliates) >= limit:
                    break
                
                # Check if there are more pages
                total_count = paging.get("total_count", 0)
                
                # If we've fetched all available affiliates, stop
                if total_count > 0 and len(all_affiliates) >= total_count:
                    break
                
                # If we got fewer than expected, we've reached the last page
                if len(data) < page_size:
                    break
                
                # Check if we've fetched enough (safety check)
                if total_count > 0:
                    remaining = total_count - len(all_affiliates)
                    if remaining <= 0:
                        break
                
                page += 1
                
                # Safety limit to prevent infinite loops
                if page > 50:
                    break
            
            # Return up to limit if specified, otherwise return all
            if limit:
                return all_affiliates[:limit]
            return all_affiliates
        except Exception as e:
            print(f"Error fetching affiliates: {str(e)}")
            return []
    
    def get_offers(self, limit: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """
        Get list of offers using the correct Everflow API endpoint with full pagination.
        
        Args:
            limit: Maximum number of offers to return. If None, fetches ALL offers.
            search_term: Optional search term to filter offers by name (client-side filtering)
        
        Returns:
            List of offer dictionaries with full pagination support.
        """
        try:
            all_offers = []
            page = 1
            page_size = 50  # Default page size from API
            
            while True:
                # Use pagination - Everflow API supports page parameter
                params = {"page": page}
                
                response = self._request("GET", "/v1/networks/offers", params=params)
                data = response.get("offers", [])
                paging = response.get("paging", {})
                
                if not data:
                    break  # No more offers
                
                # Extract and format offers
                for offer in data:
                    offer_id = offer.get("network_offer_id")
                    if offer_id:
                        offer_name = offer.get("name", f"Offer {offer_id}")
                        
                        # If search_term provided, filter by name
                        if search_term and search_term.lower() not in offer_name.lower():
                            continue
                        
                        all_offers.append({
                            "offer_id": offer_id,
                            "offer_name": offer_name,
                            # Include additional fields for reference
                            "advertiser_id": offer.get("network_advertiser_id"),
                            "destination_url": offer.get("destination_url"),
                            "_raw": offer  # Store full response for debugging
                        })
                        
                        # Stop if we've reached the limit
                        if limit and len(all_offers) >= limit:
                            break
                
                # Check if we've reached the limit
                if limit and len(all_offers) >= limit:
                    break
                
                # Check if there are more pages
                total_count = paging.get("total_count", 0)
                
                # If we've fetched all available offers, stop
                if total_count > 0 and len(all_offers) >= total_count:
                    print(f"✅ Fetched all {total_count} offers across {page} pages")
                    break
                
                # If we got fewer than expected, we've reached the last page
                if len(data) < page_size:
                    print(f"✅ Reached last page (page {page}, got {len(data)} offers)")
                    break
                
                # Check if we've fetched enough (safety check)
                # If total_count is available and we've reached it, stop
                if total_count > 0:
                    # Calculate if we need more pages
                    remaining = total_count - len(all_offers)
                    if remaining <= 0:
                        break
                
                page += 1
                
                # Safety limit to prevent infinite loops (max 50 pages = 2500 offers)
                if page > 50:
                    print(f"⚠️  Reached safety limit of 50 pages, stopping pagination")
                    break
            
            # Return up to limit if specified, otherwise return all
            if limit:
                return all_offers[:limit]
            return all_offers
        except Exception as e:
            print(f"Error fetching offers: {str(e)}")
            return []
    
    def get_landing_pages(self, offer_id: Optional[int] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Get list of landing pages (offer URLs) with full pagination support.
        
        Args:
            offer_id: Optional offer ID to filter landing pages
            limit: Maximum number of landing pages to return. If None, fetches ALL landing pages.
        
        Returns:
            List of landing page dictionaries with full pagination support.
        """
        from datetime import datetime, timedelta
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        columns = [{"column": "offer_url"}]
        filters = []
        
        if offer_id:
            filters.append({
                "resource_type": "offer",
                "filter_id_value": str(offer_id)
            })
        
        all_lps = []
        page = 1
        page_size = 100  # Default page size for entity reports
        
        try:
            while True:
                payload = {
                    "columns": columns,
                    "query": {"filters": filters},
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "timezone_id": self.timezone_id,
                    "page": page,
                    "page_size": page_size
                }
                
                response = self._request("POST", "/v1/networks/reporting/entity", payload)
                table = response.get("table", [])
                paging = response.get("paging", {})
                
                if not table:
                    break  # No more landing pages
                
                # Extract unique landing pages - use ALL fields from API response
                seen_ids = set([lp.get("offer_url_id") for lp in all_lps if lp.get("offer_url_id")])
                
                for row in table:
                    lp_id = row.get("offer_url_id")
                    if lp_id and lp_id not in seen_ids:
                        seen_ids.add(lp_id)
                        # Capture ALL landing page fields from Everflow API response
                        all_lps.append({
                            "offer_url_id": lp_id,
                            "offer_url_name": row.get("offer_url_name") or row.get("offer_url") or f"LP {lp_id}",
                            "offer_id": row.get("offer_id"),
                            "offer_url": row.get("offer_url"),  # Sometimes the name is in this field
                            # Store full row for additional context
                            "_raw": {k: v for k, v in row.items() if k.startswith("offer_url")}
                        })
                        
                        # Stop if we've reached the limit
                        if limit and len(all_lps) >= limit:
                            break
                
                # Check if we've reached the limit
                if limit and len(all_lps) >= limit:
                    break
                
                # Check if there are more pages
                total_count = paging.get("total_count", 0)
                total_pages = paging.get("total_pages", 1)
                current_page = paging.get("current_page", page)
                
                # If we've fetched all available landing pages, stop
                if total_count > 0 and len(all_lps) >= total_count:
                    break
                
                # If we've reached the last page or got fewer than expected, stop
                if current_page >= total_pages or len(table) < page_size:
                    break
                
                page += 1
            
            # Return up to limit if specified, otherwise return all
            if limit:
                return all_lps[:limit]
            return all_lps
        except Exception as e:
            print(f"Error fetching landing pages: {str(e)}")
            return []
    
    def get_countries(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get list of countries with traffic, with full pagination support.
        
        Args:
            limit: Maximum number of countries to return. If None, fetches ALL countries.
        
        Returns:
            List of country dictionaries with full pagination support.
        """
        from datetime import datetime, timedelta
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        all_countries = []
        page = 1
        page_size = 100  # Default page size for entity reports
        seen = set()
        
        try:
            while True:
                payload = {
                    "columns": [{"column": "country"}],
                    "query": {"filters": []},
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "timezone_id": self.timezone_id,
                    "page": page,
                    "page_size": page_size
                }
                
                response = self._request("POST", "/v1/networks/reporting/entity", payload)
                table = response.get("table", [])
                paging = response.get("paging", {})
                
                if not table:
                    break  # No more countries
                
                # Extract countries with ALL fields from API response
                for row in table:
                    country_code = row.get("country_code")
                    if country_code and country_code not in seen:
                        seen.add(country_code)
                        # Capture ALL country fields from Everflow API response
                        all_countries.append({
                            "code": country_code,
                            "name": row.get("country_name") or row.get("country") or country_code,
                            "country": row.get("country"),  # Sometimes the name is in this field
                            "country_name": row.get("country_name"),  # Explicit country_name field
                            # Store full row for additional context
                            "_raw": {k: v for k, v in row.items() if k.startswith("country")}
                        })
                        
                        # Stop if we've reached the limit
                        if limit and len(all_countries) >= limit:
                            break
                
                # Check if we've reached the limit
                if limit and len(all_countries) >= limit:
                    break
                
                # Check if there are more pages
                total_count = paging.get("total_count", 0)
                total_pages = paging.get("total_pages", 1)
                current_page = paging.get("current_page", page)
                
                # If we've fetched all available countries, stop
                if total_count > 0 and len(all_countries) >= total_count:
                    break
                
                # If we've reached the last page or got fewer than expected, stop
                if current_page >= total_pages or len(table) < page_size:
                    break
                
                page += 1
            
            # Return up to limit if specified, otherwise return all
            if limit:
                return all_countries[:limit]
            return all_countries
        except Exception as e:
            print(f"Error fetching countries: {str(e)}")
            return []
    
    def fetch_conversions(
        self,
        columns: List[str],
        filters: List[Dict],
        from_date: str,
        to_date: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict:
        """
        Fetch conversion data for viewing (not exporting).
        
        Uses the POST /v1/networks/reporting/conversions endpoint which returns
        JSON data with pagination support.
        
        Args:
            columns: List of column names to include (not used by this endpoint, but kept for compatibility)
            filters: List of filter dictionaries
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            page: Page number (default: 1)
            page_size: Results per page (default: 50)
        
        Returns:
            Dictionary with conversion data, summary, and pagination info
        """
        # Use the conversions endpoint (not /export)
        # According to Everflow API docs: POST /v1/networks/reporting/conversions
        # Required: from, to, timezone_id, show_conversions, show_events
        # Supports: pagination, query filters
        payload = {
            "from": from_date,
            "to": to_date,
            "timezone_id": self.timezone_id,
            "show_conversions": True,  # Return base conversions
            "show_events": False,  # Don't return post-conversion events for now
            "query": {
                "filters": filters
            },
            "page": page,
            "page_size": page_size
        }
        
        print(f"🔍 Calling Everflow API: POST /v1/networks/reporting/conversions")
        print(f"🔍 Payload: {json.dumps(payload, indent=2)}")
        print(f"⏱️  Timeout set to 30 seconds for reporting endpoint")
        try:
            response = self._request("POST", "/v1/networks/reporting/conversions", payload)
            
            # The API returns: {"conversions": [...], "paging": {...}}
            # Map to our expected format
            conversions = response.get("conversions", [])
            paging = response.get("paging", {})
            
            print(f"✅ API Response: {len(conversions)} conversions returned")
            
            return {
                "table": conversions,  # Alias for compatibility
                "conversions": conversions,
                "paging": paging
            }
        except requests.exceptions.Timeout as e:
            error_msg = f"Everflow API request timed out after 30 seconds. The query may be too large. Try a shorter date range or add more filters."
            print(f"❌ Everflow API timeout: {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            # Extract detailed error information
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_msg = f"Everflow API Error: {json.dumps(error_json, indent=2)}"
                except:
                    error_msg = f"Everflow API Error: {e.response.text if hasattr(e.response, 'text') else str(e)}"
            print(f"❌ Everflow API call failed: {error_msg}")
            raise Exception(f"Failed to fetch conversions: {error_msg}")
    
    def update_conversion_status(
        self,
        conversion_id: str,
        status: str
    ) -> Dict:
        """
        Update the status of a conversion (approve/reject).
        Uses endpoint discovery to find the correct endpoint.
        
        Args:
            conversion_id: The conversion ID
            status: New status ("approved", "rejected", "invalid", etc.)
        
        Returns:
            Success response
        """
        validator = get_validator()
        
        # Try to discover the correct endpoint
        suggestion = validator.get_endpoint_suggestion(f"update conversion {conversion_id} status {status}")
        
        # Known endpoint patterns to try
        endpoints_to_try = [
            f"/v1/networks/conversions/{conversion_id}/status",
            f"/v1/networks/conversions/{conversion_id}",
            "/v1/networks/conversions/bulk-status",
        ]
        
        if suggestion:
            endpoints_to_try.insert(0, suggestion)
        
        payload = {"status": status}
        last_error = None
        
        for endpoint in endpoints_to_try:
            try:
                # Validate endpoint first
                validation = validator.validate_endpoint(endpoint, "PUT")
                if not validation.valid:
                    # Try POST instead
                    validation = validator.validate_endpoint(endpoint, "POST")
                    method = "POST" if validation.valid else "PUT"
                else:
                    method = "PUT"
                
                response = self._request(method, endpoint, data=payload)
                logger.info(f"Successfully updated conversion {conversion_id} using {endpoint}")
                return response
            except Exception as e:
                logger.debug(f"Failed to update conversion using {endpoint}: {e}")
                last_error = e
                continue
        
        # If all endpoints failed, raise error
        raise Exception(
            f"Failed to update conversion status. Tried endpoints: {', '.join(endpoints_to_try)}. "
            f"Last error: {str(last_error)}"
        )
    
    def bulk_update_conversion_status(
        self,
        conversion_ids: List[str],
        status: str
    ) -> Dict:
        """
        Bulk update conversion statuses.
        
        Args:
            conversion_ids: List of conversion IDs
            status: New status ("approved", "rejected", "invalid", etc.)
        
        Returns:
            Success response with count of updated conversions
        """
        try:
            endpoint = "/v1/networks/conversions/bulk-status"
            payload = {
                "conversion_ids": conversion_ids,
                "status": status
            }
            response = self._request("POST", endpoint, data=payload)
            return response
        except Exception as e:
            raise Exception(f"Failed to bulk update conversion statuses: {str(e)}")


def fetch_real_data() -> Dict[str, Any]:
    """Fetch real data from Everflow API for testing."""
    print("=" * 60)
    print("Fetching Real Data from Everflow API")
    print("=" * 60)
    
    client = EverflowClient()
    
    data = {
        "affiliates": [],
        "offers": [],
        "landing_pages": [],
        "countries": []
    }
    
    print("\n📊 Fetching affiliates...")
    data["affiliates"] = client.get_affiliates(limit=5)
    print(f"   ✅ Found {len(data['affiliates'])} affiliates")
    if data["affiliates"]:
        for aff in data["affiliates"][:3]:
            print(f"      - Partner {aff['affiliate_id']}: {aff['affiliate_name']}")
    
    print("\n📊 Fetching offers...")
    data["offers"] = client.get_offers(limit=5)
    print(f"   ✅ Found {len(data['offers'])} offers")
    if data["offers"]:
        for offer in data["offers"][:3]:
            print(f"      - Offer {offer['offer_id']}: {offer['offer_name']}")
    
    print("\n📊 Fetching landing pages...")
    if data["offers"]:
        # Get LPs for first offer
        first_offer_id = data["offers"][0]["offer_id"]
        data["landing_pages"] = client.get_landing_pages(offer_id=first_offer_id, limit=5)
        print(f"   ✅ Found {len(data['landing_pages'])} landing pages for Offer {first_offer_id}")
        if data["landing_pages"]:
            for lp in data["landing_pages"][:3]:
                print(f"      - LP {lp['offer_url_id']}: {lp['offer_url_name']}")
    
    print("\n📊 Fetching countries...")
    data["countries"] = client.get_countries()
    print(f"   ✅ Found {len(data['countries'])} countries")
    if data["countries"]:
        print(f"      - {', '.join(data['countries'][:10])}")
    
    print("\n" + "=" * 60)
    print("✅ Data fetch complete!")
    print("=" * 60)
    
    return data


if __name__ == "__main__":
    data = fetch_real_data()
    print("\n📋 Summary:")
    print(f"   Affiliates: {len(data['affiliates'])}")
    print(f"   Offers: {len(data['offers'])}")
    print(f"   Landing Pages: {len(data['landing_pages'])}")
    print(f"   Countries: {len(data['countries'])}")

