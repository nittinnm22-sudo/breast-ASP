# Lung ASP

FDG PET/CT Lung Tumor Segmentation with Mediastinal Exclusion

## 🚀 Quick Start

**Want to build a standalone executable?** 
👉 **[COMPLETE DOWNLOAD & BUILD GUIDE](COMPLETE_DOWNLOAD_BUILD_GUIDE.md)** - Start here!

**Quick visual overview?**
👉 **[QUICK VISUAL GUIDE](QUICK_VISUAL_GUIDE.md)** - Diagrams and flowcharts

**Already downloaded? Verify your files:**
```bash
python verify_download.py
```

---

## Overview

Lung ASP is a comprehensive pipeline for automated primary lung tumor segmentation and radiomics extraction from FDG PET/CT imaging. The pipeline implements:

- **CT-based thoracic body mask** constraint (HU −500 to +1000)
- **Comprehensive anatomical exclusion** via TotalSegmentator (mediastinum, spine, ribs, vessels, organs)
- **Random walker segmentation** with clinically validated seed thresholds (5% FG, 2% BG, β=5)
- **Complete radiomics suite**: SUVmax, SUVmean, SUVpeak, MTV, TLG, Dmax, NHOCmax, NHOPmax, gETU, sphericity/asphericity
- **High-quality QC overlays** with 3-plane visualization

## Features

### Core Segmentation
- Thoracic body mask from CT (HU thresholding + morphological closing)
- TotalSegmentator-based anatomical exclusion (40+ structures)
- Random walker with correct clinical parameters
- Post-processing and refinement

### Radiomics Metrics
- **SUV Statistics**: SUVmax, SUVmean, SUVpeak (PERCIST 1cm³ sphere)
- **Volume Metrics**: MTV (41% threshold), TLG, tumor volume
- **Spatial Metrics**: Intra-lesion Dmax, NHOCmax, NHOPmax
- **Shape Metrics**: Sphericity (Ψ), Asphericity (ASP)
- **Advanced Uptake**: gETU for α = 0.25, 0.5, 1.0, 2.0, 4.0

### DICOM Support & GPU Acceleration
- **Direct DICOM input** - No pre-conversion needed
- **Automatic NIfTI conversion** using dicom2nifti
- **Geometry preservation** - ImageOrientation, PixelSpacing maintained
- **GPU acceleration** - NVIDIA GPU support for faster processing (RTX 4050, 6GB VRAM tested)
- See [DICOM_GPU_GUIDE.md](DICOM_GPU_GUIDE.md) for details

### Quality Control
- 3-plane orthogonal overlays (axial, coronal, sagittal)
- Tumor contours on PET and CT
- Constraint mask visualization
- High-resolution 300 DPI output

## 📦 Building Standalone Executable (Recommended)

### Want a standalone .exe/.app with ALL dependencies built-in?

**📖 Complete Guide:** [COMPLETE_DOWNLOAD_BUILD_GUIDE.md](COMPLETE_DOWNLOAD_BUILD_GUIDE.md) ⭐ **Start Here!**

**🎨 Visual Guide:** [QUICK_VISUAL_GUIDE.md](QUICK_VISUAL_GUIDE.md)

**Quick steps:**
1. Download this repository: `git clone https://github.com/nittinnm22-sudo/breast-ASP.git`
2. Verify files: `python verify_download.py`
3. Build: `build_executable.bat` (Windows) or `./build_executable.sh` (Mac/Linux)
4. Wait 20-30 minutes
5. Get standalone app in `dist/LungASP/`

**What's included in the executable:**
- ✅ Python runtime (target computers don't need Python)
- ✅ TotalSegmentator (complete)
- ✅ nnU-Net v2 (nnunetv2)
- ✅ All Python dependencies
- ✅ DICOM to NIfTI conversion
- ✅ GPU support (CUDA libraries)
- ✅ GUI interface

**Distribution:**
- Copy entire `dist/LungASP/` folder to any computer
- No installation required - just run!
- Works on computers without Python

---

## Installation (For Development Only)

### Requirements
- Python ≥ 3.10
- Dependencies: see `requirements-full.txt`

### Quick Install

```bash
# Install all dependencies including dicom2nifti, TotalSegmentator, nnU-Net
pip install -r requirements-full.txt

# For GPU support (NVIDIA with CUDA 12.x)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Or use automated scripts:

```bash
# Linux/Mac
./build_full.sh

# Windows
build_full.bat
```

Or manual installation:

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

### Command Line Interface

```bash
lung-asp --pet pet.nii.gz --ct ct.nii.gz --output ./results --case patient001 --generate-qc
```

### Graphical User Interface

```bash
# Linux/Mac
python3 src/Lung_ASP_GUI.py

# Windows
RUN_GUI.bat
```

### Python API

```python
from Lung_ASP import process_case

metrics = process_case(
    pet_nifti_path="pet.nii.gz",
    ct_nifti_path="ct.nii.gz",
    out_dir="./results",
    case_id="patient001"
)

print(f"SUVmax: {metrics['SUVmax']:.2f}")
print(f"MTV: {metrics['MTV_ml']:.2f} mL")
```

## Output Files

For each case, the pipeline generates:

- `<case>_tumor_mask.nii.gz` - Binary tumor segmentation
- `<case>_body_mask.nii.gz` - Thoracic body constraint mask
- `<case>_exclusion_mask.nii.gz` - Anatomical exclusion mask
- `<case>_pet_resampled.nii.gz` - PET resampled to CT space
- `<case>_metrics.json` - All computed metrics (JSON)
- `<case>_metrics.csv` - All computed metrics (CSV)
- `<case>_qc_overlay.png` - QC visualization (if enabled)
- `<case>_totalseg/` - TotalSegmentator output directory

## Clinical Methodology

### Seed Thresholds
- Foreground: 5% of SUVmax (candidate pool)
- Background: 2% of SUVmax (candidate pool)

### Random Walker Parameters
- Beta (β): 5
- Solver tolerance: 1×10⁻²
- Mode: Conjugate gradient multigrid

### Anatomical Exclusion
- Mediastinum: heart, aorta, esophagus, trachea, pulmonary veins
- Vessels: vena cava, brachiocephalic, subclavian
- Skeleton: spine (C7-T12, L1), ribs (1-12 bilateral), sternum, scapulae
- Organs: liver, spleen, stomach, kidneys, thyroid

### Shape Metrics
- Sphericity: Ψ = π^(1/3) × (6V)^(2/3) / A
- Asphericity: ASP = 1 − Ψ

## Citation

If you use this software in your research, please cite appropriately.

*Note: This is research software. Formal citation information will be added upon publication.*

## Repository Note

This repository is named `breast-ASP` but contains the Lung ASP (lung tumor segmentation) implementation. The package name is `lung-asp`.

## License

MIT License - see LICENSE file for details
