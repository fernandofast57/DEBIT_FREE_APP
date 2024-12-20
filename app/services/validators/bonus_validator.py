
from decimal import Decimal
from typing import Dict
from app.utils.structure_validator import StructureValidator

class BonusValidator:
    def __init__(self):
        self.structure_validator = StructureValidator()
        
    def validate_bonus_calculation(self, purchase_amount: Decimal, level: int, bonus: Decimal) -> bool:
        """Validate bonus calculation for a specific level"""
        if level < 1 or level > 3:
            return False
            
        expected_rate = Decimal(self.structure_validator.config['allowed_modifications']['bonus_system']['rates'][f'level{level}']) / 100
        expected_bonus = purchase_amount * expected_rate
        
        return abs(expected_bonus - bonus) < Decimal('0.00001')  # Tolerance for floating point
        
    def validate_distribution(self, distribution_results: Dict) -> bool:
        """Validate complete bonus distribution"""
        return all(1 <= result['level'] <= 3 for result in distribution_results.values())
