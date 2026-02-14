"""
Mask QC Overlay Generation Module.

Creates high-resolution QC overlay images with:
- 3 orthogonal planes (axial, coronal, sagittal) at lesion centroid
- Binary tumor contour on co-registered PET uptake
- Constraint mask boundary as dashed cyan contour
- CT with tumor mask overlay
- 300 DPI output
"""
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from skimage import measure
import logging

logger = logging.getLogger(__name__)


def generate_qc_overlays(
    pet_nifti_path,
    ct_nifti_path,
    tumor_mask_path,
    constraint_mask_path,
    output_path,
    dpi=300
):
    """
    Generate comprehensive QC overlay images.
    
    Parameters
    ----------
    pet_nifti_path : str or Path
        Path to PET NIfTI file
    ct_nifti_path : str or Path
        Path to CT NIfTI file
    tumor_mask_path : str or Path
        Path to tumor mask NIfTI
    constraint_mask_path : str or Path
        Path to constraint (body) mask NIfTI
    output_path : str or Path
        Output path for PNG file
    dpi : int, optional
        Output DPI (default: 300)
    """
    logger.info(f"Generating QC overlays -> {output_path}")
    
    # Load all images
    pet_img = nib.load(str(pet_nifti_path))
    pet_data = pet_img.get_fdata()
    
    ct_img = nib.load(str(ct_nifti_path))
    ct_data = ct_img.get_fdata()
    
    tumor_img = nib.load(str(tumor_mask_path))
    tumor_mask = tumor_img.get_fdata() > 0.5
    
    constraint_img = nib.load(str(constraint_mask_path))
    constraint_mask = constraint_img.get_fdata() > 0.5
    
    # Compute tumor centroid
    if np.any(tumor_mask):
        coords = np.array(np.where(tumor_mask))
        centroid = np.mean(coords, axis=1).astype(int)
    else:
        # Use volume center if no tumor
        centroid = np.array(tumor_mask.shape) // 2
    
    # Extract slices at centroid
    axial_idx = centroid[2]
    coronal_idx = centroid[1]
    sagittal_idx = centroid[0]
    
    # Create figure with 3 rows (PET, CT, Combined) x 3 columns (Axial, Coronal, Sagittal)
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    
    # --- Row 1: PET with tumor contour ---
    # Axial
    _plot_overlay(
        axes[0, 0],
        pet_data[:, :, axial_idx],
        tumor_mask[:, :, axial_idx],
        constraint_mask[:, :, axial_idx],
        "PET - Axial",
        cmap='hot'
    )
    
    # Coronal
    _plot_overlay(
        axes[0, 1],
        pet_data[:, coronal_idx, :],
        tumor_mask[:, coronal_idx, :],
        constraint_mask[:, coronal_idx, :],
        "PET - Coronal",
        cmap='hot'
    )
    
    # Sagittal
    _plot_overlay(
        axes[0, 2],
        pet_data[sagittal_idx, :, :],
        tumor_mask[sagittal_idx, :, :],
        constraint_mask[sagittal_idx, :, :],
        "PET - Sagittal",
        cmap='hot'
    )
    
    # --- Row 2: CT with tumor contour ---
    # Axial
    _plot_overlay(
        axes[1, 0],
        ct_data[:, :, axial_idx],
        tumor_mask[:, :, axial_idx],
        constraint_mask[:, :, axial_idx],
        "CT - Axial",
        cmap='gray',
        vmin=-1000,
        vmax=500
    )
    
    # Coronal
    _plot_overlay(
        axes[1, 1],
        ct_data[:, coronal_idx, :],
        tumor_mask[:, coronal_idx, :],
        constraint_mask[:, coronal_idx, :],
        "CT - Coronal",
        cmap='gray',
        vmin=-1000,
        vmax=500
    )
    
    # Sagittal
    _plot_overlay(
        axes[1, 2],
        ct_data[sagittal_idx, :, :],
        tumor_mask[sagittal_idx, :, :],
        constraint_mask[sagittal_idx, :, :],
        "CT - Sagittal",
        cmap='gray',
        vmin=-1000,
        vmax=500
    )
    
    # --- Row 3: Combined (CT background with PET overlay) ---
    # Axial
    _plot_combined(
        axes[2, 0],
        ct_data[:, :, axial_idx],
        pet_data[:, :, axial_idx],
        tumor_mask[:, :, axial_idx],
        constraint_mask[:, :, axial_idx],
        "Combined - Axial"
    )
    
    # Coronal
    _plot_combined(
        axes[2, 1],
        ct_data[:, coronal_idx, :],
        pet_data[:, coronal_idx, :],
        tumor_mask[:, coronal_idx, :],
        constraint_mask[:, coronal_idx, :],
        "Combined - Coronal"
    )
    
    # Sagittal
    _plot_combined(
        axes[2, 2],
        ct_data[sagittal_idx, :, :],
        pet_data[sagittal_idx, :, :],
        tumor_mask[sagittal_idx, :, :],
        constraint_mask[sagittal_idx, :, :],
        "Combined - Sagittal"
    )
    
    plt.tight_layout()
    plt.savefig(str(output_path), dpi=dpi, bbox_inches='tight')
    plt.close()
    
    logger.info(f"QC overlays saved to {output_path}")


def _plot_overlay(ax, image, tumor_mask, constraint_mask, title, cmap='gray', vmin=None, vmax=None):
    """
    Plot single slice with tumor and constraint contours.
    
    Parameters
    ----------
    ax : matplotlib axis
        Axis to plot on
    image : ndarray
        2D image slice
    tumor_mask : ndarray
        2D tumor mask slice
    constraint_mask : ndarray
        2D constraint mask slice
    title : str
        Plot title
    cmap : str, optional
        Colormap for image
    vmin, vmax : float, optional
        Value range for image display
    """
    # Display base image
    if vmin is not None and vmax is not None:
        ax.imshow(image.T, cmap=cmap, origin='lower', vmin=vmin, vmax=vmax, aspect='auto')
    else:
        ax.imshow(image.T, cmap=cmap, origin='lower', aspect='auto')
    
    # Add tumor contour (red solid line)
    if np.any(tumor_mask):
        try:
            contours = measure.find_contours(tumor_mask.T, 0.5)
            for contour in contours:
                ax.plot(contour[:, 1], contour[:, 0], 'r-', linewidth=2, label='Tumor')
        except Exception as e:
            logger.warning(f"Failed to extract tumor contour: {e}")
    
    # Add constraint mask contour (cyan dashed line)
    if np.any(constraint_mask):
        try:
            contours = measure.find_contours(constraint_mask.T, 0.5)
            for contour in contours:
                ax.plot(contour[:, 1], contour[:, 0], 'c--', linewidth=1.5, label='Body Mask', alpha=0.7)
        except Exception as e:
            logger.warning(f"Failed to extract constraint contour: {e}")
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # Add legend (only show once per unique label)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8)


def _plot_combined(ax, ct_slice, pet_slice, tumor_mask, constraint_mask, title):
    """
    Plot combined CT/PET overlay with contours.
    
    Parameters
    ----------
    ax : matplotlib axis
        Axis to plot on
    ct_slice : ndarray
        2D CT slice
    pet_slice : ndarray
        2D PET slice
    tumor_mask : ndarray
        2D tumor mask slice
    constraint_mask : ndarray
        2D constraint mask slice
    title : str
        Plot title
    """
    # Display CT as base
    ax.imshow(ct_slice.T, cmap='gray', origin='lower', vmin=-1000, vmax=500, aspect='auto')
    
    # Overlay PET with transparency
    pet_masked = np.ma.masked_where(pet_slice.T < 1.0, pet_slice.T)  # Mask low SUV
    ax.imshow(pet_masked, cmap='hot', origin='lower', alpha=0.5, aspect='auto')
    
    # Add tumor contour (red solid line)
    if np.any(tumor_mask):
        try:
            contours = measure.find_contours(tumor_mask.T, 0.5)
            for contour in contours:
                ax.plot(contour[:, 1], contour[:, 0], 'r-', linewidth=2, label='Tumor')
        except Exception as e:
            logger.warning(f"Failed to extract tumor contour: {e}")
    
    # Add constraint mask contour (cyan dashed line)
    if np.any(constraint_mask):
        try:
            contours = measure.find_contours(constraint_mask.T, 0.5)
            for contour in contours:
                ax.plot(contour[:, 1], contour[:, 0], 'c--', linewidth=1.5, label='Body Mask', alpha=0.7)
        except Exception as e:
            logger.warning(f"Failed to extract constraint contour: {e}")
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8)


if __name__ == "__main__":
    # Example CLI usage
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) >= 6:
        pet_path = sys.argv[1]
        ct_path = sys.argv[2]
        tumor_path = sys.argv[3]
        constraint_path = sys.argv[4]
        output_path = sys.argv[5]
        
        generate_qc_overlays(pet_path, ct_path, tumor_path, constraint_path, output_path)
    else:
        print("Usage: python Mask_QC.py <pet_nifti> <ct_nifti> <tumor_mask> <constraint_mask> <output_png>")
