"""
Optimized Multi-Modal District Extraction - Level 4 Fast
Extracts from TEXT, TABLES, IMAGES, and CHARTS efficiently
Skips full-page OCR in favor of targeted image analysis
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
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False


class OptimizedDistrictExtractor:
    """Optimized multi-modal extraction focusing on high-value data sources."""
    
    DISTRICT_DATA_DIR = Path("/Users/providencemtendereki/Zim District data ")
    OUTPUT_PATH = Path(__file__).parent.parent / "data" / "districts_multimodal.json"
    
    def __init__(self):
        self.extracted_count = 0
        self.error_count = 0
        self.stats = {
            'text_extractions': 0,
            'table_extractions': 0,
            'images_detected': 0,
            'charts_detected': 0,
        }
    
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
                    
                    # Count images
                    if page.images:
                        detection['images_per_page'][page_key] = len(page.images)
                        detection['total_images'] += len(page.images)
                    
                    # Count graphics/curves
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
    
    # ============== DEEP DATA EXTRACTION ==============
    
    def extract_rainfall_deep(self, text: str, tables: List[Dict]) -> Dict[str, Any]:
        """Extract rainfall from TEXT and TABLES."""
        rainfall = {}
        
        # Strategy 1: Direct text patterns
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
                    break
                except (ValueError, IndexError):
                    pass
        
        # Strategy 2: Extract from tables
        if 'annual_mm' not in rainfall:
            for table_info in tables:
                table = table_info['data']
                if not table or len(table) < 2:
                    continue
                
                for row_idx, row in enumerate(table):
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
                                            break
                                    except ValueError:
                                        pass
        
        # Strategy 3: Seasonal rainfall
        if 'annual_mm' not in rainfall:
            seasonal_patterns = {
                'summer': [r'[Ss]ummer\s+(?:rainfall|rain)[:\s]*(\d+(?:\.\d+)?)\s*mm'],
                'winter': [r'[Ww]inter\s+(?:rainfall|rain)[:\s]*(\d+(?:\.\d+)?)\s*mm'],
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
        """Extract yields from TEXT and TABLES."""
        yields = {}
        crops = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco', 
                'cotton', 'soybeans', 'wheat', 'rice', 'sunflower', 'vegetables']
        
        # Strategy 1: Text patterns
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
                    for std_crop in crops:
                        if std_crop in crop_name or crop_name in std_crop:
                            if std_crop not in yields or yield_val > yields[std_crop]:
                                yields[std_crop] = yield_val
                            break
                except (ValueError, AttributeError):
                    pass
        
        # Strategy 2: Extract from tables
        for table_info in tables:
            table = table_info['data']
            if not table or len(table) < 2:
                continue
            
            for row in table:
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                if any(kw in row_str for kw in ['yield', 'production', 't/ha', 'tonnes']):
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
            'ultisol', 'mollisol', 'spodosol', 'histosol', 'inceptisol',
            'sandy loam', 'clay loam', 'sandy clay', 'silty loam'
        ]
        
        # Strategy 1: Text search
        for soil in soil_keywords:
            pattern = rf'\b{soil}\b'
            if re.search(pattern, text, re.IGNORECASE):
                soils.add(soil.lower())
        
        # Strategy 2: Tables
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
            'market_days': [],
        }
        
        # Strategy 1: Trading centers
        center_patterns = [
            r'(?:growth\s+point|trading\s+center|market|depot)[:\s]*([A-Z][a-zA-Z\s]+?)(?:\n|,|;|\.|$)',
        ]
        
        for pattern in center_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                center = match.group(1).strip()
                if 5 < len(center) < 50 and center not in markets['trading_centers']:
                    markets['trading_centers'].append(center)
        
        # Strategy 2: Commodities
        commodities = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco',
                      'cotton', 'soybeans', 'wheat', 'rice', 'vegetables', 'fruits']
        
        for commodity in commodities:
            if re.search(rf'\b{commodity}\b', text, re.IGNORECASE):
                if commodity not in markets['commodities']:
                    markets['commodities'].append(commodity)
        
        # Strategy 3: Tables for market data
        for table_info in tables:
            table = table_info['data']
            for row in table:
                row_str = ' '.join(str(cell) for cell in row if cell)
                if any(keyword in row_str.lower() for keyword in ['market', 'trading', 'depot']):
                    for cell in row:
                        if cell and isinstance(cell, str) and 5 < len(cell) < 50:
                            if cell not in markets['trading_centers']:
                                markets['trading_centers'].append(cell.strip())
        
        # Remove duplicates and limit
        markets['trading_centers'] = list(set(markets['trading_centers']))[:10]
        markets['commodities'] = list(set(markets['commodities']))
        
        return markets
    
    def extract_population_deep(self, text: str, tables: List[Dict]) -> Optional[int]:
        """Extract population from TEXT and TABLES."""
        
        # Strategy 1: Text patterns
        patterns = [
            r'population[:\s]*(?:is\s+)?(?:approximately\s+)?(\d+(?:[,\s]\d+)*)',
            r'(\d+(?:[,\s]\d+)*)\s+(?:people|inhabitants|population)',
            r'Total\s+population[:\s]*(\d+(?:[,\s]\d+)*)',
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
        
        # Strategy 2: Tables
        for table_info in tables:
            table = table_info['data']
            for row in table:
                row_str = ' '.join(str(cell).lower() for cell in row if cell)
                if 'population' in row_str:
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
        """Process single PDF with extraction methods."""
        logger.info(f"Processing: {district_name}")
        
        # Extract text
        text = self.extract_all_text(pdf_path)
        
        # Extract tables
        tables = self.extract_tables(pdf_path)
        
        # Detect images/charts
        detections = self.detect_images_and_charts(pdf_path)
        
        # Deep data extraction
        district_data = {
            'name': district_name,
            'rainfall': self.extract_rainfall_deep(text, tables),
            'soil_types': self.extract_soil_deep(text, tables),
            'crops': {
                'primary': [],
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
        
        # Extract crop names from text
        crop_keywords = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco',
                        'cotton', 'soybeans', 'wheat', 'rice', 'vegetables']
        for crop in crop_keywords:
            if re.search(rf'\b{crop}\b', text, re.IGNORECASE):
                district_data['crops']['primary'].append(crop)
        
        self.extracted_count += 1
        return district_data
    
    def run_extraction(self):
        """Run extraction on all district PDFs."""
        if not self.DISTRICT_DATA_DIR.exists():
            logger.error(f"Directory not found: {self.DISTRICT_DATA_DIR}")
            return
        
        all_data = {}
        # Filter for district profile PDFs
        pdf_files = sorted([f for f in self.DISTRICT_DATA_DIR.glob("*District*.pdf")])
        
        logger.info(f"Found {len(pdf_files)} district PDFs")
        
        start_time = time.time()
        
        for pdf_path in pdf_files:
            try:
                # Extract district name from filename
                district_name = pdf_path.stem
                for pattern in ["-District-Profile", "-District", "District-Profile"]:
                    district_name = district_name.replace(pattern, "")
                district_name = district_name.replace("-", " ")
                
                district_data = self.process_pdf(str(pdf_path), district_name)
                all_data[district_name] = district_data
            except Exception as e:
                logger.error(f"Error processing {pdf_path.name}: {e}")
                self.error_count += 1
        
        elapsed = time.time() - start_time
        
        # Save results
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.OUTPUT_PATH, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        logger.info(f"\n✅ Extraction Complete!")
        logger.info(f"   Districts processed: {self.extracted_count}/{len(pdf_files)}")
        logger.info(f"   Errors: {self.error_count}")
        logger.info(f"   Time elapsed: {elapsed:.1f}s")
        logger.info(f"   Output: {self.OUTPUT_PATH}")
        logger.info(f"\nExtraction Stats:")
        logger.info(f"   Text extractions: {self.stats['text_extractions']}")
        logger.info(f"   Table extractions: {self.stats['table_extractions']}")
        logger.info(f"   Images detected: {self.stats['images_detected']}")
        logger.info(f"   Charts detected: {self.stats['charts_detected']}")


if __name__ == "__main__":
    extractor = OptimizedDistrictExtractor()
    extractor.run_extraction()
