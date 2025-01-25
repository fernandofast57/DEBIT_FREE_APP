import logging
from datetime import datetime
from app.utils.structure_validator import StructureValidator
from app.services.blockchain_service import BlockchainService
from app.services.batch_collection_service import BatchCollectionService
from app.utils.logging_config import GlossaryComplianceLogger

class ValidationReport:
    def __init__(self):
        self.validation_status = None
        self.validation_results = {}
        self.logger = logging.getLogger(__name__)
        self.structure_validator = StructureValidator()
        self.blockchain_service = BlockchainService()
        self.batch_service = BatchCollectionService()

    async def generate_report(self):
        compliance_logger = GlossaryComplianceLogger()

        # Validate components
        structure_results = self.structure_validator.validate_structure()
        blockchain_results = await self._validate_blockchain()
        batch_results = await self._validate_batch_system()

        # Log compliance for each component
        compliance_logger.log_validation('structure', structure_results)
        compliance_logger.log_validation('blockchain', blockchain_results)
        compliance_logger.log_validation('batch_system', batch_results)

        results = {
            'structure': structure_results,
            'blockchain': blockchain_results,
            'batch_system': batch_results,
            'timestamp': datetime.utcnow().isoformat()
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
import json
from datetime import datetime
from typing import Dict, Any

class ValidationReport:
    def __init__(self):
        self.validations = []
        self.timestamp = datetime.utcnow()

    def add_validation(self, feature: str, result: bool, details: Dict[str, Any]):
        self.validations.append({
            "feature": feature,
            "passed": result,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

    def generate_report(self) -> Dict[str, Any]:
        return {
            "report_id": str(self.timestamp.timestamp()),
            "validations": self.validations,
            "summary": {
                "total": len(self.validations),
                "passed": len([v for v in self.validations if v["passed"]]),
                "failed": len([v for v in self.validations if not v["passed"]])
            }
        }

    def save_report(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.generate_report(), f, indent=2)