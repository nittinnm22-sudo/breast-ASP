"""
Radiomics Feature Extraction Module

This module provides functionality for extracting metabolic and shape
radiomics features from segmented breast tumors.
"""

import numpy as np
from scipy import ndimage
from skimage import measure
import warnings


class MetabolicRadiomics:
    """
    Extract metabolic radiomics features from FDG PET images.
    
    Metabolic features include SUV statistics, total lesion glycolysis (TLG),
    and metabolic tumor volume (MTV).
    """
    
    def __init__(self):
        """Initialize the metabolic radiomics extractor."""
        pass
        
    def extract_features(self, pet_image, tumor_mask, spacing=(1.0, 1.0, 1.0)):
        """
        Extract metabolic radiomics features.
        
        Args:
            pet_image (np.ndarray): 3D PET image array with SUV values
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            spacing (tuple): Voxel spacing in mm (z, y, x)
            
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
        
        # Metabolic tumor volume (MTV) - volume of tumor with SUV > 2.5
        mtv_threshold = 2.5
        mtv_mask = (pet_image > mtv_threshold) & (tumor_mask > 0)
        mtv_ml = float(np.sum(mtv_mask) * voxel_volume_ml)
        
        # Total lesion glycolysis (TLG)
        tlg = float(suv_mean * mtv_ml)
        
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
            'n_voxels': len(tumor_voxels)
        }
        
        return features
    
    def _calculate_suv_peak(self, pet_image, tumor_mask, spacing, 
                           sphere_volume_ml=1.0):
        """
        Calculate SUV peak - average SUV in sphere with highest average.
        
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
        
        # Create spherical structuring element
        sphere_radius_voxels = [int(np.ceil(sphere_radius * spacing[i] / spacing[0])) 
                               for i in range(3)]
        
        # Use maximum filter to find peak
        masked_pet = pet_image.copy()
        masked_pet[tumor_mask == 0] = 0
        
        # Simple approach: use uniform filter for averaging
        from scipy.ndimage import uniform_filter
        kernel_size = [max(3, int(2 * r + 1)) for r in sphere_radius_voxels]
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
            'n_voxels': 0
        }


class ShapeRadiomics:
    """
    Extract shape radiomics features from segmented tumors.
    
    Shape features include volume, surface area, sphericity, compactness,
    and other geometric properties.
    """
    
    def __init__(self):
        """Initialize the shape radiomics extractor."""
        pass
        
    def extract_features(self, tumor_mask, spacing=(1.0, 1.0, 1.0)):
        """
        Extract shape radiomics features.
        
        Args:
            tumor_mask (np.ndarray): Binary tumor segmentation mask
            spacing (tuple): Voxel spacing in mm (z, y, x)
            
        Returns:
            dict: Dictionary containing shape features
        """
        if not np.any(tumor_mask):
            return self._empty_features()
            
        # Calculate voxel volume
        voxel_volume_mm3 = np.prod(spacing)
        
        # Get region properties
        labeled = measure.label(tumor_mask, connectivity=3)
        regions = measure.regionprops(labeled)
        
        if len(regions) == 0:
            return self._empty_features()
            
        # Use largest component if multiple regions
        if len(regions) > 1:
            largest_region = max(regions, key=lambda r: r.area)
        else:
            largest_region = regions[0]
            
        # Volume
        volume_voxels = largest_region.area
        volume_mm3 = float(volume_voxels * voxel_volume_mm3)
        volume_ml = volume_mm3 / 1000.0
        
        # Surface area (approximate using marching cubes)
        try:
            verts, faces, normals, values = measure.marching_cubes(
                tumor_mask.astype(float), level=0.5, spacing=spacing
            )
            surface_area_mm2 = float(measure.mesh_surface_area(verts, faces))
        except (RuntimeError, ValueError):
            # Fallback if marching cubes fails
            surface_area_mm2 = self._approximate_surface_area(tumor_mask, spacing)
        
        # Sphericity: ratio of surface area of sphere with same volume to actual surface area
        sphere_surface_area = (36 * np.pi * volume_mm3 ** 2) ** (1/3)
        sphericity = float(sphere_surface_area / surface_area_mm2) if surface_area_mm2 > 0 else 0.0
        
        # Compactness (normalized)
        compactness_1 = float(volume_mm3 / (surface_area_mm2 ** (3/2))) if surface_area_mm2 > 0 else 0.0
        compactness_2 = float(36 * np.pi * (volume_mm3 ** 2) / (surface_area_mm2 ** 3)) if surface_area_mm2 > 0 else 0.0
        
        # Bounding box and dimensions
        bbox = largest_region.bbox  # (min_z, min_y, min_x, max_z, max_y, max_x)
        bbox_volume = float((bbox[3] - bbox[0]) * (bbox[4] - bbox[1]) * (bbox[5] - bbox[2]) * voxel_volume_mm3)
        
        # Maximum 3D diameter (approximate)
        max_diameter_mm = self._calculate_max_diameter(tumor_mask, spacing)
        
        # Elongation and flatness (based on eigenvalues of inertia tensor)
        try:
            # Get moments for scaled coordinates
            coords = np.argwhere(tumor_mask > 0)
            coords_scaled = coords * spacing
            
            # Calculate inertia tensor
            centered = coords_scaled - coords_scaled.mean(axis=0)
            inertia = np.dot(centered.T, centered) / len(coords)
            eigenvalues = np.linalg.eigvalsh(inertia)
            eigenvalues = np.sort(eigenvalues)[::-1]  # Sort descending
            
            if eigenvalues[0] > 0:
                elongation = float(np.sqrt(eigenvalues[1] / eigenvalues[0]))
                flatness = float(np.sqrt(eigenvalues[2] / eigenvalues[0]))
            else:
                elongation = 0.0
                flatness = 0.0
        except (ValueError, IndexError, np.linalg.LinAlgError) as e:
            elongation = 0.0
            flatness = 0.0
        
        # Solidity: ratio of volume to convex hull volume
        try:
            from scipy.spatial import ConvexHull, QhullError
            coords = np.argwhere(tumor_mask > 0) * spacing
            if len(coords) >= 4:
                hull = ConvexHull(coords)
                convex_volume = hull.volume
                solidity = float(volume_mm3 / convex_volume) if convex_volume > 0 else 0.0
            else:
                solidity = 1.0
        except (ImportError, ValueError, QhullError) as e:
            solidity = 1.0
            
        features = {
            'Volume_mm3': volume_mm3,
            'Volume_ml': volume_ml,
            'SurfaceArea_mm2': surface_area_mm2,
            'Sphericity': sphericity,
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
        """
        Approximate surface area when marching cubes fails.
        
        Args:
            mask (np.ndarray): Binary mask
            spacing (tuple): Voxel spacing
            
        Returns:
            float: Approximate surface area in mm²
        """
        # Count boundary voxels
        eroded = ndimage.binary_erosion(mask)
        boundary = mask & ~eroded
        n_boundary_voxels = np.sum(boundary)
        
        # Approximate area per boundary voxel
        voxel_face_area = np.mean([spacing[i] * spacing[j] 
                                   for i in range(3) for j in range(i+1, 3)])
        
        return float(n_boundary_voxels * voxel_face_area * 6)  # 6 faces per voxel
    
    def _calculate_max_diameter(self, mask, spacing):
        """
        Calculate maximum 3D diameter.
        
        Args:
            mask (np.ndarray): Binary mask
            spacing (tuple): Voxel spacing
            
        Returns:
            float: Maximum diameter in mm
        """
        coords = np.argwhere(mask > 0)
        if len(coords) < 2:
            return 0.0
            
        # Scale coordinates by spacing
        coords_scaled = coords * spacing
        
        # Sample points to avoid excessive computation
        if len(coords_scaled) > 1000:
            indices = np.random.choice(len(coords_scaled), 1000, replace=False)
            coords_sample = coords_scaled[indices]
        else:
            coords_sample = coords_scaled
        
        # Calculate pairwise distances
        from scipy.spatial.distance import pdist
        distances = pdist(coords_sample, metric='euclidean')
        
        return float(np.max(distances)) if len(distances) > 0 else 0.0
    
    def _empty_features(self):
        """Return empty feature dictionary."""
        return {
            'Volume_mm3': 0.0,
            'Volume_ml': 0.0,
            'SurfaceArea_mm2': 0.0,
            'Sphericity': 0.0,
            'Compactness1': 0.0,
            'Compactness2': 0.0,
            'MaxDiameter_mm': 0.0,
            'BoundingBoxVolume_mm3': 0.0,
            'Elongation': 0.0,
            'Flatness': 0.0,
            'Solidity': 0.0,
            'n_voxels': 0
        }
