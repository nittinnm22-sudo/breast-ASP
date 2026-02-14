#!/bin/bash
# Build script for Lung ASP on Linux/Mac

set -e

echo "============================================"
echo "Lung ASP - Full Build Script (Linux/Mac)"
echo "============================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found"
    exit 1
fi

echo "[1/4] Installing dependencies..."
pip3 install -r requirements.txt

echo
echo "[2/4] Installing Lung ASP package..."
pip3 install -e .

echo
echo "[3/4] Checking TotalSegmentator installation..."
python3 src/download_models.py

echo
echo "[4/4] Build complete!"
echo
echo "To run the GUI: python3 src/Lung_ASP_GUI.py"
echo "To run the CLI: lung-asp --help"
echo
