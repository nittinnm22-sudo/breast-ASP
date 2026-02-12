# Complete Python Source Code for Lung-ASP
This document contains the **complete source code** for all 9 Python scripts in the lung_asp package.
**Total**: 2,373 lines of Python code across 9 files

---

## Table of Contents

1. [__init__.py](#1---init--py) (31 lines)
2. [dicom_converter.py](#2-dicom-converterpy) (177 lines)
3. [lung_exclusion.py](#3-lung-exclusionpy) (265 lines)
4. [lung_pipeline.py](#4-lung-pipelinepy) (231 lines)
5. [lung_radiomics.py](#5-lung-radiomicspy) (621 lines)
6. [lung_segmentation.py](#6-lung-segmentationpy) (298 lines)
7. [nnunet_wrapper.py](#7-nnunet-wrapperpy) (252 lines)
8. [qc_visualization.py](#8-qc-visualizationpy) (297 lines)
9. [totalsegmentor_wrapper.py](#9-totalsegmentor-wrapperpy) (201 lines)

---

## 1. __init__.py

**Lines**: 31
**Location**: `src/lung_asp/__init__.py`

```python
"""
Lung Tumor Segmentation Package for FDG PET/CT Imaging

This package provides tools for:
- DICOM to NIfTI conversion with geometry preservation
- Primary lung tumor segmentation using random walker algorithm
- Mediastinal region exclusion
- Advanced metabolic and shape radiomics feature extraction
- Quality control visualization
"""

__version__ = "1.0.0"
__author__ = "Lung ASP Project"

from .dicom_converter import DICOMConverter
from .lung_segmentation import LungTumorSegmenter
from .lung_exclusion import MediastinalExcluder
from .lung_radiomics import LungMetabolicRadiomics, LungShapeRadiomics, AdvancedMetrics
from .lung_pipeline import LungTumorPipeline
from .qc_visualization import QCVisualizer

__all__ = [
    'DICOMConverter',
    'LungTumorSegmenter',
    'MediastinalExcluder',
    'LungMetabolicRadiomics',
    'LungShapeRadiomics',
    'AdvancedMetrics',
    'LungTumorPipeline',
    'QCVisualizer'
]

```

---

## 2. dicom_converter.py

**Lines**: 177
**Location**: `src/lung_asp/dicom_converter.py`

```python
"""
DICOM to NIfTI Conversion Module

This module handles conversion of DICOM PET/CT images to NIfTI format
with preservation of image orientation and voxel geometry.
"""

import os
import numpy as np
import nibabel as nib
import dicom2nifti
import pydicom
from pathlib import Path


class DICOMConverter:
    """
    Converts DICOM PET/CT images to NIfTI format with geometry preservation.
    """
    
    def __init__(self, output_dir=None):
        """
        Initialize the DICOM converter.
        
        Args:
            output_dir (str): Directory to save converted NIfTI files
        """
        self.output_dir = output_dir or os.getcwd()
        os.makedirs(self.output_dir, exist_ok=True)
        
    def convert_dicom_to_nifti(self, dicom_dir, output_filename="PET_converted.nii.gz",
                               modality="PT"):
        """
        Convert DICOM series to NIfTI format.
        
        Args:
            dicom_dir (str): Directory containing DICOM files
            output_filename (str): Output NIfTI filename
            modality (str): Modality to convert ("PT" for PET, "CT" for CT)
            
        Returns:
            str: Path to converted NIfTI file
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # Use dicom2nifti for conversion with geometry preservation
            dicom2nifti.convert_directory(
                dicom_dir, 
                self.output_dir,
                compression=True,
                reorient=False  # Preserve original orientation
            )
            
            # Rename to desired filename if needed
            nifti_files = list(Path(self.output_dir).glob("*.nii.gz"))
            if nifti_files and not os.path.exists(output_path):
                os.rename(str(nifti_files[0]), output_path)
                
        except Exception as e:
            print(f"Warning: dicom2nifti failed, using fallback method: {e}")
            self._convert_dicom_fallback(dicom_dir, output_path, modality)
        
        return output_path
    
    def _convert_dicom_fallback(self, dicom_dir, output_path, modality="PT"):
        """
        Fallback DICOM to NIfTI conversion using pydicom and nibabel.
        
        Args:
            dicom_dir (str): Directory containing DICOM files
            output_path (str): Output NIfTI file path
            modality (str): Modality to convert
        """
        # Read all DICOM files
        dicom_files = sorted([
            os.path.join(dicom_dir, f) for f in os.listdir(dicom_dir)
            if f.endswith('.dcm') or not f.startswith('.')
        ])
        
        if not dicom_files:
            raise ValueError(f"No DICOM files found in {dicom_dir}")
        
        # Read first slice to get metadata
        first_slice = pydicom.dcmread(dicom_files[0])
        
        # Filter by modality if multiple modalities present
        if hasattr(first_slice, 'Modality'):
            dicom_files = [
                f for f in dicom_files
                if pydicom.dcmread(f, stop_before_pixels=True).Modality == modality
            ]
        
        # Sort by instance number or slice location
        slices = []
        for dcm_file in dicom_files:
            ds = pydicom.dcmread(dcm_file)
            slices.append(ds)
        
        # Sort slices
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        
        # Create 3D volume
        img_shape = (slices[0].Rows, slices[0].Columns, len(slices))
        volume = np.zeros(img_shape, dtype=np.float32)
        
        for i, dcm_slice in enumerate(slices):
            volume[:, :, i] = dcm_slice.pixel_array.astype(np.float32)
            
            # Apply rescale slope and intercept if present
            if hasattr(dcm_slice, 'RescaleSlope'):
                volume[:, :, i] = volume[:, :, i] * dcm_slice.RescaleSlope
            if hasattr(dcm_slice, 'RescaleIntercept'):
                volume[:, :, i] = volume[:, :, i] + dcm_slice.RescaleIntercept
        
        # Get voxel spacing
        pixel_spacing = slices[0].PixelSpacing
        slice_thickness = float(slices[0].SliceThickness) if hasattr(slices[0], 'SliceThickness') else 1.0
        
        # Calculate slice spacing from positions if available
        if len(slices) > 1:
            pos1 = np.array(slices[0].ImagePositionPatient)
            pos2 = np.array(slices[1].ImagePositionPatient)
            slice_spacing = np.linalg.norm(pos2 - pos1)
        else:
            slice_spacing = slice_thickness
        
        # Create affine matrix
        spacing = [float(pixel_spacing[0]), float(pixel_spacing[1]), slice_spacing]
        affine = np.diag([spacing[0], spacing[1], spacing[2], 1.0])
        
        # Get image position for proper origin
        if hasattr(slices[0], 'ImagePositionPatient'):
            origin = slices[0].ImagePositionPatient
            affine[0, 3] = origin[0]
            affine[1, 3] = origin[1]
            affine[2, 3] = origin[2]
        
        # Create NIfTI image
        nifti_img = nib.Nifti1Image(volume, affine)
        
        # Save
        nib.save(nifti_img, output_path)
        print(f"Converted DICOM to NIfTI: {output_path}")
        print(f"  Shape: {volume.shape}")
        print(f"  Spacing: {spacing}")
    
    def load_nifti(self, nifti_path):
        """
        Load NIfTI file and return image data and metadata.
        
        Args:
            nifti_path (str): Path to NIfTI file
            
        Returns:
            tuple: (image_data, affine, spacing)
        """
        nifti_img = nib.load(nifti_path)
        image_data = nifti_img.get_fdata()
        affine = nifti_img.affine
        
        # Extract spacing from affine
        spacing = np.sqrt(np.sum(affine[:3, :3]**2, axis=0))
        
        return image_data, affine, spacing
    
    def save_nifti(self, image_data, affine, output_path):
        """
        Save image data as NIfTI file.
        
        Args:
            image_data (np.ndarray): Image data
            affine (np.ndarray): Affine transformation matrix
            output_path (str): Output file path
        """
        nifti_img = nib.Nifti1Image(image_data, affine)
        nib.save(nifti_img, output_path)

```

---

## 3. lung_exclusion.py

**Lines**: 265
**Location**: `src/lung_asp/lung_exclusion.py`

```python
"""
Mediastinal Exclusion Module

This module provides functionality for excluding mediastinal regions
from lung tumor segmentation masks to ensure only peripheral lung tumors
are analyzed.
"""

import numpy as np
from scipy import ndimage
from skimage import measure, morphology


class MediastinalExcluder:
    """
    Excludes mediastinal regions from tumor segmentation.
    
    The mediastinal region is the central chest area containing the heart,
    great vessels, and lymph nodes that should be excluded from peripheral
    lung tumor analysis.
    """
    
    def __init__(self, exclusion_margin_mm=20.0):
        """
        Initialize the mediastinal excluder.
        
        Args:
            exclusion_margin_mm (float): Safety margin around excluded regions in mm
        """
        self.exclusion_margin_mm = exclusion_margin_mm
        
    def exclude_mediastinal_regions(self, tumor_mask, pet_image, ct_image=None,
                                    spacing=(1.0, 1.0, 1.0)):
        """
        Exclude mediastinal regions from tumor mask.
        
        This method identifies and removes mediastinal regions based on:
        1. Anatomical location (central chest region)
        2. CT characteristics if available
        3. SUV patterns typical of mediastinal structures
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            pet_image (np.ndarray): 3D PET image array with SUV values
            ct_image (np.ndarray): Optional 3D CT image for anatomical reference
            spacing (tuple): Voxel spacing in mm (z, y, x)
            
        Returns:
            np.ndarray: Tumor mask with mediastinal regions excluded
        """
        if not np.any(tumor_mask):
            return tumor_mask
            
        # Create working copy
        filtered_mask = tumor_mask.copy()
        
        # Label connected components
        labeled_mask = measure.label(tumor_mask, connectivity=3)
        regions = measure.regionprops(labeled_mask)
        
        # Calculate image dimensions and reference points
        nz, ny, nx = tumor_mask.shape
        center_x = nx // 2
        center_y = ny // 2
        
        # Define mediastinal region (central chest)
        # Typically within 30% of center in x-direction
        mediastinal_x_range = int(nx * 0.3)
        
        # Identify and remove mediastinal regions
        for region in regions:
            centroid_z, centroid_y, centroid_x = region.centroid
            
            # Mediastinal regions are typically:
            # 1. Central (near midline in x)
            # 2. Middle to posterior in y
            # 3. Middle thorax in z
            
            distance_from_center_x = abs(centroid_x - center_x)
            is_central = distance_from_center_x < mediastinal_x_range
            
            # Check if in mediastinal y-range (middle to posterior)
            is_mediastinal_y = centroid_y > ny * 0.3 and centroid_y < ny * 0.8
            
            # Check z-range (mid thorax)
            is_mediastinal_z = centroid_z > nz * 0.2 and centroid_z < nz * 0.7
            
            # Calculate region characteristics
            volume_mm3 = region.area * np.prod(spacing)
            
            # Mediastinal structures typically have:
            # - Central location
            # - Variable size
            # - May have high SUV (lymph nodes, vessels)
            
            if is_central and is_mediastinal_y and is_mediastinal_z:
                # Additional check: peripheral lung tumors are usually
                # more lateral than mediastinal structures
                if distance_from_center_x < nx * 0.2:  # Very central
                    filtered_mask[labeled_mask == region.label] = 0
        
        return filtered_mask
    
    def exclude_by_ct_anatomy(self, tumor_mask, ct_image, spacing=(1.0, 1.0, 1.0)):
        """
        Exclude mediastinal regions using CT anatomical information.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            ct_image (np.ndarray): 3D CT image with HU values
            spacing (tuple): Voxel spacing in mm
            
        Returns:
            np.ndarray: Tumor mask with CT-based mediastinal exclusion
        """
        if ct_image is None:
            return tumor_mask
            
        filtered_mask = tumor_mask.copy()
        
        # Create mediastinal mask based on CT characteristics
        # Mediastinum contains soft tissue (0-100 HU), vessels (30-70 HU)
        # and some fat (-100 to -50 HU)
        
        # Simple approach: identify central high-density structures
        mediastinal_region = (ct_image > -50) & (ct_image < 150)
        
        # Focus on central region
        nz, ny, nx = ct_image.shape
        center_x = nx // 2
        x_margin = int(nx * 0.25)
        
        # Create central region mask
        central_mask = np.zeros_like(mediastinal_region)
        central_mask[:, :, (center_x - x_margin):(center_x + x_margin)] = True
        
        mediastinal_region = mediastinal_region & central_mask
        
        # Morphological operations to clean up
        try:
            struct_elem = morphology.ball(3)
            mediastinal_region = morphology.closing(mediastinal_region, 
                                                   struct_elem)
        except (ValueError, MemoryError):
            mediastinal_region = morphology.closing(mediastinal_region,
                                                   morphology.ball(1))
        
        # Exclude regions overlapping with mediastinum
        filtered_mask = filtered_mask & (~mediastinal_region)
        
        return filtered_mask
    
    def exclude_by_location(self, tumor_mask, mediastinal_bbox=None):
        """
        Exclude regions based on explicit mediastinal bounding box.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            mediastinal_bbox (tuple): Bounding box (z_min, z_max, y_min, y_max, x_min, x_max)
            
        Returns:
            np.ndarray: Tumor mask with specified region excluded
        """
        if mediastinal_bbox is None:
            return tumor_mask
            
        filtered_mask = tumor_mask.copy()
        z_min, z_max, y_min, y_max, x_min, x_max = mediastinal_bbox
        
        # Zero out mediastinal region
        filtered_mask[z_min:z_max, y_min:y_max, x_min:x_max] = 0
        
        return filtered_mask
    
    def exclude_hilar_regions(self, tumor_mask, pet_image, ct_image=None,
                             spacing=(1.0, 1.0, 1.0)):
        """
        Exclude hilar (lung root) regions which may contain lymph nodes.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            pet_image (np.ndarray): 3D PET image
            ct_image (np.ndarray): Optional 3D CT image
            spacing (tuple): Voxel spacing
            
        Returns:
            np.ndarray: Tumor mask with hilar regions excluded
        """
        if not np.any(tumor_mask):
            return tumor_mask
            
        filtered_mask = tumor_mask.copy()
        labeled_mask = measure.label(tumor_mask, connectivity=3)
        regions = measure.regionprops(labeled_mask, intensity_image=pet_image)
        
        nz, ny, nx = tumor_mask.shape
        center_x = nx // 2
        
        for region in regions:
            centroid_z, centroid_y, centroid_x = region.centroid
            
            # Hilar regions are:
            # - Para-mediastinal (near center but not at center)
            # - Middle to posterior in y
            # - Middle thorax in z
            # - Often have moderate to high SUV
            
            distance_from_center_x = abs(centroid_x - center_x)
            is_paramediastinal = (distance_from_center_x > nx * 0.15 and 
                                 distance_from_center_x < nx * 0.35)
            
            is_hilar_y = centroid_y > ny * 0.35 and centroid_y < ny * 0.75
            is_hilar_z = centroid_z > nz * 0.25 and centroid_z < nz * 0.65
            
            volume_mm3 = region.area * np.prod(spacing)
            is_small_to_medium = volume_mm3 < 10000  # Less than 10 cm³
            
            # Hilar lymph nodes typically have:
            # - Small to medium volume
            # - Para-mediastinal location
            # - Moderate SUV
            suv_max = region.intensity_max
            suv_mean = region.intensity_mean
            is_moderate_uptake = suv_max < 15.0 and suv_mean > 2.0
            
            if (is_paramediastinal and is_hilar_y and is_hilar_z and 
                is_small_to_medium and is_moderate_uptake):
                # Likely hilar lymph node, exclude
                filtered_mask[labeled_mask == region.label] = 0
        
        return filtered_mask
    
    def apply_all_exclusions(self, tumor_mask, pet_image, ct_image=None,
                            spacing=(1.0, 1.0, 1.0), mediastinal_bbox=None):
        """
        Apply all mediastinal exclusion methods.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            pet_image (np.ndarray): 3D PET image array with SUV values
            ct_image (np.ndarray): Optional 3D CT image
            spacing (tuple): Voxel spacing in mm (z, y, x)
            mediastinal_bbox (tuple): Optional explicit mediastinal bounding box
            
        Returns:
            np.ndarray: Tumor mask with all mediastinal regions excluded
        """
        # Apply location-based exclusion
        filtered_mask = self.exclude_mediastinal_regions(tumor_mask, pet_image, 
                                                         ct_image, spacing)
        
        # Apply CT-based exclusion if available
        if ct_image is not None:
            filtered_mask = self.exclude_by_ct_anatomy(filtered_mask, ct_image, 
                                                       spacing)
        
        # Apply hilar exclusion
        filtered_mask = self.exclude_hilar_regions(filtered_mask, pet_image, 
                                                   ct_image, spacing)
        
        # Apply explicit bounding box exclusion if provided
        if mediastinal_bbox is not None:
            filtered_mask = self.exclude_by_location(filtered_mask, mediastinal_bbox)
            
        return filtered_mask

```

---

## 4. lung_pipeline.py

**Lines**: 231
**Location**: `src/lung_asp/lung_pipeline.py`

```python
"""
Lung Tumor Analysis Pipeline

This module provides a complete pipeline for FDG PET/CT lung tumor analysis
with mediastinal exclusion and comprehensive radiomics.
"""

import numpy as np
import os
from .dicom_converter import DICOMConverter
from .lung_segmentation import LungTumorSegmenter
from .lung_exclusion import MediastinalExcluder
from .lung_radiomics import LungMetabolicRadiomics, LungShapeRadiomics, AdvancedMetrics
from .qc_visualization import QCVisualizer


class LungTumorPipeline:
    """
    Complete pipeline for lung tumor segmentation and radiomics analysis
    with mediastinal exclusion.
    """
    
    def __init__(self, suv_threshold=2.5, min_volume_mm3=100.0,
                 use_random_walker=True, mtv_threshold_percent=41,
                 isotropic_spacing=1.0, getu_a=1.0):
        """
        Initialize the pipeline.
        
        Args:
            suv_threshold (float): SUV threshold for tumor segmentation
            min_volume_mm3 (float): Minimum tumor volume in mm³
            use_random_walker (bool): Use random walker algorithm
            mtv_threshold_percent (int): MTV threshold as % of SUVmax
            isotropic_spacing (float): Target spacing for surface analysis (mm)
            getu_a (float): gETU power parameter
        """
        self.converter = DICOMConverter()
        self.segmenter = LungTumorSegmenter(suv_threshold, min_volume_mm3, 
                                           use_random_walker)
        self.excluder = MediastinalExcluder()
        self.metabolic_extractor = LungMetabolicRadiomics()
        self.shape_extractor = LungShapeRadiomics(isotropic_spacing)
        self.advanced_metrics = AdvancedMetrics()
        self.qc_visualizer = QCVisualizer()
        self.mtv_threshold_percent = mtv_threshold_percent
        self.getu_a = getu_a
        
    def process_from_dicom(self, pet_dicom_dir, ct_dicom_dir=None, 
                          output_dir=None, seed_point=None):
        """
        Process from DICOM files.
        
        Args:
            pet_dicom_dir (str): Directory containing PET DICOM files
            ct_dicom_dir (str): Optional directory containing CT DICOM files
            output_dir (str): Output directory for results
            seed_point (tuple): Optional seed point for segmentation
            
        Returns:
            dict: Complete results
        """
        if output_dir:
            self.converter.output_dir = output_dir
            self.qc_visualizer.output_dir = output_dir
        
        # Convert DICOM to NIfTI
        print("Converting PET DICOM to NIfTI...")
        pet_nifti_path = self.converter.convert_dicom_to_nifti(
            pet_dicom_dir, "PET_converted.nii.gz", modality="PT"
        )
        
        # Load PET
        pet_image, pet_affine, pet_spacing = self.converter.load_nifti(pet_nifti_path)
        
        # Convert CT if provided
        ct_image = None
        ct_spacing = None
        if ct_dicom_dir:
            print("Converting CT DICOM to NIfTI...")
            ct_nifti_path = self.converter.convert_dicom_to_nifti(
                ct_dicom_dir, "CT_converted.nii.gz", modality="CT"
            )
            ct_image, _, ct_spacing = self.converter.load_nifti(ct_nifti_path)
        
        # Process
        return self.process(pet_image, ct_image, pet_spacing, seed_point)
    
    def process(self, pet_image, ct_image=None, spacing=(1.0, 1.0, 1.0),
                seed_point=None, mediastinal_bbox=None, generate_qc=True):
        """
        Process PET/CT images to segment lung tumors and extract radiomics.
        
        This method:
        1. Segments primary lung tumors from PET image
        2. Excludes mediastinal regions
        3. Extracts metabolic radiomics features
        4. Extracts shape radiomics features
        5. Calculates advanced metrics
        6. Generates QC visualizations
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            ct_image (np.ndarray): Optional 3D CT image
            spacing (tuple): Voxel spacing in mm (z, y, x)
            seed_point (tuple): Optional seed point for random walker
            mediastinal_bbox (tuple): Optional mediastinal bounding box
            generate_qc (bool): Generate QC visualizations
            
        Returns:
            dict: Results containing masks, features, and QC paths
        """
        print("Segmenting lung tumor...")
        # Step 1: Segment primary lung tumor
        initial_mask = self.segmenter.segment(pet_image, ct_image, spacing, 
                                             seed_point)
        
        # Get largest lesion (primary tumor)
        initial_mask = self.segmenter.get_largest_lesion(initial_mask)
        
        print("Excluding mediastinal regions...")
        # Step 2: Exclude mediastinal regions
        final_mask = self.excluder.apply_all_exclusions(
            initial_mask, pet_image, ct_image, spacing, mediastinal_bbox
        )
        
        # Ensure we still have largest component after exclusion
        final_mask = self.segmenter.get_largest_lesion(final_mask)
        
        print("Extracting metabolic features...")
        # Step 3: Extract metabolic radiomics features
        metabolic_features = self.metabolic_extractor.extract_features(
            pet_image, final_mask, spacing, self.mtv_threshold_percent
        )
        
        print("Extracting shape features...")
        # Step 4: Extract shape radiomics features
        shape_features = self.shape_extractor.extract_features(
            final_mask, spacing, resample_isotropic=True
        )
        
        print("Calculating advanced metrics...")
        # Step 5: Calculate advanced metrics
        advanced_features = self.advanced_metrics.extract_all_advanced_metrics(
            final_mask, pet_image, spacing, self.getu_a
        )
        
        # Combine all features
        combined_features = {
            **metabolic_features,
            **shape_features,
            **advanced_features
        }
        
        results = {
            'tumor_mask': final_mask,
            'tumor_mask_before_exclusion': initial_mask,
            'metabolic_features': metabolic_features,
            'shape_features': shape_features,
            'advanced_features': advanced_features,
            'combined_features': combined_features,
            'spacing': spacing
        }
        
        # Step 6: Generate QC visualizations
        if generate_qc and np.any(final_mask):
            print("Generating QC visualizations...")
            try:
                qc_overlay_path = self.qc_visualizer.create_qc_overlay(
                    pet_image, final_mask, "Mask_QC.png", ct_image, spacing
                )
                results['qc_overlay_path'] = qc_overlay_path
                
                qc_report_path = self.qc_visualizer.create_comprehensive_qc_report(
                    pet_image, final_mask, metabolic_features, shape_features,
                    advanced_features, ct_image, spacing, "QC_Report.png"
                )
                results['qc_report_path'] = qc_report_path
                
            except Exception as e:
                print(f"Warning: QC generation failed: {e}")
                results['qc_overlay_path'] = None
                results['qc_report_path'] = None
        
        print("Processing complete!")
        return results
    
    def process_and_save(self, pet_image, output_dir, ct_image=None, 
                        spacing=(1.0, 1.0, 1.0), seed_point=None,
                        mask_filename="tumor_mask.nii.gz",
                        features_filename="tumor_features.csv"):
        """
        Process image and save results.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            output_dir (str): Output directory
            ct_image (np.ndarray): Optional 3D CT image
            spacing (tuple): Voxel spacing
            seed_point (tuple): Optional seed point
            mask_filename (str): Mask output filename
            features_filename (str): Features CSV filename
            
        Returns:
            dict: Processing results
        """
        import pandas as pd
        
        # Update output directories
        self.qc_visualizer.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Process image
        results = self.process(pet_image, ct_image, spacing, seed_point)
        
        # Save mask as NIfTI
        mask_path = os.path.join(output_dir, mask_filename)
        affine = np.diag([spacing[0], spacing[1], spacing[2], 1.0])
        self.converter.save_nifti(results['tumor_mask'].astype(np.float32), 
                                  affine, mask_path)
        print(f"Tumor mask saved: {mask_path}")
        
        # Save features to CSV
        features_df = pd.DataFrame([results['combined_features']])
        features_path = os.path.join(output_dir, features_filename)
        features_df.to_csv(features_path, index=False)
        print(f"Features saved: {features_path}")
        
        results['mask_path'] = mask_path
        results['features_path'] = features_path
        
        return results

```

---

## 5. lung_radiomics.py

**Lines**: 621
**Location**: `src/lung_asp/lung_radiomics.py`

```python
"""
Lung Tumor Radiomics Module

This module provides comprehensive radiomics feature extraction for lung tumors
including metabolic, shape, and advanced geometric metrics.
"""

import numpy as np
from scipy import ndimage
from scipy.spatial import ConvexHull, distance_matrix
from scipy.spatial.distance import pdist, cdist
from skimage import measure, morphology
import trimesh
import warnings


class LungMetabolicRadiomics:
    """
    Extract metabolic radiomics features from FDG PET lung tumors.
    
    Includes SUV statistics, MTV, TLG, and advanced uptake metrics.
    """
    
    def __init__(self):
        """Initialize the metabolic radiomics extractor."""
        pass
        
    def extract_features(self, pet_image, tumor_mask, spacing=(1.0, 1.0, 1.0),
                        mtv_threshold_percent=41):
        """
        Extract metabolic radiomics features.
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            spacing (tuple): Voxel spacing in mm (z, y, x)
            mtv_threshold_percent (int): MTV threshold as % of SUVmax (default: 41)
            
        Returns:
            dict: Dictionary containing metabolic features
        """
        if not np.any(tumor_mask):
            return self._empty_features()
            
        # Extract tumor voxel values
        tumor_voxels = pet_image[tumor_mask > 0]
        
        if len(tumor_voxels) == 0:
            return self._empty_features()
            
        # Calculate voxel volume in mL
        voxel_volume_ml = np.prod(spacing) / 1000.0  # mm³ to mL
        
        # Basic SUV statistics
        suv_max = float(np.max(tumor_voxels))
        suv_mean = float(np.mean(tumor_voxels))
        suv_std = float(np.std(tumor_voxels))
        suv_median = float(np.median(tumor_voxels))
        suv_min = float(np.min(tumor_voxels))
        
        # Calculate percentiles
        suv_p25 = float(np.percentile(tumor_voxels, 25))
        suv_p75 = float(np.percentile(tumor_voxels, 75))
        suv_p90 = float(np.percentile(tumor_voxels, 90))
        
        # Metabolic tumor volume (MTV) at 41% SUVmax threshold
        mtv_threshold = suv_max * (mtv_threshold_percent / 100.0)
        mtv_mask = (pet_image >= mtv_threshold) & (tumor_mask > 0)
        mtv_ml = float(np.sum(mtv_mask) * voxel_volume_ml)
        
        # Total lesion glycolysis (TLG) - using MTV region
        if np.any(mtv_mask):
            mtv_voxels = pet_image[mtv_mask]
            tlg = float(np.mean(mtv_voxels) * mtv_ml)
        else:
            tlg = 0.0
        
        # SUV peak - average SUV in 1 cm³ sphere with highest average
        suv_peak = self._calculate_suv_peak(pet_image, tumor_mask, spacing)
        
        # Coefficient of variation
        cov = float(suv_std / suv_mean) if suv_mean > 0 else 0.0
        
        features = {
            'SUVmax': suv_max,
            'SUVmean': suv_mean,
            'SUVstd': suv_std,
            'SUVmedian': suv_median,
            'SUVmin': suv_min,
            'SUVp25': suv_p25,
            'SUVp75': suv_p75,
            'SUVp90': suv_p90,
            'SUVpeak': suv_peak,
            'MTV_ml': mtv_ml,
            'TLG': tlg,
            'COV': cov,
            'MTV_threshold_percent': mtv_threshold_percent,
            'n_voxels': len(tumor_voxels)
        }
        
        return features
    
    def _calculate_suv_peak(self, pet_image, tumor_mask, spacing, 
                           sphere_volume_ml=1.0):
        """
        Calculate SUV peak - average SUV in 1 cm³ sphere with highest average.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            tumor_mask (np.ndarray): Binary tumor mask
            spacing (tuple): Voxel spacing in mm
            sphere_volume_ml (float): Volume of sphere in mL (default: 1.0 cm³)
            
        Returns:
            float: SUV peak value
        """
        if not np.any(tumor_mask):
            return 0.0
            
        # Calculate sphere radius in voxels
        voxel_volume_ml = np.prod(spacing) / 1000.0
        sphere_voxels = sphere_volume_ml / voxel_volume_ml
        sphere_radius = (3 * sphere_voxels / (4 * np.pi)) ** (1/3)
        
        # Use uniform filter for averaging
        from scipy.ndimage import uniform_filter
        kernel_size = [max(3, int(2 * sphere_radius + 1)) for _ in range(3)]
        
        masked_pet = pet_image.copy()
        masked_pet[tumor_mask == 0] = 0
        
        averaged = uniform_filter(masked_pet, size=kernel_size)
        
        suv_peak = float(np.max(averaged[tumor_mask > 0])) if np.any(tumor_mask) else 0.0
        
        return suv_peak
    
    def _empty_features(self):
        """Return empty feature dictionary."""
        return {
            'SUVmax': 0.0,
            'SUVmean': 0.0,
            'SUVstd': 0.0,
            'SUVmedian': 0.0,
            'SUVmin': 0.0,
            'SUVp25': 0.0,
            'SUVp75': 0.0,
            'SUVp90': 0.0,
            'SUVpeak': 0.0,
            'MTV_ml': 0.0,
            'TLG': 0.0,
            'COV': 0.0,
            'MTV_threshold_percent': 41,
            'n_voxels': 0
        }


class LungShapeRadiomics:
    """
    Extract shape radiomics features from segmented lung tumors.
    
    Includes volume, surface area, sphericity, asphericity, and other
    geometric properties using marching cubes for surface extraction.
    """
    
    def __init__(self, isotropic_spacing=1.0):
        """
        Initialize the shape radiomics extractor.
        
        Args:
            isotropic_spacing (float): Target isotropic spacing in mm for resampling
        """
        self.isotropic_spacing = isotropic_spacing
        
    def resample_to_isotropic(self, mask, original_spacing, target_spacing=1.0):
        """
        Resample mask to isotropic voxels using nearest neighbor.
        
        Args:
            mask (np.ndarray): Binary mask
            original_spacing (tuple): Original voxel spacing (z, y, x)
            target_spacing (float): Target isotropic spacing in mm
            
        Returns:
            tuple: (resampled_mask, new_spacing)
        """
        from scipy.ndimage import zoom
        
        # Calculate zoom factors
        zoom_factors = [original_spacing[i] / target_spacing for i in range(3)]
        
        # Resample using nearest neighbor (order=0) to preserve labels
        resampled_mask = zoom(mask, zoom_factors, order=0)
        
        new_spacing = (target_spacing, target_spacing, target_spacing)
        
        return resampled_mask, new_spacing
    
    def extract_surface_with_marching_cubes(self, mask, spacing=(1.0, 1.0, 1.0)):
        """
        Extract triangular surface mesh using marching cubes.
        
        Args:
            mask (np.ndarray): Binary mask
            spacing (tuple): Voxel spacing
            
        Returns:
            tuple: (vertices, faces, surface_area_mm2) or (None, None, 0.0)
        """
        if not np.any(mask):
            return None, None, 0.0
        
        try:
            # Extract surface using marching cubes
            verts, faces, normals, values = measure.marching_cubes(
                mask.astype(float), level=0.5, spacing=spacing
            )
            
            # Calculate surface area
            surface_area_mm2 = float(measure.mesh_surface_area(verts, faces))
            
            return verts, faces, surface_area_mm2
            
        except (RuntimeError, ValueError) as e:
            print(f"Marching cubes failed: {e}")
            return None, None, self._approximate_surface_area(mask, spacing)
    
    def extract_features(self, tumor_mask, spacing=(1.0, 1.0, 1.0), 
                        resample_isotropic=True):
        """
        Extract shape radiomics features.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            spacing (tuple): Voxel spacing in mm (z, y, x)
            resample_isotropic (bool): Resample to isotropic 1mm grid
            
        Returns:
            dict: Dictionary containing shape features
        """
        if not np.any(tumor_mask):
            return self._empty_features()
        
        # Resample to isotropic if requested
        if resample_isotropic:
            iso_mask, iso_spacing = self.resample_to_isotropic(
                tumor_mask, spacing, self.isotropic_spacing
            )
        else:
            iso_mask = tumor_mask
            iso_spacing = spacing
            
        # Calculate voxel volume
        voxel_volume_mm3 = np.prod(spacing)
        
        # Get region properties
        labeled = measure.label(tumor_mask, connectivity=3)
        regions = measure.regionprops(labeled)
        
        if len(regions) == 0:
            return self._empty_features()
            
        # Use largest component
        if len(regions) > 1:
            largest_region = max(regions, key=lambda r: r.area)
        else:
            largest_region = regions[0]
            
        # Volume (using original spacing)
        volume_voxels = largest_region.area
        volume_mm3 = float(volume_voxels * voxel_volume_mm3)
        volume_ml = volume_mm3 / 1000.0
        
        # Surface area using marching cubes on isotropic mask
        verts, faces, surface_area_mm2 = self.extract_surface_with_marching_cubes(
            iso_mask, iso_spacing
        )
        
        # Sphericity (Ψ) and Asphericity (ASP)
        # Ψ = π^(1/3) * (6V)^(2/3) / A
        # ASP = 1 - Ψ
        if surface_area_mm2 > 0 and volume_mm3 > 0:
            sphericity = (np.pi ** (1/3)) * ((6 * volume_mm3) ** (2/3)) / surface_area_mm2
            sphericity = float(min(sphericity, 1.0))  # Clamp to [0, 1]
            asphericity = float(1.0 - sphericity)
        else:
            sphericity = 0.0
            asphericity = 1.0
        
        # Compactness measures
        compactness_1 = float(volume_mm3 / (surface_area_mm2 ** (3/2))) if surface_area_mm2 > 0 else 0.0
        compactness_2 = float(36 * np.pi * (volume_mm3 ** 2) / (surface_area_mm2 ** 3)) if surface_area_mm2 > 0 else 0.0
        
        # Bounding box
        bbox = largest_region.bbox
        bbox_volume = float((bbox[3] - bbox[0]) * (bbox[4] - bbox[1]) * (bbox[5] - bbox[2]) * voxel_volume_mm3)
        
        # Maximum 3D diameter (using isotropic mask for accuracy)
        max_diameter_mm = self._calculate_max_diameter(iso_mask, iso_spacing)
        
        # Elongation and flatness
        try:
            coords = np.argwhere(tumor_mask > 0)
            coords_scaled = coords * spacing
            centered = coords_scaled - coords_scaled.mean(axis=0)
            inertia = np.dot(centered.T, centered) / len(coords)
            eigenvalues = np.linalg.eigvalsh(inertia)
            eigenvalues = np.sort(eigenvalues)[::-1]
            
            if eigenvalues[0] > 0:
                elongation = float(np.sqrt(eigenvalues[1] / eigenvalues[0]))
                flatness = float(np.sqrt(eigenvalues[2] / eigenvalues[0]))
            else:
                elongation = 0.0
                flatness = 0.0
        except (ValueError, IndexError, np.linalg.LinAlgError):
            elongation = 0.0
            flatness = 0.0
        
        # Solidity
        try:
            coords = np.argwhere(tumor_mask > 0) * spacing
            if len(coords) >= 4:
                hull = ConvexHull(coords)
                convex_volume = hull.volume
                solidity = float(volume_mm3 / convex_volume) if convex_volume > 0 else 0.0
            else:
                solidity = 1.0
        except (ImportError, ValueError, Exception):
            solidity = 1.0
            
        features = {
            'Volume_mm3': volume_mm3,
            'Volume_ml': volume_ml,
            'SurfaceArea_mm2': surface_area_mm2,
            'Sphericity': sphericity,
            'Asphericity': asphericity,
            'Compactness1': compactness_1,
            'Compactness2': compactness_2,
            'MaxDiameter_mm': max_diameter_mm,
            'BoundingBoxVolume_mm3': bbox_volume,
            'Elongation': elongation,
            'Flatness': flatness,
            'Solidity': solidity,
            'n_voxels': int(volume_voxels)
        }
        
        return features
    
    def _approximate_surface_area(self, mask, spacing):
        """Approximate surface area when marching cubes fails."""
        eroded = ndimage.binary_erosion(mask)
        boundary = mask & ~eroded
        n_boundary_voxels = np.sum(boundary)
        voxel_face_area = np.mean([spacing[i] * spacing[j] 
                                   for i in range(3) for j in range(i+1, 3)])
        return float(n_boundary_voxels * voxel_face_area * 6)
    
    def _calculate_max_diameter(self, mask, spacing):
        """Calculate maximum 3D diameter."""
        coords = np.argwhere(mask > 0)
        if len(coords) < 2:
            return 0.0
        coords_scaled = coords * spacing
        if len(coords_scaled) > 1000:
            indices = np.random.choice(len(coords_scaled), 1000, replace=False)
            coords_sample = coords_scaled[indices]
        else:
            coords_sample = coords_scaled
        distances = pdist(coords_sample, metric='euclidean')
        return float(np.max(distances)) if len(distances) > 0 else 0.0
    
    def _empty_features(self):
        """Return empty feature dictionary."""
        return {
            'Volume_mm3': 0.0,
            'Volume_ml': 0.0,
            'SurfaceArea_mm2': 0.0,
            'Sphericity': 0.0,
            'Asphericity': 1.0,
            'Compactness1': 0.0,
            'Compactness2': 0.0,
            'MaxDiameter_mm': 0.0,
            'BoundingBoxVolume_mm3': 0.0,
            'Elongation': 0.0,
            'Flatness': 0.0,
            'Solidity': 0.0,
            'n_voxels': 0
        }


class AdvancedMetrics:
    """
    Calculate advanced geometric and uptake metrics for lung tumors.
    
    Includes NHOCmax, NHOPmax, Dmax, DmaxVox, and gETU.
    """
    
    def __init__(self):
        """Initialize advanced metrics calculator."""
        pass
    
    def calculate_nhocmax(self, tumor_mask, pet_image, spacing=(1.0, 1.0, 1.0)):
        """
        Calculate NHOCmax - Normalized Hotspot-to-Centroid distance.
        
        NHOCmax = d(x_SUVmax, x_centroid) / R
        where R is the radius of equivalent-volume sphere
        
        Args:
            tumor_mask (np.ndarray): Binary tumor mask
            pet_image (np.ndarray): PET image with SUV values
            spacing (tuple): Voxel spacing in mm
            
        Returns:
            float: NHOCmax value
        """
        if not np.any(tumor_mask):
            return 0.0
        
        # Find SUVmax location
        tumor_region = pet_image * tumor_mask
        suv_max_idx = np.unravel_index(np.argmax(tumor_region), tumor_region.shape)
        suv_max_coords = np.array(suv_max_idx) * spacing
        
        # Calculate centroid
        coords = np.argwhere(tumor_mask > 0)
        coords_scaled = coords * spacing
        centroid = coords_scaled.mean(axis=0)
        
        # Distance from SUVmax to centroid
        distance_mm = np.linalg.norm(suv_max_coords - centroid)
        
        # Calculate equivalent-volume sphere radius
        volume_mm3 = np.sum(tumor_mask) * np.prod(spacing)
        R = ((3 * volume_mm3) / (4 * np.pi)) ** (1/3)
        
        # Normalize
        nhocmax = float(distance_mm / R) if R > 0 else 0.0
        
        return nhocmax
    
    def calculate_nhopmax(self, tumor_mask, pet_image, spacing=(1.0, 1.0, 1.0)):
        """
        Calculate NHOPmax - Normalized Hotspot-to-Perimeter distance.
        
        NHOPmax = d_min(x_SUVmax, boundary) / R
        where R is the radius of equivalent-volume sphere
        
        Args:
            tumor_mask (np.ndarray): Binary tumor mask
            pet_image (np.ndarray): PET image with SUV values
            spacing (tuple): Voxel spacing in mm
            
        Returns:
            float: NHOPmax value
        """
        if not np.any(tumor_mask):
            return 0.0
        
        # Find SUVmax location
        tumor_region = pet_image * tumor_mask
        suv_max_idx = np.unravel_index(np.argmax(tumor_region), tumor_region.shape)
        
        # Find boundary (surface) voxels
        eroded = ndimage.binary_erosion(tumor_mask)
        boundary = tumor_mask & (~eroded)
        
        # Calculate distance transform from boundary
        # Distance transform gives distance to nearest background (0) voxel
        # We want distance to boundary, so invert the mask
        dist_transform = ndimage.distance_transform_edt(
            tumor_mask, sampling=spacing
        )
        
        # Alternative: calculate distance to boundary directly
        boundary_coords = np.argwhere(boundary > 0) * spacing
        suv_max_coords = np.array(suv_max_idx) * spacing
        
        if len(boundary_coords) > 0:
            distances = np.linalg.norm(boundary_coords - suv_max_coords, axis=1)
            min_distance_mm = float(np.min(distances))
        else:
            min_distance_mm = 0.0
        
        # Calculate equivalent-volume sphere radius
        volume_mm3 = np.sum(tumor_mask) * np.prod(spacing)
        R = ((3 * volume_mm3) / (4 * np.pi)) ** (1/3)
        
        # Normalize
        nhopmax = float(min_distance_mm / R) if R > 0 else 0.0
        
        return nhopmax
    
    def calculate_dmax(self, tumor_mask, spacing=(1.0, 1.0, 1.0)):
        """
        Calculate intra-lesion Dmax - maximum 3D diameter.
        
        Dmax = max distance between any two boundary points
        
        Args:
            tumor_mask (np.ndarray): Binary tumor mask
            spacing (tuple): Voxel spacing in mm
            
        Returns:
            float: Dmax in mm
        """
        if not np.any(tumor_mask):
            return 0.0
        
        # Find boundary voxels
        eroded = ndimage.binary_erosion(tumor_mask)
        boundary = tumor_mask & (~eroded)
        
        boundary_coords = np.argwhere(boundary > 0) * spacing
        
        if len(boundary_coords) < 2:
            return 0.0
        
        # Sample if too many points
        if len(boundary_coords) > 1000:
            indices = np.random.choice(len(boundary_coords), 1000, replace=False)
            boundary_coords = boundary_coords[indices]
        
        # Calculate pairwise distances
        distances = pdist(boundary_coords, metric='euclidean')
        dmax = float(np.max(distances)) if len(distances) > 0 else 0.0
        
        return dmax
    
    def calculate_dmax_vox(self, tumor_mask, spacing=(1.0, 1.0, 1.0)):
        """
        Calculate intra-lesion DmaxVox - voxel-based maximum diameter.
        
        Uses surface voxel centers for calculation.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor mask
            spacing (tuple): Voxel spacing in mm
            
        Returns:
            float: DmaxVox in mm
        """
        # For voxel-based, this is equivalent to Dmax
        return self.calculate_dmax(tumor_mask, spacing)
    
    def calculate_getu(self, pet_image, tumor_mask, spacing=(1.0, 1.0, 1.0), 
                      a=1.0):
        """
        Calculate gETU - generalized effective total uptake.
        
        gETU(a) = (Δv * Σ(u_i^a))^(1/a)
        
        where:
        - u_i are SUV values in tumor VOI
        - Δv is voxel volume in mL
        - a is power parameter (a=1 gives TLG, a→∞ emphasizes SUVmax)
        
        Args:
            pet_image (np.ndarray): PET image with SUV values
            tumor_mask (np.ndarray): Binary tumor mask
            spacing (tuple): Voxel spacing in mm
            a (float): Power parameter (default: 1.0)
            
        Returns:
            dict: gETU value and related metrics
        """
        if not np.any(tumor_mask):
            return {'gETU': 0.0, 'a_parameter': a}
        
        # Extract SUV values
        suv_values = pet_image[tumor_mask > 0]
        
        if len(suv_values) == 0:
            return {'gETU': 0.0, 'a_parameter': a}
        
        # Voxel volume in mL
        voxel_volume_ml = np.prod(spacing) / 1000.0
        
        # Calculate gETU
        if a > 0:
            sum_powers = np.sum(suv_values ** a)
            getu = float((voxel_volume_ml * sum_powers) ** (1/a))
        else:
            # For a→0, gETU → V (volume)
            getu = float(len(suv_values) * voxel_volume_ml)
        
        return {
            'gETU': getu,
            'a_parameter': a,
            'n_voxels': len(suv_values)
        }
    
    def extract_all_advanced_metrics(self, tumor_mask, pet_image, 
                                     spacing=(1.0, 1.0, 1.0), getu_a=1.0):
        """
        Extract all advanced metrics.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor mask
            pet_image (np.ndarray): PET image
            spacing (tuple): Voxel spacing
            getu_a (float): gETU power parameter
            
        Returns:
            dict: All advanced metrics
        """
        nhocmax = self.calculate_nhocmax(tumor_mask, pet_image, spacing)
        nhopmax = self.calculate_nhopmax(tumor_mask, pet_image, spacing)
        dmax = self.calculate_dmax(tumor_mask, spacing)
        dmax_vox = self.calculate_dmax_vox(tumor_mask, spacing)
        getu_result = self.calculate_getu(pet_image, tumor_mask, spacing, getu_a)
        
        return {
            'NHOCmax': nhocmax,
            'NHOPmax': nhopmax,
            'Dmax_mm': dmax,
            'DmaxVox_mm': dmax_vox,
            'gETU': getu_result['gETU'],
            'gETU_a_parameter': getu_result['a_parameter']
        }

```

---

## 6. lung_segmentation.py

**Lines**: 298
**Location**: `src/lung_asp/lung_segmentation.py`

```python
"""
Lung Tumor Segmentation Module

This module provides functionality for segmenting primary lung tumors
from FDG PET/CT imaging using random walker algorithm and SUV thresholding.
"""

import numpy as np
from scipy import ndimage
from skimage import measure, morphology, segmentation
from skimage.filters import threshold_otsu
import warnings


class LungTumorSegmenter:
    """
    Segments primary lung tumors from FDG PET/CT images using random walker.
    
    Attributes:
        suv_threshold (float): SUV threshold for tumor detection (default: 2.5)
        min_volume_mm3 (float): Minimum tumor volume in mm³ (default: 100.0)
        use_random_walker (bool): Use random walker algorithm (default: True)
    """
    
    def __init__(self, suv_threshold=2.5, min_volume_mm3=100.0, use_random_walker=True):
        """
        Initialize the lung tumor segmenter.
        
        Args:
            suv_threshold (float): SUV threshold for initial segmentation
            min_volume_mm3 (float): Minimum tumor volume to consider
            use_random_walker (bool): Use random walker algorithm
        """
        self.suv_threshold = suv_threshold
        self.min_volume_mm3 = min_volume_mm3
        self.use_random_walker = use_random_walker
        
    def create_thoracic_body_mask(self, ct_image, hu_min=-500, hu_max=1000, 
                                  closing_radius=20):
        """
        Create thoracic body mask from CT to restrict segmentation field.
        
        Args:
            ct_image (np.ndarray): 3D CT image array with HU values
            hu_min (int): Minimum HU threshold
            hu_max (int): Maximum HU threshold
            closing_radius (int): Morphological closing radius in voxels
            
        Returns:
            np.ndarray: Binary thoracic body mask
        """
        if ct_image is None:
            return None
            
        # Threshold CT to get body region
        body_mask = (ct_image >= hu_min) & (ct_image <= hu_max)
        
        # Morphological closing to fill gaps
        if closing_radius > 0:
            try:
                # Use ball structuring element for 3D closing
                struct_elem = morphology.ball(closing_radius)
                body_mask = morphology.closing(body_mask, struct_elem)
            except (ValueError, MemoryError):
                # Fallback to smaller radius if memory issue
                struct_elem = morphology.ball(min(closing_radius // 2, 10))
                body_mask = morphology.closing(body_mask, struct_elem)
        
        # Fill holes
        body_mask = ndimage.binary_fill_holes(body_mask)
        
        # Keep only largest component (main thorax)
        labeled = measure.label(body_mask, connectivity=3)
        if labeled.max() > 0:
            regions = measure.regionprops(labeled)
            largest_region = max(regions, key=lambda r: r.area)
            body_mask = (labeled == largest_region.label).astype(np.uint8)
        
        return body_mask
    
    def segment_with_random_walker(self, pet_image, ct_image=None, 
                                   spacing=(1.0, 1.0, 1.0), seed_point=None,
                                   beta=130):
        """
        Segment lung tumor using random walker algorithm.
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            ct_image (np.ndarray): Optional 3D CT image for anatomical guidance
            spacing (tuple): Voxel spacing in mm (z, y, x)
            seed_point (tuple): Optional seed point (z, y, x) for tumor
            beta (float): Random walker beta parameter (edge weight)
            
        Returns:
            np.ndarray: Binary segmentation mask
        """
        # Create thoracic body mask if CT available
        thoracic_mask = None
        if ct_image is not None:
            thoracic_mask = self.create_thoracic_body_mask(ct_image)
        
        # Initial high threshold segmentation for seed
        high_threshold = max(self.suv_threshold * 1.5, 4.0)
        seed_mask = pet_image >= high_threshold
        
        # Restrict to thoracic region
        if thoracic_mask is not None:
            seed_mask = seed_mask & thoracic_mask
        
        # Remove small objects
        try:
            seed_mask = morphology.remove_small_objects(seed_mask, max_size=10)
        except TypeError:
            seed_mask = morphology.remove_small_objects(seed_mask, min_size=10)
        
        # If no automatic seeds and seed point provided, use it
        if not np.any(seed_mask) and seed_point is not None:
            seed_mask[seed_point] = True
        
        # If still no seeds, fall back to threshold-based
        if not np.any(seed_mask):
            return self.segment_threshold_based(pet_image, thoracic_mask, spacing)
        
        # Create markers for random walker
        markers = np.zeros_like(pet_image, dtype=np.int32)
        
        # Label tumor seeds
        labeled_seeds = measure.label(seed_mask, connectivity=3)
        regions = measure.regionprops(labeled_seeds)
        
        if len(regions) > 0:
            # Use largest seed region as tumor marker
            largest_seed = max(regions, key=lambda r: r.area)
            markers[labeled_seeds == largest_seed.label] = 1  # Tumor
        else:
            return self.segment_threshold_based(pet_image, thoracic_mask, spacing)
        
        # Create background markers (low SUV regions)
        background_mask = pet_image < (self.suv_threshold * 0.5)
        if thoracic_mask is not None:
            background_mask = background_mask & thoracic_mask
        
        # Erode background to avoid tumor boundary
        background_mask = morphology.erosion(background_mask, 
                                            morphology.ball(3))
        markers[background_mask] = 2  # Background
        
        # Prepare image for random walker (normalize)
        image_normalized = pet_image.copy()
        if image_normalized.max() > 0:
            image_normalized = image_normalized / image_normalized.max()
        
        try:
            # Apply random walker
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                labels = segmentation.random_walker(
                    image_normalized, 
                    markers, 
                    beta=beta, 
                    mode='cg_mg'
                )
            
            # Extract tumor label
            tumor_mask = (labels == 1).astype(np.uint8)
            
        except (ValueError, RuntimeError) as e:
            print(f"Random walker failed: {e}, using threshold method")
            return self.segment_threshold_based(pet_image, thoracic_mask, spacing)
        
        # Post-process
        tumor_mask = self._post_process_mask(tumor_mask, pet_image, spacing)
        
        return tumor_mask
    
    def segment_threshold_based(self, pet_image, thoracic_mask=None, 
                                spacing=(1.0, 1.0, 1.0)):
        """
        Fallback threshold-based segmentation.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            thoracic_mask (np.ndarray): Optional thoracic body mask
            spacing (tuple): Voxel spacing
            
        Returns:
            np.ndarray: Binary tumor mask
        """
        # Apply SUV threshold
        binary_mask = pet_image >= self.suv_threshold
        
        # Restrict to thoracic region
        if thoracic_mask is not None:
            binary_mask = binary_mask & thoracic_mask
        
        # Remove small objects
        try:
            binary_mask = morphology.remove_small_objects(binary_mask, max_size=10)
            binary_mask = morphology.remove_small_holes(binary_mask, max_size=10)
        except TypeError:
            binary_mask = morphology.remove_small_objects(binary_mask, min_size=10)
            binary_mask = morphology.remove_small_holes(binary_mask, area_threshold=10)
        
        # Post-process
        binary_mask = self._post_process_mask(binary_mask, pet_image, spacing)
        
        return binary_mask
    
    def _post_process_mask(self, mask, pet_image, spacing):
        """
        Post-process segmentation mask.
        
        Args:
            mask (np.ndarray): Binary mask
            pet_image (np.ndarray): PET image
            spacing (tuple): Voxel spacing
            
        Returns:
            np.ndarray: Post-processed mask
        """
        if not np.any(mask):
            return mask
        
        # Morphological closing (radius 2 voxels)
        try:
            struct_elem = morphology.ball(2)
            mask = morphology.closing(mask, struct_elem)
        except (ValueError, MemoryError):
            mask = morphology.closing(mask, morphology.ball(1))
        
        # Fill holes (cavities >= 500 voxels) INSIDE the mask
        # Only fill holes that are surrounded by the tumor
        mask_filled = ndimage.binary_fill_holes(mask)
        
        # Find holes (regions inside tumor that were filled)
        holes = mask_filled & (~mask)
        labeled_holes = measure.label(holes, connectivity=3)
        regions = measure.regionprops(labeled_holes)
        
        # Only keep large holes filled
        for region in regions:
            if region.area >= 500:
                mask[labeled_holes == region.label] = 1
        
        # Label connected components and filter by volume
        labeled_mask = measure.label(mask, connectivity=3)
        voxel_volume = np.prod(spacing)
        regions = measure.regionprops(labeled_mask)
        
        final_mask = np.zeros_like(mask, dtype=np.uint8)
        for region in regions:
            volume_mm3 = region.area * voxel_volume
            if volume_mm3 >= self.min_volume_mm3:
                final_mask[labeled_mask == region.label] = 1
        
        return final_mask
    
    def get_largest_lesion(self, mask):
        """
        Extract the largest connected component (primary tumor).
        
        Args:
            mask (np.ndarray): Binary segmentation mask
            
        Returns:
            np.ndarray: Binary mask containing only the largest lesion
        """
        labeled = measure.label(mask, connectivity=3)
        if labeled.max() == 0:
            return mask
            
        regions = measure.regionprops(labeled)
        largest_region = max(regions, key=lambda r: r.area)
        
        return (labeled == largest_region.label).astype(np.uint8)
    
    def segment(self, pet_image, ct_image=None, spacing=(1.0, 1.0, 1.0), 
                seed_point=None):
        """
        Main segmentation method.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            ct_image (np.ndarray): Optional 3D CT image
            spacing (tuple): Voxel spacing in mm
            seed_point (tuple): Optional seed point for random walker
            
        Returns:
            np.ndarray: Binary tumor mask
        """
        if self.use_random_walker:
            return self.segment_with_random_walker(pet_image, ct_image, spacing, 
                                                   seed_point)
        else:
            thoracic_mask = None
            if ct_image is not None:
                thoracic_mask = self.create_thoracic_body_mask(ct_image)
            return self.segment_threshold_based(pet_image, thoracic_mask, spacing)

```

---

## 7. nnunet_wrapper.py

**Lines**: 252
**Location**: `src/lung_asp/nnunet_wrapper.py`

```python
"""
nnU-Net Integration Module

Wrapper for nnU-Net to provide advanced lung tumor segmentation
using pre-trained deep learning models.
"""

import os
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NnUNetWrapper:
    """
    Wrapper for nnU-Net functionality.
    
    Provides deep learning-based segmentation for:
    - Lung tumor detection
    - Precise boundary delineation
    - Multi-class tissue segmentation
    """
    
    def __init__(self, model_dir=None, model_name='Task001_LungTumor'):
        """
        Initialize nnU-Net wrapper.
        
        Args:
            model_dir (str): Directory containing nnU-Net models
            model_name (str): Name of the model to use
        """
        self.model_dir = model_dir
        self.model_name = model_name
        self._nnunet_available = False
        self._initialize_nnunet()
        
    def _initialize_nnunet(self):
        """Check if nnU-Net is available and initialize."""
        try:
            from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
            from nnunetv2.paths import nnUNet_results
            
            self.nnUNetPredictor = nnUNetPredictor
            self.nnUNet_results = nnUNet_results
            self._nnunet_available = True
            logger.info("nnU-Net initialized successfully")
            
        except ImportError:
            logger.warning("nnU-Net not available. Deep learning segmentation disabled.")
            self._nnunet_available = False
    
    def is_available(self):
        """Check if nnU-Net is available."""
        return self._nnunet_available
    
    def predict(self, input_path, output_path=None, fold='all', checkpoint='checkpoint_best.pth'):
        """
        Run nnU-Net prediction on input image.
        
        Args:
            input_path (str): Path to input NIfTI file or directory
            output_path (str): Path for output segmentation
            fold (str): Which fold to use ('all', 0, 1, 2, 3, 4)
            checkpoint (str): Checkpoint file name
        
        Returns:
            np.ndarray: Segmentation mask or None if failed
        """
        if not self._nnunet_available:
            logger.warning("nnU-Net not available")
            return None
        
        try:
            logger.info(f"Running nnU-Net prediction on {input_path}")
            
            # Initialize predictor
            predictor = self.nnUNetPredictor(
                tile_step_size=0.5,
                use_gaussian=True,
                use_mirroring=True,
                perform_everything_on_gpu=True,
                device='cuda:0' if self._check_cuda() else 'cpu',
                verbose=False,
                verbose_preprocessing=False,
                allow_tqdm=True
            )
            
            # Setup model
            model_folder = self._get_model_folder()
            if model_folder is None:
                logger.error("Model folder not found")
                return None
            
            predictor.initialize_from_trained_model_folder(
                model_folder,
                use_folds=(fold,) if fold != 'all' else None,
                checkpoint_name=checkpoint,
            )
            
            # Prepare output
            if output_path is None:
                output_path = str(Path(input_path).parent / "nnunet_output.nii.gz")
            
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run prediction
            predictor.predict_from_files(
                [[input_path]],  # List of list of input files
                [str(output_path)],  # List of output files
                save_probabilities=False,
                overwrite=True,
                num_processes_preprocessing=2,
                num_processes_segmentation_export=2,
                folder_with_segs_from_prev_stage=None,
                num_parts=1,
                part_id=0,
            )
            
            logger.info(f"Prediction saved to {output_path}")
            
            # Load and return segmentation
            import nibabel as nib
            seg_img = nib.load(output_path)
            seg_data = seg_img.get_fdata()
            
            return seg_data
            
        except Exception as e:
            logger.error(f"nnU-Net prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_model_folder(self):
        """Get the model folder path."""
        if self.model_dir is not None:
            return Path(self.model_dir)
        
        # Try to find in default nnU-Net results directory
        try:
            results_dir = Path(self.nnUNet_results)
            # Typical structure: nnUNet_results/DatasetXXX_Name/Trainer__Plans/
            # This is a simplified search - adjust based on actual structure
            model_folders = list(results_dir.glob(f"**/{self.model_name}*"))
            if model_folders:
                return model_folders[0]
        except:
            pass
        
        return None
    
    def _check_cuda(self):
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def convert_to_binary_mask(self, segmentation, tumor_label=1):
        """
        Convert multi-class segmentation to binary tumor mask.
        
        Args:
            segmentation (np.ndarray): Multi-class segmentation
            tumor_label (int): Label ID for tumor class
            
        Returns:
            np.ndarray: Binary tumor mask
        """
        if segmentation is None:
            return None
        
        binary_mask = (segmentation == tumor_label).astype(np.uint8)
        return binary_mask
    
    def post_process_segmentation(self, segmentation, min_size=100):
        """
        Post-process segmentation to remove small components.
        
        Args:
            segmentation (np.ndarray): Segmentation mask
            min_size (int): Minimum component size in voxels
            
        Returns:
            np.ndarray: Cleaned segmentation
        """
        from skimage.measure import label
        from skimage.morphology import remove_small_objects
        
        # Label connected components
        labeled = label(segmentation, connectivity=3)
        
        # Remove small objects
        try:
            cleaned = remove_small_objects(labeled, max_size=min_size-1)
        except TypeError:
            # Older API
            cleaned = remove_small_objects(labeled, min_size=min_size)
        
        # Convert back to binary
        return (cleaned > 0).astype(np.uint8)


def download_nnunet_models(model_name='Task001_LungTumor', output_dir=None):
    """
    Download nnU-Net pre-trained models.
    
    Note: This is a placeholder. Actual model download would require:
    1. Models hosted on a server (Zenodo, Hugging Face, etc.)
    2. Download logic using requests/wget
    3. Model extraction and placement in correct directory
    
    Args:
        model_name (str): Name of the model to download
        output_dir (str): Directory to save models
        
    Returns:
        bool: True if successful
    """
    try:
        import requests
        from pathlib import Path
        
        if output_dir is None:
            # Use default nnU-Net directory
            try:
                from nnunetv2.paths import nnUNet_results
                output_dir = Path(nnUNet_results)
            except:
                output_dir = Path.home() / ".nnunet" / "results"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Model download for {model_name}")
        logger.info(f"Target directory: {output_dir}")
        
        # Placeholder for actual download logic
        logger.warning("Model download not implemented. Please manually place models in:")
        logger.warning(f"  {output_dir}")
        logger.warning("Models should follow nnU-Net directory structure:")
        logger.warning("  DatasetXXX_Name/Trainer__Plans/fold_X/")
        
        return False
        
    except Exception as e:
        logger.error(f"Failed to download models: {e}")
        return False

```

---

## 8. qc_visualization.py

**Lines**: 297
**Location**: `src/lung_asp/qc_visualization.py`

```python
"""
Quality Control Visualization Module

This module generates QC overlays by superimposing binary contours on
co-registered PET uptake in three orthogonal planes.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from skimage import measure
import os


class QCVisualizer:
    """
    Generate quality control overlays for tumor segmentation.
    
    Creates orthogonal plane views (axial, sagittal, coronal) with
    tumor contours overlaid on PET uptake.
    """
    
    def __init__(self, output_dir=None):
        """
        Initialize QC visualizer.
        
        Args:
            output_dir (str): Directory to save QC images
        """
        self.output_dir = output_dir or os.getcwd()
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_qc_overlay(self, pet_image, tumor_mask, output_filename="Mask_QC.png",
                         ct_image=None, spacing=(1.0, 1.0, 1.0), dpi=300):
        """
        Create QC overlay showing tumor contour on PET in 3 orthogonal planes.
        
        Args:
            pet_image (np.ndarray): 3D PET image with SUV values
            tumor_mask (np.ndarray): Binary tumor mask
            output_filename (str): Output filename
            ct_image (np.ndarray): Optional CT image for anatomical reference
            spacing (tuple): Voxel spacing in mm
            dpi (int): Image resolution (default: 300 for high resolution)
            
        Returns:
            str: Path to saved QC image
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not np.any(tumor_mask):
            print("Warning: Empty tumor mask, cannot create QC overlay")
            return None
        
        # Find lesion centroid
        coords = np.argwhere(tumor_mask > 0)
        centroid = coords.mean(axis=0).astype(int)
        centroid_z, centroid_y, centroid_x = centroid
        
        # Ensure centroid is within bounds
        centroid_z = np.clip(centroid_z, 0, pet_image.shape[0] - 1)
        centroid_y = np.clip(centroid_y, 0, pet_image.shape[1] - 1)
        centroid_x = np.clip(centroid_x, 0, pet_image.shape[2] - 1)
        
        # Create figure with 3 subplots (one for each plane)
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Define colormap for PET (hot colormap for SUV)
        pet_cmap = plt.cm.hot
        
        # Extract slices at centroid
        # Axial (z-plane)
        pet_axial = pet_image[centroid_z, :, :]
        mask_axial = tumor_mask[centroid_z, :, :]
        
        # Coronal (y-plane)
        pet_coronal = pet_image[:, centroid_y, :]
        mask_coronal = tumor_mask[:, centroid_y, :]
        
        # Sagittal (x-plane)
        pet_sagittal = pet_image[:, :, centroid_x]
        mask_sagittal = tumor_mask[:, :, centroid_x]
        
        # Plot axial
        self._plot_overlay(axes[0], pet_axial, mask_axial, 'Axial', pet_cmap)
        
        # Plot coronal
        self._plot_overlay(axes[1], pet_coronal, mask_coronal, 'Coronal', pet_cmap)
        
        # Plot sagittal
        self._plot_overlay(axes[2], pet_sagittal, mask_sagittal, 'Sagittal', pet_cmap)
        
        # Add overall title
        fig.suptitle(f'QC Overlay - Tumor Segmentation at Centroid ({centroid_z}, {centroid_y}, {centroid_x})',
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save with high resolution
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        
        print(f"QC overlay saved: {output_path}")
        return output_path
    
    def _plot_overlay(self, ax, pet_slice, mask_slice, title, cmap):
        """
        Plot a single slice with overlay.
        
        Args:
            ax: Matplotlib axis
            pet_slice (np.ndarray): 2D PET slice
            mask_slice (np.ndarray): 2D mask slice
            title (str): Subplot title
            cmap: Colormap for PET
        """
        # Display PET image
        vmin = np.percentile(pet_slice[pet_slice > 0], 1) if np.any(pet_slice > 0) else 0
        vmax = np.percentile(pet_slice[pet_slice > 0], 99) if np.any(pet_slice > 0) else 1
        
        im = ax.imshow(pet_slice, cmap=cmap, aspect='equal', 
                      vmin=vmin, vmax=vmax, interpolation='bilinear')
        
        # Overlay contour if mask is present
        if np.any(mask_slice):
            contours = measure.find_contours(mask_slice, 0.5)
            for contour in contours:
                ax.plot(contour[:, 1], contour[:, 0], 'cyan', linewidth=2)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')
        
        # Add colorbar
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='SUV')
    
    def create_3d_volume_rendering(self, pet_image, tumor_mask, 
                                   output_filename="3D_rendering.png",
                                   dpi=150):
        """
        Create a 3D volume rendering of the tumor.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            tumor_mask (np.ndarray): Binary tumor mask
            output_filename (str): Output filename
            dpi (int): Image resolution
            
        Returns:
            str: Path to saved image
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not np.any(tumor_mask):
            print("Warning: Empty tumor mask, cannot create 3D rendering")
            return None
        
        from mpl_toolkits.mplot3d import Axes3D
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        try:
            # Extract surface using marching cubes
            verts, faces, normals, values = measure.marching_cubes(
                tumor_mask.astype(float), level=0.5
            )
            
            # Create 3D plot
            fig = plt.figure(figsize=(10, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Create mesh
            mesh = Poly3DCollection(verts[faces], alpha=0.7, 
                                   facecolor='red', edgecolor='darkred')
            ax.add_collection3d(mesh)
            
            # Set limits
            ax.set_xlim(verts[:, 0].min(), verts[:, 0].max())
            ax.set_ylim(verts[:, 1].min(), verts[:, 1].max())
            ax.set_zlim(verts[:, 2].min(), verts[:, 2].max())
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('3D Tumor Rendering', fontsize=14, fontweight='bold')
            
            # Save
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
            plt.close()
            
            print(f"3D rendering saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"3D rendering failed: {e}")
            return None
    
    def create_comprehensive_qc_report(self, pet_image, tumor_mask, 
                                      metabolic_features, shape_features,
                                      advanced_features=None,
                                      ct_image=None, spacing=(1.0, 1.0, 1.0),
                                      output_filename="QC_Report.png", dpi=300):
        """
        Create comprehensive QC report with images and metrics.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            tumor_mask (np.ndarray): Binary tumor mask
            metabolic_features (dict): Metabolic radiomics features
            shape_features (dict): Shape radiomics features
            advanced_features (dict): Optional advanced metrics
            ct_image (np.ndarray): Optional CT image
            spacing (tuple): Voxel spacing
            output_filename (str): Output filename
            dpi (int): Image resolution
            
        Returns:
            str: Path to saved report
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not np.any(tumor_mask):
            print("Warning: Empty tumor mask, cannot create QC report")
            return None
        
        # Create figure with grid layout
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Find lesion centroid
        coords = np.argwhere(tumor_mask > 0)
        centroid = coords.mean(axis=0).astype(int)
        centroid_z, centroid_y, centroid_x = centroid
        
        # Clip centroid
        centroid_z = np.clip(centroid_z, 0, pet_image.shape[0] - 1)
        centroid_y = np.clip(centroid_y, 0, pet_image.shape[1] - 1)
        centroid_x = np.clip(centroid_x, 0, pet_image.shape[2] - 1)
        
        # Orthogonal slices
        pet_axial = pet_image[centroid_z, :, :]
        mask_axial = tumor_mask[centroid_z, :, :]
        pet_coronal = pet_image[:, centroid_y, :]
        mask_coronal = tumor_mask[:, centroid_y, :]
        pet_sagittal = pet_image[:, :, centroid_x]
        mask_sagittal = tumor_mask[:, :, centroid_x]
        
        # Plot orthogonal views
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_overlay(ax1, pet_axial, mask_axial, 'Axial', plt.cm.hot)
        
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_overlay(ax2, pet_coronal, mask_coronal, 'Coronal', plt.cm.hot)
        
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_overlay(ax3, pet_sagittal, mask_sagittal, 'Sagittal', plt.cm.hot)
        
        # Feature tables
        ax_metabolic = fig.add_subplot(gs[1, :2])
        ax_metabolic.axis('off')
        metabolic_text = self._format_features_table(metabolic_features, "Metabolic Features")
        ax_metabolic.text(0.05, 0.95, metabolic_text, transform=ax_metabolic.transAxes,
                         fontsize=9, verticalalignment='top', family='monospace')
        
        ax_shape = fig.add_subplot(gs[1, 2:])
        ax_shape.axis('off')
        shape_text = self._format_features_table(shape_features, "Shape Features")
        ax_shape.text(0.05, 0.95, shape_text, transform=ax_shape.transAxes,
                     fontsize=9, verticalalignment='top', family='monospace')
        
        # Advanced features if provided
        if advanced_features:
            ax_advanced = fig.add_subplot(gs[2, :])
            ax_advanced.axis('off')
            advanced_text = self._format_features_table(advanced_features, "Advanced Metrics")
            ax_advanced.text(0.05, 0.95, advanced_text, transform=ax_advanced.transAxes,
                           fontsize=9, verticalalignment='top', family='monospace')
        
        # Overall title
        fig.suptitle('Comprehensive QC Report - Lung Tumor Segmentation', 
                    fontsize=16, fontweight='bold')
        
        # Save
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        
        print(f"Comprehensive QC report saved: {output_path}")
        return output_path
    
    def _format_features_table(self, features, title):
        """Format features as text table."""
        text = f"{title}:\n" + "=" * 40 + "\n"
        for key, value in features.items():
            if isinstance(value, float):
                text += f"{key:25s}: {value:10.4f}\n"
            else:
                text += f"{key:25s}: {value}\n"
        return text

```

---

## 9. totalsegmentor_wrapper.py

**Lines**: 201
**Location**: `src/lung_asp/totalsegmentor_wrapper.py`

```python
"""
TotalSegmentor Integration Module

Wrapper for TotalSegmentor to provide body part segmentation
and anatomical structure identification for lung tumor analysis.
"""

import os
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TotalSegmentorWrapper:
    """
    Wrapper for TotalSegmentor functionality.
    
    Provides anatomical segmentation to help with:
    - Lung region identification
    - Mediastinal structure exclusion
    - Body region masking
    """
    
    def __init__(self, model_dir=None):
        """
        Initialize TotalSegmentor wrapper.
        
        Args:
            model_dir (str): Directory containing TotalSegmentor models
        """
        self.model_dir = model_dir
        self._totalseg_available = False
        self._initialize_totalsegmentor()
        
    def _initialize_totalsegmentor(self):
        """Check if TotalSegmentor is available and initialize."""
        try:
            import totalsegmentor
            from totalsegmentor.python_api import totalsegmentor as ts_segment
            self.totalsegmentor = totalsegmentor
            self.ts_segment = ts_segment
            self._totalseg_available = True
            logger.info("TotalSegmentor initialized successfully")
        except ImportError:
            logger.warning("TotalSegmentor not available. Anatomical segmentation disabled.")
            self._totalseg_available = False
    
    def is_available(self):
        """Check if TotalSegmentor is available."""
        return self._totalseg_available
    
    def segment_ct(self, ct_path, output_path=None, fast=True, roi_subset=None):
        """
        Segment CT image using TotalSegmentor.
        
        Args:
            ct_path (str): Path to CT NIfTI file
            output_path (str): Path for output segmentation
            fast (bool): Use fast mode (lower resolution)
            roi_subset (list): List of specific ROIs to segment
                             (e.g., ['lung_upper_lobe_left', 'lung_lower_lobe_left'])
        
        Returns:
            np.ndarray: Segmentation mask or None if failed
        """
        if not self._totalseg_available:
            logger.warning("TotalSegmentor not available")
            return None
        
        try:
            # Default ROI subset for lung analysis
            if roi_subset is None:
                roi_subset = [
                    'lung_upper_lobe_left',
                    'lung_lower_lobe_left', 
                    'lung_middle_lobe_left',
                    'lung_upper_lobe_right',
                    'lung_middle_lobe_right',
                    'lung_lower_lobe_right',
                    'heart',
                    'trachea',
                    'pulmonary_artery'
                ]
            
            logger.info(f"Running TotalSegmentor on {ct_path}")
            
            # Run segmentation
            if output_path is None:
                output_path = str(Path(ct_path).parent / "totalseg_output.nii.gz")
            
            # Call TotalSegmentor
            self.ts_segment(
                ct_path,
                output_path,
                ml=True,  # Use multilabel output
                fast=fast,
                roi_subset=roi_subset,
                statistics=False
            )
            
            logger.info(f"Segmentation saved to {output_path}")
            
            # Load and return segmentation
            import nibabel as nib
            seg_img = nib.load(output_path)
            seg_data = seg_img.get_fdata()
            
            return seg_data
            
        except Exception as e:
            logger.error(f"TotalSegmentor segmentation failed: {e}")
            return None
    
    def extract_lung_mask(self, segmentation):
        """
        Extract combined lung mask from TotalSegmentor output.
        
        Args:
            segmentation (np.ndarray): TotalSegmentor segmentation output
            
        Returns:
            np.ndarray: Binary lung mask
        """
        if segmentation is None:
            return None
        
        # TotalSegmentor lung label IDs (this may vary by version)
        # Check TotalSegmentor documentation for exact label mapping
        lung_labels = [1, 2, 3, 4, 5, 6]  # Placeholder - update with actual labels
        
        lung_mask = np.isin(segmentation, lung_labels)
        return lung_mask.astype(np.uint8)
    
    def extract_mediastinal_mask(self, segmentation):
        """
        Extract mediastinal structures mask from TotalSegmentor output.
        
        Args:
            segmentation (np.ndarray): TotalSegmentor segmentation output
            
        Returns:
            np.ndarray: Binary mediastinal mask
        """
        if segmentation is None:
            return None
        
        # Mediastinal structure labels (heart, major vessels, etc.)
        mediastinal_labels = [7, 8]  # Placeholder - update with actual labels
        
        mediastinal_mask = np.isin(segmentation, mediastinal_labels)
        return mediastinal_mask.astype(np.uint8)
    
    def get_thoracic_body_mask(self, ct_image, segmentation=None):
        """
        Get thoracic body mask, optionally using TotalSegmentor output.
        
        Args:
            ct_image (np.ndarray): CT image array
            segmentation (np.ndarray): Optional TotalSegmentor segmentation
            
        Returns:
            np.ndarray: Binary body mask
        """
        # Simple threshold-based body mask
        body_mask = (ct_image > -500) & (ct_image < 1000)
        
        # Could be refined using TotalSegmentor output if available
        if segmentation is not None:
            # Use any segmented structure to define body region
            body_mask = body_mask | (segmentation > 0)
        
        return body_mask.astype(np.uint8)


def download_totalsegmentor_models(output_dir=None):
    """
    Download TotalSegmentor pre-trained models.
    
    Args:
        output_dir (str): Directory to save models
        
    Returns:
        bool: True if successful
    """
    try:
        from totalsegmentor.libs import download_pretrained_weights
        
        if output_dir is None:
            # Use default TotalSegmentor directory
            output_dir = Path.home() / ".totalsegmentor" / "nnunet" / "results"
        
        logger.info(f"Downloading TotalSegmentor models to {output_dir}")
        download_pretrained_weights(str(output_dir))
        logger.info("Models downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download models: {e}")
        return False

```

---

