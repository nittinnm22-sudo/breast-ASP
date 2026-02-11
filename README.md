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
- pyradiomics >= 3.0.1
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
Breast-ASP: FDG PET/CT Breast Tumor Segmentation with Axillary Exclusion
https://github.com/nittinnm22-sudo/breast-ASP
```

## Contact

For questions or issues, please open an issue on GitHub.

## Acknowledgments

This package implements methods for breast tumor segmentation and radiomics analysis with a focus on accurate primary tumor characterization through axillary region exclusion.
