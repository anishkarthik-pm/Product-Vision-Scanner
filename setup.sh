#!/bin/bash
# Setup script for Retail Compliance Analyzer

set -e  # Exit on error

echo "============================================================"
echo "RETAIL COMPLIANCE ANALYZER - AUTOMATED SETUP"
echo "============================================================"
echo ""

# Check Python version
echo "Step 1: Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "✗ Python not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"

# Check if version is >= 3.8
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
    echo "✗ Python 3.8 or higher required. Found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo ""
echo "Step 2: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Step 3: Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Could not find venv/bin/activate"
    exit 1
fi

# Install dependencies
echo ""
echo "Step 4: Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Set up .env file
echo ""
echo "Step 5: Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    cp .env.example .env
    echo "✓ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Anthropic API key!"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
    echo "Then edit .env:"
    echo "  nano .env"
    echo "  # or"
    echo "  vim .env"
    echo ""
fi

# Run verification
echo ""
echo "Step 6: Running setup verification..."
$PYTHON_CMD test_setup.py

echo ""
echo "============================================================"
echo "SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. If not done already, configure your API key:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment (in new terminal sessions):"
echo "   source venv/bin/activate"
echo ""
echo "3. Run a quick test:"
echo "   python quick_test.py"
echo ""
echo "4. Try analyzing an image:"
echo "   python -m analyzer.multi_cli analyze image.jpg --type waste"
echo ""
echo "5. Read the documentation:"
echo "   - QUICKSTART.md - Quick start guide"
echo "   - MULTI_TYPE_GUIDE.md - Comprehensive guide"
echo "   - examples/ - Code examples"
echo ""
