#!/bin/bash
#
# Setup and Full Ingestion Script
# This script installs dependencies and runs the full ingestion process
#

echo "========================================="
echo "Agriculture RAG - Setup & Full Ingestion"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

echo -e "\n${YELLOW}Step 1: Activating virtual environment...${NC}"
source venv/bin/activate || {
    echo -e "${RED}Failed to activate virtual environment${NC}"
    exit 1
}

echo -e "\n${YELLOW}Step 2: Installing OCR and DOCX dependencies...${NC}"
pip install -q pytesseract pdf2image Pillow python-docx || {
    echo -e "${RED}Failed to install Python packages${NC}"
    exit 1
}

echo -e "\n${YELLOW}Step 3: Checking for Tesseract OCR...${NC}"
if ! command -v tesseract &> /dev/null; then
    echo -e "${YELLOW}Tesseract not found. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install tesseract
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y tesseract-ocr
    else
        echo -e "${RED}Please install Tesseract manually:${NC}"
        echo "  macOS: brew install tesseract"
        echo "  Linux: sudo apt install tesseract-ocr"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Tesseract already installed${NC}"
fi

echo -e "\n${YELLOW}Step 4: Starting full ingestion process...${NC}"
echo -e "${YELLOW}This will process all 718 files and may take 1-3 hours${NC}"
echo -e "${YELLOW}Press Ctrl+C to cancel${NC}\n"

sleep 3

python scripts/full_ingestion.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo -e "\n${GREEN}=========================================${NC}"
    echo -e "${GREEN}✓ Ingestion completed successfully!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo -e "\n${GREEN}You can now start the RAG system:${NC}"
    echo -e "  uvicorn src.api.main:app --reload"
else
    echo -e "\n${RED}=========================================${NC}"
    echo -e "${RED}✗ Ingestion failed with exit code $exit_code${NC}"
    echo -e "${RED}=========================================${NC}"
fi

exit $exit_code
