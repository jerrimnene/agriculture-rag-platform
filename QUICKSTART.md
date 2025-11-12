# 🚀 Quick Start Guide

## Get Started in 5 Minutes!

### Step 1: Setup (One-time)

```bash
cd ~/agriculture-rag-platform
./scripts/setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories

### Step 2: Start Ollama (if not running)

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it (in a separate terminal)
ollama serve
```

### Step 3: Run the Platform

```bash
./scripts/run.sh
```

This will:
- Check if Ollama is running
- Initialize the database (first time only - may take 10-30 minutes)
- Start the API server

### Step 4: Use the Platform

**Web Interface:**
Open your browser to: http://localhost:8000

**API Docs:**
http://localhost:8000/docs

**Test Query:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are best practices for maize farming?"}'
```

## 🎯 Example Queries

Try asking:
- "What are the best maize varieties for Zimbabwe?"
- "How do I manage livestock in drought conditions?"
- "Tell me about climate-smart agriculture practices"
- "What are the government policies on agricultural subsidies?"
- "How can I improve my soybean yields?"

## 📁 Project Structure

```
~/agriculture-rag-platform/
├── README.md              ← Full documentation
├── QUICKSTART.md          ← This file
├── requirements.txt       ← Python dependencies
├── config/config.yaml     ← Settings
├── scripts/
│   ├── setup.sh          ← One-time setup
│   ├── run.sh            ← Start the platform
│   └── init_database.py  ← Process documents
├── src/                  ← Source code
├── frontend/             ← Web interface
└── data/vector_db/       ← Vector database
```

## ⚠️ Troubleshooting

**"Ollama is not running"**
```bash
ollama serve
```

**"Module not found"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"No documents found"**
Make sure your PDFs are in:
`/Users/providencemtendereki/Documents/Old Staff/data_raw`

## 🔄 Updating Documents

To add new PDFs or reprocess existing ones:

```bash
source venv/bin/activate
python scripts/init_database.py
```

## 🛑 Stopping the Platform

Press `Ctrl+C` in the terminal where the server is running.

## 📚 Learn More

See [README.md](README.md) for complete documentation.

---

**Need Help?** Check the API docs at http://localhost:8000/docs
