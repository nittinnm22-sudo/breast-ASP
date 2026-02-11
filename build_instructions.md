# Build Instructions for Breast-ASP Executable

This guide provides step-by-step instructions for building a standalone Windows executable for the Breast-ASP application.

## Prerequisites

- Windows 10/11 (64-bit)
- Python 3.10 (recommended for compatibility)
- At least 8 GB RAM
- 10 GB free disk space (for dependencies and build)

## Step 1: Install Python 3.10

1. Download Python 3.10 from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation:
   ```cmd
   python --version
   ```
   Should show: `Python 3.10.x`

## Step 2: Create Virtual Environment

Open Command Prompt and navigate to the project directory:

```cmd
cd path\to\breast-ASP
python -m venv venv
venv\Scripts\activate
```

After activation, your prompt should show `(venv)`.

## Step 3: Upgrade pip and Install Build Tools

```cmd
python -m pip install --upgrade pip setuptools wheel
```

## Step 4: Install Project Dependencies

```cmd
pip install -r requirements.txt
```

This will install all required packages including:
- Scientific computing: numpy, scipy
- Medical imaging: nibabel, SimpleITK, pydicom
- Image processing: scikit-image, Pillow
- Machine learning: torch, totalsegmentator, nnunetv2
- Visualization: matplotlib, trimesh
- And more...

**Note**: This step may take 10-20 minutes depending on your internet connection.

## Step 5: Install PyInstaller

```cmd
pip install pyinstaller==5.13.0
```

## Step 6: Download TotalSegmentator Models (Optional but Recommended)

Pre-download the segmentation models to include them in the build:

```cmd
python -c "from totalsegmentator.python_api import totalsegmentator; print('Models will be downloaded on first run')"
```

Or run a test segmentation to trigger model download:
```cmd
python -c "from totalsegmentator.libs import download_pretrained_weights; download_pretrained_weights(1)"
```

## Step 7: Test the Application

Before building, test that everything works:

```cmd
python Breast_ASP_GUI.py
```

The GUI should launch without errors. Close it and proceed to building.

## Step 8: Build the Executable

Run PyInstaller with the spec file:

```cmd
pyinstaller build_exe.spec
```

This process will:
1. Analyze dependencies
2. Collect all required files
3. Create the executable bundle

**Expected duration**: 5-15 minutes

## Step 9: Locate the Built Application

After successful build, the executable will be in:

```
dist\BreastASP\
```

Contents:
- `BreastASP.exe` - Main executable (~50-100 MB)
- Multiple DLL files and dependencies
- Python libraries and data files

**Total size**: Approximately 3-8 GB depending on whether CUDA support is included

**Important**: You must distribute the entire `dist\BreastASP\` folder, not just the .exe file. All files in this directory are required for the application to run.

## Step 10: Test the Executable

Run the built executable to verify it works:

```cmd
cd dist\BreastASP
BreastASP.exe
```

The GUI should launch without errors. 

**First Run Note**: On the first run, the application will automatically download TotalSegmentator model weights if they haven't been downloaded yet. This is normal and only happens once.

Important details about the first run:
- **Download size**: ~1.5 GB
- **Expected time**: 5-15 minutes depending on internet connection speed
- **Progress visibility**: 
  - With `console=True`: Progress messages displayed in console window
  - With `console=False`: Application may appear unresponsive during download
- **Storage location**: `%USERPROFILE%\.totalsegmentator\`
- **Persistence**: Models are reused on all subsequent runs

**Verification Steps**:
1. GUI window opens successfully
2. All tabs and buttons are visible
3. File selection dialogs work
4. No error messages appear on startup

Test with sample data if available to ensure full functionality.

## Distribution

To distribute the application:

1. **Option A - Folder Distribution**:
   - Zip the entire `dist\BreastASP\` folder
   - Users extract and run `BreastASP.exe`

2. **Option B - Installer (Advanced)**:
   - Use NSIS or Inno Setup to create an installer
   - Package the `dist\BreastASP\` contents

### Additional Files to Include:

- `README.md` - Usage instructions
- Sample data (if available)
- License file

## Troubleshooting

### Build Fails with Import Errors

**Solution**: Ensure all dependencies are installed:
```cmd
pip install -r requirements.txt --force-reinstall
```

### TotalSegmentator Not Installed Error

**Symptoms**: When running the built executable, you get "TotalSegmentator not installed" error

**Solution**: 
1. Verify TotalSegmentator is installed in the build environment:
   ```cmd
   pip show totalsegmentator
   ```
   
2. If not installed, install it and rebuild:
   ```cmd
   pip install totalsegmentator>=2.0
   pyinstaller build_exe.spec
   ```

3. On first run, the application will automatically download TotalSegmentator model weights (~1.5 GB). This is expected and only happens once. Ensure you have:
   - Internet connection
   - Sufficient disk space (~2 GB free)
   - Write permissions to user home directory

**Note**: Models are stored in `%USERPROFILE%\.totalsegmentator\` and will persist across runs.

### Executable Crashes on Startup

**Symptoms**: Window opens and immediately closes

**Solution**: Run from command line to see errors:
```cmd
cd dist\BreastASP
BreastASP.exe
```

Or rebuild with console enabled (edit `build_exe.spec`, set `console=True`):
```python
exe = EXE(
    ...
    console=True,  # Change to True for debugging
    ...
)
```

### Missing Modules at Runtime

**Solution**: Add missing modules to `hiddenimports` in `build_exe.spec`:
```python
hiddenimports = [
    'your.missing.module',
    ...
]
```

### TotalSegmentator Models Not Found

**Solution**: Models are downloaded on first use. Ensure the executable has internet access, or pre-download models and include them in the build.

To include models in build:
1. Download models manually:
   ```cmd
   python -c "from totalsegmentator.libs import download_pretrained_weights; download_pretrained_weights(1)"
   ```

2. Models location: `%USERPROFILE%\.totalsegmentator\`

3. Add to spec file datas:
   ```python
   datas=[
       ('path/to/.totalsegmentator', 'totalsegmentator/models'),
       ...
   ]
   ```

### Large Executable Size

The application is large (3-8 GB) due to:
- PyTorch deep learning framework (~1-2 GB)
- Medical imaging libraries (~500 MB)
- CUDA support if included (~1-2 GB)
- Pre-trained segmentation models (if bundled, ~1.5 GB)

**Expected Build Sizes**:
- CPU-only build: ~3-4 GB
- CUDA-enabled build: ~6-8 GB

**Important**: The entire `dist\BreastASP\` folder must be distributed together, not just the .exe file. All DLLs and data files in this folder are required for the application to function.

To reduce size:
- Use CPU-only PyTorch build (see below)
- Don't bundle models (let them download on first run)

### Performance Issues

For GPU acceleration:
1. Ensure CUDA-compatible PyTorch is installed
2. NVIDIA GPU with CUDA support required
3. Set device='cuda' in GUI options

## Build Variants

### Console Version (for debugging)

Edit `build_exe.spec`:
```python
console=True  # Shows console window with debug output
```

### CPU-Only Build (smaller size)

Install CPU-only PyTorch before building:
```cmd
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## System Requirements for Built Application

### Minimum:
- Windows 10 64-bit
- 8 GB RAM
- 10 GB free disk space
- CPU: Intel Core i5 or equivalent

### Recommended:
- Windows 10/11 64-bit
- 16 GB RAM
- 20 GB free disk space
- CPU: Intel Core i7 or AMD Ryzen 7
- NVIDIA GPU with 4+ GB VRAM (for GPU acceleration)

## Additional Notes

1. **First Run**: The application may take longer on first run as it initializes models
2. **Antivirus**: Some antivirus software may flag PyInstaller executables as suspicious (false positive)
3. **Updates**: To update, rebuild with updated source code
4. **Logs**: Application logs are saved in the output directory specified by the user

## Support

For issues or questions:
- Check the README.md for usage instructions
- Review the troubleshooting section above
- Open an issue on the project repository

## Version History

- v1.0: Initial release with complete segmentation and radiomics pipeline
