#!/bin/bash
# Quick start script for Adsomnia Workflow API

echo "============================================================"
echo "Starting Adsomnia Workflow API"
echo "============================================================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected"
    echo "   Activate your venv first: source venv/bin/activate"
    echo ""
fi

# Check if FastAPI is installed
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing FastAPI dependencies..."
    pip install fastapi uvicorn[standard] pydantic
    echo ""
fi

# Start the server
echo "🚀 Starting API server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo "============================================================"
echo ""

uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

