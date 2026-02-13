# 🔧 Windows Build Troubleshooting Guide

## Common Build Errors and Solutions

### Error: "Getting requirements to build editable did not run successfully"

**Symptom**:
```
Step 3: Installing lung_asp package...
Obtaining file:///C:/Users/nitin/Desktop/Lung_ASP
  Getting requirements to build editable ... error
  error: subprocess-exited-with-error
```

**Cause**: The setup.py file had issues reading requirements.txt during the build process.

**Solution**: This has been fixed in the latest version. Update your setup.py file or use the workaround below.

---

## Quick Fix Steps

### Method 1: Use Updated setup.py (Recommended)

1. Download the latest `setup.py` from the repository
2. Replace your local `setup.py` with the updated version
3. Try building again

### Method 2: Manual Installation (Workaround)

If you still encounter issues, install dependencies manually:

```cmd
REM Step 1: Install dependencies directly
pip install numpy scipy scikit-image SimpleITK pandas nibabel dicom2nifti trimesh matplotlib pydicom

REM Step 2: Install optional dependencies
pip install totalsegmentor nnunetv2

REM Step 3: Install PyInstaller
pip install pyinstaller>=5.10.0

REM Step 4: Try installing the package again
pip install -e .
```

### Method 3: Install Without Editable Mode

If editable mode fails, use regular installation:

```cmd
REM Install in regular mode (not editable)
pip install .
```

---

## Other Common Windows Errors

### 1. TotalSegmentor Not Found

**Error**: `✗ TotalSegmentor not found`

**Solution**:
```cmd
pip install totalsegmentor
totalsegmentor_download_weights
```

### 2. PyTorch CUDA Version Mismatch

**Error**: PyTorch with wrong CUDA version

**Solution** (CPU-only, smaller):
```cmd
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Solution** (GPU with CUDA 11.8):
```cmd
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### 3. Permission Errors

**Error**: `Access denied` or `Permission denied`

**Solutions**:
- Run CMD as Administrator
- Check antivirus isn't blocking
- Close any programs using the files

### 4. Build Fails with VC++ Errors

**Error**: Missing Visual C++ compiler

**Solution**:
1. Install Microsoft C++ Build Tools: https://visualstudio.microsoft.com/downloads/
2. Or install Visual Studio Community Edition with C++ support

### 5. Out of Memory During Build

**Error**: `MemoryError` during PyInstaller build

**Solutions**:
- Close other applications
- Increase virtual memory
- Use `--clean` flag: `pyinstaller lung_asp.spec --clean`
- Build one module at a time

### 6. Long Path Issues

**Error**: `The system cannot find the path specified` for long paths

**Solution**:
```cmd
REM Enable long paths in Windows
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

Or move project to shorter path like `C:\Lung_ASP`

### 7. Encoding Errors

**Error**: `UnicodeDecodeError` or encoding issues

**Solution**:
```cmd
REM Set UTF-8 encoding
chcp 65001
```

### 8. Import Errors After Build

**Error**: `ModuleNotFoundError` when running the EXE

**Solution**:
1. Check `build/lung_asp/warn-lung_asp.txt` for missing modules
2. Add missing modules to `hiddenimports` in `lung_asp.spec`
3. Rebuild: `pyinstaller lung_asp.spec --clean --noconfirm`

---

## Diagnostic Commands

### Check Python Environment

```cmd
REM Check Python version
python --version

REM Check pip version
pip --version

REM Check installed packages
pip list

REM Check specific package
pip show numpy
```

### Check PyTorch Installation

```cmd
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

### Check TotalSegmentor

```cmd
python -c "import totalsegmentor; print('TotalSegmentor: OK')"
```

### Check nnU-Net

```cmd
python -c "import nnunetv2; print('nnU-Net: OK')"
```

### Test Import of lung_asp

```cmd
python -c "from lung_asp import LungTumorPipeline; print('lung_asp: OK')"
```

---

## Clean Build

If all else fails, start fresh:

```cmd
REM 1. Clean previous builds
rmdir /s /q build
rmdir /s /q dist
del /q *.spec~

REM 2. Deactivate and remove virtual environment
deactivate
rmdir /s /q lung_env

REM 3. Create new virtual environment
python -m venv lung_env
lung_env\Scripts\activate

REM 4. Upgrade pip
python -m pip install --upgrade pip setuptools wheel

REM 5. Install dependencies
pip install -r requirements_exe.txt

REM 6. Install package
pip install -e .

REM 7. Build
pyinstaller lung_asp.spec --clean --noconfirm
```

---

## Still Having Issues?

### Get Detailed Error Information

```cmd
REM Build with verbose output
pip install -e . -v

REM Or with even more detail
pip install -e . -vv
```

### Check Build Logs

1. Look at `build/lung_asp/warn-lung_asp.txt`
2. Check `build/lung_asp/xref-lung_asp.html`
3. Review console output carefully

### Report the Issue

If you still can't resolve the issue, please report it with:

1. Full error message (copy from CMD)
2. Python version: `python --version`
3. Operating system version
4. List of installed packages: `pip list`
5. Contents of `warn-lung_asp.txt` if it exists

---

## Prevention Tips

### 1. Use Virtual Environment

Always use a virtual environment to avoid conflicts:

```cmd
python -m venv lung_env
lung_env\Scripts\activate
```

### 2. Keep Dependencies Updated

```cmd
pip install --upgrade pip setuptools wheel
pip install --upgrade -r requirements.txt
```

### 3. Use Specific Python Version

Python 3.10 is recommended. Avoid 3.12+ as some packages may not be compatible.

### 4. Check Disk Space

Ensure you have at least 15 GB free space for:
- Dependencies (~2 GB)
- Models (~1 GB)
- Build artifacts (~2 GB)
- Final EXE (~3-5 GB)

### 5. Stable Internet Connection

Model downloads require stable internet:
- TotalSegmentor: ~300 MB
- nnU-Net models: ~500 MB

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Setup.py error | Use updated setup.py |
| TotalSegmentor missing | `pip install totalsegmentor` |
| nnU-Net missing | `pip install nnunetv2` |
| PyTorch CUDA | Install CPU version |
| Permission denied | Run as Admin |
| Long paths | Move to C:\ |
| Memory error | Close apps, use --clean |
| Import errors | Check warn file, rebuild |

---

## Success Checklist

- [ ] Python 3.8-3.11 installed
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] setup.py updated to latest version
- [ ] TotalSegmentor downloaded
- [ ] Build completed without errors
- [ ] EXE runs and shows help
- [ ] Test with sample data passes

If all items are checked, your build is successful! ✅

---

**Last Updated**: 2026-02-13

For more help, see:
- `WINDOWS_BUILD_INSTRUCTIONS.md` - Complete build guide
- `HOW_TO_BUILD_EXE.md` - General build instructions
- `BUILD_LOCAL.md` - Detailed build documentation
