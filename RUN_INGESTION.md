# 🚀 Run Full Document Ingestion - Quick Start

## What This Does

Processes **all 718 PDFs and DOCX files** from your `PDFs data` directory with:
- ✅ **85+ District Profile PDFs** with automatic district extraction
- ✅ **OCR for scanned PDFs** (even image-based PDFs)
- ✅ **DOCX files** ("11 Keys to Achieve 11 Tonnes" series)
- ✅ **Geographic metadata** (districts, provinces, natural regions)
- ✅ **Full-text search** capabilities after ingestion

---

## 🎯 One Command to Run Everything

```bash
./scripts/setup_and_ingest.sh
```

**This will:**
1. Install OCR dependencies (pytesseract, pdf2image, Pillow, python-docx)
2. Install Tesseract OCR engine (brew install tesseract on Mac)
3. Process all 718 documents
4. Extract district/province information
5. Generate embeddings
6. Store everything in vector database

**Time Required:** 1-3 hours

---

## 📊 What You'll Get

### After Completion:
- ✅ **75,000+ document chunks** embedded
- ✅ **50+ districts** tagged and searchable
- ✅ **10 provinces** covered
- ✅ **All natural regions** (I-V) identified
- ✅ **District-specific queries** working perfectly

### Example Queries That Will Work:
```
"What crops are grown in Bindura district?"
"Tell me about Hwange district agriculture"
"Maize farming in Mashonaland East"
"Cattle production in Matabeleland South"
"Best crops for Natural Region IV"
```

---

## 📝 Alternative: Manual Steps

If you prefer to run steps manually:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Install dependencies
pip install pytesseract pdf2image Pillow python-docx
brew install tesseract  # macOS only

# 3. Run ingestion
python scripts/full_ingestion.py

# 4. Verify (after completion)
python scripts/verify_ingestion.py
```

---

## 🎉 After Ingestion

### Start the RAG System:
```bash
uvicorn src.api.main:app --reload
```

### Access Web Interface:
```
http://localhost:8000
```

### Test Your System:
```bash
python scripts/test_retrieval.py
```

---

## 📁 Files Created

**New Scripts:**
- `scripts/full_ingestion.py` - Main ingestion script
- `scripts/setup_and_ingest.sh` - Automated setup
- `src/ingestion/enhanced_processor.py` - Enhanced processor with OCR

**Documentation:**
- `FULL_INGESTION_GUIDE.md` - Comprehensive guide
- `RUN_INGESTION.md` - This quick start
- `DATA_VERIFICATION_REPORT.md` - Current data status

---

## ⚡ Ready to Start?

**Run this command now:**
```bash
./scripts/setup_and_ingest.sh
```

Then wait 1-3 hours while it processes everything. You can monitor progress in the terminal!

---

**Questions?** Check `FULL_INGESTION_GUIDE.md` for detailed information.
