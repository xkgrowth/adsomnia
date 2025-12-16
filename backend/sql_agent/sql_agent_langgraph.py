"""
sql_agent_langgraph.py - LangGraph implementation for Studio.
Alternative implementation using LangGraph primitives for deeper customization.
"""
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import os
import pathlib
import requests
from .config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    OPENAI_API_VERSION,
)

# Initialize components (same as sql_agent.py)
os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
os.environ["OPENAI_API_VERSION"] = OPENAI_API_VERSION

model = init_chat_model(
    "azure_openai:gpt-4.1",
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Setup database
url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
local_path = pathlib.Path("Chinook.db")

if not local_path.exists():
    response = requests.get(url)
    if response.status_code == 200:
        local_path.write_bytes(response.content)

db = SQLDatabase.from_uri("sqlite:///Chinook.db")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# Create LangGraph
tool_node = ToolNode(tools)
graph = StateGraph(...)  # Simplified - full implementation would require proper state definition
graph.add_node("tools", tool_node)
graph.add_edge("tools", END)
graph = graph.compile(checkpointer=MemorySaver())

