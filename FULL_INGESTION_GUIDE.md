# Full Document Ingestion Guide

## Overview

This guide will help you process and embed **all 718 documents** (PDFs and DOCX files) from your `PDFs data` directory into the RAG system with:
- ✅ Automatic district/province extraction
- ✅ OCR support for scanned PDFs
- ✅ DOCX file processing
- ✅ Geographic metadata tagging
- ✅ Comprehensive text extraction

---

## What Will Be Processed

### Files to Process: **718 Total**
- **PDFs:** ~700+ files
  - District Profile PDFs (85+)
  - Policy documents
  - Agricultural guides
  - Research reports
  - Scanned documents (will use OCR)
  
- **DOCX:** ~15+ files
  - "11 Keys to Achieve 11 Tonnes" series
  - Other Word documents

### Geographic Coverage
The system will automatically extract and tag:
- **50+ Districts** (Bindura, Hwange, Mutare, Gweru, Masvingo, etc.)
- **10 Provinces** (All Zimbabwe provinces)
- **5 Natural Regions** (Regions I-V)

---

## Quick Start - Run Everything Automatically

### Option 1: Single Command (Recommended)

```bash
./scripts/setup_and_ingest.sh
```

This will:
1. ✅ Activate virtual environment
2. ✅ Install OCR dependencies (pytesseract, pdf2image, Pillow, python-docx)
3. ✅ Install Tesseract OCR engine
4. ✅ Process all 718 files
5. ✅ Extract district/province information
6. ✅ Generate embeddings
7. ✅ Store in vector database

**Expected Time:** 1-3 hours (depending on your machine)

---

## Manual Step-by-Step Process

### Step 1: Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install Python packages
pip install pytesseract pdf2image Pillow python-docx

# Install Tesseract OCR engine
# macOS:
brew install tesseract

# Linux:
sudo apt install tesseract-ocr
```

### Step 2: Verify Installation

```bash
# Test enhanced processor
python src/ingestion/enhanced_processor.py
```

This will test processing on a few sample district profile PDFs.

### Step 3: Run Full Ingestion

```bash
source venv/bin/activate
python scripts/full_ingestion.py
```

### Step 4: Monitor Progress

The script will show:
- Files being processed (with progress bar)
- Districts/provinces found in each document
- Chunk creation statistics
- Embedding generation progress
- Final statistics

---

## What Happens During Ingestion

### Phase 1: Document Processing (30-90 min)
```
Processing documents...
├── Extract text from PDFs
├── Apply OCR to scanned PDFs (slower)
├── Extract text from DOCX files
├── Clean and normalize text
├── Extract district/province names
├── Chunk documents (1000 words per chunk)
└── Tag with metadata
```

### Phase 2: Embedding Generation (30-60 min)
```
Generating embeddings...
├── Load sentence-transformer model
├── Convert text chunks to 384-dim vectors
├── Store in ChromaDB
└── Build search index
```

### Phase 3: Verification (1 min)
```
Testing retrieval...
├── Run sample queries
├── Verify district-specific retrieval
├── Check geographic metadata
└── Generate statistics report
```

---

## Expected Output

### During Processing
```
INFO: Processing: Bindura-District-Profile.pdf
INFO: Created 45 chunks from Bindura-District-Profile.pdf
INFO:   Districts found: Bindura
INFO:   Provinces found: Mashonaland Central
```

### Final Statistics
```
🎉 INGESTION COMPLETE!
================================================================================
⏱️  Total Time: 2h 15m 30s
📊 Documents before: 6,514
📊 Documents after: 85,230
📊 New documents added: 78,716
📁 Source files processed: 718
🗺️  Districts covered: 52
🗺️  Provinces covered: 10
🗺️  Natural Regions: 5
📂 Categories: crop, livestock, policy, district_profile, climate, general
🔍 Embedding Model: sentence-transformers/all-MiniLM-L6-v2
💾 Vector DB Location: data/vector_db/
================================================================================
```

### Sample Test Results
```
🔍 Query: 'Bindura district agriculture'
   ✓ Top result: Bindura-District-Profile.pdf
   📍 Districts: Bindura
   📍 Provinces: Mashonaland Central
   📄 Preview: Bindura District is located in Mashonaland Central Province...
```

---

## What Gets Extracted

### Metadata for Each Document Chunk
```python
{
    'filename': 'Bindura-District-Profile.pdf',
    'category': 'district_profile',
    'districts': ['Bindura'],
    'provinces': ['Mashonaland Central'],
    'natural_regions': ['Region II'],
    'chunk_index': 0,
    'total_words': 1000
}
```

### Geographic Entities Detected
- **Districts:** Extracted from filename and content
- **Provinces:** Matched against Zimbabwe's 10 provinces
- **Natural Regions:** I, II, IIa, IIb, III, IV, V
- **Cities:** Harare, Bulawayo, Mutare, etc.

---

## Troubleshooting

### OCR Issues
If you see "OCR libraries not available":
```bash
pip install pytesseract pdf2image Pillow
brew install tesseract  # macOS
```

### DOCX Issues
If DOCX files fail to process:
```bash
pip install python-docx
```

### Memory Issues
If processing fails due to memory:
- Process in batches (edit `full_ingestion.py` to limit files)
- Close other applications
- Consider processing overnight

### Slow Processing
- OCR is CPU-intensive (scanned PDFs take longer)
- Large files (33MB+) take more time
- Progress bar shows estimated completion time

---

## After Ingestion

### 1. Verify Data
```bash
python scripts/verify_ingestion.py
```

### 2. Test Retrieval
```bash
python scripts/test_retrieval.py
```

### 3. Start API Server
```bash
uvicorn src.api.main:app --reload
```

### 4. Access Web Interface
Open: http://localhost:8000

---

## Query Examples After Ingestion

### District-Specific Queries
```
"What crops are grown in Bindura district?"
"Tell me about Hwange district agriculture"
"Climate conditions in Masvingo district"
```

### Province-Level Queries
```
"Maize farming in Mashonaland East"
"Cattle production in Matabeleland"
"Agricultural activities in Manicaland"
```

### Natural Region Queries
```
"Best crops for Natural Region IV"
"Livestock suitable for Region V"
"Farming practices in Region II"
```

### Crop/Livestock Queries
```
"Maize varieties for drought areas"
"Cattle breeds for low rainfall regions"
"Wheat irrigation requirements"
```

---

## File Structure After Ingestion

```
agriculture-rag-platform/
├── data/
│   ├── vector_db/
│   │   ├── chroma.sqlite3          (Large - 500MB+)
│   │   └── 7361b851.../            (Embeddings)
│   └── raw/
│       └── zimbabwe_regional_agriculture.json
├── src/
│   └── ingestion/
│       ├── enhanced_processor.py    (New - OCR support)
│       └── document_processor.py    (Original)
└── scripts/
    ├── full_ingestion.py           (New - Main script)
    ├── setup_and_ingest.sh         (New - Auto setup)
    └── verify_ingestion.py         (Verification)
```

---

## Performance Benchmarks

### Processing Speed (Approximate)
- **Text PDFs:** ~2-5 seconds per file
- **Scanned PDFs (OCR):** ~30-60 seconds per file
- **DOCX files:** ~1-2 seconds per file
- **Embedding generation:** ~100 chunks per second

### Database Size
- **Before:** 251 MB (6,514 chunks)
- **After:** ~500-700 MB (85,000+ chunks)

### Memory Usage
- **Peak RAM:** 4-6 GB during embedding generation
- **Disk Space:** 700+ MB for vector database

---

## Success Criteria

✅ All 718 files processed without fatal errors  
✅ 50+ districts identified and tagged  
✅ 10 provinces covered  
✅ 75,000+ document chunks created  
✅ District-specific queries return relevant results  
✅ Geographic metadata properly extracted  

---

## Next Steps

1. **Run the ingestion:**
   ```bash
   ./scripts/setup_and_ingest.sh
   ```

2. **Wait for completion** (1-3 hours)

3. **Verify results:**
   ```bash
   python scripts/verify_ingestion.py
   ```

4. **Start using the system:**
   ```bash
   uvicorn src.api.main:app --reload
   ```

5. **Test queries** about specific districts!

---

## Support

If you encounter issues:
1. Check the log output for specific errors
2. Verify all dependencies are installed
3. Ensure sufficient disk space (1GB+)
4. Make sure Tesseract is installed for OCR

---

**Ready to process all 718 documents with full district/province extraction!** 🚀
