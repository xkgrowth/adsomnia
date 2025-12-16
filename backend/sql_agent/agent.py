"""
SQL Agent Implementation following LangChain tutorial.
Steps 1-4: LLM setup, database configuration, tools, and agent creation.
"""
import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from .config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    OPENAI_API_VERSION,
    DATABASE_URI,
)


def setup_azure_llm():
    """
    Step 1: Select an LLM - Azure OpenAI configuration.
    
    Returns:
        Initialized chat model for Azure OpenAI.
    """
    # Set environment variables for Azure OpenAI
    os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
    os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    os.environ["OPENAI_API_VERSION"] = OPENAI_API_VERSION
    
    # Initialize the model
    model = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
    )
    
    print("✅ Azure OpenAI LLM initialized")
    return model


def setup_database(db_uri: str = None):
    """
    Step 2: Configure the database.
    
    Args:
        db_uri: Database URI. Defaults to DATABASE_URI from config.
    
    Returns:
        SQLDatabase instance.
    """
    if db_uri is None:
        db_uri = DATABASE_URI
    
    db = SQLDatabase.from_uri(db_uri)
    
    print(f"✅ Database configured - Dialect: {db.dialect}")
    print(f"   Available tables: {db.get_usable_table_names()}")
    
    # Show sample output
    sample = db.run("SELECT * FROM Artist LIMIT 5;")
    print(f"   Sample output: {sample}")
    
    return db


def setup_tools(db: SQLDatabase, model):
    """
    Step 3: Add tools for database interactions.
    
    Args:
        db: SQLDatabase instance.
        model: Initialized chat model.
    
    Returns:
        List of tools from SQLDatabaseToolkit.
    """
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()
    
    print("\n✅ Tools configured:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description[:80]}...")
    
    return tools


def create_sql_agent(model, tools, db: SQLDatabase, top_k: int = 5):
    """
    Step 4: Use create_agent to build the SQL agent.
    
    Args:
        model: Initialized chat model.
        tools: List of tools from SQLDatabaseToolkit.
        db: SQLDatabase instance.
        top_k: Maximum number of results to return (default: 5).
    
    Returns:
        Configured agent.
    """
    system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
        dialect=db.dialect,
        top_k=top_k,
    )
    
    agent = create_agent(
        model,
        tools,
        system_prompt=system_prompt,
    )
    
    print("\n✅ SQL Agent created with system prompt")
    return agent


def build_agent(db_uri: str = None, top_k: int = 5):
    """
    Build a complete SQL agent following all setup steps.
    
    Args:
        db_uri: Optional database URI override.
        top_k: Maximum number of results to return.
    
    Returns:
        Tuple of (agent, model, db, tools)
    """
    print("=" * 60)
    print("Building SQL Agent - Following LangChain Tutorial")
    print("=" * 60)
    
    # Step 1: Setup LLM
    model = setup_azure_llm()
    
    # Step 2: Setup Database
    db = setup_database(db_uri)
    
    # Step 3: Setup Tools
    tools = setup_tools(db, model)
    
    # Step 4: Create Agent
    agent = create_sql_agent(model, tools, db, top_k)
    
    print("\n" + "=" * 60)
    print("✅ SQL Agent setup complete!")
    print("=" * 60)
    
    return agent, model, db, tools

