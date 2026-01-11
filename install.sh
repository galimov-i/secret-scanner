#!/bin/bash

# Config Secrets Scanner Installation Script
# This script installs the required Python dependencies

set -e  # Exit on any error

echo "=========================================="
echo "Config Secrets Scanner - Installation"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.10 or higher and try again."
    exit 1
fi

# Check Python version (requires 3.10+)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "✓ Python version detected: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Error: Python 3.10 or higher is required."
    echo "Current version: $PYTHON_VERSION"
    echo "Please upgrade Python and try again."
    exit 1
fi

echo "✓ Python version is compatible (3.10+)"
echo ""

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✓ pip3 is available"
echo ""

# Install dependencies from requirements.txt
echo "Installing Python dependencies..."
echo ""

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Dependencies installed successfully!"
    else
        echo ""
        echo "❌ Error: Failed to install dependencies."
        exit 1
    fi
else
    echo "❌ Error: requirements.txt not found in current directory."
    exit 1
fi

echo ""

# Make scanner.py executable
if [ -f "scanner.py" ]; then
    chmod +x scanner.py
    echo "✓ scanner.py is now executable"
else
    echo "⚠️  Warning: scanner.py not found in current directory"
fi

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "You can now run the scanner with:"
echo "  python3 scanner.py"
echo ""
echo "Or if executable:"
echo "  ./scanner.py"
echo ""
