
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

def deploy_contract():
    try:
        print("\nStarting deployment process...")
        load_dotenv()

        w3 = Web3(Web3.HTTPProvider(MUMBAI_RPC_URLS[0]))
        if not w3.is_connected():
            raise ConnectionError("Could not connect to Polygon Mumbai")

        private_key = os.getenv('POLYGON_PRIVATE_KEY')
        if not private_key:
            raise ValueError("POLYGON_PRIVATE_KEY not found in environment")
        account = Account.from_key(private_key)

        with open('blockchain/contracts/GoldSystem.sol') as f:
            contract_source = f.read()

        # Compile the contract using solc
        compiled_sol = compile_source(contract_source)
        contract_interface = compiled_sol['<stdin>:NobleGoldSystem']

        contract = w3.eth.contract(
            abi=contract_interface['abi'],
            bytecode=contract_interface['bin']
        )

        transaction = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': w3.eth.gas_price
        })

        signed_txn = account.sign_transaction(transaction)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        print(f"Contract deployment transaction sent: {tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        contract_address = receipt['contractAddress']
        print(f"Contract deployed to: {contract_address}")

        deployment_info = {
            'address': contract_address,
            'network': 'mumbai',
            'deployer': account.address,
            'timestamp': time.time()
        }

        with open('deployment.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)

        return contract_address

    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        raise

if __name__ == '__main__':
    deploy_contract()
