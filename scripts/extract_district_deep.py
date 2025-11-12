"""
Deep District Profile Extraction - Professional Grade Level 3
Extracts rainfall, soil, crops, yields, markets from ALL pages with multiple strategies
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class DeepDistrictExtractor:
    """Deep extraction from district profile PDFs."""
    
    DISTRICT_DATA_DIR = Path("/Users/providencemtendereki/Zim District data ")
    OUTPUT_PATH = Path(__file__).parent.parent / "data" / "districts_deep.json"
    
    def __init__(self):
        self.extracted_count = 0
        self.error_count = 0
    
    def extract_all_text(self, pdf_path: str) -> str:
        """Extract text from ALL pages of PDF."""
        if not PDFPLUMBER_AVAILABLE:
            return ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
                return text
        except Exception as e:
            logger.warning(f"Error extracting PDF {pdf_path}: {e}")
            return ""
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """Extract tables from PDF - often contain rainfall, yields data."""
        if not PDFPLUMBER_AVAILABLE:
            return []
        
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_idx, table in enumerate(page_tables):
                            tables.append({
                                'page': page_num + 1,
                                'table_index': table_idx,
                                'data': table
                            })
        except Exception as e:
            logger.warning(f"Error extracting tables from {pdf_path}: {e}")
        
        return tables
    
    def extract_rainfall_deep(self, text: str, tables: List[Dict]) -> Dict[str, Any]:
        """Deep rainfall extraction from text AND tables."""
        rainfall = {}
        
        # Strategy 1: Direct text patterns
        text_patterns = [
            r'(?:mean\s+)?annual\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)',
            r'rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)\s*(?:per\s+annum|annually|p\.a\.)',
            r'(\d+(?:\.\d+)?)\s*mm\s+(?:annual|yearly)',
            r'average\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*mm',
            r'(?:Total\s+)?rainfall[:\s]*(\d+(?:\.\d+)?)\s*mm',
        ]
        
        for pattern in text_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    rainfall['annual_mm'] = int(float(matches[0]))
                    logger.debug(f"Found rainfall from text: {rainfall['annual_mm']}mm")
                    break
                except (ValueError, IndexError):
                    pass
        
        # Strategy 2: Look in tables for rainfall columns
        for table_info in tables:
            table = table_info['data']
            if not table or len(table) < 2:
                continue
            
            # Look for rainfall-like headers and values
            for row_idx, row in enumerate(table):
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                
                # Check if row header contains rainfall keywords
                if any(kw in row_str for kw in ['rainfall', 'precipitation', 'rain', 'mm']):
                    # Try to find numerical values in this row
                    for cell in row:
                        if cell:
                            nums = re.findall(r'\d+(?:\.\d+)?', str(cell))
                            if nums:
                                try:
                                    val = int(float(nums[0]))
                                    if 100 < val < 2000:  # Reasonable rainfall range
                                        rainfall['annual_mm'] = val
                                        logger.debug(f"Found rainfall from table: {val}mm")
                                        break
                                except ValueError:
                                    pass
        
        # Strategy 3: Seasonal rainfall patterns
        seasonal_patterns = {
            'summer': [
                r'[Ss]ummer\s+(?:rainfall|rain)[:\s]*(\d+(?:\.\d+)?)\s*mm',
                r'Nov\w*\s*-\s*Mar\w*[:\s]*(\d+(?:\.\d+)?)\s*mm',
            ],
            'winter': [
                r'[Ww]inter\s+(?:rainfall|rain)[:\s]*(\d+(?:\.\d+)?)\s*mm',
                r'Apr\w*\s*-\s*Oct\w*[:\s]*(\d+(?:\.\d+)?)\s*mm',
            ],
            'rainy_season': [
                r'[Rr]ainy\s+season[:\s]*(\d+(?:\.\d+)?)\s*mm',
            ]
        }
        
        for season, patterns in seasonal_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        rainfall[f'{season}_mm'] = int(float(match.group(1)))
                    except (ValueError, AttributeError):
                        pass
        
        return rainfall
    
    def extract_yields_deep(self, text: str, tables: List[Dict]) -> Dict[str, float]:
        """Deep crop yield extraction from text AND tables."""
        yields = {}
        
        # Crop keywords
        crops = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco', 'cotton', 
                 'soybeans', 'wheat', 'rice', 'sunflower', 'vegetables']
        
        # Strategy 1: Text patterns for yields
        yield_patterns = [
            r'(\w+)\s+(?:yield|production)[:\s]*(\d+(?:\.\d+)?)\s*(?:tonnes?|t)(?:\s*/?ha)?',
            r'(\w+)[:\s]*(\d+(?:\.\d+)?)\s*(?:tonnes?|t)\s*(?:per\s+hectare|/ha)',
            r'(?:average\s+)?(\w+)\s+yield[:\s]*(\d+(?:\.\d+)?)\s*(?:t/ha|tonnes?/ha)',
        ]
        
        for pattern in yield_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                crop_name = match.group(1).lower()
                try:
                    yield_val = float(match.group(2))
                    # Match to standard crop names
                    for std_crop in crops:
                        if std_crop in crop_name or crop_name in std_crop:
                            if std_crop not in yields or yield_val > yields[std_crop]:
                                yields[std_crop] = yield_val
                            logger.debug(f"Found yield - {std_crop}: {yield_val} t/ha")
                            break
                except (ValueError, AttributeError):
                    pass
        
        # Strategy 2: Extract yields from tables
        for table_info in tables:
            table = table_info['data']
            if not table or len(table) < 2:
                continue
            
            # Look for yield-like rows
            for row_idx, row in enumerate(table):
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                
                # Check if row contains yield/production keywords
                if any(kw in row_str for kw in ['yield', 'production', 't/ha', 'tonnes']):
                    # First cell usually has crop name
                    if row and row[0]:
                        crop_name = str(row[0]).lower()
                        # Look for numeric values in rest of row
                        for cell in row[1:]:
                            if cell:
                                nums = re.findall(r'\d+(?:\.\d+)?', str(cell))
                                if nums:
                                    try:
                                        val = float(nums[0])
                                        if 0.1 < val < 50:  # Reasonable yield range
                                            for std_crop in crops:
                                                if std_crop in crop_name:
                                                    yields[std_crop] = val
                                                    logger.debug(f"Found yield in table - {std_crop}: {val}")
                                                    break
                                            break
                                    except ValueError:
                                        pass
        
        return yields
    
    def extract_soil_deep(self, text: str, tables: List[Dict]) -> List[str]:
        """Deep soil extraction."""
        soils = set()
        
        soil_patterns = [
            r'soil\s+type[:\s]*([^.\n]+)',
            r'soils[:\s]*([^.\n]+)',
            r'dominant\s+soils?[:\s]*([^.\n]+)',
            r'(?:the\s+)?district\s+(?:has\s+)?(?:predominantly\s+)?([a-z\s]+?)\s+soils?',
        ]
        
        soil_keywords = ['sandy', 'clay', 'loam', 'volcanic', 'laterite', 'ferruginous', 
                        'shallow', 'deep', 'rocky', 'gravelly', 'silt', 'calcareous']
        
        # Text extraction
        for pattern in soil_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                soil_text = match.group(1).lower()
                for keyword in soil_keywords:
                    if keyword in soil_text:
                        soils.add(keyword)
        
        # Table extraction
        for table_info in tables:
            table = table_info['data']
            if not table:
                continue
            
            for row in table:
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                if 'soil' in row_str:
                    for keyword in soil_keywords:
                        if keyword in row_str:
                            soils.add(keyword)
        
        return list(soils)
    
    def extract_markets_deep(self, text: str) -> Dict[str, Any]:
        """Deep market extraction."""
        markets = {
            'trading_centers': [],
            'commodities': [],
            'market_days': []
        }
        
        # Market patterns - look for capitalized names
        market_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:trading\s+centre?|market|growth\s+point)',
            r'(?:trading\s+centre|market|trading\s+center)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:main\s+)?market(?:s)?[:\s]*([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*)',
        ]
        
        for pattern in market_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                market_name = match.group(1)
                if len(market_name) > 3:
                    markets['trading_centers'].append(market_name)
        
        # Remove duplicates
        markets['trading_centers'] = list(set(markets['trading_centers']))
        
        # Commodities
        commodity_keywords = ['maize', 'tobacco', 'cotton', 'groundnuts', 'beans', 
                             'vegetables', 'livestock', 'grain', 'sugar', 'sunflower']
        for commodity in commodity_keywords:
            if commodity in text.lower():
                markets['commodities'].append(commodity)
        
        markets['commodities'] = list(set(markets['commodities']))
        
        # Market days
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_pattern = r'(?:market\s+days?|trading\s+days?)[:\s]+([^.\n]+)'
        match = re.search(day_pattern, text, re.IGNORECASE)
        if match:
            day_text = match.group(1)
            for day in days:
                if day.lower() in day_text.lower():
                    markets['market_days'].append(day)
        
        return markets
    
    def extract_crops_deep(self, text: str, tables: List[Dict]) -> Dict[str, Any]:
        """Deep crop extraction."""
        crops = {
            'primary': [],
            'secondary': [],
            'yields': {}
        }
        
        crop_keywords = {
            'maize': ['maize', 'corn', 'mealies'],
            'sorghum': ['sorghum'],
            'millet': ['millet'],
            'groundnuts': ['groundnuts', 'peanuts'],
            'beans': ['beans', 'bean'],
            'tobacco': ['tobacco'],
            'cotton': ['cotton'],
            'soybeans': ['soybean', 'soya'],
            'vegetables': ['vegetables', 'tomato', 'onion', 'cabbage'],
            'wheat': ['wheat'],
            'sunflower': ['sunflower'],
        }
        
        text_lower = text.lower()
        
        # Extract from text
        for crop, keywords in crop_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    pattern = rf'(?:crop|produce|grown|cultivat|yield|agric)[^.]*\b{re.escape(keyword)}\b'
                    if re.search(pattern, text_lower):
                        crops['primary'].append(crop)
                        break
        
        # Extract yields
        yields = self.extract_yields_deep(text, tables)
        crops['yields'] = yields
        
        # Remove duplicates
        crops['primary'] = list(set(crops['primary']))
        
        return crops
    
    def extract_population_deep(self, text: str, tables: List[Dict]) -> Optional[int]:
        """Deep population extraction."""
        patterns = [
            r'population[:\s]*(\d+(?:,\d+)*)\s*(?:people|inhabitants)?',
            r'(?:district\s+)?population\s+(?:is|of|=)[:\s]*(\d+(?:,\d+)*)',
            r'(\d+(?:,\d+)*)\s+(?:people|inhabitants|population)',
            r'population\s+density[:\s]*(\d+(?:,\d+)*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(',', ''))
                except (ValueError, AttributeError):
                    pass
        
        # Try tables
        for table_info in tables:
            table = table_info['data']
            if not table:
                continue
            
            for row in table:
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                if 'population' in row_str:
                    for cell in row:
                        if cell:
                            nums = re.findall(r'\d+(?:,\d+)*', str(cell))
                            if nums:
                                try:
                                    return int(nums[0].replace(',', ''))
                                except ValueError:
                                    pass
        
        return None
    
    def extract_district_profile_deep(self, district_name: str, pdf_path: str) -> Dict[str, Any]:
        """Extract complete district profile using all strategies."""
        
        logger.info(f"Deep processing {district_name}...")
        
        # Extract text from ALL pages
        text = self.extract_all_text(pdf_path)
        if not text:
            logger.warning(f"Could not extract text from {pdf_path}")
            return {}
        
        # Extract tables
        tables = self.extract_tables(pdf_path)
        logger.debug(f"Found {len(tables)} tables")
        
        profile = {
            "name": district_name,
            "pdf_path": pdf_path,
            "pages_processed": len(text.split('--- PAGE')),
            "rainfall": self.extract_rainfall_deep(text, tables),
            "soil_types": self.extract_soil_deep(text, tables),
            "crops": self.extract_crops_deep(text, tables),
            "markets": self.extract_markets_deep(text),
            "population": self.extract_population_deep(text, tables),
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
        """Process all districts with deep extraction."""
        
        if not PDFPLUMBER_AVAILABLE:
            logger.error("pdfplumber not available")
            return {}
        
        districts = {}
        pdfs = self.list_district_pdfs()
        
        logger.info(f"Starting deep extraction for {len(pdfs)} districts...")
        
        for idx, pdf_info in enumerate(pdfs, 1):
            try:
                profile = self.extract_district_profile_deep(pdf_info["name"], pdf_info["path"])
                if profile:
                    districts[pdf_info["name"]] = profile
                    self.extracted_count += 1
                
                if idx % 10 == 0:
                    logger.info(f"Processed {idx}/{len(pdfs)}...")
            except Exception as e:
                logger.error(f"Error processing {pdf_info['name']}: {e}")
                self.error_count += 1
        
        return districts
    
    def save_database(self, data: Dict, output_path: Path):
        """Save to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(data)} districts to {output_path}")
    
    def print_stats(self, data: Dict):
        """Print extraction statistics."""
        print("\n" + "="*70)
        print("📊 DEEP EXTRACTION COMPLETE")
        print("="*70)
        print(f"Total districts: {len(data)}")
        print(f"Successfully extracted: {self.extracted_count}")
        print(f"Errors: {self.error_count}")
        
        with_rainfall = len([d for d in data.values() if d.get('rainfall', {}).get('annual_mm')])
        with_soil = len([d for d in data.values() if d.get('soil_types')])
        with_crops = len([d for d in data.values() if d.get('crops', {}).get('primary')])
        with_markets = len([d for d in data.values() if d.get('markets', {}).get('trading_centers')])
        with_yields = len([d for d in data.values() if d.get('crops', {}).get('yields')])
        with_population = len([d for d in data.values() if d.get('population')])
        
        print(f"\nData Coverage:")
        print(f"  ✅ Rainfall: {with_rainfall}/55 ({with_rainfall*100//55}%)")
        print(f"  ✅ Soil: {with_soil}/55 ({with_soil*100//55}%)")
        print(f"  ✅ Crops: {with_crops}/55 ({with_crops*100//55}%)")
        print(f"  ✅ Yields: {with_yields}/55 ({with_yields*100//55}%)")
        print(f"  ✅ Markets: {with_markets}/55 ({with_markets*100//55}%)")
        print(f"  ✅ Population: {with_population}/55 ({with_population*100//55}%)")
        
        print("\nSample Data (First District with Yields):")
        for name, data in data.items():
            if data.get('crops', {}).get('yields'):
                print(f"  {name}:")
                print(f"    Rainfall: {data.get('rainfall', {}).get('annual_mm')}mm")
                print(f"    Yields: {data.get('crops', {}).get('yields')}")
                break
        
        print("="*70 + "\n")


def main():
    """Main execution."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    print("\n🚀 DEEP DISTRICT PROFILE EXTRACTION (Level 3 - Professional)\n")
    print("Processing ALL pages with advanced strategies...\n")
    
    if not PDFPLUMBER_AVAILABLE:
        print("Installing pdfplumber...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber"], check=False)
        return
    
    extractor = DeepDistrictExtractor()
    districts_data = extractor.process_all_districts()
    
    extractor.save_database(districts_data, extractor.OUTPUT_PATH)
    extractor.print_stats(districts_data)
    
    return extractor.OUTPUT_PATH


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
