"""
Real-World Quality Assurance Tests
Uses real IDs from Everflow API or realistic sample data.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from .workflow_agent import build_workflow_agent
from .everflow_client import fetch_real_data, EverflowClient


def get_test_data() -> Dict:
    """Get test data - try real API first, fallback to realistic samples."""
    print("Attempting to fetch real data from Everflow API...")
    
    try:
        data = fetch_real_data()
        # Check if we got real data
        if data["affiliates"] or data["offers"]:
            print("✅ Using real data from Everflow API")
            return data
    except Exception as e:
        print(f"⚠️  API fetch failed: {str(e)}")
    
    # Fallback to realistic sample data with names
    print("📋 Using realistic sample data for testing")
    return {
        "affiliates": [
            {"affiliate_id": 12345, "affiliate_name": "Premium Traffic Partners"},
            {"affiliate_id": 23456, "affiliate_name": "Global Media Network"},
            {"affiliate_id": 34567, "affiliate_name": "Digital Marketing Pro"},
            {"affiliate_id": 45678, "affiliate_name": "Affiliate Masters"},
            {"affiliate_id": 56789, "affiliate_name": "Traffic Boosters Inc"}
        ],
        "offers": [
            {"offer_id": 1001, "offer_name": "Summer Promo 2024"},
            {"offer_id": 1002, "offer_name": "Holiday Special"},
            {"offer_id": 1003, "offer_name": "Evergreen Offer A"},
            {"offer_id": 1004, "offer_name": "Winter Campaign"},
            {"offer_id": 1005, "offer_name": "New Year Deal"}
        ],
        "landing_pages": [
            {"offer_url_id": 5001, "offer_url_name": "Summer LP v2", "offer_id": 1001, "offer_name": "Summer Promo 2024"},
            {"offer_url_id": 5002, "offer_url_name": "Summer LP v1", "offer_id": 1001, "offer_name": "Summer Promo 2024"},
            {"offer_url_id": 5003, "offer_url_name": "Holiday Main Page", "offer_id": 1002, "offer_name": "Holiday Special"},
            {"offer_url_id": 5004, "offer_url_name": "Generic Offer Page", "offer_id": 1003, "offer_name": "Evergreen Offer A"}
        ],
        "countries": [
            {"code": "US", "name": "United States", "country": "United States", "country_name": "United States"},
            {"code": "DE", "name": "Germany", "country": "Germany", "country_name": "Germany"},
            {"code": "GB", "name": "United Kingdom", "country": "United Kingdom", "country_name": "United Kingdom"},
            {"code": "FR", "name": "France", "country": "France", "country_name": "France"},
            {"code": "CA", "name": "Canada", "country": "Canada", "country_name": "Canada"},
            {"code": "AU", "name": "Australia", "country": "Australia", "country_name": "Australia"},
            {"code": "NL", "name": "Netherlands", "country": "Netherlands", "country_name": "Netherlands"},
            {"code": "ES", "name": "Spain", "country": "Spain", "country_name": "Spain"},
            {"code": "IT", "name": "Italy", "country": "Italy", "country_name": "Italy"},
            {"code": "PL", "name": "Poland", "country": "Poland", "country_name": "Poland"}
        ]
    }


class RealWorldQATests:
    """Real-world QA tests using actual or realistic IDs."""
    
    def __init__(self):
        self.agent = None
        self.test_data = None
        self.results = []
        
    def setup(self):
        """Setup agent and fetch test data."""
        print("=" * 60)
        print("Real-World QA Test Suite")
        print("=" * 60)
        
        print("\n1. Building agent...")
        try:
            self.agent, _, _ = build_workflow_agent()
            print("   ✅ Agent ready")
        except Exception as e:
            print(f"   ❌ Agent setup failed: {str(e)}")
            return False
        
        print("\n2. Fetching test data...")
        self.test_data = get_test_data()
        print(f"   ✅ Test data ready:")
        print(f"      - {len(self.test_data['affiliates'])} affiliates")
        print(f"      - {len(self.test_data['offers'])} offers")
        print(f"      - {len(self.test_data['landing_pages'])} landing pages")
        print(f"      - {len(self.test_data['countries'])} countries")
        
        return True
    
    def generate_test_queries(self) -> List[Dict]:
        """Generate realistic test queries using real IDs."""
        queries = []
        
        # Get sample IDs and names
        affiliates = self.test_data["affiliates"]
        offers = self.test_data["offers"]
        landing_pages = self.test_data["landing_pages"]
        countries = self.test_data["countries"]
        
        # Handle country format (can be list of strings or list of dicts)
        # Support all field names: code, name, country, country_name
        country_codes = []
        country_names = []
        for c in countries:
            if isinstance(c, str):
                country_codes.append(c)
                country_names.append(c)
            else:
                # Try all possible field names from Everflow API
                code = c.get("code") or c.get("country_code")
                name = c.get("name") or c.get("country_name") or c.get("country")
                if code:
                    country_codes.append(code)
                if name:
                    country_names.append(name)
        
        # WF2 - Top Landing Pages (Real IDs and Names)
        if offers:
            offer = offers[0]
            # Test with ID
            queries.append({
                "query": f"Which landing page is best for Offer {offer['offer_id']}?",
                "category": "WF2 - Real Offer ID",
                "expected_workflow": "wf2_identify_top_lps",
                "real_id": f"offer_id={offer['offer_id']}"
            })
            
            # Test with name
            queries.append({
                "query": f"Which landing page is best for {offer['offer_name']}?",
                "category": "WF2 - Real Offer Name",
                "expected_workflow": "wf2_identify_top_lps",
                "real_id": f"offer_name=\"{offer['offer_name']}\""
            })
            
            if country_codes:
                # Test with ID + country code
                queries.append({
                    "query": f"Show me top 3 landing pages for Offer {offer['offer_id']} in {country_codes[0]}",
                    "category": "WF2 - Real Offer ID + Country Code",
                    "expected_workflow": "wf2_identify_top_lps",
                    "real_id": f"offer_id={offer['offer_id']}, country={country_codes[0]}"
                })
                
                # Test with name + country name
                if country_names:
                    queries.append({
                        "query": f"Show me top 3 landing pages for {offer['offer_name']} in {country_names[0]}",
                        "category": "WF2 - Real Offer Name + Country Name",
                        "expected_workflow": "wf2_identify_top_lps",
                        "real_id": f"offer_name=\"{offer['offer_name']}\", country={country_names[0]}"
                    })
        
        # WF1 - Tracking Links (Real IDs and Names)
        if affiliates and offers:
            aff = affiliates[0]
            offer = offers[0]
            
            # Test with IDs
            queries.append({
                "query": f"Generate a tracking link for Partner {aff['affiliate_id']} on Offer {offer['offer_id']}",
                "category": "WF1 - Real Partner ID + Offer ID",
                "expected_workflow": "wf1_generate_tracking_link",
                "real_id": f"affiliate_id={aff['affiliate_id']}, offer_id={offer['offer_id']}"
            })
            
            # Test with names
            queries.append({
                "query": f"Generate a tracking link for {aff['affiliate_name']} on {offer['offer_name']}",
                "category": "WF1 - Real Partner Name + Offer Name",
                "expected_workflow": "wf1_generate_tracking_link",
                "real_id": f"affiliate_name=\"{aff['affiliate_name']}\", offer_name=\"{offer['offer_name']}\""
            })
            
            # Test with mixed (name + ID)
            if len(affiliates) > 1:
                queries.append({
                    "query": f"Get tracking link for {affiliates[1]['affiliate_name']} on offer {offers[0]['offer_id']}",
                    "category": "WF1 - Mixed Names and IDs",
                    "expected_workflow": "wf1_generate_tracking_link",
                    "real_id": f"affiliate_name=\"{affiliates[1]['affiliate_name']}\", offer_id={offers[0]['offer_id']}"
                })
        
        # WF3 - Export Reports (Realistic dates)
        queries.append({
            "query": "Export a fraud report for last week",
            "category": "WF3 - Fraud Report",
            "expected_workflow": "wf3_export_report",
            "real_id": "date_range=last_week"
        })
        
        if offers:
            # Test with ID
            queries.append({
                "query": f"Download conversion data for Offer {offers[0]['offer_id']} from last month",
                "category": "WF3 - Real Offer ID Export",
                "expected_workflow": "wf3_export_report",
                "real_id": f"offer_id={offers[0]['offer_id']}"
            })
            
            # Test with name
            queries.append({
                "query": f"Export conversion data for {offers[0]['offer_name']} from last month",
                "category": "WF3 - Real Offer Name Export",
                "expected_workflow": "wf3_export_report",
                "real_id": f"offer_name=\"{offers[0]['offer_name']}\""
            })
        
        # WF6 - Weekly Summary
        queries.append({
            "query": "Give me the weekly performance summary",
            "category": "WF6 - Weekly Summary",
            "expected_workflow": "wf6_generate_weekly_summary",
            "real_id": "default"
        })
        
        if country_codes and country_names:
            # Test with country code
            queries.append({
                "query": f"What's our top performing geo this week? Show me {country_codes[0]} specifically",
                "category": "WF6 - Geo Summary (Code)",
                "expected_workflow": "wf6_generate_weekly_summary",
                "real_id": f"country={country_codes[0]}"
            })
            
            # Test with country name
            queries.append({
                "query": f"What's our top performing geo this week? Show me {country_names[0]} specifically",
                "category": "WF6 - Geo Summary (Name)",
                "expected_workflow": "wf6_generate_weekly_summary",
                "real_id": f"country={country_names[0]}"
            })
        
        # Mixed queries with real IDs and names
        if offers and country_codes:
            # Test with ID + code
            queries.append({
                "query": f"Which landing pages work best in {country_codes[0]} for Offer {offers[0]['offer_id']}?",
                "category": "WF2 - Complex Query (ID + Code)",
                "expected_workflow": "wf2_identify_top_lps",
                "real_id": f"offer_id={offers[0]['offer_id']}, country={country_codes[0]}"
            })
            
            # Test with name + name
            if country_names:
                queries.append({
                    "query": f"Which landing pages work best in {country_names[0]} for {offers[0]['offer_name']}?",
                    "category": "WF2 - Complex Query (Name + Name)",
                    "expected_workflow": "wf2_identify_top_lps",
                    "real_id": f"offer_name=\"{offers[0]['offer_name']}\", country={country_names[0]}"
                })
        
        # Edge cases with real IDs and names
        if offers:
            queries.append({
                "query": f"Show me data for offer {offers[0]['offer_id']}",
                "category": "Edge - Incomplete Query (ID)",
                "expected_workflow": None,
                "real_id": "incomplete"
            })
            
            queries.append({
                "query": f"Show me data for {offers[0]['offer_name']}",
                "category": "Edge - Incomplete Query (Name)",
                "expected_workflow": None,
                "real_id": "incomplete"
            })
        
        return queries
    
    def test_query(self, query_info: Dict) -> Tuple[bool, Dict]:
        """Test a single query and return results."""
        query = query_info["query"]
        category = query_info["category"]
        
        try:
            result = self.agent.invoke({"messages": [{"role": "user", "content": query}]})
            
            # Extract response
            if "messages" in result:
                last_message = result["messages"][-1]
                response = last_message.content if hasattr(last_message, "content") else str(last_message)
            else:
                response = str(result)
            
            # Quality checks
            has_table = "|" in response and "---" in response
            has_formatted_numbers = "," in response or "%" in response
            has_structure = "\n" in response or "**" in response
            response_length = len(response)
            
            # Check if correct workflow was called
            tool_calls = []
            if "messages" in result:
                for msg in result["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_calls.extend([tc.get("name", "") for tc in msg.tool_calls])
            
            correct_workflow = False
            if query_info.get("expected_workflow"):
                correct_workflow = query_info["expected_workflow"] in tool_calls
            
            quality_score = 0
            if response_length > 50:
                quality_score += 1
            if has_table:
                quality_score += 2
            if has_formatted_numbers:
                quality_score += 1
            if has_structure:
                quality_score += 1
            if correct_workflow or not query_info.get("expected_workflow"):
                quality_score += 1
            
            passed = quality_score >= 4  # At least 4/6 points
            
            return passed, {
                "query": query,
                "category": category,
                "response": response,
                "response_length": response_length,
                "has_table": has_table,
                "has_formatted_numbers": has_formatted_numbers,
                "has_structure": has_structure,
                "tool_calls": tool_calls,
                "correct_workflow": correct_workflow,
                "quality_score": quality_score,
                "passed": passed,
                "real_id": query_info.get("real_id", "")
            }
            
        except Exception as e:
            return False, {
                "query": query,
                "category": category,
                "error": str(e),
                "passed": False
            }
    
    def run_tests(self):
        """Run all real-world QA tests."""
        if not self.setup():
            return
        
        print("\n" + "=" * 60)
        print("Generating Real-World Test Queries")
        print("=" * 60)
        
        test_queries = self.generate_test_queries()
        print(f"\n✅ Generated {len(test_queries)} realistic test queries")
        
        print("\n" + "=" * 60)
        print("Running QA Tests")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for i, query_info in enumerate(test_queries, 1):
            print(f"\n[{i}/{len(test_queries)}] {query_info['category']}")
            print(f"Query: \"{query_info['query']}\"")
            print(f"Real ID: {query_info.get('real_id', 'N/A')}")
            
            success, result = self.test_query(query_info)
            self.results.append(result)
            
            if success:
                passed += 1
                status = "✅ PASS"
            else:
                failed += 1
                status = "❌ FAIL"
            
            print(f"Status: {status}")
            print(f"Quality Score: {result.get('quality_score', 0)}/6")
            print(f"Response Length: {result.get('response_length', 0)} chars")
            print(f"Has Table: {result.get('has_table', False)}")
            print(f"Formatted Numbers: {result.get('has_formatted_numbers', False)}")
            print(f"Tool Calls: {result.get('tool_calls', [])}")
            
            if result.get('error'):
                print(f"Error: {result['error']}")
            
            print("-" * 60)
        
        # Summary
        self.print_summary(passed, failed, len(test_queries))
    
    def print_summary(self, passed: int, failed: int, total: int):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("Real-World QA Test Summary")
        print("=" * 60)
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Quality metrics
        avg_score = sum(r.get("quality_score", 0) for r in self.results) / len(self.results) if self.results else 0
        tables_count = sum(1 for r in self.results if r.get("has_table"))
        formatted_count = sum(1 for r in self.results if r.get("has_formatted_numbers"))
        
        print(f"\nQuality Metrics:")
        print(f"  Average Quality Score: {avg_score:.1f}/6")
        print(f"  Responses with Tables: {tables_count}/{total} ({tables_count/total*100:.0f}%)")
        print(f"  Responses with Formatted Numbers: {formatted_count}/{total} ({formatted_count/total*100:.0f}%)")
        
        # By category
        print(f"\nResults by Category:")
        categories = {}
        for result in self.results:
            cat = result.get("category", "Unknown")
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0}
            if result.get("passed"):
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
        
        for category, counts in sorted(categories.items()):
            total_cat = counts["passed"] + counts["failed"]
            pass_rate_cat = (counts["passed"] / total_cat * 100) if total_cat > 0 else 0
            status = "✅" if counts["failed"] == 0 else "⚠️"
            print(f"  {status} {category}: {counts['passed']}/{total_cat} ({pass_rate_cat:.0f}%)")
        
        print()


def main():
    """Run real-world QA tests."""
    suite = RealWorldQATests()
    suite.run_tests()


if __name__ == "__main__":
    main()

