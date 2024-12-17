
from web3 import Web3
from eth_account import Account
from eth_utils import to_checksum_address
import json
import os
from dotenv import load_dotenv
from solcx import compile_source

def deploy_contract():
    try:
        load_dotenv()
        
        private_key = os.getenv('POLYGON_PRIVATE_KEY')
        if not private_key or not private_key.startswith('0x'):
            raise ValueError("POLYGON_PRIVATE_KEY deve essere una stringa hex valida che inizia con '0x'")
            
        w3 = Web3(Web3.HTTPProvider(os.getenv('POLYGON_RPC_URL')))
        if not w3.is_connected():
            raise ConnectionError("Impossibile connettersi alla rete Polygon")
            
        account = Account.from_key(private_key)
        print(f"Deploying from address: {account.address}")
        
        with open('blockchain/contracts/GoldSystem.sol') as file:
            solidity_file = file.read()
            
        print("Compilando il contratto...")
        compiled_sol = compile_source(
            solidity_file,
            output_values=['abi', 'bin']
        )
        contract_interface = compiled_sol['<stdin>:GoldSystem']
        
        GoldSystem = w3.eth.contract(
            abi=contract_interface['abi'],
            bytecode=contract_interface['bin']
        )
        
        gas_estimate = GoldSystem.constructor().estimate_gas()
        print(f"Gas stimato per il deploy: {gas_estimate}")
        
        transaction = {
            'from': account.address,
            'gas': gas_estimate,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address)
        }
        
        print("Deploying contract...")
        contract_tx = GoldSystem.constructor().build_transaction(transaction)
        signed_tx = account.sign_transaction(contract_tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print("Waiting for confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        contract_address = tx_receipt['contractAddress']
        print(f"Contract deployed at: {contract_address}")
        
        with open('contract_address.txt', 'w') as f:
            f.write(contract_address)
            
        with open('blockchain/contracts/GoldSystem.json', 'w') as f:
            json.dump(contract_interface['abi'], f, indent=2)
            
        print("Deploy completato con successo!")
        return contract_address
        
    except Exception as e:
        print(f"Errore durante il deploy: {str(e)}")
        raise

if __name__ == '__main__':
    deploy_contract()
