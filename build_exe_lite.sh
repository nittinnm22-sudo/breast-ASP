#!/bin/bash
# Simplified build script for Lung-ASP lite executable
# This version excludes heavy ML dependencies for faster building

set -e  # Exit on error

echo "========================================"
echo "Lung-ASP Lite Executable Build Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install minimal dependencies
echo -e "${YELLOW}Installing minimal dependencies...${NC}"
echo "This should be much faster than the full version..."
pip install -r requirements_build.txt

# Install the package
echo -e "${YELLOW}Installing lung_asp package...${NC}"
pip install -e .

# Build with PyInstaller
echo -e "${YELLOW}Building executable with PyInstaller...${NC}"
pyinstaller lung_asp_lite.spec --clean --noconfirm

# Check if build was successful
if [ -d "dist/lung_asp" ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Executable location: dist/lung_asp/"
    echo "Main executable: dist/lung_asp/lung_asp"
    echo ""
    echo "Note: This is the LITE version without TotalSegmentor/nnU-Net"
    echo "It includes all basic segmentation and radiomics features."
    echo ""
    echo "To run:"
    echo "  ./dist/lung_asp/lung_asp --help"
    echo ""
    echo "To package for distribution:"
    echo "  tar -czf lung_asp_lite_v1.0.0.tar.gz dist/lung_asp/"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Build failed!${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "Check the output above for errors."
    exit 1
fi

echo ""
echo "Done!"
