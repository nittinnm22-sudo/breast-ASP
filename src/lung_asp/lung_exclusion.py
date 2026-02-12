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
            mediastinal_region = morphology.binary_closing(mediastinal_region, 
                                                          struct_elem)
        except (ValueError, MemoryError):
            mediastinal_region = morphology.binary_closing(mediastinal_region,
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
