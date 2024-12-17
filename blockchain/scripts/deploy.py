
from web3 import Web3
from eth_account import Account
from eth_utils import to_checksum_address
import json
import os
from dotenv import load_dotenv
import time

MUMBAI_RPC_URLS = [
    'https://rpc-mumbai.maticvigil.com',
    'https://polygon-mumbai.blockpi.network/v1/rpc/public',
    'https://polygon-mumbai.g.alchemy.com/v2/demo',
    'https://polygon-testnet.public.blastapi.io'
]

def get_working_web3():
    for rpc_url in MUMBAI_RPC_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
            if w3.is_connected():
                print(f"Connected successfully to: {rpc_url}")
                return w3
        except Exception as e:
            print(f"RPC {rpc_url} not available: {str(e)}")
            continue
    return None

def deploy_contract():
    try:
        load_dotenv()
        
        w3 = get_working_web3()
        if not w3:
            raise ConnectionError("No RPC available. Try again later.")
            
        chain_id = w3.eth.chain_id
        print(f"Connected to chain ID: {chain_id}")
        if chain_id != 80001:
            raise ValueError(f"Wrong chain ID. Expected 80001 (Mumbai), got {chain_id}")
            
        private_key = os.getenv('POLYGON_PRIVATE_KEY')
        if not private_key or not private_key.startswith('0x'):
            raise ValueError("POLYGON_PRIVATE_KEY must be a valid hex string starting with '0x'")
        
        account = Account.from_key(private_key)
        print(f"Account address: {account.address}")
        
        balance = w3.eth.get_balance(account.address)
        balance_matic = w3.from_wei(balance, 'ether')
        print(f"Balance: {balance_matic} MATIC")
        
        if balance_matic < 0.1:
            raise ValueError("Insufficient balance. Need at least 0.1 MATIC for deployment")
        
        contract_path = 'blockchain/contracts/GoldSystem.json'
        if not os.path.exists(contract_path):
            raise FileNotFoundError(f"Contract file not found: {contract_path}")
            
        with open(contract_path) as file:
            contract_data = json.load(file)
            
        if 'bytecode' not in contract_data or 'abi' not in contract_data:
            raise ValueError("Contract file must contain 'bytecode' and 'abi'")
        
        print("Preparing deployment...")
        contract = w3.eth.contract(
            abi=contract_data['abi'],
            bytecode=contract_data['bytecode']
        )
        
        gas_estimate = contract.constructor().estimate_gas() + 100000
        gas_price = w3.eth.gas_price
        total_cost = w3.from_wei(gas_estimate * gas_price, 'ether')
        print(f"Estimated deployment cost: {total_cost} MATIC")
        
        nonce = w3.eth.get_transaction_count(account.address)
        transaction = {
            'from': account.address,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': chain_id
        }
        
        print("Sending transaction...")
        contract_tx = contract.constructor().build_transaction(transaction)
        signed_tx = account.sign_transaction(contract_tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"Transaction sent: {tx_hash.hex()}")
        print("Waiting for confirmation...")
        
        for i in range(30):
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    contract_address = receipt['contractAddress']
                    print(f"Contract deployed to: {contract_address}")
                    
                    with open('deployed_contract.json', 'w') as f:
                        json.dump({
                            'address': contract_address,
                            'network': 'mumbai',
                            'deployer': account.address,
                            'timestamp': time.time()
                        }, f, indent=2)
                        
                    return contract_address
            except Exception:
                print(".", end="", flush=True)
                time.sleep(10)
                continue
                
        raise TimeoutError("Timeout waiting for confirmation")
        
    except Exception as e:
        print(f"Error during deployment: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        address = deploy_contract()
        print(f"Deployment completed successfully at: {address}")
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
