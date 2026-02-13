# Building Lung-ASP Executable Locally

Complete guide for building the Lung-ASP standalone executable on your local machine with all dependencies (TotalSegmentor, nnU-Net, PyTorch) included.

## Prerequisites

### System Requirements
- Windows 10/11, Linux (Ubuntu 20.04+), or macOS 10.15+
- Python 3.8 - 3.11 (Python 3.12 may have compatibility issues with some packages)
- 16GB RAM minimum (32GB recommended)
- 20GB free disk space
- GPU with CUDA support (optional, for faster processing)

### Installed Packages (Already on Your System)
You mentioned you have these installed:
- ✅ TotalSegmentor
- ✅ nnU-Net (nnunetv2)
- ✅ PyTorch
- ✅ All other dependencies

## Quick Start - Build Commands

### Option 1: Full Build (Recommended - Includes TotalSegmentor & nnU-Net)

```bash
# Navigate to project directory
cd /path/to/breast-ASP

# Run the build script
# For Linux/macOS:
chmod +x build_exe.sh
./build_exe.sh

# For Windows:
build_exe.bat
```

### Option 2: Manual Step-by-Step Build

#### Step 1: Install the Package
```bash
pip install -e .
```

#### Step 2: Verify Dependencies
```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import totalsegmentor; print('TotalSegmentor: OK')"
python -c "import nnunetv2; print('nnU-Net: OK')"
python -c "import lung_asp; print('Lung-ASP: OK')"
```

#### Step 3: Build with PyInstaller
```bash
# Clean previous builds
rm -rf build/ dist/

# Build the executable
pyinstaller lung_asp.spec --clean --noconfirm
```

#### Step 4: Verify Build
```bash
# Check if executable was created
ls -lh dist/lung_asp/

# Test the executable
./dist/lung_asp/lung_asp --help
```

## Detailed Build Process

### 1. Check Python Version
```bash
python --version
# Should be 3.8 - 3.11
```

### 2. Activate Virtual Environment (Optional but Recommended)
```bash
# Create virtual environment
python -m venv venv_build

# Activate it
# Linux/macOS:
source venv_build/bin/activate
# Windows:
venv_build\Scripts\activate
```

### 3. Ensure All Dependencies Are Installed
```bash
# Install from requirements_exe.txt
pip install -r requirements_exe.txt

# Or install individually if needed:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118  # For CUDA 11.8
pip install totalsegmentor
pip install nnunetv2
pip install pyinstaller>=5.10.0
```

### 4. Install Lung-ASP Package
```bash
pip install -e .
```

### 5. Test Before Building
```bash
# Test the CLI directly
python lung_asp_cli.py --help

# Test with a simple command
python lung_asp_cli.py --version
```

### 6. Build the Executable
```bash
pyinstaller lung_asp.spec --clean --noconfirm
```

**Build Time**: 5-15 minutes depending on your system

### 7. Post-Build Steps

#### Check Build Output
```bash
# View build directory structure
ls -R dist/lung_asp/ | head -50

# Check executable size
du -sh dist/lung_asp/
```

#### Test the Executable
```bash
# Navigate to dist directory
cd dist/lung_asp/

# Test help command
./lung_asp --help

# Test version
./lung_asp --version
```

## Package for Distribution

### Create ZIP Archive (Windows)
```cmd
cd dist
tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
```

### Create TAR.GZ Archive (Linux/macOS)
```bash
cd dist
tar -czf lung_asp_v1.0.0_$(uname -s)_$(uname -m).tar.gz lung_asp/
```

## Expected Output

### Build Success Indicators
```
✓ BUILD COMPLETED SUCCESSFULLY
✓ Executable location: dist/lung_asp/
✓ Main executable: dist/lung_asp/lung_asp (or lung_asp.exe on Windows)
```

### Package Size Estimates
- **Base executable + dependencies**: 1-2 GB
- **With TotalSegmentor models**: +300-500 MB
- **With nnU-Net models**: +500-1000 MB per model
- **Total package**: 2-4 GB (depending on models included)

### Directory Structure After Build
```
dist/
└── lung_asp/
    ├── lung_asp (or lung_asp.exe)        # Main executable
    └── _internal/                         # Dependencies and libraries
        ├── numpy/
        ├── scipy/
        ├── torch/
        ├── totalsegmentor/
        ├── nnunetv2/
        └── ... (other packages)
```

## Bundling Pre-trained Models

### TotalSegmentor Models
Models are automatically downloaded on first use, but you can bundle them:

```bash
# Download models before building
totalsegmentor --download_models

# Models are stored in:
# Linux/macOS: ~/.totalsegmentor/nnunet/results/
# Windows: C:\Users\<username>\.totalsegmentor\nnunet\results\
```

To bundle models in the executable:
1. Edit `lung_asp.spec`
2. Add to `datas`:
```python
datas += [('/path/to/.totalsegmentor', 'totalsegmentor')]
```

### nnU-Net Models
```bash
# Set environment variable for model directory
export nnUNet_results="/path/to/nnUNet_results"

# Bundle models by adding to lung_asp.spec:
datas += [(os.environ['nnUNet_results'], 'nnunet_models')]
```

## Troubleshooting

### Issue: PyInstaller Not Found
```bash
pip install --upgrade pyinstaller
```

### Issue: Missing Dependencies
```bash
# Install all requirements
pip install -r requirements_exe.txt

# Or check what's missing
python -c "import PyInstaller; import torch; import totalsegmentor; import nnunetv2"
```

### Issue: Build Fails with Import Errors
Check the `build/lung_asp/warn-lung_asp.txt` file for missing modules and add them to `hiddenimports` in `lung_asp.spec`.

### Issue: Executable Crashes on Start
```bash
# Run with debug mode
./dist/lung_asp/lung_asp --debug

# Check if models are accessible
./dist/lung_asp/lung_asp --check-dependencies
```

### Issue: CUDA/GPU Not Detected
```bash
# Test PyTorch CUDA
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# If false, reinstall PyTorch with CUDA:
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Large Executable Size
To reduce size:
1. Use `--strip` flag in PyInstaller
2. Exclude unnecessary backends: `excludes=['tkinter', 'PyQt5', 'PyQt6']`
3. Don't bundle models (download on first use instead)
4. Use UPX compression (enabled by default)

## Advanced Configuration

### Custom Spec File Modifications

Edit `lung_asp.spec` to customize:

```python
# Exclude packages to reduce size
excludes=[
    'tkinter',
    'PyQt5',
    'PyQt6',
    'jupyter',
    'IPython',
],

# Add custom data files
datas += [
    ('path/to/custom/models', 'models'),
    ('path/to/config.json', '.'),
],

# Add runtime hooks
runtime_hooks=['hooks/runtime_hook.py'],

# One-file build (slower startup, single .exe)
# Comment out COLLECT section and use:
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lung_asp',
    debug=False,
    upx=True,
    console=True,
)
```

### GPU-Only Build
If building for GPU systems only, you can exclude CPU-only libraries:
```python
excludes += ['torch.cpu', 'cpuinfo']
```

### Minimal Build (No Deep Learning)
For testing or CPU-limited systems:
```python
excludes += ['totalsegmentor', 'nnunetv2', 'torch']
```

## Platform-Specific Notes

### Windows
- Install Visual C++ Redistributable 2015-2022
- May need Windows SDK for some packages
- Use `build_exe.bat` script
- Executable will be `lung_asp.exe`

### Linux
- Install build essentials: `sudo apt-get install build-essential`
- May need additional libraries: `sudo apt-get install libssl-dev libffi-dev`
- Use `build_exe.sh` script
- Executable will be `lung_asp`

### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- May need to codesign the app
- Use `build_exe.sh` script
- Executable will be `lung_asp`

## Verification Checklist

After building, verify:

- [ ] Executable runs: `./dist/lung_asp/lung_asp --help`
- [ ] Dependencies load: `./dist/lung_asp/lung_asp --check-dependencies`
- [ ] TotalSegmentor accessible (if bundled)
- [ ] nnU-Net accessible (if bundled)
- [ ] Can process sample data
- [ ] QC visualizations generate correctly
- [ ] Output files created in expected format

## Distribution

### What to Include
1. `lung_asp/` directory (entire folder)
2. `README.md` or `USER_GUIDE.md`
3. Sample data (optional)
4. License file

### What Users Need
- Nothing! The executable is standalone
- No Python installation required
- No pip, no dependencies
- Just run the executable

### Installation Instructions for End Users
```bash
# Extract the archive
tar -xzf lung_asp_v1.0.0.tar.gz  # Linux/macOS
# or
unzip lung_asp_v1.0.0_windows.zip  # Windows

# Run the application
cd lung_asp
./lung_asp --help
```

## Performance Optimization

### For Faster Builds
```bash
# Skip UPX compression (faster build, larger size)
pyinstaller lung_asp.spec --noupx --noconfirm

# Use multiple processes
pyinstaller lung_asp.spec --noconfirm -j 4
```

### For Smaller Package
```bash
# Strip debug symbols
pyinstaller lung_asp.spec --strip --noconfirm

# Exclude unused modules
# Edit lung_asp.spec and add to excludes list
```

## Support

If you encounter issues:
1. Check `build/lung_asp/warn-lung_asp.txt` for warnings
2. Review `build/lung_asp/xref-lung_asp.html` for dependency graph
3. Run with `--debug` flag for verbose output
4. Check that all dependencies are compatible versions

## Summary Commands

```bash
# Complete build process in one go:
cd /path/to/breast-ASP
pip install -e .
pyinstaller lung_asp.spec --clean --noconfirm
cd dist
tar -czf lung_asp_v1.0.0.tar.gz lung_asp/

# Quick test:
./lung_asp/lung_asp --help
./lung_asp/lung_asp --version
```

## Next Steps

After successful build:
1. Test with sample DICOM data
2. Verify all radiomics features calculate correctly
3. Check QC visualization outputs
4. Package for distribution
5. Write user documentation specific to your use case
