"""
Entity Name-to-ID Resolution System
Resolves entity names (offers, affiliates, countries) to their IDs for API calls.
"""
from typing import Optional, Union, Dict, List
from .test_data_reference import (
    AFFILIATES, OFFERS, COUNTRIES,
    get_affiliate_by_name, get_offer_by_name, get_country_by_name, get_country_by_code
)
from .everflow_client import EverflowClient


class EntityResolver:
    """Resolves entity names to IDs for API calls."""
    
    def __init__(self):
        self.client = EverflowClient()
        self._affiliate_cache: Dict[str, int] = {}
        self._offer_cache: Dict[str, int] = {}
        self._country_cache: Dict[str, str] = {}
    
    def resolve_affiliate(self, value: Union[int, str]) -> Optional[int]:
        """
        Resolve affiliate ID from either ID or name.
        Uses affiliate_name from Everflow API response.
        
        Args:
            value: Affiliate ID (int) or name (str)
        
        Returns:
            Affiliate ID or None if not found
        """
        # If already an ID, return it
        if isinstance(value, int):
            return value
        
        # Normalize input name
        search_name = str(value).strip().lower()
        
        # Check cache first
        if search_name in self._affiliate_cache:
            return self._affiliate_cache[search_name]
        
        # Try test data first (for testing)
        test_aff = get_affiliate_by_name(value)
        if test_aff:
            self._affiliate_cache[search_name] = test_aff["id"]
            return test_aff["id"]
        
        # Try to fetch from API - use ALL affiliate fields from response
        try:
            # Fetch ALL affiliates (no limit) to ensure we find the one we're looking for
            affiliates = self.client.get_affiliates(limit=None)
            for aff in affiliates:
                aff_id = aff.get("affiliate_id")
                if not aff_id:
                    continue
                
                # Check ALL possible name fields from Everflow API
                possible_names = [
                    aff.get("affiliate_name", ""),
                    aff.get("affiliate", ""),
                    # Check raw data if available
                    aff.get("_raw", {}).get("affiliate_name", ""),
                    aff.get("_raw", {}).get("affiliate", ""),
                ]
                
                # Try exact and partial matches on all name fields
                for name in possible_names:
                    if not name:
                        continue
                    name_lower = str(name).strip().lower()
                    
                    # Exact match
                    if name_lower == search_name:
                        # Check for duplicate names (many-to-one issue)
                        if search_name in self._affiliate_cache and self._affiliate_cache[search_name] != aff_id:
                            print(f"⚠️  WARNING: Duplicate affiliate name '{value}' found! IDs: {self._affiliate_cache[search_name]}, {aff_id}")
                            # Return first match (current behavior)
                        self._affiliate_cache[search_name] = aff_id
                        return aff_id
                    
                    # Partial match (name contains search term or vice versa)
                    if search_name in name_lower or name_lower in search_name:
                        # Check for duplicate names
                        if search_name in self._affiliate_cache and self._affiliate_cache[search_name] != aff_id:
                            print(f"⚠️  WARNING: Duplicate affiliate name '{value}' found! IDs: {self._affiliate_cache[search_name]}, {aff_id}")
                        self._affiliate_cache[search_name] = aff_id
                        return aff_id
        except Exception as e:
            print(f"API lookup failed for affiliate '{value}': {str(e)}")
            pass  # Fall back to test data
        
        return None
    
    def resolve_offer(self, value: Union[int, str]) -> Optional[int]:
        """
        Resolve offer ID from either ID or name.
        Uses offer_name (advertiser_name) from Everflow API response.
        
        Args:
            value: Offer ID (int) or name (str)
        
        Returns:
            Offer ID or None if not found
        """
        # If already an ID, return it
        if isinstance(value, int):
            return value
        
        # Normalize input name
        search_name = str(value).strip().lower()
        
        # Helper function to normalize brackets/parentheses and special chars for matching
        def normalize_for_matching(text: str) -> str:
            """Normalize text by replacing brackets/parentheses and removing extra spaces."""
            # Replace brackets and parentheses with a standard character for matching
            text = text.replace('[', '(').replace(']', ')')
            # Remove extra spaces
            return ' '.join(text.split())
        
        # Check cache first
        if search_name in self._offer_cache:
            return self._offer_cache[search_name]
        
        # Try test data first (for testing)
        test_offer = get_offer_by_name(value)
        if test_offer:
            self._offer_cache[search_name] = test_offer["id"]
            return test_offer["id"]
        
        # Try to fetch from API - use ALL offer fields from response
        # Note: Everflow API returns offer_name, advertiser_name, offer fields
        try:
            # Fetch ALL offers (no limit) to ensure we find the one we're looking for
            offers = self.client.get_offers(limit=None)
            print(f"🔍 Searching for offer: '{value}' (normalized: '{search_name}') in {len(offers)} offers")
            
            for offer in offers:
                offer_id = offer.get("offer_id")
                if not offer_id:
                    continue
                
                # Check ALL possible name fields from Everflow API
                # Priority: offer_name > advertiser_name > advertiser > offer
                possible_names = [
                    offer.get("offer_name", ""),
                    offer.get("advertiser_name", ""),  # Explicit advertiser_name field
                    offer.get("advertiser", ""),
                    offer.get("offer", ""),
                    # Check raw data if available
                    offer.get("_raw", {}).get("name", ""),  # API returns "name" in raw data
                    offer.get("_raw", {}).get("offer_name", ""),
                    offer.get("_raw", {}).get("advertiser_name", ""),
                    offer.get("_raw", {}).get("advertiser", ""),
                    offer.get("_raw", {}).get("offer", ""),
                ]
                
                # Try exact and partial matches on all name fields
                for name in possible_names:
                    if not name:
                        continue
                    name_lower = str(name).strip().lower()
                    
                    # Exact match
                    if name_lower == search_name:
                        print(f"✅ Exact match found: Offer ID {offer_id} = '{name}'")
                        # Check for duplicate names (many-to-one issue)
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                            # Return first match (current behavior)
                        self._offer_cache[search_name] = offer_id
                        return offer_id
                    
                    # Normalize both for better matching (normalize brackets/parentheses, remove extra spaces)
                    search_normalized = normalize_for_matching(search_name)
                    name_normalized = normalize_for_matching(name_lower)
                    
                    # Exact match after normalization
                    if search_normalized == name_normalized:
                        print(f"✅ Normalized match found: Offer ID {offer_id} = '{name}' (normalized: '{name_normalized}')")
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                        self._offer_cache[search_name] = offer_id
                        return offer_id
                    
                    # Partial match (search name in offer name) - check if key words match
                    if search_normalized in name_normalized:
                        print(f"✅ Partial match (search in name) found: Offer ID {offer_id} = '{name}'")
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                        self._offer_cache[search_name] = offer_id
                        return offer_id
                    
                    # Partial match (offer name in search name)
                    if name_normalized in search_normalized:
                        print(f"✅ Partial match (name in search) found: Offer ID {offer_id} = '{name}'")
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                        self._offer_cache[search_name] = offer_id
                        return offer_id
                    
                    # Word-based matching: if all significant words in search_name appear in name
                    search_words = [w for w in search_normalized.split() if len(w) > 2]  # Ignore short words like "it", "do", etc.
                    if search_words and all(word in name_normalized for word in search_words):
                        print(f"✅ Word-based match found: Offer ID {offer_id} = '{name}' (all words: {search_words})")
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                        self._offer_cache[search_name] = offer_id
                        return offer_id
                    
                    # First word matching: if the first significant word matches (e.g., "Matchaora" matches "Matchaora - IT - DOI")
                    if search_words:
                        first_word = search_words[0]
                        name_words = [w for w in name_normalized.split() if len(w) > 2]
                        if name_words and first_word == name_words[0]:
                            # First word matches, this is likely the same offer
                            print(f"✅ First word match found: Offer ID {offer_id} = '{name}' (first word: '{first_word}')")
                            if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                                print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                            self._offer_cache[search_name] = offer_id
                            return offer_id
        except Exception as e:
            print(f"API lookup failed for offer '{value}': {str(e)}")
            pass  # Fall back to test data
        
        return None
    
    def resolve_country(self, value: Union[str, int]) -> Optional[str]:
        """
        Resolve country code from either code or name.
        
        Args:
            value: Country code (str) or name (str)
        
        Returns:
            Country code (e.g., "US") or None if not found
        """
        # If already a code (2-3 letters), return it
        if isinstance(value, str) and len(value) <= 3 and value.isupper():
            return value.upper()
        
        # Check cache first
        if value in self._country_cache:
            return self._country_cache[value]
        
        # Try test data first
        country = get_country_by_name(value)
        if country:
            code = country["code"]
            self._country_cache[value] = code
            return code
        
        # Also try by code (case-insensitive)
        country = get_country_by_code(value)
        if country:
            code = country["code"]
            self._country_cache[value] = code
            return code
        
        # Try to fetch from API - use ALL country fields from response
        try:
            countries = self.client.get_countries()
            for country_data in countries:
                # Handle both dict and string formats
                if isinstance(country_data, dict):
                    country_code = country_data.get("code")
                    # Check ALL possible name fields from Everflow API
                    possible_names = [
                        country_data.get("name", ""),
                        country_data.get("country_name", ""),
                        country_data.get("country", ""),
                        country_data.get("_raw", {}).get("country_name", ""),
                        country_data.get("_raw", {}).get("country", ""),
                    ]
                else:
                    # If it's just a string code, use it directly
                    country_code = country_data
                    possible_names = []
                
                if not country_code:
                    continue
                
                # Check if input matches code
                if str(value).upper() == str(country_code).upper():
                    self._country_cache[value] = country_code
                    return country_code
                
                # Check all name fields
                for name in possible_names:
                    if not name:
                        continue
                    name_lower = str(name).strip().lower()
                    search_lower = str(value).strip().lower()
                    
                    # Exact match
                    if name_lower == search_lower:
                        self._country_cache[value] = country_code
                        return country_code
                    
                    # Partial match
                    if search_lower in name_lower or name_lower in search_lower:
                        self._country_cache[value] = country_code
                        return country_code
        except Exception as e:
            print(f"API lookup failed for country '{value}': {str(e)}")
            pass  # Fall back to test data
        
        return None
    
    def resolve_entities(self, **kwargs) -> Dict[str, Union[int, str, None]]:
        """
        Resolve multiple entities at once.
        
        Args:
            **kwargs: Entity values to resolve (affiliate_id, offer_id, country_code, etc.)
        
        Returns:
            Dict with resolved IDs/codes
        """
        resolved = {}
        
        # Resolve affiliate
        if "affiliate_id" in kwargs:
            resolved["affiliate_id"] = self.resolve_affiliate(kwargs["affiliate_id"])
        elif "affiliate_name" in kwargs:
            resolved["affiliate_id"] = self.resolve_affiliate(kwargs["affiliate_name"])
        
        # Resolve offer
        if "offer_id" in kwargs:
            resolved["offer_id"] = self.resolve_offer(kwargs["offer_id"])
        elif "offer_name" in kwargs:
            resolved["offer_id"] = self.resolve_offer(kwargs["offer_name"])
        
        # Resolve country
        if "country_code" in kwargs:
            resolved["country_code"] = self.resolve_country(kwargs["country_code"])
        elif "country" in kwargs:
            resolved["country_code"] = self.resolve_country(kwargs["country"])
        elif "country_name" in kwargs:
            resolved["country_code"] = self.resolve_country(kwargs["country_name"])
        
        return resolved


# Global resolver instance
_resolver = None

def get_resolver() -> EntityResolver:
    """Get or create global entity resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = EntityResolver()
    return _resolver

