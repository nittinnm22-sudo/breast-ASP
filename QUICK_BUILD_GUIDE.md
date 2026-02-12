# 🚀 QUICK BUILD REFERENCE - Save This!

## One-Command Build (Recommended)

### Linux/macOS:
```bash
chmod +x build_full.sh && ./build_full.sh
```

### Windows:
```cmd
build_full.bat
```

---

## Manual Build Commands

### 1. Install Package
```bash
pip install -e .
```

### 2. Build Executable
```bash
pyinstaller lung_asp.spec --clean --noconfirm
```

### 3. Test
```bash
# Linux/macOS:
./dist/lung_asp/lung_asp --help

# Windows:
dist\lung_asp\lung_asp.exe --help
```

### 4. Package
```bash
# Linux/macOS:
cd dist && tar -czf lung_asp_v1.0.0.tar.gz lung_asp/

# Windows:
cd dist && tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
```

---

## Verify Dependencies Before Building

```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import totalsegmentor; print('TotalSegmentor: OK')"
python -c "import nnunetv2; print('nnU-Net: OK')"
python -c "import PyInstaller; print('PyInstaller: OK')"
```

---

## If Dependencies Missing

```bash
pip install -r requirements_exe.txt
```

Or install individually:
```bash
pip install torch torchvision
pip install totalsegmentor
pip install nnunetv2
pip install pyinstaller
```

---

## Common Issues & Fixes

### Issue: PyInstaller fails
```bash
pip install --upgrade pyinstaller
```

### Issue: Missing modules during build
Edit `lung_asp.spec`, add to `hiddenimports`:
```python
hiddenimports += ['missing_module_name']
```

### Issue: Executable crashes
```bash
# Check warnings
cat build/lung_asp/warn-lung_asp.txt

# Run with debug
./dist/lung_asp/lung_asp --debug
```

### Issue: Too large (>5GB)
Edit `lung_asp.spec`, add to `excludes`:
```python
excludes += ['tkinter', 'PyQt5', 'jupyter']
```

---

## File Locations

- **Source code**: `lung_asp_cli.py`
- **Build config**: `lung_asp.spec`
- **Build output**: `dist/lung_asp/`
- **Build logs**: `build/lung_asp/`
- **Executable**: `dist/lung_asp/lung_asp` (or `.exe`)

---

## Test Commands After Build

```bash
# Help
./dist/lung_asp/lung_asp --help

# Version
./dist/lung_asp/lung_asp --version

# Check dependencies
./dist/lung_asp/lung_asp --check-dependencies

# Process sample data
./dist/lung_asp/lung_asp \
  --pet-nifti sample_pet.nii.gz \
  --ct-nifti sample_ct.nii.gz \
  --output results/ \
  --verbose
```

---

## Distribution Package Contents

```
lung_asp_v1.0.0.tar.gz (or .zip)
├── lung_asp/                    # Main directory
│   ├── lung_asp (or .exe)      # Executable
│   └── _internal/               # Dependencies
│       ├── torch/
│       ├── totalsegmentor/
│       ├── nnunetv2/
│       └── ... (all libraries)
```

---

## Expected Sizes

- Base package: 1-2 GB
- With TotalSegmentor models: +300-500 MB
- With nnU-Net models: +500-1000 MB
- **Total: 2-4 GB**

---

## Build Time

- Clean system: 10-15 minutes
- Subsequent builds: 5-10 minutes
- Includes: dependency collection, bundling, compression

---

## Support Files to Save

Save these files from the repository:
1. ✅ `build_full.sh` (Linux/macOS)
2. ✅ `build_full.bat` (Windows)  
3. ✅ `lung_asp.spec` (PyInstaller config)
4. ✅ `lung_asp_cli.py` (Main script)
5. ✅ `requirements_exe.txt` (Dependencies)
6. ✅ `setup.py` (Package config)
7. ✅ `src/` directory (Source code)
8. ✅ `BUILD_LOCAL.md` (Detailed guide)

---

## Complete Build Process (Copy-Paste Ready)

### Linux/macOS:
```bash
# Navigate to project
cd /path/to/breast-ASP

# Make script executable
chmod +x build_full.sh

# Run build
./build_full.sh

# Test
./dist/lung_asp/lung_asp --help

# Package
cd dist
tar -czf lung_asp_v1.0.0_$(uname -s).tar.gz lung_asp/
cd ..

# Done!
ls -lh dist/*.tar.gz
```

### Windows (PowerShell/CMD):
```cmd
REM Navigate to project
cd C:\path\to\breast-ASP

REM Run build
build_full.bat

REM Test
dist\lung_asp\lung_asp.exe --help

REM Package (if not done automatically)
cd dist
tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
cd ..

REM Done!
dir dist\*.zip
```

---

## Usage After Building

End users just need to:
1. Extract the archive
2. Run the executable
3. No Python or dependencies needed!

```bash
# Extract
tar -xzf lung_asp_v1.0.0.tar.gz

# Run
cd lung_asp
./lung_asp --pet-dicom PET_DIR/ --output results/
```

---

## Need Help?

See detailed documentation:
- `BUILD_LOCAL.md` - Complete build guide
- `USER_GUIDE.md` - End-user documentation
- `BUILD_EXECUTABLE.md` - Technical details

---

**SAVE THIS FILE** for quick reference when building!
