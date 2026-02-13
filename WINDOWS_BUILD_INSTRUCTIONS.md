# 🪟 Windows Build Instructions - Complete Guide

## Building Lung-ASP Standalone EXE with All Dependencies

**Your Location**: `C:\Users\nitin\Desktop\Lung_ASP`  
**Goal**: Build complete standalone EXE with TotalSegmentor, nnU-Net, and all models  
**Platform**: Windows using CMD (Command Prompt)  
**Time**: 30-45 minutes  
**Result**: Standalone application (3-5 GB with models)

---

## 📋 Complete 15-Step Process

### Phase 1: Environment Setup (Steps 1-3)

#### Step 1: Navigate to Project Directory

Open CMD (Command Prompt) and navigate to your project:

```cmd
cd C:\Users\nitin\Desktop\Lung_ASP
```

**Verify you're in the right place**:
```cmd
dir
```

You should see: `src`, `lung_asp_cli.py`, `setup.py`, `build_full.bat`, etc.

---

#### Step 2: Check Python Version

```cmd
python --version
```

**Required**: Python 3.8, 3.9, 3.10, or 3.11  
**Example output**: `Python 3.10.0`

❌ **If Python not found**:
- Download from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

---

#### Step 3: Create Virtual Environment

```cmd
python -m venv lung_env
```

This creates a clean Python environment in the `lung_env` folder.

**Why virtual environment?**
- Clean dependency management
- No conflicts with system Python
- Easy to rebuild if needed

---

### Phase 2: Install Dependencies (Steps 4-6)

#### Step 4: Activate Virtual Environment

```cmd
lung_env\Scripts\activate
```

Your prompt should now show `(lung_env)` at the beginning.

**Example**:
```
(lung_env) C:\Users\nitin\Desktop\Lung_ASP>
```

---

#### Step 5: Install the Lung-ASP Package

```cmd
pip install -e .
```

This installs the lung_asp package and core dependencies.

**Expected output**: Installation of numpy, scipy, scikit-image, nibabel, etc.

**Time**: 2-5 minutes

---

#### Step 6: Install All Dependencies

```cmd
pip install pyinstaller>=5.10.0
pip install totalsegmentor nnunetv2
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**What this installs**:
- PyInstaller: For building the EXE
- TotalSegmentor: Anatomical segmentation
- nnU-Net v2: Deep learning segmentation
- PyTorch: Deep learning framework (CPU version)

**Time**: 5-15 minutes (downloading large packages)

**Note**: This installs CPU version of PyTorch. For GPU support, see troubleshooting section.

---

### Phase 3: Download Models (Steps 7-8)

#### Step 7: Download TotalSegmentor Models

```cmd
totalsegmentor_download_weights
```

This downloads TotalSegmentor pretrained models (~300 MB).

**Time**: 5-10 minutes (depending on internet speed)

**Models downloaded to**: `C:\Users\nitin\.totalsegmentor\`

---

#### Step 8: Download nnU-Net Models (Optional)

If you have nnU-Net models:

```cmd
python download_models.py --download-nnunet
```

Or manually place your nnU-Net models in:
```
C:\Users\nitin\.nnunet\models\
```

**Note**: nnU-Net models are optional. The system will work without them using alternative segmentation methods.

---

### Phase 4: Build Executable (Steps 9-12)

#### Step 9: Build with PyInstaller

```cmd
pyinstaller lung_asp.spec --clean --noconfirm
```

**What this does**:
- Reads `lung_asp.spec` configuration
- Bundles Python interpreter
- Includes all dependencies
- Creates standalone executable

**Time**: 5-15 minutes

**Expected output**: 
```
Building EXE from EXE-00.toc completed successfully.
```

**Result**: Executable created in `dist\lung_asp\`

---

#### Step 10: Bundle TotalSegmentor Models

Copy TotalSegmentor models into the distribution:

```cmd
xcopy /E /I %USERPROFILE%\.totalsegmentor dist\lung_asp\_internal\.totalsegmentor
```

This ensures the EXE can find the models.

---

#### Step 11: Bundle nnU-Net Models (If Downloaded)

If you have nnU-Net models:

```cmd
xcopy /E /I %USERPROFILE%\.nnunet dist\lung_asp\_internal\.nnunet
```

---

#### Step 12: Test the Executable

```cmd
dist\lung_asp\lung_asp.exe --help
```

**Expected output**: Help message with all command-line options

**Test basic functionality**:
```cmd
dist\lung_asp\lung_asp.exe --version
```

✅ **Success!** If you see the help/version, the build works!

---

### Phase 5: Package & Distribute (Steps 13-15)

#### Step 13: Create Distribution Package

Package everything into a ZIP file:

```cmd
cd dist
tar -a -c -f lung_asp_windows.zip lung_asp
```

**Alternative** (if `tar` not available):
- Right-click the `lung_asp` folder
- Select "Send to" → "Compressed (zipped) folder"

**Result**: `lung_asp_windows.zip` (~3-5 GB with models)

---

#### Step 14: Test on Another System (Optional)

To verify it's truly standalone:

1. Copy `lung_asp_windows.zip` to another Windows computer
2. Extract the ZIP
3. Run `lung_asp\lung_asp.exe --help`
4. Test with sample data

This verifies no dependencies are missing.

---

#### Step 15: Final Verification

**Verification Checklist**:

✅ Executable exists: `dist\lung_asp\lung_asp.exe`  
✅ Help command works: `lung_asp.exe --help`  
✅ Version displays: `lung_asp.exe --version`  
✅ TotalSegmentor models bundled (check `_internal\.totalsegmentor\`)  
✅ Package size reasonable (2-5 GB)  
✅ Runs without Python installed

**You're done!** 🎉

---

## 📊 Expected Results

### Directory Structure After Build:

```
C:\Users\nitin\Desktop\Lung_ASP\
├── dist\
│   └── lung_asp\
│       ├── lung_asp.exe                    ← Main executable
│       └── _internal\
│           ├── torch\                      ← PyTorch
│           ├── totalsegmentor\            ← TotalSegmentor code
│           ├── nnunetv2\                  ← nnU-Net code
│           ├── .totalsegmentor\           ← TotalSegmentor models
│           ├── .nnunet\                   ← nnU-Net models (if downloaded)
│           ├── numpy\
│           ├── scipy\
│           ├── skimage\
│           └── ... (all other dependencies)
```

### File Sizes:

- **Executable + Python dependencies**: ~1-2 GB
- **TotalSegmentor models**: ~300 MB
- **nnU-Net models**: ~500 MB (if included)
- **Total package**: ~2-5 GB

### Capabilities:

✅ Process DICOM PET/CT files  
✅ Convert DICOM to NIfTI  
✅ Segment lung tumors  
✅ Exclude mediastinal regions  
✅ Calculate 32 radiomics features  
✅ Generate QC visualizations  
✅ Export results (CSV, NIfTI, PNG)  
✅ **Completely standalone - no Python needed!**

---

## 🔧 Troubleshooting

### Issue 1: Python Not Found

**Error**: `'python' is not recognized`

**Solution**:
1. Download Python from https://www.python.org/
2. During installation, check "Add Python to PATH"
3. Restart CMD
4. Verify: `python --version`

---

### Issue 2: pip Not Found

**Error**: `'pip' is not recognized`

**Solution**:
```cmd
python -m pip --version
```

If this works, use `python -m pip` instead of `pip`:
```cmd
python -m pip install -e .
```

---

### Issue 3: Virtual Environment Activation Fails

**Error**: Cannot be loaded because running scripts is disabled

**Solution**:
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy RemoteSigned
```

Then try again with CMD.

**Alternative**: Use `python -m venv` and activate with full path:
```cmd
C:\Users\nitin\Desktop\Lung_ASP\lung_env\Scripts\activate
```

---

### Issue 4: PyTorch Installation Fails

**Error**: Could not find a version that satisfies torch

**Solution**: Install CPU version explicitly:
```cmd
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

For GPU support (if you have NVIDIA GPU):
```cmd
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

### Issue 5: TotalSegmentor Download Fails

**Error**: Connection timeout or download error

**Solution 1**: Retry with better connection
```cmd
totalsegmentor_download_weights --force
```

**Solution 2**: Manual download
1. Download from: https://github.com/wasserth/TotalSegmentator
2. Place in: `C:\Users\nitin\.totalsegmentor\`

---

### Issue 6: PyInstaller Build Warnings

**Check warnings**:
```cmd
type build\lung_asp\warn-lung_asp.txt
```

**Common warnings** (usually safe to ignore):
- Module not found (optional dependencies)
- Hidden imports (already configured in spec file)

**If build fails**: Update dependencies
```cmd
pip install --upgrade pip setuptools wheel
pip install --upgrade pyinstaller
```

---

### Issue 7: EXE Doesn't Run

**Error**: Application failed to start

**Debug steps**:
1. Run with debug flag:
```cmd
dist\lung_asp\lung_asp.exe --debug
```

2. Check for missing DLLs:
   - Install Microsoft Visual C++ Redistributable
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

3. Test in CMD from dist directory:
```cmd
cd dist\lung_asp
lung_asp.exe --help
```

---

### Issue 8: Models Not Found

**Error**: TotalSegmentor models not found

**Solution**: Verify and re-copy models
```cmd
REM Check if models exist
dir %USERPROFILE%\.totalsegmentor

REM Re-copy to distribution
xcopy /E /I /Y %USERPROFILE%\.totalsegmentor dist\lung_asp\_internal\.totalsegmentor
```

**Set environment variable** (if needed):
```cmd
set TOTALSEG_WEIGHTS_PATH=%CD%\dist\lung_asp\_internal\.totalsegmentor
```

---

## 💡 Tips & Best Practices

### Building for Distribution:

1. **Test on clean Windows VM** to verify standalone nature
2. **Include README** with usage instructions
3. **Provide sample data** for testing
4. **Document system requirements** (Windows 10+, 8GB RAM)

### Optimizing Build Size:

If package is too large, you can:
- Use CPU-only PyTorch (smaller than CUDA version)
- Exclude unused nnU-Net models
- Use UPX compression (add `--upx-dir` to PyInstaller)

### GPU Support:

For GPU-accelerated inference:
```cmd
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Requires NVIDIA GPU with CUDA support.

---

## 📚 Related Documentation

- **BUILD_LOCAL.md**: Detailed build guide (all platforms)
- **HOW_TO_BUILD_EXE.md**: Quick build guide
- **USER_GUIDE.md**: Using the application
- **APPLICATION_SCRIPTS.md**: Complete source code
- **BUILD_CHECKLIST.md**: Build verification checklist

---

## 🎯 Quick Reference

### Essential Commands:

```cmd
REM Navigate to project
cd C:\Users\nitin\Desktop\Lung_ASP

REM Setup environment
python -m venv lung_env
lung_env\Scripts\activate

REM Install everything
pip install -e .
pip install pyinstaller totalsegmentor nnunetv2
pip install torch --index-url https://download.pytorch.org/whl/cpu

REM Download models
totalsegmentor_download_weights

REM Build
pyinstaller lung_asp.spec --clean --noconfirm

REM Bundle models
xcopy /E /I %USERPROFILE%\.totalsegmentor dist\lung_asp\_internal\.totalsegmentor

REM Test
dist\lung_asp\lung_asp.exe --help

REM Package
cd dist
tar -a -c -f lung_asp_windows.zip lung_asp
```

---

## ✅ Success Checklist

After completing all steps, verify:

- [ ] Executable created: `dist\lung_asp\lung_asp.exe`
- [ ] Help command works: Shows all options
- [ ] Version command works: Shows version info
- [ ] Models bundled: Check `_internal\.totalsegmentor\`
- [ ] Size reasonable: 2-5 GB total
- [ ] Runs standalone: No Python needed
- [ ] Package created: `lung_asp_windows.zip`
- [ ] All tests pass: Try with sample data

**All checked?** You're ready to distribute! 🎉

---

## 🎉 You're Done!

You now have a **complete standalone Windows application** that includes:

✅ Lung-ASP executable  
✅ All Python dependencies  
✅ TotalSegmentor + models  
✅ nnU-Net (if included)  
✅ 32 radiomics features  
✅ Complete analysis pipeline  

**No installation needed for end users!**

Just distribute `lung_asp_windows.zip` and users can extract and run!

---

**Questions?** See:
- BUILD_LOCAL.md for more details
- USER_GUIDE.md for usage instructions
- FAQ.md for common questions
