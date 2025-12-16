"""
Test Data Reference - IDs and Names Mapping
Quick reference for all test data used in QA tests.
"""
from typing import Dict, List

# Affiliates/Partners
AFFILIATES = [
    {"id": 12345, "name": "Premium Traffic Partners"},
    {"id": 23456, "name": "Global Media Network"},
    {"id": 34567, "name": "Digital Marketing Pro"},
    {"id": 45678, "name": "Affiliate Masters"},
    {"id": 56789, "name": "Traffic Boosters Inc"}
]

# Offers
OFFERS = [
    {"id": 1001, "name": "Summer Promo 2024"},
    {"id": 1002, "name": "Holiday Special"},
    {"id": 1003, "name": "Evergreen Offer A"},
    {"id": 1004, "name": "Winter Campaign"},
    {"id": 1005, "name": "New Year Deal"}
]

# Landing Pages
LANDING_PAGES = [
    {"id": 5001, "name": "Summer LP v2", "offer_id": 1001, "offer_name": "Summer Promo 2024"},
    {"id": 5002, "name": "Summer LP v1", "offer_id": 1001, "offer_name": "Summer Promo 2024"},
    {"id": 5003, "name": "Holiday Main Page", "offer_id": 1002, "offer_name": "Holiday Special"},
    {"id": 5004, "name": "Generic Offer Page", "offer_id": 1003, "offer_name": "Evergreen Offer A"}
]

# Countries
COUNTRIES = [
    {"code": "US", "name": "United States"},
    {"code": "DE", "name": "Germany"},
    {"code": "GB", "name": "United Kingdom"},
    {"code": "FR", "name": "France"},
    {"code": "CA", "name": "Canada"},
    {"code": "AU", "name": "Australia"},
    {"code": "NL", "name": "Netherlands"},
    {"code": "ES", "name": "Spain"},
    {"code": "IT", "name": "Italy"},
    {"code": "PL", "name": "Poland"}
]

def get_affiliate_by_id(affiliate_id: int) -> Dict:
    """Get affiliate by ID."""
    return next((a for a in AFFILIATES if a["id"] == affiliate_id), None)

def get_affiliate_by_name(name: str) -> Dict:
    """Get affiliate by name."""
    return next((a for a in AFFILIATES if a["name"].lower() == name.lower()), None)

def get_offer_by_id(offer_id: int) -> Dict:
    """Get offer by ID."""
    return next((o for o in OFFERS if o["id"] == offer_id), None)

def get_offer_by_name(name: str) -> Dict:
    """Get offer by name."""
    return next((o for o in OFFERS if o["name"].lower() == name.lower()), None)

def get_country_by_code(code: str) -> Dict:
    """Get country by code."""
    return next((c for c in COUNTRIES if c["code"].upper() == code.upper()), None)

def get_country_by_name(name: str) -> Dict:
    """Get country by name."""
    return next((c for c in COUNTRIES if c["name"].lower() == name.lower()), None)

def print_test_data_summary():
    """Print summary of all test data."""
    print("=" * 60)
    print("Test Data Reference")
    print("=" * 60)
    
    print("\n📊 Affiliates/Partners:")
    for aff in AFFILIATES:
        print(f"   ID: {aff['id']:5d} | Name: {aff['name']}")
    
    print("\n📊 Offers:")
    for offer in OFFERS:
        print(f"   ID: {offer['id']:5d} | Name: {offer['name']}")
    
    print("\n📊 Landing Pages:")
    for lp in LANDING_PAGES:
        print(f"   ID: {lp['id']:5d} | Name: {lp['name']:20s} | Offer: {lp['offer_id']} ({lp['offer_name']})")
    
    print("\n📊 Countries:")
    for country in COUNTRIES:
        print(f"   Code: {country['code']:2s} | Name: {country['name']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_test_data_summary()

