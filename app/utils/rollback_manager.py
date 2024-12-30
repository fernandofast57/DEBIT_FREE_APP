
import logging
from typing import Any, Dict, List
from datetime import datetime
from app.database import db
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class RollbackManager:
    def __init__(self):
        self.operations_log = []
        self.current_transaction = None
        
    @contextmanager
    def transaction(self, operation_name: str):
        try:
            self.current_transaction = {
                'name': operation_name,
                'timestamp': datetime.utcnow(),
                'changes': []
            }
            yield
            self.operations_log.append(self.current_transaction)
            self.current_transaction = None
        except Exception as e:
            if self.current_transaction:
                self._rollback_transaction(self.current_transaction)
            logger.error(f"Transaction failed: {str(e)}")
            raise
            
    def record_change(self, model: Any, operation: str, data: Dict):
        if self.current_transaction:
            self.current_transaction['changes'].append({
                'model': model.__class__.__name__,
                'operation': operation,
                'data': data,
                'timestamp': datetime.utcnow()
            })
            
    def _rollback_transaction(self, transaction: Dict):
        try:
            for change in reversed(transaction['changes']):
                if change['operation'] == 'insert':
                    self._delete_record(change['model'], change['data'])
                elif change['operation'] == 'update':
                    self._restore_record(change['model'], change['data'])
                elif change['operation'] == 'delete':
                    self._recreate_record(change['model'], change['data'])
                    
            db.session.commit()
            logger.info(f"Successfully rolled back transaction: {transaction['name']}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to rollback transaction: {str(e)}")
            
    def _delete_record(self, model_name: str, data: Dict):
        model = self._get_model_class(model_name)
        record = model.query.get(data['id'])
        if record:
            db.session.delete(record)
            
    def _restore_record(self, model_name: str, data: Dict):
        model = self._get_model_class(model_name)
        record = model.query.get(data['id'])
        if record:
            for key, value in data['previous_state'].items():
                setattr(record, key, value)
                
    def _recreate_record(self, model_name: str, data: Dict):
        model = self._get_model_class(model_name)
        new_record = model(**data['state'])
        db.session.add(new_record)
        
    def _get_model_class(self, model_name: str) -> Any:
        import app.models.models as models
        return getattr(models, model_name)

rollback_manager = RollbackManager()
