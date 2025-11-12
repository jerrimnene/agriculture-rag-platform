"""
Local Language Translation Module
Auto-generates Shona and Ndebele summaries of agricultural advice
"""

import logging
from typing import Dict, Optional
import ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalLanguageTranslator:
    """Translates agricultural advice into Shona and Ndebele."""
    
    def __init__(self, llm_model: str = "mistral", llm_base_url: str = "http://localhost:11434"):
        self.llm_model = llm_model
        self.llm_base_url = llm_base_url
        self.client = ollama.Client(host=llm_base_url)
        
        # Common agricultural terms in Shona and Ndebele
        self.agricultural_glossary = {
            'shona': {
                'maize': 'chibage',
                'crop': 'mbesa / zvirimwa',
                'soil': 'ivhu',
                'fertilizer': 'fetiraiza',
                'planting': 'kudyara',
                'harvest': 'kukohwa',
                'rain': 'mvura',
                'farmer': 'murimi',
                'field': 'munda',
                'seed': 'mbeu',
                'cattle': 'mombe',
                'drought': 'kusanaya kwemvura'
            },
            'ndebele': {
                'maize': 'umbila',
                'crop': 'isivuno / izilimo',
                'soil': 'umhlabathi',
                'fertilizer': 'umanyolo',
                'planting': 'ukuhlwanyela',
                'harvest': 'ukuvuna',
                'rain': 'imvula',
                'farmer': 'umlimi',
                'field': 'insimu',
                'seed': 'inhlanyelo',
                'cattle': 'inkomo',
                'drought': 'isomiso'
            }
        }
    
    def extract_key_points(self, text: str) -> str:
        """Extract 2-3 key actionable points from the response."""
        prompt = f"""Extract 2-3 key actionable recommendations from this agricultural advice.
Make them brief, practical, and suitable for translation.

Text: {text}

Key Points (numbered list):"""
        
        try:
            response = self.client.generate(
                model=self.llm_model,
                prompt=prompt,
                options={'temperature': 0.3}
            )
            return response['response'].strip()
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            # Fallback: take first 200 chars
            return text[:200] + "..."
    
    def translate_to_shona(self, text: str) -> str:
        """Translate agricultural advice to Shona."""
        # Include glossary context
        glossary_context = "\\n".join([f"{en} = {sn}" for en, sn in self.agricultural_glossary['shona'].items()])
        
        prompt = f"""Translate this agricultural advice into Shona (ChiShona).
Keep it simple, clear, and practical for Zimbabwean farmers.
Use these common agricultural terms:

{glossary_context}

English text: {text}

Shona translation:"""
        
        try:
            response = self.client.generate(
                model=self.llm_model,
                prompt=prompt,
                options={'temperature': 0.5}
            )
            return response['response'].strip()
        except Exception as e:
            logger.error(f"Error translating to Shona: {e}")
            return f"[Translation unavailable: {str(e)}]"
    
    def translate_to_ndebele(self, text: str) -> str:
        """Translate agricultural advice to Ndebele."""
        # Include glossary context
        glossary_context = "\\n".join([f"{en} = {nd}" for en, nd in self.agricultural_glossary['ndebele'].items()])
        
        prompt = f"""Translate this agricultural advice into Ndebele (IsiNdebele).
Keep it simple, clear, and practical for Zimbabwean farmers.
Use these common agricultural terms:

{glossary_context}

English text: {text}

Ndebele translation:"""
        
        try:
            response = self.client.generate(
                model=self.llm_model,
                prompt=prompt,
                options={'temperature': 0.5}
            )
            return response['response'].strip()
        except Exception as e:
            logger.error(f"Error translating to Ndebele: {e}")
            return f"[Translation unavailable: {str(e)}]"
    
    def generate_multilingual_summary(
        self,
        full_response: str,
        include_shona: bool = True,
        include_ndebele: bool = True
    ) -> Dict[str, str]:
        """
        Generate a multilingual summary with English, Shona, and Ndebele.
        
        Returns:
            Dict with 'english', 'shona', and 'ndebele' keys
        """
        # Extract key points
        key_points = self.extract_key_points(full_response)
        
        result = {
            'english': key_points
        }
        
        if include_shona:
            logger.info("Translating to Shona...")
            result['shona'] = self.translate_to_shona(key_points)
        
        if include_ndebele:
            logger.info("Translating to Ndebele...")
            result['ndebele'] = self.translate_to_ndebele(key_points)
        
        return result
    
    def format_for_display(self, translations: Dict[str, str]) -> str:
        """Format multilingual summary for display."""
        output = []
        
        if 'english' in translations:
            output.append("📋 **Key Points (English)**")
            output.append(translations['english'])
            output.append("")
        
        if 'shona' in translations:
            output.append("🇿🇼 **Zvakakoshwa (ChiShona)**")
            output.append(translations['shona'])
            output.append("")
        
        if 'ndebele' in translations:
            output.append("🇿🇼 **Okubalulekileyo (IsiNdebele)**")
            output.append(translations['ndebele'])
            output.append("")
        
        return "\\n".join(output)


class QuickPhraseTranslator:
    """Quick translation for common farming phrases without LLM."""
    
    COMMON_PHRASES = {
        'Plant now': {
            'shona': 'Dyara izvozvi',
            'ndebele': 'Hlwanyela manje'
        },
        'Good time to plant': {
            'shona': 'Inguva yakanaka yekudyara',
            'ndebele': 'Yisikhathi esihle sokuhlwanyela'
        },
        'Use fertilizer': {
            'shona': 'Shandisa fetiraiza',
            'ndebele': 'Sebenzisa umanyolo'
        },
        'Wait for rain': {
            'shona': 'Mirira mvura',
            'ndebele': 'Linda imvula'
        },
        'Too late to plant': {
            'shona': 'Kwaneta kudyara',
            'ndebele': 'Sekwephuze isikhathi sokuhlwanyela'
        },
        'Consult extension officer': {
            'shona': 'Bvunza extension officer',
            'ndebele': 'Buza i-extension officer'
        }
    }
    
    @classmethod
    def get_phrase(cls, phrase: str, language: str = 'shona') -> Optional[str]:
        """Get quick translation for common phrase."""
        return cls.COMMON_PHRASES.get(phrase, {}).get(language)


if __name__ == "__main__":
    # Test the translator
    translator = LocalLanguageTranslator()
    
    test_text = """For maize planting in Bulawayo this month, it's important to:
1. Ensure soil moisture is adequate before planting
2. Use certified seed varieties suitable for Natural Region V
3. Apply basal fertilizer at planting time"""
    
    print("Testing Local Language Translation:")
    print("=" * 50)
    
    result = translator.generate_multilingual_summary(test_text)
    formatted = translator.format_for_display(result)
    print(formatted)
