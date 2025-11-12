"""
Citation-Tracked District Extraction - Level 5 Professional
Every data point includes source evidence:
- PDF filename
- Page number
- Section/table name
- Exact quote/location
- Confidence level
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class CitedDistrictExtractor:
    """Extract with full citation evidence for authority approval."""
    
    ZIMBABWE_64_DISTRICTS = {
        'Beitbridge', 'Bikita', 'Bindura', 'Binga', 'Bubi', 'Buhera', 'Bulilima',
        'Chegutu', 'Chikomba', 'Chimanimani', 'Chipinge', 'Chiredzi', 'Chirumhanzu',
        'Chivi', 'Gokwe North', 'Gokwe South', 'Goromonzi', 'Guruve', 'Gutu', 'Gwanda',
        'Gweru', 'Hwange', 'Hwedza', 'Insiza', 'Kariba', 'Kwekwe', 'Lupane', 'Makonde',
        'Mangwe', 'Marondera', 'Masvingo', 'Matobo', 'Mazowe', 'Mberengwa', 'Mbire',
        'Mhondoro Ngezi', 'Mudzi', 'Murehwa', 'Mutare', 'Mutasa', 'Mwenezi', 'Nyanga',
        'Sanyati', 'Shamva', 'Shurugwi', 'Tsholotsho', 'UMP', 'Zvimba', 'Rushinga',
        'Mutoko', 'Seke', 'Zaka', 'Umguza', 'Umzingwane', 'Centenary', 'Karoi', 'Rusape',
        'Uzumba Maramba Pfungwe', 'MT Darwin'
    }
    
    DISTRICT_DATA_DIR = Path("/Users/providencemtendereki/Zim District data ")
    OUTPUT_PATH = Path(__file__).parent.parent / "data" / "districts_cited.json"
    EVIDENCE_PATH = Path(__file__).parent.parent / "data" / "districts_evidence.json"
    
    def __init__(self):
        self.extracted_count = 0
        self.error_count = 0
        self.evidence_log = {}
    
    def match_district(self, filename: str) -> Optional[str]:
        """Match PDF filename to official district."""
        clean = filename.replace("-District-Profile", "").replace("-District", "").replace("-", " ")
        
        for dist in self.ZIMBABWE_64_DISTRICTS:
            if dist.lower() == clean.lower():
                return dist
            if dist.lower() in clean.lower() or clean.lower() in dist.lower():
                return dist
        return None
    
    def extract_with_citation(self, pdf_path: str, district_name: str) -> Tuple[Dict, Dict]:
        """Extract data with full citation tracking."""
        logger.info(f"Processing: {district_name} ({Path(pdf_path).name})")
        
        data = {'name': district_name, 'sources': []}
        evidence = {'district': district_name, 'pdf': Path(pdf_path).name, 'extractions': []}
        
        if not PDFPLUMBER_AVAILABLE:
            return data, evidence
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract rainfall with citations
                rainfall_data = self._extract_rainfall_cited(pdf, district_name)
                if rainfall_data:
                    data['rainfall'] = rainfall_data['data']
                    evidence['extractions'].append(rainfall_data['citation'])
                
                # Extract markets with citations
                markets_data = self._extract_markets_cited(pdf, district_name)
                if markets_data:
                    data['markets'] = markets_data['data']
                    for citation in markets_data['citations']:
                        evidence['extractions'].append(citation)
                
                # Extract soil with citations
                soil_data = self._extract_soil_cited(pdf, district_name)
                if soil_data:
                    data['soil_types'] = soil_data['data']
                    evidence['extractions'].append(soil_data['citation'])
                
                # Extract yields with citations
                yields_data = self._extract_yields_cited(pdf, district_name)
                if yields_data:
                    data['crops'] = {'yields': yields_data['data']}
                    for citation in yields_data['citations']:
                        evidence['extractions'].append(citation)
                
                # Extract population with citations
                pop_data = self._extract_population_cited(pdf, district_name)
                if pop_data:
                    data['population'] = pop_data['data']
                    evidence['extractions'].append(pop_data['citation'])
        
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            self.error_count += 1
        
        return data, evidence
    
    def _extract_rainfall_cited(self, pdf, district: str) -> Optional[Dict]:
        """Extract rainfall WITH full citation."""
        try:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                patterns = [
                    r'(?:mean\s+)?annual\s+rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)',
                    r'rainfall[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|millimetres?)',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        value = int(float(match.group(1)))
                        if 100 < value < 2000:
                            # Extract surrounding context
                            start = max(0, match.start() - 50)
                            end = min(len(text), match.end() + 50)
                            context = text[start:end].strip()
                            
                            return {
                                'data': {'annual_mm': value, 'source': 'text'},
                                'citation': {
                                    'field': 'rainfall',
                                    'value': f"{value}mm",
                                    'page': page_num + 1,
                                    'section': 'Climate/Rainfall',
                                    'exact_text': context,
                                    'confidence': 'high',
                                    'pattern': pattern[:50] + '...'
                                }
                            }
                
                # Check tables
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        if not table:
                            continue
                        for row in table:
                            row_str = ' '.join(str(c).lower() for c in row if c)
                            if 'rainfall' in row_str:
                                for cell in row:
                                    nums = re.findall(r'\d+(?:\.\d+)?', str(cell))
                                    if nums:
                                        try:
                                            value = int(float(nums[0]))
                                            if 100 < value < 2000:
                                                return {
                                                    'data': {'annual_mm': value, 'source': 'table'},
                                                    'citation': {
                                                        'field': 'rainfall',
                                                        'value': f"{value}mm",
                                                        'page': page_num + 1,
                                                        'section': f'Table {table_idx + 1}',
                                                        'exact_text': str(row),
                                                        'confidence': 'high',
                                                        'table_index': table_idx
                                                    }
                                                }
                                        except ValueError:
                                            pass
        
        except Exception as e:
            logger.debug(f"Error extracting rainfall: {e}")
        
        return None
    
    def _extract_markets_cited(self, pdf, district: str) -> Optional[Dict]:
        """Extract markets WITH full citations."""
        markets = []
        citations = []
        
        try:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                # Find trading centers
                patterns = [
                    r'(?:trading\s+center|growth\s+point|market)[:\s]*([A-Z][a-zA-Z\s]{2,30}?)(?:\n|,|$)',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        market_name = match.group(1).strip()
                        if 3 < len(market_name) < 50 and market_name not in markets:
                            markets.append(market_name)
                            
                            # Get context
                            start = max(0, match.start() - 100)
                            end = min(len(text), match.end() + 100)
                            context = text[start:end].strip()
                            
                            citations.append({
                                'field': 'markets',
                                'value': market_name,
                                'type': 'trading_center',
                                'page': page_num + 1,
                                'section': 'Markets/Trading Centers',
                                'exact_text': context,
                                'confidence': 'medium'
                            })
                
                # Check tables for market data
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        if not table:
                            continue
                        for row in table:
                            row_str = ' '.join(str(c) for c in row if c)
                            if any(kw in row_str.lower() for kw in ['market', 'trading', 'depot']):
                                for cell in row:
                                    if cell and isinstance(cell, str) and 3 < len(cell) < 50:
                                        if cell not in markets:
                                            markets.append(cell)
                                            citations.append({
                                                'field': 'markets',
                                                'value': cell,
                                                'type': 'trading_center',
                                                'page': page_num + 1,
                                                'section': f'Table {table_idx + 1}',
                                                'exact_text': str(row),
                                                'confidence': 'high'
                                            })
        
        except Exception as e:
            logger.debug(f"Error extracting markets: {e}")
        
        if markets:
            return {
                'data': {'trading_centers': markets[:10]},
                'citations': citations
            }
        return None
    
    def _extract_soil_cited(self, pdf, district: str) -> Optional[Dict]:
        """Extract soil WITH full citations."""
        soils = []
        
        try:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                soil_keywords = ['clay', 'loam', 'sandy', 'silt', 'vertisol', 'alfisol']
                
                for soil in soil_keywords:
                    if re.search(rf'\b{soil}\b', text, re.IGNORECASE):
                        soils.append(soil)
                        
                        match = re.search(rf'\b{soil}\b', text, re.IGNORECASE)
                        start = max(0, match.start() - 80)
                        end = min(len(text), match.end() + 80)
                        context = text[start:end].strip()
                        
                        return {
                            'data': soils,
                            'citation': {
                                'field': 'soil_types',
                                'value': soil,
                                'page': page_num + 1,
                                'section': 'Soil Classification',
                                'exact_text': context,
                                'confidence': 'medium'
                            }
                        }
        
        except Exception as e:
            logger.debug(f"Error extracting soil: {e}")
        
        if soils:
            return {'data': soils, 'citation': {}}
        return None
    
    def _extract_yields_cited(self, pdf, district: str) -> Optional[Dict]:
        """Extract yields WITH citations."""
        yields = {}
        citations = []
        
        try:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                patterns = [
                    r'(\w+)\s+yield[:\s]*(\d+(?:\.\d+)?)\s*(?:t/ha|tonnes?/ha)',
                    r'(\w+)[:\s]*(\d+(?:\.\d+)?)\s*t/ha',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        crop = match.group(1).lower()
                        value = float(match.group(2))
                        
                        if crop not in yields:
                            yields[crop] = value
                            
                            start = max(0, match.start() - 60)
                            end = min(len(text), match.end() + 60)
                            context = text[start:end].strip()
                            
                            citations.append({
                                'field': 'yields',
                                'crop': crop,
                                'value': f"{value} t/ha",
                                'page': page_num + 1,
                                'section': 'Crop Production/Yields',
                                'exact_text': context,
                                'confidence': 'high'
                            })
        
        except Exception as e:
            logger.debug(f"Error extracting yields: {e}")
        
        if yields:
            return {
                'data': yields,
                'citations': citations
            }
        return None
    
    def _extract_population_cited(self, pdf, district: str) -> Optional[Dict]:
        """Extract population WITH citation."""
        try:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                patterns = [
                    r'population[:\s]*(?:is\s+)?(\d+(?:[,\s]\d+)*)',
                    r'Total.*?population[:\s]*(\d+(?:[,\s]\d+)*)',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        pop_str = match.group(1).replace(',', '').replace(' ', '')
                        try:
                            pop = int(pop_str)
                            if 1000 < pop < 10000000:
                                start = max(0, match.start() - 80)
                                end = min(len(text), match.end() + 80)
                                context = text[start:end].strip()
                                
                                return {
                                    'data': pop,
                                    'citation': {
                                        'field': 'population',
                                        'value': f"{pop:,}",
                                        'page': page_num + 1,
                                        'section': 'Demographics',
                                        'exact_text': context,
                                        'confidence': 'high'
                                    }
                                }
                        except ValueError:
                            pass
        
        except Exception as e:
            logger.debug(f"Error extracting population: {e}")
        
        return None
    
    def run_extraction(self):
        """Extract from ALL 64 districts with citations."""
        if not self.DISTRICT_DATA_DIR.exists():
            logger.error(f"Directory not found")
            return
        
        all_data = {}
        all_evidence = {}
        pdf_files = sorted(self.DISTRICT_DATA_DIR.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDFs, extracting 64 districts with citations...")
        
        start_time = time.time()
        extracted_districts = set()
        
        for pdf_path in pdf_files:
            try:
                district_name = self.match_district(pdf_path.stem)
                
                if district_name is None or district_name in extracted_districts:
                    continue
                
                data, evidence = self.extract_with_citation(str(pdf_path), district_name)
                all_data[district_name] = data
                all_evidence[district_name] = evidence
                extracted_districts.add(district_name)
                self.extracted_count += 1
            
            except Exception as e:
                logger.error(f"Error: {e}")
                self.error_count += 1
        
        elapsed = time.time() - start_time
        
        # Save results
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.OUTPUT_PATH, 'w') as f:
            json.dump(all_data, f, indent=2)
        with open(self.EVIDENCE_PATH, 'w') as f:
            json.dump(all_evidence, f, indent=2)
        
        missing = self.ZIMBABWE_64_DISTRICTS - extracted_districts
        
        logger.info(f"\n✅ Extraction Complete!")
        logger.info(f"   Districts extracted: {len(extracted_districts)}/64")
        logger.info(f"   Missing: {len(missing)} (no PDFs)")
        if missing:
            logger.info(f"   Missing districts: {', '.join(sorted(missing)[:5])}...")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Data output: {self.OUTPUT_PATH}")
        logger.info(f"   Evidence output: {self.EVIDENCE_PATH}")


if __name__ == "__main__":
    extractor = CitedDistrictExtractor()
    extractor.run_extraction()
