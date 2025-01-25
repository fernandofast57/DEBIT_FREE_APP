
#!/usr/bin/env python
import sys
from app.utils.structure_validator import StructureValidator

def main():
    validator = StructureValidator()
    if not validator.validate_codebase():
        print("❌ Code does not comply with glossary standards")
        sys.exit(1)
    print("✓ Code complies with glossary standards")
    sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python
from app.middleware.code_standardization_middleware import CodeStandardizationMiddleware
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

def check_files():
    standardizer = CodeStandardizationMiddleware()
    python_files = Path('.').rglob('*.py')
    
    has_issues = False
    for file_path in python_files:
        issues = standardizer.validate_file(str(file_path))
        if any(issues.values()):
            has_issues = True
            print(f"\nIssues in {file_path}:")
            for category, problems in issues.items():
                if problems:
                    print(f"  {category}:")
                    for problem in problems:
                        print(f"    - {problem}")
    
    return not has_issues

if __name__ == "__main__":
    if not check_files():
        print("\n❌ Code does not comply with glossary standards")
        sys.exit(1)
    print("\n✓ Code complies with glossary standards")
    sys.exit(0)
