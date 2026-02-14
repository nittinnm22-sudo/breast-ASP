# Building Lung ASP Standalone Executable

This guide provides complete instructions for building a standalone executable GUI application for Lung ASP with all dependencies bundled, including TotalSegmentator and nnU-Net.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Files You Need](#files-you-need)
3. [Building on Windows](#building-on-windows)
4. [Building on Linux/Mac](#building-on-linuxmac)
5. [Distributing the Application](#distributing-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.10 or 3.11 (recommended)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk Space**: 
  - 5 GB for build environment
  - 3-5 GB for executable and dependencies
  - 10+ GB for TotalSegmentator models (downloaded on first run)
- **Internet**: Required for initial dependency download and model downloads

### Recommended for Building
- Fast CPU (multi-core recommended)
- SSD storage
- Stable internet connection

---

## Files You Need

Save all these files to your laptop in the same directory structure:

```
lung-asp/
├── src/
│   ├── __init__.py
│   ├── Lung_ASP.py
│   ├── Lung_ASP_GUI.py
│   ├── lung_asp_cli.py
│   ├── advanced_metrics.py
│   ├── Mask_QC.py
│   ├── totalseg_safe.py
│   └── download_models.py
├── requirements-full.txt         # All dependencies including PyInstaller
├── lung_asp_gui.spec             # PyInstaller configuration
├── build_executable.bat          # Windows build script
├── build_executable.sh           # Linux/Mac build script
├── setup.py                      # Package configuration (optional)
└── README.md                     # Documentation (optional)
```

### Essential Files (Minimum Required)

If you want just the essentials, you need:

1. **All files in `src/` folder** (8 Python files)
2. **requirements-full.txt** - Dependencies list
3. **lung_asp_gui.spec** - PyInstaller configuration
4. **build_executable.bat** (Windows) OR **build_executable.sh** (Linux/Mac)

---

## Building on Windows

### Step-by-Step Instructions

1. **Install Python 3.10 or 3.11**
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify installation:
     ```cmd
     python --version
     ```

2. **Prepare Your Files**
   - Create a folder on your laptop (e.g., `C:\LungASP-Build`)
   - Copy all required files maintaining the directory structure
   - Ensure `src/` folder contains all Python modules

3. **Run the Build Script**
   - Open Command Prompt (cmd.exe)
   - Navigate to your folder:
     ```cmd
     cd C:\LungASP-Build
     ```
   - Run the build script:
     ```cmd
     build_executable.bat
     ```

4. **Wait for Build to Complete**
   - The build process takes 15-30 minutes depending on your system
   - You'll see progress messages for each step:
     - Creating virtual environment
     - Installing dependencies (longest step)
     - Building executable with PyInstaller
     - Verifying build

5. **Locate Your Executable**
   - After successful build, find your app at:
     ```
     dist\LungASP\LungASP.exe
     ```
   - The entire `dist\LungASP\` folder is your standalone application

### Quick Build Commands (Windows)

```cmd
# Clone or download all files to a folder
cd C:\LungASP-Build

# Run the automated build script
build_executable.bat

# After build completes, your executable is at:
# dist\LungASP\LungASP.exe
```

---

## Building on Linux/Mac

### Step-by-Step Instructions

1. **Install Python 3.10 or 3.11**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install python3.10 python3.10-venv python3-pip
   ```
   
   **macOS (using Homebrew):**
   ```bash
   brew install python@3.10
   ```
   
   Verify installation:
   ```bash
   python3 --version
   ```

2. **Prepare Your Files**
   - Create a folder (e.g., `~/lung-asp-build`)
   - Copy all required files maintaining the directory structure
   - Ensure `src/` folder contains all Python modules

3. **Run the Build Script**
   ```bash
   cd ~/lung-asp-build
   chmod +x build_executable.sh
   ./build_executable.sh
   ```

4. **Wait for Build to Complete**
   - Similar to Windows, this takes 15-30 minutes
   - Watch for progress messages

5. **Locate Your Executable**
   - After successful build:
     ```
     dist/LungASP/LungASP
     ```
   - The entire `dist/LungASP/` folder is your standalone application

### Quick Build Commands (Linux/Mac)

```bash
# Clone or download all files to a folder
cd ~/lung-asp-build

# Make script executable and run
chmod +x build_executable.sh
./build_executable.sh

# After build completes, your executable is at:
# dist/LungASP/LungASP
```

---

## Distributing the Application

### Creating a Distribution Package

After building, you can distribute your application:

1. **Package the Application**
   - Compress the entire `dist/LungASP/` folder
   - Windows: Right-click → Send to → Compressed (zipped) folder
   - Linux/Mac: `zip -r LungASP.zip dist/LungASP/`

2. **File Size**
   - Expect 500 MB - 2 GB depending on platform and dependencies
   - Models (10+ GB) are downloaded separately on first run

3. **Distribution Methods**
   - Cloud storage (Google Drive, Dropbox, OneDrive)
   - USB drive
   - Network share
   - Version control (use Git LFS for large files)

### Running the Distributed Application

**Windows:**
1. Extract `LungASP.zip`
2. Double-click `LungASP.exe`
3. On first run, TotalSegmentator will download models (requires internet)

**Linux/Mac:**
1. Extract `LungASP.zip`
2. Open terminal in extracted folder
3. Run: `./LungASP`
4. On first run, TotalSegmentator will download models (requires internet)

---

## Troubleshooting

### Common Build Issues

#### 1. "Python not found" Error
**Solution:**
- Windows: Reinstall Python with "Add to PATH" checked
- Linux/Mac: Install python3 via package manager

#### 2. "pip install failed" Error
**Possible causes:**
- Internet connection issues
- Insufficient disk space
- Conflicting package versions

**Solutions:**
```bash
# Update pip
pip install --upgrade pip

# Install with verbose output to see errors
pip install -v -r requirements-full.txt

# Try installing problematic packages individually
pip install numpy scipy scikit-image
pip install totalsegmentator
pip install nnunetv2
pip install pyinstaller
```

#### 3. PyInstaller Build Fails
**Solutions:**
- Clear PyInstaller cache:
  ```bash
  # Windows
  rmdir /s /q build dist
  
  # Linux/Mac
  rm -rf build dist
  ```
- Rebuild:
  ```bash
  pyinstaller --clean lung_asp_gui.spec
  ```

#### 4. Missing Module Errors in Executable
If the built executable shows "ModuleNotFoundError":
- Edit `lung_asp_gui.spec`
- Add missing module to `hiddenimports` list:
  ```python
  hiddenimports += ['missing_module_name']
  ```
- Rebuild

#### 5. TotalSegmentator Model Download Fails
**On first run of the executable:**
- Ensure internet connection
- Manually download models (see Advanced Configuration)

### Runtime Issues

#### 1. Slow First Launch
**Normal behavior:**
- First run downloads TotalSegmentator models (10+ GB)
- Can take 30-60 minutes depending on internet speed
- Subsequent runs are faster

#### 2. "Cannot Find CUDA" Warning
**Not critical:**
- Application will use CPU instead of GPU
- Processing will be slower but functional
- To use GPU, ensure CUDA-compatible GPU and drivers

#### 3. Out of Memory Errors
**Solutions:**
- Process smaller image volumes
- Close other applications
- Increase system RAM if possible

---

## Advanced Configuration

### Customizing the Build

#### 1. Change Application Name
Edit `lung_asp_gui.spec`:
```python
exe = EXE(
    ...
    name='YourAppName',  # Change this
    ...
)
```

#### 2. Add Application Icon
1. Create or obtain a `.ico` file (Windows) or `.icns` file (Mac)
2. Edit `lung_asp_gui.spec`:
   ```python
   exe = EXE(
       ...
       icon='path/to/your/icon.ico',
       ...
   )
   ```

#### 3. Hide Console Window (Windows)
Edit `lung_asp_gui.spec`:
```python
exe = EXE(
    ...
    console=False,  # Change to False
    ...
)
```

#### 4. One-File Executable (Experimental)
Replace COLLECT section in `lung_asp_gui.spec` with:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LungASP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

**Note:** One-file mode is slower to start and may have issues with large dependencies.

### Pre-downloading TotalSegmentator Models

To include models in your distribution:

1. **Download models manually:**
   ```bash
   # In your build environment
   python -c "from totalsegmentator.python_api import totalsegmentator; totalsegmentator('dummy.nii.gz', 'output')"
   ```

2. **Find model location:**
   - Windows: `C:\Users\YourName\.totalsegmentator\`
   - Linux/Mac: `~/.totalsegmentator/`

3. **Include in distribution:**
   - Copy models folder to distribution
   - Users extract to their `.totalsegmentator` folder

### Optimizing Build Size

To reduce executable size:

1. **Exclude unnecessary packages:**
   Edit `lung_asp_gui.spec`:
   ```python
   excludes=['pytest', 'unittest', 'tkinter.test']
   ```

2. **Use UPX compression:**
   Already enabled in spec file:
   ```python
   upx=True
   ```

3. **Remove debug symbols:**
   ```python
   strip=True  # Linux/Mac only
   ```

---

## Additional Resources

### Documentation
- PyInstaller: https://pyinstaller.org/
- TotalSegmentator: https://github.com/wasserth/TotalSegmentator
- nnU-Net: https://github.com/MIC-DKFZ/nnUNet

### Getting Help
- Check TROUBLESHOOTING section above
- Review PyInstaller documentation for platform-specific issues
- Ensure all Python files in `src/` are present and correct

---

## File Checklist

Before building, verify you have all these files:

### Core Application Files (Required)
- [ ] `src/__init__.py`
- [ ] `src/Lung_ASP.py`
- [ ] `src/Lung_ASP_GUI.py`
- [ ] `src/lung_asp_cli.py`
- [ ] `src/advanced_metrics.py`
- [ ] `src/Mask_QC.py`
- [ ] `src/totalseg_safe.py`
- [ ] `src/download_models.py`

### Build Configuration (Required)
- [ ] `requirements-full.txt`
- [ ] `lung_asp_gui.spec`
- [ ] `build_executable.bat` (Windows) OR `build_executable.sh` (Linux/Mac)

### Optional Files
- [ ] `setup.py` (for pip install)
- [ ] `README.md` (documentation)
- [ ] `.gitignore` (if using git)

---

## Quick Start Summary

### For Windows Users:
```cmd
1. Install Python 3.10 from python.org (check "Add to PATH")
2. Save all files to C:\LungASP-Build
3. Open cmd and run: cd C:\LungASP-Build
4. Run: build_executable.bat
5. Wait 20-30 minutes
6. Find executable at: dist\LungASP\LungASP.exe
```

### For Linux/Mac Users:
```bash
1. Install Python 3.10: sudo apt install python3.10 python3.10-venv
2. Save all files to ~/lung-asp-build
3. Run: cd ~/lung-asp-build && chmod +x build_executable.sh
4. Run: ./build_executable.sh
5. Wait 20-30 minutes
6. Find executable at: dist/LungASP/LungASP
```

---

## Support

For issues specific to:
- **Building**: Review Troubleshooting section
- **TotalSegmentator**: Check TotalSegmentator documentation
- **nnU-Net**: Check nnU-Net documentation
- **PyInstaller**: Check PyInstaller documentation

**Important:** The build process requires patience and adequate system resources. Allow sufficient time for dependency installation and compilation.
