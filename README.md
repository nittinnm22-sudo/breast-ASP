# Breast-ASP: FDG PET/CT Breast Tumor Segmentation with Axillary Exclusion

A comprehensive Python package for FDG PET/CT primary breast tumor segmentation with automated axillary and axillary lymph node exclusion, enabling accurate metabolic and shape radiomics feature extraction.

## Features

### Core Functionality
- **Primary Breast Tumor Segmentation**: Automated segmentation of breast tumors from FDG PET/CT imaging using SUV thresholding and morphological operations
- **Axillary Region Exclusion**: Intelligent exclusion of axillary (armpit) regions and axillary lymph nodes based on:
  - Anatomical location (lateral and superior positioning)
  - SUV pattern analysis
  - Morphological characteristics
  - Volume and shape criteria
- **Metabolic Radiomics**: Comprehensive metabolic feature extraction including:
  - SUV statistics (max, mean, median, std, percentiles)
  - SUV peak calculation
  - Metabolic Tumor Volume (MTV)
  - Total Lesion Glycolysis (TLG)
  - Coefficient of variation
- **Shape Radiomics**: Detailed geometric feature extraction including:
  - Volume and surface area
  - Sphericity and compactness
  - Elongation and flatness
  - Maximum diameter
  - Solidity

## Installation

```bash
# Clone the repository
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- numpy >= 1.21.0
- scipy >= 1.7.0
- scikit-image >= 0.18.0
- SimpleITK >= 2.1.0
- pandas >= 1.3.0

## Quick Start

### Basic Usage with Pipeline

```python
from breast_asp.pipeline import BreastTumorPipeline
import numpy as np

# Load your PET and CT images (as numpy arrays with SUV values)
pet_image = ...  # 3D numpy array with SUV values
ct_image = ...   # 3D numpy array with HU values (optional)
spacing = (3.0, 2.0, 2.0)  # voxel spacing in mm (z, y, x)

# Initialize pipeline
pipeline = BreastTumorPipeline(
    suv_threshold=2.5,        # SUV threshold for segmentation
    min_volume_mm3=100.0,     # minimum tumor volume
    exclusion_margin_mm=20.0  # safety margin for exclusion
)

# Process images and extract features
results = pipeline.process(pet_image, ct_image, spacing)

# Access results
tumor_mask = results['tumor_mask']  # Final segmentation with exclusions
metabolic_features = results['metabolic_features']
shape_features = results['shape_features']

print(f"SUVmax: {metabolic_features['SUVmax']:.2f}")
print(f"MTV: {metabolic_features['MTV_ml']:.2f} mL")
print(f"TLG: {metabolic_features['TLG']:.2f}")
print(f"Volume: {shape_features['Volume_ml']:.2f} mL")
print(f"Sphericity: {shape_features['Sphericity']:.3f}")
```

### Individual Component Usage

```python
from breast_asp.segmentation import BreastTumorSegmenter
from breast_asp.exclusion import AxillaryExcluder
from breast_asp.radiomics import MetabolicRadiomics, ShapeRadiomics

# Step 1: Segment tumors
segmenter = BreastTumorSegmenter(suv_threshold=2.5, min_volume_mm3=100.0)
tumor_mask = segmenter.segment_primary_breast_region(pet_image, ct_image, spacing)

# Step 2: Exclude axillary regions
excluder = AxillaryExcluder(exclusion_margin_mm=20.0)
filtered_mask = excluder.apply_all_exclusions(tumor_mask, pet_image, ct_image, spacing)

# Step 3: Extract features
metabolic_extractor = MetabolicRadiomics()
shape_extractor = ShapeRadiomics()

metabolic_features = metabolic_extractor.extract_features(pet_image, filtered_mask, spacing)
shape_features = shape_extractor.extract_features(filtered_mask, spacing)
```

### Explicit Axillary Region Definition

```python
# Define explicit axillary bounding boxes (optional)
axillary_bbox = {
    'left': (z_min, z_max, y_min, y_max, x_min, x_max),
    'right': (z_min, z_max, y_min, y_max, x_min, x_max)
}

results = pipeline.process(pet_image, ct_image, spacing, axillary_bbox=axillary_bbox)
```

### Save Features to CSV

```python
output_path = "breast_tumor_features.csv"
results = pipeline.process_and_save_features(
    pet_image, output_path, ct_image, spacing
)
```

## Examples

Run the comprehensive example script:

```bash
python examples/example_usage.py
```

This demonstrates:
1. Basic pipeline usage
2. Individual component usage
3. Explicit axillary region exclusion
4. Saving features to CSV

## Module Overview

### `segmentation.py`
- **BreastTumorSegmenter**: Segments primary breast tumors from FDG PET/CT
  - SUV-based thresholding
  - Connected component analysis
  - Volume filtering
  - Optional CT-based breast region refinement

### `exclusion.py`
- **AxillaryExcluder**: Excludes axillary and lymph node regions
  - Location-based exclusion (lateral and superior regions)
  - SUV pattern-based lymph node identification
  - Explicit bounding box exclusion
  - Combined multi-method exclusion

### `radiomics.py`
- **MetabolicRadiomics**: Extracts metabolic features
  - SUV statistics (max, mean, median, std, percentiles, peak)
  - MTV (Metabolic Tumor Volume)
  - TLG (Total Lesion Glycolysis)
  - Coefficient of variation

- **ShapeRadiomics**: Extracts geometric features
  - Volume and surface area
  - Sphericity, compactness, solidity
  - Elongation, flatness
  - Maximum diameter
  - Bounding box properties

### `pipeline.py`
- **BreastTumorPipeline**: Complete end-to-end processing pipeline
  - Integrates segmentation, exclusion, and feature extraction
  - Handles the full workflow from images to radiomics features
  - Supports CSV export

## Extracted Features

### Metabolic Features (13 features)
- SUVmax, SUVmean, SUVstd, SUVmedian, SUVmin
- SUVp25, SUVp75, SUVp90, SUVpeak
- MTV_ml (Metabolic Tumor Volume in mL)
- TLG (Total Lesion Glycolysis)
- COV (Coefficient of Variation)
- n_voxels

### Shape Features (12 features)
- Volume_mm3, Volume_ml
- SurfaceArea_mm2
- Sphericity, Compactness1, Compactness2
- MaxDiameter_mm
- BoundingBoxVolume_mm3
- Elongation, Flatness
- Solidity
- n_voxels

## Clinical Application

This package is designed for:
- **Breast cancer FDG PET/CT analysis**: Quantitative tumor characterization
- **Treatment response assessment**: Serial measurements with consistent methodology
- **Research studies**: Standardized radiomics feature extraction
- **Clinical trials**: Reproducible quantitative imaging biomarkers

### Key Advantage: Axillary Exclusion
Axillary lymph nodes can confound primary breast tumor analysis. This package automatically:
1. Identifies and excludes axillary regions based on anatomical location
2. Filters out lymph nodes based on SUV patterns and morphology
3. Ensures radiomics features reflect only primary breast tumor characteristics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for research and educational purposes.

## Citation

If you use this package in your research, please cite:
```
Breast-ASP: FDG PET/CT Tumor Segmentation and Radiomics Analysis
https://github.com/nittinnm22-sudo/breast-ASP
```

## Contact

For questions or issues, please open an issue on GitHub.

## Acknowledgments

This package implements methods for breast and lung tumor segmentation and radiomics analysis with a focus on accurate primary tumor characterization through anatomical region exclusion.

---

# Lung-ASP: FDG PET/CT Lung Tumor Segmentation with Mediastinal Exclusion

## Overview

Comprehensive Python package for FDG PET/CT primary lung tumor segmentation with automated mediastinal exclusion and advanced radiomics feature extraction.

## Features

### Core Functionality
- **DICOM to NIfTI Conversion**: Automated conversion with geometry preservation using dicom2nifti
- **Lung Tumor Segmentation**: 
  - Random walker algorithm for accurate boundary detection
  - Threshold-based fallback method
  - CT-based thoracic body mask (HU -500 to +1000)
  - Morphological post-processing (closing, hole filling ≥500 voxels)
- **Mediastinal Exclusion**: Intelligent exclusion of central chest structures:
  - Location-based (central region identification)
  - CT anatomy-based filtering
  - Hilar lymph node detection
  - Multi-method combined approach

### Advanced Radiomics (32 Features)

#### Metabolic Features (14 metrics)
- SUV statistics: SUVmax, SUVmean, SUVmedian, SUVmin, SUVstd
- SUV percentiles: p25, p75, p90
- **SUVpeak**: Average SUV in 1 cm³ hottest sphere
- **MTV**: Metabolic Tumor Volume at 41% SUVmax threshold
- **TLG**: Total Lesion Glycolysis
- Coefficient of Variation (COV)

#### Shape Features (13 metrics)
- Volume (mm³ and mL)
- Surface area (mm²) via marching cubes
- **Sphericity (Ψ)**: π^(1/3) × (6V)^(2/3) / A
- **Asphericity (ASP)**: 1 - Ψ
- Compactness measures (2 variants)
- Maximum 3D diameter
- Elongation and flatness
- Solidity

#### Advanced Geometric & Uptake Metrics (6 metrics)
- **NHOCmax**: Normalized Hotspot-to-Centroid distance
  - `NHOCmax = d(SUVmax_location, centroid) / R`
  - R = equivalent-volume sphere radius
- **NHOPmax**: Normalized Hotspot-to-Perimeter distance
  - `NHOPmax = d_min(SUVmax_location, boundary) / R`
- **Dmax**: Intra-lesion maximum 3D diameter (Feret diameter)
- **DmaxVox**: Voxel-based maximum diameter
- **gETU**: Generalized Effective Total Uptake
  - `gETU(a) = (Δv × Σ(u_i^a))^(1/a)`
  - Flexible power parameter (a=1 gives TLG, a→∞ emphasizes SUVmax)

### Quality Control
- Orthogonal plane overlays (axial, sagittal, coronal)
- Comprehensive QC reports with metrics tables
- High-resolution output (300 DPI)
- 3D surface rendering support

## Installation

```bash
pip install -r requirements.txt
```

### Additional Dependencies
- nibabel >= 3.2.0
- dicom2nifti >= 2.4.0
- trimesh >= 3.20.0
- matplotlib >= 3.5.0
- pydicom >= 2.3.0

## Quick Start: Lung Tumor Analysis

### Basic Pipeline Usage

```python
from lung_asp.lung_pipeline import LungTumorPipeline
import numpy as np

# Load PET and CT images
pet_image = ...  # 3D numpy array with SUV values
ct_image = ...   # 3D CT image with HU values
spacing = (3.0, 2.5, 2.5)  # voxel spacing in mm (z, y, x)

# Initialize pipeline
pipeline = LungTumorPipeline(
    suv_threshold=2.5,           # SUV threshold
    min_volume_mm3=100.0,        # minimum tumor volume
    use_random_walker=True,       # use random walker algorithm
    mtv_threshold_percent=41,     # MTV threshold (% of SUVmax)
    isotropic_spacing=1.0,        # target spacing for surface analysis
    getu_a=1.0                    # gETU power parameter
)

# Process images
results = pipeline.process(pet_image, ct_image, spacing, generate_qc=True)

# Access all features
metabolic = results['metabolic_features']
shape = results['shape_features']
advanced = results['advanced_features']

print(f"SUVmax: {metabolic['SUVmax']:.2f}")
print(f"MTV (41%): {metabolic['MTV_ml']:.2f} mL")
print(f"TLG: {metabolic['TLG']:.2f}")
print(f"Sphericity: {shape['Sphericity']:.3f}")
print(f"Asphericity: {shape['Asphericity']:.3f}")
print(f"NHOCmax: {advanced['NHOCmax']:.4f}")
print(f"NHOPmax: {advanced['NHOPmax']:.4f}")
print(f"gETU: {advanced['gETU']:.2f}")
```

### Process from DICOM

```python
from lung_asp.lung_pipeline import LungTumorPipeline

pipeline = LungTumorPipeline()

# Convert DICOM to NIfTI and process
results = pipeline.process_from_dicom(
    pet_dicom_dir="/path/to/pet/dicoms",
    ct_dicom_dir="/path/to/ct/dicoms",
    output_dir="/path/to/output"
)
```

### Individual Components

```python
from lung_asp.lung_segmentation import LungTumorSegmenter
from lung_asp.lung_exclusion import MediastinalExcluder
from lung_asp.lung_radiomics import LungMetabolicRadiomics, LungShapeRadiomics, AdvancedMetrics

# Step 1: Segmentation
segmenter = LungTumorSegmenter(suv_threshold=2.5, use_random_walker=True)
tumor_mask = segmenter.segment(pet_image, ct_image, spacing)

# Step 2: Mediastinal exclusion
excluder = MediastinalExcluder()
filtered_mask = excluder.apply_all_exclusions(tumor_mask, pet_image, ct_image, spacing)

# Step 3: Extract features
metabolic_extractor = LungMetabolicRadiomics()
shape_extractor = LungShapeRadiomics(isotropic_spacing=1.0)
advanced_calculator = AdvancedMetrics()

metabolic_features = metabolic_extractor.extract_features(pet_image, filtered_mask, spacing)
shape_features = shape_extractor.extract_features(filtered_mask, spacing)
advanced_features = advanced_calculator.extract_all_advanced_metrics(filtered_mask, pet_image, spacing)
```

## Examples

### Breast Tumor Analysis
```bash
python examples/example_usage.py
```

### Lung Tumor Analysis
```bash
python examples/lung_examples/example_lung_usage.py
```

## Module Structure

### Breast ASP (`src/breast_asp/`)
- `segmentation.py`: Breast tumor segmentation
- `exclusion.py`: Axillary region exclusion
- `radiomics.py`: Metabolic and shape radiomics
- `pipeline.py`: End-to-end pipeline

### Lung ASP (`src/lung_asp/`)
- `dicom_converter.py`: DICOM to NIfTI conversion
- `lung_segmentation.py`: Lung tumor segmentation with random walker
- `lung_exclusion.py`: Mediastinal region exclusion
- `lung_radiomics.py`: Comprehensive radiomics (metabolic, shape, advanced)
- `qc_visualization.py`: Quality control visualizations
- `lung_pipeline.py`: End-to-end pipeline

## Clinical Applications

- **Breast Cancer**: Quantitative primary tumor characterization excluding axillary lymph nodes
- **Lung Cancer**: Peripheral tumor analysis excluding mediastinal and hilar structures
- **Treatment Response**: Serial measurements with consistent methodology
- **Research Studies**: Standardized radiomics feature extraction
- **Clinical Trials**: Reproducible quantitative imaging biomarkers

## Key Advantages

1. **Anatomical Exclusion**: Automated filtering of confounding structures (axillary/mediastinal)
2. **Advanced Metrics**: Beyond standard radiomics (NHOCmax, NHOPmax, gETU, etc.)
3. **Geometry Preservation**: Proper handling of DICOM/NIfTI spatial information
4. **Quality Control**: Automated visualization for validation
5. **Modular Design**: Use individual components or complete pipelines
