#!/usr/bin/env python3
"""
Simple test runner that handles import paths correctly
"""
import sys
import os

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now run pytest
import pytest

if __name__ == "__main__":
    print("🧪 Running Translation Library Tests")
    print("=" * 50)
    
    # Run tests with verbose output
    exit_code = pytest.main([
        "test_translator.py",
        "-v",
        "--tb=short"
    ])
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    sys.exit(exit_code)