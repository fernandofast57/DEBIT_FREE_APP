
from typing import Dict, List
import json
import logging

class StructureValidator:
    def __init__(self):
        self.logger = logging.getLogger('structure_validator')
        with open('app/config/project_structure.json') as f:
            self.config = json.load(f)
    
    def validate_modification(self, file_path: str) -> bool:
        """Valida se un file può essere modificato"""
        return file_path in self.config['allowed_modifications']['allowed_modules']
    
    def validate_bonus_rate(self, level: int, rate: float) -> bool:
        """Valida i tassi di bonus"""
        rates = self.config['allowed_modifications']['bonus_system']['rates']
        return rate == rates[f'level{level}']

    def validate_structure(self) -> Dict[str, bool]:
        """Valida l'intera struttura del progetto"""
        results = {
            'contracts': self.validate_contracts(),
            'services': self.validate_services(),
            'models': self.validate_models(),
            'api': self.validate_api_structure()
        }
        return results
    
    def log_modification(self, file_path: str, modification_type: str):
        """Logga ogni modifica al codice"""
        self.logger.info(f"Code modification: {modification_type} in {file_path}")
