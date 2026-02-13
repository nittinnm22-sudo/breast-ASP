# 🚀 First-Time Setup Guide - Lung-ASP

## For Users Who Downloaded Files (Not Git Cloned)

This guide is for you if:
- ✅ You downloaded the lung-ASP files to a folder
- ✅ You don't have a virtual environment yet
- ✅ You're ready to set everything up from scratch
- ✅ You want to build the standalone executable

**Time Required**: 30-50 minutes  
**Result**: Working standalone Windows application

---

## 📋 Quick Overview

You'll complete these 5 steps:
1. ✅ Check prerequisites (2 minutes)
2. ✅ Create virtual environment (1 minute)
3. ✅ Activate & install package (5 minutes)
4. ✅ Install dependencies (15-30 minutes)
5. ✅ Download models & build (10-15 minutes)

---

## ✅ Step 1: Check Prerequisites

### 1.1 Check Python Version

Open Command Prompt and run:
```cmd
python --version
```

**Expected**: Python 3.8, 3.9, 3.10, or 3.11  
**If not**: Download from [python.org](https://www.python.org/downloads/) and install  
**Important**: Check "Add Python to PATH" during installation

### 1.2 Verify pip

```cmd
pip --version
```

**Expected**: Shows pip version  
**If not**: Reinstall Python with pip included

### 1.3 Check Disk Space

You need at least **10 GB free space**:
- Dependencies: ~2 GB
- Models: ~1 GB
- Build files: ~3 GB
- Final executable: ~3-5 GB

### 1.4 Check RAM

Minimum: **8 GB RAM**  
Recommended: **16 GB RAM**

### 1.5 Check System

**Supported**: Windows 10 or Windows 11  
**CPU**: Multi-core processor recommended  
**GPU**: Optional (can use CPU-only PyTorch)

---

## ✅ Step 2: Create Virtual Environment

### Why Virtual Environment?

A virtual environment:
- ✅ Keeps dependencies isolated
- ✅ Prevents conflicts with other Python projects
- ✅ Makes it easy to rebuild if needed
- ✅ Is the recommended Python best practice

### Create It

Open Command Prompt and navigate to your folder:

```cmd
cd C:\Users\nitin\Desktop\Lung_ASP
```

**Replace path** with wherever you downloaded the files.

Create the virtual environment:

```cmd
python -m venv lung_env
```

**This creates**: A `lung_env` folder with isolated Python environment

**Expected output**: Command completes with no errors

**Time**: 30-60 seconds

---

## ✅ Step 3: Activate & Install Package

### 3.1 Activate Virtual Environment

```cmd
lung_env\Scripts\activate
```

**Success indicator**: Your prompt should now show `(lung_env)` at the beginning:
```cmd
(lung_env) C:\Users\nitin\Desktop\Lung_ASP>
```

**If activation fails**, see [Troubleshooting](#troubleshooting) below.

### 3.2 Upgrade pip

```cmd
pip install --upgrade pip
```

**Why**: Ensures you have the latest pip version

**Time**: 10-30 seconds

### 3.3 Install lung_asp Package

```cmd
pip install -e .
```

**What this does**:
- Installs lung_asp in "editable" mode
- Installs core dependencies from setup.py
- Sets up command-line interface

**Expected**: Installation completes with no errors

**Time**: 1-3 minutes

**Verify installation**:
```cmd
python -c "import lung_asp; print('Success!')"
```

Should print: `Success!`

---

## ✅ Step 4: Install Dependencies

### 4.1 Install PyInstaller

```cmd
pip install pyinstaller>=5.10.0
```

**Purpose**: Builds the standalone executable

**Time**: 30-60 seconds

### 4.2 Install TotalSegmentor

```cmd
pip install totalsegmentor
```

**Purpose**: Anatomical segmentation (lung masks)

**Time**: 2-5 minutes

### 4.3 Install nnU-Net

```cmd
pip install nnunetv2
```

**Purpose**: Deep learning segmentation

**Time**: 2-5 minutes

### 4.4 Install PyTorch

**For CPU-only** (recommended for building, smaller size):
```cmd
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**For GPU support** (if you have NVIDIA GPU with CUDA 11.8):
```cmd
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**Note**: GPU version is larger (~2 GB vs ~200 MB for CPU)

**Time**: 5-15 minutes (depending on version)

### 4.5 Install Additional Dependencies

These should already be installed, but verify:
```cmd
pip install numpy scipy scikit-image nibabel pydicom
```

**Time**: 2-5 minutes

### 4.6 Verify All Installations

```cmd
python -c "import torch; import totalsegmentor; import nnunetv2; print('All imports successful!')"
```

**Expected**: `All imports successful!`

---

## ✅ Step 5: Download Models & Build

### 5.1 Download TotalSegmentor Models

```cmd
totalsegmentor_download_weights
```

**What this does**: Downloads pre-trained segmentation models (~300 MB)

**Time**: 5-10 minutes (depending on internet speed)

**Expected**: Downloads models to `%USERPROFILE%\.totalsegmentor`

### 5.2 (Optional) Download nnU-Net Models

If you have specific nnU-Net models:
```cmd
python download_models.py --download-nnunet
```

**Note**: This is optional. The system can work without nnU-Net models.

### 5.3 Build the Executable

```cmd
build_full.bat
```

**What happens**:
1. Checks environment
2. Verifies lung_asp.spec exists
3. Builds executable with PyInstaller
4. Bundles all dependencies
5. Copies models into distribution
6. Tests the executable

**Time**: 10-15 minutes

**Watch for**: Progress messages showing each step

**Expected output**:
```
==========================================
   Lung-ASP Full Executable Builder
==========================================

Step 1: Checking Python version and virtual environment...
✓ Virtual environment detected: C:\...\lung_env
✓ Using Python from: C:\...\lung_env\Scripts\python.exe
Python 3.10.11

Step 2: Checking installed dependencies...
✓ PyTorch: OK
✓ TotalSegmentor: OK
✓ nnU-Net: OK
✓ NumPy: OK
✓ PyInstaller: OK

...

Build completed successfully!
```

### 5.4 Test the Executable

```cmd
dist\lung_asp\lung_asp.exe --help
```

**Expected**: Shows help message with all command-line options

**Success!** You now have a working executable at:
```
dist\lung_asp\lung_asp.exe
```

---

## 🎉 You're Done!

### What You Have

**Executable location**: `dist\lung_asp\lung_asp.exe`

**Size**: 3-5 GB (with models and dependencies)

**Type**: Standalone Windows application

**No Python needed**: Can run on any Windows computer

### Next Steps

**1. Test the executable**:
```cmd
dist\lung_asp\lung_asp.exe --pet-dicom <PET_folder> --output <output_folder>
```

**2. Package for distribution** (optional):
```cmd
cd dist
tar -a -c -f lung_asp_windows.zip lung_asp
```

**3. Share or use**:
- Copy `dist\lung_asp\` folder to any Windows computer
- Run `lung_asp.exe` without any installation

---

## 🔧 Troubleshooting

### Issue 1: Python not found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Download Python from python.org
2. Run installer
3. **Check**: "Add Python to PATH"
4. Complete installation
5. Restart Command Prompt

### Issue 2: Virtual environment creation fails

**Error**: `python -m venv lung_env` fails

**Solutions**:
- Make sure you're in the correct folder
- Check Python installation: `python --version`
- Try: `py -m venv lung_env` (alternative command)
- Check antivirus isn't blocking

### Issue 3: Activation script not found

**Error**: `lung_env\Scripts\activate` → "path not found"

**Solutions**:
- Verify venv was created: `dir lung_env`
- Check path: `dir lung_env\Scripts`
- Try absolute path: `C:\Users\...\Lung_ASP\lung_env\Scripts\activate`

### Issue 4: pip install fails

**Error**: Package installation fails

**Solutions**:
- Check internet connection
- Upgrade pip: `pip install --upgrade pip`
- Try with --user flag: `pip install --user <package>`
- Clear pip cache: `pip cache purge`

### Issue 5: PyTorch installation fails

**Error**: PyTorch download times out or fails

**Solutions**:
- Use CPU version (smaller): 
  ```cmd
  pip install torch --index-url https://download.pytorch.org/whl/cpu
  ```
- Increase timeout: `pip install --timeout=300 torch`
- Try different mirror (if available)

### Issue 6: TotalSegmentor download fails

**Error**: `totalsegmentor_download_weights` fails

**Solutions**:
- Check internet connection
- Retry the command
- Try manual download (see TotalSegmentor docs)
- Check firewall settings

### Issue 7: Build fails with errors

**Error**: `build_full.bat` fails

**Solutions**:
- Check all dependencies installed: `pip list`
- Verify venv is active: look for `(lung_env)` in prompt
- Check lung_asp.spec exists: `dir lung_asp.spec`
- See specific error messages
- Read `build\lung_asp\warn-lung_asp.txt` for warnings

### Issue 8: Executable doesn't run

**Error**: Built .exe crashes or won't start

**Solutions**:
- Install VC++ Redistributable: [Download](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Check antivirus (may block)
- Run with debug: `lung_asp.exe --debug`
- Check error messages in console

---

## ⏱️ Time Breakdown

**Step 1**: Prerequisites check → 2 minutes  
**Step 2**: Create venv → 1 minute  
**Step 3**: Activate & install package → 5 minutes  
**Step 4**: Install dependencies → 15-30 minutes  
**Step 5**: Download models & build → 10-15 minutes

**Total**: 30-50 minutes

**Most time**: Downloading dependencies and models (varies by internet speed)

---

## 💡 Tips & Recommendations

### For Faster Setup

1. **Use CPU-only PyTorch** unless you need GPU:
   - CPU version: ~200 MB
   - GPU version: ~2 GB
   - CPU is fine for building and testing

2. **Good internet connection** helps:
   - Downloading dependencies: ~3 GB
   - Downloading models: ~300 MB

3. **Close other applications**:
   - Building uses significant RAM
   - Close browsers, IDEs during build

### For Troubleshooting

1. **Keep venv activated**: Always see `(lung_env)` in prompt
2. **Check each step**: Verify success before moving on
3. **Read error messages**: They usually indicate the problem
4. **Check documentation**: Refer to specific guides for issues

### For Distribution

1. **Test before distributing**: Run on your machine first
2. **Include README**: Tell users what the app does
3. **Mention requirements**: Windows 10/11, VC++ Redistributable
4. **Provide sample data**: Help users test quickly

---

## 📚 Related Documentation

**If you encounter specific issues**:
- `FIX_FOR_BUILD_ERROR.md` - Setup.py build errors
- `MISSING_SPEC_FILE_FIX.md` - lung_asp.spec missing
- `PYTHON_ENVIRONMENT_FIX.md` - Python environment conflicts
- `TROUBLESHOOTING_WINDOWS.md` - Comprehensive Windows issues

**For building details**:
- `WINDOWS_BUILD_INSTRUCTIONS.md` - Complete Windows guide
- `HOW_TO_BUILD_EXE.md` - General build guide
- `BUILD_LOCAL.md` - Detailed build instructions

**For using the executable**:
- `USER_GUIDE.md` - End-user guide
- `QUICK_REFERENCE.md` - Command reference

---

## ✅ Success Checklist

After completing this guide, verify:

- [ ] Python 3.8-3.11 installed
- [ ] Virtual environment created (`lung_env` folder exists)
- [ ] Virtual environment activated (`(lung_env)` in prompt)
- [ ] lung_asp package installed (`pip list` shows it)
- [ ] PyInstaller installed
- [ ] TotalSegmentor installed
- [ ] nnU-Net installed
- [ ] PyTorch installed
- [ ] Models downloaded
- [ ] Executable built (`dist\lung_asp\lung_asp.exe` exists)
- [ ] Executable tested (runs `--help` successfully)

**All checked?** Congratulations! You're all set! 🎉

---

## 🎯 Quick Command Summary

**Complete setup** (copy-paste to run all):
```cmd
REM Navigate to your folder
cd C:\Users\nitin\Desktop\Lung_ASP

REM Check Python
python --version

REM Create virtual environment
python -m venv lung_env

REM Activate it
lung_env\Scripts\activate

REM Upgrade pip
pip install --upgrade pip

REM Install package
pip install -e .

REM Install build tools
pip install pyinstaller>=5.10.0

REM Install ML frameworks
pip install totalsegmentor nnunetv2

REM Install PyTorch (CPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu

REM Download models
totalsegmentor_download_weights

REM Build executable
build_full.bat

REM Test it
dist\lung_asp\lung_asp.exe --help
```

**Done!** 🚀

---

## 📧 Need More Help?

If you're still having issues:

1. **Check specific guides**: See "Related Documentation" above
2. **Read error messages**: They usually tell you what's wrong
3. **Check issue tracker**: See if others had same problem
4. **Open an issue**: Provide error messages and steps you tried

---

**Remember**: The first setup takes 30-50 minutes, but you only do it once! After that, you'll have a fully working standalone application. 🎉

Good luck! 🚀
