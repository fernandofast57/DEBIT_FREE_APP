
import logging
from app.utils.structure_validator import StructureValidator
from app.services.blockchain_service import BlockchainService
from app.services.batch_collection_service import BatchCollectionService

class ValidationReport:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.structure_validator = StructureValidator()
        self.blockchain_service = BlockchainService()
        self.batch_service = BatchCollectionService()

    async def generate_report(self):
        results = {
            'structure': self.structure_validator.validate_structure(),
            'blockchain': await self._validate_blockchain(),
            'batch_system': await self._validate_batch_system()
        }
        return results

    async def _validate_blockchain(self):
        try:
            return {
                'connection': self.blockchain_service.w3.is_connected(),
                'contract': bool(self.blockchain_service.contract)
            }
        except Exception as e:
            self.logger.error(f"Blockchain validation error: {str(e)}")
            return {'error': str(e)}

    async def _validate_batch_system(self):
        try:
            return await self.batch_service.validate_system_state()
        except Exception as e:
            self.logger.error(f"Batch system validation error: {str(e)}")
            return {'error': str(e)}
