
import json
import os

class StructureValidator:
    def __init__(self):
        with open('app/config/project_structure.json') as f:
            self.config = json.load(f)
    
    def validate_modification(self, file_path: str) -> bool:
        return file_path in self.config['allowed_modifications']['allowed_modules']
    
    def validate_bonus_rate(self, level: int, rate: float) -> bool:
        rates = self.config['allowed_modifications']['bonus_system']['rates']
        return rate == rates[f'level{level}']

    def validate_levels(self, levels: int) -> bool:
        return levels == self.config['allowed_modifications']['bonus_system']['levels']
