
import json
import logging
from pathlib import Path

class StandardsChecker:
    def __init__(self):
        self.logger = logging.getLogger('standards_checker')
        self.standards = self._load_standards()
        self.glossary = self._load_glossary()
        
    def _load_standards(self):
        try:
            with open('docs/OFFICIAL_STANDARDS.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load standards: {e}")
            return {}
            
    def _load_glossary(self):
        try:
            with open('docs/GLOSSARY.md', 'r', encoding='utf-8') as f:
                return f.read().lower()
        except Exception as e:
            self.logger.error(f"Failed to load glossary: {e}")
            return ""
            
    def validate_name(self, name: str) -> bool:
        return (
            name in self.glossary or
            name in str(self.standards)
        )
