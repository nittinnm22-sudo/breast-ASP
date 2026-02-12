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
