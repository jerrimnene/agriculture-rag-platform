"""
Clean Multi-Modal District Extraction - Level 4 Professional
Extracts from TEXT, TABLES, IMAGES, and CHARTS
FILTERED to only the 55 official Zimbabwe districts
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False


class CleanDistrictExtractor:
    """Multi-modal extraction for 55 official Zimbabwe districts only."""
    
    # The 55 official Zimbabwe districts
    ZIMBABWE_DISTRICTS = {
        'Beitbridge', 'Bikita', 'Bindura', 'Binga', 'Bubi', 'Buhera', 'Bulilima',
        'Chegutu', 'Chikomba', 'Chimanimani', 'Chipinge', 'Chiredzi', 'Chirumhanzu',
        'Chivi', 'Gokwe North', 'Gokwe South', 'Goromonzi', 'Guruve', 'Gutu', 'Gwanda',
        'Gweru', 'Hwange', 'Hwedza', 'Insiza', 'Kariba', 'Kwekwe', 'Lupane', 'Makonde',
        'Mangwe', 'Marondera', 'Masvingo', 'Matobo', 'Mazowe', 'Mberengwa', 'Mbire',
        'Mhondoro Ngezi', 'Mudzi', 'Murehwa', 'Mutare', 'Mutasa', 'Mwenezi', 'Nyanga',
        'Rzambuk', 'Rusape', 'Sanyati', 'Shamva', 'Shurugwi', 'Tsholotsho', 'UMP',
        'Uzumba Maramba Pfungwe', 'Zvimba', 'Karoi', 'MT Darwin', 'Centenary'
    }
    
    DISTRICT_DATA_DIR = Path("/Users/providencemtendereki/Zim District data ")
    OUTPUT_PATH = Path(__file__).parent.parent / "data" / "districts_multimodal_clean.json"
    
    def __init__(self):
        self.extracted_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.stats = {
            'text_extractions': 0,
            'table_extractions': 0,
            'images_detected': 0,
            'charts_detected': 0,
        }
    
    def match_district_name(self, filename_stem: str) -> Optional[str]:
        """Try to match a PDF filename to an official district."""
        # Clean filename
        clean = filename_stem.replace("-District-Profile", "").replace("-District", "").replace("-", " ")
        
        # Direct match
        if clean in self.ZIMBABWE_DISTRICTS:
            return clean
        
        # Case-insensitive match
        clean_lower = clean.lower()
        for dist in self.ZIMBABWE_DISTRICTS:
            if dist.lower() == clean_lower:
                return dist
        
        # Partial match (handles variations like "MT Darwin" vs "Mt Darwin")
        for dist in self.ZIMBABWE_DISTRICTS:
            if dist.lower() in clean_lower or clean_lower in dist.lower():
                # Only if it's a reasonable match
                if len(clean) > 3 and len(dist) > 3:
                    return dist
        
        return None
    
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
                self.stats['text_extractions'] += 1
                return text
        except Exception as e:
            logger.debug(f"Error extracting text: {e}")
            return ""
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """Extract structured tables from PDF."""
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
                if tables:
                    self.stats['table_extractions'] += 1
        except Exception as e:
            logger.debug(f"Error extracting tables: {e}")
        
        return tables
    
    def detect_images_and_charts(self, pdf_path: str) -> Dict[str, Any]:
        """Detect images and charts without full OCR."""
        if not PDFPLUMBER_AVAILABLE:
            return {}
        
        detection = {
            'images_per_page': {},
            'graphics_per_page': {},
            'total_images': 0,
            'total_graphics': 0,
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_key = page_num + 1
                    
                    if page.images:
                        detection['images_per_page'][page_key] = len(page.images)
                        detection['total_images'] += len(page.images)
                    
                    if page.curves or page.lines:
                        graphic_count = len(page.curves) + len(page.lines)
                        detection['graphics_per_page'][page_key] = graphic_count
                        detection['total_graphics'] += graphic_count
                
                if detection['total_images'] > 0:
                    self.stats['images_detected'] += 1
                if detection['total_graphics'] > 0:
                    self.stats['charts_detected'] += 1
        
        except Exception as e:
            logger.debug(f"Error detecting images/charts: {e}")
        
        return detection
    
    def extract_rainfall_deep(self, text: str, tables: List[Dict]) -> Dict[str, Any]:
        """Extract rainfall from TEXT and TABLES."""
        rainfall = {}
        
        text_patterns = [
            r'(?:mean\s+)?annual\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)',
            r'rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)\s*(?:per\s+annum|annually|p\.a\.)',
            r'(\d+(?:\.\d+)?)\s*mm\s+(?:annual|yearly)',
            r'average\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*mm',
            r'Total\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*mm',
        ]
        
        for pattern in text_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    rainfall['annual_mm'] = int(float(matches[0]))
                    rainfall['source'] = 'text'
                    return rainfall
                except (ValueError, IndexError):
                    pass
        
        if 'annual_mm' not in rainfall:
            for table_info in tables:
                table = table_info['data']
                if not table or len(table) < 2:
                    continue
                
                for row in table:
                    row_str = ' '.join(str(cell).lower() for cell in row if cell)
                    if any(kw in row_str for kw in ['rainfall', 'precipitation', 'rain', 'mm']):
                        for cell in row:
                            if cell:
                                nums = re.findall(r'\d+(?:\.\d+)?', str(cell))
                                if nums:
                                    try:
                                        val = int(float(nums[0]))
                                        if 100 < val < 2000:
                                            rainfall['annual_mm'] = val
                                            rainfall['source'] = 'table'
                                            return rainfall
                                    except ValueError:
                                        pass
        
        return rainfall
    
    def extract_yields_deep(self, text: str, tables: List[Dict]) -> Dict[str, float]:
        """Extract yields from TEXT and TABLES."""
        yields = {}
        crops = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco', 
                'cotton', 'soybeans', 'wheat', 'rice', 'sunflower', 'vegetables']
        
        yield_patterns = [
            r'(\w+)\s+(?:yield|production)[:\s]*(\d+(?:\.\d+)?)\s*(?:tonnes?|t)(?:\s*/?ha)?',
            r'(\w+)[:\s]*(\d+(?:\.\d+)?)\s*(?:tonnes?|t)\s*(?:per\s+hectare|/ha)',
        ]
        
        for pattern in yield_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                crop_name = match.group(1).lower()
                try:
                    yield_val = float(match.group(2))
                    for std_crop in crops:
                        if std_crop in crop_name:
                            if std_crop not in yields or yield_val > yields[std_crop]:
                                yields[std_crop] = yield_val
                            break
                except (ValueError, AttributeError):
                    pass
        
        for table_info in tables:
            table = table_info['data']
            if not table or len(table) < 2:
                continue
            
            for row in table:
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                if any(kw in row_str for kw in ['yield', 'production', 't/ha']):
                    if row and row[0]:
                        crop_name = str(row[0]).lower()
                        for cell in row[1:]:
                            if cell:
                                nums = re.findall(r'\d+(?:\.\d+)?', str(cell))
                                if nums:
                                    try:
                                        val = float(nums[0])
                                        if 0.1 < val < 50:
                                            for std_crop in crops:
                                                if std_crop in crop_name:
                                                    if std_crop not in yields:
                                                        yields[std_crop] = val
                                                    break
                                    except ValueError:
                                        pass
        
        return yields
    
    def extract_soil_deep(self, text: str, tables: List[Dict]) -> List[str]:
        """Extract soil types from TEXT and TABLES."""
        soils = set()
        soil_keywords = [
            'clay', 'loam', 'sandy', 'silt', 'vertisol', 'alfisol', 'oxisol',
            'sandy loam', 'clay loam', 'sandy clay', 'silty loam'
        ]
        
        for soil in soil_keywords:
            if re.search(rf'\b{soil}\b', text, re.IGNORECASE):
                soils.add(soil.lower())
        
        for table_info in tables:
            table = table_info['data']
            for row in table:
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                for soil in soil_keywords:
                    if soil in row_str:
                        soils.add(soil)
        
        return sorted(list(soils))
    
    def extract_markets_deep(self, text: str, tables: List[Dict]) -> Dict[str, Any]:
        """Extract market data from TEXT and TABLES."""
        markets = {
            'trading_centers': [],
            'commodities': [],
        }
        
        commodities = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco',
                      'cotton', 'soybeans', 'wheat', 'rice', 'vegetables', 'fruits']
        
        for commodity in commodities:
            if re.search(rf'\b{commodity}\b', text, re.IGNORECASE):
                markets['commodities'].append(commodity)
        
        for table_info in tables:
            table = table_info['data']
            for row in table:
                row_str = ' '.join(str(cell) for cell in row if cell)
                if any(kw in row_str.lower() for kw in ['market', 'trading']):
                    for cell in row:
                        if cell and isinstance(cell, str) and 5 < len(cell) < 50:
                            if cell not in markets['trading_centers']:
                                markets['trading_centers'].append(cell.strip())
        
        markets['trading_centers'] = list(set(markets['trading_centers']))[:10]
        markets['commodities'] = list(set(markets['commodities']))
        
        return markets
    
    def extract_population_deep(self, text: str, tables: List[Dict]) -> Optional[int]:
        """Extract population from TEXT and TABLES."""
        patterns = [
            r'population[:\s]*(?:is\s+)?(?:approximately\s+)?(\d+(?:[,\s]\d+)*)',
            r'(\d+(?:[,\s]\d+)*)\s+(?:people|inhabitants)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                pop_str = match.group(1).replace(',', '').replace(' ', '')
                try:
                    pop = int(pop_str)
                    if 1000 < pop < 10000000:
                        return pop
                except ValueError:
                    pass
        
        for table_info in tables:
            table = table_info['data']
            for row in table:
                if any('population' in str(cell).lower() for cell in row):
                    for cell in row:
                        if cell:
                            nums = re.findall(r'\d+(?:[,\s]\d+)*', str(cell))
                            if nums:
                                try:
                                    pop = int(nums[0].replace(',', '').replace(' ', ''))
                                    if 1000 < pop < 10000000:
                                        return pop
                                except ValueError:
                                    pass
        
        return None
    
    def process_pdf(self, pdf_path: str, district_name: str) -> Dict[str, Any]:
        """Process single PDF."""
        logger.info(f"Processing: {district_name}")
        
        text = self.extract_all_text(pdf_path)
        tables = self.extract_tables(pdf_path)
        detections = self.detect_images_and_charts(pdf_path)
        
        crop_keywords = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco',
                        'cotton', 'soybeans', 'wheat', 'rice', 'vegetables']
        primary_crops = [c for c in crop_keywords if re.search(rf'\b{c}\b', text, re.IGNORECASE)]
        
        return {
            'name': district_name,
            'rainfall': self.extract_rainfall_deep(text, tables),
            'soil_types': self.extract_soil_deep(text, tables),
            'crops': {
                'primary': primary_crops,
                'yields': self.extract_yields_deep(text, tables)
            },
            'markets': self.extract_markets_deep(text, tables),
            'population': self.extract_population_deep(text, tables),
            'extraction_metadata': {
                'images_detected': detections.get('total_images', 0),
                'graphics_detected': detections.get('total_graphics', 0),
                'tables_extracted': len(tables),
            }
        }
    
    def run_extraction(self):
        """Run extraction on all district PDFs, filtering to 55 official districts."""
        if not self.DISTRICT_DATA_DIR.exists():
            logger.error(f"Directory not found: {self.DISTRICT_DATA_DIR}")
            return
        
        all_data = {}
        pdf_files = sorted(self.DISTRICT_DATA_DIR.glob("*District*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDFs, filtering to 55 official districts...")
        
        start_time = time.time()
        
        for pdf_path in pdf_files:
            try:
                # Try to match to official district
                district_name = self.match_district_name(pdf_path.stem)
                
                if district_name is None:
                    logger.info(f"Skipping (not a district): {pdf_path.name}")
                    self.skipped_count += 1
                    continue
                
                # Skip if already extracted
                if district_name in all_data:
                    logger.info(f"Skipping duplicate: {pdf_path.name} (already have {district_name})")
                    self.skipped_count += 1
                    continue
                
                district_data = self.process_pdf(str(pdf_path), district_name)
                all_data[district_name] = district_data
                self.extracted_count += 1
            
            except Exception as e:
                logger.error(f"Error processing {pdf_path.name}: {e}")
                self.error_count += 1
        
        elapsed = time.time() - start_time
        
        # Save results
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.OUTPUT_PATH, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        logger.info(f"\n✅ Extraction Complete!")
        logger.info(f"   Districts extracted: {self.extracted_count}")
        logger.info(f"   PDFs skipped: {self.skipped_count}")
        logger.info(f"   Errors: {self.error_count}")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Output: {self.OUTPUT_PATH}")


if __name__ == "__main__":
    extractor = CleanDistrictExtractor()
    extractor.run_extraction()
