#!/bin/bash
# Simple test runner that handles the import path

echo "🧪 Running Translation Library Tests"
echo "====================================="

# Add parent directory to PYTHONPATH so Python can find translation_library
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run pytest
echo ""
echo "Running unit tests..."
python3 -m pytest test_translator.py -v

echo ""
echo "✅ Tests complete!"