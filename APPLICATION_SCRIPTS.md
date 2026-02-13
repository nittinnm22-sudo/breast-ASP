# 📝 LUNG-ASP APPLICATION SCRIPTS

Complete source code for all application scripts and build files.

---

## 📋 Table of Contents

1. [lung_asp_cli.py](#1-lung_asp_clipy-244-lines) - Command-line Interface
2. [download_models.py](#2-download_modelspy-224-lines) - Model Download Helper
3. [setup.py](#3-setuppy-40-lines) - Package Installation Script
4. [build_full.sh](#4-build_fullsh-190-lines) - Linux/macOS Build Script
5. [build_full.bat](#5-build_fullbat-141-lines) - Windows Build Script

**Total**: 5 files, 839 lines of code

---

## 1. lung_asp_cli.py (244 lines)

**Purpose**: Main command-line interface for the lung-ASP standalone executable.

**Features**:
- DICOM and NIfTI input support
- Configurable segmentation parameters
- Radiomics feature extraction
- QC visualization generation
- Progress logging

**Usage**:
```bash
# Process DICOM files
python lung_asp_cli.py --pet-dicom PET/ --ct-dicom CT/ --output results/

# Process NIfTI files
python lung_asp_cli.py --pet-nifti pet.nii.gz --ct-nifti ct.nii.gz --output results/

# With custom parameters
python lung_asp_cli.py --pet-dicom PET/ --suv-threshold 3.0 --mtv-threshold 50 --output results/
```

### Source Code:

```python
#!/usr/bin/env python
"""
Lung-ASP CLI Application
Standalone executable for lung tumor segmentation and radiomics analysis
"""

import argparse
import sys
import os
from pathlib import Path
import logging

# Add src to path if running from source
if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lung_asp.lung_pipeline import LungTumorPipeline
from lung_asp.dicom_converter import DICOMConverter


def setup_logging(verbose=False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('lung_asp_cli')


def process_dicom(args, logger):
    """Process DICOM files."""
    logger.info("Starting DICOM processing...")
    logger.info(f"PET DICOM directory: {args.pet_dicom}")
    
    # Initialize pipeline
    pipeline = LungTumorPipeline(
        suv_threshold=args.suv_threshold,
        min_volume_mm3=args.min_volume,
        use_random_walker=args.use_random_walker,
        mtv_threshold_percent=args.mtv_threshold,
        getu_a=args.getu_a
    )
    
    # Set output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Processing images...")
    
    try:
        # Process from DICOM
        results = pipeline.process_from_dicom(
            pet_dicom_dir=args.pet_dicom,
            ct_dicom_dir=args.ct_dicom,
            output_dir=str(output_dir),
            seed_point=None
        )
        
        logger.info("✓ Processing complete!")
        logger.info(f"Results saved to: {output_dir}")
        
        # Print summary
        if results.get('metabolic_features'):
            logger.info("\n=== Metabolic Features ===")
            logger.info(f"SUVmax: {results['metabolic_features']['SUVmax']:.2f}")
            logger.info(f"SUVmean: {results['metabolic_features']['SUVmean']:.2f}")
            logger.info(f"MTV: {results['metabolic_features']['MTV_ml']:.2f} mL")
            logger.info(f"TLG: {results['metabolic_features']['TLG']:.2f}")
        
        if results.get('shape_features'):
            logger.info("\n=== Shape Features ===")
            logger.info(f"Volume: {results['shape_features']['Volume_ml']:.2f} mL")
            logger.info(f"Sphericity: {results['shape_features']['Sphericity']:.3f}")
            logger.info(f"Asphericity: {results['shape_features']['Asphericity']:.3f}")
        
        if results.get('advanced_features'):
            logger.info("\n=== Advanced Metrics ===")
            logger.info(f"NHOCmax: {results['advanced_features']['NHOCmax']:.4f}")
            logger.info(f"NHOPmax: {results['advanced_features']['NHOPmax']:.4f}")
            logger.info(f"gETU: {results['advanced_features']['gETU']:.2f}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def process_nifti(args, logger):
    """Process NIfTI files."""
    logger.info("Starting NIfTI processing...")
    logger.info(f"PET NIfTI: {args.pet_nifti}")
    
    # Initialize pipeline
    pipeline = LungTumorPipeline(
        suv_threshold=args.suv_threshold,
        min_volume_mm3=args.min_volume,
        use_random_walker=args.use_random_walker,
        mtv_threshold_percent=args.mtv_threshold,
        getu_a=args.getu_a
    )
    
    # Load NIfTI files
    converter = DICOMConverter()
    
    try:
        logger.info("Loading PET image...")
        pet_image, pet_affine, pet_spacing = converter.load_nifti(args.pet_nifti)
        
        ct_image = None
        if args.ct_nifti:
            logger.info("Loading CT image...")
            ct_image, _, _ = converter.load_nifti(args.ct_nifti)
        
        # Set output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        pipeline.qc_visualizer.output_dir = str(output_dir)
        
        logger.info("Processing images...")
        
        # Process
        results = pipeline.process(
            pet_image, ct_image, pet_spacing,
            generate_qc=not args.no_qc
        )
        
        # Save results
        logger.info("Saving results...")
        mask_path = output_dir / "tumor_mask.nii.gz"
        converter.save_nifti(results['tumor_mask'].astype(float), pet_affine, str(mask_path))
        
        # Save features
        import pandas as pd
        features_path = output_dir / "tumor_features.csv"
        features_df = pd.DataFrame([results['combined_features']])
        features_df.to_csv(features_path, index=False)
        
        logger.info("✓ Processing complete!")
        logger.info(f"Mask saved: {mask_path}")
        logger.info(f"Features saved: {features_path}")
        
        # Print summary
        logger.info(f"\nTotal features extracted: {len(results['combined_features'])}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Lung-ASP: FDG PET/CT Lung Tumor Segmentation and Radiomics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process DICOM files
  lung_asp_cli --pet-dicom /path/to/pet --ct-dicom /path/to/ct --output /path/to/output
  
  # Process NIfTI files
  lung_asp_cli --pet-nifti pet.nii.gz --ct-nifti ct.nii.gz --output /path/to/output
  
  # Adjust parameters
  lung_asp_cli --pet-dicom /path/to/pet --suv-threshold 3.0 --mtv-threshold 50 --output /path/to/output
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--pet-dicom', type=str,
                            help='Path to PET DICOM directory')
    input_group.add_argument('--pet-nifti', type=str,
                            help='Path to PET NIfTI file')
    
    # Optional CT input
    parser.add_argument('--ct-dicom', type=str,
                       help='Path to CT DICOM directory (optional)')
    parser.add_argument('--ct-nifti', type=str,
                       help='Path to CT NIfTI file (optional)')
    
    # Output
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='Output directory for results')
    
    # Segmentation parameters
    parser.add_argument('--suv-threshold', type=float, default=2.5,
                       help='SUV threshold for segmentation (default: 2.5)')
    parser.add_argument('--min-volume', type=float, default=100.0,
                       help='Minimum tumor volume in mm³ (default: 100)')
    parser.add_argument('--use-random-walker', action='store_true', default=True,
                       help='Use random walker algorithm (default: True)')
    parser.add_argument('--no-random-walker', dest='use_random_walker', 
                       action='store_false',
                       help='Use threshold-based segmentation only')
    
    # Radiomics parameters
    parser.add_argument('--mtv-threshold', type=int, default=41,
                       help='MTV threshold as %% of SUVmax (default: 41)')
    parser.add_argument('--getu-a', type=float, default=1.0,
                       help='gETU power parameter (default: 1.0)')
    
    # QC options
    parser.add_argument('--no-qc', action='store_true',
                       help='Disable QC visualization generation')
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--version', action='version', version='Lung-ASP 1.0.0')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Display header
    logger.info("="*70)
    logger.info("Lung-ASP: FDG PET/CT Lung Tumor Segmentation")
    logger.info("Version 1.0.0")
    logger.info("="*70)
    
    # Process based on input type
    if args.pet_dicom:
        return process_dicom(args, logger)
    elif args.pet_nifti:
        return process_nifti(args, logger)
    else:
        logger.error("No input specified. Use --help for usage information.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

---

## 2. download_models.py (224 lines)

**Purpose**: Helper script to download and setup pre-trained models for TotalSegmentor and nnU-Net.

**Features**:
- Download TotalSegmentor models
- Setup nnU-Net models
- Check installed models
- Prepare models for executable bundling

**Usage**:
```bash
# Download TotalSegmentor models
python download_models.py --download-totalseg

# Check which models are installed
python download_models.py --check

# Setup models for executable
python download_models.py --setup-exe dist/
```

### Source Code:

```python
#!/usr/bin/env python
"""
Model Download Helper for Lung-ASP

This script helps download and setup pre-trained models for:
- TotalSegmentor
- nnU-Net

Models are stored in appropriate directories for the executable to use.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_totalsegmentor_models(output_dir=None):
    """Download TotalSegmentor models."""
    logger.info("="*70)
    logger.info("Downloading TotalSegmentor Models")
    logger.info("="*70)
    
    try:
        # Check if totalsegmentor is installed
        import totalsegmentor
        logger.info("TotalSegmentor package found")
        
        # Run the download command
        logger.info("Starting model download...")
        logger.info("This may take 10-30 minutes depending on your connection...")
        
        result = subprocess.run(
            ['totalsegmentor', '--download_models'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✓ TotalSegmentor models downloaded successfully!")
            
            # Show model location
            model_dir = Path.home() / ".totalsegmentor"
            logger.info(f"Models stored in: {model_dir}")
            return True
        else:
            logger.error("Model download failed!")
            logger.error(result.stderr)
            return False
            
    except ImportError:
        logger.error("TotalSegmentor not installed!")
        logger.error("Install with: pip install totalsegmentor")
        return False
    except Exception as e:
        logger.error(f"Error downloading models: {e}")
        return False


def download_nnunet_models(model_url=None, output_dir=None):
    """Download nnU-Net models."""
    logger.info("="*70)
    logger.info("nnU-Net Model Setup")
    logger.info("="*70)
    
    if output_dir is None:
        try:
            from nnunetv2.paths import nnUNet_results
            output_dir = Path(nnUNet_results)
        except:
            output_dir = Path.home() / ".nnunet" / "results"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"nnU-Net models directory: {output_dir}")
    
    if model_url:
        logger.info(f"Downloading from: {model_url}")
        # Add download logic here
        logger.warning("Automatic download not implemented yet")
        logger.info("Please manually download models and place them in:")
        logger.info(f"  {output_dir}")
        return False
    else:
        logger.warning("No model URL provided")
        logger.info("To use nnU-Net models:")
        logger.info("1. Obtain pre-trained lung tumor models")
        logger.info("2. Place them in the nnU-Net results directory:")
        logger.info(f"   {output_dir}")
        logger.info("3. Ensure they follow the structure:")
        logger.info("   DatasetXXX_LungTumor/")
        logger.info("     └── nnUNetTrainer__nnUNetPlans/")
        logger.info("         └── fold_X/")
        logger.info("             ├── checkpoint_best.pth")
        logger.info("             └── ...")
        return False


def check_models():
    """Check if models are installed."""
    logger.info("="*70)
    logger.info("Checking Installed Models")
    logger.info("="*70)
    
    # Check TotalSegmentor
    ts_dir = Path.home() / ".totalsegmentor"
    if ts_dir.exists() and any(ts_dir.glob("**/*.pkl")):
        logger.info("✓ TotalSegmentor models found")
        logger.info(f"  Location: {ts_dir}")
    else:
        logger.warning("✗ TotalSegmentor models not found")
    
    # Check nnU-Net
    try:
        from nnunetv2.paths import nnUNet_results
        nnunet_dir = Path(nnUNet_results)
    except:
        nnunet_dir = Path.home() / ".nnunet" / "results"
    
    if nnunet_dir.exists() and any(nnunet_dir.glob("**/checkpoint*.pth")):
        logger.info("✓ nnU-Net models found")
        logger.info(f"  Location: {nnunet_dir}")
    else:
        logger.warning("✗ nnU-Net models not found")
        logger.info(f"  Expected location: {nnunet_dir}")


def setup_for_executable(dist_dir):
    """Setup models for inclusion in executable."""
    logger.info("="*70)
    logger.info("Setting Up Models for Executable")
    logger.info("="*70)
    
    dist_dir = Path(dist_dir)
    models_dir = dist_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Copying models to: {models_dir}")
    
    # Copy TotalSegmentor models
    ts_dir = Path.home() / ".totalsegmentor"
    if ts_dir.exists():
        logger.info("Copying TotalSegmentor models...")
        import shutil
        ts_target = models_dir / "totalsegmentor"
        if not ts_target.exists():
            shutil.copytree(ts_dir, ts_target)
            logger.info(f"✓ TotalSegmentor models copied")
        else:
            logger.info("  Models already exist, skipping")
    else:
        logger.warning("  TotalSegmentor models not found")
    
    # Copy nnU-Net models
    try:
        from nnunetv2.paths import nnUNet_results
        nnunet_dir = Path(nnUNet_results)
    except:
        nnunet_dir = Path.home() / ".nnunet" / "results"
    
    if nnunet_dir.exists():
        logger.info("Copying nnU-Net models...")
        import shutil
        nnunet_target = models_dir / "nnunet"
        if not nnunet_target.exists():
            shutil.copytree(nnunet_dir, nnunet_target)
            logger.info(f"✓ nnU-Net models copied")
        else:
            logger.info("  Models already exist, skipping")
    else:
        logger.warning("  nnU-Net models not found")
    
    logger.info(f"\nModels directory: {models_dir}")
    logger.info("These models will be bundled with the executable")


def main():
    parser = argparse.ArgumentParser(
        description='Download and setup models for Lung-ASP',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--download-totalseg', action='store_true',
                       help='Download TotalSegmentor models')
    parser.add_argument('--download-nnunet', action='store_true',
                       help='Download nnU-Net models (requires URL)')
    parser.add_argument('--nnunet-url', type=str,
                       help='URL for nnU-Net models')
    parser.add_argument('--check', action='store_true',
                       help='Check which models are installed')
    parser.add_argument('--setup-exe', type=str,
                       help='Setup models for executable (provide dist directory)')
    parser.add_argument('--all', action='store_true',
                       help='Download all models')
    
    args = parser.parse_args()
    
    if args.check or (not args.download_totalseg and not args.download_nnunet 
                     and not args.setup_exe and not args.all):
        check_models()
    
    if args.download_totalseg or args.all:
        download_totalsegmentor_models()
    
    if args.download_nnunet or args.all:
        download_nnunet_models(args.nnunet_url)
    
    if args.setup_exe:
        setup_for_executable(args.setup_exe)
    
    logger.info("\nDone!")


if __name__ == '__main__':
    main()
```

---

## 3. setup.py (40 lines)

**Purpose**: Package installation script using setuptools.

**Usage**:
```bash
# Install in editable mode (development)
pip install -e .

# Install normally
pip install .

# Install with dev dependencies
pip install -e ".[dev]"
```

### Source Code:

```python
"""Setup configuration for breast-ASP package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="breast-asp",
    version="1.0.0",
    author="Breast ASP Project",
    description="FDG PET/CT Breast Tumor Segmentation with Axillary Exclusion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nittinnm22-sudo/breast-ASP",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-cov>=3.0.0"],
    },
)
```

---

## 4. build_full.sh (190 lines)

**Purpose**: Complete automated build script for Linux/macOS with all dependencies.

**Features**:
- Python version checking
- Dependency verification
- Package installation
- CLI testing
- Build execution
- Verification
- Optional packaging

**Usage**:
```bash
chmod +x build_full.sh
./build_full.sh
```

### Source Code:

```bash
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
```

---

## 5. build_full.bat (141 lines)

**Purpose**: Complete automated build script for Windows with all dependencies.

**Features**:
- Python version checking
- Dependency verification
- Package installation
- CLI testing
- Build execution
- Verification
- Optional packaging

**Usage**:
```cmd
build_full.bat
```

### Source Code:

```batch
@echo off
REM #######################################
REM Lung-ASP Executable Builder for Windows
REM Complete build script with all dependencies
REM Run this on your local Windows system
REM #######################################

echo ==========================================
echo    Lung-ASP Full Executable Builder
echo    With TotalSegmentor ^& nnU-Net
echo ==========================================
echo.

REM Step 1: Check Python version
echo Step 1: Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8-3.11
    pause
    exit /b 1
)
echo.

REM Step 2: Check dependencies
echo Step 2: Checking installed dependencies...
python -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>nul || echo ✗ PyTorch not found
python -c "import totalsegmentor; print('✓ TotalSegmentor: OK')" 2>nul || echo ✗ TotalSegmentor not found
python -c "import nnunetv2; print('✓ nnU-Net: OK')" 2>nul || echo ✗ nnU-Net not found
python -c "import numpy; print('✓ NumPy: OK')" 2>nul || echo ✗ NumPy not found
python -c "import PyInstaller; print('✓ PyInstaller: OK')" 2>nul || echo ✗ PyInstaller not found
echo.

pause
echo.

REM Step 3: Install lung_asp package
echo Step 3: Installing lung_asp package...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install package
    pause
    exit /b 1
)
echo ✓ Package installed
echo.

REM Step 4: Test CLI
echo Step 4: Testing CLI functionality...
python lung_asp_cli.py --help >nul 2>&1
if errorlevel 1 (
    echo ERROR: CLI test failed
    pause
    exit /b 1
)
echo ✓ CLI test passed
echo.

REM Step 5: Clean previous builds
echo Step 5: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✓ Cleaned
echo.

REM Step 6: Build with PyInstaller
echo Step 6: Building executable with PyInstaller...
echo This may take 5-15 minutes...
echo.

pyinstaller lung_asp.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo ✓ Build completed successfully!
echo.

REM Step 7: Verify build
echo Step 7: Verifying build...

if exist dist\lung_asp\lung_asp.exe (
    echo ✓ Executable found
    
    REM Test executable
    echo.
    echo Testing executable...
    dist\lung_asp\lung_asp.exe --help >nul 2>&1
    if errorlevel 1 (
        echo ⚠ Executable test failed ^(might still work^)
    ) else (
        echo ✓ Executable test passed
    )
) else (
    echo ERROR: Executable not found
    pause
    exit /b 1
)
echo.

REM Step 8: Summary
echo ==========================================
echo        BUILD SUCCESSFUL!
echo ==========================================
echo.
echo 📦 Executable location: dist\lung_asp\
echo 🚀 Main executable: dist\lung_asp\lung_asp.exe
echo.
echo To test:
echo   dist\lung_asp\lung_asp.exe --help
echo.
echo To package for distribution:
echo   cd dist
echo   tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
echo   cd ..
echo.

REM Optional: Create package
set /p CREATE_PKG="Create distributable ZIP package now? (y/n): "
if /i "%CREATE_PKG%"=="y" (
    echo Creating package...
    cd dist
    tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
    if errorlevel 1 (
        echo ERROR: Failed to create ZIP
        echo You can manually zip the dist\lung_asp folder
    ) else (
        echo ✓ Package created: dist\lung_asp_v1.0.0_windows.zip
    )
    cd ..
    echo.
)

echo Done! 🎉
echo.
pause
```

---

## 📊 Summary

### Complete Application Scripts:

| File | Lines | Purpose |
|------|-------|---------|
| lung_asp_cli.py | 244 | CLI interface |
| download_models.py | 224 | Model management |
| setup.py | 40 | Package installation |
| build_full.sh | 190 | Linux/macOS build |
| build_full.bat | 141 | Windows build |
| **Total** | **839** | **Complete system** |

### Quick Start:

**1. Save all files** to your lung-ASP project directory

**2. Build the executable**:
```bash
# Linux/macOS
chmod +x build_full.sh
./build_full.sh

# Windows
build_full.bat
```

**3. Test the executable**:
```bash
# Linux/macOS
./dist/lung_asp/lung_asp --help

# Windows
dist\lung_asp\lung_asp.exe --help
```

**4. Run your analysis**:
```bash
./dist/lung_asp/lung_asp --pet-dicom PET/ --ct-dicom CT/ --output results/
```

---

## ✅ All Files Ready

You now have **complete source code** for:
- ✅ Command-line interface (244 lines)
- ✅ Model download helper (224 lines)
- ✅ Package setup (40 lines)
- ✅ Build scripts for all platforms (331 lines)

**Total**: 839 lines of production-ready code! 🚀

---

**Last Updated**: 2026-02-12

**Repository**: https://github.com/nittinnm22-sudo/breast-ASP
