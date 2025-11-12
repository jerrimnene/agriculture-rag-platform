"""
ZAIES Knowledge Extraction & Structuring System
================================================
Transforms 400+ generic agricultural documents into location-adaptable knowledge

Purpose: Extract structured knowledge from PDFs/docs and tag for Natural Region adaptation
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from dataclasses import dataclass, asdict
import anthropic  # Claude API for extraction

@dataclass
class AgriculturalKnowledge:
    """Structured knowledge unit from documents"""
    knowledge_id: str
    source_document: str
    knowledge_type: str  # fertilizer, seed, pest, disease, irrigation, market, etc.
    crop: Optional[str]
    livestock: Optional[str]
    
    # Core content
    recommendation: str
    dosage_rate: Optional[str]
    timing: Optional[str]
    cost_estimate: Optional[str]
    expected_yield: Optional[str]
    
    # Location adaptation tags
    adaptable_by_rainfall: bool  # Can be adapted based on rainfall zones
    adaptable_by_soil: bool      # Can be adapted based on soil types
    adaptable_by_temperature: bool
    
    # Natural Region applicability (I, II, III, IV, V)
    applicable_regions: List[str]
    
    # Evidence strength
    source_authority: int  # 100=govt, 90=academic, 70=NGO, 50=commercial
    date_published: Optional[str]
    
    # Original context
    original_text: str
    page_number: int


class DocumentProcessor:
    """Process and structure agricultural documents"""
    
    def __init__(self, claude_api_key: str):
        self.client = anthropic.Anthropic(api_key=claude_api_key)
        
        # Authority scoring
        self.authority_scores = {
            'government': 100,  # AGRITEX, Department of Agric
            'academic': 90,     # University of Zimbabwe
            'international': 85, # FAO, FEWS NET
            'ngo': 70,          # CARE, Oxfam
            'commercial': 50    # Seed companies, fertilizer suppliers
        }
    
    def extract_pdf_text(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from PDF by page"""
        text_by_page = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_by_page[page_num + 1] = page.extract_text()
        except Exception as e:
            print(f"Error extracting PDF {pdf_path}: {e}")
        
        return text_by_page
    
    def identify_source_authority(self, document_name: str, content: str) -> tuple[str, int]:
        """Identify document source type and authority score"""
        content_lower = content.lower()
        name_lower = document_name.lower()
        
        # Check for government sources
        govt_indicators = ['agritex', 'ministry of agriculture', 'government of zimbabwe', 
                          'department of agriculture', 'agricultural extension']
        if any(ind in content_lower or ind in name_lower for ind in govt_indicators):
            return 'government', 100
        
        # Check for academic sources
        academic_indicators = ['university', 'research station', 'journal', 'thesis', 'phd']
        if any(ind in content_lower or ind in name_lower for ind in academic_indicators):
            return 'academic', 90
        
        # Check for international organizations
        intl_indicators = ['fao', 'fews net', 'world bank', 'usaid', 'cimmyt', 'icrisat']
        if any(ind in content_lower or ind in name_lower for ind in intl_indicators):
            return 'international', 85
        
        # Check for NGOs
        ngo_indicators = ['care', 'oxfam', 'plan international', 'world vision']
        if any(ind in content_lower or ind in name_lower for ind in ngo_indicators):
            return 'ngo', 70
        
        # Default to commercial
        return 'commercial', 50
    
    def extract_knowledge_with_claude(self, text: str, page_num: int, 
                                     source_doc: str, source_type: str,
                                     authority_score: int) -> List[AgriculturalKnowledge]:
        """Use Claude to extract structured knowledge from text"""
        
        prompt = f"""You are analyzing a Zimbabwean agricultural document to extract structured, actionable knowledge.

SOURCE DOCUMENT: {source_doc}
SOURCE TYPE: {source_type}
PAGE: {page_num}

ZIMBABWE CONTEXT:
- Natural Regions I-V (I=high rainfall 1000mm+, V=low rainfall <450mm)
- Crops: Maize, tobacco, cotton, sorghum, millet, groundnuts
- Farmers need SPECIFIC recommendations (not generic advice)

EXTRACT THE FOLLOWING from the text below:

For each piece of actionable agricultural advice, extract:
1. **knowledge_type**: fertilizer/seed/pest/disease/irrigation/market/planting/harvesting
2. **crop** or **livestock**: What this advice applies to
3. **recommendation**: The actual advice (be specific)
4. **dosage_rate**: If applicable (e.g., "200kg/ha")
5. **timing**: When to apply (e.g., "4 weeks after planting")
6. **cost_estimate**: If mentioned
7. **expected_yield**: If mentioned
8. **adaptable_by_rainfall**: TRUE if recommendation should vary by rainfall zone
9. **adaptable_by_soil**: TRUE if recommendation depends on soil type
10. **adaptable_by_temperature**: TRUE if temperature affects this
11. **applicable_regions**: Which Natural Regions (I, II, III, IV, V) this applies to
    - If document says "high rainfall areas" → [I, II]
    - If document says "semi-arid" → [IV, V]
    - If generic/not specified → [I, II, III, IV, V]

Return JSON array of knowledge units.

TEXT TO ANALYZE:
{text}

Return ONLY valid JSON array, no other text."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            knowledge_units = json.loads(response_text)
            
            # Convert to AgriculturalKnowledge objects
            structured_knowledge = []
            for i, unit in enumerate(knowledge_units):
                knowledge = AgriculturalKnowledge(
                    knowledge_id=f"{source_doc}_p{page_num}_{i}",
                    source_document=source_doc,
                    knowledge_type=unit.get('knowledge_type', 'general'),
                    crop=unit.get('crop'),
                    livestock=unit.get('livestock'),
                    recommendation=unit.get('recommendation', ''),
                    dosage_rate=unit.get('dosage_rate'),
                    timing=unit.get('timing'),
                    cost_estimate=unit.get('cost_estimate'),
                    expected_yield=unit.get('expected_yield'),
                    adaptable_by_rainfall=unit.get('adaptable_by_rainfall', False),
                    adaptable_by_soil=unit.get('adaptable_by_soil', False),
                    adaptable_by_temperature=unit.get('adaptable_by_temperature', False),
                    applicable_regions=unit.get('applicable_regions', ['I', 'II', 'III', 'IV', 'V']),
                    source_authority=authority_score,
                    date_published=None,  # TODO: Extract from document
                    original_text=text[:500],  # First 500 chars as context
                    page_number=page_num
                )
                structured_knowledge.append(knowledge)
            
            return structured_knowledge
            
        except Exception as e:
            print(f"Error extracting knowledge with Claude: {e}")
            return []
    
    def process_document(self, pdf_path: str) -> List[AgriculturalKnowledge]:
        """Process entire document and extract all knowledge"""
        print(f"\n📄 Processing: {pdf_path}")
        
        document_name = os.path.basename(pdf_path)
        
        # Extract text by page
        text_by_page = self.extract_pdf_text(pdf_path)
        
        if not text_by_page:
            print(f"❌ Could not extract text from {pdf_path}")
            return []
        
        # Identify source authority (sample from first page)
        first_page_text = text_by_page.get(1, '')
        source_type, authority_score = self.identify_source_authority(
            document_name, first_page_text
        )
        
        print(f"   Source: {source_type} (Authority: {authority_score}/100)")
        
        # Extract knowledge from each page
        all_knowledge = []
        for page_num, text in text_by_page.items():
            # Skip pages with too little content
            if len(text.strip()) < 100:
                continue
            
            print(f"   📖 Extracting knowledge from page {page_num}...")
            
            knowledge_units = self.extract_knowledge_with_claude(
                text=text,
                page_num=page_num,
                source_doc=document_name,
                source_type=source_type,
                authority_score=authority_score
            )
            
            all_knowledge.extend(knowledge_units)
            print(f"      ✅ Extracted {len(knowledge_units)} knowledge units")
        
        print(f"✅ Total knowledge units from {document_name}: {len(all_knowledge)}")
        return all_knowledge
    
    def process_document_folder(self, folder_path: str, output_json: str):
        """Process all PDFs in folder and save structured knowledge"""
        folder = Path(folder_path)
        pdf_files = list(folder.glob('*.pdf'))
        
        print(f"\n🔍 Found {len(pdf_files)} PDF files in {folder_path}")
        print("=" * 80)
        
        all_knowledge = []
        
        for pdf_file in pdf_files:
            knowledge_units = self.process_document(str(pdf_file))
            all_knowledge.extend(knowledge_units)
        
        # Save to JSON
        output_data = [asdict(k) for k in all_knowledge]
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"✅ COMPLETE: Processed {len(pdf_files)} documents")
        print(f"✅ Extracted {len(all_knowledge)} knowledge units")
        print(f"✅ Saved to: {output_json}")
        
        # Print summary statistics
        self.print_summary(all_knowledge)
    
    def print_summary(self, knowledge: List[AgriculturalKnowledge]):
        """Print summary statistics"""
        print("\n📊 KNOWLEDGE BASE SUMMARY:")
        print("-" * 80)
        
        # By knowledge type
        types = {}
        for k in knowledge:
            types[k.knowledge_type] = types.get(k.knowledge_type, 0) + 1
        
        print("\n🏷️  Knowledge Types:")
        for ktype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"   {ktype:20s}: {count:4d} units")
        
        # By crop
        crops = {}
        for k in knowledge:
            if k.crop:
                crops[k.crop] = crops.get(k.crop, 0) + 1
        
        print("\n🌾 Top Crops:")
        for crop, count in sorted(crops.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {crop:20s}: {count:4d} units")
        
        # Adaptability
        rainfall_adaptable = sum(1 for k in knowledge if k.adaptable_by_rainfall)
        soil_adaptable = sum(1 for k in knowledge if k.adaptable_by_soil)
        
        print(f"\n🎯 Adaptability:")
        print(f"   Rainfall-adaptable: {rainfall_adaptable} ({rainfall_adaptable/len(knowledge)*100:.1f}%)")
        print(f"   Soil-adaptable:     {soil_adaptable} ({soil_adaptable/len(knowledge)*100:.1f}%)")
        
        # Authority
        govt = sum(1 for k in knowledge if k.source_authority == 100)
        academic = sum(1 for k in knowledge if k.source_authority == 90)
        
        print(f"\n🏛️  Evidence Quality:")
        print(f"   Government sources: {govt} ({govt/len(knowledge)*100:.1f}%)")
        print(f"   Academic sources:   {academic} ({academic/len(knowledge)*100:.1f}%)")


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python document_structuring_system.py <folder_path> <output_json>")
        print("Example: python document_structuring_system.py ./documents ./knowledge_base.json")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    output_json = sys.argv[2]
    
    # Get Claude API key
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
    if not claude_api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Process documents
    processor = DocumentProcessor(claude_api_key=claude_api_key)
    processor.process_document_folder(folder_path, output_json)
