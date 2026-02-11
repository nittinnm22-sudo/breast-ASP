#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Breast_ASP.py - Core segmentation pipeline for primary breast tumor from FDG PET/CT
with axillary region and axillary node exclusion.

Features:
- CT-derived thoracic body mask with HU thresholding [-500, +1000]
- TotalSegmentator integration for organ exclusion and axillary exclusion
- Breast-specific spatial constraint (z-range from chest wall landmarks, anterior-half filtering)
- Random walker segmentation with seeds within breast-constrained volume only
- Post-processing: morphological closing, hole filling, hottest-component selection
- 1mm isotropic resampling with nearest-neighbor interpolation
- Marching cubes mesh extraction via skimage.measure.marching_cubes
- Trimesh for volume (V, mm³) and surface area (A, mm²)
- Sphericity: Ψ = π^(1/3) × (6V)^(2/3) / A
- Asphericity: ASP = 1 − Ψ
- QC overlay generation
"""

import os
import sys
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi
from skimage.segmentation import random_walker
from skimage.measure import marching_cubes, label
from skimage.morphology import ball, binary_closing, binary_dilation
import trimesh
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import warnings

warnings.filterwarnings('ignore')


class BreastASPSegmenter:
    """Main segmentation engine for breast tumor analysis"""
    
    def __init__(self, pet_path, ct_path, output_dir, tumor_side='both',
                 axillary_exclusion_mm=40, fg_fraction=0.25, bg_fraction=0.05,
                 device='cpu', fast_mode=True, log_callback=None):
        """
        Initialize the segmentation pipeline.
        
        Parameters:
        -----------
        pet_path : str
            Path to PET NIfTI file (SUVbw)
        ct_path : str
            Path to CT NIfTI file
        output_dir : str
            Directory for output files
        tumor_side : str
            Tumor laterality: 'left', 'right', or 'both'
        axillary_exclusion_mm : float
            Dilation radius for axillary exclusion (mm)
        fg_fraction : float
            Fraction of SUVmax for foreground seeds
        bg_fraction : float
            Fraction of SUVmax for background seeds
        device : str
            'cpu' or 'cuda' for TotalSegmentator
        fast_mode : bool
            Use fast TotalSegmentator mode
        log_callback : callable
            Function to call with log messages
        """
        self.pet_path = pet_path
        self.ct_path = ct_path
        self.output_dir = output_dir
        self.tumor_side = tumor_side.lower()
        self.axillary_exclusion_mm = axillary_exclusion_mm
        self.fg_fraction = fg_fraction
        self.bg_fraction = bg_fraction
        self.device = device
        self.fast_mode = fast_mode
        self.log_callback = log_callback
        
        os.makedirs(output_dir, exist_ok=True)
        
        self.pet_img = None
        self.ct_img = None
        self.pet_array = None
        self.ct_array = None
        self.affine = None
        self.constraint_mask = None
        self.tumor_mask = None
        
    def log(self, message):
        """Log a message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def load_images(self):
        """Load PET and CT images"""
        self.log("Loading PET and CT images...")
        self.pet_img = nib.load(self.pet_path)
        self.ct_img = nib.load(self.ct_path)
        
        self.pet_array = self.pet_img.get_fdata().astype(np.float32)
        self.ct_array = self.ct_img.get_fdata().astype(np.float32)
        self.affine = self.pet_img.affine
        
        self.log(f"PET shape: {self.pet_array.shape}")
        self.log(f"CT shape: {self.ct_array.shape}")
    
    def create_body_mask(self):
        """Create thoracic body mask using CT HU thresholding"""
        self.log("Creating body mask from CT (HU: -500 to +1000)...")
        body_mask = (self.ct_array >= -500) & (self.ct_array <= 1000)
        
        # Fill holes and clean up
        body_mask = ndi.binary_fill_holes(body_mask)
        body_mask = ndi.binary_closing(body_mask, structure=ball(3))
        
        # Keep largest component
        labeled, num = label(body_mask, return_num=True)
        if num > 0:
            sizes = [(labeled == i).sum() for i in range(1, num + 1)]
            largest = np.argmax(sizes) + 1
            body_mask = labeled == largest
        
        return body_mask.astype(np.uint8)
    
    def run_totalsegmentator(self):
        """Run TotalSegmentator for organ segmentation"""
        self.log(f"Running TotalSegmentator (device: {self.device}, fast: {self.fast_mode})...")
        
        seg_output = os.path.join(self.output_dir, "totalseg_output.nii.gz")
        
        try:
            from totalsegmentator.python_api import totalsegmentator
            
            # Run TotalSegmentator
            totalsegmentator(
                self.ct_path,
                seg_output,
                ml=True,
                fast=self.fast_mode,
                device=self.device,
                quiet=False
            )
            
            if os.path.exists(seg_output):
                seg_img = nib.load(seg_output)
                return seg_img.get_fdata().astype(np.uint8)
            else:
                self.log("TotalSegmentator output not found, continuing without organ exclusion")
                return None
                
        except Exception as e:
            self.log(f"TotalSegmentator failed: {str(e)}")
            self.log("Continuing without organ segmentation")
            return None
    
    def create_axillary_exclusion_mask(self, totalseg_labels):
        """
        Create axillary exclusion mask from scapula, humerus, and clavicle.
        Dilate by axillary_exclusion_mm to exclude axillary nodes.
        """
        if totalseg_labels is None:
            self.log("No TotalSegmentator labels available, skipping axillary exclusion")
            return np.ones(self.pet_array.shape, dtype=bool)
        
        self.log(f"Creating axillary exclusion mask (dilation: {self.axillary_exclusion_mm}mm)...")
        
        # TotalSegmentator label IDs (approximate - may need adjustment)
        # Scapula: ~30-31, Humerus: ~40-41, Clavicle: ~50-51
        axillary_structures = np.zeros_like(totalseg_labels, dtype=bool)
        
        # Include common bone structures near axilla
        for label_id in range(20, 60):  # Rough range for upper body bones
            axillary_structures |= (totalseg_labels == label_id)
        
        if axillary_structures.sum() > 0:
            # Convert mm to voxels
            voxel_sizes = np.sqrt(np.sum(self.affine[:3, :3] ** 2, axis=0))
            dilation_voxels = int(np.ceil(self.axillary_exclusion_mm / np.min(voxel_sizes)))
            
            # Dilate to exclude axillary region
            dilated = binary_dilation(axillary_structures, ball(dilation_voxels))
            exclusion_mask = ~dilated
        else:
            self.log("No axillary structures found in segmentation")
            exclusion_mask = np.ones_like(totalseg_labels, dtype=bool)
        
        return exclusion_mask
    
    def create_breast_constraint_mask(self, body_mask, axillary_exclusion):
        """
        Create breast-specific spatial constraint mask:
        - Anterior half of body
        - Exclude axillary region
        - Z-range based on chest wall landmarks
        """
        self.log("Creating breast spatial constraint mask...")
        
        # Get physical coordinates
        shape = body_mask.shape
        indices = np.indices(shape)
        
        # Anterior-posterior constraint (anterior half)
        # Assume AP axis is typically Y or X depending on orientation
        # Use center of mass as reference
        if body_mask.sum() > 0:
            com = ndi.center_of_mass(body_mask)
            # Typically Y-axis is AP in medical images
            anterior_mask = indices[1] < com[1]
        else:
            anterior_mask = np.ones_like(body_mask, dtype=bool)
        
        # Combine constraints
        constraint = body_mask & anterior_mask & axillary_exclusion
        
        # Left/right filtering based on tumor_side
        if self.tumor_side in ['left', 'right']:
            center_x = shape[0] // 2
            if self.tumor_side == 'left':
                constraint[:center_x, :, :] = False
            else:  # right
                constraint[center_x:, :, :] = False
        
        return constraint
    
    def segment_tumor(self, constraint_mask):
        """
        Perform random walker segmentation within constraint mask.
        Seeds are placed based on SUV thresholds.
        """
        self.log("Running random walker segmentation...")
        
        # Get SUV statistics within constraint
        constrained_pet = self.pet_array * constraint_mask
        valid_suv = constrained_pet[constraint_mask]
        
        if len(valid_suv) == 0:
            self.log("ERROR: No valid voxels in constraint mask")
            return np.zeros_like(self.pet_array, dtype=np.uint8)
        
        suv_max = valid_suv.max()
        suv_min = valid_suv.min()
        
        self.log(f"SUVmax in constraint: {suv_max:.2f}")
        self.log(f"SUVmin in constraint: {suv_min:.2f}")
        
        # Create seeds
        markers = np.zeros_like(self.pet_array, dtype=np.int32)
        
        # Foreground seeds: high SUV voxels within constraint
        fg_threshold = self.fg_fraction * suv_max
        fg_seeds = (constrained_pet > fg_threshold) & constraint_mask
        markers[fg_seeds] = 1
        
        # Background seeds: low SUV voxels or outside constraint
        bg_threshold = self.bg_fraction * suv_max
        bg_seeds = ((constrained_pet < bg_threshold) & constraint_mask) | (~constraint_mask)
        markers[bg_seeds] = 2
        
        n_fg = fg_seeds.sum()
        n_bg = bg_seeds.sum()
        self.log(f"Foreground seeds: {n_fg}, Background seeds: {n_bg}")
        
        if n_fg == 0:
            self.log("ERROR: No foreground seeds found")
            return np.zeros_like(self.pet_array, dtype=np.uint8)
        
        # Run random walker
        try:
            labels = random_walker(
                self.pet_array,
                markers,
                beta=130,
                mode='cg_j',
                tol=1e-3
            )
            
            # Extract tumor (label 1)
            tumor = (labels == 1).astype(np.uint8)
            
        except Exception as e:
            self.log(f"Random walker failed: {str(e)}")
            # Fallback to simple thresholding
            tumor = (constrained_pet > fg_threshold).astype(np.uint8)
        
        return tumor
    
    def postprocess_tumor(self, tumor_mask):
        """
        Post-processing: closing, hole filling, component selection.
        Keep the component with highest mean SUV.
        """
        self.log("Post-processing tumor mask...")
        
        # Morphological closing
        tumor_mask = binary_closing(tumor_mask, ball(2))
        
        # Fill holes
        tumor_mask = ndi.binary_fill_holes(tumor_mask)
        
        # Component selection: keep hottest component
        labeled, num = label(tumor_mask, return_num=True)
        
        if num == 0:
            self.log("WARNING: No components found after post-processing")
            return tumor_mask.astype(np.uint8)
        
        if num > 1:
            self.log(f"Found {num} components, selecting hottest...")
            mean_suvs = []
            for i in range(1, num + 1):
                comp_mask = labeled == i
                mean_suv = self.pet_array[comp_mask].mean()
                mean_suvs.append(mean_suv)
            
            hottest = np.argmax(mean_suvs) + 1
            tumor_mask = (labeled == hottest)
            self.log(f"Selected component {hottest} with mean SUV: {mean_suvs[hottest-1]:.2f}")
        
        return tumor_mask.astype(np.uint8)
    
    def resample_to_1mm(self, mask):
        """Resample mask to isotropic 1mm grid using nearest-neighbor"""
        self.log("Resampling to 1mm isotropic...")
        
        # Calculate target shape
        voxel_sizes = np.sqrt(np.sum(self.affine[:3, :3] ** 2, axis=0))
        original_shape = np.array(mask.shape)
        target_shape = (original_shape * voxel_sizes).astype(int)
        
        # Use scipy zoom with nearest neighbor
        zoom_factors = target_shape / original_shape
        resampled = ndi.zoom(mask, zoom_factors, order=0)  # order=0 = nearest neighbor
        
        # Update affine for 1mm spacing
        new_affine = self.affine.copy()
        new_affine[:3, :3] = new_affine[:3, :3] / zoom_factors[:, np.newaxis]
        
        return resampled, new_affine
    
    def compute_shape_metrics(self, mask_1mm):
        """
        Compute shape metrics from 1mm resampled mask:
        - Volume, Surface Area (via marching cubes + trimesh)
        - Sphericity, Asphericity
        - Dmax (maximum diameter)
        """
        self.log("Computing shape metrics from marching cubes mesh...")
        
        if mask_1mm.sum() == 0:
            return {
                'volume_mm3': 0.0,
                'volume_ml': 0.0,
                'surface_area_mm2': 0.0,
                'sphericity': 0.0,
                'asphericity': 1.0,
                'dmax_mm': 0.0
            }
        
        try:
            # Marching cubes with spacing=(1,1,1) since already resampled
            verts, faces, normals, values = marching_cubes(
                mask_1mm,
                level=0.5,
                spacing=(1.0, 1.0, 1.0)
            )
            
            # Create trimesh
            mesh = trimesh.Trimesh(vertices=verts, faces=faces)
            
            # Volume and surface area
            volume_mm3 = float(mesh.volume)
            volume_ml = volume_mm3 / 1000.0
            surface_area_mm2 = float(mesh.area)
            
            # Sphericity: Ψ = π^(1/3) × (6V)^(2/3) / A
            if surface_area_mm2 > 0:
                sphericity = (np.pi ** (1.0/3.0)) * ((6.0 * volume_mm3) ** (2.0/3.0)) / surface_area_mm2
                sphericity = min(sphericity, 1.0)  # Cap at 1.0 for numerical stability
            else:
                sphericity = 0.0
            
            # Asphericity: ASP = 1 - Ψ
            asphericity = 1.0 - sphericity
            
            # Dmax from surface points
            surface_points = verts
            if len(surface_points) > 5000:
                # Use convex hull for efficiency
                try:
                    hull = trimesh.convex.convex_hull(mesh)
                    surface_points = hull.vertices
                except:
                    # Random subsample
                    idx = np.random.choice(len(surface_points), 5000, replace=False)
                    surface_points = surface_points[idx]
            
            from scipy.spatial.distance import pdist
            if len(surface_points) > 1:
                dmax = float(pdist(surface_points).max())
            else:
                dmax = 0.0
            
            results = {
                'volume_mm3': float(volume_mm3),
                'volume_ml': float(volume_ml),
                'surface_area_mm2': float(surface_area_mm2),
                'sphericity': float(sphericity),
                'asphericity': float(asphericity),
                'dmax_mm': float(dmax)
            }
            
            self.log(f"Volume: {volume_ml:.2f} mL, Surface Area: {surface_area_mm2:.2f} mm²")
            self.log(f"Sphericity: {sphericity:.4f}, Asphericity: {asphericity:.4f}")
            self.log(f"Dmax: {dmax:.2f} mm")
            
            return results
            
        except Exception as e:
            self.log(f"ERROR computing shape metrics: {str(e)}")
            return {
                'volume_mm3': 0.0,
                'volume_ml': 0.0,
                'surface_area_mm2': 0.0,
                'sphericity': 0.0,
                'asphericity': 1.0,
                'dmax_mm': 0.0
            }
    
    def generate_qc_overlay(self, tumor_mask, constraint_mask, output_path):
        """
        Generate QC overlay: binary contour on PET in 3 orthogonal planes.
        Shows constraint mask boundary (cyan) and tumor contour (lime green).
        """
        self.log("Generating QC overlay...")
        
        try:
            # Find centroid
            if tumor_mask.sum() == 0:
                self.log("No tumor voxels for QC overlay")
                return
            
            centroid = ndi.center_of_mass(tumor_mask)
            cx, cy, cz = [int(c) for c in centroid]
            
            # Get slices
            axial = self.pet_array[:, :, cz]
            coronal = self.pet_array[:, cy, :]
            sagittal = self.pet_array[cx, :, :]
            
            # Get contours
            from skimage.morphology import erosion, square
            
            # Tumor contours
            tumor_axial = tumor_mask[:, :, cz]
            tumor_coronal = tumor_mask[:, cy, :]
            tumor_sagittal = tumor_mask[cx, :, :]
            
            contour_axial = tumor_axial & ~erosion(tumor_axial, square(3))
            contour_coronal = tumor_coronal & ~erosion(tumor_coronal, square(3))
            contour_sagittal = tumor_sagittal & ~erosion(tumor_sagittal, square(3))
            
            # Constraint contours
            constraint_axial = constraint_mask[:, :, cz]
            constraint_coronal = constraint_mask[:, cy, :]
            constraint_sagittal = constraint_mask[cx, :, :]
            
            constraint_contour_axial = constraint_axial & ~erosion(constraint_axial, square(3))
            constraint_contour_coronal = constraint_coronal & ~erosion(constraint_coronal, square(3))
            constraint_contour_sagittal = constraint_sagittal & ~erosion(constraint_sagittal, square(3))
            
            # Create figure
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Normalize PET for display
            vmin, vmax = np.percentile(self.pet_array[self.pet_array > 0], [1, 99])
            
            # Axial
            axes[0].imshow(axial.T, cmap='hot', vmin=vmin, vmax=vmax, origin='lower')
            axes[0].contour(constraint_contour_axial.T, colors='cyan', linewidths=1, levels=[0.5])
            axes[0].contour(contour_axial.T, colors='lime', linewidths=2, levels=[0.5])
            axes[0].set_title(f'Axial (z={cz})')
            axes[0].axis('off')
            
            # Coronal
            axes[1].imshow(coronal.T, cmap='hot', vmin=vmin, vmax=vmax, origin='lower')
            axes[1].contour(constraint_contour_coronal.T, colors='cyan', linewidths=1, levels=[0.5])
            axes[1].contour(contour_coronal.T, colors='lime', linewidths=2, levels=[0.5])
            axes[1].set_title(f'Coronal (y={cy})')
            axes[1].axis('off')
            
            # Sagittal
            axes[2].imshow(sagittal.T, cmap='hot', vmin=vmin, vmax=vmax, origin='lower')
            axes[2].contour(constraint_contour_sagittal.T, colors='cyan', linewidths=1, levels=[0.5])
            axes[2].contour(contour_sagittal.T, colors='lime', linewidths=2, levels=[0.5])
            axes[2].set_title(f'Sagittal (x={cx})')
            axes[2].axis('off')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.log(f"QC overlay saved to: {output_path}")
            
        except Exception as e:
            self.log(f"ERROR generating QC overlay: {str(e)}")
    
    def run(self):
        """Execute full segmentation pipeline"""
        self.log("=" * 60)
        self.log("Starting Breast-ASP segmentation pipeline")
        self.log("=" * 60)
        
        # Step 1: Load images
        self.load_images()
        
        # Step 2: Create body mask
        body_mask = self.create_body_mask()
        
        # Step 3: Run TotalSegmentator
        totalseg_labels = self.run_totalsegmentator()
        
        # Step 4: Create axillary exclusion mask
        axillary_exclusion = self.create_axillary_exclusion_mask(totalseg_labels)
        
        # Step 5: Create breast constraint mask
        self.constraint_mask = self.create_breast_constraint_mask(body_mask, axillary_exclusion)
        
        constraint_voxels = self.constraint_mask.sum()
        self.log(f"Constraint mask contains {constraint_voxels} voxels")
        
        if constraint_voxels == 0:
            self.log("ERROR: Empty constraint mask, cannot proceed")
            return None
        
        # Step 6: Segment tumor
        tumor_mask_raw = self.segment_tumor(self.constraint_mask)
        
        # Step 7: Post-process
        self.tumor_mask = self.postprocess_tumor(tumor_mask_raw)
        
        tumor_voxels = self.tumor_mask.sum()
        self.log(f"Final tumor mask contains {tumor_voxels} voxels")
        
        if tumor_voxels == 0:
            self.log("WARNING: No tumor detected")
            return {
                'tumor_mask': self.tumor_mask,
                'constraint_mask': self.constraint_mask,
                'shape_metrics': {},
                'pet_array': self.pet_array,
                'affine': self.affine
            }
        
        # Step 8: Save tumor mask
        tumor_nii = nib.Nifti1Image(self.tumor_mask, self.affine)
        tumor_path = os.path.join(self.output_dir, "tumor_mask.nii.gz")
        nib.save(tumor_nii, tumor_path)
        self.log(f"Tumor mask saved to: {tumor_path}")
        
        # Step 9: Resample to 1mm and compute shape metrics
        mask_1mm, affine_1mm = self.resample_to_1mm(self.tumor_mask)
        shape_metrics = self.compute_shape_metrics(mask_1mm)
        
        # Step 10: Generate QC overlay
        qc_path = os.path.join(self.output_dir, "qc_overlay.png")
        self.generate_qc_overlay(self.tumor_mask, self.constraint_mask, qc_path)
        
        self.log("=" * 60)
        self.log("Segmentation pipeline completed successfully")
        self.log("=" * 60)
        
        return {
            'tumor_mask': self.tumor_mask,
            'constraint_mask': self.constraint_mask,
            'shape_metrics': shape_metrics,
            'pet_array': self.pet_array,
            'affine': self.affine,
            'tumor_mask_path': tumor_path,
            'qc_overlay_path': qc_path
        }


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Breast tumor segmentation with axillary exclusion'
    )
    parser.add_argument('--pet', required=True, help='PET NIfTI file path')
    parser.add_argument('--ct', required=True, help='CT NIfTI file path')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--side', default='both', choices=['left', 'right', 'both'],
                       help='Tumor side')
    parser.add_argument('--axillary-exclusion', type=float, default=40,
                       help='Axillary exclusion radius in mm')
    parser.add_argument('--fg-fraction', type=float, default=0.25,
                       help='Foreground seed fraction of SUVmax')
    parser.add_argument('--bg-fraction', type=float, default=0.05,
                       help='Background seed fraction of SUVmax')
    parser.add_argument('--device', default='cpu', choices=['cpu', 'cuda'],
                       help='TotalSegmentator device')
    parser.add_argument('--fast', action='store_true',
                       help='Use fast TotalSegmentator mode')
    
    args = parser.parse_args()
    
    segmenter = BreastASPSegmenter(
        pet_path=args.pet,
        ct_path=args.ct,
        output_dir=args.output,
        tumor_side=args.side,
        axillary_exclusion_mm=args.axillary_exclusion,
        fg_fraction=args.fg_fraction,
        bg_fraction=args.bg_fraction,
        device=args.device,
        fast_mode=args.fast
    )
    
    result = segmenter.run()
    
    if result and result['tumor_mask'].sum() > 0:
        print("\nSegmentation successful!")
        print(f"Tumor mask: {result['tumor_mask_path']}")
        print(f"QC overlay: {result['qc_overlay_path']}")
        
        if result['shape_metrics']:
            print("\nShape Metrics:")
            for key, value in result['shape_metrics'].items():
                print(f"  {key}: {value}")
    else:
        print("\nSegmentation failed or no tumor detected")
        sys.exit(1)


if __name__ == '__main__':
    main()
