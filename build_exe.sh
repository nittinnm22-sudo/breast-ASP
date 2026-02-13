#!/bin/bash
# Build script for Lung-ASP standalone executable

set -e  # Exit on error

echo "========================================"
echo "Lung-ASP Executable Build Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment should be created
if [ ! -d "venv_build" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv_build
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv_build/bin/activate || . venv_build/Scripts/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
echo "This may take a while (especially PyTorch)..."
pip install -r requirements_exe.txt

# Install the package
echo -e "${YELLOW}Installing lung_asp package...${NC}"
pip install -e .

# Download models (optional - can be done manually)
echo -e "${YELLOW}Note: Pre-trained models should be downloaded separately${NC}"
echo "  - TotalSegmentor: Run 'totalsegmentor --download_models'"
echo "  - nnU-Net: Place models in appropriate directory"
echo ""

# Build with PyInstaller
echo -e "${YELLOW}Building executable with PyInstaller...${NC}"
pyinstaller lung_asp.spec --clean --noconfirm

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
    echo "To run:"
    echo "  ./dist/lung_asp/lung_asp --help"
    echo ""
    echo "To package for distribution:"
    echo "  zip -r lung_asp_v1.0.0.zip dist/lung_asp/"
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

# Optional: Create distributable package
read -p "Create distributable ZIP package? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Creating ZIP package...${NC}"
    cd dist
    zip -r lung_asp_v1.0.0_$(uname -s)_$(uname -m).zip lung_asp/
    cd ..
    echo -e "${GREEN}Package created: dist/lung_asp_v1.0.0_$(uname -s)_$(uname -m).zip${NC}"
fi

echo ""
echo "Done!"
