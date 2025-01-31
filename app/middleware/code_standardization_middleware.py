
import ast
import re
from typing import Dict, List, Set
from pathlib import Path
import logging
from app.utils.structure_validator import StructureValidator

logger = logging.getLogger(__name__)

class CodeStandardizationMiddleware:
    def __init__(self):
        self.validator = StructureValidator()
        self.glossary_terms = self._load_glossary_terms()
        
    def validate_file(self, file_path: str) -> Dict[str, List[str]]:
        with open(file_path, 'r') as f:
            content = f.read()
            
        issues = {
            'variable_names': [],
            'function_names': [],
            'class_names': [],
            'metric_names': []
        }
        
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                self._validate_name(node.id, 'variable_names', issues)
            elif isinstance(node, ast.FunctionDef):
                self._validate_name(node.name, 'function_names', issues)
            elif isinstance(node, ast.ClassDef):
                self._validate_name(node.name, 'class_names', issues)
                
        return issues

    def validate_name(self, name: str, category: str, issues: Dict[str, List[str]]) -> None:
        """Validates if a name follows glossary standards"""
        if not self.matches_glossary_term(name):
            issues[category].append(f"'{name}' does not comply with glossary standards")

    def _matches_glossary(self, name: str) -> bool:
        return name.lower() in self.glossary_terms

    def _load_glossary_terms(self) -> Set[str]:
        return set(term.lower() for term in self.validator.get_glossary_terms())
