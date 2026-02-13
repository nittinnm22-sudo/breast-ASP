# Lung-ASP Standalone Executable

## Overview

This directory contains everything needed to build Lung-ASP as a standalone executable application with TotalSegmentor and nnU-Net integration.

## Features

- **Standalone Executable**: No Python installation required
- **Complete Dependencies**: All Python packages bundled
- **TotalSegmentor Integration**: Anatomical structure segmentation
- **nnU-Net Integration**: Deep learning tumor segmentation
- **Command-Line Interface**: Easy-to-use CLI
- **Cross-Platform**: Build for Windows, Linux, and macOS

## Prerequisites for Building

### System Requirements
- Python 3.8 or higher
- 8GB+ RAM (16GB recommended)
- 10GB+ free disk space
- CUDA-capable GPU (optional, for faster processing)

### Software Requirements
- Git (for cloning)
- Python development headers
- C++ compiler (for some dependencies)

#### Windows
```bash
# Install Python from python.org
# Install Microsoft Visual C++ Build Tools
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-venv gcc g++ git
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

## Building the Executable

### Step 1: Clone Repository
```bash
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP
```

### Step 2: Run Build Script

#### Linux/macOS
```bash
./build_exe.sh
```

#### Windows
```batch
build_exe.bat
```

The build process will:
1. Create a virtual environment
2. Install all dependencies (this takes 10-30 minutes)
3. Build the executable with PyInstaller
4. Create the distributable package in `dist/lung_asp/`

### Step 3: Download Models (Important!)

The executable needs pre-trained models to function:

#### TotalSegmentor Models
```bash
# Activate the build environment
source venv_build/bin/activate  # Linux/macOS
# or
venv_build\Scripts\activate.bat  # Windows

# Download models
totalsegmentor --download_models
```

#### nnU-Net Models
nnU-Net models need to be obtained separately:
1. Download from: [Model source - provide link]
2. Place in: `~/.nnunet/results/` (Linux/macOS) or `%USERPROFILE%\.nnunet\results\` (Windows)
3. Or bundle with the executable in `dist/lung_asp/models/`

## Using the Executable

### Basic Usage

```bash
# Show help
./dist/lung_asp/lung_asp --help

# Process DICOM files
./dist/lung_asp/lung_asp \
  --pet-dicom /path/to/pet/dicom \
  --ct-dicom /path/to/ct/dicom \
  --output /path/to/output

# Process NIfTI files
./dist/lung_asp/lung_asp \
  --pet-nifti pet_image.nii.gz \
  --ct-nifti ct_image.nii.gz \
  --output /path/to/output
```

### Advanced Options

```bash
# Adjust segmentation parameters
./dist/lung_asp/lung_asp \
  --pet-dicom /path/to/pet \
  --suv-threshold 3.0 \
  --min-volume 200 \
  --mtv-threshold 50 \
  --output /path/to/output \
  --verbose

# Disable random walker (faster but less accurate)
./dist/lung_asp/lung_asp \
  --pet-nifti pet.nii.gz \
  --no-random-walker \
  --output /path/to/output

# Skip QC visualization generation
./dist/lung_asp/lung_asp \
  --pet-nifti pet.nii.gz \
  --no-qc \
  --output /path/to/output
```

## Output Files

The executable creates:
- `tumor_mask.nii.gz` - Binary segmentation mask
- `tumor_features.csv` - All 32 radiomics features
- `Mask_QC.png` - Quality control overlay (3 orthogonal views)
- `QC_Report.png` - Comprehensive report with metrics
- `PET_converted.nii.gz` - Converted PET image (if from DICOM)
- `CT_converted.nii.gz` - Converted CT image (if from DICOM)

## Distribution

### Creating a Release Package

#### Linux/macOS
```bash
cd dist
tar -czf lung_asp_v1.0.0_linux_x64.tar.gz lung_asp/
```

#### Windows
```batch
cd dist
# Use 7-Zip or built-in compression
tar -czf lung_asp_v1.0.0_windows_x64.zip lung_asp/
```

### Package Contents
```
lung_asp/
├── lung_asp(.exe)           # Main executable
├── _internal/               # Bundled dependencies
│   ├── numpy/
│   ├── torch/
│   ├── totalsegmentor/
│   ├── nnunetv2/
│   └── ...
├── models/                  # Optional: bundled models
│   ├── totalsegmentor/
│   └── nnunet/
└── README.txt              # User documentation
```

## Troubleshooting

### Build Issues

**Problem**: PyInstaller fails with "module not found"
- **Solution**: Add missing modules to `hiddenimports` in `lung_asp.spec`

**Problem**: Out of memory during build
- **Solution**: Close other applications, use `--exclude` in spec file

**Problem**: Missing DLL/shared library errors
- **Solution**: Install Visual C++ Redistributables (Windows) or required system libraries (Linux)

### Runtime Issues

**Problem**: "Models not found"
- **Solution**: Ensure models are downloaded and in correct location

**Problem**: CUDA errors
- **Solution**: Run with CPU mode or install correct CUDA version

**Problem**: "Permission denied"
- **Solution**: Make executable: `chmod +x lung_asp` (Linux/macOS)

### Model Issues

**Problem**: TotalSegmentor models not loading
- **Solution**: 
  1. Check model directory exists
  2. Re-download models: `totalsegmentor --download_models`
  3. Ensure models are in `~/.totalsegmentor/` or bundled with exe

**Problem**: nnU-Net prediction fails
- **Solution**:
  1. Verify model structure matches nnU-Net requirements
  2. Check model was trained with compatible nnU-Net version
  3. Test with smaller image first

## Development Notes

### Modifying the Executable

To add new features:
1. Edit source files in `src/lung_asp/`
2. Update `lung_asp_cli.py` if changing CLI
3. Rebuild: `./build_exe.sh`

### Optimizing Size

The executable is large (1-3 GB) due to:
- PyTorch and deep learning libraries
- TotalSegmentor and nnU-Net
- All dependencies

To reduce size:
- Use `--exclude-module` in spec file
- Build without GPU support: exclude CUDA libraries
- Use one-file mode (slower startup but single file)

### Custom Models

To bundle custom models:
1. Place models in `models/` directory
2. Update `lung_asp.spec` datas section
3. Modify wrapper code to load from bundled location

## Performance

### Expected Processing Times

- **DICOM Conversion**: 10-30 seconds
- **Segmentation (CPU)**: 2-5 minutes per case
- **Segmentation (GPU)**: 30 seconds - 2 minutes per case
- **Radiomics Extraction**: 10-30 seconds
- **QC Generation**: 5-15 seconds

### Hardware Recommendations

**Minimum**:
- CPU: 4 cores, 2.5 GHz
- RAM: 8 GB
- Storage: 5 GB for software + models

**Recommended**:
- CPU: 8+ cores, 3.0+ GHz
- RAM: 16+ GB
- GPU: NVIDIA with 6+ GB VRAM
- Storage: 20+ GB (SSD preferred)

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/nittinnm22-sudo/breast-ASP/issues
- Documentation: See main README.md

## License

See LICENSE file in the main repository.

## Citation

If you use this software in your research, please cite:
```
Lung-ASP: FDG PET/CT Lung Tumor Segmentation and Radiomics Analysis
https://github.com/nittinnm22-sudo/breast-ASP
```
