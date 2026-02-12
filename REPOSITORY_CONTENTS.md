# 📦 Repository Contents

## ✅ YES! This Repository Includes BOTH Systems

When you clone this repository, you get **BOTH** breast-ASP and lung-ASP systems!

```bash
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
```

**Downloads**:
- ✅ breast_asp package (breast tumor analysis)
- ✅ lung_asp package (lung tumor analysis)
- ✅ All examples, tests, and documentation
- ✅ Everything!

---

## 📁 Complete Repository Structure

```
breast-ASP/                          ← One repository, BOTH systems!
│
├── 📂 src/                          ← Source code (152 KB)
│   ├── 📂 breast_asp/              ← Breast tumor analysis (44 KB)
│   │   ├── __init__.py
│   │   ├── segmentation.py         ← SUV thresholding + random walker
│   │   ├── exclusion.py            ← Axillary node exclusion
│   │   ├── radiomics.py            ← 24 radiomics features
│   │   └── pipeline.py             ← End-to-end pipeline
│   │
│   └── 📂 lung_asp/                ← Lung tumor analysis (108 KB)
│       ├── __init__.py
│       ├── dicom_converter.py      ← DICOM to NIfTI conversion
│       ├── lung_segmentation.py    ← Random walker + deep learning
│       ├── lung_exclusion.py       ← Mediastinal exclusion
│       ├── lung_radiomics.py       ← 32 radiomics features
│       ├── lung_pipeline.py        ← End-to-end pipeline
│       ├── qc_visualization.py     ← Quality control overlays
│       ├── totalsegmentor_wrapper.py  ← TotalSegmentor integration
│       └── nnunet_wrapper.py       ← nnU-Net integration
│
├── 📂 examples/                     ← Example scripts
│   ├── 📂 breast_examples/
│   │   └── example_usage.py        ← 5 breast tumor examples
│   └── 📂 lung_examples/
│       └── example_lung_usage.py   ← 5 lung tumor examples
│
├── 📂 tests/                        ← Unit tests
│   ├── test_basic.py               ← 6 breast tumor tests
│   └── test_lung.py                ← 8 lung tumor tests
│
├── 🔧 Build Scripts
│   ├── build_full.sh               ← Linux/macOS executable builder
│   ├── build_full.bat              ← Windows executable builder
│   ├── lung_asp.spec               ← PyInstaller configuration
│   └── lung_asp_cli.py             ← Command-line interface
│
├── 📋 Configuration
│   ├── setup.py                    ← Package installation
│   ├── requirements.txt            ← Basic dependencies
│   ├── requirements_exe.txt        ← Full dependencies with DL
│   └── .gitignore                  ← Git ignore rules
│
└── 📚 Documentation (13 guides)
    ├── README.md                   ← Main documentation
    ├── FAQ.md                      ← Frequently asked questions
    ├── REPOSITORY_CONTENTS.md      ← This file!
    │
    ├── Download Guides:
    │   ├── HOW_TO_DOWNLOAD.md      ← Complete download guide
    │   ├── DOWNLOAD_QUICK.md       ← Quick reference
    │   ├── DOWNLOAD_VISUAL.md      ← Visual guide
    │   └── DOWNLOAD_INDEX.md       ← Guide selector
    │
    ├── Build Guides:
    │   ├── START_HERE.md           ← Quick start
    │   ├── BUILD_LOCAL.md          ← Detailed build guide
    │   ├── BUILD_CHECKLIST.md      ← Verification steps
    │   └── QUICK_BUILD_GUIDE.md    ← Command reference
    │
    └── Reference Docs:
        ├── USER_GUIDE.md           ← End-user documentation
        ├── LUNG_ASP_IMPLEMENTATION.md    ← Technical details
        └── EXECUTABLE_IMPLEMENTATION.md  ← Build system details
```

---

## 📊 Package Comparison

| Feature | Breast-ASP | Lung-ASP | Combined |
|---------|------------|----------|----------|
| **Source Code** | 44 KB | 108 KB | 152 KB |
| **Modules** | 5 | 9 | 14 |
| **Radiomics Features** | 24 | 32 | 56 |
| **Unit Tests** | 6 | 8 | 14 |
| **Examples** | 5 | 5 | 10 |
| **Segmentation** | Threshold + RW | RW + Deep Learning | Both |
| **Exclusion Logic** | Axillary nodes | Mediastinum | Both |
| **DICOM Support** | - | ✅ Built-in | Via lung_asp |
| **Deep Learning** | - | TotalSeg + nnU-Net | Via lung_asp |
| **QC Visualization** | Basic | Advanced | Both |

**RW = Random Walker algorithm**

---

## 🎯 What You Get

### Breast Tumor Analysis System
**Location**: `src/breast_asp/`

**Capabilities**:
- ✅ FDG PET/CT breast tumor segmentation
- ✅ Axillary and axillary node exclusion
- ✅ 13 metabolic features (SUVmax, SUVmean, MTV, TLG, etc.)
- ✅ 12 shape features (volume, surface area, sphericity, etc.)
- ✅ Random walker refinement
- ✅ Automated pipeline

**Output**:
- Tumor mask (NIfTI)
- Radiomics features (CSV)
- Processing logs

---

### Lung Tumor Analysis System  
**Location**: `src/lung_asp/`

**Capabilities**:
- ✅ FDG PET/CT lung tumor segmentation
- ✅ Mediastinal exclusion
- ✅ DICOM to NIfTI conversion (geometry-preserving)
- ✅ Random walker + deep learning (TotalSegmentor, nnU-Net)
- ✅ 14 metabolic features (SUVmax, SUVmean, MTV at 41%, TLG, etc.)
- ✅ 13 shape features (sphericity, asphericity, max diameter, etc.)
- ✅ 6 advanced metrics (NHOCmax, NHOPmax, Dmax, gETU, etc.)
- ✅ Comprehensive QC visualizations (orthogonal planes)
- ✅ CT-based thoracic body mask
- ✅ Morphological post-processing
- ✅ Automated pipeline

**Output**:
- Tumor mask (NIfTI)
- Radiomics features (CSV)
- QC overlays (PNG)
- Processing logs

---

## 🚀 How to Use Both Systems

### Installation (One Time)
```bash
# Clone repository (gets BOTH systems)
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP

# Install package
pip install -e .
```

### Use Breast System
```python
from breast_asp import BreastTumorPipeline

# Create pipeline
pipeline = BreastTumorPipeline(
    suv_threshold=2.5,
    use_random_walker=True
)

# Process data
results = pipeline.process(
    pet_data=pet_array,
    ct_data=ct_array,
    voxel_size=(2.0, 2.0, 3.0)
)

# Get features
print(f"SUVmax: {results['metabolic']['suvmax']}")
print(f"Volume: {results['shape']['volume_ml']} mL")
```

### Use Lung System
```python
from lung_asp import LungTumorPipeline

# Create pipeline
pipeline = LungTumorPipeline(
    suv_threshold=2.5,
    mtv_threshold=41,  # 41% of SUVmax
    use_random_walker=True,
    generate_qc=True
)

# Process data (from DICOM)
results = pipeline.process_dicom(
    pet_dicom_dir='PET/',
    ct_dicom_dir='CT/',
    output_dir='results/'
)

# Get features
print(f"SUVmax: {results['metabolic']['suvmax']}")
print(f"Sphericity: {results['shape']['sphericity']}")
print(f"NHOCmax: {results['advanced']['nhoc_max']}")
```

### Build Executable (Lung System)
```bash
# Build standalone executable with all dependencies
./build_full.sh

# Run executable
./dist/lung_asp/lung_asp --help
./dist/lung_asp/lung_asp --pet-dicom PET/ --ct-dicom CT/ --output results/
```

---

## ✅ Verification After Cloning

To verify you have both systems:

```bash
# Check breast_asp is present
ls src/breast_asp/
# Expected: __init__.py  exclusion.py  pipeline.py  radiomics.py  segmentation.py ✅

# Check lung_asp is present
ls src/lung_asp/
# Expected: dicom_converter.py  lung_exclusion.py  lung_pipeline.py
#           lung_radiomics.py  lung_segmentation.py  nnunet_wrapper.py
#           qc_visualization.py  totalsegmentor_wrapper.py  __init__.py ✅

# Import both packages
python -c "from breast_asp import BreastTumorPipeline; print('Breast: OK')"
python -c "from lung_asp import LungTumorPipeline; print('Lung: OK')"

# Both should print "OK" ✅
```

---

## 💡 Why One Repository?

**Historical Context**:
- Started as "breast-ASP" (breast tumor with asphericity analysis)
- Extended to include lung tumors with advanced metrics
- Grew into comprehensive PET/CT analysis toolkit

**Benefits**:
- ✅ One download for complete toolkit
- ✅ Shared dependencies and infrastructure
- ✅ Consistent code quality and style
- ✅ Unified documentation
- ✅ Easy to compare implementations
- ✅ Complete medical imaging ecosystem

**Flexibility**:
- Use breast_asp alone
- Use lung_asp alone
- Use both together
- Build executable for distribution
- Extend with custom modules

---

## 🎓 Key Takeaways

### Question: "Will git clone include lung-ASP?"
### Answer: **YES! Absolutely! ✅**

**Facts**:
1. ✅ This is ONE repository containing BOTH systems
2. ✅ Cloning downloads the entire repository
3. ✅ The entire repository includes both `src/breast_asp/` and `src/lung_asp/`
4. ✅ Therefore, cloning gives you BOTH systems automatically
5. ✅ Nothing is separate or requires additional downloads

**Proof**:
```
git clone breast-ASP
    ↓
Downloads entire repo
    ↓
Repo contains src/breast_asp/ ✅
Repo contains src/lung_asp/ ✅
    ↓
You have BOTH systems! ✅✅✅
```

---

## 📚 Where to Go Next

**Just Downloaded?**
1. Read [README.md](README.md) - Overview and quick start
2. Read [FAQ.md](FAQ.md) - Common questions answered
3. Check examples in `examples/` directory

**Want to Use the Code?**
1. Install: `pip install -e .`
2. Try breast examples: `python examples/breast_examples/example_usage.py`
3. Try lung examples: `python examples/lung_examples/example_lung_usage.py`

**Want to Build Executable?**
1. Read [START_HERE.md](START_HERE.md) - Quick start guide
2. Read [BUILD_LOCAL.md](BUILD_LOCAL.md) - Detailed instructions
3. Run: `./build_full.sh`

**Need Help?**
1. Check [FAQ.md](FAQ.md) - Answers to common questions
2. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command reference
3. Check [USER_GUIDE.md](USER_GUIDE.md) - Complete user manual

---

## 🎉 Summary

**One Repository = Complete Package**

```
Repository Name: breast-ASP
Repository Contains:
  ├─ breast_asp package (5 modules, 24 features) ✅
  ├─ lung_asp package (9 modules, 32 features) ✅
  ├─ Examples (10 examples) ✅
  ├─ Tests (14 tests) ✅
  ├─ Build scripts ✅
  └─ Documentation (13 guides) ✅

Total: 14 modules, 56 features, complete toolkit

One clone = Everything! 🚀
```

---

**Last Updated**: February 2026  
**Repository**: https://github.com/nittinnm22-sudo/breast-ASP  
**License**: Check repository for license information
