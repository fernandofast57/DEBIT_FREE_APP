from typing import Dict, Any
from web3 import Web3
import os
from app.utils.errors import ValidationError
import json
import logging
from app.models.models import NobleRelation, Transaction, GoldTransformation
from sqlalchemy import inspect

class StructureValidator:
    def __init__(self):
        self.logger = logging.getLogger('structure_validator')
        with open('app/config/project_structure.json') as f:
            self.config = json.load(f)
        with open('docs/GLOSSARY.md', 'r') as f:
            self.glossary = f.read()
    
    def validate_model_names(self) -> Dict[str, bool]:
        """Validates model names against glossary definitions"""
        results = {}
        inspector = inspect(NobleRelation)
        
        # Check core models
        model_checks = {
            'NobleRelation': ['noble_relations', 'verification_status'],
            'Transaction': ['transactions', 'status'],
            'GoldTransformation': ['gold_transformations', 'fixing_price']
        }
        
        for model_name, attributes in model_checks.items():
            table_name = attributes[0]
            status_field = attributes[1]
            results[model_name] = {
                'table_name_valid': table_name in self.glossary.lower(),
                'status_field_valid': status_field in self.glossary.lower()
            }
            
        return results

    def validate_status_codes(self, status: str) -> bool:
        """Validates status codes against glossary definitions"""
        valid_statuses = [
            'to_be_verified', 'verified', 'rejected',
            'available', 'reserved', 'distributed'
        ]
        return status in valid_statuses
    
    def validate_modification(self, file_path: str) -> bool:
        """Validates if a file can be modified"""
        return file_path in self.config['allowed_modifications']['allowed_modules']
    
    def validate_bonus_rate(self, level: int, rate: float) -> bool:
        """Validates bonus rates"""
        rates = self.config['allowed_modifications']['bonus_system']['rates']
        return rate == rates[f'level{level}']

    def validate_blockchain_config(self) -> bool:
        try:
            w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_ENDPOINTS').split(',')[0]))
            return w3.is_connected()
        except Exception as e:
            self.logger.error(f"Blockchain validation failed: {str(e)}")
            return False

    def validate_service_names(self) -> Dict[str, bool]:
        """Validates service names against glossary definitions"""
        service_names = {
            'accounting': 'accounting_service',
            'transactions': 'transaction_validator',
            'transformation': 'transformation_service',
            'batch_collection': 'batch_collection_service',
            'bonus_distribution': 'bonus_distribution_service'
        }
        
        results = {}
        for glossary_name, service_name in service_names.items():
            results[service_name] = glossary_name in self.glossary.lower()
        return results

    def validate_api_endpoints(self) -> Dict[str, bool]:
        """Validates API endpoint names against glossary definitions"""
        endpoint_checks = {
            'auth_bp': '/auth',
            'gold_bp': '/gold',
            'affiliate_bp': '/affiliate',
            'noble_bp': '/noble',
            'transformations_bp': '/transformations',
            'transfers_bp': '/transfers',
            'bonuses_bp': '/bonuses',
            'system_bp': '/system'
        }
        
        results = {}
        for blueprint_name, endpoint in endpoint_checks.items():
            results[blueprint_name] = blueprint_name in self.glossary.lower()
        return results

    def validate_blockchain_transactions(self) -> Dict[str, bool]:
        """Validates blockchain transaction types against glossary"""
        transaction_types = {
            'gold_transfer': ['transfer', 'amount', 'recipient'],
            'noble_verification': ['noble_id', 'status', 'timestamp'],
            'gold_transformation': ['euro_amount', 'gold_grams', 'fixing_price']
        }
        
        results = {}
        for tx_type, fields in transaction_types.items():
            results[tx_type] = all(field in self.glossary.lower() for field in fields)
        return results

    def validate_schema_definitions(self) -> Dict[str, bool]:
        """Validates database schema definitions against glossary"""
        schema_checks = {
            'User': ['email', 'blockchain_address', 'noble_rank'],
            'MoneyAccount': ['balance', 'currency', 'user_id'],
            'GoldAccount': ['balance', 'user_id', 'last_updated'],
            'Transaction': ['amount', 'status', 'transaction_type'],
            'GoldTransformation': ['euro_amount', 'gold_grams', 'fixing_price']
        }
        
        results = {}
        for model_name, fields in schema_checks.items():
            results[model_name] = {
                'model_valid': model_name.lower() in self.glossary.lower(),
                'fields_valid': all(field in self.glossary.lower() for field in fields)
            }
        return results

    def validate_security_config(self) -> Dict[str, bool]:
        """Validates security configurations against glossary"""
        security_checks = {
            'rate_limiting': ['requests_per_minute', 'cooldown_period'],
            'authentication': ['jwt_expiration', 'refresh_token'],
            'noble_verification': ['kyc_status', 'verification_level'],
            'transaction_security': ['signature', 'nonce', 'timestamp']
        }
        
        results = {}
        for component, requirements in security_checks.items():
            results[component] = all(req in self.glossary.lower() for req in requirements)
        return results

    def validate_structure(self) -> Dict[str, bool]:
        """Validates entire project structure"""
        results = {
            'models': self.validate_model_names(),
            'schemas': self.validate_schema_definitions(),
            'services': self.validate_service_names(),
            'blockchain': self.validate_blockchain_config(),
            'endpoints': self.validate_api_endpoints(),
            'transactions': self.validate_blockchain_transactions(),
            'security': self.validate_security_config(),
            'business_rules': self.validate_business_rules(),
            'noble_system': self.validate_noble_system(),
            'bonus_system': self.validate_bonus_system(),
            'transactions': self.validate_transaction_processes(),
            'workflows': self.validate_workflow_processes(),
            'investments': self.validate_investment_tracking(),
            'performance': self.validate_performance_analytics(),
            'risk_assessment': self.validate_risk_assessment(),
            'status_codes': all(self.validate_status_codes(status) 
                              for status in ['verified', 'to_be_verified', 'rejected'])
        }
        return results

    def validate_business_rules(self) -> Dict[str, bool]:
        """Validates business rules and domain constraints against glossary"""
        business_rules = {
            'noble_ranks': ['bronze', 'silver', 'gold', 'platinum'],
            'gold_operations': ['buy', 'sell', 'transform', 'transfer'],
            'commission_types': ['fixed', 'percentage', 'tiered'],
            'transaction_limits': ['daily_limit', 'monthly_limit', 'minimum_amount']
        }
        
        results = {}
        for rule_type, terms in business_rules.items():
            results[rule_type] = all(term in self.glossary.lower() for term in terms)
        return results

    def validate_noble_system(self) -> Dict[str, bool]:
        """Validates noble system integration and verification process"""
        noble_checks = {
            'verification': ['kyc_status', 'document_verification', 'noble_verification'],
            'integration': ['blockchain_noble_service', 'noble_rank_service'],
            'processes': ['rank_upgrade', 'bonus_calculation', 'verification_workflow'],
            'documentation': ['document_type', 'document_number', 'verification_date']
        }
        
        results = {}
        for check_type, requirements in noble_checks.items():
            results[check_type] = all(req in self.glossary.lower() for req in requirements)
        return results
        
    def validate_bonus_system(self) -> Dict[str, bool]:
        """Validates bonus distribution system and rates"""
        bonus_checks = {
            'rates': ['client_share', 'network_share', 'operational_share'],
            'distribution': ['direct_bonus', 'network_bonus', 'leadership_bonus'],
            'calculations': ['volume_based', 'rank_based', 'time_based'],
            'conditions': ['minimum_volume', 'active_status', 'kyc_verified']
        }
        
        results = {}
        for check_type, requirements in bonus_checks.items():
            results[check_type] = all(req in self.glossary.lower() for req in requirements)
            
        # Validate bonus rates from config
        try:
            for level in range(1, self.config['allowed_modifications']['bonus_system']['levels'] + 1):
                rate_key = f'level{level}'
                if rate_key not in self.config['allowed_modifications']['bonus_system']['rates']:
                    results['rates'] = False
                    break
        except KeyError:
            results['rates'] = False
            
        return results

    def validate_transaction_processes(self) -> Dict[str, bool]:
        """Validates transaction processes and constraints"""
        transaction_checks = {
            'types': ['purchase', 'sale', 'transfer', 'transformation'],
            'validation': ['amount_check', 'balance_check', 'kyc_check'],
            'status_flow': ['pending', 'processing', 'completed', 'failed'],
            'security': ['signature_check', 'double_spend_check', 'rate_limit_check']
        }
        
        results = {}
        for check_type, requirements in transaction_checks.items():
            results[check_type] = all(req in self.glossary.lower() for req in requirements)
        return results

    def validate_workflow_processes(self) -> Dict[str, bool]:
        """Validates workflow processes and state transitions"""
        workflow_checks = {
            'states': ['initiated', 'validated', 'processed', 'completed'],
            'transitions': ['validate_kyc', 'process_payment', 'confirm_delivery'],
            'roles': ['user', 'admin', 'noble', 'system'],
            'triggers': ['user_action', 'system_event', 'time_based', 'condition_based']
        }
        
        results = {}
        for check_type, requirements in workflow_checks.items():
            results[check_type] = all(req in self.glossary.lower() for req in requirements)
        return results
        
    def validate_investment_tracking(self) -> Dict[str, bool]:
        """Validates investment tracking and performance metrics"""
        investment_checks = {
            'metrics': ['roi', 'current_value', 'purchase_price', 'holding_period'],
            'performance': ['daily_gain', 'monthly_gain', 'yearly_gain'],
            'analytics': ['market_price', 'volume_weighted_price', 'price_trends'],
            'reporting': ['investment_history', 'performance_report', 'tax_report']
        }
        
        results = {}
        for check_type, requirements in investment_checks.items():
            results[check_type] = all(req in self.glossary.lower() for req in requirements)
        return results

    def validate_performance_analytics(self) -> Dict[str, bool]:
        """Validates performance analytics system"""
        performance_checks = {
            'metrics': ['daily_performance', 'weekly_performance', 'monthly_performance'],
            'indicators': ['growth_rate', 'risk_metrics', 'volatility'],
            'benchmarks': ['market_comparison', 'peer_comparison', 'historical_performance'],
            'reporting': ['performance_summary', 'risk_report', 'trend_analysis']
        }
        
        results = {}
        for check_type, requirements in performance_checks.items():
            results[check_type] = all(req in self.glossary.lower() for req in requirements)
        return results

    def validate_risk_assessment(self) -> Dict[str, bool]:
        """Validates risk assessment system and parameters"""
        risk_checks = {
            'market_risk': ['price_volatility', 'market_liquidity', 'currency_risk'],
            'operational_risk': ['system_failure', 'process_error', 'human_error'],
            'compliance_risk': ['regulatory_changes', 'reporting_requirements', 'aml_compliance'],
            'investment_risk': ['concentration_risk', 'counterparty_risk', 'settlement_risk']
        }
        
        results = {}
        for check_type, requirements in risk_checks.items():
            results[check_type] = all(req in self.glossary.lower() for req in requirements)
        return results

    def log_modification(self, file_path: str, modification_type: str):
        """Logs code modifications"""
        self.logger.info(f"Code modification: {modification_type} in {file_path}")