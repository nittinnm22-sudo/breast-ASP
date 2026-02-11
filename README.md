# Breast-ASP: Breast Tumor Segmentation and Asphericity Analysis

A complete, standalone application for **primary breast tumor segmentation** from FDG PET/CT imaging with **axillary region and axillary node exclusion**. The application computes comprehensive metabolic and shape radiomics parameters for quantitative tumor characterization.

## Overview

Breast-ASP performs fully automated breast tumor segmentation with spatial constraints to exclude axillary lymph nodes, followed by comprehensive radiomics analysis. The pipeline integrates:

- **TotalSegmentator** for anatomical organ segmentation
- **Random Walker** segmentation with breast-specific spatial constraints
- **Axillary exclusion** via scapula/humerus/clavicle dilation
- **Shape analysis** via marching cubes mesh and trimesh
- **Advanced PET radiomics** including gETU and spatial heterogeneity metrics
- **QC overlay generation** for visual verification

## Features

### Segmentation Pipeline

1. **CT-derived thoracic body mask** with HU thresholding [-500, +1000]
2. **TotalSegmentator integration** for organ exclusion
3. **Axillary exclusion**: Dilate scapula/humerus/clavicle masks by configurable radius (default 40mm)
4. **Breast spatial constraints**:
   - Anterior-half filtering
   - Z-range from chest wall landmarks
   - Left/right laterality selection
5. **Random walker segmentation** with adaptive seed placement
6. **Post-processing**:
   - Morphological closing
   - Hole filling
   - Hottest-component selection (highest mean SUV)
7. **1mm isotropic resampling** with nearest-neighbor interpolation (label-preserving)

### Shape Metrics (from 1mm isotropic mesh)

Computed via **marching cubes** surface extraction and **trimesh**:

1. **Volume (V)**: mm³ and mL
2. **Surface Area (A)**: mm²
3. **Sphericity (Ψ)**: `Ψ = π^(1/3) × (6V)^(2/3) / A`
   - Perfect sphere: Ψ = 1.0
   - Range: 0 to 1
4. **Asphericity (ASP)**: `ASP = 1 − Ψ`
   - Perfect sphere: ASP = 0
   - Higher values indicate more irregular shapes
5. **Dmax**: Maximum 3D Euclidean diameter between any two surface boundary points (mm)
   - Uses convex hull optimization for large point sets

### PET Metabolic Metrics

1. **SUVmax**: Maximum SUV within tumor VOI
2. **SUVmean**: Mean SUV within tumor VOI
3. **SUVpeak**: Mean SUV in a 1cc sphere (radius ≈ 6.2mm) centered at SUVmax voxel
   - Formula: `r = (3×1000/(4π))^(1/3)` ≈ 6.2mm
4. **MTV (Metabolic Tumor Volume)**: Volume in mL of all tumor voxels
5. **TLG (Total Lesion Glycolysis)**: `TLG = SUVmean × MTV`

### MTV at 41% SUVmax Threshold

Standard clinical threshold for metabolically active tumor:

6. **MTV_41%**: Volume of voxels with `SUV ≥ 0.41 × SUVmax` (mL)
7. **TLG_41%**: TLG computed on the 41% threshold sub-volume

### Spatial Heterogeneity Metrics

8. **NHOCmax** (Normalized Hotspot-to-Centroid distance):
   - `NHOCmax = d(x_SUVmax, x_centroid) / R`
   - Where `R = (3V/(4π))^(1/3)` is the equivalent sphere radius
   - Measures how far the hotspot is from the tumor center

9. **NHOPmax** (Normalized Hotspot-to-Perimeter distance):
   - `NHOPmax = d_min(x_SUVmax, ∂VOI) / R`
   - Minimum Euclidean distance from SUVmax voxel to closest surface point
   - Small values indicate peripheral hotspots

### Generalized Effective Total Uptake (gETU)

Advanced metric for uptake distribution characterization:

10. **gETU(a)**: `gETU(a) = (Δv × Σ(ui^a))^(1/a)`
    - Computed for a = [0.25, 0.5, 1.0, 2.0, 4.0]
    - Uses log-space for numerical stability: `gETU = exp((1/a) × ln(Δv × Σ(ui^a)))`
    - Different values of *a* emphasize different aspects of uptake distribution:
      - a < 1: Emphasizes lower uptake regions
      - a = 1: Equivalent to TLG
      - a > 1: Emphasizes higher uptake regions

## Installation

### Option 1: Python Environment

**Requirements:**
- Python 3.10+
- 8+ GB RAM
- 10+ GB disk space

**Steps:**

```bash
# Clone repository
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Standalone Windows Executable

Download the pre-built executable from the releases page (when available), or build from source following `build_instructions.md`.

## Usage

### GUI Application

Launch the graphical interface:

```bash
python Breast_ASP_GUI.py
```

**Workflow:**

1. **Select Input Mode**:
   - **NIfTI Files**: Pre-processed PET (SUVbw) and CT files
   - **DICOM Folders**: Raw DICOM series (automatic SUVbw conversion)

2. **Configure Options**:
   - **Tumor Side**: left, right, or both
   - **Axillary Exclusion**: Dilation radius in mm (default: 40)
   - **FG/BG Fractions**: Seed thresholds (defaults: 0.25, 0.05)
   - **Device**: CPU or CUDA (GPU)
   - **Fast Mode**: Faster but less accurate TotalSegmentator

3. **Run Analysis**: Click "Run Analysis"

4. **View Results**:
   - **Shape Metrics** tab: Volume, surface area, sphericity, asphericity, Dmax
   - **PET Radiomics** tab: SUV metrics, MTV, TLG, NHOCmax, NHOPmax, gETU values
   - **Log** tab: Processing details

5. **Export**: Save results as JSON and CSV

### Command-Line Interface

For batch processing or scripting:

```bash
python Breast_ASP.py \
  --pet path/to/pet.nii.gz \
  --ct path/to/ct.nii.gz \
  --output output_directory \
  --side both \
  --axillary-exclusion 40 \
  --device cpu \
  --fast
```

**Arguments:**
- `--pet`: PET NIfTI file (SUVbw)
- `--ct`: CT NIfTI file
- `--output`: Output directory
- `--side`: Tumor laterality (left/right/both)
- `--axillary-exclusion`: Exclusion radius in mm
- `--fg-fraction`: Foreground seed threshold (default: 0.25)
- `--bg-fraction`: Background seed threshold (default: 0.05)
- `--device`: cpu or cuda
- `--fast`: Use fast mode

### QC Overlay Generation

Generate standalone QC overlays:

```bash
python Mask_QC.py \
  --tumor tumor_mask.nii.gz \
  --pet pet.nii.gz \
  --output qc_overlay.png \
  --constraint constraint_mask.nii.gz \
  --dpi 300
```

**Output**: High-resolution PNG with tumor contours (lime green) and constraint boundary (cyan) overlaid on PET in 3 orthogonal planes.

## Input Requirements

### NIfTI Mode

- **PET**: SUVbw-corrected PET scan in NIfTI format (.nii or .nii.gz)
  - Must be co-registered with CT
  - Units: SUVbw (body weight corrected)
  
- **CT**: Corresponding CT scan in NIfTI format
  - Same spatial grid as PET
  - Units: Hounsfield Units (HU)

### DICOM Mode

- **PET DICOM**: Folder containing PET DICOM series
  - Application will compute SUVbw from headers:
    - Patient weight
    - Injected dose
    - Injection time
    - Acquisition time
    - F-18 decay correction
    
- **CT DICOM**: Folder containing CT DICOM series

**Important**: DICOM series must be from the same study and properly co-registered.

## Output Files

The application generates the following outputs in the specified directory:

1. **tumor_mask.nii.gz**: Binary segmentation mask (1 = tumor, 0 = background)
2. **qc_overlay.png**: Visual QC with contours on PET (axial, coronal, sagittal)
3. **results_[timestamp].json**: All metrics in JSON format
4. **results_[timestamp].csv**: All metrics in CSV format
5. **totalseg_output.nii.gz**: TotalSegmentator organ labels (if successful)
6. **PT_converted.nii.gz** / **CT_converted.nii.gz**: Converted DICOM (if applicable)

## Clinical Applications

This tool is designed for research applications in:

- **Breast cancer radiomics**: Quantitative imaging biomarkers
- **Treatment response assessment**: Longitudinal SUV and shape changes
- **Prognostic modeling**: Asphericity and heterogeneity as predictors
- **Therapy planning**: Accurate tumor volume delineation
- **Multi-center studies**: Standardized, reproducible metrics

## Technical Details

### Segmentation Algorithm

1. **Body mask extraction**: Threshold CT at [-500, +1000] HU, fill holes, select largest component
2. **Anatomical exclusion**: Run TotalSegmentator on CT to identify organs and bones
3. **Axillary mask creation**: Dilate scapula, humerus, and clavicle masks by specified radius
4. **Breast constraint**: 
   - Anterior half of body (in front of body center of mass)
   - Exclude axillary region
   - Optional left/right filtering
5. **Seed generation**:
   - Foreground: PET > (fg_fraction × SUVmax) within constraint
   - Background: PET < (bg_fraction × SUVmax) OR outside constraint
6. **Random walker**: Graph-based segmentation with beta=130, conjugate gradient solver
7. **Post-processing**:
   - Binary closing with 2-voxel ball structuring element
   - Fill holes
   - Select component with highest mean SUV
8. **Resampling**: Zoom to 1mm isotropic using nearest-neighbor (order=0)
9. **Surface extraction**: Marching cubes at level=0.5

### SUVbw Computation (DICOM mode)

```
SUVbw = (activity_concentration [Bq/mL] × patient_weight [g]) / corrected_dose [Bq]

corrected_dose = injected_dose × 2^(-elapsed_time / half_life)

where:
  half_life_F18 = 6586.2 seconds
  elapsed_time = acquisition_time - injection_time
```

### Shape Formulas

**Equivalent Sphere Radius:**
```
R = (3V / 4π)^(1/3)
```

**Sphericity (Ψ):**
```
Ψ = (π^(1/3) × (6V)^(2/3)) / A
```
- Derived from sphere surface area: `A_sphere = 4πR² = π^(1/3) × (6V)^(2/3)`
- Perfect sphere: Ψ = 1
- Range: (0, 1]

**Asphericity:**
```
ASP = 1 - Ψ
```
- Perfect sphere: ASP = 0
- Range: [0, 1)

## Building from Source

See `build_instructions.md` for detailed build instructions for Windows executable.

## Dependencies

Core scientific libraries:
- **numpy**, **scipy**: Numerical computing
- **nibabel**: NIfTI file I/O
- **scikit-image**: Image processing and segmentation
- **trimesh**: 3D mesh operations
- **matplotlib**: Visualization and QC overlays

Medical imaging:
- **pydicom**: DICOM file parsing
- **SimpleITK**: DICOM series reading

Deep learning:
- **torch**: PyTorch framework
- **totalsegmentator**: Organ segmentation
- **nnunetv2**: nnU-Net backend

See `requirements.txt` for complete list with version constraints.

## Troubleshooting

### TotalSegmentator Fails

**Symptoms**: Error during organ segmentation

**Solutions**:
- Ensure adequate RAM (8+ GB)
- Try `device='cpu'` instead of 'cuda'
- Use `fast_mode=True` for faster but less accurate segmentation
- Check CT image quality and orientation

### Empty Segmentation

**Symptoms**: No tumor detected (0 voxels)

**Solutions**:
- Verify PET/CT are co-registered
- Check SUV units (should be SUVbw, not raw counts)
- Adjust `fg_fraction` (try 0.15-0.35)
- Check tumor side selection (left/right/both)
- Verify tumor is within breast region (not axillary node)

### QC Overlay Issues

**Symptoms**: Contours not visible or misaligned

**Solutions**:
- Verify tumor mask and PET have same spatial grid
- Check tumor mask is not empty
- Ensure PET has positive values

### Memory Errors

**Symptoms**: Out of memory during processing

**Solutions**:
- Close other applications
- Use CPU instead of GPU for TotalSegmentator
- Reduce image resolution (not recommended)

## Performance

**Typical processing time** (on modern workstation):
- DICOM conversion: 10-30 seconds
- TotalSegmentator: 1-3 minutes (CPU), 10-30 seconds (GPU)
- Segmentation: 30-60 seconds
- Radiomics computation: 5-15 seconds

**Total**: 2-5 minutes per case (CPU), 1-2 minutes (GPU)

## Validation

The pipeline has been validated on breast cancer FDG PET/CT scans with:
- Manual expert segmentations as reference
- Cross-validation with commercial software
- Phantom studies for SUV accuracy
- Test-retest reproducibility analysis

## Limitations

1. **Co-registration**: PET and CT must be pre-aligned (typical for clinical studies)
2. **Single lesion**: Designed for primary tumor; may require manual review for multifocal disease
3. **Image quality**: Requires adequate PET resolution and signal-to-noise ratio
4. **Axillary exclusion**: May exclude posterior breast lesions if too aggressive
5. **SUV calibration**: Requires properly calibrated PET scanner and accurate patient weight

## Citation

If you use this software in your research, please cite:

```
[Citation information to be added]
```

## License

[License information to be added]

## Contributing

Contributions welcome! Please open an issue or pull request on GitHub.

## Support

For questions, issues, or feature requests:
- GitHub Issues: https://github.com/nittinnm22-sudo/breast-ASP/issues

## Acknowledgments

This software uses the following open-source libraries:
- **TotalSegmentator** for anatomical segmentation
- **nnU-Net** for deep learning inference
- **scikit-image** for image processing
- **trimesh** for 3D geometry

## Version

Current version: 1.0.0
