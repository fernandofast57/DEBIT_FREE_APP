
from web3 import Web3
from eth_account import Account
import json
import os
from dotenv import load_dotenv

def deploy_contract():
    load_dotenv()
    
    w3 = Web3(Web3.HTTPProvider(os.getenv('POLYGON_RPC_URL')))
    account = Account.from_key(os.getenv('POLYGON_PRIVATE_KEY'))
    
    # Leggi ABI e bytecode
    with open('blockchain/contracts/GoldSystem.abi', 'r') as f:
        abi = f.read()
    with open('blockchain/contracts/GoldSystem.bin', 'r') as f:
        bytecode = f.read()
    
    Contract = w3.eth.contract(
        abi=abi,
        bytecode=bytecode
    )
    
    transaction = Contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'maxFeePerGas': w3.to_wei(50, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(1, 'gwei')
    })
    
    signed_txn = account.sign_transaction(transaction)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contratto deployato su: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

if __name__ == "__main__":
    deploy_contract()
