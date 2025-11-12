#!/bin/bash

# Agriculture RAG Platform Startup Script

echo "🌾 Agriculture RAG Platform"
echo "=============================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
echo "🔍 Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   Run: ollama serve"
    exit 1
fi

echo "✓ Ollama is running"

# Check if vector database exists
if [ ! -d "data/vector_db" ] || [ -z "$(ls -A data/vector_db)" ]; then
    echo ""
    echo "⚠️  Vector database not found or empty."
    echo "Would you like to initialize it now? This will process all documents."
    read -p "Initialize database? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python scripts/init_database.py
        if [ $? -ne 0 ]; then
            echo "❌ Database initialization failed"
            exit 1
        fi
    else
        echo "❌ Cannot start without initialized database"
        exit 1
    fi
fi

# Start the API server
echo ""
echo "🚀 Starting Agriculture RAG Platform API..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Web UI: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd src/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
