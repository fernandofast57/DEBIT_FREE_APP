#!/usr/bin/env python
import sys
import os
from typing import List
from app.middleware.standards_enforcer_middleware import StandardsEnforcer
import logging

logger = logging.getLogger(__name__)

def validate_standards() -> List[str]:
    enforcer = StandardsEnforcer()
    violations = []

    for root, _, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_violations = enforcer.validate_file(file_path)
                violations.extend(file_violations)

    if violations:
        logger.error("Standard violations found:")
        for violation in violations:
            logger.error(violation)

    return violations

def run_pre_commit_hook() -> bool:
    violations = validate_standards()
    return len(violations) == 0

if __name__ == "__main__":
    if not run_pre_commit_hook():
        print("\n❌ Code does not comply with glossary standards")
        sys.exit(1)
    print("\n✓ Code complies with glossary standards")
    sys.exit(0)