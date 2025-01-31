
from datetime import datetime
from app.models.contract import Contract
from app.database import db
from app.utils.audit_logger import audit_logger

class ContractService:
    @staticmethod
    async def send_contract(user_id: int, contract_file_path: str) -> dict:
        """Send contract to user"""
        contract = Contract(
            user_id=user_id,
            status='inviato',
            contract_file_path=contract_file_path,
            sent_date=datetime.utcnow(),
            contract_number=f"CNT-{user_id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        )
        
        db.session.add(contract)
        await db.session.commit()
        
        audit_logger.info(f"Contract sent to user {user_id}")
        return {"status": "success", "contract_id": contract.id}

    @staticmethod
    async def receive_signed_contract(contract_id: int) -> dict:
        """Process received signed contract"""
        contract = await Contract.query.get(contract_id)
        if not contract:
            raise ValueError("Contract not found")
            
        contract.status = 'firmato'
        contract.received_date = datetime.utcnow()
        await db.session.commit()
        
        audit_logger.info(f"Signed contract received for user {contract.user_id}")
        return {"status": "success", "message": "Contract processed successfully"}
