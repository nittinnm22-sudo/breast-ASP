"""
Breast Tumor Segmentation Module

This module provides functionality for segmenting primary breast tumors
from FDG PET/CT imaging data using SUV thresholding and connected component analysis.
"""

import numpy as np
from scipy import ndimage
from skimage import measure, morphology
import SimpleITK as sitk


class BreastTumorSegmenter:
    """
    Segments primary breast tumors from FDG PET/CT images.
    
    Attributes:
        suv_threshold (float): SUV threshold for tumor detection (default: 2.5)
        min_volume_mm3 (float): Minimum tumor volume in mm³ (default: 100.0)
    """
    
    def __init__(self, suv_threshold=2.5, min_volume_mm3=100.0):
        """
        Initialize the breast tumor segmenter.
        
        Args:
            suv_threshold (float): SUV threshold for initial segmentation
            min_volume_mm3 (float): Minimum tumor volume to consider
        """
        self.suv_threshold = suv_threshold
        self.min_volume_mm3 = min_volume_mm3
        
    def segment(self, pet_image, spacing=(1.0, 1.0, 1.0)):
        """
        Segment breast tumors from PET image.
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            spacing (tuple): Voxel spacing in mm (z, y, x)
            
        Returns:
            np.ndarray: Binary segmentation mask of breast tumors
        """
        # Apply SUV threshold
        binary_mask = pet_image >= self.suv_threshold
        
        # Remove small objects and holes
        # Note: Using max_size=10 for newer API (>= 0.26.0) to maintain 
        # consistent behavior with min_size=10 in older versions
        try:
            # Try newer API first (scikit-image >= 0.26.0)
            binary_mask = morphology.remove_small_objects(binary_mask, max_size=10)
            binary_mask = morphology.remove_small_holes(binary_mask, max_size=10)
        except TypeError:
            # Fall back to older API
            binary_mask = morphology.remove_small_objects(binary_mask, min_size=10)
            binary_mask = morphology.remove_small_holes(binary_mask, area_threshold=10)
        
        # Label connected components
        labeled_mask = measure.label(binary_mask, connectivity=3)
        
        # Filter by volume
        voxel_volume = np.prod(spacing)
        regions = measure.regionprops(labeled_mask)
        
        final_mask = np.zeros_like(binary_mask, dtype=bool)
        for region in regions:
            volume_mm3 = region.area * voxel_volume
            if volume_mm3 >= self.min_volume_mm3:
                final_mask[labeled_mask == region.label] = True
                
        return final_mask.astype(np.uint8)
    
    def segment_primary_breast_region(self, pet_image, ct_image=None, 
                                     spacing=(1.0, 1.0, 1.0)):
        """
        Segment primary breast tumors, focusing on breast region.
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            ct_image (np.ndarray): Optional 3D CT image for anatomical reference
            spacing (tuple): Voxel spacing in mm (z, y, x)
            
        Returns:
            np.ndarray: Binary mask of primary breast tumors
        """
        # Get initial segmentation
        tumor_mask = self.segment(pet_image, spacing)
        
        # If CT is available, use it to refine breast region
        if ct_image is not None:
            # Simple breast region definition based on CT density
            # Breast tissue typically has CT values between -200 and 100 HU
            breast_region = (ct_image > -200) & (ct_image < 100)
            tumor_mask = tumor_mask & breast_region
        
        return tumor_mask
    
    def get_largest_component(self, mask):
        """
        Extract the largest connected component from a binary mask.
        
        Args:
            mask (np.ndarray): Binary segmentation mask
            
        Returns:
            np.ndarray: Binary mask containing only the largest component
        """
        labeled = measure.label(mask, connectivity=3)
        if labeled.max() == 0:
            return mask
            
        regions = measure.regionprops(labeled)
        largest_region = max(regions, key=lambda r: r.area)
        
        return (labeled == largest_region.label).astype(np.uint8)
