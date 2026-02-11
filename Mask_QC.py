#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mask_QC.py - Standalone QC overlay generator for breast tumor segmentation

Generates high-resolution QC overlays showing:
- Binary contour superimposed on co-registered PET
- 3 orthogonal planes (axial, coronal, sagittal) at lesion centroid
- Constraint mask boundary (cyan) and tumor contour (lime green)
- Saves as high-resolution PNG (300 DPI default)

Can be run standalone with command-line arguments or imported as a module.
"""

import os
import argparse
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy import ndimage as ndi
from skimage.morphology import erosion, dilation, square, cube


def generate_qc_overlay(tumor_mask_path, pet_path, output_path,
                       constraint_mask_path=None, dpi=300):
    """
    Generate QC overlay with tumor and constraint contours on PET.
    
    Parameters:
    -----------
    tumor_mask_path : str
        Path to tumor mask NIfTI file
    pet_path : str
        Path to PET NIfTI file
    output_path : str
        Path to save output PNG
    constraint_mask_path : str, optional
        Path to constraint mask NIfTI file
    dpi : int
        Output resolution in DPI
    
    Returns:
    --------
    success : bool
    """
    
    print(f"Loading tumor mask: {tumor_mask_path}")
    tumor_img = nib.load(tumor_mask_path)
    tumor_mask = tumor_img.get_fdata().astype(bool)
    
    print(f"Loading PET: {pet_path}")
    pet_img = nib.load(pet_path)
    pet_array = pet_img.get_fdata()
    
    if constraint_mask_path and os.path.exists(constraint_mask_path):
        print(f"Loading constraint mask: {constraint_mask_path}")
        constraint_img = nib.load(constraint_mask_path)
        constraint_mask = constraint_img.get_fdata().astype(bool)
    else:
        print("No constraint mask provided")
        constraint_mask = None
    
    # Find tumor centroid
    if tumor_mask.sum() == 0:
        print("ERROR: Empty tumor mask")
        return False
    
    centroid = ndi.center_of_mass(tumor_mask)
    cx, cy, cz = [int(round(c)) for c in centroid]
    
    print(f"Tumor centroid: ({cx}, {cy}, {cz})")
    print(f"Tumor volume: {tumor_mask.sum()} voxels")
    
    # Clamp to valid indices
    cx = max(0, min(cx, tumor_mask.shape[0] - 1))
    cy = max(0, min(cy, tumor_mask.shape[1] - 1))
    cz = max(0, min(cz, tumor_mask.shape[2] - 1))
    
    # Extract slices
    pet_axial = pet_array[:, :, cz]
    pet_coronal = pet_array[:, cy, :]
    pet_sagittal = pet_array[cx, :, :]
    
    tumor_axial = tumor_mask[:, :, cz]
    tumor_coronal = tumor_mask[:, cy, :]
    tumor_sagittal = tumor_mask[cx, :, :]
    
    # Compute contours via erosion
    print("Computing contours...")
    
    try:
        # 2D erosion for contours
        contour_axial = tumor_axial & ~erosion(tumor_axial, square(3))
        contour_coronal = tumor_coronal & ~erosion(tumor_coronal, square(3))
        contour_sagittal = tumor_sagittal & ~erosion(tumor_sagittal, square(3))
    except Exception as e:
        print(f"Warning: Erosion failed, using original mask: {e}")
        contour_axial = tumor_axial
        contour_coronal = tumor_coronal
        contour_sagittal = tumor_sagittal
    
    # Constraint mask contours if available
    if constraint_mask is not None:
        constraint_axial = constraint_mask[:, :, cz]
        constraint_coronal = constraint_mask[:, cy, :]
        constraint_sagittal = constraint_mask[cx, :, :]
        
        try:
            constraint_contour_axial = constraint_axial & ~erosion(constraint_axial, square(3))
            constraint_contour_coronal = constraint_coronal & ~erosion(constraint_coronal, square(3))
            constraint_contour_sagittal = constraint_sagittal & ~erosion(constraint_sagittal, square(3))
        except:
            constraint_contour_axial = constraint_axial
            constraint_contour_coronal = constraint_coronal
            constraint_contour_sagittal = constraint_sagittal
    else:
        constraint_contour_axial = None
        constraint_contour_coronal = None
        constraint_contour_sagittal = None
    
    # Normalize PET for display
    pet_valid = pet_array[pet_array > 0]
    if len(pet_valid) > 0:
        vmin, vmax = np.percentile(pet_valid, [1, 99])
    else:
        vmin, vmax = 0, 1
    
    print(f"PET display range: [{vmin:.2f}, {vmax:.2f}]")
    
    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Axial
    axes[0].imshow(pet_axial.T, cmap='hot', vmin=vmin, vmax=vmax, origin='lower', interpolation='bilinear')
    if constraint_contour_axial is not None:
        axes[0].contour(constraint_contour_axial.T, colors='cyan', linewidths=1.5, levels=[0.5], alpha=0.8)
    axes[0].contour(contour_axial.T, colors='lime', linewidths=2.5, levels=[0.5], alpha=1.0)
    axes[0].set_title(f'Axial (z={cz})', fontsize=12, fontweight='bold')
    axes[0].axis('off')
    
    # Coronal
    axes[1].imshow(pet_coronal.T, cmap='hot', vmin=vmin, vmax=vmax, origin='lower', interpolation='bilinear')
    if constraint_contour_coronal is not None:
        axes[1].contour(constraint_contour_coronal.T, colors='cyan', linewidths=1.5, levels=[0.5], alpha=0.8)
    axes[1].contour(contour_coronal.T, colors='lime', linewidths=2.5, levels=[0.5], alpha=1.0)
    axes[1].set_title(f'Coronal (y={cy})', fontsize=12, fontweight='bold')
    axes[1].axis('off')
    
    # Sagittal
    axes[2].imshow(pet_sagittal.T, cmap='hot', vmin=vmin, vmax=vmax, origin='lower', interpolation='bilinear')
    if constraint_contour_sagittal is not None:
        axes[2].contour(constraint_contour_sagittal.T, colors='cyan', linewidths=1.5, levels=[0.5], alpha=0.8)
    axes[2].contour(contour_sagittal.T, colors='lime', linewidths=2.5, levels=[0.5], alpha=1.0)
    axes[2].set_title(f'Sagittal (x={cx})', fontsize=12, fontweight='bold')
    axes[2].axis('off')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='lime', edgecolor='lime', label='Tumor')]
    if constraint_contour_axial is not None:
        legend_elements.insert(0, Patch(facecolor='cyan', edgecolor='cyan', label='Constraint'))
    fig.legend(handles=legend_elements, loc='upper center', ncol=2, frameon=False, fontsize=10)
    
    plt.suptitle('Tumor Segmentation QC', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save
    print(f"Saving to: {output_path}")
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("QC overlay generated successfully!")
    return True


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Generate QC overlay for tumor segmentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with tumor mask and PET
  python Mask_QC.py --tumor tumor_mask.nii.gz --pet pet.nii.gz --output qc.png
  
  # Include constraint mask
  python Mask_QC.py --tumor tumor_mask.nii.gz --pet pet.nii.gz \\
                    --constraint constraint_mask.nii.gz --output qc.png
  
  # High resolution output
  python Mask_QC.py --tumor tumor_mask.nii.gz --pet pet.nii.gz \\
                    --output qc.png --dpi 600
        """
    )
    
    parser.add_argument('--tumor', required=True,
                       help='Path to tumor mask NIfTI file')
    parser.add_argument('--pet', required=True,
                       help='Path to PET NIfTI file')
    parser.add_argument('--output', required=True,
                       help='Path to output PNG file')
    parser.add_argument('--constraint', default=None,
                       help='Path to constraint mask NIfTI file (optional)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='Output resolution in DPI (default: 300)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.tumor):
        print(f"ERROR: Tumor mask not found: {args.tumor}")
        return 1
    
    if not os.path.exists(args.pet):
        print(f"ERROR: PET file not found: {args.pet}")
        return 1
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate overlay
    success = generate_qc_overlay(
        tumor_mask_path=args.tumor,
        pet_path=args.pet,
        output_path=args.output,
        constraint_mask_path=args.constraint,
        dpi=args.dpi
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
