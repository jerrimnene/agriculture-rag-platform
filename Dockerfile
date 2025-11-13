FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install only essential dependencies (no heavy ML libs)
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn==0.27.0 \
    pydantic==2.5.3 \
    python-multipart==0.0.6 \
    pyyaml==6.0.1 \
    aiohttp==3.9.1 \
    aiofiles==23.2.1 \
    jinja2==3.1.3 \
    python-dotenv==1.0.0 \
    requests>=2.31.0 \
    numpy==1.26.3 \
    pandas==2.1.4 \
    # Core RAG dependencies only
    chromadb==0.4.22 \
    sentence-transformers==2.3.1 \
    langchain==0.1.4 \
    langchain-community==0.0.16

# Copy application code
COPY src ./src
COPY config ./config
COPY frontend ./frontend
COPY data ./data

# Expose port
EXPOSE 8080

# Start - fly.io sets PORT=8080
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
