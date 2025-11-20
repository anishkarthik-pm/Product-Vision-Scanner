#!/usr/bin/env python3
"""
Setup Verification Script

Checks that the Retail Compliance Analyzer is properly installed and configured.
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python 3.8+ required, found {version.major}.{version.minor}"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"


def check_dependencies():
    """Check that required packages are installed"""
    required = {
        "anthropic": "anthropic",
        "dotenv": "python-dotenv",
        "PIL": "Pillow",
        "jsonschema": "jsonschema"
    }

    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        return False, f"Missing packages: {', '.join(missing)}"
    return True, "All required packages installed"


def check_env_file():
    """Check for .env file and API key"""
    env_path = Path(".env")

    if not env_path.exists():
        return False, ".env file not found. Copy .env.example to .env and add your API key"

    # Check if API key is set (but don't expose it)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            return False, "ANTHROPIC_API_KEY not set in .env file"

        if api_key == "your_api_key_here":
            return False, "ANTHROPIC_API_KEY still set to placeholder value"

        return True, "API key configured"
    except Exception as e:
        return False, f"Error reading .env: {str(e)}"


def check_analyzer_import():
    """Check that the analyzer module can be imported"""
    try:
        from analyzer import RetailComplianceAnalyzer
        return True, "Analyzer module loads successfully"
    except ImportError as e:
        return False, f"Cannot import analyzer: {str(e)}"


def check_schema():
    """Check that schema.json exists and is valid"""
    schema_path = Path("schema.json")

    if not schema_path.exists():
        return False, "schema.json not found"

    try:
        import json
        with open(schema_path) as f:
            json.load(f)
        return True, "schema.json is valid"
    except Exception as e:
        return False, f"Invalid schema.json: {str(e)}"


def main():
    """Run all checks"""
    print("=" * 60)
    print("Retail Compliance Analyzer - Setup Verification")
    print("=" * 60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Analyzer Module", check_analyzer_import),
        ("JSON Schema", check_schema),
    ]

    all_passed = True
    results = []

    for name, check_func in checks:
        try:
            passed, message = check_func()
            results.append((name, passed, message))
            if not passed:
                all_passed = False
        except Exception as e:
            results.append((name, False, f"Check failed: {str(e)}"))
            all_passed = False

    # Print results
    for name, passed, message in results:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
        print(f"  {message}")
        print()

    # Summary
    print("=" * 60)
    if all_passed:
        print("✓ All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Place a store image in the project directory")
        print("  2. Run: python -m analyzer.cli analyze your_image.jpg")
        print("  3. Check out examples/ for more usage patterns")
        print()
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Configure API key: cp .env.example .env && edit .env")
        print("  - Ensure you're in the project root directory")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
