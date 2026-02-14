# Quick Visual Guide: Download → Build → Distribute

## 🎯 Goal: Create Standalone Executable with ALL Dependencies

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  INPUT:  GitHub Repository                                        │
│  OUTPUT: Standalone .exe with TotalSegmentator + nnU-Net built-in │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Download All Files ⬇️

### Method A: Using Git (Recommended)

```
┌─────────────────────────────────────────────────────┐
│  1. Open Command Prompt / Terminal                  │
│                                                     │
│  2. Run:                                            │
│     git clone https://github.com/               │
│               nittinnm22-sudo/breast-ASP.git        │
│                                                     │
│  3. Enter folder:                                   │
│     cd breast-ASP                                   │
└─────────────────────────────────────────────────────┘
```

### Method B: Download ZIP (No Git)

```
┌─────────────────────────────────────────────────────┐
│  1. Visit: https://github.com/                     │
│            nittinnm22-sudo/breast-ASP               │
│                                                     │
│  2. Click: "Code" → "Download ZIP"                 │
│                                                     │
│  3. Extract ZIP to your laptop                     │
│                                                     │
│  4. Open folder in terminal                        │
└─────────────────────────────────────────────────────┘
```

**Result:** You now have all files on your laptop! ✓

---

## Step 2: Verify Files ✅

```
┌─────────────────────────────────────────────────────┐
│  Run verification:                                  │
│                                                     │
│    python verify_download.py                        │
│                                                     │
│  Expected output:                                   │
│    ✓ All required files present                    │
│    ✓ Ready to build                                │
└─────────────────────────────────────────────────────┘
```

**If verification fails:** Re-download the repository

---

## Step 3: Build Executable 🔨

### Windows

```
┌─────────────────────────────────────────────────────┐
│  1. Open Command Prompt                             │
│                                                     │
│  2. Navigate to folder:                             │
│     cd C:\path\to\breast-ASP                        │
│                                                     │
│  3. Run build:                                      │
│     build_executable.bat                            │
│                                                     │
│  4. Wait: 20-30 minutes ⏱️                          │
└─────────────────────────────────────────────────────┘
```

### Mac/Linux

```
┌─────────────────────────────────────────────────────┐
│  1. Open Terminal                                   │
│                                                     │
│  2. Navigate to folder:                             │
│     cd ~/path/to/breast-ASP                         │
│                                                     │
│  3. Make executable:                                │
│     chmod +x build_executable.sh                    │
│                                                     │
│  4. Run build:                                      │
│     ./build_executable.sh                           │
│                                                     │
│  5. Wait: 20-30 minutes ⏱️                          │
└─────────────────────────────────────────────────────┘
```

### What Happens During Build

```
[1/6] Checking Python version...       ✓  5 sec
[2/6] Creating virtual environment...  ✓  10 sec
[3/6] Activating environment...        ✓  5 sec
[4/6] Installing dependencies...       ⏳  15-25 min
      - numpy, scipy, scikit-image
      - TotalSegmentator
      - nnU-Net (nnunetv2)
      - PyInstaller
      - All other libraries
[5/6] Building executable...           ⏳  5-10 min
      - Bundling Python runtime
      - Bundling all libraries
      - Creating executable
[6/6] Verifying build...               ✓  5 sec

BUILD SUCCESSFUL! 🎉
```

---

## Step 4: Result - Standalone Application 📦

### Folder Structure After Build

```
breast-ASP/
├── dist/
│   └── LungASP/              ⭐ YOUR STANDALONE APPLICATION
│       ├── LungASP.exe       (Windows executable)
│       ├── LungASP           (Mac/Linux executable)
│       └── _internal/        (bundled dependencies)
│           ├── numpy/
│           ├── scipy/
│           ├── totalsegmentator/
│           ├── nnunetv2/
│           └── ... (all libraries)
```

### What's Included

```
✅ Python runtime (no Python needed on target PC)
✅ NumPy, SciPy, scikit-image
✅ TotalSegmentator (complete)
✅ nnU-Net v2
✅ GUI (Tkinter, matplotlib)
✅ Medical imaging (NiBabel, PyDICOM, SimpleITK)
✅ DICOM conversion (dicom2nifti)
✅ All application code
```

### Size

```
Initial:     ~2-3 GB  (without models)
After 1st:   ~5-8 GB  (models downloaded)
```

---

## Step 5: Test on Build Computer 🧪

```
┌─────────────────────────────────────────────────────┐
│  Windows:                                           │
│    cd dist\LungASP                                  │
│    LungASP.exe                                      │
│                                                     │
│  Mac/Linux:                                         │
│    cd dist/LungASP                                  │
│    ./LungASP                                        │
│                                                     │
│  Expected: GUI window opens! ✓                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 6: Distribute to Other Computers 🚀

### What to Share

```
┌─────────────────────────────────────────────────────┐
│  Copy ENTIRE folder:                                │
│    dist/LungASP/     (whole folder)                 │
│                                                     │
│  DO NOT copy just the .exe file!                   │
│  The _internal folder is required!                 │
└─────────────────────────────────────────────────────┘
```

### Transfer Methods

```
Option 1: USB Drive
  - Copy dist/LungASP folder to USB
  - Paste on target computer
  
Option 2: Network Share
  - Share dist/LungASP folder
  - Copy from network to target computer

Option 3: Cloud Storage
  - Compress to ZIP: LungASP.zip
  - Upload to Dropbox/Google Drive/OneDrive
  - Download on target computer
  - Extract ZIP

Option 4: File Transfer
  - Use WeTransfer, Send Anywhere, etc.
  - Send LungASP.zip (2-3 GB)
```

### On Target Computer

```
┌─────────────────────────────────────────────────────┐
│  1. Extract/Copy LungASP folder                     │
│                                                     │
│  2. Double-click LungASP.exe                        │
│                                                     │
│  3. First run:                                      │
│     - May take 2-5 minutes                          │
│     - Downloads models (~3-5 GB)                    │
│     - Needs internet connection once                │
│                                                     │
│  4. Subsequent runs: Instant! ⚡                    │
└─────────────────────────────────────────────────────┘
```

---

## Complete Workflow Diagram

```
┌─────────────┐
│   GITHUB    │  Download repository
│ Repository  │────────────────────┐
└─────────────┘                    │
                                   ▼
┌─────────────┐              ┌──────────┐
│  YOUR       │  Verify      │  Files   │
│  LAPTOP     │◄─────────────│ On Disk  │
│             │              └──────────┘
│             │                    │
│   Python    │  Build             │
│  Installed  │◄───────────────────┘
│             │              
│             │  Produces    ┌──────────────┐
│             │─────────────►│ dist/LungASP │
└─────────────┘              │  Standalone  │
                             │ Executable   │
                             └──────────────┘
                                   │
                                   │ Copy
                                   │
                ┌──────────────────┴─────────────────┐
                │                                    │
                ▼                                    ▼
        ┌──────────────┐                   ┌──────────────┐
        │  Computer A  │                   │  Computer B  │
        │  (No Python) │                   │  (No Python) │
        │              │                   │              │
        │  Just run:   │                   │  Just run:   │
        │  LungASP.exe │                   │  LungASP.exe │
        └──────────────┘                   └──────────────┘
```

---

## Checklist ✓

Use this checklist to track your progress:

```
□ Python 3.10+ installed on build computer
□ 15+ GB disk space available
□ Internet connection available
□ Downloaded repository (git clone or ZIP)
□ Run verify_download.py → All files present
□ Run build_executable.bat/sh
□ Wait 20-30 minutes for build
□ Build successful message shown
□ Test: Run dist/LungASP/LungASP.exe
□ GUI opens successfully
□ Copy entire dist/LungASP folder
□ Test on another computer
□ Works without Python installed ✓
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.10+ from python.org |
| Missing files | Re-download repository |
| Build fails | Delete venv_build folder, run again |
| Out of disk space | Free up 15+ GB |
| Slow download | Stable internet needed for dependencies |
| Module not found in exe | Copy entire folder, not just .exe |
| Models not downloading | Internet connection required on first run |

---

## Time & Space Requirements

### Build Time
- **Fast computer (SSD, fast internet):** 15-20 minutes
- **Average computer:** 20-30 minutes
- **Slow computer/internet:** 30-45 minutes

### Disk Space
- **During build:** 15 GB temporary
- **Final executable:** 2-3 GB
- **With models:** 5-8 GB total

### First Run on Target Computer
- **Download models:** 2-5 minutes (with fast internet)
- **Model size:** 3-5 GB
- **Only once!** Subsequent runs are instant

---

## Summary

```
1. Download repository → Your laptop has all source files
2. Verify files → Ensure nothing missing
3. Run build script → Wait 20-30 minutes
4. Test executable → GUI opens successfully
5. Share folder → Copy to any computer, no Python needed!

Result: Standalone application with TotalSegmentator and 
        nnU-Net built-in, works without Python installed!
```

---

## Files You Need

### Absolute Minimum (11 files)

```
src/
  ├── Lung_ASP.py
  ├── Lung_ASP_GUI.py
  ├── advanced_metrics.py
  ├── Mask_QC.py
  ├── totalseg_safe.py
  ├── download_models.py
  ├── dicom_converter.py
  └── lung_asp_cli.py

requirements-full.txt
lung_asp_gui.spec
build_executable.bat (Windows) or build_executable.sh (Mac/Linux)
```

### Recommended (Add these)

```
verify_download.py
BUILD_INSTRUCTIONS.md
COMPLETE_DOWNLOAD_BUILD_GUIDE.md
README.md
```

**Best:** Download entire repository!

---

## Next Steps

1. ✅ Read this guide
2. ✅ Download repository to your laptop
3. ✅ Run `verify_download.py`
4. ✅ Run `build_executable.bat` or `./build_executable.sh`
5. ✅ Wait for build to complete
6. ✅ Test the executable
7. ✅ Share with others!

**You're ready to build!** 🚀
