"""
Step 5: Run the agent - Main script to execute workflow agent queries.
"""
from .workflow_agent import build_workflow_agent


def run_agent_example():
    """Run example queries with the workflow orchestrator agent."""
    # Build the agent
    agent, model, tools = build_workflow_agent()
    
    # Example questions for Everflow workflows
    questions = [
        "Which landing page is best for Offer 123?",
        "Export a fraud report for last week",
        "Give me the weekly performance summary",
        "Generate a tracking link for Partner 456 on Offer 789",
    ]
    
    print("\n" + "=" * 60)
    print("Running Example Workflow Queries")
    print("=" * 60)
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        print("-" * 60)
        
        try:
            # Run the agent
            result = agent.invoke({"messages": [{"role": "user", "content": question}]})
            
            # Print the final response
            if "messages" in result:
                last_message = result["messages"][-1]
                if hasattr(last_message, "content"):
                    print(f"✅ Answer: {last_message.content}")
                else:
                    print(f"✅ Result: {last_message}")
            else:
                print(f"✅ Result: {result}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)


if __name__ == "__main__":
    run_agent_example()

