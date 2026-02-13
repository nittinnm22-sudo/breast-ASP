"""
Breast Tumor Analysis Pipeline

This module provides a complete pipeline for FDG PET/CT breast tumor analysis
with axillary and axillary node exclusion.
"""

import numpy as np
from .segmentation import BreastTumorSegmenter
from .exclusion import AxillaryExcluder
from .radiomics import MetabolicRadiomics, ShapeRadiomics


class BreastTumorPipeline:
    """
    Complete pipeline for breast tumor segmentation and radiomics analysis
    with axillary and axillary node exclusion.
    """
    
    def __init__(self, suv_threshold=2.5, min_volume_mm3=100.0, 
                 exclusion_margin_mm=20.0):
        """
        Initialize the pipeline.
        
        Args:
            suv_threshold (float): SUV threshold for tumor segmentation
            min_volume_mm3 (float): Minimum tumor volume in mm³
            exclusion_margin_mm (float): Safety margin for exclusion regions
        """
        self.segmenter = BreastTumorSegmenter(suv_threshold, min_volume_mm3)
        self.excluder = AxillaryExcluder(exclusion_margin_mm)
        self.metabolic_extractor = MetabolicRadiomics()
        self.shape_extractor = ShapeRadiomics()
        
    def process(self, pet_image, ct_image=None, spacing=(1.0, 1.0, 1.0),
                axillary_bbox=None):
        """
        Process FDG PET/CT image to segment breast tumors and extract radiomics.
        
        This method:
        1. Segments primary breast tumors from PET image
        2. Excludes axillary and axillary lymph node regions
        3. Extracts metabolic radiomics features
        4. Extracts shape radiomics features
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            ct_image (np.ndarray): Optional 3D CT image for anatomical reference
            spacing (tuple): Voxel spacing in mm (z, y, x)
            axillary_bbox (dict): Optional explicit bounding boxes for axillary regions
            
        Returns:
            dict: Results containing:
                - 'tumor_mask': Binary mask of primary breast tumors (with exclusions)
                - 'tumor_mask_before_exclusion': Binary mask before axillary exclusion
                - 'metabolic_features': Dictionary of metabolic radiomics features
                - 'shape_features': Dictionary of shape radiomics features
                - 'combined_features': Combined metabolic and shape features
        """
        # Step 1: Segment primary breast tumors
        initial_mask = self.segmenter.segment_primary_breast_region(
            pet_image, ct_image, spacing
        )
        
        # Step 2: Exclude axillary and lymph node regions
        final_mask = self.excluder.apply_all_exclusions(
            initial_mask, pet_image, ct_image, spacing, axillary_bbox
        )
        
        # Step 3: Extract metabolic radiomics features
        metabolic_features = self.metabolic_extractor.extract_features(
            pet_image, final_mask, spacing
        )
        
        # Step 4: Extract shape radiomics features
        shape_features = self.shape_extractor.extract_features(
            final_mask, spacing
        )
        
        # Combine all features
        combined_features = {
            **metabolic_features,
            **shape_features
        }
        
        results = {
            'tumor_mask': final_mask,
            'tumor_mask_before_exclusion': initial_mask,
            'metabolic_features': metabolic_features,
            'shape_features': shape_features,
            'combined_features': combined_features
        }
        
        return results
    
    def process_and_save_features(self, pet_image, output_path, 
                                  ct_image=None, spacing=(1.0, 1.0, 1.0),
                                  axillary_bbox=None):
        """
        Process image and save features to CSV file.
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            output_path (str): Path to save CSV file
            ct_image (np.ndarray): Optional 3D CT image
            spacing (tuple): Voxel spacing in mm (z, y, x)
            axillary_bbox (dict): Optional axillary region bounding boxes
            
        Returns:
            dict: Processing results
        """
        import pandas as pd
        
        # Process image
        results = self.process(pet_image, ct_image, spacing, axillary_bbox)
        
        # Convert features to DataFrame
        features_df = pd.DataFrame([results['combined_features']])
        
        # Save to CSV
        features_df.to_csv(output_path, index=False)
        
        return results
