from typing import List
from translate import Translator

class LanguageService:
    SUPPORTED_LANGUAGES = {
        'es': 'Castellano',
        'en': 'English',
        'fr': 'Français',
        'it': 'Italiano'
    }
    
    def __init__(self):
        self.translators = {
            lang: Translator(to_lang=lang) 
            for lang in self.SUPPORTED_LANGUAGES.keys()
        }
    
    def translate_content(self, content: str, target_language: str) -> str:
        if target_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {target_language}")
            
        translator = self.translators[target_language]
        return translator.translate(content)