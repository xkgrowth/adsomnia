"""Chat endpoint that uses the workflow agent for natural language queries."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.api.deps import verify_api_key
from backend.sql_agent.workflow_agent import build_workflow_agent

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Cache the agent to avoid rebuilding on every request (expensive operation)
_agent_cache = None

def get_agent():
    """Get or build the workflow agent (cached)."""
    global _agent_cache
    if _agent_cache is None:
        print("🔧 Building workflow agent (first request)...")
        _agent_cache, _, _ = build_workflow_agent()
        print("✅ Workflow agent built and cached")
    return _agent_cache


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
        import time
        start_time = time.time()
        
        # Get the cached workflow agent (built once, reused for all requests)
        agent = get_agent()
        agent_time = time.time() - start_time
        if agent_time > 0.1:
            print(f"⏱️  Agent retrieval took {agent_time:.2f} seconds")
        
        # Use thread_id from request or generate a default one
        thread_id = request.thread_id or "default"
        
        # Configure the agent with thread_id for conversation context
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke the agent with the user's message
        # AgentExecutor expects {"input": "message"} format
        invoke_start = time.time()
        print(f"🚀 Invoking agent with message: {request.message[:100]}...")
        
        # Wrap agent.invoke with timeout protection using asyncio
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        
        try:
            # Run agent.invoke in executor with timeout
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    executor,
                    lambda: agent.invoke({"input": request.message}, config)
                ),
                timeout=80.0  # 80 second timeout (should be fast with pre-formatted responses)
            )
        except asyncio.TimeoutError:
            executor.shutdown(wait=False)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Agent processing timed out after 100 seconds. The query may be too complex or the LLM is taking too long. Please try a simpler query or shorter date range."
            )
        finally:
            executor.shutdown(wait=False)
        
        invoke_time = time.time() - invoke_start
        print(f"⏱️  Agent processing took {invoke_time:.2f} seconds")
        
        # Extract the response from the agent's result
        # AgentExecutor returns {"output": "response"} format
        print(f"🔍 Agent result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
        print(f"🔍 Agent result type: {type(result)}")
        if isinstance(result, dict):
            print(f"🔍 Agent result full structure: {json.dumps({k: str(type(v)) for k, v in result.items()}, indent=2)}")
        
        response_content = None
        
        if "output" in result:
            response_content = result["output"]
            print(f"📝 Using 'output' field, length: {len(str(response_content))}")
            if len(str(response_content)) > 0:
                print(f"📝 First 200 chars of output: {str(response_content)[:200]}")
        elif "messages" in result:
            messages = result["messages"]
            print(f"📝 Found {len(messages)} messages in result")
            if len(messages) > 0:
                last_message = messages[-1]
                print(f"📝 Last message type: {type(last_message)}")
                if hasattr(last_message, "content"):
                    response_content = last_message.content
                    print(f"📝 Using last message content, length: {len(str(response_content))}")
                    if len(str(response_content)) > 0:
                        print(f"📝 First 200 chars: {str(response_content)[:200]}")
                else:
                    response_content = str(last_message)
                    print(f"📝 Using str(last_message), length: {len(str(response_content))}")
            else:
                print(f"⚠️  Warning: messages array is empty")
        else:
            response_content = str(result)
            print(f"📝 Using str(result), length: {len(str(response_content))}")
            if len(str(response_content)) > 0:
                print(f"📝 First 200 chars: {str(response_content)[:200]}")
        
        # Validate response is not empty
        if not response_content or (isinstance(response_content, str) and response_content.strip() == ""):
            print(f"⚠️  Warning: Agent returned empty response. Result structure: {type(result)}")
            if isinstance(result, dict):
                print(f"⚠️  Result dict contents: {list(result.keys())}")
                print(f"⚠️  Full result (first 1000 chars): {str(result)[:1000]}")
            # Try to extract any error information
            if isinstance(result, dict) and "intermediate_steps" in result:
                print(f"⚠️  Intermediate steps found: {len(result.get('intermediate_steps', []))}")
                for i, step in enumerate(result.get('intermediate_steps', [])):
                    print(f"⚠️  Step {i}: {type(step)}")
            response_content = "I apologize, but I received an empty response from the workflow agent. Please try your query again or rephrase it."
        
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

