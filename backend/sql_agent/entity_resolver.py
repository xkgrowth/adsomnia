"""
Entity Name-to-ID Resolution System
Resolves entity names (offers, affiliates, countries) to their IDs for API calls.
"""
from typing import Optional, Union, Dict, List, Tuple
from difflib import SequenceMatcher
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
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings using SequenceMatcher.
        Returns a value between 0.0 (no similarity) and 1.0 (identical).
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _find_similar_entities(
        self, 
        search_term: str, 
        entities: List[Dict], 
        name_fields: List[str],
        min_similarity: float = 0.6,
        max_results: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Find entities with similar names using fuzzy matching.
        
        Args:
            search_term: The search term to match against
            entities: List of entity dictionaries
            name_fields: List of field names to check (e.g., ["affiliate_name", "affiliate"])
            min_similarity: Minimum similarity ratio (0.0-1.0) to include
            max_results: Maximum number of results to return
        
        Returns:
            List of tuples (entity_dict, similarity_score) sorted by similarity (highest first)
        """
        search_lower = search_term.lower().strip()
        matches = []
        
        for entity in entities:
            # Check all possible name fields
            for field in name_fields:
                name = entity.get(field, "")
                if not name:
                    continue
                
                name_lower = str(name).lower().strip()
                
                # Calculate similarity
                similarity = self._calculate_similarity(search_lower, name_lower)
                
                if similarity >= min_similarity:
                    matches.append((entity, similarity))
                    break  # Only add once per entity
        
        # Sort by similarity (highest first) and return top results
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:max_results]
    
    def resolve_affiliate(self, value: Union[int, str], return_suggestions: bool = False) -> Union[Optional[int], Tuple[Optional[int], List[Dict]]]:
        """
        Resolve affiliate ID from either ID or name.
        Uses affiliate_name from Everflow API response.
        
        Args:
            value: Affiliate ID (int) or name (str)
            return_suggestions: If True, returns tuple (id, suggestions) even when match is found
        
        Returns:
            Affiliate ID or None if not found
            If return_suggestions=True, returns (id, suggestions_list)
        """
        # If already an ID, return it
        if isinstance(value, int):
            if return_suggestions:
                return value, []
            return value
        
        # Normalize input name
        search_name = str(value).strip().lower()
        
        # Check cache first
        if search_name in self._affiliate_cache:
            if return_suggestions:
                return self._affiliate_cache[search_name], []
            return self._affiliate_cache[search_name]
        
        # Try test data first (for testing)
        test_aff = get_affiliate_by_name(value)
        if test_aff:
            self._affiliate_cache[search_name] = test_aff["id"]
            if return_suggestions:
                return test_aff["id"], []
            return test_aff["id"]
        
        # Try to fetch from API - use ALL affiliate fields from response
        try:
            # Fetch ALL affiliates (no limit) to ensure we find the one we're looking for
            affiliates = self.client.get_affiliates(limit=None)
            best_match = None
            best_similarity = 0.0
            
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
                        self._affiliate_cache[search_name] = aff_id
                        if return_suggestions:
                            return aff_id, []
                        return aff_id
                    
                    # Partial match (name contains search term or vice versa)
                    if search_name in name_lower or name_lower in search_name:
                        # Check for duplicate names
                        if search_name in self._affiliate_cache and self._affiliate_cache[search_name] != aff_id:
                            print(f"⚠️  WARNING: Duplicate affiliate name '{value}' found! IDs: {self._affiliate_cache[search_name]}, {aff_id}")
                        self._affiliate_cache[search_name] = aff_id
                        if return_suggestions:
                            return aff_id, []
                        return aff_id
                    
                    # Calculate similarity for fuzzy matching
                    similarity = self._calculate_similarity(search_name, name_lower)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = aff
            
            # If we found a good fuzzy match (similarity >= 0.85), use it
            if best_match and best_similarity >= 0.85:
                aff_id = best_match.get("affiliate_id")
                self._affiliate_cache[search_name] = aff_id
                if return_suggestions:
                    return aff_id, []
                return aff_id
            
            # If no good match found, get suggestions for error message
            if return_suggestions or best_similarity < 0.85:
                suggestions = self._find_similar_entities(
                    search_name,
                    affiliates,
                    ["affiliate_name", "affiliate"],
                    min_similarity=0.5,
                    max_results=5
                )
                suggestions_list = [
                    {
                        "affiliate_id": aff.get("affiliate_id"),
                        "affiliate_name": aff.get("affiliate_name", aff.get("affiliate", "")),
                        "similarity": round(sim * 100, 1)  # Convert to percentage
                    }
                    for aff, sim in suggestions
                ]
                if return_suggestions:
                    return None, suggestions_list
                return None
                
        except Exception as e:
            print(f"API lookup failed for affiliate '{value}': {str(e)}")
            pass  # Fall back to test data
        
        if return_suggestions:
            return None, []
        return None
    
    def resolve_offer(self, value: Union[int, str], return_suggestions: bool = False) -> Union[Optional[int], Tuple[Optional[int], List[Dict]]]:
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
            if return_suggestions:
                return self._offer_cache[search_name], []
            return self._offer_cache[search_name]
        
        # Try test data first (for testing)
        test_offer = get_offer_by_name(value)
        if test_offer:
            self._offer_cache[search_name] = test_offer["id"]
            if return_suggestions:
                return test_offer["id"], []
            return test_offer["id"]
        
        # Try to fetch from API - use ALL offer fields from response
        # Note: Everflow API returns offer_name, advertiser_name, offer fields
        try:
            # Fetch ALL offers (no limit) to ensure we find the one we're looking for
            offers = self.client.get_offers(limit=None)
            print(f"🔍 Searching for offer: '{value}' (normalized: '{search_name}') in {len(offers)} offers")
            
            best_match = None
            best_similarity = 0.0
            
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
                        self._offer_cache[search_name] = offer_id
                        if return_suggestions:
                            return offer_id, []
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
                        if return_suggestions:
                            return offer_id, []
                        return offer_id
                    
                    # Partial match (search name in offer name) - check if key words match
                    if search_normalized in name_normalized:
                        print(f"✅ Partial match (search in name) found: Offer ID {offer_id} = '{name}'")
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                        self._offer_cache[search_name] = offer_id
                        if return_suggestions:
                            return offer_id, []
                        return offer_id
                    
                    # Partial match (offer name in search name)
                    if name_normalized in search_normalized:
                        print(f"✅ Partial match (name in search) found: Offer ID {offer_id} = '{name}'")
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                        self._offer_cache[search_name] = offer_id
                        if return_suggestions:
                            return offer_id, []
                        return offer_id
                    
                    # Word-based matching: if all significant words in search_name appear in name
                    search_words = [w for w in search_normalized.split() if len(w) > 2]  # Ignore short words like "it", "do", etc.
                    if search_words and all(word in name_normalized for word in search_words):
                        print(f"✅ Word-based match found: Offer ID {offer_id} = '{name}' (all words: {search_words})")
                        if search_name in self._offer_cache and self._offer_cache[search_name] != offer_id:
                            print(f"⚠️  WARNING: Duplicate offer name '{value}' found! IDs: {self._offer_cache[search_name]}, {offer_id}")
                        self._offer_cache[search_name] = offer_id
                        if return_suggestions:
                            return offer_id, []
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
                            if return_suggestions:
                                return offer_id, []
                            return offer_id
                    
                    # Calculate similarity for fuzzy matching (typo tolerance)
                    similarity = self._calculate_similarity(search_normalized, name_normalized)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = offer
            
            # Debug: Print what we found
            if best_match:
                print(f"🔍 Best match found: Offer ID {best_match.get('offer_id')} = '{best_match.get('offer_name', '')}' (similarity: {best_similarity:.2%})")
            else:
                print(f"🔍 No best match found (best_similarity: {best_similarity:.2%})")
            
            # If we found a good fuzzy match (similarity >= 0.85), use it automatically
            # Also auto-use perfect matches (100% similarity) even if return_suggestions=True
            if best_match and best_similarity >= 0.85:
                offer_id = best_match.get("offer_id")
                print(f"✅ Fuzzy match found: Offer ID {offer_id} = '{best_match.get('offer_name', '')}' (similarity: {best_similarity:.2%})")
                self._offer_cache[search_name] = offer_id
                # Always return the ID for matches >= 85%, even if return_suggestions=True
                # The caller can still get suggestions if needed, but we prioritize the match
                if return_suggestions:
                    # Return the ID and empty suggestions since we found a match
                    return offer_id, []
                return offer_id
            
            # If no good match found, get suggestions for error message
            # But first, check if suggestions contain a perfect match that we should auto-use
            if return_suggestions or best_similarity < 0.85:
                suggestions = self._find_similar_entities(
                    search_name,
                    offers,
                    ["offer_name", "advertiser_name", "advertiser", "offer"],
                    min_similarity=0.5,
                    max_results=5
                )
                suggestions_list = [
                    {
                        "offer_id": offer.get("offer_id"),
                        "offer_name": offer.get("offer_name", offer.get("advertiser_name", "")),
                        "similarity": round(sim * 100, 1)  # Convert to percentage
                    }
                    for offer, sim in suggestions
                ]
                
                # Check if suggestions contain a perfect match (100% similarity) that we should auto-use
                perfect_match = next((s for s in suggestions_list if s.get("similarity", 0) >= 100.0), None)
                if perfect_match:
                    offer_id = perfect_match.get("offer_id")
                    print(f"✅ Perfect match found in suggestions: Offer ID {offer_id} = '{perfect_match.get('offer_name')}' (100% match)")
                    self._offer_cache[search_name] = offer_id
                    if return_suggestions:
                        return offer_id, []
                    return offer_id
                
                if return_suggestions:
                    return None, suggestions_list
                return None
                
        except Exception as e:
            print(f"API lookup failed for offer '{value}': {str(e)}")
            pass  # Fall back to test data
        
        if return_suggestions:
            return None, []
        return None
    
    def resolve_country(self, value: Union[str, int], return_suggestions: bool = False) -> Union[Optional[str], Tuple[Optional[str], List[Dict]]]:
        """
        Resolve country code from either code or name.
        
        Args:
            value: Country code (str) or name (str)
            return_suggestions: If True, returns tuple (code, suggestions) even when match is found
        
        Returns:
            Country code (e.g., "US") or None if not found
            If return_suggestions=True, returns (code, suggestions_list)
        """
        # If already a code (2-3 letters), return it
        if isinstance(value, str) and len(value) <= 3 and value.isupper():
            if return_suggestions:
                return value.upper(), []
            return value.upper()
        
        # Normalize input
        search_term = str(value).strip().lower()
        
        # Check cache first
        if search_term in self._country_cache:
            if return_suggestions:
                return self._country_cache[search_term], []
            return self._country_cache[search_term]
        
        # Try test data first
        country = get_country_by_name(value)
        if country:
            code = country["code"]
            self._country_cache[search_term] = code
            if return_suggestions:
                return code, []
            return code
        
        # Also try by code (case-insensitive)
        country = get_country_by_code(value)
        if country:
            code = country["code"]
            self._country_cache[search_term] = code
            if return_suggestions:
                return code, []
            return code
        
        # Try to fetch from API - use ALL country fields from response
        try:
            countries = self.client.get_countries()
            best_match = None
            best_similarity = 0.0
            countries_list = []
            
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
                    countries_list.append({
                        "code": country_code,
                        "name": country_data.get("country_name") or country_data.get("name") or country_data.get("country", ""),
                        "possible_names": possible_names
                    })
                else:
                    # If it's just a string code, use it directly
                    country_code = country_data
                    possible_names = []
                    countries_list.append({
                        "code": country_code,
                        "name": str(country_code),
                        "possible_names": []
                    })
                
                if not country_code:
                    continue
                
                # Check if input matches code
                if str(value).upper() == str(country_code).upper():
                    self._country_cache[search_term] = country_code
                    if return_suggestions:
                        return country_code, []
                    return country_code
                
                # Check all name fields
                for name in possible_names:
                    if not name:
                        continue
                    name_lower = str(name).strip().lower()
                    search_lower = str(value).strip().lower()
                    
                    # Exact match
                    if name_lower == search_lower:
                        self._country_cache[search_term] = country_code
                        if return_suggestions:
                            return country_code, []
                        return country_code
                    
                    # Partial match
                    if search_lower in name_lower or name_lower in search_lower:
                        self._country_cache[search_term] = country_code
                        if return_suggestions:
                            return country_code, []
                        return country_code
                    
                    # Calculate similarity for fuzzy matching
                    similarity = self._calculate_similarity(search_lower, name_lower)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = country_data if isinstance(country_data, dict) else {"code": country_code, "name": str(country_code)}
            
            # If we found a good fuzzy match (similarity >= 0.85), use it automatically
            if best_match and best_similarity >= 0.85:
                country_code = best_match.get("code") if isinstance(best_match, dict) else best_match
                print(f"✅ Fuzzy match found: Country code {country_code} (similarity: {best_similarity:.2%})")
                self._country_cache[search_term] = country_code
                if return_suggestions:
                    return country_code, []
                return country_code
            
            # If no good match found, get suggestions for error message
            if return_suggestions or best_similarity < 0.85:
                # Build suggestions list manually since countries have different structure
                suggestions_list = []
                for country_item in countries_list:
                    country_code = country_item.get("code")
                    country_name = country_item.get("name", "")
                    if not country_code:
                        continue
                    
                    # Calculate similarity with all possible names
                    max_sim = 0.0
                    for name in [country_name] + country_item.get("possible_names", []):
                        if not name:
                            continue
                        sim = self._calculate_similarity(search_term, str(name).lower())
                        max_sim = max(max_sim, sim)
                    
                    if max_sim >= 0.5:  # Only include if similarity is reasonable
                        suggestions_list.append({
                            "country_code": country_code,
                            "country_name": country_name,
                            "similarity": round(max_sim * 100, 1)
                        })
                
                # Sort by similarity and take top 5
                suggestions_list.sort(key=lambda x: x["similarity"], reverse=True)
                suggestions_list = suggestions_list[:5]
                
                if return_suggestions:
                    return None, suggestions_list
                return None
                
        except Exception as e:
            print(f"API lookup failed for country '{value}': {str(e)}")
            pass  # Fall back to test data
        
        if return_suggestions:
            return None, []
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
    
    def resolve_filters(self, filters: Dict[str, any]) -> Dict[str, any]:
        """
        Resolve all entity names in a filters dictionary to IDs.
        This is workflow-agnostic and can be used by any workflow tool.
        
        Args:
            filters: Dictionary with filter keys (may contain offer_name, affiliate_name, etc.)
        
        Returns:
            Dictionary with resolved IDs (offer_name -> offer_id, affiliate_name -> affiliate_id, etc.)
        
        Raises:
            ValueError: If entities cannot be resolved, includes suggestions in error message
        
        Example:
            Input:  {"offer_name": "Papoaolado - BR - DOI", "affiliate_name": "iMonetizeIt", "source_id": 134505}
            Output: {"offer_id": 292, "affiliate_id": 1009, "source_id": 134505}
        """
        resolved = filters.copy()
        errors = []
        
        # Resolve offer_name -> offer_id
        if "offer_name" in resolved:
            offer_name = resolved["offer_name"]
            offer_id, suggestions = self.resolve_offer(offer_name, return_suggestions=True)
            if offer_id:
                resolved["offer_id"] = offer_id
                del resolved["offer_name"]
            else:
                error_msg = f"Could not find offer: {offer_name}"
                if suggestions:
                    error_msg += "\n\nDid you mean one of these?"
                    for sug in suggestions[:5]:
                        error_msg += f"\n- {sug['offer_name']} (ID: {sug['offer_id']}, {sug['similarity']}% match)"
                errors.append(error_msg)
        
        # Resolve affiliate_name -> affiliate_id
        if "affiliate_name" in resolved:
            affiliate_name = resolved["affiliate_name"]
            affiliate_id, suggestions = self.resolve_affiliate(affiliate_name, return_suggestions=True)
            if affiliate_id:
                resolved["affiliate_id"] = affiliate_id
                del resolved["affiliate_name"]
            else:
                error_msg = f"Could not find affiliate: {affiliate_name}"
                if suggestions:
                    error_msg += "\n\nDid you mean one of these?"
                    for sug in suggestions[:5]:
                        error_msg += f"\n- {sug['affiliate_name']} (ID: {sug['affiliate_id']}, {sug['similarity']}% match)"
                errors.append(error_msg)
        
        # Resolve country_name or country -> country_code
        if "country_name" in resolved:
            country_name = resolved["country_name"]
            country_code, suggestions = self.resolve_country(country_name, return_suggestions=True)
            if country_code:
                resolved["country_code"] = country_code
                del resolved["country_name"]
            else:
                error_msg = f"Could not find country: {country_name}"
                if suggestions:
                    error_msg += "\n\nDid you mean one of these?"
                    for sug in suggestions[:5]:
                        error_msg += f"\n- {sug['country_name']} ({sug['country_code']}, {sug['similarity']}% match)"
                errors.append(error_msg)
        elif "country" in resolved and "country_code" not in resolved:
            country = resolved["country"]
            country_code, suggestions = self.resolve_country(country, return_suggestions=True)
            if country_code:
                resolved["country_code"] = country_code
                del resolved["country"]
            elif suggestions:
                # Only error if we have suggestions (meaning it was a name, not a code)
                error_msg = f"Could not find country: {country}"
                error_msg += "\n\nDid you mean one of these?"
                for sug in suggestions[:5]:
                    error_msg += f"\n- {sug['country_name']} ({sug['country_code']}, {sug['similarity']}% match)"
                errors.append(error_msg)
            # Don't error if no suggestions - it might already be a code
        
        # If there were errors, raise an exception with all errors and suggestions
        if errors:
            raise ValueError("\n\n".join(errors))
        
        return resolved


# Global resolver instance
_resolver = None

def get_resolver() -> EntityResolver:
    """Get or create global entity resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = EntityResolver()
    return _resolver

