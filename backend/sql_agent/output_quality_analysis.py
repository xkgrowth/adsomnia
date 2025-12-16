"""
Detailed Output Quality Analysis
Analyzes agent responses for formatting, completeness, and user-friendliness.
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from .workflow_agent import build_workflow_agent


def analyze_response(response: str, query: str) -> dict:
    """Analyze a single response for quality metrics."""
    analysis = {
        "length": len(response),
        "word_count": len(response.split()),
        "has_structure": False,
        "has_markdown": False,
        "has_data": False,
        "has_links": False,
        "is_user_friendly": True,
        "issues": [],
        "strengths": []
    }
    
    # Check for structure
    if any(marker in response for marker in ["\n", "|", "*", "-", ":", "#"]):
        analysis["has_structure"] = True
        analysis["strengths"].append("Well-structured response")
    
    # Check for markdown
    if any(marker in response for marker in ["**", "*", "`", "[", "]", "#"]):
        analysis["has_markdown"] = True
        analysis["strengths"].append("Uses markdown formatting")
    
    # Check for data/metrics
    if any(indicator in response.lower() for indicator in ["%", "$", "conversion", "click", "revenue", "offer", "partner"]):
        analysis["has_data"] = True
        analysis["strengths"].append("Contains relevant data/metrics")
    
    # Check for links
    if "http" in response or "https" in response or ".csv" in response:
        analysis["has_links"] = True
        analysis["strengths"].append("Contains links/URLs")
    
    # Check for issues
    if len(response) < 20:
        analysis["issues"].append("Response too short")
        analysis["is_user_friendly"] = False
    
    if response.lower().strip() in ["", "none", "null", "error"]:
        analysis["issues"].append("Empty or error-like response")
        analysis["is_user_friendly"] = False
    
    error_keywords = ["traceback", "exception", "failed", "error occurred"]
    if any(keyword in response.lower() for keyword in error_keywords):
        analysis["issues"].append("Contains error messages")
        analysis["is_user_friendly"] = False
    
    # Check if response answers the query
    query_lower = query.lower()
    if "which" in query_lower or "what" in query_lower or "show" in query_lower:
        if len(response) < 50:
            analysis["issues"].append("May not fully answer the question")
    
    return analysis


def test_sample_queries():
    """Test a sample of queries and analyze output quality."""
    print("=" * 60)
    print("Output Quality Analysis")
    print("=" * 60)
    
    # Build agent
    print("\nBuilding agent...")
    agent, model, tools = build_workflow_agent()
    print("✅ Agent ready\n")
    
    # Sample queries
    test_queries = [
        "Which landing page is best for Offer 123?",
        "Export a fraud report for last week",
        "Give me the weekly performance summary",
        "Generate a tracking link for Partner 123 on Offer 456",
    ]
    
    print("=" * 60)
    print("Testing Sample Queries")
    print("=" * 60)
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: \"{query}\"")
        print("-" * 60)
        
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": query}]})
            
            # Extract response
            if "messages" in result:
                last_message = result["messages"][-1]
                response = last_message.content if hasattr(last_message, "content") else str(last_message)
            else:
                response = str(result)
            
            # Analyze
            analysis = analyze_response(response, query)
            
            # Print analysis
            print(f"Response Length: {analysis['length']} chars, {analysis['word_count']} words")
            print(f"\nQuality Metrics:")
            print(f"  Structure: {'✅' if analysis['has_structure'] else '❌'}")
            print(f"  Markdown: {'✅' if analysis['has_markdown'] else '❌'}")
            print(f"  Data/Metrics: {'✅' if analysis['has_data'] else '❌'}")
            print(f"  Links: {'✅' if analysis['has_links'] else '❌'}")
            print(f"  User-Friendly: {'✅' if analysis['is_user_friendly'] else '❌'}")
            
            if analysis['strengths']:
                print(f"\nStrengths:")
                for strength in analysis['strengths']:
                    print(f"  ✅ {strength}")
            
            if analysis['issues']:
                print(f"\nIssues:")
                for issue in analysis['issues']:
                    print(f"  ⚠️  {issue}")
            
            print(f"\nResponse Preview:")
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"  {preview}")
            
            results.append({
                "query": query,
                "response": response,
                "analysis": analysis
            })
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary
    print("=" * 60)
    print("Quality Summary")
    print("=" * 60)
    
    total = len(results)
    user_friendly = sum(1 for r in results if r['analysis']['is_user_friendly'])
    has_structure = sum(1 for r in results if r['analysis']['has_structure'])
    has_data = sum(1 for r in results if r['analysis']['has_data'])
    
    print(f"\nTotal Queries Tested: {total}")
    print(f"User-Friendly Responses: {user_friendly}/{total} ({user_friendly/total*100:.0f}%)")
    print(f"Structured Responses: {has_structure}/{total} ({has_structure/total*100:.0f}%)")
    print(f"Responses with Data: {has_data}/{total} ({has_data/total*100:.0f}%)")
    
    # Recommendations
    print("\n" + "-" * 60)
    print("Recommendations:")
    print("-" * 60)
    
    if user_friendly < total:
        print("⚠️  Some responses need improvement for user-friendliness")
    
    if has_structure < total * 0.7:
        print("⚠️  Consider improving response formatting/structure")
    
    if has_data < total * 0.7:
        print("⚠️  Some responses may lack relevant data/metrics")
    
    avg_length = sum(r['analysis']['length'] for r in results) / total if total > 0 else 0
    print(f"\nAverage Response Length: {avg_length:.0f} characters")
    
    if avg_length < 100:
        print("⚠️  Responses may be too brief - consider adding more context")
    elif avg_length > 500:
        print("⚠️  Responses may be too verbose - consider condensing")
    else:
        print("✅ Response length is appropriate")


if __name__ == "__main__":
    test_sample_queries()

