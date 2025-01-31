#!/usr/bin/env python3
from app.utils.pre_commit_hook import run_pre_commit_hook
import sys

def validate_language():
    """Validate that no Italian terms are used in the codebase"""
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith(('.py', '.md', '.json')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    # Add Italian terms to check
                    italian_terms = ['creazione', 'delle', 'tabelle', 'mancanti', 'conto', 'oro', 'servizio']
                    for term in italian_terms:
                        if term in content:
                            print(f"Italian term '{term}' found in {file_path}")
                            return False
    return True

if __name__ == "__main__":
    standards_valid = run_pre_commit_hook()
    language_valid = validate_language()
    
    if not (standards_valid and language_valid):
        print("Validation failed. Please fix the errors before committing.")
        sys.exit(1)
    sys.exit(0)