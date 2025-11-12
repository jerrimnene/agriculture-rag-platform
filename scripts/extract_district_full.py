"""
Enhanced District Profile Extraction - Level 3 Processing
Extracts rainfall, soil, crops, yields, markets, and livestock from PDFs
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("Install pdfplumber: pip install pdfplumber")


class DistrictProfileExtractor:
    """Extract full structured data from district profile PDFs."""
    
    DISTRICT_DATA_DIR = Path("/Users/providencemtendereki/Zim District data ")
    OUTPUT_PATH = Path(__file__).parent.parent / "data" / "districts_full.json"
    
    def __init__(self):
        """Initialize extractor."""
        self.extracted_count = 0
        self.error_count = 0
    
    def extract_text_from_pdf(self, pdf_path: str, pages: int = 20) -> str:
        """Extract text from first N pages of PDF."""
        if not PDFPLUMBER_AVAILABLE:
            return ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page_num in range(min(pages, len(pdf.pages))):
                    page_text = pdf.pages[page_num].extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.warning(f"Error extracting PDF {pdf_path}: {e}")
            return ""
    
    def extract_rainfall(self, text: str) -> Dict[str, Any]:
        """Extract rainfall data from text."""
        rainfall = {}
        
        # Look for annual rainfall patterns
        annual_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:mm|millimeters?)\s*(?:annual|per\s+year|p\.a\.)',
            r'annual\s+rainfall[:\s]+(\d+(?:\.\d+)?)\s*mm',
            r'rainfall[:\s]+(\d+(?:\.\d+)?)\s*mm',
            r'(\d+(?:\.\d+)?)\s*mm\s+(?:rain|precipitation)',
        ]
        
        for pattern in annual_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rainfall['annual_mm'] = int(float(match.group(1)))
                    break
                except (ValueError, AttributeError):
                    pass
        
        # Look for seasonal rainfall
        seasonal_patterns = {
            'summer': r'[Ss]ummer[:\s]+(\d+(?:\.\d+)?)\s*mm',
            'winter': r'[Ww]inter[:\s]+(\d+(?:\.\d+)?)\s*mm',
            'rainy': r'[Rr]ainy\s+season[:\s]+(\d+(?:\.\d+)?)\s*mm',
        }
        
        for season, pattern in seasonal_patterns.items():
            match = re.search(pattern, text)
            if match:
                try:
                    rainfall[f'{season}_mm'] = int(float(match.group(1)))
                except (ValueError, AttributeError):
                    pass
        
        return rainfall
    
    def extract_soil_types(self, text: str) -> List[str]:
        """Extract soil type information."""
        soils = []
        
        soil_keywords = [
            'sandy', 'clay', 'loam', 'volcanic', 'ferruginous',
            'laterite', 'sandy loam', 'clay loam', 'silt', 'shallow',
            'deep', 'rocky', 'gravelly', 'calcareous'
        ]
        
        text_lower = text.lower()
        for soil_type in soil_keywords:
            if soil_type in text_lower:
                # Check if it's actually describing soil (not just mentioned)
                pattern = rf'(?:soil|soils)[^.]*\b{re.escape(soil_type)}\b'
                if re.search(pattern, text_lower):
                    soils.append(soil_type)
        
        return list(set(soils))  # Remove duplicates
    
    def extract_crops(self, text: str) -> Dict[str, Any]:
        """Extract crop information and yields."""
        crops = {
            'primary': [],
            'secondary': [],
            'yields': {}
        }
        
        # Common Zimbabwe crops
        crop_keywords = {
            'maize': ['maize', 'corn', 'mealies', 'zea mays'],
            'sorghum': ['sorghum', 'grain sorghum'],
            'millet': ['millet', 'finger millet'],
            'groundnuts': ['groundnuts', 'peanuts', 'arachis'],
            'soybeans': ['soybean', 'soya'],
            'beans': ['bean', 'beans'],
            'tobacco': ['tobacco'],
            'cotton': ['cotton'],
            'vegetables': ['vegetables', 'tomato', 'onion', 'cabbage', 'lettuce'],
            'sugar': ['sugar', 'sugarcane'],
            'wheat': ['wheat'],
        }
        
        text_lower = text.lower()
        
        for crop, keywords in crop_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Check if it's in agricultural context
                    pattern = rf'(?:crop|produce|grown|cultivat|yield)[^.]*\b{re.escape(keyword)}\b'
                    if re.search(pattern, text_lower) or keyword == 'tobacco':
                        if crop not in crops['primary']:
                            crops['primary'].append(crop)
                    break
        
        # Extract yields (tonnes/ha or bags/ha)
        yield_patterns = [
            r'(\w+)\s+(?:yield|production)[:\s]+(\d+(?:\.\d+)?)\s*(?:tonnes?|t/ha|t/ha)',
            r'(\w+)[:\s]+(\d+(?:\.\d+)?)\s*(?:tonnes?|bags?)\s*(?:per\s+hectare|/ha)',
        ]
        
        for pattern in yield_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                crop_name = match.group(1).lower()
                try:
                    yield_val = float(match.group(2))
                    for std_crop, keywords in crop_keywords.items():
                        if any(kw in crop_name for kw in keywords):
                            crops['yields'][std_crop] = yield_val
                            break
                except (ValueError, AttributeError):
                    pass
        
        return crops
    
    def extract_livestock(self, text: str) -> Dict[str, Any]:
        """Extract livestock information."""
        livestock = {
            'types': [],
            'population': {}
        }
        
        livestock_types = ['cattle', 'goats', 'sheep', 'pigs', 'poultry', 'donkeys', 'horses']
        
        text_lower = text.lower()
        for animal in livestock_types:
            if animal in text_lower:
                livestock['types'].append(animal)
        
        # Extract population numbers
        pop_patterns = [
            r'(\w+)\s+population[:\s]+(\d+(?:,\d+)*)',
            r'(?:cattle|goats|sheep|pigs|poultry)[:\s]+(\d+(?:,\d+)*)\s*(?:animals?|heads?)',
        ]
        
        for pattern in pop_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    animal = match.group(1).lower() if 'cattle' not in match.group(0).lower() else 'cattle'
                    pop = int(match.group(2).replace(',', ''))
                    livestock['population'][animal] = pop
                except (ValueError, AttributeError, IndexError):
                    pass
        
        return livestock
    
    def extract_markets(self, text: str) -> Dict[str, Any]:
        """Extract market and trading center information."""
        markets = {
            'trading_centers': [],
            'main_markets': [],
            'commodities': [],
            'market_days': []
        }
        
        # Look for trading center/market names (usually capitalized)
        # Pattern: "[Name] Trading Centre/Market/Growth Point"
        market_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:trading\s+centre?|market|growth\s+point)',
            r'(?:trading\s+centre|market)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in market_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                market_name = match.group(1)
                if len(market_name) > 3 and market_name not in markets['trading_centers']:
                    markets['trading_centers'].append(market_name)
        
        # Extract main commodities traded
        commodity_keywords = ['maize', 'tobacco', 'cotton', 'groundnuts', 'beans', 'vegetables', 'livestock', 'grain']
        text_lower = text.lower()
        for commodity in commodity_keywords:
            if commodity in text_lower:
                if commodity not in markets['commodities']:
                    markets['commodities'].append(commodity)
        
        # Extract market days
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        market_day_pattern = r'(?:market\s+days?|trading\s+days?)[:\s]+([^.]+)'
        match = re.search(market_day_pattern, text, re.IGNORECASE)
        if match:
            day_text = match.group(1)
            for day in days:
                if day.lower() in day_text.lower():
                    markets['market_days'].append(day)
        
        return markets
    
    def extract_population(self, text: str) -> Optional[int]:
        """Extract district population."""
        patterns = [
            r'population[:\s]+(\d+(?:,\d+)*)',
            r'(?:district\s+)?population\s+(?:is|of)[:\s]*(\d+(?:,\d+)*)',
            r'(\d+(?:,\d+)*)\s+(?:people|inhabitants|population)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(',', ''))
                except (ValueError, AttributeError):
                    pass
        
        return None
    
    def extract_vulnerabilities(self, text: str) -> List[str]:
        """Extract vulnerability/risk information."""
        vulnerabilities = []
        
        risk_keywords = {
            'drought': ['drought', 'dry spell', 'water stress'],
            'flood': ['flood', 'waterlog', 'excessive rain'],
            'crop_failure': ['crop failure', 'crop loss'],
            'pest': ['pest', 'pests', 'infestation'],
            'disease': ['disease', 'malaria', 'cholera'],
            'food_insecurity': ['food insecurity', 'hunger', 'food shortage'],
            'poverty': ['poverty', 'poor', 'impoverish'],
        }
        
        text_lower = text.lower()
        for risk, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    vulnerabilities.append(risk)
                    break
        
        return list(set(vulnerabilities))
    
    def extract_district_profile(self, district_name: str, pdf_path: str) -> Dict[str, Any]:
        """Extract complete district profile from PDF."""
        
        logger.info(f"Processing {district_name}...")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"Could not extract text from {pdf_path}")
            return {}
        
        profile = {
            "name": district_name,
            "pdf_path": pdf_path,
            "rainfall": self.extract_rainfall(text),
            "soil_types": self.extract_soil_types(text),
            "crops": self.extract_crops(text),
            "livestock": self.extract_livestock(text),
            "markets": self.extract_markets(text),
            "population": self.extract_population(text),
            "vulnerabilities": self.extract_vulnerabilities(text),
        }
        
        return profile
    
    def list_district_pdfs(self) -> List[Dict]:
        """List all district PDF files."""
        if not self.DISTRICT_DATA_DIR.exists():
            logger.error(f"Directory not found: {self.DISTRICT_DATA_DIR}")
            return []
        
        pdfs = []
        for file in sorted(self.DISTRICT_DATA_DIR.iterdir()):
            if file.name.endswith("-District-Profile.pdf"):
                district_name = file.name.replace("-District-Profile.pdf", "")
                pdfs.append({
                    "name": district_name,
                    "path": str(file)
                })
        
        return pdfs
    
    def process_all_districts(self) -> Dict[str, Dict]:
        """Process all district PDFs."""
        
        if not PDFPLUMBER_AVAILABLE:
            logger.error("pdfplumber not available. Install with: pip install pdfplumber")
            return {}
        
        districts = {}
        pdfs = self.list_district_pdfs()
        
        logger.info(f"Found {len(pdfs)} district PDFs")
        
        for idx, pdf_info in enumerate(pdfs, 1):
            try:
                profile = self.extract_district_profile(pdf_info["name"], pdf_info["path"])
                if profile:
                    districts[pdf_info["name"]] = profile
                    self.extracted_count += 1
                    
                    if idx % 10 == 0:
                        logger.info(f"Processed {idx}/{len(pdfs)} districts...")
            except Exception as e:
                logger.error(f"Error processing {pdf_info['name']}: {e}")
                self.error_count += 1
        
        return districts
    
    def merge_with_existing(self, new_data: Dict, existing_path: Path) -> Dict:
        """Merge new extracted data with existing database."""
        merged = {}
        
        # Load existing data
        if existing_path.exists():
            try:
                with open(existing_path, 'r') as f:
                    merged = json.load(f)
                logger.info(f"Loaded {len(merged)} existing districts")
            except Exception as e:
                logger.warning(f"Could not load existing data: {e}")
        
        # Merge with new data (new data takes precedence)
        for district, data in new_data.items():
            if district in merged:
                # Merge: keep existing basic data, add new extracted data
                for key, value in data.items():
                    if value and (key not in merged[district] or not merged[district][key]):
                        merged[district][key] = value
            else:
                merged[district] = data
        
        return merged
    
    def save_database(self, data: Dict, output_path: Path):
        """Save database to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(data)} districts to {output_path}")
    
    def print_sample(self, data: Dict):
        """Print sample of extracted data."""
        print("\n" + "="*70)
        print("📊 SAMPLE EXTRACTED DATA (First District)")
        print("="*70)
        
        first_district = list(data.values())[0] if data else None
        if first_district:
            print(json.dumps(first_district, indent=2)[:1000])
            print("...")
        
        print("\n" + "="*70)
        print("📈 EXTRACTION SUMMARY")
        print("="*70)
        print(f"Total districts: {len(data)}")
        print(f"Successfully extracted: {self.extracted_count}")
        print(f"Errors: {self.error_count}")
        
        # Count what was extracted
        with_rainfall = len([d for d in data.values() if d.get('rainfall', {}).get('annual_mm')])
        with_crops = len([d for d in data.values() if d.get('crops', {}).get('primary')])
        with_markets = len([d for d in data.values() if d.get('markets', {}).get('trading_centers')])
        
        print(f"\nData extracted:")
        print(f"  ✅ Rainfall data: {with_rainfall}/{len(data)} districts")
        print(f"  ✅ Crop data: {with_crops}/{len(data)} districts")
        print(f"  ✅ Market data: {with_markets}/{len(data)} districts")
        print("="*70 + "\n")


def main():
    """Main execution."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    print("\n🚀 Starting Enhanced District Profile Extraction (Level 3)...\n")
    
    # Check dependencies
    print("Checking dependencies...")
    print(f"  pdfplumber: {'✓ Available' if PDFPLUMBER_AVAILABLE else '✗ Not installed'}")
    
    if not PDFPLUMBER_AVAILABLE:
        print("\n⚠️  Installing pdfplumber...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber"], check=False)
        logger.info("pdfplumber installed. Please run this script again.")
        return
    
    # Create extractor
    extractor = DistrictProfileExtractor()
    
    # Process all districts
    print(f"\n📂 Reading from: {extractor.DISTRICT_DATA_DIR}")
    districts_data = extractor.process_all_districts()
    
    # Merge with existing
    existing_db = Path(__file__).parent.parent / "data" / "districts_database.json"
    merged_data = extractor.merge_with_existing(districts_data, existing_db)
    
    # Save
    extractor.save_database(merged_data, extractor.OUTPUT_PATH)
    
    # Print summary
    extractor.print_sample(merged_data)
    
    return extractor.OUTPUT_PATH


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
