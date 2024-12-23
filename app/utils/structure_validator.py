
from typing import Dict, Any
from web3 import Web3
import os
from app.utils.errors import ValidationError
import json
import logging
from app.models.models import NobleRelation, Transaction, GoldTransformation
from sqlalchemy import inspect

class StructureValidator:
    def __init__(self):
        self.logger = logging.getLogger('structure_validator')
        with open('app/config/project_structure.json') as f:
            self.config = json.load(f)
        with open('docs/GLOSSARY.md', 'r') as f:
            self.glossary = f.read()
    
    def validate_model_names(self) -> Dict[str, bool]:
        """Validates model names against glossary definitions"""
        results = {}
        inspector = inspect(NobleRelation)
        
        # Check core models
        model_checks = {
            'NobleRelation': ['noble_relations', 'verification_status'],
            'Transaction': ['transactions', 'status'],
            'GoldTransformation': ['gold_transformations', 'fixing_price']
        }
        
        for model_name, attributes in model_checks.items():
            table_name = attributes[0]
            status_field = attributes[1]
            results[model_name] = {
                'table_name_valid': table_name in self.glossary.lower(),
                'status_field_valid': status_field in self.glossary.lower()
            }
            
        return results

    def validate_status_codes(self, status: str) -> bool:
        """Validates status codes against glossary definitions"""
        valid_statuses = [
            'to_be_verified', 'verified', 'rejected',
            'available', 'reserved', 'distributed'
        ]
        return status in valid_statuses
    
    def validate_modification(self, file_path: str) -> bool:
        """Validates if a file can be modified"""
        return file_path in self.config['allowed_modifications']['allowed_modules']
    
    def validate_bonus_rate(self, level: int, rate: float) -> bool:
        """Validates bonus rates"""
        rates = self.config['allowed_modifications']['bonus_system']['rates']
        return rate == rates[f'level{level}']

    def validate_blockchain_config(self) -> bool:
        try:
            w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_ENDPOINTS').split(',')[0]))
            return w3.is_connected()
        except Exception as e:
            self.logger.error(f"Blockchain validation failed: {str(e)}")
            return False

    def validate_structure(self) -> Dict[str, bool]:
        """Validates entire project structure"""
        results = {
            'models': self.validate_model_names(),
            'blockchain': self.validate_blockchain_config(),
            'status_codes': all(self.validate_status_codes(status) 
                              for status in ['verified', 'to_be_verified', 'rejected'])
        }
        return results
        
    def log_modification(self, file_path: str, modification_type: str):
        """Logs code modifications"""
        self.logger.info(f"Code modification: {modification_type} in {file_path}")
