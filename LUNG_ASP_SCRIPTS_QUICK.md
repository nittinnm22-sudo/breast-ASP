# 📝 Lung-ASP Python Scripts - Quick Reference

## All 14 Python Scripts

### 📦 Core Modules (src/lung_asp/)

1. **`__init__.py`** (31 lines) - Package initialization
2. **`dicom_converter.py`** (177 lines) - DICOM → NIfTI conversion
3. **`lung_exclusion.py`** (265 lines) - Mediastinal exclusion
4. **`lung_pipeline.py`** (231 lines) - End-to-end pipeline
5. **`lung_radiomics.py`** (621 lines) - 32 radiomics features
6. **`lung_segmentation.py`** (298 lines) - Tumor segmentation
7. **`nnunet_wrapper.py`** (252 lines) - nnU-Net integration
8. **`qc_visualization.py`** (297 lines) - Quality control visualizations
9. **`totalsegmentor_wrapper.py`** (201 lines) - TotalSegmentor integration

### 🖥️ CLI & Scripts

10. **`lung_asp_cli.py`** (244 lines) - Command-line interface
11. **`download_models.py`** (224 lines) - Model download utility
12. **`setup.py`** (40 lines) - Installation configuration

### 🏗️ Build Configs

13. **`lung_asp.spec`** - PyInstaller config (full version)
14. **`lung_asp_lite.spec`** - PyInstaller config (lite version)

---

## 📊 Quick Stats

- **Total Files**: 14
- **Total Lines**: 2,881
- **Total Features**: 32 radiomics features
- **Location**: `src/lung_asp/` + root directory

---

## 🔍 Find Scripts

### In Repository:
```bash
cd breast-ASP
ls src/lung_asp/*.py           # Core modules
ls lung_asp_cli.py             # CLI
ls download_models.py setup.py # Helpers
ls *.spec                      # Build configs
```

### On GitHub:
- https://github.com/nittinnm22-sudo/breast-ASP/tree/main/src/lung_asp
- https://github.com/nittinnm22-sudo/breast-ASP/blob/main/lung_asp_cli.py

---

## 🚀 Quick Usage

### Python:
```python
from lung_asp import LungTumorPipeline

pipeline = LungTumorPipeline()
results = pipeline.process(pet_data, ct_data, pet_affine, voxel_size)
```

### CLI:
```bash
python lung_asp_cli.py --pet-dicom PET/ --ct-dicom CT/ --output results/
```

### Build:
```bash
pyinstaller lung_asp.spec --clean
./dist/lung_asp/lung_asp --help
```

---

## 📚 More Details

See **LUNG_ASP_SCRIPTS.md** for:
- Detailed descriptions of each script
- Complete method listings
- Full usage examples
- Dependencies
- Feature breakdown

---

**All scripts are in the repository - ready to use!** ✅
