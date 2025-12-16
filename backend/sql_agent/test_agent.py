"""
Test script for the Workflow Orchestrator Agent.
Tests the agent with various queries to ensure it routes correctly to workflows.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Verify required environment variables
required_vars = [
    "GEMINI_KEY",  # or GOOGLE_API_KEY
    "EVERFLOW_API_KEY",
    "EVERFLOW_BASE_URL",
]

# Check for Gemini key (can be GEMINI_KEY or GOOGLE_API_KEY)
gemini_key = os.getenv("GEMINI_KEY") or os.getenv("GOOGLE_API_KEY")
if not gemini_key:
    missing_vars = ["GEMINI_KEY or GOOGLE_API_KEY"]
else:
    missing_vars = [var for var in required_vars if var != "GEMINI_KEY" and not os.getenv(var)]

if missing_vars:
    print("❌ Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nPlease set these in your .env file or environment.")
    sys.exit(1)

print("✅ All required environment variables are set")
if gemini_key:
    print(f"   - Google API Key: {'*' * (len(gemini_key) - 4)}{gemini_key[-4:]}")
print(f"   - Everflow Base URL: {os.getenv('EVERFLOW_BASE_URL')}")
print()

# Import after env check
from .workflow_agent import build_workflow_agent
from .workflow_tools import get_workflow_tools


def test_workflow_tools():
    """Test that all workflow tools are properly configured."""
    print("=" * 60)
    print("Testing Workflow Tools")
    print("=" * 60)
    
    tools = get_workflow_tools()
    print(f"\n✅ Found {len(tools)} workflow tools:")
    
    for tool in tools:
        print(f"   - {tool.name}")
        print(f"     Description: {tool.description[:80]}...")
    
    print("\n✅ All workflow tools loaded successfully")
    return tools


def test_agent_setup():
    """Test that the agent can be built successfully."""
    print("\n" + "=" * 60)
    print("Testing Agent Setup")
    print("=" * 60)
    
    try:
        agent, model, tools = build_workflow_agent()
        print("\n✅ Agent built successfully!")
        return agent, model, tools
    except Exception as e:
        print(f"\n❌ Error building agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None


def test_simple_query(agent, query: str):
    """Test a simple query with the agent."""
    print(f"\n{'=' * 60}")
    print(f"Testing Query: {query}")
    print("=" * 60)
    
    try:
        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
        
        if "messages" in result:
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                print(f"\n✅ Agent Response:")
                print("-" * 60)
                print(last_message.content)
                print("-" * 60)
                return True
            else:
                print(f"\n⚠️  Unexpected message format: {type(last_message)}")
                print(f"Message: {last_message}")
                return False
        else:
            print(f"\n⚠️  Unexpected result format: {result}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error executing query: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Workflow Agent Test Suite")
    print("=" * 60)
    
    # Test 1: Workflow Tools
    tools = test_workflow_tools()
    if not tools:
        print("\n❌ Workflow tools test failed. Aborting.")
        return
    
    # Test 2: Agent Setup
    agent, model, tools = test_agent_setup()
    if not agent:
        print("\n❌ Agent setup test failed. Aborting.")
        return
    
    # Test 3: Simple Queries
    print("\n" + "=" * 60)
    print("Testing Agent Queries")
    print("=" * 60)
    
    test_queries = [
        "Which landing page is best for Offer 123?",
        "Give me the weekly performance summary",
        "Export a fraud report for last week",
    ]
    
    results = []
    for query in test_queries:
        success = test_simple_query(agent, query)
        results.append((query, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for query, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {query}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    run_tests()

