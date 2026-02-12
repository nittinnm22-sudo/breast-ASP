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
