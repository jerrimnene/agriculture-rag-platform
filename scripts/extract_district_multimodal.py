"""
Multi-Modal District Profile Extraction - Level 4 Professional
Extracts data from TEXT, TABLES, IMAGES, CHARTS, and DIAGRAMS
Supports OCR for handwritten/scanned content + chart data extraction
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from io import BytesIO
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
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False


class MultiModalDistrictExtractor:
    """Professional-grade multi-modal extraction from district profiles."""
    
    DISTRICT_DATA_DIR = Path("/Users/providencemtendereki/Zim District data ")
    OUTPUT_PATH = Path(__file__).parent.parent / "data" / "districts_multimodal.json"
    
    def __init__(self):
        self.extracted_count = 0
        self.error_count = 0
        self.stats = {
            'text_extractions': 0,
            'table_extractions': 0,
            'image_extractions': 0,
            'chart_extractions': 0,
            'total_images_processed': 0,
            'ocr_texts_found': 0,
            'charts_detected': 0,
        }
    
    # ============== TEXT EXTRACTION ==============
    
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
            logger.warning(f"Error extracting PDF text {pdf_path}: {e}")
            return ""
    
    # ============== TABLE EXTRACTION ==============
    
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
                        self.stats['table_extractions'] += 1
        except Exception as e:
            logger.warning(f"Error extracting tables from {pdf_path}: {e}")
        
        return tables
    
    # ============== IMAGE EXTRACTION & OCR ==============
    
    def extract_images_with_ocr(self, pdf_path: str) -> Dict[int, Dict[str, Any]]:
        """Extract images from PDF and perform OCR on each."""
        if not PDFPLUMBER_AVAILABLE or not PIL_AVAILABLE:
            return {}
        
        images_data = {}
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    if not page.images:
                        continue
                    
                    images_data[page_num + 1] = {
                        'count': len(page.images),
                        'ocr_texts': [],
                        'detected_numbers': [],
                    }
                    
                    for img_idx, img in enumerate(page.images):
                        try:
                            # Extract image from PDF
                            img_bytes = page.crop(img['bbox']).to_image().tobytes()
                            pil_image = Image.open(BytesIO(img_bytes))
                            
                            # Perform OCR
                            if PYTESSERACT_AVAILABLE:
                                ocr_text = pytesseract.image_to_string(pil_image)
                                if ocr_text.strip():
                                    images_data[page_num + 1]['ocr_texts'].append({
                                        'image_idx': img_idx,
                                        'text': ocr_text
                                    })
                                    self.stats['ocr_texts_found'] += 1
                            
                            # Extract numbers from OCR text
                            numbers = re.findall(r'\d+(?:\.\d+)?', ocr_text)
                            if numbers:
                                images_data[page_num + 1]['detected_numbers'].extend(numbers)
                            
                            self.stats['total_images_processed'] += 1
                        
                        except Exception as e:
                            logger.debug(f"Error processing image {img_idx} on page {page_num + 1}: {e}")
        
        except Exception as e:
            logger.warning(f"Error extracting images from {pdf_path}: {e}")
        
        if images_data:
            self.stats['image_extractions'] += 1
        
        return images_data
    
    # ============== CHART/GRAPH DETECTION ==============
    
    def extract_chart_data(self, pdf_path: str) -> Dict[int, List[Dict]]:
        """Detect and extract data from charts/graphs in PDF."""
        if not PDFPLUMBER_AVAILABLE or not CV_AVAILABLE or not PIL_AVAILABLE:
            return {}
        
        charts_data = {}
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    if not page.curves and not page.lines:
                        continue
                    
                    # Convert page to image for analysis
                    page_image = page.to_image(resolution=150)
                    img_array = np.array(page_image.original)
                    
                    # Detect bar charts and trend lines
                    detected_charts = self._detect_chart_patterns(img_array, page_num + 1)
                    
                    if detected_charts:
                        charts_data[page_num + 1] = detected_charts
                        self.stats['charts_detected'] += len(detected_charts)
                
                if charts_data:
                    self.stats['chart_extractions'] += 1
        
        except Exception as e:
            logger.warning(f"Error extracting charts from {pdf_path}: {e}")
        
        return charts_data
    
    def _detect_chart_patterns(self, img_array: np.ndarray, page_num: int) -> List[Dict]:
        """Detect chart patterns in image using OpenCV."""
        detected = []
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Detect lines (for bar charts, axes)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
            
            if lines is not None and len(lines) > 5:
                detected.append({
                    'type': 'bar_chart_detected',
                    'confidence': 'medium',
                    'line_count': len(lines),
                    'page': page_num
                })
            
            # Detect circles/dots (for scatter plots)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                      param1=50, param2=30, minRadius=2, maxRadius=20)
            
            if circles is not None:
                detected.append({
                    'type': 'scatter_plot_detected',
                    'confidence': 'medium',
                    'point_count': len(circles[0]),
                    'page': page_num
                })
            
            # Detect contours (for maps, distribution diagrams)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 20:
                detected.append({
                    'type': 'distribution_map_detected',
                    'confidence': 'low',
                    'contour_count': len(contours),
                    'page': page_num
                })
        
        except Exception as e:
            logger.debug(f"Error in chart pattern detection: {e}")
        
        return detected
    
    # ============== DEEP DATA EXTRACTION ==============
    
    def extract_rainfall_deep(self, text: str, tables: List[Dict], 
                             images_data: Dict, charts_data: Dict) -> Dict[str, Any]:
        """Extract rainfall from TEXT, TABLES, IMAGES, and CHARTS."""
        rainfall = {}
        
        # Strategy 1: Direct text patterns
        text_patterns = [
            r'(?:mean\s+)?annual\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)',
            r'rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)\s*(?:per\s+annum|annually|p\.a\.)',
            r'(\d+(?:\.\d+)?)\s*mm\s+(?:annual|yearly)',
            r'average\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*mm',
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
        
        # Strategy 3: Extract from OCR text in images (charts, diagrams)
        for page_num, img_info in images_data.items():
            for ocr_entry in img_info.get('ocr_texts', []):
                ocr_text = ocr_entry.get('text', '')
                matches = re.findall(r'(?:rainfall|rain)\s*(?:[\w\s]*?)(\d+(?:\.\d+)?)\s*mm', 
                                   ocr_text, re.IGNORECASE)
                if matches:
                    try:
                        val = int(float(matches[0]))
                        if 100 < val < 2000 and 'annual_mm' not in rainfall:
                            rainfall['annual_mm'] = val
                            rainfall['source'] = 'ocr_image'
                    except ValueError:
                        pass
        
        # Strategy 4: Chart-detected rainfall might be in numbers
        if 'annual_mm' not in rainfall and charts_data:
            for page_num, charts in charts_data.items():
                for chart in charts:
                    if 'rainfall' in str(chart).lower() or 'precipitation' in str(chart).lower():
                        # Try to extract from associated OCR text
                        if page_num in images_data:
                            for ocr_entry in images_data[page_num].get('ocr_texts', []):
                                nums = re.findall(r'\d+(?:\.\d+)?', ocr_entry.get('text', ''))
                                if nums:
                                    try:
                                        val = int(float(nums[0]))
                                        if 100 < val < 2000:
                                            rainfall['annual_mm'] = val
                                            rainfall['source'] = 'chart_ocr'
                                            break
                                    except ValueError:
                                        pass
        
        return rainfall
    
    def extract_yields_deep(self, text: str, tables: List[Dict],
                           images_data: Dict, charts_data: Dict) -> Dict[str, float]:
        """Extract yields from TEXT, TABLES, IMAGES, and CHARTS."""
        yields = {}
        crops = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco', 
                'cotton', 'soybeans', 'wheat', 'rice', 'sunflower', 'vegetables']
        
        # Strategy 1: Text patterns
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
        
        # Strategy 3: Extract from OCR text in images (yield comparison charts)
        for page_num, img_info in images_data.items():
            for ocr_entry in img_info.get('ocr_texts', []):
                ocr_text = ocr_entry.get('text', '')
                # Look for patterns like "Maize 3.5" or "Yield: 4.2 t/ha"
                for pattern in yield_patterns:
                    matches = re.finditer(pattern, ocr_text, re.IGNORECASE)
                    for match in matches:
                        crop_name = match.group(1).lower()
                        try:
                            yield_val = float(match.group(2))
                            for std_crop in crops:
                                if std_crop in crop_name:
                                    if std_crop not in yields:
                                        yields[std_crop] = yield_val
                                    break
                        except (ValueError, AttributeError):
                            pass
        
        return yields
    
    def extract_soil_deep(self, text: str, tables: List[Dict],
                         images_data: Dict, charts_data: Dict) -> List[str]:
        """Extract soil types from TEXT, TABLES, IMAGES, and DIAGRAMS."""
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
        
        # Strategy 3: OCR from images (soil maps, diagrams)
        for page_num, img_info in images_data.items():
            for ocr_entry in img_info.get('ocr_texts', []):
                ocr_text = ocr_entry.get('text', '').lower()
                for soil in soil_keywords:
                    if soil in ocr_text:
                        soils.add(soil)
        
        return sorted(list(soils))
    
    def extract_markets_deep(self, text: str, tables: List[Dict],
                            images_data: Dict, charts_data: Dict) -> Dict[str, Any]:
        """Extract market data from TEXT, TABLES, IMAGES."""
        markets = {
            'trading_centers': [],
            'commodities': [],
            'market_days': [],
            'sources': []
        }
        
        # Strategy 1: Text patterns for trading centers
        center_patterns = [
            r'(?:growth\s+point|trading\s+center|market|depot)[:\s]*([A-Z][a-zA-Z\s]+?)(?:\n|,|;|\.|$)',
        ]
        
        for pattern in center_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                center = match.group(1).strip()
                if len(center) < 50 and center not in markets['trading_centers']:
                    markets['trading_centers'].append(center)
        
        # Strategy 2: Commodity patterns
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
                        if cell and isinstance(cell, str) and len(cell) > 3 and len(cell) < 50:
                            if cell not in markets['trading_centers']:
                                markets['trading_centers'].append(cell.strip())
        
        # Strategy 4: OCR from images (market maps, lists)
        for page_num, img_info in images_data.items():
            for ocr_entry in img_info.get('ocr_texts', []):
                ocr_text = ocr_entry.get('text', '')
                # Look for capitalized words that might be market names
                potential_centers = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', ocr_text)
                markets['trading_centers'].extend(potential_centers)
        
        # Remove duplicates
        markets['trading_centers'] = list(set(markets['trading_centers']))[:10]
        markets['commodities'] = list(set(markets['commodities']))
        
        return markets
    
    def extract_population_deep(self, text: str, tables: List[Dict],
                               images_data: Dict) -> Optional[int]:
        """Extract population from TEXT, TABLES, IMAGES."""
        
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
        
        # Strategy 3: OCR from images
        for page_num, img_info in images_data.items():
            for ocr_entry in img_info.get('ocr_texts', []):
                ocr_text = ocr_entry.get('text', '')
                match = re.search(r'population[:\s]*(\d+(?:[,\s]\d+)*)', ocr_text, re.IGNORECASE)
                if match:
                    pop_str = match.group(1).replace(',', '').replace(' ', '')
                    try:
                        pop = int(pop_str)
                        if 1000 < pop < 10000000:
                            return pop
                    except ValueError:
                        pass
        
        return None
    
    # ============== MAIN PROCESSING ==============
    
    def process_pdf(self, pdf_path: str, district_name: str) -> Dict[str, Any]:
        """Process single PDF with all extraction methods."""
        logger.info(f"Processing: {district_name}")
        
        # Text extraction
        text = self.extract_all_text(pdf_path)
        
        # Structured data extraction
        tables = self.extract_tables(pdf_path)
        
        # Image/Chart extraction
        images_data = self.extract_images_with_ocr(pdf_path)
        charts_data = self.extract_chart_data(pdf_path)
        
        # Deep data extraction (uses all sources)
        district_data = {
            'name': district_name,
            'rainfall': self.extract_rainfall_deep(text, tables, images_data, charts_data),
            'soil_types': self.extract_soil_deep(text, tables, images_data, charts_data),
            'crops': {
                'primary': [],
                'yields': self.extract_yields_deep(text, tables, images_data, charts_data)
            },
            'markets': self.extract_markets_deep(text, tables, images_data, charts_data),
            'population': self.extract_population_deep(text, tables, images_data),
            'extraction_metadata': {
                'pages_processed': self._count_pages(pdf_path),
                'images_found': sum(img_info['count'] for img_info in images_data.values()),
                'ocr_texts_extracted': sum(len(img_info.get('ocr_texts', [])) 
                                          for img_info in images_data.values()),
                'charts_detected': sum(len(charts) for charts in charts_data.values()),
                'tables_extracted': len(tables),
            }
        }
        
        # Extract crop names from crops mentioned in text
        crop_keywords = ['maize', 'sorghum', 'millet', 'groundnuts', 'beans', 'tobacco',
                        'cotton', 'soybeans', 'wheat', 'rice', 'vegetables']
        for crop in crop_keywords:
            if re.search(rf'\b{crop}\b', text, re.IGNORECASE):
                district_data['crops']['primary'].append(crop)
        
        self.extracted_count += 1
        return district_data
    
    def _count_pages(self, pdf_path: str) -> int:
        """Count pages in PDF."""
        if not PDFPLUMBER_AVAILABLE:
            return 0
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except Exception:
            return 0
    
    def run_extraction(self):
        """Run extraction on all district PDFs."""
        if not self.DISTRICT_DATA_DIR.exists():
            logger.error(f"Directory not found: {self.DISTRICT_DATA_DIR}")
            return
        
        all_data = {}
        pdf_files = sorted([f for f in self.DISTRICT_DATA_DIR.glob("*.pdf") 
                           if "District" in f.name])
        
        logger.info(f"Found {len(pdf_files)} district PDFs")
        
        start_time = time.time()
        
        for pdf_path in pdf_files:
            try:
                district_name = pdf_path.stem.replace("-District-Profile", "").replace("-", " ")
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
        logger.info(f"   Images processed: {self.stats['total_images_processed']}")
        logger.info(f"   OCR texts found: {self.stats['ocr_texts_found']}")
        logger.info(f"   Charts detected: {self.stats['charts_detected']}")


if __name__ == "__main__":
    extractor = MultiModalDistrictExtractor()
    extractor.run_extraction()
