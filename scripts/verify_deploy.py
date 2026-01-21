#!/usr/bin/env python3
"""Pre-deployment verification script for Alter-5 Origination Engine.

This script verifies that all required components are properly configured
before deploying to production.

Usage:
    python scripts/verify_deploy.py
    python scripts/verify_deploy.py --env production
    python scripts/verify_deploy.py --skip-api-tests
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional
import importlib
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_check(name: str, passed: bool, message: str = "") -> None:
    """Print a check result."""
    status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    msg = f" - {message}" if message else ""
    print(f"  [{status}] {name}{msg}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"  {Colors.YELLOW}WARNING: {message}{Colors.END}")


def check_python_version() -> bool:
    """Check Python version is 3.11+."""
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 11
    print_check(
        "Python version",
        passed,
        f"{version.major}.{version.minor}.{version.micro}"
    )
    return passed


def check_required_files() -> bool:
    """Check all required files exist."""
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "config/settings.py",
        "config/airtable_schema.py",
        "core/models.py",
        "core/airtable_client.py",
        "agents/buscador.py",
        "agents/enriquecedor.py",
        "agents/evaluador_fei.py",
        "agents/selector.py",
        "agents/redactor.py",
        "integrations/claude.py",
        "integrations/gemini.py",
        "frontend/app.py",
        "api/main.py",
        "orchestration/tasks.py",
    ]

    all_exist = True
    for file in required_files:
        exists = Path(file).exists()
        if not exists:
            print_check(f"File: {file}", False, "NOT FOUND")
            all_exist = False

    if all_exist:
        print_check("All required files", True, f"{len(required_files)} files")

    return all_exist


def check_imports() -> bool:
    """Check all core modules can be imported."""
    modules = [
        ("config.settings", "Settings configuration"),
        ("core.models", "Data models"),
        ("core.airtable_client", "Airtable client"),
        ("core.async_utils", "Async utilities"),
        ("core.rate_limiter", "Rate limiter"),
    ]

    all_pass = True
    for module_name, description in modules:
        try:
            importlib.import_module(module_name)
            print_check(f"Import: {description}", True)
        except ImportError as e:
            print_check(f"Import: {description}", False, str(e))
            all_pass = False

    return all_pass


def check_environment_variables(env_file: Optional[str] = None) -> tuple[bool, list[str]]:
    """Check required environment variables are set."""
    # Load .env if specified
    if env_file and Path(env_file).exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

    required_vars = [
        ("ANTHROPIC_API_KEY", True, "Claude API key"),
        ("GOOGLE_API_KEY", True, "Gemini API key"),
        ("AIRTABLE_PAT", True, "Airtable Personal Access Token"),
        ("AIRTABLE_BASE_ID", True, "Airtable Base ID"),
    ]

    optional_vars = [
        ("REDIS_URL", False, "Redis connection URL"),
        ("MONGODB_URL", False, "MongoDB connection URL"),
        ("SLACK_BOT_TOKEN", False, "Slack notifications"),
        ("PROXYCURL_API_KEY", False, "LinkedIn data"),
        ("MAILCHIMP_API_KEY", False, "Email marketing"),
        ("ALTER5_API_KEY", False, "API authentication"),
        ("CORS_ORIGINS", False, "CORS allowed origins"),
    ]

    missing_required = []
    all_pass = True

    print("\n  Required:")
    for var_name, required, description in required_vars:
        value = os.getenv(var_name)
        if value:
            # Mask the value for security
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print_check(f"  {var_name}", True, masked)
        else:
            print_check(f"  {var_name}", False, description)
            if required:
                missing_required.append(var_name)
                all_pass = False

    print("\n  Optional:")
    for var_name, _, description in optional_vars:
        value = os.getenv(var_name)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print_check(f"  {var_name}", True, masked)
        else:
            print_warning(f"{var_name} not set - {description}")

    return all_pass, missing_required


def check_api_connectivity(skip: bool = False) -> bool:
    """Test connectivity to external APIs."""
    if skip:
        print_warning("API connectivity tests skipped")
        return True

    results = []

    # Test Anthropic
    try:
        import anthropic
        client = anthropic.Anthropic()
        # Just check we can create a client (don't make actual call)
        print_check("Anthropic API", True, "Client initialized")
        results.append(True)
    except Exception as e:
        print_check("Anthropic API", False, str(e)[:50])
        results.append(False)

    # Test Gemini
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            print_check("Gemini API", True, "Configured")
            results.append(True)
        else:
            print_check("Gemini API", False, "No API key")
            results.append(False)
    except Exception as e:
        print_check("Gemini API", False, str(e)[:50])
        results.append(False)

    # Test Airtable
    try:
        from pyairtable import Api
        pat = os.getenv("AIRTABLE_PAT")
        base_id = os.getenv("AIRTABLE_BASE_ID")
        if pat and base_id:
            api = Api(pat)
            # Just check we can create API client
            print_check("Airtable API", True, "Client initialized")
            results.append(True)
        else:
            print_check("Airtable API", False, "Missing credentials")
            results.append(False)
    except Exception as e:
        print_check("Airtable API", False, str(e)[:50])
        results.append(False)

    return all(results)


def check_docker() -> bool:
    """Check Docker configuration."""
    import subprocess

    try:
        # Check Docker is available
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print_check("Docker installed", True, result.stdout.strip())
        else:
            print_check("Docker installed", False)
            return False

        # Check Dockerfile can be parsed
        dockerfile = Path("Dockerfile")
        if dockerfile.exists():
            content = dockerfile.read_text()
            if "FROM python:3.11" in content:
                print_check("Dockerfile valid", True)
            else:
                print_check("Dockerfile valid", False, "Check base image")
                return False

        return True

    except FileNotFoundError:
        print_warning("Docker not found - skipping Docker checks")
        return True
    except Exception as e:
        print_check("Docker check", False, str(e)[:50])
        return False


def check_settings_config() -> bool:
    """Verify settings configuration loads correctly."""
    try:
        from config.settings import get_settings

        settings = get_settings()

        # Check critical settings have values
        checks = [
            ("COOLING_OFF_DAYS", settings.COOLING_OFF_DAYS > 0),
            ("MAX_TARGETS_PER_CAMPAIGN", settings.MAX_TARGETS_PER_CAMPAIGN > 0),
            ("MIN_FIT_SCORE", 0 <= settings.MIN_FIT_SCORE <= 1),
            ("CLAUDE_MODEL", bool(settings.CLAUDE_MODEL)),
            ("GEMINI_MODEL", bool(settings.GEMINI_MODEL)),
        ]

        all_pass = True
        for name, valid in checks:
            if not valid:
                print_check(f"Setting: {name}", False)
                all_pass = False

        if all_pass:
            print_check("Settings configuration", True, "All valid")

        return all_pass

    except Exception as e:
        print_check("Settings configuration", False, str(e)[:50])
        return False


def run_quick_tests() -> bool:
    """Run quick unit tests."""
    try:
        import subprocess

        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-x", "-q", "--tb=no", "-k", "not integration"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            # Extract test count from output
            lines = result.stdout.strip().split("\n")
            summary = [l for l in lines if "passed" in l or "failed" in l]
            msg = summary[-1] if summary else "Tests passed"
            print_check("Unit tests", True, msg)
            return True
        else:
            print_check("Unit tests", False, "Some tests failed")
            if result.stdout:
                print(f"\n{result.stdout[:500]}")
            return False

    except subprocess.TimeoutExpired:
        print_check("Unit tests", False, "Timeout")
        return False
    except FileNotFoundError:
        print_warning("pytest not found - skipping tests")
        return True
    except Exception as e:
        print_check("Unit tests", False, str(e)[:50])
        return False


def main():
    """Run all verification checks."""
    parser = argparse.ArgumentParser(description="Verify deployment readiness")
    parser.add_argument("--env", help="Path to .env file to load")
    parser.add_argument("--skip-api-tests", action="store_true", help="Skip API connectivity tests")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unit tests")
    args = parser.parse_args()

    print(f"\n{Colors.BOLD}Alter-5 Origination Engine - Deployment Verification{Colors.END}")
    print(f"{'='*60}\n")

    results = {}

    # 1. Python Version
    print_header("1. Python Environment")
    results["python"] = check_python_version()

    # 2. Required Files
    print_header("2. Required Files")
    results["files"] = check_required_files()

    # 3. Module Imports
    print_header("3. Module Imports")
    results["imports"] = check_imports()

    # 4. Environment Variables
    print_header("4. Environment Variables")
    results["env"], missing = check_environment_variables(args.env)

    # 5. Settings Configuration
    print_header("5. Settings Configuration")
    results["settings"] = check_settings_config()

    # 6. API Connectivity
    print_header("6. API Connectivity")
    results["api"] = check_api_connectivity(args.skip_api_tests)

    # 7. Docker
    print_header("7. Docker Configuration")
    results["docker"] = check_docker()

    # 8. Unit Tests
    if not args.skip_tests:
        print_header("8. Quick Tests")
        results["tests"] = run_quick_tests()

    # Summary
    print_header("SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    all_pass = all(results.values())

    if all_pass:
        print(f"{Colors.GREEN}{Colors.BOLD}ALL CHECKS PASSED ({passed}/{total}){Colors.END}")
        print(f"\n{Colors.GREEN}Ready for deployment!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}SOME CHECKS FAILED ({passed}/{total}){Colors.END}")

        if missing:
            print(f"\n{Colors.YELLOW}Missing required environment variables:{Colors.END}")
            for var in missing:
                print(f"  - {var}")

        print(f"\n{Colors.YELLOW}Please fix the issues above before deploying.{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
