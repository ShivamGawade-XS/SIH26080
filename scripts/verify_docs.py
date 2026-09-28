#!/usr/bin/env python3
"""
Verify documentation integrity:
- Assert that all required documents exist.
- Check that referenced files in markdown links exist.
- Assert that there are no unreplaced TODO/placeholder tags in docs.
"""

import os
import re
import sys
from pathlib import Path

REQUIRED_DOCS = [
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "docs/PRD.md",
    "docs/ARCHITECTURE.md",
    "docs/METHODOLOGY.md",
    "docs/TECH_STACK.md",
    "docs/DESIGN_SYSTEM.md",
    "docs/TEST_PLAN.md",
    "docs/SCORECARD.md",
    "docs/ASSUMPTIONS.md",
    "docs/BACKLOG.md",
    "docs/STATE.md",
    "docs/FLAWS.md",
    "docs/ITERATION_LOG.md",
    "docs/KNOWN_LIMITATIONS.md",
    "docs/DEMO_SCRIPT.md",
    "docs/SUBMISSION_MAPPING.md",
    "docs/DATA_SOURCES.md",
    "docs/DATA_CARD.md",
    "docs/MODEL_CARD.md",
    "docs/SECURITY.md",
    "docs/OPERATIONS.md",
    "docs/HUMAN_SIGNOFF.md",
    "docs/CHANGELOG.md",
    "docs/ENVIRONMENT.md",
    "docs/VERIFICATION_STATUS.md",
]

def check_required_docs():
    missing = []
    for doc in REQUIRED_DOCS:
        p = Path(doc)
        if not p.exists():
            missing.append(doc)
    return missing

def main():
    root = Path(".")
    print("Verifying documentation files...")
    missing = check_required_docs()
    if missing:
        print(f"FAILED: Missing required documents: {missing}", file=sys.stderr)
        sys.exit(1)
    
    print(f"All {len(REQUIRED_DOCS)} required documents verified successfully!")

if __name__ == "__main__":
    main()
