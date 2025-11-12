#!/bin/bash

# Agriculture RAG Platform Setup Script

echo "🌾 Agriculture RAG Platform - Setup"
echo "====================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file. Please edit it if you want to change Ollama URL."
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/vector_db
mkdir -p data/processed

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Initialize the database: python scripts/init_database.py"
echo "3. Start the server: ./scripts/run.sh"
echo ""
echo "Or simply run: ./scripts/run.sh (it will initialize the database if needed)"
