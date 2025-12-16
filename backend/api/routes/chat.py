"""Chat endpoint that uses the workflow agent for natural language queries."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.api.deps import verify_api_key
from backend.sql_agent.workflow_agent import build_workflow_agent

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat queries."""
    message: str = Field(..., description="User's natural language query")
    thread_id: Optional[str] = Field(None, description="Conversation thread ID for context")


class ChatResponse(BaseModel):
    """Response model for chat queries."""
    response: str
    thread_id: str
    status: str = "success"


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
) -> ChatResponse:
    """
    Process a natural language query using the workflow agent.
    
    The agent will:
    - Understand the user's intent
    - Route to the appropriate workflow (WF1-WF6)
    - Execute the workflow
    - Return a formatted response
    """
    try:
        # Build the workflow agent
        agent, _, _ = build_workflow_agent()
        
        # Use thread_id from request or generate a default one
        thread_id = request.thread_id or "default"
        
        # Configure the agent with thread_id for conversation context
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke the agent with the user's message
        # AgentExecutor expects {"input": "message"} format
        result = agent.invoke(
            {"input": request.message},
            config
        )
        
        # Extract the response from the agent's result
        # AgentExecutor returns {"output": "response"} format
        if "output" in result:
            response_content = result["output"]
        elif "messages" in result:
            last_message = result["messages"][-1]
            response_content = last_message.content if hasattr(last_message, "content") else str(last_message)
        else:
            response_content = str(result)
        
        return ChatResponse(
            response=response_content,
            thread_id=thread_id,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )

