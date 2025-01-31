
import os
import ast
import json
from typing import Dict, List, Set

class CodebaseValidator:
    def __init__(self):
        self.standards = self._load_standards()
        self.issues = []
        
    def _load_standards(self) -> dict:
        with open('docs/OFFICIAL_STANDARDS.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_file(self, file_path: str) -> List[str]:
        if not file_path.endswith('.py'):
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._validate_class(node.name, file_path)
                elif isinstance(node, ast.FunctionDef):
                    self._validate_function(node.name, file_path)
                    
        except Exception as e:
            self.issues.append(f"Error processing {file_path}: {str(e)}")
            
    def _validate_class(self, name: str, file_path: str):
        standards = self.standards['standard_definitions']
        
        if name.startswith('Monitor'):
            if name not in standards['monitors']:
                self.issues.append(f"Non-standard monitor class '{name}' in {file_path}")
        elif name.startswith('Servizio'):
            if name not in standards['services']['core']:
                self.issues.append(f"Non-standard service class '{name}' in {file_path}")
        elif name.startswith('Validatore'):
            if name not in standards['services']['validators']:
                self.issues.append(f"Non-standard validator class '{name}' in {file_path}")
                
    def _validate_function(self, name: str, file_path: str):
        standards = self.standards['standard_definitions']
        if 'formats' in standards and name not in standards['formats']:
            if any(keyword in name.lower() for keyword in ['formato', 'precision']):
                self.issues.append(f"Non-standard format function '{name}' in {file_path}")

def main():
    validator = CodebaseValidator()
    root_dirs = ['app', 'tests', 'blockchain']
    
    for root_dir in root_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    validator.validate_file(file_path)
                    
    if validator.issues:
        print("\nInconsistencies found:")
        for issue in validator.issues:
            print(f"- {issue}")
    else:
        print("\nNo inconsistencies found. Codebase follows standards.")

if __name__ == '__main__':
    main()
