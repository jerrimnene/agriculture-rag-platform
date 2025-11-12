# 🌾 Hupfumi.Africa's Earth Evidence AI

**Where the land speaks, data listens, and wisdom decides.**

Hupfumi.Africa is Zimbabwe's first **Earth Evidence AI** — an Ancestral Intelligence ecosystem that unites traditional wisdom, ecological data, and modern analytics to drive agricultural prosperity from soil to soul.

This sovereign intelligence platform provides evidence-backed guidance rooted in Zimbabwe's natural regions, climate patterns, soil characteristics, and time-tested agricultural practices. Built on an **Agentic Retrieval-Augmented Generation (RAG)** architecture, it connects farmers, extension officers, and policymakers to comprehensive knowledge including crop production guides, livestock management, policy frameworks, climate-smart practices, and food security assessments.

## 🎯 Features

### Core Platform
- **Agentic RAG System**: Intelligent document retrieval with multiple search strategies
- **Local LLM**: Uses Mistral via Ollama for privacy and cost-effectiveness
- **Semantic Search**: Vector-based similarity search using ChromaDB
- **Category Filtering**: Search within specific domains (crops, livestock, policy, etc.)
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Web Interface**: Clean, user-friendly chat interface
- **Comprehensive Knowledge Base**: Processes PDFs on:
  - Crop production (maize, soya, sugar beans, hot peppers, etc.)
  - Livestock management (cattle, goats, pigs, poultry, fish)
  - Agricultural policies and frameworks
  - Climate-smart agriculture
  - Market linkages and value chains
  - Food security assessments

### Advanced Features (Phase 1-3)
- **📚 Enhanced Citations**: Show source organization, document name, and PDF links
- **🎯 Confidence Scoring**: 0-100 trust rating based on source quality, recency, and agreement
- **🌍 Local Language Support**: Auto-generate Shona/Ndebele summaries with agricultural glossary
- **🌐 Web Scraping**: Pull latest data from international sources (World Bank, FAO, USAID, etc.)
- **📊 Export Market Intelligence**: Comprehensive market data for 5 major Zimbabwe crops
- **👥 Farmer Profiles**: Gender/youth segmentation with personalized program recommendations
- **⚖️ Multi-Source Reconciliation**: Automatically detect and resolve conflicting expert recommendations

## 🏗️ Architecture

```
agriculture-rag-platform/
├── src/
│   ├── ingestion/           # Document processing pipeline
│   │   └── document_processor.py
│   ├── embeddings/          # Vector store and embeddings
│   │   └── vector_store.py
│   ├── agents/              # Agentic RAG system
│   │   └── rag_agent.py
│   └── api/                 # FastAPI application
│       └── main.py
├── data/
│   ├── raw/                 # Original PDF documents
│   ├── processed/           # Processed documents
│   └── vector_db/           # ChromaDB vector store
├── config/
│   └── config.yaml          # Configuration file
├── frontend/
│   └── index.html           # Web interface
├── scripts/
│   ├── setup.sh             # Setup script
│   ├── run.sh               # Startup script
│   └── init_database.py     # Database initialization
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- 8GB+ RAM recommended

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd ~/agriculture-rag-platform
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x scripts/*.sh
   ```

3. **Run setup:**
   ```bash
   ./scripts/setup.sh
   ```

4. **Make sure Ollama is running with Mistral:**
   ```bash
   # In a separate terminal
   ollama serve
   ```

5. **Initialize the database (first time only):**
   ```bash
   source venv/bin/activate
   python scripts/init_database.py
   ```
   
   This will:
   - Process all PDF documents from your data directory
   - Extract and chunk text
   - Generate embeddings
   - Store in ChromaDB vector database
   - May take 10-30 minutes depending on document count

6. **Start the platform:**
   ```bash
   ./scripts/run.sh
   ```

7. **Access the platform:**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📖 Usage

### Web Interface

1. Open http://localhost:8000 in your browser
2. Type your agricultural question in the chat input
3. Click "Send" or press Enter
4. Get detailed, citation-backed responses

**Example Questions:**
- "What are the best practices for maize cultivation in Zimbabwe?"
- "How can I implement climate-smart agriculture techniques?"
- "What are the requirements for cattle farming?"
- "Tell me about soybean production guidelines"

### API Usage

#### Query Endpoint

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the best maize varieties for Zimbabwe?"}'
```

#### Search Endpoint

```bash
curl "http://localhost:8000/search?q=maize+farming&top_k=5"
```

#### Category-Specific Search

```bash
curl "http://localhost:8000/search?q=cattle+management&category=livestock"
```

#### Get Categories

```bash
curl "http://localhost:8000/categories"
```

### Python SDK Example

```python
import requests

# Query the knowledge base
response = requests.post(
    "http://localhost:8000/query",
    json={"query": "How to manage maize pests?"}
)

result = response.json()
print(result['response'])
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
# Vector store settings
embeddings:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_size: 1000
  chunk_overlap: 200

# LLM settings
llm:
  provider: "ollama"
  model: "mistral"
  base_url: "http://localhost:11434"

# Retrieval settings
retrieval:
  top_k: 5
  score_threshold: 0.7
```

## 🔧 Advanced Features

### Multi-Source Reconciliation (Phase 3)

**Automatically detects when expert sources disagree** and provides balanced recommendations:

```python
result = agent.query(
    "When should I plant maize?",
    district="Harare"
)

# Check for conflicts
if result['reconciliation']['has_conflicts']:
    print("⚠️ Expert sources disagree:")
    for conflict in result['reconciliation']['conflicts']:
        print(conflict['display'])
else:
    print("✅ All sources agree")
```

**Features:**
- Authority scoring (AGRITEX, ICRISAT, FAO, etc.)
- Geographic specificity bonus (+20 for Zimbabwe-specific)
- Recency weighting (prefer current data)
- Conflict types: timing, quantity, method, safety warnings
- Transparent display of disagreements
- Weighted consensus recommendations

**See**: `docs/RECONCILIATION_GUIDE.md` for detailed usage

### Farmer Profile System

**Track farmer demographics for personalized recommendations:**

```python
from src.user.farmer_profile import FarmerProfileManager

manager = FarmerProfileManager()
profile = manager.create_profile(
    user_id="farmer_001",
    name="John Moyo",
    age=28,
    gender="male",
    farm_size="small",
    hectares=3.5,
    district="Harare",
    primary_crops=["maize", "beans"],
    language_preference="shona"
)

# Get personalized recommendations
engine = PersonalizationEngine()
programs = engine.get_relevant_programs(profile)
```

### Export Market Intelligence

**Comprehensive market data for major crops:**

```python
from src.markets.export_intelligence import ExportIntelligence

intel = ExportIntelligence()

# Get tobacco export data
tobacco_data = intel.get_crop_export_data("tobacco")
print(f"Export value: ${tobacco_data['annual_export_value']}")
print(f"Top destination: {tobacco_data['destinations'][0]['country']}")

# Compare markets
comparison = intel.compare_markets(["tobacco", "macadamia"])
```

### Custom Document Categories

Documents are automatically categorized based on filename patterns:
- **crop**: maize, soya, beans, peppers, grains
- **livestock**: cattle, goats, pigs, poultry, fish
- **policy**: policy, framework, strategy
- **climate**: climate, CSA, IPCC
- **market**: market, value-chain
- **food_security**: assessments, livelihoods

### Multi-Query Search

The agent can automatically generate query variations for comprehensive results:

```python
from src.agents.rag_agent import AgricultureRAGAgent
from src.embeddings.vector_store import VectorStore

vector_store = VectorStore(persist_directory="./data/vector_db")
agent = AgricultureRAGAgent(vector_store)

result = agent.query("Best maize farming practices")
print(result['response'])
```

## 🐛 Troubleshooting

### Ollama Connection Error
```bash
# Make sure Ollama is running
ollama serve

# Check if Mistral is available
ollama list

# Pull Mistral if needed
ollama pull mistral
```

### Empty Vector Database
```bash
# Reinitialize the database
python scripts/init_database.py
```

### Import Errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Change the port in config/config.yaml
api:
  port: 8001  # Use different port
```

## 📊 Performance

- **Document Processing**: ~1-2 seconds per PDF
- **Query Response Time**: 2-5 seconds (depends on LLM)
- **Embedding Generation**: ~100 chunks per second
- **Memory Usage**: ~2-4GB during operation

## 🔐 Security Notes

- This platform is designed for local use
- All data stays on your machine
- No external API calls (except to local Ollama)
- Suitable for sensitive agricultural data

## 🤝 Contributing

To add more documents:
1. Place PDF files in `/Users/providencemtendereki/Documents/Old Staff/data_raw`
2. Run: `python scripts/init_database.py` to reindex

## 📝 License

This project is created for agricultural knowledge sharing in Zimbabwe.

## 🙏 Acknowledgments

Built with:
- **Ollama & Mistral**: Local LLM inference
- **LangChain**: Agent framework
- **ChromaDB**: Vector database
- **Sentence Transformers**: Embeddings
- **FastAPI**: Web framework

---

**Project Location**: `/Users/providencemtendereki/agriculture-rag-platform`

**Data Source**: `/Users/providencemtendereki/Documents/Old Staff/data_raw`

For questions or issues, please check the logs or API documentation at http://localhost:8000/docs
