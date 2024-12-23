
from decimal import Decimal
from typing import Dict
from app.utils.structure_validator import StructureValidator

class BonusValidator:
    def __init__(self):
        self.structure_validator = StructureValidator()
        
    def validate_bonus_calculation(self, purchase_amount: Decimal, level: int, bonus: Decimal) -> bool:
        """Validate bonus calculation for a specific level according to glossary"""
        if level < 1 or level > 3:
            return False
            
        # Get rates from structure validator
        bonus_rates = {
            1: Decimal('0.05'),  # 5% for level 1
            2: Decimal('0.03'),  # 3% for level 2
            3: Decimal('0.02')   # 2% for level 3
        }
        
        expected_bonus = purchase_amount * bonus_rates[level]
        return abs(expected_bonus - bonus) < Decimal('0.00001')
        
    def validate_distribution(self, distribution_results: Dict) -> bool:
        """Validate complete bonus distribution including noble ranks"""
        if not distribution_results:
            return False
            
        for result in distribution_results.values():
            if not (1 <= result['level'] <= 3):
                return False
            if result.get('noble_rank') and not self.validate_noble_bonus(result['noble_rank']):
                return False
        return True
        
    def validate_noble_bonus(self, noble_rank: str) -> bool:
        """Validate noble rank bonus according to glossary"""
        valid_ranks = ['Bronze', 'Silver', 'Gold', 'Platinum']
        return noble_rank in valid_ranks
