
from web3 import Web3
from eth_account import Account
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

def test_rpc_connection(url):
    print(f"Testing RPC connection to {url}...")
    try:
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10}))
        if w3.is_connected():
            block = w3.eth.block_number
            print(f"✓ Connection successful. Current block: {block}")
            return w3
        else:
            print("✗ Connection failed: is_connected() returned False")
            return None
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return None

def get_working_web3():
    print("\nTesting RPC connections...")
    for url in MUMBAI_RPC_URLS:
        w3 = test_rpc_connection(url)
        if w3:
            return w3    
    return None

def deploy_contract():
    try:
        print("\nStarting deployment process...")
        load_dotenv()
        print("Environment variables loaded")
        
        w3 = get_working_web3()
        if not w3:
            raise ConnectionError("Could not connect to any RPC endpoint")
            
        chain_id = w3.eth.chain_id
        print(f"\nConnected to network with chain ID: {chain_id}")
        if chain_id != 80001:
            raise ValueError(f"Wrong network. Expected Mumbai (80001), got {chain_id}")
            
        private_key = os.getenv('POLYGON_PRIVATE_KEY')
        if not private_key:
            raise ValueError("POLYGON_PRIVATE_KEY not found in environment variables")
            
        if not private_key.startswith('0x'):
            private_key = f"0x{private_key}"
            
        account = Account.from_key(private_key)
        print(f"Deploying from account: {account.address}")
        
        balance = w3.eth.get_balance(account.address)
        balance_matic = w3.from_wei(balance, 'ether')
        print(f"Account balance: {balance_matic} MATIC")
        
        print("\nLoading contract data...")
        contract_path = 'blockchain/contracts/GoldSystem.json'
        if not os.path.exists(contract_path):
            raise FileNotFoundError(f"Contract file not found at: {contract_path}")
        
        with open(contract_path) as f:
            contract_data = json.load(f)
            
        print("Preparing contract deployment...")
        contract = w3.eth.contract(
            abi=contract_data['abi'],
            bytecode=contract_data['bytecode']
        )
        
        gas_estimate = contract.constructor().estimate_gas() + 100000
        gas_price = w3.eth.gas_price
        total_cost = w3.from_wei(gas_estimate * gas_price, 'ether')
        print(f"\nEstimated deployment cost: {total_cost} MATIC")
        
        nonce = w3.eth.get_transaction_count(account.address)
        transaction = {
            'from': account.address,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': chain_id
        }
        
        print("\nSending deployment transaction...")
        contract_tx = contract.constructor().build_transaction(transaction)
        signed_tx = account.sign_transaction(contract_tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction sent: {tx_hash.hex()}")
        
        print("\nWaiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt['status'] == 1:
            contract_address = receipt['contractAddress']
            print(f"\n✓ Contract deployed successfully!")
            print(f"Contract address: {contract_address}")
            
            deployment_info = {
                'address': contract_address,
                'network': 'mumbai',
                'deployer': account.address,
                'timestamp': time.time(),
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber']
            }
            
            with open('deployment.json', 'w') as f:
                json.dump(deployment_info, f, indent=2)
            print("\nDeployment info saved to deployment.json")
            
            return contract_address
        else:
            raise Exception("Contract deployment failed")
            
    except Exception as e:
        print(f"\nError during deployment: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        address = deploy_contract()
        print(f"\nDeployment successful! Contract address: {address}")
    except Exception as e:
        print(f"\nDeployment failed: {str(e)}")
