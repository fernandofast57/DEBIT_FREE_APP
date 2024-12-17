
import os

def create_directory_structure():
    # Directory structure
    directories = [
        'app',
        'app/api/v1',
        'app/models',
        'app/routes',
        'app/services',
        'app/utils',
        'blockchain/contracts',
        'blockchain/scripts',
        'migrations',
        'tests',
        'logs'
    ]
    
    test_files = [
        'test_complete_system.py',
        'test_api.py',
        'test_blockchain_integration.py',
        'test_system_flow.py'
    ]

    services = [
        'batch_collection_service.py',
        'blockchain_service.py',
        'bonus_distribution_service.py',
        'transformation_service.py'
    ]

    api_files = [
        'bonuses.py',
        'transfers.py',
        'transformations.py'
    ]

    util_files = [
        'auth.py',
        'errors.py',
        'logging_config.py'
    ]

    model_files = [
        'user.py',
        'account.py',
        'transaction.py',
        'affiliate.py',
        'noble_system.py',
        'models.py'
    ]

    root_files = [
        'requirements.txt',
        'wsgi.py',
        'config.py'
    ]

    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        with open(f"{directory}/__init__.py", 'w') as f:
            f.write('# Package initialization\n')

    # Create test files
    for test_file in test_files:
        path = f"tests/{test_file}"
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(f'# Test file: {test_file}\n')

    # Create service files
    for service in services:
        path = f"app/services/{service}"
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(f'# Service: {service}\n')

    # Create API files
    for api_file in api_files:
        path = f"app/api/v1/{api_file}"
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(f'# API Endpoint: {api_file}\n')

    # Create utility files
    for util_file in util_files:
        path = f"app/utils/{util_file}"
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(f'# Utility: {util_file}\n')

    # Create model files
    for model_file in model_files:
        path = f"app/models/{model_file}"
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(f'# Model: {model_file}\n')

    # Create root files
    for root_file in root_files:
        if not os.path.exists(root_file):
            with open(root_file, 'w') as f:
                f.write(f'# Root file: {root_file}\n')

    # Create migration readme
    with open('migrations/README', 'w') as f:
        f.write('Alembic migrations directory\n')

    # Create example smart contract
    with open('blockchain/contracts/GoldSystem.sol', 'w') as f:
        f.write('// Smart contract per il sistema Gold\n')

    print("Project structure created successfully!")

if __name__ == "__main__":
    create_directory_structure()
