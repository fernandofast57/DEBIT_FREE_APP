
from typing import Dict
from web3 import Web3
from app.utils.logging_config import logger

class ValidatoreBlockchain:
    """Validatore per le operazioni blockchain secondo glossario"""
    def __init__(self, web3_provider):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        
    def valida_transazione(self, tx_hash: str) -> Dict:
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            block_number = receipt.blockNumber
            confirmations = self.web3.eth.block_number - block_number

            return {
                'valido': receipt.status == 1,
                'stato': 'verificato' if receipt.status == 1 else 'rifiutato',
                'conferme': confirmations,
                'blocco': block_number,
                'gas_usato': receipt.gasUsed
            }
        except Exception as e:
            logger.error(f"Errore validazione tx {tx_hash}: {str(e)}")
            return {'valido': False, 'stato': 'errore', 'messaggio': str(e)}
