"""
Axillary and Axillary Node Exclusion Module

This module provides functionality for excluding axillary (armpit) regions
and axillary lymph nodes from breast tumor segmentation masks.
"""

import numpy as np
from scipy import ndimage
from skimage import measure, morphology


class AxillaryExcluder:
    """
    Excludes axillary and axillary lymph node regions from tumor segmentation.
    
    The axillary region is defined as the armpit area and includes lymph nodes
    that should be excluded from primary breast tumor analysis.
    """
    
    def __init__(self, exclusion_margin_mm=20.0):
        """
        Initialize the axillary excluder.
        
        Args:
            exclusion_margin_mm (float): Safety margin around excluded regions in mm
        """
        self.exclusion_margin_mm = exclusion_margin_mm
        
    def exclude_axillary_regions(self, tumor_mask, pet_image, 
                                 spacing=(1.0, 1.0, 1.0)):
        """
        Exclude axillary and lymph node regions from tumor mask.
        
        This method identifies and removes axillary regions based on:
        1. Anatomical location (lateral and superior regions)
        2. SUV patterns typical of lymph nodes
        3. Shape characteristics
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            pet_image (np.ndarray): 3D PET image array with SUV values
            spacing (tuple): Voxel spacing in mm (z, y, x)
            
        Returns:
            np.ndarray: Tumor mask with axillary regions excluded
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
        
        # Identify and remove axillary regions
        for region in regions:
            # Get region properties
            centroid_z, centroid_y, centroid_x = region.centroid
            
            # Axillary regions are typically:
            # 1. Lateral (far from center in x)
            # 2. Superior (in upper portion of image)
            # 3. Small to medium sized
            lateral_distance = abs(centroid_x - center_x)
            is_lateral = lateral_distance > nx * 0.25  # More than 25% from center
            is_superior = centroid_z < nz * 0.4  # In upper 40% of image
            
            # Calculate region characteristics
            volume_mm3 = region.area * np.prod(spacing)
            is_small_to_medium = volume_mm3 < 5000  # Less than 5 cm³
            
            # Axillary lymph nodes typically have:
            # - Elongated or rounded shape
            # - Small to medium volume
            # - Lateral and superior location
            if is_lateral and is_superior and is_small_to_medium:
                # Mark as axillary region to exclude
                filtered_mask[labeled_mask == region.label] = 0
                
        return filtered_mask
    
    def exclude_by_location(self, tumor_mask, axillary_bbox=None):
        """
        Exclude regions based on explicit axillary bounding box.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            axillary_bbox (dict): Dictionary with 'left' and 'right' bounding boxes
                                 Each bbox is (z_min, z_max, y_min, y_max, x_min, x_max)
            
        Returns:
            np.ndarray: Tumor mask with specified regions excluded
        """
        if axillary_bbox is None:
            return tumor_mask
            
        filtered_mask = tumor_mask.copy()
        
        # Exclude left axillary region
        if 'left' in axillary_bbox:
            z_min, z_max, y_min, y_max, x_min, x_max = axillary_bbox['left']
            filtered_mask[z_min:z_max, y_min:y_max, x_min:x_max] = 0
            
        # Exclude right axillary region
        if 'right' in axillary_bbox:
            z_min, z_max, y_min, y_max, x_min, x_max = axillary_bbox['right']
            filtered_mask[z_min:z_max, y_min:y_max, x_min:x_max] = 0
            
        return filtered_mask
    
    def exclude_lymph_nodes_by_suv(self, tumor_mask, pet_image, 
                                   node_suv_max=10.0, spacing=(1.0, 1.0, 1.0)):
        """
        Exclude potential lymph nodes based on SUV characteristics.
        
        Lymph nodes often show different SUV patterns than primary tumors.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            pet_image (np.ndarray): 3D PET image array with SUV values
            node_suv_max (float): Maximum SUV threshold for lymph nodes
            spacing (tuple): Voxel spacing in mm (z, y, x)
            
        Returns:
            np.ndarray: Tumor mask with lymph nodes excluded
        """
        if not np.any(tumor_mask):
            return tumor_mask
            
        filtered_mask = tumor_mask.copy()
        labeled_mask = measure.label(tumor_mask, connectivity=3)
        regions = measure.regionprops(labeled_mask, intensity_image=pet_image)
        
        for region in regions:
            # Get SUV statistics for the region
            region_suv_max = region.intensity_max
            region_suv_mean = region.intensity_mean
            
            # Calculate volume
            volume_mm3 = region.area * np.prod(spacing)
            
            # Lymph nodes typically have:
            # - Moderate SUV (not extremely high)
            # - Small volume (< 3 cm³)
            # - More uniform uptake
            is_moderate_suv = region_suv_max < node_suv_max
            is_small = volume_mm3 < 3000
            is_uniform = (region_suv_max / region_suv_mean) < 2.0
            
            if is_moderate_suv and is_small and is_uniform:
                filtered_mask[labeled_mask == region.label] = 0
                
        return filtered_mask
    
    def apply_all_exclusions(self, tumor_mask, pet_image, ct_image=None,
                            spacing=(1.0, 1.0, 1.0), axillary_bbox=None):
        """
        Apply all axillary exclusion methods.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            pet_image (np.ndarray): 3D PET image array with SUV values
            ct_image (np.ndarray): Optional 3D CT image for anatomical reference
            spacing (tuple): Voxel spacing in mm (z, y, x)
            axillary_bbox (dict): Optional explicit bounding boxes for axillary regions
            
        Returns:
            np.ndarray: Tumor mask with all axillary regions excluded
        """
        # Apply location-based exclusion
        filtered_mask = self.exclude_axillary_regions(tumor_mask, pet_image, spacing)
        
        # Apply SUV-based lymph node exclusion
        filtered_mask = self.exclude_lymph_nodes_by_suv(filtered_mask, pet_image, 
                                                        spacing=spacing)
        
        # Apply explicit bounding box exclusion if provided
        if axillary_bbox is not None:
            filtered_mask = self.exclude_by_location(filtered_mask, axillary_bbox)
            
        return filtered_mask
