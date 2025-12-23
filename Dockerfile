# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY .env.example ./.env.example

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Cloud Run will use PORT env var, but we expose 8080 as default)
EXPOSE 8080

# Set environment variable for Cloud Run (default to 8080)
ENV PORT=8080

# Run the application
# Cloud Run will set PORT env var dynamically
CMD sh -c "uvicorn backend.api.main:app --host 0.0.0.0 --port \${PORT:-8080}"

