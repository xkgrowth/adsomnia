"""
Everflow API Client for fetching real data.
"""
import os
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from .config import EVERFLOW_API_KEY, EVERFLOW_BASE_URL, EVERFLOW_TIMEZONE_ID


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
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                # For GET requests, data should be query parameters
                response = requests.get(url, headers=self.headers, params=data, timeout=10)
            else:
                # For POST requests, data should be JSON body
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    def get_affiliates(self, limit: int = 10) -> List[Dict]:
        """Get list of affiliates/partners using the correct Everflow API endpoint."""
        try:
            # Use the correct endpoint: GET /v1/networks/affiliates
            response = self._request("GET", "/v1/networks/affiliates")
            data = response.get("affiliates", [])
            
            # Extract and format affiliates
            affiliates = []
            for aff in data[:limit]:
                aff_id = aff.get("network_affiliate_id")
                if aff_id:
                    affiliates.append({
                        "affiliate_id": aff_id,
                        "affiliate_name": aff.get("name", f"Partner {aff_id}"),
                        # Include additional fields for reference
                        "account_status": aff.get("account_status"),
                        "_raw": aff  # Store full response for debugging
                    })
            
            return affiliates
        except Exception as e:
            print(f"Error fetching affiliates: {str(e)}")
            return []
    
    def get_offers(self, limit: int = 10) -> List[Dict]:
        """Get list of offers using the correct Everflow API endpoint."""
        try:
            # Use the correct endpoint: GET /v1/networks/offers
            response = self._request("GET", "/v1/networks/offers")
            data = response.get("offers", [])
            
            # Extract and format offers
            offers = []
            for offer in data[:limit]:
                offer_id = offer.get("network_offer_id")
                if offer_id:
                    offers.append({
                        "offer_id": offer_id,
                        "offer_name": offer.get("name", f"Offer {offer_id}"),
                        # Include additional fields for reference
                        "advertiser_id": offer.get("network_advertiser_id"),
                        "destination_url": offer.get("destination_url"),
                        "_raw": offer  # Store full response for debugging
                    })
            
            return offers
        except Exception as e:
            print(f"Error fetching offers: {str(e)}")
            return []
    
    def get_landing_pages(self, offer_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Get list of landing pages (offer URLs)."""
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
        
        payload = {
            "columns": columns,
            "query": {"filters": filters},
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "timezone_id": self.timezone_id
        }
        
        try:
            response = self._request("POST", "/v1/networks/reporting/entity", payload)
            table = response.get("table", [])
            
            # Extract unique landing pages - use ALL fields from API response
            lps = []
            seen_ids = set()
            for row in table:
                lp_id = row.get("offer_url_id")
                if lp_id and lp_id not in seen_ids:
                    seen_ids.add(lp_id)
                    # Capture ALL landing page fields from Everflow API response
                    lps.append({
                        "offer_url_id": lp_id,
                        "offer_url_name": row.get("offer_url_name") or row.get("offer_url") or f"LP {lp_id}",
                        "offer_id": row.get("offer_id"),
                        "offer_url": row.get("offer_url"),  # Sometimes the name is in this field
                        # Store full row for additional context
                        "_raw": {k: v for k, v in row.items() if k.startswith("offer_url")}
                    })
                    if len(lps) >= limit:
                        break
            
            return lps
        except Exception as e:
            print(f"Error fetching landing pages: {str(e)}")
            return []
    
    def get_countries(self) -> List[str]:
        """Get list of countries with traffic."""
        from datetime import datetime, timedelta
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        payload = {
            "columns": [{"column": "country"}],
            "query": {"filters": []},
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "timezone_id": self.timezone_id
        }
        
        try:
            response = self._request("POST", "/v1/networks/reporting/entity", payload)
            table = response.get("table", [])
            
            # Extract countries with ALL fields from API response
            countries = []
            seen = set()
            for row in table:
                country_code = row.get("country_code")
                if country_code and country_code not in seen:
                    seen.add(country_code)
                    # Capture ALL country fields from Everflow API response
                    countries.append({
                        "code": country_code,
                        "name": row.get("country_name") or row.get("country") or country_code,
                        "country": row.get("country"),  # Sometimes the name is in this field
                        "country_name": row.get("country_name"),  # Explicit country_name field
                        # Store full row for additional context
                        "_raw": {k: v for k, v in row.items() if k.startswith("country")}
                    })
            
            # Return as list of dicts with all fields
            return countries
        except Exception as e:
            print(f"Error fetching countries: {str(e)}")
            return []


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

