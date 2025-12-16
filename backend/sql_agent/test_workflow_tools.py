"""
Simple test for workflow tools without requiring Azure OpenAI.
Tests that the tools are properly configured and can be called.
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Check Everflow config
everflow_key = os.getenv("EVERFLOW_API_KEY")
everflow_url = os.getenv("EVERFLOW_BASE_URL")

print("=" * 60)
print("Workflow Tools Test (No LLM Required)")
print("=" * 60)

if everflow_key:
    print(f"✅ EVERFLOW_API_KEY: {'*' * (len(everflow_key) - 4)}{everflow_key[-4:]}")
else:
    print("❌ EVERFLOW_API_KEY: Not set")

if everflow_url:
    print(f"✅ EVERFLOW_BASE_URL: {everflow_url}")
else:
    print("❌ EVERFLOW_BASE_URL: Not set")

print()

# Test workflow tools
print("=" * 60)
print("Testing Workflow Tools")
print("=" * 60)

try:
    from .workflow_tools import get_workflow_tools
    
    tools = get_workflow_tools()
    print(f"\n✅ Successfully loaded {len(tools)} workflow tools:\n")
    
    for tool in tools:
        print(f"📦 {tool.name}")
        print(f"   Description: {tool.description[:100]}...")
        print()
    
    # Test calling each tool with sample inputs
    print("=" * 60)
    print("Testing Tool Execution (with placeholder data)")
    print("=" * 60)
    
    test_results = []
    
    # Test WF1
    print("\n1. Testing wf1_generate_tracking_link...")
    try:
        result = tools[0].invoke({"affiliate_id": 123, "offer_id": 456})
        print(f"   ✅ Success: {result[:100]}...")
        test_results.append(("WF1", True))
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        test_results.append(("WF1", False))
    
    # Test WF2
    print("\n2. Testing wf2_identify_top_lps...")
    try:
        result = tools[1].invoke({"offer_id": 123})
        print(f"   ✅ Success: {result[:100]}...")
        test_results.append(("WF2", True))
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        test_results.append(("WF2", False))
    
    # Test WF3
    print("\n3. Testing wf3_export_report...")
    try:
        result = tools[2].invoke({"report_type": "fraud", "date_range": "last week"})
        print(f"   ✅ Success: {result[:100]}...")
        test_results.append(("WF3", True))
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        test_results.append(("WF3", False))
    
    # Test WF4
    print("\n4. Testing wf4_check_default_lp_alert...")
    try:
        result = tools[3].invoke({})
        print(f"   ✅ Success: {result[:100]}...")
        test_results.append(("WF4", True))
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        test_results.append(("WF4", False))
    
    # Test WF5
    print("\n5. Testing wf5_check_paused_partners...")
    try:
        result = tools[4].invoke({})
        print(f"   ✅ Success: {result[:100]}...")
        test_results.append(("WF5", True))
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        test_results.append(("WF5", False))
    
    # Test WF6
    print("\n6. Testing wf6_generate_weekly_summary...")
    try:
        result = tools[5].invoke({"days": 7, "group_by": "country"})
        print(f"   ✅ Success: {result[:100]}...")
        test_results.append(("WF6", True))
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        test_results.append(("WF6", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for workflow, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {workflow}")
    
    print(f"\nResults: {passed}/{total} workflow tools working")
    
    if passed == total:
        print("\n🎉 All workflow tools are working correctly!")
        print("\n💡 Next step: Set up Azure OpenAI credentials to test the full agent.")
    else:
        print(f"\n⚠️  {total - passed} workflow tool(s) need attention.")
    
except ImportError as e:
    print(f"\n❌ Import error: {str(e)}")
    print("Make sure you're in the virtual environment and dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

