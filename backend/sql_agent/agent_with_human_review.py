"""
Step 7: Implement human-in-the-loop review.
Agent with middleware to pause for human approval before executing workflow operations.
Uses Google Gemini following LangChain tutorial pattern.
"""
import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from .config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL,
)
from .workflow_tools import get_workflow_tools


def create_agent_with_human_review():
    """
    Create workflow agent with human-in-the-loop middleware.
    Pauses before executing write operations (WF1) for approval.
    Uses Google Gemini following LangChain tutorial pattern.
    
    Returns:
        Configured agent with human review middleware.
    """
    # Setup LLM - Google Gemini
    if GOOGLE_API_KEY:
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    else:
        raise ValueError("GEMINI_KEY or GOOGLE_API_KEY not found in environment variables")
    
    model = init_chat_model(GEMINI_MODEL)
    
    # Setup Workflow Tools
    tools = get_workflow_tools()
    
    # System prompt for workflow agent
    system_prompt = """
You are the Adsomnia Data Agent, an intelligent assistant that helps users interact with Everflow marketing data.

Available workflows: WF1 (tracking links), WF2 (top LPs), WF3 (export reports), WF4 (default LP alerts), WF5 (paused partners), WF6 (weekly summaries).

For WF1 (generate_tracking_link), always pause for user confirmation if approval is needed.
Be conversational, extract entities from queries, and route to the appropriate workflow.
"""
    
    # Create agent with human-in-the-loop middleware
    # Interrupt on WF1 (tracking links) which may require approval
    agent = create_agent(
        model,
        tools,
        system_prompt=system_prompt,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={"wf1_generate_tracking_link": True},
                description_prefix="Workflow execution pending approval",
            ),
        ],
        checkpointer=InMemorySaver(),
    )
    
    print("✅ Workflow Agent with human-in-the-loop review created")
    return agent


def run_with_human_review(question: str, config: dict = None):
    """
    Run agent with human review - pauses before executing workflow operations (especially WF1).
    
    Args:
        question: User question to ask the agent.
        config: Optional configuration dict with thread_id.
    
    Returns:
        Generator of agent steps.
    """
    if config is None:
        config = {"configurable": {"thread_id": "1"}}
    
    agent = create_agent_with_human_review()
    
    print(f"\n❓ Question: {question}")
    print("=" * 60)
    
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config,
        stream_mode="values",
    ):
        if "messages" in step:
            step["messages"][-1].pretty_print()
        elif "__interrupt__" in step:
            print("\n" + "=" * 60)
            print("⏸️  INTERRUPTED - Human Review Required")
            print("=" * 60)
            interrupt = step["__interrupt__"][0]
            for request in interrupt.value["action_requests"]:
                print(f"\n{request['description']}")
                print(f"Workflow: {request.get('tool', 'N/A')}")
                print(f"Args: {request.get('args', {})}")
            
            # Return the interrupt so caller can decide to approve/reject
            yield step
        else:
            yield step


def resume_execution(decision: str = "approve", config: dict = None):
    """
    Resume agent execution after human review.
    
    Args:
        decision: "approve" or "reject"
        config: Configuration dict with thread_id.
    
    Returns:
        Generator of agent steps after resumption.
    """
    if config is None:
        config = {"configurable": {"thread_id": "1"}}
    
    agent = create_agent_with_human_review()
    
    decision_type = "approve" if decision.lower() == "approve" else "reject"
    
    for step in agent.stream(
        Command(resume={"decisions": [{"type": decision_type}]}),
        config,
        stream_mode="values",
    ):
        if "messages" in step:
            step["messages"][-1].pretty_print()
        elif "__interrupt__" in step:
            print("\n⏸️  INTERRUPTED:")
            interrupt = step["__interrupt__"][0]
            for request in interrupt.value["action_requests"]:
                print(request["description"])
            yield step
        else:
            yield step


if __name__ == "__main__":
    # Example usage
    question = "Generate a tracking link for Partner 123 on Offer 456"
    config = {"configurable": {"thread_id": "1"}}
    
    print("Running agent with human-in-the-loop review...")
    print("The agent will pause before executing workflow operations (especially WF1) for your approval.\n")
    
    # Run and handle interrupts
    for step in run_with_human_review(question, config):
        if "__interrupt__" in step:
            print("\n💡 To approve and continue, call resume_execution('approve')")
            print("   To reject, call resume_execution('reject')")
            break

