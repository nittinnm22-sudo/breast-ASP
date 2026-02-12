# Lung-ASP Executable - User Guide

## Quick Start

### Running the Application

1. **Extract the Package**
   ```bash
   # Linux/macOS
   tar -xzf lung_asp_v1.0.0.tar.gz
   cd lung_asp
   
   # Windows
   # Extract using Windows Explorer or 7-Zip
   # Navigate to the lung_asp folder
   ```

2. **Run the Application**
   ```bash
   # Linux/macOS
   ./lung_asp --help
   
   # Windows
   lung_asp.exe --help
   ```

### Basic Usage

#### Process DICOM Files
```bash
lung_asp --pet-dicom /path/to/pet/folder --ct-dicom /path/to/ct/folder --output /path/to/results
```

#### Process NIfTI Files
```bash
lung_asp --pet-nifti pet_scan.nii.gz --ct-nifti ct_scan.nii.gz --output /path/to/results
```

## Command-Line Options

### Required Arguments
- `--pet-dicom PATH` - Directory containing PET DICOM files
- `--pet-nifti PATH` - Path to PET NIfTI file
- `--output PATH` or `-o PATH` - Output directory for results

### Optional Arguments
- `--ct-dicom PATH` - Directory containing CT DICOM files (optional but recommended)
- `--ct-nifti PATH` - Path to CT NIfTI file (optional but recommended)
- `--suv-threshold FLOAT` - SUV threshold for segmentation (default: 2.5)
- `--min-volume FLOAT` - Minimum tumor volume in mm³ (default: 100)
- `--mtv-threshold INT` - MTV threshold as % of SUVmax (default: 41)
- `--getu-a FLOAT` - gETU power parameter (default: 1.0)
- `--no-random-walker` - Use threshold-based segmentation only (faster)
- `--no-qc` - Skip QC visualization generation
- `--verbose` or `-v` - Show detailed processing information
- `--version` - Show version information

## Output Files

After processing, you will find these files in the output directory:

1. **tumor_mask.nii.gz** - Binary segmentation mask of the detected tumor
2. **tumor_features.csv** - Complete radiomics features (32 metrics)
3. **Mask_QC.png** - Quality control overlay showing segmentation on PET
4. **QC_Report.png** - Comprehensive report with all metrics
5. **PET_converted.nii.gz** - Converted PET image (if input was DICOM)
6. **CT_converted.nii.gz** - Converted CT image (if input was DICOM)

## Understanding the Results

### Radiomics Features (32 total)

#### Metabolic Features (14)
- **SUVmax** - Maximum SUV in tumor
- **SUVmean** - Average SUV  
- **SUVpeak** - Average SUV in 1 cm³ hottest sphere
- **MTV** - Metabolic Tumor Volume at 41% SUVmax
- **TLG** - Total Lesion Glycolysis (MTV × SUVmean)
- Plus: SUVstd, SUVmedian, SUVmin, percentiles, COV

#### Shape Features (13)
- **Volume** - Tumor volume in mm³ and mL
- **Surface Area** - Tumor surface area in mm²
- **Sphericity (Ψ)** - How spherical the tumor is (0-1)
- **Asphericity (ASP)** - Deviation from sphere (0-1)
- **Max Diameter** - Maximum 3D diameter
- Plus: Compactness, Elongation, Flatness, Solidity

#### Advanced Metrics (6)
- **NHOCmax** - Normalized hotspot-to-centroid distance
- **NHOPmax** - Normalized hotspot-to-perimeter distance
- **Dmax** - Maximum 3D diameter (Feret)
- **DmaxVox** - Voxel-based maximum diameter
- **gETU** - Generalized effective total uptake

## Examples

### Example 1: Basic Processing
```bash
lung_asp --pet-dicom ./patient_001/PET --ct-dicom ./patient_001/CT --output ./results/patient_001
```

### Example 2: Adjust Segmentation Threshold
```bash
lung_asp --pet-nifti pet.nii.gz --ct-nifti ct.nii.gz --suv-threshold 3.0 --output ./results
```

### Example 3: Fast Processing (No Random Walker)
```bash
lung_asp --pet-nifti pet.nii.gz --no-random-walker --no-qc --output ./results
```

### Example 4: Verbose Output
```bash
lung_asp --pet-dicom ./PET --ct-dicom ./CT --output ./results --verbose
```

## Troubleshooting

### Common Issues

**Problem**: "No module named 'numpy'" or similar errors
- **Cause**: Executable is corrupted or incomplete
- **Solution**: Re-extract the package from archive

**Problem**: "Models not found" error
- **Cause**: Pre-trained models are missing
- **Solution**: Models should be bundled with the executable. If not, contact support.

**Problem**: "Out of memory" error
- **Cause**: Insufficient RAM for processing
- **Solution**: 
  - Close other applications
  - Use `--no-qc` flag to reduce memory usage
  - Process smaller regions if possible

**Problem**: Slow processing
- **Cause**: CPU-only processing or large images
- **Solution**:
  - Use `--no-random-walker` for faster segmentation
  - Ensure GPU drivers are installed (if available)
  - Use a machine with more CPU cores

**Problem**: "Permission denied" (Linux/macOS)
- **Cause**: Executable doesn't have execute permission
- **Solution**: Run `chmod +x lung_asp`

**Problem**: Windows Defender blocks the executable
- **Cause**: Unsigned executable triggers security warnings
- **Solution**: 
  - Click "More info" and "Run anyway"
  - Or add to Windows Defender exceptions

### Getting Help

For additional help:
1. Run with `--verbose` flag to see detailed error messages
2. Check the log files in the output directory
3. Report issues at: https://github.com/nittinnm22-sudo/breast-ASP/issues

## System Requirements

### Minimum
- **CPU**: 4 cores, 2.5 GHz
- **RAM**: 8 GB
- **Storage**: 5 GB (including models)
- **OS**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+

### Recommended
- **CPU**: 8+ cores, 3.0+ GHz
- **RAM**: 16+ GB
- **GPU**: NVIDIA with 6+ GB VRAM (for faster processing)
- **Storage**: 20+ GB (SSD preferred)
- **OS**: Latest stable version

## Tips for Best Results

1. **Use Both PET and CT**: CT helps with anatomical localization and mediastinal exclusion
2. **Check Input Quality**: Ensure DICOM/NIfTI files are not corrupted
3. **Review QC Images**: Always check the quality control overlays to verify segmentation
4. **Adjust Thresholds**: If segmentation is too aggressive or conservative, adjust `--suv-threshold`
5. **Use Verbose Mode**: For troubleshooting, run with `--verbose` flag

## Data Privacy

This application processes data **locally** on your machine. No data is sent to external servers.

## Citation

If you use this software in your research, please cite:
```
Lung-ASP: FDG PET/CT Lung Tumor Segmentation and Radiomics Analysis
https://github.com/nittinnm22-sudo/breast-ASP
Version 1.0.0
```

## License

See LICENSE file for terms of use.

## Version

Current version: 1.0.0
Release date: 2024

---

For developers interested in the source code or contributing, visit:
https://github.com/nittinnm22-sudo/breast-ASP
