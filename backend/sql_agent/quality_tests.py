"""
Quality Tests for Workflow Agent Output
Tests response quality, routing accuracy, formatting, and error handling.
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from .workflow_agent import build_workflow_agent
from .workflow_tools import get_workflow_tools


class QualityTestSuite:
    """Comprehensive quality testing for agent outputs."""
    
    def __init__(self):
        self.agent = None
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Build the agent for testing."""
        print("=" * 60)
        print("Quality Test Suite - Workflow Agent")
        print("=" * 60)
        print("\nSetting up agent...")
        
        try:
            self.agent, model, tools = build_workflow_agent()
            print("✅ Agent setup complete\n")
            return True
        except Exception as e:
            print(f"❌ Agent setup failed: {str(e)}")
            return False
    
    def test_query(self, query: str, expected_workflow: str = None, 
                   expected_entities: Dict = None, min_length: int = 10) -> Tuple[bool, str]:
        """
        Test a single query and validate output quality.
        
        Args:
            query: The user query to test
            expected_workflow: Expected workflow tool to be called (optional)
            expected_entities: Expected entities to be extracted (optional)
            min_length: Minimum response length
        
        Returns:
            (success, message) tuple
        """
        try:
            result = self.agent.invoke({"messages": [{"role": "user", "content": query}]})
            
            # Extract response
            if "messages" in result:
                last_message = result["messages"][-1]
                response = last_message.content if hasattr(last_message, "content") else str(last_message)
            else:
                response = str(result)
            
            # Quality checks
            checks = []
            
            # 1. Response not empty
            if len(response.strip()) < min_length:
                checks.append(f"❌ Response too short ({len(response)} chars, min {min_length})")
            else:
                checks.append(f"✅ Response length: {len(response)} chars")
            
            # 2. Response contains useful information
            if response.lower() in ["", "error", "none", "null"]:
                checks.append("❌ Response appears empty or error-like")
            else:
                checks.append("✅ Response contains content")
            
            # 3. Check for proper formatting (markdown, structure)
            has_structure = any(marker in response for marker in ["\n", "|", "*", "-", ":"])
            if has_structure:
                checks.append("✅ Response has structure/formatting")
            else:
                checks.append("⚠️  Response lacks structure (may be fine for simple answers)")
            
            # 4. Check for error messages
            error_keywords = ["error", "failed", "exception", "traceback", "not found"]
            has_errors = any(keyword in response.lower() for keyword in error_keywords)
            if has_errors and "error" not in query.lower():
                checks.append("⚠️  Response contains error keywords (may be false positive)")
            else:
                checks.append("✅ No obvious error messages")
            
            # 5. Check tool calls in result (if available)
            tool_calls = []
            if "messages" in result:
                for msg in result["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_calls.extend([tc.get("name", "") for tc in msg.tool_calls])
            
            if tool_calls:
                checks.append(f"✅ Tools called: {', '.join(set(tool_calls))}")
                if expected_workflow:
                    if expected_workflow in tool_calls:
                        checks.append(f"✅ Correct workflow called: {expected_workflow}")
                    else:
                        checks.append(f"⚠️  Expected {expected_workflow}, got {tool_calls}")
            else:
                checks.append("⚠️  No tool calls detected (may be direct response)")
            
            # Summary
            all_passed = all("✅" in check or "⚠️" in check for check in checks)
            critical_passed = all("✅" in check for check in checks[:3])  # First 3 are critical
            
            return critical_passed, "\n".join(checks)
            
        except Exception as e:
            return False, f"❌ Exception: {str(e)}"
    
    def run_test_suite(self):
        """Run comprehensive test suite."""
        
        if not self.setup():
            return
        
        print("=" * 60)
        print("Running Quality Tests")
        print("=" * 60)
        
        # Test cases organized by workflow
        test_cases = [
            # WF2 - Top Performing Landing Pages
            {
                "query": "Which landing page is best for Offer 123?",
                "expected_workflow": "wf2_identify_top_lps",
                "expected_entities": {"offer_id": 123},
                "category": "WF2 - Top LPs"
            },
            {
                "query": "Show me the top 3 landing pages for offer 456 in Germany",
                "expected_workflow": "wf2_identify_top_lps",
                "expected_entities": {"offer_id": 456, "country_code": "DE", "top_n": 3},
                "category": "WF2 - Top LPs with filters"
            },
            {
                "query": "What's the best converting page for the Summer Promo offer?",
                "expected_workflow": "wf2_identify_top_lps",
                "category": "WF2 - Named offer"
            },
            
            # WF3 - Export Reports
            {
                "query": "Export a fraud report for last week",
                "expected_workflow": "wf3_export_report",
                "expected_entities": {"report_type": "fraud", "date_range": "last week"},
                "category": "WF3 - Fraud Report"
            },
            {
                "query": "Download conversion data for December 2024",
                "expected_workflow": "wf3_export_report",
                "expected_entities": {"report_type": "conversions", "date_range": "December 2024"},
                "category": "WF3 - Conversions Export"
            },
            {
                "query": "Get me a CSV of all conversions with sub1, sub2, affiliate for last month",
                "expected_workflow": "wf3_export_report",
                "category": "WF3 - Custom columns"
            },
            
            # WF6 - Weekly Summary
            {
                "query": "Give me the weekly performance summary",
                "expected_workflow": "wf6_generate_weekly_summary",
                "category": "WF6 - Weekly Summary"
            },
            {
                "query": "What's our top performing geo this week?",
                "expected_workflow": "wf6_generate_weekly_summary",
                "category": "WF6 - Geo summary"
            },
            {
                "query": "Show me a summary of internal advertiser performance",
                "expected_workflow": "wf6_generate_weekly_summary",
                "category": "WF6 - Internal advertiser"
            },
            
            # WF1 - Tracking Links
            {
                "query": "Generate a tracking link for Partner 123 on Offer 456",
                "expected_workflow": "wf1_generate_tracking_link",
                "expected_entities": {"affiliate_id": 123, "offer_id": 456},
                "category": "WF1 - Tracking Link"
            },
            {
                "query": "Get tracking link for affiliate ABC on the summer promo offer",
                "expected_workflow": "wf1_generate_tracking_link",
                "category": "WF1 - Named entities"
            },
            
            # Edge cases
            {
                "query": "Help me",
                "expected_workflow": None,
                "category": "Edge - Help request"
            },
            {
                "query": "What can you do?",
                "expected_workflow": None,
                "category": "Edge - Capabilities question"
            },
            {
                "query": "Show me data for offer",
                "expected_workflow": None,  # Incomplete query
                "category": "Edge - Incomplete query"
            },
        ]
        
        print(f"\nRunning {len(test_cases)} test cases...\n")
        
        for i, test_case in enumerate(test_cases, 1):
            category = test_case.get("category", "General")
            query = test_case["query"]
            expected_workflow = test_case.get("expected_workflow")
            
            print(f"[{i}/{len(test_cases)}] {category}")
            print(f"Query: \"{query}\"")
            
            success, details = self.test_query(
                query,
                expected_workflow=expected_workflow,
                expected_entities=test_case.get("expected_entities"),
                min_length=20
            )
            
            if success:
                self.passed += 1
                status = "✅ PASS"
            else:
                self.failed += 1
                status = "❌ FAIL"
            
            print(f"Status: {status}")
            print(f"Details:\n{details}")
            print("-" * 60)
            print()
            
            self.test_results.append({
                "category": category,
                "query": query,
                "success": success,
                "details": details
            })
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("Quality Test Summary")
        print("=" * 60)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Category breakdown
        print("\n" + "-" * 60)
        print("Results by Category:")
        print("-" * 60)
        
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0}
            if result["success"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
        
        for category, counts in sorted(categories.items()):
            total_cat = counts["passed"] + counts["failed"]
            pass_rate_cat = (counts["passed"] / total_cat * 100) if total_cat > 0 else 0
            status = "✅" if counts["failed"] == 0 else "⚠️"
            print(f"{status} {category}: {counts['passed']}/{total_cat} ({pass_rate_cat:.0f}%)")
        
        # Recommendations
        print("\n" + "-" * 60)
        print("Recommendations:")
        print("-" * 60)
        
        if pass_rate >= 90:
            print("✅ Excellent! Agent is performing well.")
        elif pass_rate >= 75:
            print("⚠️  Good performance, but some improvements needed.")
        else:
            print("❌ Significant issues detected. Review failed tests.")
        
        # Common issues
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n⚠️  {len(failed_tests)} test(s) failed. Review output quality.")
        
        print()


def main():
    """Run quality tests."""
    suite = QualityTestSuite()
    suite.run_test_suite()


if __name__ == "__main__":
    main()

