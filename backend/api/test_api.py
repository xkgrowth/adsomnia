"""Test script for API endpoints."""
import requests
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"  # Update with your API key from .env

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def test_health():
    """Test health check endpoint."""
    print("\n" + "=" * 60)
    print("Testing Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_wf1_tracking_link():
    """Test WF1 - Generate tracking link."""
    print("\n" + "=" * 60)
    print("Testing WF1 - Generate Tracking Link")
    print("=" * 60)
    
    payload = {
        "affiliate_id": 12345,
        "offer_id": 1001
    }
    
    response = requests.post(
        f"{API_BASE}/api/workflows/wf1/tracking-link",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_wf2_top_lps():
    """Test WF2 - Top landing pages."""
    print("\n" + "=" * 60)
    print("Testing WF2 - Top Landing Pages")
    print("=" * 60)
    
    payload = {
        "offer_id": 1001,
        "country_code": "US",
        "days": 30,
        "min_leads": 20,
        "top_n": 3
    }
    
    response = requests.post(
        f"{API_BASE}/api/workflows/wf2/top-landing-pages",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_wf3_export_report():
    """Test WF3 - Export report."""
    print("\n" + "=" * 60)
    print("Testing WF3 - Export Report")
    print("=" * 60)
    
    payload = {
        "report_type": "fraud",
        "date_range": "last week",
        "columns": ["sub1", "sub2", "affiliate"],
        "filters": {
            "offer_id": 1001
        }
    }
    
    response = requests.post(
        f"{API_BASE}/api/workflows/wf3/export-report",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_wf4_default_lp_alert():
    """Test WF4 - Default LP alert."""
    print("\n" + "=" * 60)
    print("Testing WF4 - Default LP Alert")
    print("=" * 60)
    
    payload = {
        "date": "2024-12-15",
        "click_threshold": 50
    }
    
    response = requests.post(
        f"{API_BASE}/api/workflows/wf4/default-lp-alert",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_wf5_paused_partners():
    """Test WF5 - Paused partners."""
    print("\n" + "=" * 60)
    print("Testing WF5 - Paused Partners")
    print("=" * 60)
    
    payload = {
        "analysis_days": 3,
        "drop_threshold": -50.0
    }
    
    response = requests.post(
        f"{API_BASE}/api/workflows/wf5/paused-partners",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_wf6_weekly_summary():
    """Test WF6 - Weekly summary."""
    print("\n" + "=" * 60)
    print("Testing WF6 - Weekly Summary")
    print("=" * 60)
    
    payload = {
        "days": 7,
        "group_by": "country"
    }
    
    response = requests.post(
        f"{API_BASE}/api/workflows/wf6/weekly-summary",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_authentication():
    """Test authentication failure."""
    print("\n" + "=" * 60)
    print("Testing Authentication (should fail)")
    print("=" * 60)
    
    bad_headers = {"X-API-Key": "wrong-key"}
    
    response = requests.post(
        f"{API_BASE}/api/workflows/wf1/tracking-link",
        json={"affiliate_id": 12345, "offer_id": 1001},
        headers=bad_headers
    )
    
    print(f"Status: {response.status_code} (expected 401)")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401


def main():
    """Run all tests."""
    print("=" * 60)
    print("Adsomnia Workflow API Test Suite")
    print("=" * 60)
    print(f"\nAPI Base URL: {API_BASE}")
    print(f"API Key: {API_KEY[:20]}...")
    
    results = []
    
    # Test health check (no auth required)
    results.append(("Health Check", test_health()))
    
    # Test authentication
    results.append(("Authentication", test_authentication()))
    
    # Test all workflows
    results.append(("WF1 - Tracking Link", test_wf1_tracking_link()))
    results.append(("WF2 - Top Landing Pages", test_wf2_top_lps()))
    results.append(("WF3 - Export Report", test_wf3_export_report()))
    results.append(("WF4 - Default LP Alert", test_wf4_default_lp_alert()))
    results.append(("WF5 - Paused Partners", test_wf5_paused_partners()))
    results.append(("WF6 - Weekly Summary", test_wf6_weekly_summary()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

