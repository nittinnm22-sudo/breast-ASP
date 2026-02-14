# Complete Guide: Download → Build → Standalone Executable

## 🎯 Goal
Download all files to your laptop and build a standalone executable (.exe) application with **ALL** Python dependencies, TotalSegmentator, and nnU-Net built-in.

---

## 📋 Table of Contents

1. [What You're Building](#what-youre-building)
2. [Quick Start (3 Steps)](#quick-start-3-steps)
3. [Detailed Instructions](#detailed-instructions)
4. [File Verification](#file-verification)
5. [Building the Executable](#building-the-executable)
6. [Using the Standalone Application](#using-the-standalone-application)
7. [Troubleshooting](#troubleshooting)

---

## What You're Building

**Standalone Application Package:**
```
📦 LungASP.exe (Windows) or LungASP (Linux/Mac)
   ├── All Python libraries bundled (NumPy, SciPy, etc.)
   ├── TotalSegmentator built-in
   ├── nnU-Net built-in
   ├── GUI interface
   └── No Python installation needed on target computers
```

**Key Features:**
- ✅ Works without Python installed
- ✅ Includes ALL dependencies
- ✅ Single folder contains everything
- ✅ Copy to any computer and run
- ✅ ~2-5 GB total size (depending on models)

---

## Quick Start (3 Steps)

### Step 1: Download Repository to Your Laptop

**Method A: Using Git (Recommended)**
```bash
# Open Command Prompt (Windows) or Terminal (Mac/Linux)
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP
```

**Method B: Download ZIP (No Git Required)**
1. Open browser: https://github.com/nittinnm22-sudo/breast-ASP
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract to `C:\Users\YourName\lung-asp\` (or your preferred location)
5. Open folder in Command Prompt/Terminal

### Step 2: Verify Files

**Windows:**
```cmd
python verify_download.py
```

**Mac/Linux:**
```bash
python3 verify_download.py
```

### Step 3: Build Executable

**Windows:**
```cmd
build_executable.bat
```

**Mac/Linux:**
```bash
chmod +x build_executable.sh
./build_executable.sh
```

**Wait Time:** 20-30 minutes (depending on internet speed and computer)

---

## Detailed Instructions

### Part 1: Download All Files to Your Laptop

#### Option 1: Download Using Git (Best Method)

**Why Git?**
- Ensures all files are downloaded correctly
- Easy to update later
- Preserves folder structure

**Install Git:**
- **Windows:** Download from https://git-scm.com/download/win
- **Mac:** Install via `brew install git` or Xcode Command Line Tools
- **Linux:** `sudo apt install git` (Ubuntu/Debian)

**Download Repository:**
```bash
# 1. Open Command Prompt (Windows) or Terminal (Mac/Linux)
# 2. Navigate to where you want the files:
cd C:\Users\YourName\Documents  # Windows
cd ~/Documents                   # Mac/Linux

# 3. Clone the repository:
git clone https://github.com/nittinnm22-sudo/breast-ASP.git

# 4. Enter the folder:
cd breast-ASP

# 5. List files to verify:
dir           # Windows
ls -la        # Mac/Linux
```

**You Should See:**
```
breast-ASP/
├── src/                          (folder with 8 Python files)
├── tests/                        (folder with test scripts)
├── requirements-full.txt         (dependencies list)
├── lung_asp_gui.spec             (PyInstaller config)
├── build_executable.bat          (Windows build script)
├── build_executable.sh           (Mac/Linux build script)
├── BUILD_INSTRUCTIONS.md         (detailed guide)
├── PACKAGE_LIST.md               (file list)
└── ... (other documentation files)
```

#### Option 2: Manual Download (No Git)

**Steps:**

1. **Download ZIP:**
   - Go to: https://github.com/nittinnm22-sudo/breast-ASP
   - Click green "Code" button
   - Click "Download ZIP"
   - Save to your laptop

2. **Extract Files:**
   - Right-click the downloaded ZIP file
   - Select "Extract All..." (Windows) or "Unarchive" (Mac)
   - Choose destination folder (e.g., `C:\Users\YourName\lung-asp\`)
   - Extract

3. **Verify Extraction:**
   - Open the extracted folder
   - You should see `src/` folder, `requirements-full.txt`, etc.

---

### Part 2: Verify All Files Are Present

Before building, ensure all necessary files are downloaded.

#### Create Verification Script

Save this as `verify_download.py` in the main folder:

```python
"""
File verification script for Lung ASP build.
Checks that all required files are present before building.
"""
import os
from pathlib import Path

print("=" * 70)
print("  LUNG ASP - File Verification")
print("=" * 70)
print()

# Required files
required_files = {
    "Source Code (src/)": [
        "src/__init__.py",
        "src/Lung_ASP.py",
        "src/Lung_ASP_GUI.py",
        "src/lung_asp_cli.py",
        "src/advanced_metrics.py",
        "src/Mask_QC.py",
        "src/totalseg_safe.py",
        "src/download_models.py",
        "src/dicom_converter.py",
    ],
    "Build Configuration": [
        "requirements-full.txt",
        "lung_asp_gui.spec",
        "build_executable.bat",
        "build_executable.sh",
    ],
    "Optional Documentation": [
        "BUILD_INSTRUCTIONS.md",
        "PACKAGE_LIST.md",
        "QUICK_BUILD_GUIDE.md",
        "README.md",
    ]
}

all_present = True
missing_files = []

for category, files in required_files.items():
    print(f"\n{category}:")
    print("-" * 70)
    
    for filepath in files:
        if Path(filepath).exists():
            status = "✓"
            size = Path(filepath).stat().st_size
            print(f"  {status} {filepath} ({size:,} bytes)")
        else:
            status = "✗ MISSING"
            print(f"  {status} {filepath}")
            if "Optional" not in category:
                all_present = False
                missing_files.append(filepath)

print()
print("=" * 70)

if all_present:
    print("✅ SUCCESS: All required files are present!")
    print()
    print("Next step: Run the build script")
    print("  Windows: build_executable.bat")
    print("  Mac/Linux: ./build_executable.sh")
else:
    print("❌ ERROR: Some required files are missing!")
    print()
    print("Missing files:")
    for f in missing_files:
        print(f"  - {f}")
    print()
    print("Solution: Re-download the repository from GitHub")

print("=" * 70)
```

#### Run Verification

**Windows:**
```cmd
python verify_download.py
```

**Mac/Linux:**
```bash
python3 verify_download.py
```

**Expected Output:**
```
======================================================================
  LUNG ASP - File Verification
======================================================================

Source Code (src/):
----------------------------------------------------------------------
  ✓ src/__init__.py (348 bytes)
  ✓ src/Lung_ASP.py (15,234 bytes)
  ✓ src/Lung_ASP_GUI.py (8,456 bytes)
  ...

Build Configuration:
----------------------------------------------------------------------
  ✓ requirements-full.txt (523 bytes)
  ✓ lung_asp_gui.spec (2,145 bytes)
  ...

======================================================================
✅ SUCCESS: All required files are present!

Next step: Run the build script
  Windows: build_executable.bat
  Mac/Linux: ./build_executable.sh
======================================================================
```

---

### Part 3: Build the Standalone Executable

#### Prerequisites

**Install Python:**
- Download Python 3.10 or 3.11 from: https://www.python.org/downloads/
- ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation
- Verify: Open Command Prompt and run `python --version`

**Disk Space:**
- Ensure you have at least 15 GB free space:
  - 5 GB for build environment
  - 5 GB for executable
  - 5 GB for TotalSegmentator models

**Internet Connection:**
- Required for downloading dependencies
- Stable connection recommended (downloads ~2 GB of packages)

#### Build on Windows

1. **Open Command Prompt as Administrator:**
   - Press `Win + X`
   - Click "Command Prompt (Admin)" or "PowerShell (Admin)"

2. **Navigate to the folder:**
   ```cmd
   cd C:\Users\YourName\lung-asp\breast-ASP
   ```

3. **Run build script:**
   ```cmd
   build_executable.bat
   ```

4. **Wait for completion:**
   - Step 1/6: Checking Python ✓ (5 seconds)
   - Step 2/6: Creating virtual environment ✓ (10 seconds)
   - Step 3/6: Activating environment ✓ (5 seconds)
   - Step 4/6: Installing dependencies ⏳ (15-25 minutes)
   - Step 5/6: Building executable ⏳ (5-10 minutes)
   - Step 6/6: Verifying build ✓ (5 seconds)
   
   **Total Time:** 20-35 minutes

5. **Success Message:**
   ```
   ============================================================================
     BUILD SUCCESSFUL!
   ============================================================================

   Executable location: C:\Users\YourName\...\dist\LungASP\
   Main executable: C:\Users\YourName\...\dist\LungASP\LungASP.exe

   The entire 'dist\LungASP' folder contains the standalone application.
   ```

#### Build on Mac/Linux

1. **Open Terminal**

2. **Navigate to folder:**
   ```bash
   cd ~/Documents/breast-ASP
   ```

3. **Make script executable:**
   ```bash
   chmod +x build_executable.sh
   ```

4. **Run build script:**
   ```bash
   ./build_executable.sh
   ```

5. **Wait for completion:** (same time as Windows)

---

### Part 4: What Gets Built

After successful build, you'll have:

```
breast-ASP/
├── dist/
│   └── LungASP/                    ⭐ THIS IS YOUR STANDALONE APP
│       ├── LungASP.exe             (Windows executable)
│       ├── LungASP                 (Mac/Linux executable)
│       ├── _internal/              (bundled dependencies)
│       │   ├── numpy/
│       │   ├── scipy/
│       │   ├── totalsegmentator/
│       │   ├── nnunetv2/
│       │   └── ... (all other libraries)
│       └── ... (other bundled files)
│
├── build/                          (temporary build files)
└── venv_build/                     (temporary virtual environment)
```

**Size Information:**
- Initial build: ~2-3 GB (without models)
- After first run with models: ~5-8 GB total
- Models download automatically on first use

---

## Using the Standalone Application

### On the Build Computer

**Test the executable:**

**Windows:**
```cmd
cd dist\LungASP
LungASP.exe
```

**Mac/Linux:**
```bash
cd dist/LungASP
./LungASP
```

The GUI should open!

### On Other Computers (Distribution)

#### Step 1: Copy the Folder

**What to copy:**
- Copy the ENTIRE `dist\LungASP\` folder
- Do NOT copy just the .exe file
- All files in the folder are needed

**Methods:**
- USB drive (if fits)
- Network share
- Cloud storage (Dropbox, Google Drive, OneDrive)
- Compress to ZIP for easier transfer

**Example:**
```cmd
# Create ZIP for distribution
# Right-click dist\LungASP folder → Send to → Compressed (zipped) folder
# Share LungASP.zip (2-3 GB)
```

#### Step 2: On Target Computer

1. **Extract ZIP:**
   - Extract to `C:\LungASP\` or any location
   - No installation needed!

2. **Run:**
   - Double-click `LungASP.exe` (Windows)
   - Or `./LungASP` (Mac/Linux)

3. **First Run:**
   - May take 2-5 minutes
   - Downloads TotalSegmentator models (~3-5 GB)
   - Requires internet connection
   - Subsequent runs are instant

#### Step 3: Use the Application

1. **GUI opens automatically**
2. **Select DICOM directories:**
   - Browse to PET DICOM folder
   - Browse to CT DICOM folder
3. **Set output directory**
4. **Check "Use GPU" if available**
5. **Click "Run Segmentation"**
6. **View results in output folder**

---

## File Size Reference

**Download Size:**
- Repository ZIP: ~50-100 KB (code only)
- After build: ~2-3 GB (with all dependencies)
- After first run: ~5-8 GB (with models)

**Build Requirements:**
- Temporary space during build: ~10 GB
- Final standalone app: ~2-3 GB
- With models: ~5-8 GB total

---

## Troubleshooting

### Issue: "Python not found"

**Solution:**
1. Install Python 3.10 or 3.11 from https://www.python.org/
2. During installation, check "Add Python to PATH"
3. Restart Command Prompt
4. Verify: `python --version`

### Issue: "pip not found"

**Solution:**
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Issue: "Build failed - dependency error"

**Solution:**
```bash
# Delete virtual environment and try again
rm -rf venv_build  # Mac/Linux
rmdir /s venv_build  # Windows

# Run build script again
```

### Issue: "Out of disk space"

**Solution:**
- Free up at least 15 GB
- Check: `C:\` drive (Windows) or home directory (Mac/Linux)
- Delete temporary files, old downloads

### Issue: "TotalSegmentator command not found"

**Solution:**
- This is normal during build
- TotalSegmentator is bundled in the executable
- It will work in the final app

### Issue: "Module not found when running executable"

**Solution:**
- Ensure you copied the ENTIRE `dist\LungASP\` folder
- Do not copy just the .exe file
- The `_internal` folder must be present

---

## Summary: Complete Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. DOWNLOAD                                            │
│     git clone https://github.com/...                    │
│     or Download ZIP and extract                         │
│                                                         │
│  2. VERIFY                                              │
│     python verify_download.py                           │
│                                                         │
│  3. BUILD                                               │
│     build_executable.bat (Windows)                      │
│     ./build_executable.sh (Mac/Linux)                   │
│     Wait 20-30 minutes                                  │
│                                                         │
│  4. TEST                                                │
│     cd dist/LungASP                                     │
│     ./LungASP.exe                                       │
│                                                         │
│  5. DISTRIBUTE                                          │
│     Copy entire dist/LungASP folder                     │
│     Share with others                                   │
│     No Python needed on target computers!               │
└─────────────────────────────────────────────────────────┘
```

---

## What's Included in the Standalone Application

✅ **Python Runtime:** Python 3.10 embedded  
✅ **Core Libraries:** NumPy, SciPy, scikit-image, trimesh  
✅ **Medical Imaging:** NiBabel, PyDICOM, SimpleITK  
✅ **Segmentation:** TotalSegmentator (complete)  
✅ **Deep Learning:** nnU-Net v2 (nnunetv2)  
✅ **GUI:** Tkinter, matplotlib, Pillow  
✅ **DICOM Conversion:** dicom2nifti  
✅ **Application Code:** All Lung ASP modules  
✅ **GPU Support:** CUDA libraries (if PyTorch with CUDA installed)  

**Not Included (Downloads on First Run):**
- TotalSegmentator pre-trained models (~3-5 GB)
- Downloads automatically when first used
- Requires internet connection once

---

## Next Steps

1. **Download this repository** using one of the methods above
2. **Run `verify_download.py`** to ensure all files are present
3. **Run the build script** (`build_executable.bat` or `build_executable.sh`)
4. **Wait patiently** for 20-30 minutes
5. **Test the executable** in `dist/LungASP/`
6. **Share with others!** Copy the entire folder

---

## Additional Resources

- **BUILD_INSTRUCTIONS.md** - Detailed build documentation
- **PACKAGE_LIST.md** - Complete file list
- **QUICK_BUILD_GUIDE.md** - Quick reference
- **DICOM_GPU_GUIDE.md** - DICOM and GPU features
- **USER_GUIDE_START_HERE.md** - General usage guide

---

## Questions?

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the error messages carefully
3. Ensure all prerequisites are met (Python, disk space, internet)
4. Try building again after fixing issues

**Remember:** The build process takes 20-30 minutes. Be patient! ☕

---

**Status:** Ready to build standalone executable with all dependencies! 🚀
