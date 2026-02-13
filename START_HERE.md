# 🎯 COMPLETE BUILD INSTRUCTIONS - SAVE THIS!

## Everything You Need to Build the Lung-ASP Executable

### 📋 Prerequisites (You Already Have)
✅ TotalSegmentor installed
✅ nnU-Net (nnunetv2) installed
✅ PyTorch installed
✅ All other dependencies

---

## 🚀 OPTION 1: One-Command Build (EASIEST)

### On Linux/macOS:
```bash
cd /path/to/breast-ASP
chmod +x build_full.sh
./build_full.sh
```

### On Windows:
```cmd
cd C:\path\to\breast-ASP
build_full.bat
```

**That's it!** The script will:
- Check all dependencies
- Install the package
- Build the executable
- Test it
- Create a distribution package

**Time**: 5-15 minutes
**Result**: `dist/lung_asp/` with your executable

---

## 🛠️ OPTION 2: Manual Build (Step-by-Step)

### Step 1: Install the Package
```bash
cd /path/to/breast-ASP
pip install -e .
```

### Step 2: Build with PyInstaller
```bash
pyinstaller lung_asp.spec --clean --noconfirm
```

### Step 3: Test the Executable
```bash
# Linux/macOS:
./dist/lung_asp/lung_asp --help

# Windows:
dist\lung_asp\lung_asp.exe --help
```

### Step 4: Create Distribution Package
```bash
# Linux/macOS:
cd dist
tar -czf lung_asp_v1.0.0.tar.gz lung_asp/

# Windows:
cd dist
tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
```

---

## 📦 What You'll Get

After building:
```
dist/
└── lung_asp/                           ← This entire folder is your app
    ├── lung_asp (or lung_asp.exe)     ← The executable
    └── _internal/                      ← All dependencies bundled
        ├── torch/
        ├── totalsegmentor/
        ├── nnunetv2/
        ├── numpy/
        ├── scipy/
        └── ... (everything else)
```

**Size**: 2-4 GB (depending on models)
**Portable**: Can copy to any computer (same OS)
**Standalone**: No Python or pip needed to run

---

## ✅ Verify Your Build

Test these commands:
```bash
# Show help
./dist/lung_asp/lung_asp --help

# Show version
./dist/lung_asp/lung_asp --version

# Process sample data
./dist/lung_asp/lung_asp \
  --pet-nifti test_pet.nii.gz \
  --ct-nifti test_ct.nii.gz \
  --output results/ \
  --verbose
```

---

## 🔧 If Something Goes Wrong

### Missing PyInstaller?
```bash
pip install pyinstaller>=5.10.0
```

### Missing Dependencies?
```bash
pip install -r requirements_exe.txt
```

### Build Fails?
Check the warnings file:
```bash
cat build/lung_asp/warn-lung_asp.txt
```

### Executable Crashes?
Run with debug mode:
```bash
./dist/lung_asp/lung_asp --debug
```

---

## 📤 How to Share Your Executable

### Package It
```bash
# Linux/macOS:
cd dist
tar -czf lung_asp_v1.0.0.tar.gz lung_asp/

# Windows:
cd dist
tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
```

### Distribute
Share the `.tar.gz` or `.zip` file. Users just:
1. Extract it
2. Run `./lung_asp/lung_asp` (or `lung_asp.exe`)
3. No installation needed!

---

## 📝 Files You Should Save

Make sure you have these files from the repository:

**Essential:**
- ✅ `build_full.sh` (Linux/macOS) or `build_full.bat` (Windows)
- ✅ `lung_asp.spec` (PyInstaller configuration)
- ✅ `lung_asp_cli.py` (Main entry point)
- ✅ `setup.py` (Package configuration)
- ✅ `requirements_exe.txt` (Dependencies list)
- ✅ `src/` directory (All source code)

**Helpful:**
- ✅ `BUILD_LOCAL.md` (Detailed build guide)
- ✅ `QUICK_BUILD_GUIDE.md` (Quick reference)
- ✅ `BUILD_CHECKLIST.md` (Verification checklist)
- ✅ `USER_GUIDE.md` (End-user documentation)

---

## 💡 Pro Tips

### Faster Builds
```bash
# Skip UPX compression (faster, but larger)
pyinstaller lung_asp.spec --noupx --noconfirm
```

### Smaller Package
Edit `lung_asp.spec` and add:
```python
excludes=['tkinter', 'PyQt5', 'jupyter', 'IPython']
```

### Bundle Models
Edit `lung_asp.spec` and add:
```python
datas += [('/path/to/.totalsegmentor', 'totalsegmentor_models')]
```

---

## 🎯 Quick Command Reference

```bash
# Verify dependencies
python -c "import torch, totalsegmentor, nnunetv2, PyInstaller; print('All OK!')"

# Install package
pip install -e .

# Build executable
pyinstaller lung_asp.spec --clean --noconfirm

# Test executable
./dist/lung_asp/lung_asp --help

# Create package
cd dist && tar -czf lung_asp.tar.gz lung_asp/

# Check size
du -sh dist/lung_asp

# Run on sample data
./dist/lung_asp/lung_asp --pet-nifti pet.nii.gz --output results/
```

---

## 📊 Expected Timeline

1. **First time setup**: 5 minutes
2. **Building**: 10-15 minutes
3. **Testing**: 2 minutes
4. **Packaging**: 1 minute

**Total**: ~20 minutes start to finish

---

## 🆘 Need Help?

Check these documents in order:
1. `QUICK_BUILD_GUIDE.md` - Quick commands
2. `BUILD_LOCAL.md` - Detailed guide
3. `BUILD_CHECKLIST.md` - Verify each step
4. Build output in `build/lung_asp/warn-lung_asp.txt`

---

## ✨ Summary

You have everything installed. Just run:

```bash
# One command:
./build_full.sh   # (or build_full.bat on Windows)

# Wait 10-15 minutes

# Done! Your executable is in:
# dist/lung_asp/lung_asp
```

Package it, share it, use it anywhere! 🚀

---

**SAVE THIS FILE** - It has everything you need!

Last updated: 2026-02-12
Version: 1.0.0
