
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
