"""Comprehensive test runner to ensure 100% coverage."""

import subprocess  # nosec B404
import sys
from pathlib import Path


def run_tests_with_coverage():
    """Run all tests with coverage reporting."""
    # Change to project root directory
    project_root = Path(__file__).parent.parent

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=src/Fishing_Line_Material_Properties_Analysis",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml",
        "--cov-fail-under=100",
        "--verbose",
        "tests/",
    ]

    print("Running comprehensive test suite...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=project_root, check=False)  # nosec B603

    if result.returncode == 0:
        print("\n✅ All tests passed with 100% coverage!")
    else:
        print(f"\n❌ Tests failed with return code {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests_with_coverage()
    sys.exit(exit_code)
