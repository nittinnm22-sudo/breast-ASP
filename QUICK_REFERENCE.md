# Lung-ASP Executable - Quick Reference

## 🚀 Quick Start

### For End Users (Running the Executable)

```bash
# Extract and run
tar -xzf lung_asp_v1.0.0.tar.gz
cd lung_asp
./lung_asp --pet-dicom /path/to/pet --ct-dicom /path/to/ct --output ./results
```

### For Developers (Building the Executable)

```bash
# Clone and build
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP
./build_exe.sh
```

## 📋 Command Quick Reference

### Basic Commands
```bash
# Help
lung_asp --help

# Process DICOM
lung_asp --pet-dicom PET_DIR --ct-dicom CT_DIR --output OUT_DIR

# Process NIfTI
lung_asp --pet-nifti pet.nii.gz --ct-nifti ct.nii.gz --output OUT_DIR
```

### Common Options
```bash
# Adjust SUV threshold
--suv-threshold 3.0

# Set minimum volume
--min-volume 200

# Disable random walker (faster)
--no-random-walker

# Skip QC generation
--no-qc

# Verbose output
--verbose
```

## 📁 Output Files

| File | Description |
|------|-------------|
| `tumor_mask.nii.gz` | Binary segmentation mask |
| `tumor_features.csv` | 32 radiomics features |
| `Mask_QC.png` | Quality control overlay |
| `QC_Report.png` | Comprehensive report |

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Models not found" | Run `download_models.py --download-totalseg` |
| "Out of memory" | Use `--no-qc` flag, close other apps |
| "Permission denied" | Run `chmod +x lung_asp` (Linux/macOS) |
| Slow processing | Use `--no-random-walker` flag |

## 📊 Features Extracted (32 total)

### Metabolic (14)
- SUVmax, SUVmean, SUVpeak
- MTV (41% threshold), TLG
- Percentiles, COV

### Shape (13)
- Volume, Surface Area
- Sphericity, Asphericity
- Max Diameter, Compactness

### Advanced (6)
- NHOCmax, NHOPmax
- Dmax, DmaxVox
- gETU

## 🛠️ Build Process

```bash
# 1. Install dependencies
pip install -r requirements_exe.txt

# 2. Download models
python download_models.py --download-totalseg

# 3. Build executable
pyinstaller lung_asp.spec

# 4. Package for distribution
zip -r lung_asp.zip dist/lung_asp/
```

## 📞 Support

- Issues: https://github.com/nittinnm22-sudo/breast-ASP/issues
- Documentation: BUILD_EXECUTABLE.md, USER_GUIDE.md
- Examples: See examples/ directory

## 💡 Tips

1. **Always use CT when available** - Improves mediastinal exclusion
2. **Check QC images** - Verify segmentation quality
3. **Adjust thresholds** - Fine-tune for your data
4. **Use verbose mode** - For troubleshooting
5. **Process locally** - No internet required

## 🔒 Privacy

✅ All processing is local
✅ No data sent externally
✅ Fully offline capable

---

**Version**: 1.0.0  
**License**: MIT  
**Repository**: https://github.com/nittinnm22-sudo/breast-ASP
