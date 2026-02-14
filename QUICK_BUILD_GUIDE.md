# QUICK BUILD REFERENCE CARD
# Lung ASP Executable Builder

## 🚀 FASTEST WAY TO BUILD

### Windows (3 commands):
```cmd
cd C:\Your-Folder
build_executable.bat
# Wait 20-30 minutes → Done!
```

### Linux/Mac (3 commands):
```bash
cd ~/your-folder
chmod +x build_executable.sh && ./build_executable.sh
# Wait 20-30 minutes → Done!
```

---

## 📦 FILES YOU NEED (Total: 11 files)

### Folder: src/ (8 files)
```
✓ __init__.py
✓ Lung_ASP.py
✓ Lung_ASP_GUI.py          ← Main GUI
✓ lung_asp_cli.py
✓ advanced_metrics.py
✓ Mask_QC.py
✓ totalseg_safe.py
✓ download_models.py
```

### Root folder (3 files)
```
✓ requirements-full.txt     ← Dependencies
✓ lung_asp_gui.spec         ← Build config
✓ build_executable.bat/sh   ← Build script
```

**Total size: < 100 KB** (tiny!)

---

## 💻 SYSTEM REQUIREMENTS

| Item | Requirement |
|------|-------------|
| **Python** | 3.10 or 3.11 |
| **RAM** | 8 GB min, 16 GB recommended |
| **Disk** | 20 GB free space |
| **Internet** | Required for build |
| **Time** | 20-30 minutes |

---

## 📥 WHERE TO GET FILES

### Option 1: Git Clone
```bash
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP
```

### Option 2: Manual Download
1. Go to: https://github.com/nittinnm22-sudo/breast-ASP
2. Click "Code" → "Download ZIP"
3. Extract and use

---

## 🔨 BUILD PROCESS

```
Step 1: Check Python     ✓ python --version
Step 2: Create venv      ✓ Automatic
Step 3: Install deps     ✓ 10-20 min
Step 4: Build executable ✓ 5-10 min
Step 5: Verify          ✓ Check dist/
```

---

## 📍 WHERE IS MY EXECUTABLE?

After successful build:

**Windows:**
```
dist\LungASP\LungASP.exe
```

**Linux/Mac:**
```
dist/LungASP/LungASP
```

**Copy entire `dist/LungASP/` folder to distribute!**

---

## ⚠️ COMMON ISSUES

| Problem | Solution |
|---------|----------|
| Python not found | Add Python to PATH |
| pip install fails | Check internet connection |
| Build fails | Delete build/ and dist/ folders, retry |
| Executable won't run | Copy entire dist/LungASP/ folder, not just .exe |

---

## 📤 DISTRIBUTE YOUR APP

1. Compress `dist/LungASP/` folder
2. Share via USB/Cloud/Network
3. Users extract and run
4. First run downloads models (needs internet)

**App size: 500 MB - 2 GB compressed**

---

## 🎯 QUICK CHECKLIST

Before building:
- [ ] Python 3.10/3.11 installed
- [ ] All 11 files present
- [ ] Internet connected
- [ ] 20 GB disk space free

After building:
- [ ] dist/LungASP/ folder exists
- [ ] Executable runs without errors
- [ ] Models download on first run

---

## 🆘 NEED HELP?

1. Read: `BUILD_INSTRUCTIONS.md` (detailed guide)
2. Check: Troubleshooting section
3. Verify: All files present with `PACKAGE_LIST.md`

---

## 📞 DEPENDENCIES INCLUDED

✓ NumPy, SciPy, scikit-image
✓ Matplotlib, Pillow
✓ NiBabel, PyDICOM, SimpleITK
✓ TotalSegmentator
✓ nnU-Net
✓ All GUI libraries
✓ Everything needed!

---

**Build once → Run anywhere → No Python needed on target computers!**

_Last updated: February 2026_
