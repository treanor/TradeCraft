#!/usr/bin/env python3
"""
Test runner script for TradeCraft.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run unit tests only
    python run_tests.py --integration # Run integration tests only
    python run_tests.py --coverage   # Run with coverage report
"""
import sys
import subprocess
from pathlib import Path


def run_tests(test_type=None, coverage=False):
    """Run tests with specified options."""
    cmd = ["python", "-m", "pytest"]
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=utils", "--cov=pages", "--cov=components", "--cov-report=html", "--cov-report=term"])
    
    # Add test type filter
    if test_type:
        cmd.extend(["-m", test_type])
    
    # Add verbose output
    cmd.append("-v")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main test runner."""
    args = sys.argv[1:]
    
    test_type = None
    coverage = False
    
    for arg in args:
        if arg == "--unit":
            test_type = "unit"
        elif arg == "--integration":
            test_type = "integration"
        elif arg == "--coverage":
            coverage = True
        elif arg == "--help":
            print(__doc__)
            return 0
    
    return run_tests(test_type, coverage)


if __name__ == "__main__":
    sys.exit(main())
