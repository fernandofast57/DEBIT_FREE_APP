
from functools import wraps
from flask import request, g
from app.utils.audit_logger import audit_logger
from datetime import datetime

def validate_transaction_flow():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            transaction_id = request.headers.get('X-Transaction-ID')
            
            # Fase 1: Validazione iniziale
            audit_logger.log_action(
                'TRANSACTION_START',
                g.user.id,
                f"Inizio validazione transazione {transaction_id}"
            )
            
            # Fase 2: Verifica saldi
            balance_check = verify_account_balances()
            if not balance_check['valid']:
                audit_logger.log_action(
                    'TRANSACTION_FAILED',
                    g.user.id,
                    f"Validazione saldi fallita: {balance_check['reason']}"
                )
                return balance_check['response']
            
            # Fase 3: Esecuzione transazione
            result = f(*args, **kwargs)
            
            # Fase 4: Registrazione esito
            audit_logger.log_action(
                'TRANSACTION_COMPLETE',
                g.user.id,
                f"Transazione {transaction_id} completata"
            )
            
            return result
        return decorated_function
    return decorator

def verify_account_balances():
    """Verifica la disponibilità dei saldi"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        
        if g.user.money_account.balance < amount:
            return {
                'valid': False,
                'reason': 'Saldo insufficiente',
                'response': {'error': 'Saldo insufficiente'}, 'status': 400
            }
            
        return {'valid': True}
    except Exception as e:
        return {
            'valid': False,
            'reason': str(e),
            'response': {'error': 'Errore nella verifica dei saldi'}, 'status': 500
        }
