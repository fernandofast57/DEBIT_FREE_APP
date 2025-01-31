import ast
import json
import os
from typing import Set, Dict, List
import logging

logger = logging.getLogger(__name__)

class StandardsEnforcer:
    def __init__(self):
        self.glossary_terms = self._load_glossary_terms()
        self.official_standards = self._load_official_standards()

    def _load_glossary_terms(self) -> Set[str]:
        with open('docs/GLOSSARY.md', 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract all defined terms
            terms = set()
            for line in content.split('\n'):
                if line.startswith('- '):
                    term = line.split(':')[0].replace('- ', '').strip()
                    terms.add(term)
            return terms

    def _load_official_standards(self) -> Dict:
        with open('docs/OFFICIAL_STANDARDS.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_file(self, file_path: str) -> List[str]:
        if not file_path.endswith('.py'):
            return []

        violations = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    if not self._is_standard_compliant(node.name):
                        violations.append(
                            f"Non-standard name '{node.name}' found in {file_path}. "
                            f"Please refer to GLOSSARY.md and OFFICIAL_STANDARDS.json"
                        )
        except Exception as e:
            logger.error(f"Error during validation of {file_path}: {str(e)}")

        return violations

    def _is_standard_compliant(self, name: str) -> bool:
        return (
            name in self.glossary_terms or
            any(name.startswith(prefix) for prefix in self.glossary_terms) or
            self._check_official_standards(name)
        )

    def _check_official_standards(self, name: str) -> bool:
        # Recursive check in official standards
        def check_dict(d: Dict) -> bool:
            for k, v in d.items():
                if isinstance(v, dict):
                    if check_dict(v):
                        return True
                elif isinstance(v, (str, list)):
                    if k == name or name in (v if isinstance(v, list) else [v]):
                        return True
            return False

        return check_dict(self.official_standards)