from typing import Dict, Any
from web3 import Web3
import os
from app.utils.errors import ValidationError
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

    def validate_blockchain_config() -> bool:
        try:
            w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_ENDPOINTS').split(',')[0]))
            return w3.is_connected()
        except Exception as e:
            self.logger.error(f"Blockchain validation failed: {str(e)}")
            return False

    def validate_structure(self) -> Dict[str, bool]:
        """Valida l'intera struttura del progetto"""
        results = {
            'contracts': self.validate_contracts(), #Assuming this function exists elsewhere
            'services': self.validate_services(), #Assuming this function exists elsewhere
            'models': self.validate_models(), #Assuming this function exists elsewhere
            'api': self.validate_api_structure(), #Assuming this function exists elsewhere
            'blockchain': self.validate_blockchain_config()
        }
        return results
        
    
    def log_modification(self, file_path: str, modification_type: str):
        """Logga ogni modifica al codice"""
        self.logger.info(f"Code modification: {modification_type} in {file_path}")