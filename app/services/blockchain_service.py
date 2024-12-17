
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from decimal import Decimal
import json
import asyncio

class BlockchainService:
    def __init__(self, app=None):
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        self.web3 = Web3(Web3.HTTPProvider(app.config['POLYGON_RPC_URL']))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        with open('blockchain/contracts/GoldSystem.json') as f:
            contract_json = json.load(f)
        self.contract = self.web3.eth.contract(
            address=app.config['SMART_CONTRACT_ADDRESS'],
            abi=contract_json['abi']
        )
        
        self.owner_account = Account.from_key(app.config['POLYGON_PRIVATE_KEY'])
        self.batch_size = 50
        self.max_gas_price = app.config.get('MAX_GAS_PRICE_GWEI', 50)
        self.estimated_gas_per_tx = 100000
        
    def estimate_batch_cost(self, num_transactions):
        gas_price_wei = self.web3.eth.gas_price
        total_gas = self.estimated_gas_per_tx * num_transactions
        cost_matic = self.web3.from_wei(gas_price_wei * total_gas, 'ether')
        return float(cost_matic)
    
    async def process_batch(self, transformations):
        try:
            if not transformations:
                return {'status': 'success', 'message': 'No transactions to process'}
                
            gas_price = self.web3.eth.gas_price
            max_gas_price_wei = self.web3.to_wei(self.max_gas_price, 'gwei')
            
            if gas_price > max_gas_price_wei:
                return {
                    'status': 'delayed',
                    'message': f'Gas price too high: {self.web3.from_wei(gas_price, "gwei")} Gwei'
                }
            
            users = []
            euro_amounts = []
            gold_amounts = []
            
            for tx in transformations[:self.batch_size]:
                users.append(self.web3.to_checksum_address(tx['user_address']))
                euro_amounts.append(int(Decimal(tx['euro_amount']) * 100))
                gold_amounts.append(int(Decimal(tx['gold_amount']) * 10000))
            
            nonce = self.web3.eth.get_transaction_count(self.owner_account.address)
            
            contract_tx = self.contract.functions.batchTransform(
                users,
                euro_amounts,
                gold_amounts,
                int(Decimal(transformations[0]['fixing_price']) * 100)
            ).build_transaction({
                'from': self.owner_account.address,
                'gas': len(users) * self.estimated_gas_per_tx,
                'gasPrice': gas_price,
                'nonce': nonce,
                'maxFeePerGas': max_gas_price_wei,
                'maxPriorityFeePerGas': self.web3.to_wei(1, 'gwei')
            })
            
            signed_tx = self.owner_account.sign_transaction(contract_tx)
            tx_hash = await self._send_transaction(signed_tx.rawTransaction)
            receipt = await self._wait_for_transaction(tx_hash, timeout=60)
            
            if receipt['status'] == 1:
                batch_cost = self.estimate_batch_cost(len(users))
                return {
                    'status': 'success',
                    'transaction_hash': tx_hash.hex(),
                    'block_number': receipt['blockNumber'],
                    'cost_matic': batch_cost,
                    'cost_per_tx': batch_cost / len(users)
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Transaction reverted'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def _wait_for_transaction(self, transaction_hash, timeout=60):
        start_time = asyncio.get_event_loop().time()
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Transaction not mined after {timeout} seconds")
            
            try:
                receipt = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.web3.eth.get_transaction_receipt,
                    transaction_hash
                )
                if receipt:
                    return receipt
            except Exception:
                pass
            await asyncio.sleep(0.5)
