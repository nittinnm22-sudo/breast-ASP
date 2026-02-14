#!/bin/bash
# ============================================================================
# Build Executable Script for Lung ASP GUI (Linux/Mac)
# ============================================================================
# This script creates a standalone executable with all dependencies
# including TotalSegmentator and nnU-Net
# ============================================================================

set -e  # Exit on error

echo ""
echo "============================================================================"
echo "  Lung ASP - Executable Build Script for Linux/Mac"
echo "============================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "[1/6] Checking Python version..."
python3 --version
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv_build" ]; then
    echo "[2/6] Creating virtual environment..."
    python3 -m venv venv_build
else
    echo "[2/6] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/6] Activating virtual environment..."
source venv_build/bin/activate

# Install dependencies
echo "[4/6] Installing dependencies (this may take 10-20 minutes)..."
echo "This includes: numpy, scipy, scikit-image, TotalSegmentator, nnU-Net, PyInstaller"
pip install --upgrade pip
pip install -r requirements-full.txt

# Build executable with PyInstaller
echo ""
echo "[5/6] Building executable with PyInstaller..."
echo "This may take 5-10 minutes depending on your system..."
pyinstaller --clean --noconfirm lung_asp_gui.spec

# Verify build
echo ""
echo "[6/6] Verifying build..."
if [ -f "dist/LungASP/LungASP" ]; then
    echo ""
    echo "============================================================================"
    echo "  BUILD SUCCESSFUL!"
    echo "============================================================================"
    echo ""
    echo "Executable location: $(pwd)/dist/LungASP/"
    echo "Main executable: $(pwd)/dist/LungASP/LungASP"
    echo ""
    echo "The entire 'dist/LungASP' folder contains the standalone application."
    echo "Copy this entire folder to any Linux/Mac computer to run the application."
    echo ""
    echo "IMPORTANT NOTES:"
    echo "- First run may be slow as TotalSegmentator downloads models"
    echo "- Ensure you have adequate disk space for models (several GB)"
    echo "- The application requires an internet connection on first run for models"
    echo ""
    echo "To run the application:"
    echo "  cd dist/LungASP"
    echo "  ./LungASP"
    echo ""
    echo "============================================================================"
else
    echo ""
    echo "ERROR: Executable was not created successfully"
    echo "Please check the build output for errors"
    exit 1
fi
