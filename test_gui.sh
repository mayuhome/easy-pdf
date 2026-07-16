#!/bin/bash
# Quick test script for Easy PDF GUI application

echo "🚀 Easy PDF GUI - Quick Test Script"
echo "===================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python version:"
python3 --version
echo ""

# Create test environment
echo "📦 Creating test virtual environment..."
python3 -m venv test_env
source test_env/bin/activate

# Install package
echo "📥 Installing Easy PDF with GUI and PDF support..."
pip install "dist/easy_pdf-0.1.0-py3-none-any.whl[pdf,gui]" -q

echo "✅ Installation complete!"
echo ""

# Verify CLI tool
echo "🧪 Testing CLI tool..."
easy-pdf health
echo ""

# Test GUI import
echo "🧪 Testing GUI module..."
python -c "from easy_pdf.gui.main_window import main; print('✅ GUI module loaded successfully!')"
echo ""

echo "🎉 All tests passed!"
echo ""
echo "To start the GUI application, run:"
echo "  source test_env/bin/activate"
echo "  easy-pdf-gui"
echo ""
echo "To use the CLI tool:"
echo "  easy-pdf --help"
