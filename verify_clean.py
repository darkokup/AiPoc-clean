"""
Security verification script for the clean copy.
Run this before publishing to GitHub to check for potential secrets.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Patterns that might indicate secrets
SECRET_PATTERNS = {
    'API Keys': [
        r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']',
        r'sk-[a-zA-Z0-9]{20,}',  # OpenAI style keys
        r'api[_-]?secret\s*=\s*["\'][^"\']{10,}["\']',
    ],
    'Passwords': [
        r'password\s*=\s*["\'][^"\']{3,}["\']',
        r'passwd\s*=\s*["\'][^"\']{3,}["\']',
        r'pwd\s*=\s*["\'][^"\']{3,}["\']',
    ],
    'Tokens': [
        r'token\s*=\s*["\'][^"\']{10,}["\']',
        r'auth[_-]?token\s*=\s*["\'][^"\']{10,}["\']',
        r'access[_-]?token\s*=\s*["\'][^"\']{10,}["\']',
    ],
    'Private Keys': [
        r'private[_-]?key\s*=\s*["\'][^"\']{10,}["\']',
        r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
    ],
    'Database URLs': [
        r'postgres://[^:]+:[^@]+@',
        r'mysql://[^:]+:[^@]+@',
        r'mongodb://[^:]+:[^@]+@',
    ],
}

# Files to exclude from search
EXCLUDE_DIRS = {
    '.git', '__pycache__', '.venv', 'venv', 'env', 'ENV',
    'node_modules', 'dist', 'build', '.pytest_cache',
    'artifacts', 'models', 'vector_db'
}

EXCLUDE_FILES = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
    '.db', '.sqlite', '.sqlite3', '.log'
}

# Files where certain patterns are expected (documentation, examples)
WHITELIST_FILES = {
    'verify_clean.py',  # This file
    'SECURITY.md',
    'SETUP.md',
    'CONTRIBUTING.md',
    'CLEAN_COPY_SUMMARY.md',
    'PUBLISHING_CHECKLIST.md',
    '.env.example',
    'README.md',
    'QUICKSTART.md',
}


def should_check_file(file_path: Path, root_dir: Path) -> bool:
    """Determine if a file should be checked."""
    # Skip if in excluded directory
    for parent in file_path.parents:
        if parent.name in EXCLUDE_DIRS:
            return False
    
    # Skip if excluded file type
    if file_path.suffix in EXCLUDE_FILES:
        return False
    
    # Skip if binary file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, PermissionError):
        return False


def check_file(file_path: Path, root_dir: Path) -> List[Tuple[str, str, int, str]]:
    """Check a file for potential secrets."""
    findings = []
    
    # Skip whitelisted files for certain checks
    is_whitelisted = file_path.name in WHITELIST_FILES
    
    # Skip this verification script itself
    if file_path.name == 'verify_clean.py':
        return findings
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            # Skip comments in documentation files
            if is_whitelisted and (line.strip().startswith('#') or 
                                  line.strip().startswith('//')):
                continue
            
            for category, patterns in SECRET_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's an obvious placeholder
                        if any(placeholder in line.lower() for placeholder in [
                            'your-key', 'your-api-key', 'sk-your-',
                            'change-this', 'changeme', 'your-password',
                            'your-secret', '<', '>', 'example', 'placeholder'
                        ]):
                            continue
                        
                        relative_path = file_path.relative_to(root_dir)
                        findings.append((
                            str(relative_path),
                            category,
                            i,
                            line.strip()
                        ))
    
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
    
    return findings


def verify_clean_copy(root_dir: str = '.') -> bool:
    """Verify the clean copy has no secrets."""
    root_path = Path(root_dir).resolve()
    all_findings = []
    
    print(f"🔍 Scanning {root_path} for potential secrets...\n")
    
    # Check all files
    for file_path in root_path.rglob('*'):
        if file_path.is_file() and should_check_file(file_path, root_path):
            findings = check_file(file_path, root_path)
            all_findings.extend(findings)
    
    # Report findings
    if all_findings:
        print("⚠️  POTENTIAL SECRETS FOUND:\n")
        print(f"{'File':<50} {'Category':<15} {'Line':<6} {'Content'}")
        print("-" * 120)
        
        for file, category, line, content in all_findings:
            print(f"{file:<50} {category:<15} {line:<6} {content[:50]}...")
        
        print(f"\n❌ Found {len(all_findings)} potential secret(s).")
        print("\n⚠️  ACTION REQUIRED:")
        print("1. Review each finding above")
        print("2. Ensure they are placeholders, not real secrets")
        print("3. If real secrets found, remove them and use environment variables")
        print("4. Update .env.example with placeholder values")
        return False
    else:
        print("✅ No obvious secrets detected!")
        print("\n📋 Additional checks you should perform:")
        print("1. Review git status: git status")
        print("2. Check what will be committed: git diff --cached")
        print("3. Ensure .env is NOT staged for commit")
        print("4. Verify .gitignore includes sensitive files")
        print("5. Review SECURITY.md and PUBLISHING_CHECKLIST.md")
        print("\n🚀 You're ready to publish!")
        return True


def check_gitignore(root_dir: str = '.') -> None:
    """Check if .gitignore is properly configured."""
    gitignore_path = Path(root_dir) / '.gitignore'
    
    required_entries = [
        '.env',
        '*.db',
        '*.sqlite',
        '__pycache__',
        'artifacts/',
        'models/',
        'vector_db/',
    ]
    
    if not gitignore_path.exists():
        print("❌ No .gitignore found!")
        return
    
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    missing = []
    for entry in required_entries:
        if entry not in gitignore_content:
            missing.append(entry)
    
    if missing:
        print(f"⚠️  .gitignore missing entries: {', '.join(missing)}")
    else:
        print("✅ .gitignore properly configured")


def check_env_example(root_dir: str = '.') -> None:
    """Check if .env.example exists and is properly formatted."""
    env_example_path = Path(root_dir) / '.env.example'
    
    if not env_example_path.exists():
        print("❌ No .env.example found!")
        return
    
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Check for real API keys (should only have placeholders)
    if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
        print("❌ .env.example contains what looks like a real API key!")
    else:
        print("✅ .env.example properly formatted with placeholders")


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("SECURITY VERIFICATION FOR CLEAN COPY")
    print("=" * 80)
    print()
    
    # Check .gitignore
    print("📁 Checking .gitignore...")
    check_gitignore()
    print()
    
    # Check .env.example
    print("📝 Checking .env.example...")
    check_env_example()
    print()
    
    # Main secret scan
    is_clean = verify_clean_copy()
    
    print()
    print("=" * 80)
    
    if is_clean:
        print("✅ VERIFICATION PASSED")
        print("\nNext steps:")
        print("1. Review PUBLISHING_CHECKLIST.md")
        print("2. Initialize git: git init")
        print("3. Add files: git add .")
        print("4. Review: git status")
        print("5. Commit: git commit -m 'Initial commit'")
        print("6. Push to GitHub")
    else:
        print("❌ VERIFICATION FAILED")
        print("\nDO NOT PUBLISH until all issues are resolved!")
    
    print("=" * 80)


if __name__ == '__main__':
    main()
