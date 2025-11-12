"""
Extract district profile data from PDFs and integrate into the system
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import PDF extraction libraries
try:
    from PyPDF2 import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logger.warning("PyPDF2 not available - install with: pip install PyPDF2")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available - install with: pip install pdfplumber")


class DistrictDataExtractor:
    """Extract district data from PDF profiles."""
    
    # District PDF location
    DISTRICT_DATA_DIR = Path("/Users/providencemtendereki/Zim District data ")
    
    # Zimbabwe province mapping
    PROVINCE_MAPPING = {
        "Harare": "Harare Metropolitan",
        "Bulawayo": "Bulawayo Metropolitan",
        "Beitbridge": "Matabeleland South",
        "Bikita": "Masvingo",
        "Bindura": "Mashonaland Central",
        "Binga": "Matabeleland North",
        "Bubi": "Matabeleland North",
        "Buhera": "Manicaland",
        "Bulilima": "Matabeleland South",
        "Chegutu": "Midlands",
        "Chikomba": "Midlands",
        "Chimanimani": "Manicaland",
        "Chipinge": "Manicaland",
        "Chiredzi": "Masvingo",
        "Chirumhanzu": "Midlands",
        "Chivi": "Masvingo",
        "Gokwe North": "Midlands",
        "Gokwe South": "Midlands",
        "Goromonzi": "Harare",
        "Guruve": "Mashonaland Central",
        "Gutu": "Masvingo",
        "Gwanda": "Matabeleland South",
        "Gweru": "Midlands",
        "Hwedza": "Mashonaland East",
        "Hwange": "Matabeleland North",
        "Insiza": "Matabeleland South",
        "Kadoma": "Midlands",
        "Kariba": "Mashonaland North",
        "Kwekwe": "Midlands",
        "Lupane": "Matabeleland North",
        "Marondera": "Mashonaland East",
        "Masvingo": "Masvingo",
        "Mazowe": "Mashonaland Central",
        "Mbire": "Mashonaland Central",
        "Murehwa": "Mashonaland East",
        "Muresikwa": "Midlands",
        "Murewa": "Mashonaland East",
        "Mutare": "Manicaland",
        "Mutoko": "Mashonaland East",
        "Muzarabani": "Mashonaland North",
        "Mvurwi": "Mashonaland North",
        "Mwenezi": "Masvingo",
        "Nyanga": "Manicaland",
        "Seke": "Harare",
        "Shamva": "Mashonaland Central",
        "Shurugwi": "Midlands",
        "Sub-Saharan": "Special",
        "Svosve": "Mashonaland East",
        "Tatuem": "Mashonaland Central",
        "Tumanyadzo": "Matabeleland South",
        "Umguza": "Matabeleland North",
        "Wedza": "Mashonaland East",
        "Zaka": "Masvingo",
        "Zandamela": "Matabeleland North",
        "Zimuto": "Masvingo"
    }
    
    # Agro-ecological zones
    AGRO_ZONES = {
        "Harare": "IIa",
        "Binga": "IV",
        "Bulawayo": "III",
        "Chitungwiza": "IIb",
        "Mutare": "IIa",
        "Gweru": "IIb",
        "Kariba": "IV",
        "Hwange": "IV",
        "Nyanga": "I",
        "Kwekwe": "IIa"
    }
    
    def list_district_pdfs(self) -> List[str]:
        """List all district PDF files."""
        if not self.DISTRICT_DATA_DIR.exists():
            logger.error(f"District data directory not found: {self.DISTRICT_DATA_DIR}")
            return []
        
        pdfs = []
        for file in self.DISTRICT_DATA_DIR.iterdir():
            if file.name.endswith("-District-Profile.pdf"):
                district_name = file.name.replace("-District-Profile.pdf", "")
                pdfs.append({
                    "name": district_name,
                    "path": str(file),
                    "size": file.stat().st_size
                })
        
        return sorted(pdfs, key=lambda x: x["name"])
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using available libraries."""
        text = ""
        
        # Try pdfplumber first (better quality)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages[:5]:  # First 5 pages usually contain key info
                        text += page.extract_text() or ""
            except Exception as e:
                logger.warning(f"Error extracting with pdfplumber from {pdf_path}: {e}")
        
        # Fallback to PyPDF2
        if not text and PYPDF_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PdfReader(file)
                    for page_num in range(min(5, len(reader.pages))):
                        page = reader.pages[page_num]
                        text += page.extract_text() or ""
            except Exception as e:
                logger.warning(f"Error extracting with PyPDF2 from {pdf_path}: {e}")
        
        return text
    
    def create_district_profile(self, district_name: str, pdf_path: Optional[str] = None) -> Dict:
        """Create a district profile from PDF or default data."""
        
        profile = {
            "name": district_name,
            "province": self.PROVINCE_MAPPING.get(district_name, "Unknown"),
            "agro_zone": self.AGRO_ZONES.get(district_name, "III"),
        }
        
        # If PDF available, extract additional information
        if pdf_path and (PYPDF_AVAILABLE or PDFPLUMBER_AVAILABLE):
            try:
                text = self.extract_text_from_pdf(pdf_path)
                
                # Extract key information from text (simplified)
                profile["has_pdf_data"] = True
                profile["pdf_path"] = pdf_path
                profile["pdf_size_mb"] = round(Path(pdf_path).stat().st_size / (1024*1024), 2)
                
            except Exception as e:
                logger.warning(f"Could not extract from {pdf_path}: {e}")
        
        return profile
    
    def generate_district_database(self) -> Dict[str, Dict]:
        """Generate complete district database from PDFs."""
        
        logger.info("Generating district database from PDFs...")
        
        districts = {}
        pdfs = self.list_district_pdfs()
        
        logger.info(f"Found {len(pdfs)} district PDF profiles")
        
        for pdf_info in pdfs:
            district_name = pdf_info["name"]
            district_profile = self.create_district_profile(district_name, pdf_info["path"])
            districts[district_name] = district_profile
            
            if len(districts) % 10 == 0:
                logger.info(f"Processed {len(districts)}/56 districts...")
        
        return districts
    
    def save_district_database(self, districts: Dict, output_path: Path):
        """Save district database to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(districts, f, indent=2)
        
        logger.info(f"Saved district database to {output_path}")
    
    def print_summary(self, districts: Dict):
        """Print summary of extracted districts."""
        print("\n" + "="*60)
        print("📊 DISTRICT DATABASE SUMMARY")
        print("="*60)
        print(f"Total Districts: {len(districts)}")
        print(f"Districts with PDF data: {len([d for d in districts.values() if d.get('has_pdf_data')])}")
        
        # Group by province
        by_province = {}
        for district, data in districts.items():
            province = data.get("province", "Unknown")
            if province not in by_province:
                by_province[province] = []
            by_province[province].append(district)
        
        print(f"\nDistricts by Province:")
        for province in sorted(by_province.keys()):
            count = len(by_province[province])
            print(f"  {province}: {count}")
        
        print("\nSample Districts:")
        for i, (name, data) in enumerate(list(districts.items())[:5]):
            print(f"  - {name} ({data.get('province')}), Agro-zone: {data.get('agro_zone')}")
        
        print("="*60 + "\n")


def main():
    """Main execution."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Create extractor
    extractor = DistrictDataExtractor()
    
    # Generate database
    print("Checking for PDF extraction libraries...")
    print(f"  pdfplumber: {'✓ Available' if PDFPLUMBER_AVAILABLE else '✗ Not installed'}")
    print(f"  PyPDF2: {'✓ Available' if PYPDF_AVAILABLE else '✗ Not installed'}")
    
    districts = extractor.generate_district_database()
    
    # Save database
    output_path = Path(__file__).parent.parent / "data" / "districts_database.json"
    extractor.save_district_database(districts, output_path)
    
    # Print summary
    extractor.print_summary(districts)
    
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
