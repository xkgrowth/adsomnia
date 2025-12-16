"""Configuration for Workflow Agent - Google Gemini and Everflow API setup."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GEMINI_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "google_genai:gemini-2.5-flash-lite")

# LangSmith Configuration (optional)
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# Everflow API Configuration
EVERFLOW_API_KEY = os.getenv("EVERFLOW_API_KEY")
EVERFLOW_BASE_URL = os.getenv("EVERFLOW_BASE_URL", "https://api.eflow.team")
EVERFLOW_TIMEZONE_ID = int(os.getenv("EVERFLOW_TIMEZONE_ID", "67"))

