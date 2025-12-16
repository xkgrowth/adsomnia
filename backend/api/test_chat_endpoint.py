"""Test script for chat endpoint."""
import requests
import json
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def test_chat_endpoint():
    """Test the chat endpoint with various queries."""
    print("=" * 60)
    print("Testing Chat Endpoint")
    print("=" * 60)
    print(f"\nAPI Base: {API_BASE}")
    print(f"API Key: {API_KEY[:20]}...")
    
    test_queries = [
        "Which landing page is best for Offer 1001?",
        "Give me the weekly performance summary",
        "Generate a tracking link for Partner 12345 on Offer 1001",
        "Export a fraud report for last week",
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_queries)}: {query}")
        print(f"{'='*60}")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/chat/query",
                json={"message": query},
                headers=headers,
                timeout=60
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success")
                print(f"Response Length: {len(data.get('response', ''))} chars")
                print(f"Thread ID: {data.get('thread_id', 'N/A')}")
                print(f"\nResponse Preview:")
                preview = data.get('response', '')[:200]
                print(f"{preview}...")
                results.append(("✅ PASS", query))
            else:
                print(f"❌ Failed")
                print(f"Error: {response.text}")
                results.append(("❌ FAIL", query))
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error - Is the API server running?")
            print(f"   Start with: uvicorn backend.api.main:app --host 0.0.0.0 --port 8000")
            results.append(("❌ CONNECTION ERROR", query))
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append(("❌ ERROR", query))
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for status, _ in results if "✅" in status)
    total = len(results)
    
    for status, query in results:
        print(f"{status} - {query[:50]}...")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All chat endpoint tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    test_chat_endpoint()

