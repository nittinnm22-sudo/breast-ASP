# 📥 How to Download All Lung-ASP Python Scripts

## 🎯 Quick Answer

To download all 9 lung-ASP Python scripts, **clone the repository**:

```bash
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP/src/lung_asp
```

**That's it!** You now have all 9 scripts.

---

## 📋 What You'll Get

### All 9 Python Scripts (2,373 lines total):

1. ✅ `__init__.py` (31 lines) - Package initialization
2. ✅ `dicom_converter.py` (177 lines) - DICOM to NIfTI conversion
3. ✅ `lung_exclusion.py` (265 lines) - Mediastinal exclusion
4. ✅ `lung_pipeline.py` (231 lines) - Complete pipeline
5. ✅ `lung_radiomics.py` (621 lines) - 32 radiomics features
6. ✅ `lung_segmentation.py` (298 lines) - Tumor segmentation
7. ✅ `nnunet_wrapper.py` (252 lines) - nnU-Net integration
8. ✅ `qc_visualization.py` (297 lines) - QC visualizations
9. ✅ `totalsegmentor_wrapper.py` (201 lines) - TotalSegmentor integration

---

## 📥 Download Methods

### Method 1: Full Repository Clone (Recommended) ⭐

**Best for**: Most users, getting complete project

```bash
# Clone the repository
git clone https://github.com/nittinnm22-sudo/breast-ASP.git

# Navigate to lung_asp scripts
cd breast-ASP/src/lung_asp

# List all scripts
ls -lh *.py
```

**Result**: All 9 scripts in `src/lung_asp/` directory

**Time**: ~30 seconds

---

### Method 2: Download ZIP (No Git Required)

**Best for**: Users without Git installed

**Steps**:
1. Go to: https://github.com/nittinnm22-sudo/breast-ASP
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file
5. Navigate to `breast-ASP-main/src/lung_asp/`

**Result**: All files in ZIP archive

**Time**: ~1 minute

---

### Method 3: Sparse Checkout (Lung-ASP Only)

**Best for**: Getting only lung_asp directory (saves bandwidth)

```bash
# Clone with sparse checkout
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/nittinnm22-sudo/breast-ASP.git

# Enter repository
cd breast-ASP

# Set sparse checkout to lung_asp only
git sparse-checkout set src/lung_asp

# Navigate to scripts
cd src/lung_asp

# Verify
ls -lh
```

**Result**: Only lung_asp scripts downloaded

**Time**: ~10 seconds

---

### Method 4: Download Individual Files

**Best for**: Getting specific scripts only

#### Using wget (Linux/macOS):

```bash
# Create directory
mkdir -p lung_asp
cd lung_asp

# Base URL
BASE_URL="https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp"

# Download all 9 scripts
wget $BASE_URL/__init__.py
wget $BASE_URL/dicom_converter.py
wget $BASE_URL/lung_exclusion.py
wget $BASE_URL/lung_pipeline.py
wget $BASE_URL/lung_radiomics.py
wget $BASE_URL/lung_segmentation.py
wget $BASE_URL/nnunet_wrapper.py
wget $BASE_URL/qc_visualization.py
wget $BASE_URL/totalsegmentor_wrapper.py
```

#### Using curl (macOS/Windows):

```bash
# Create directory
mkdir lung_asp
cd lung_asp

# Download all 9 scripts
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/__init__.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/dicom_converter.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/lung_exclusion.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/lung_pipeline.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/lung_radiomics.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/lung_segmentation.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/nnunet_wrapper.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/qc_visualization.py
curl -O https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp/totalsegmentor_wrapper.py
```

**Result**: All 9 files in current directory

---

### Method 5: GitHub CLI

**Best for**: Command-line power users with GitHub CLI installed

```bash
# Clone using GitHub CLI
gh repo clone nittinnm22-sudo/breast-ASP

# Navigate to scripts
cd breast-ASP/src/lung_asp

# List files
ls -lh
```

**Result**: Repository cloned, scripts ready

---

### Method 6: Automated Download Script

**Best for**: One-command download with verification

Create a file `download_lung_asp.sh`:

```bash
#!/bin/bash

echo "📥 Downloading lung-ASP Python scripts..."

# Create directory
mkdir -p lung_asp
cd lung_asp

# Base URL
BASE="https://raw.githubusercontent.com/nittinnm22-sudo/breast-ASP/main/src/lung_asp"

# List of files
FILES=(
    "__init__.py"
    "dicom_converter.py"
    "lung_exclusion.py"
    "lung_pipeline.py"
    "lung_radiomics.py"
    "lung_segmentation.py"
    "nnunet_wrapper.py"
    "qc_visualization.py"
    "totalsegmentor_wrapper.py"
)

# Download each file
for file in "${FILES[@]}"; do
    echo "  Downloading $file..."
    if command -v wget &> /dev/null; then
        wget -q "$BASE/$file"
    elif command -v curl &> /dev/null; then
        curl -sO "$BASE/$file"
    else
        echo "Error: Neither wget nor curl is installed!"
        exit 1
    fi
    
    if [ -f "$file" ]; then
        echo "  ✓ $file downloaded"
    else
        echo "  ✗ Failed to download $file"
    fi
done

echo ""
echo "✅ Download complete! Files in: $(pwd)"
echo "📁 Total files: $(ls -1 *.py 2>/dev/null | wc -l)"
```

**Usage**:
```bash
bash download_lung_asp.sh
```

**Result**: All scripts downloaded automatically

---

## ✅ Verification

After downloading, verify you have all files:

### Check File Count:
```bash
# Should output: 9
ls -1 *.py | wc -l
```

### Check Total Lines:
```bash
# Should show ~2373 total lines
wc -l *.py
```

### List All Files:
```bash
ls -lh *.py
```

**Expected output**:
```
-rw-r--r-- 1 user group  1.2K __init__.py
-rw-r--r-- 1 user group  6.5K dicom_converter.py
-rw-r--r-- 1 user group  9.8K lung_exclusion.py
-rw-r--r-- 1 user group  8.5K lung_pipeline.py
-rw-r--r-- 1 user group   23K lung_radiomics.py
-rw-r--r-- 1 user group   11K lung_segmentation.py
-rw-r--r-- 1 user group  9.3K nnunet_wrapper.py
-rw-r--r-- 1 user group   11K qc_visualization.py
-rw-r--r-- 1 user group  7.4K totalsegmentor_wrapper.py
```

### Test Import:
```bash
python -c "import sys; sys.path.insert(0, '.'); import lung_radiomics; print('✓ Import successful!')"
```

---

## 🔧 After Download

### 1. Install Dependencies

```bash
# Navigate to repository root
cd breast-ASP

# Install package
pip install -e .

# Or install specific requirements
pip install numpy scipy scikit-image nibabel trimesh
```

### 2. Test the Scripts

```bash
# Test basic import
python -c "from lung_asp import LungTumorPipeline; print('✓ Works!')"

# Run a simple test
cd tests
python test_lung.py
```

### 3. Use the Scripts

```python
# Example usage
from lung_asp import LungTumorPipeline

# Create pipeline
pipeline = LungTumorPipeline()

# Process PET/CT data
results = pipeline.process(pet_data, ct_data, pet_affine, voxel_size)

# Access results
print(results['metabolic_features'])
print(results['shape_features'])
```

---

## 🆘 Troubleshooting

### Issue: "Git command not found"
**Solution**: Use Method 2 (ZIP download) or install Git:
```bash
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Download from: https://git-scm.com/download/win
```

### Issue: "wget: command not found"
**Solution**: Use curl or Git clone method
```bash
# Install wget (Ubuntu/Debian)
sudo apt-get install wget

# Install wget (macOS)
brew install wget
```

### Issue: "Permission denied"
**Solution**: Use sudo or download to user directory
```bash
# Download to home directory
cd ~
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
```

### Issue: "Repository not found"
**Solution**: Check the URL and use HTTPS
```bash
# Use HTTPS (no authentication needed)
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
```

### Issue: Files downloaded but import fails
**Solution**: Install dependencies
```bash
pip install numpy scipy scikit-image nibabel trimesh matplotlib
```

---

## 📊 Quick Reference

### Platform-Specific Commands

| Platform | Quick Download Command |
|----------|----------------------|
| **Linux** | `git clone https://github.com/nittinnm22-sudo/breast-ASP.git && cd breast-ASP/src/lung_asp` |
| **macOS** | `git clone https://github.com/nittinnm22-sudo/breast-ASP.git && cd breast-ASP/src/lung_asp` |
| **Windows** | `git clone https://github.com/nittinnm22-sudo/breast-ASP.git` then `cd breast-ASP\src\lung_asp` |

### Method Comparison

| Method | Speed | Size | Difficulty | Tools Needed |
|--------|-------|------|------------|--------------|
| Full Clone | Fast | ~125 KB | Easy | Git |
| ZIP Download | Medium | ~125 KB | Easiest | Browser |
| Sparse Checkout | Very Fast | ~50 KB | Medium | Git |
| Individual Files | Slow | ~50 KB | Easy | wget/curl |
| GitHub CLI | Fast | ~125 KB | Easy | gh |
| Automated Script | Fast | ~50 KB | Easiest | wget/curl |

---

## 🎯 Summary

### To download all lung-ASP Python scripts:

**Easiest**: Method 2 (ZIP download) - No tools needed
**Fastest**: Method 3 (Sparse checkout) - Only downloads lung_asp
**Recommended**: Method 1 (Full clone) - Gets complete project

### What you get:
- ✅ 9 Python scripts
- ✅ 2,373 lines of code
- ✅ Complete lung tumor analysis system
- ✅ 32 radiomics features
- ✅ Deep learning integration (TotalSegmentor, nnU-Net)
- ✅ QC visualization tools

### Next steps:
1. Download using your preferred method
2. Verify all 9 files exist
3. Install dependencies
4. Test imports
5. Start using!

---

## 📚 Related Documentation

- **Complete Source Code**: See `ALL_LUNG_ASP_PYTHON_SCRIPTS.md`
- **Script Reference**: See `LUNG_ASP_SCRIPTS.md`
- **Quick Reference**: See `LUNG_ASP_SCRIPTS_QUICK.md`
- **Build Guide**: See `BUILD_LOCAL.md`
- **User Guide**: See `USER_GUIDE.md`

---

## ✅ Success!

You now know **6 different ways** to download all lung-ASP Python scripts!

Choose the method that works best for you and start developing! 🚀

---

*For more help, see the repository README or open an issue on GitHub.*
