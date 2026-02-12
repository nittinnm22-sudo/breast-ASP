#!/bin/bash
#######################################
# Lung-ASP Executable Builder
# Complete build script with all dependencies
# Run this on your local system
#######################################

set -e  # Exit on error

echo "=========================================="
echo "   Lung-ASP Full Executable Builder"
echo "   With TotalSegmentor & nnU-Net"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo -e "${BLUE}Step 1: Checking Python version...${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ] && [ "$MINOR" -le 11 ]; then
    echo -e "${GREEN}✓ Python version OK${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Python $PYTHON_VERSION detected. Recommended: 3.8-3.11${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# Step 2: Check dependencies
echo -e "${BLUE}Step 2: Checking installed dependencies...${NC}"

check_package() {
    python -c "import $1" 2>/dev/null && echo -e "${GREEN}✓ $1${NC}" || echo -e "${RED}✗ $1 not found${NC}"
}

check_package "torch"
check_package "totalsegmentor"
check_package "nnunetv2"
check_package "numpy"
check_package "scipy"
check_package "nibabel"
check_package "pydicom"
check_package "PyInstaller"

echo ""
read -p "Are all required packages installed? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Please install missing packages first:${NC}"
    echo "  pip install -r requirements_exe.txt"
    exit 1
fi
echo ""

# Step 3: Install lung_asp package
echo -e "${BLUE}Step 3: Installing lung_asp package...${NC}"
pip install -e .
echo -e "${GREEN}✓ Package installed${NC}"
echo ""

# Step 4: Test CLI before building
echo -e "${BLUE}Step 4: Testing CLI functionality...${NC}"
python lung_asp_cli.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ CLI test passed${NC}"
else
    echo -e "${RED}✗ CLI test failed${NC}"
    exit 1
fi
echo ""

# Step 5: Clean previous builds
echo -e "${BLUE}Step 5: Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.spec~ 2>/dev/null
echo -e "${GREEN}✓ Cleaned${NC}"
echo ""

# Step 6: Build with PyInstaller
echo -e "${BLUE}Step 6: Building executable with PyInstaller...${NC}"
echo "This may take 5-15 minutes..."
echo ""

pyinstaller lung_asp.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Build completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Build failed!${NC}"
    echo "Check the output above for errors."
    exit 1
fi
echo ""

# Step 7: Verify build
echo -e "${BLUE}Step 7: Verifying build...${NC}"

if [ -f "dist/lung_asp/lung_asp" ] || [ -f "dist/lung_asp/lung_asp.exe" ]; then
    echo -e "${GREEN}✓ Executable found${NC}"
    
    # Get size
    SIZE=$(du -sh dist/lung_asp | cut -f1)
    echo "Package size: $SIZE"
    
    # Test executable
    echo ""
    echo "Testing executable..."
    if [ -f "dist/lung_asp/lung_asp" ]; then
        ./dist/lung_asp/lung_asp --help > /dev/null 2>&1
    else
        ./dist/lung_asp/lung_asp.exe --help > /dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Executable test passed${NC}"
    else
        echo -e "${YELLOW}⚠ Executable test failed (might still work)${NC}"
    fi
else
    echo -e "${RED}✗ Executable not found${NC}"
    exit 1
fi
echo ""

# Step 8: Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       BUILD SUCCESSFUL!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📦 Executable location: dist/lung_asp/"
if [ -f "dist/lung_asp/lung_asp" ]; then
    echo "🚀 Main executable: dist/lung_asp/lung_asp"
else
    echo "🚀 Main executable: dist/lung_asp/lung_asp.exe"
fi
echo "📊 Package size: $SIZE"
echo ""
echo "To test:"
if [ -f "dist/lung_asp/lung_asp" ]; then
    echo "  ./dist/lung_asp/lung_asp --help"
else
    echo "  dist\\lung_asp\\lung_asp.exe --help"
fi
echo ""
echo "To package for distribution:"
echo "  cd dist"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "  tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp"
else
    echo "  tar -czf lung_asp_v1.0.0_$(uname -s)_$(uname -m).tar.gz lung_asp/"
fi
echo ""

# Optional: Create package
read -p "Create distributable package now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Creating package...${NC}"
    cd dist
    
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        PACKAGE_NAME="lung_asp_v1.0.0_windows.zip"
        tar -a -c -f $PACKAGE_NAME lung_asp
    else
        PACKAGE_NAME="lung_asp_v1.0.0_$(uname -s)_$(uname -m).tar.gz"
        tar -czf $PACKAGE_NAME lung_asp/
    fi
    
    cd ..
    echo -e "${GREEN}✓ Package created: dist/$PACKAGE_NAME${NC}"
    echo ""
fi

echo "Done! 🎉"
echo ""
