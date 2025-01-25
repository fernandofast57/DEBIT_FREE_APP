import logging
from datetime import datetime
from typing import Dict, Any
from app.utils.structure_validator import StructureValidator
from app.services import BlockchainService

class ValidationReport:
    def __init__(self):
        self.validation_status = 'pending'  # ['pending', 'completed', 'rejected']
        self.validation_results = {}
        self.timestamp = datetime.utcnow()
        self.logger = logging.getLogger(__name__)
        self.structure_validator = StructureValidator()
        self.blockchain_service = BlockchainService()

    async def generate_report(self) -> Dict[str, Any]:
        try:
            structure_results = await self.structure_validator.validate_structure()
            blockchain_results = await self.blockchain_service.validate_chain()

            self.validation_results = {
                'structure': structure_results,
                'blockchain': blockchain_results,
                'timestamp': self.timestamp.isoformat()
            }

            self.validation_status = 'verified' if all(self.validation_results.values()) else 'rejected'

            return {
                'status': self.validation_status,
                'results': self.validation_results
            }
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return {
                'status': 'rejected',
                'error': str(e)
            }