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
