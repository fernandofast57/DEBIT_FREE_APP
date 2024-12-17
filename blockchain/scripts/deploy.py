
from web3 import Web3
from eth_account import Account
import json
import os
from pathlib import Path

def deploy_contract():
    # Connessione a Polygon Mumbai
    w3 = Web3(Web3.HTTPProvider(os.getenv('POLYGON_RPC_URL')))
    account = Account.from_key(os.getenv('POLYGON_PRIVATE_KEY'))
    
    # Compila il contratto
    contract_path = Path('blockchain/contracts/GoldSystem.sol')
    
    # Leggi il bytecode e ABI
    with open('blockchain/contracts/GoldSystem.json') as f:
        contract_json = json.load(f)
    
    Contract = w3.eth.contract(
        abi=contract_json['abi'],
        bytecode=contract_json['bytecode']
    )
    
    # Costruisci la transazione
    transaction = Contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'maxFeePerGas': w3.to_wei(50, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(1, 'gwei')
    })
    
    # Firma e invia
    signed_txn = account.sign_transaction(transaction)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Attendi la conferma
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contratto deployato su: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

if __name__ == "__main__":
    deploy_contract()
