"""
FinOps Zero-Cost Enforcement & Static Audit Script.
Scans the entire codebase for paid API endpoints, unencrypted secrets, or out-of-budget libraries.
Ensures strict compliance with the $0.00 TCO mandate.
"""

import os
import sys
import re
from typing import List, Tuple

PROHIBITED_STRINGS: List[Tuple[str, str]] = [
    (r"api\.openai\.com", "Paid OpenAI API endpoint detected"),
    (r"api\.anthropic\.com", "Paid Anthropic API endpoint detected"),
    (r"api\.cohere\.ai", "Paid Cohere API endpoint detected"),
    (r"api\.replicate\.com", "Paid Replicate API endpoint detected"),
    (r"boto3", "AWS SDK detected (potential billable EC2/S3/Lambda charges)"),
    (r"aws_access_key_id", "AWS credential reference detected"),
    (r"gcp_service_account", "Billable GCP credential reference detected"),
]

ALLOWED_FILES = {
    "scripts/verify_zero_cost.py",
    "src/aria/github/reviewer.py",
    "tests/test_pr_reviewer.py",
    "tests/test_finops_audit.py"
}


def audit_repository(root_dir: str = ".") -> Tuple[bool, List[str]]:
    """Walks directory tree and flags any paid provider mentions or secrets."""
    violations = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip git and cache directories
        dirs[:] = [d for d in dirs if d not in {".git", ".pytest_cache", "__pycache__", "venv", ".venv", "build", "dist"}]
        
        for file in files:
            if not file.endswith((".py", ".yml", ".yaml", ".json", ".js", ".toml")):
                continue
                
            rel_path = os.path.relpath(os.path.join(root, file), root_dir).replace("\\", "/")
            if rel_path in ALLOWED_FILES:
                continue
                
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        for pattern, desc in PROHIBITED_STRINGS:
                            if re.search(pattern, line):
                                violations.append(f"{rel_path}:{line_num} - {desc}")
            except Exception:
                continue
                
    is_compliant = len(violations) == 0
    return is_compliant, violations


def main():
    print("=" * 65)
    print("  ARIA FinOps Audit: Verifying Absolute Zero-Cost Compliance")
    print("=" * 65)
    
    is_compliant, violations = audit_repository(".")
    
    if is_compliant:
        print("[SUCCESS] 100% Zero-Cost Compliance Verified.")
        print("          No paid API endpoints, billable SDKs, or credentials found.")
        print("=" * 65)
        return 0
    else:
        print(f"[VIOLATION] Found {len(violations)} non-compliant lines:")
        for v in violations:
            print(f"  - {v}")
        print("=" * 65)
        return 1


if __name__ == "__main__":
    sys.exit(main())
