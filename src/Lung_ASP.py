"""
FDG PET/CT Lung Tumor Segmentation Pipeline with Mediastinal Exclusion.

Implements random walker segmentation with:
- CT-based thoracic body mask constraint
- Comprehensive anatomical exclusion (TotalSegmentator)
- Correct clinical seed thresholds (5% FG, 2% BG)
- Beta = 5, tolerance = 1e-2
- Correct sphericity formula
"""
import numpy as np
import nibabel as nib
from pathlib import Path
import logging
import json
from scipy import ndimage
from skimage.segmentation import random_walker
import SimpleITK as sitk

from totalseg_safe import run_totalsegmentator
from advanced_metrics import compute_all_metrics

logger = logging.getLogger(__name__)


def create_thoracic_body_mask(ct_nifti_path, output_path=None, closing_radius=20):
    """
    Create CT-based thoracic body mask using HU thresholding.
    
    Threshold: -500 to +1000 HU
    Morphological closing: configurable radius (default 20 voxels)
    
    Parameters
    ----------
    ct_nifti_path : Path
        Path to CT NIfTI file
    output_path : Path, optional
        Path to save body mask
    closing_radius : int, optional
        Radius for morphological closing (default: 20 voxels)
        
    Returns
    -------
    ndarray
        Binary body mask
    """
    logger.info("Creating thoracic body mask...")
    
    # Load CT
    ct_img = nib.load(str(ct_nifti_path))
    ct_data = ct_img.get_fdata()
    
    # Apply HU threshold: -500 to +1000
    body_mask = (ct_data >= -500) & (ct_data <= 1000)
    
    # Morphological closing with configurable radius
    # Use scikit-image ball structure for efficiency
    try:
        from skimage.morphology import ball
        structure = ball(closing_radius)
    except ImportError:
        # Fallback to iterative dilation if skimage not available
        structure = ndimage.generate_binary_structure(3, 1)
        structure = ndimage.iterate_structure(structure, closing_radius)
    
    body_mask = ndimage.binary_closing(body_mask, structure=structure)
    
    # Keep largest connected component
    labeled, num_features = ndimage.label(body_mask)
    if num_features > 0:
        sizes = ndimage.sum(body_mask, labeled, range(1, num_features + 1))
        largest_label = np.argmax(sizes) + 1
        body_mask = labeled == largest_label
    
    # Save if requested
    if output_path:
        body_mask_img = nib.Nifti1Image(body_mask.astype(np.uint8), ct_img.affine, ct_img.header)
        nib.save(body_mask_img, str(output_path))
        logger.info(f"Saved body mask to {output_path}")
    
    logger.info(f"Body mask created: {np.sum(body_mask)} voxels")
    return body_mask


def create_exclusion_mask(tseg_dir, reference_nifti_path):
    """
    Create comprehensive anatomical exclusion mask from TotalSegmentator output.
    
    Excludes:
    - Mediastinum: heart, aorta, esophagus, trachea, pulmonary veins, subclavian vessels
    - Vessels: superior/inferior vena cava, brachiocephalic vessels
    - Spine: C7, T1-T12, L1
    - Ribs: left/right 1-12
    - Sternum
    - Scapulae: left/right
    - Abdominal organs: liver, spleen, stomach, kidneys
    - Thyroid
    
    Parameters
    ----------
    tseg_dir : Path
        Directory containing TotalSegmentator segmentation files
    reference_nifti_path : Path
        Reference NIfTI for affine/shape
        
    Returns
    -------
    ndarray
        Binary exclusion mask
    """
    logger.info("Creating comprehensive anatomical exclusion mask...")
    
    # Load reference
    ref_img = nib.load(str(reference_nifti_path))
    ref_shape = ref_img.shape
    exclusion_mask = np.zeros(ref_shape, dtype=bool)
    
    # Define all structures to exclude
    structures_to_exclude = [
        # Mediastinum
        'heart',
        'aorta',
        'esophagus',
        'trachea',
        'pulmonary_vein',
        # Vessels
        'superior_vena_cava',
        'inferior_vena_cava',
        'brachiocephalic_trunk',
        'brachiocephalic_vein_left',
        'brachiocephalic_vein_right',
        'subclavian_artery_left',
        'subclavian_artery_right',
        'subclavian_vein_left',
        'subclavian_vein_right',
        # Spine
        'vertebrae_C7',
        'vertebrae_T1', 'vertebrae_T2', 'vertebrae_T3', 'vertebrae_T4',
        'vertebrae_T5', 'vertebrae_T6', 'vertebrae_T7', 'vertebrae_T8',
        'vertebrae_T9', 'vertebrae_T10', 'vertebrae_T11', 'vertebrae_T12',
        'vertebrae_L1',
        # Ribs
        'rib_left_1', 'rib_left_2', 'rib_left_3', 'rib_left_4', 'rib_left_5', 'rib_left_6',
        'rib_left_7', 'rib_left_8', 'rib_left_9', 'rib_left_10', 'rib_left_11', 'rib_left_12',
        'rib_right_1', 'rib_right_2', 'rib_right_3', 'rib_right_4', 'rib_right_5', 'rib_right_6',
        'rib_right_7', 'rib_right_8', 'rib_right_9', 'rib_right_10', 'rib_right_11', 'rib_right_12',
        # Sternum
        'sternum',
        # Scapulae
        'scapula_left',
        'scapula_right',
        # Abdominal organs
        'liver',
        'spleen',
        'stomach',
        'kidney_left',
        'kidney_right',
        # Thyroid
        'thyroid_gland',
    ]
    
    # Load and combine all exclusion structures
    structures_found = 0
    for structure in structures_to_exclude:
        structure_path = Path(tseg_dir) / f"{structure}.nii.gz"
        if not structure_path.exists():
            # Try alternate naming
            structure_path = Path(tseg_dir) / f"{structure}.nii"
        
        if structure_path.exists():
            try:
                struct_img = nib.load(str(structure_path))
                struct_mask = struct_img.get_fdata() > 0.5
                exclusion_mask = exclusion_mask | struct_mask
                structures_found += 1
            except Exception as e:
                logger.warning(f"Failed to load {structure}: {e}")
        else:
            logger.debug(f"Structure not found: {structure}")
    
    logger.info(f"Loaded {structures_found}/{len(structures_to_exclude)} exclusion structures")
    logger.info(f"Exclusion mask: {np.sum(exclusion_mask)} voxels")
    
    return exclusion_mask


def resample_pet_to_ct(pet_img, ct_img):
    """
    Resample PET to CT space using SimpleITK.
    
    Parameters
    ----------
    pet_img : nibabel image
        PET NIfTI image
    ct_img : nibabel image
        CT NIfTI image (reference)
        
    Returns
    -------
    ndarray
        Resampled PET data in CT space
    """
    logger.info("Resampling PET to CT space...")
    
    # Convert to SimpleITK
    pet_sitk = sitk.GetImageFromArray(np.transpose(pet_img.get_fdata(), (2, 1, 0)))
    pet_sitk.SetOrigin(pet_img.affine[:3, 3].tolist())
    pet_sitk.SetSpacing(np.abs(np.diag(pet_img.affine)[:3]).tolist())
    
    ct_sitk = sitk.GetImageFromArray(np.transpose(ct_img.get_fdata(), (2, 1, 0)))
    ct_sitk.SetOrigin(ct_img.affine[:3, 3].tolist())
    ct_sitk.SetSpacing(np.abs(np.diag(ct_img.affine)[:3]).tolist())
    
    # Resample PET to CT grid
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(ct_sitk)
    resampler.SetInterpolator(sitk.sitkLinear)
    pet_resampled_sitk = resampler.Execute(pet_sitk)
    
    # Convert back to numpy
    pet_resampled = np.transpose(sitk.GetArrayFromImage(pet_resampled_sitk), (2, 1, 0))
    
    logger.info(f"Resampled PET shape: {pet_resampled.shape}")
    return pet_resampled


def segment_tumor_random_walker(
    pet_data,
    constraint_mask,
    exclusion_mask,
    beta=5,
    tol=1e-2
):
    """
    Segment tumor using random walker with correct clinical thresholds.
    
    Seed thresholds:
    - Foreground: 5% of SUVmax (candidate pool)
    - Background: 2% of SUVmax (candidate pool)
    - Beta: 5
    - Tolerance: 1e-2
    
    Parameters
    ----------
    pet_data : ndarray
        PET SUV data
    constraint_mask : ndarray
        Binary thoracic body mask (constraint region)
    exclusion_mask : ndarray
        Binary anatomical exclusion mask
    beta : float, optional
        Random walker beta parameter (edge weight)
    tol : float, optional
        Solver tolerance
        
    Returns
    -------
    ndarray
        Binary tumor segmentation mask
    """
    logger.info("Running random walker segmentation...")
    
    # Compute SUVmax in constraint region (excluding anatomical structures)
    valid_region = constraint_mask & ~exclusion_mask
    suv_max = np.max(pet_data[valid_region])
    
    logger.info(f"SUVmax in valid region: {suv_max:.2f}")
    
    # Define seed thresholds (CORRECT VALUES)
    fg_threshold = 0.05 * suv_max  # 5% of SUVmax
    bg_threshold = 0.02 * suv_max  # 2% of SUVmax
    
    logger.info(f"Foreground threshold (5% SUVmax): {fg_threshold:.2f}")
    logger.info(f"Background threshold (2% SUVmax): {bg_threshold:.2f}")
    
    # Create marker array
    markers = np.zeros_like(pet_data, dtype=np.int32)
    
    # Foreground seeds: high uptake in valid region
    fg_candidates = (pet_data >= fg_threshold) & valid_region
    markers[fg_candidates] = 1
    
    # Background seeds: low uptake OR excluded anatomy
    bg_candidates = ((pet_data <= bg_threshold) & constraint_mask) | exclusion_mask
    markers[bg_candidates] = 2
    
    logger.info(f"Foreground seeds: {np.sum(markers == 1)} voxels")
    logger.info(f"Background seeds: {np.sum(markers == 2)} voxels")
    
    if np.sum(markers == 1) == 0:
        logger.warning("No foreground seeds found - returning empty mask")
        return np.zeros_like(pet_data, dtype=bool)
    
    if np.sum(markers == 2) == 0:
        logger.warning("No background seeds found - using exclusion mask only")
        markers[exclusion_mask] = 2
    
    # Run random walker
    try:
        labels = random_walker(
            pet_data,
            markers,
            beta=beta,
            tol=tol,
            mode='cg_mg'
        )
        
        # Extract foreground (label 1)
        tumor_mask = (labels == 1)
        
        # Apply constraint mask
        tumor_mask = tumor_mask & constraint_mask
        
        # Remove exclusion regions
        tumor_mask = tumor_mask & ~exclusion_mask
        
        logger.info(f"Segmented tumor: {np.sum(tumor_mask)} voxels")
        
    except Exception as e:
        logger.error(f"Random walker failed: {e}")
        raise
    
    return tumor_mask


def process_case(
    pet_nifti_path,
    ct_nifti_path,
    out_dir,
    case_id="case"
):
    """
    Process a single PET/CT case for lung tumor segmentation.
    
    Pipeline:
    1. Create CT-based thoracic body mask
    2. Run TotalSegmentator on CT
    3. Create comprehensive exclusion mask
    4. Resample PET to CT space
    5. Segment tumor with random walker
    6. Compute comprehensive radiomics
    7. Save outputs
    
    Parameters
    ----------
    pet_nifti_path : str or Path
        Path to PET NIfTI file (SUV corrected)
    ct_nifti_path : str or Path
        Path to CT NIfTI file
    out_dir : str or Path
        Output directory
    case_id : str, optional
        Case identifier
        
    Returns
    -------
    dict
        Dictionary containing all computed metrics
    """
    pet_nifti_path = Path(pet_nifti_path)
    ct_nifti_path = Path(ct_nifti_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing case: {case_id}")
    logger.info(f"PET: {pet_nifti_path}")
    logger.info(f"CT: {ct_nifti_path}")
    
    # --- Step 1: Create thoracic body mask ---
    body_mask_path = out_dir / f"{case_id}_body_mask.nii.gz"
    ct_img = nib.load(str(ct_nifti_path))
    body_mask = create_thoracic_body_mask(ct_nifti_path, body_mask_path)
    
    # --- Step 2: Run TotalSegmentator ---
    tseg_dir = out_dir / f"{case_id}_totalseg"
    # FIXED: Use out_dir instead of undefined out_root
    # FIXED: Wrap return value in Path()
    tseg_dir_total = Path(run_totalsegmentator(
        ct_nifti_path,
        tseg_dir,
        fast=False,
        quiet=False
    ))
    
    # --- Step 3: Create exclusion mask ---
    exclusion_mask = create_exclusion_mask(tseg_dir_total, ct_nifti_path)
    exclusion_mask_path = out_dir / f"{case_id}_exclusion_mask.nii.gz"
    exclusion_img = nib.Nifti1Image(exclusion_mask.astype(np.uint8), ct_img.affine, ct_img.header)
    nib.save(exclusion_img, str(exclusion_mask_path))
    
    # --- Step 4: Resample PET to CT space ---
    pet_img = nib.load(str(pet_nifti_path))
    pet_resampled = resample_pet_to_ct(pet_img, ct_img)
    
    # Save resampled PET
    pet_resampled_path = out_dir / f"{case_id}_pet_resampled.nii.gz"
    pet_resampled_img = nib.Nifti1Image(pet_resampled, ct_img.affine, ct_img.header)
    nib.save(pet_resampled_img, str(pet_resampled_path))
    
    # --- Step 5: Segment tumor ---
    # FIXED: Use correct thresholds (5% FG, 2% BG) and beta=5
    tumor_mask = segment_tumor_random_walker(
        pet_resampled,
        body_mask,
        exclusion_mask,
        beta=5,  # FIXED: Was 10, should be 5
        tol=1e-2
    )
    
    # Save tumor mask
    tumor_mask_path = out_dir / f"{case_id}_tumor_mask.nii.gz"
    tumor_mask_img = nib.Nifti1Image(tumor_mask.astype(np.uint8), ct_img.affine, ct_img.header)
    nib.save(tumor_mask_img, str(tumor_mask_path))
    
    # --- Step 6: Compute comprehensive radiomics ---
    # FIXED: Sphericity formula is corrected in advanced_metrics.py
    metrics = compute_all_metrics(pet_resampled_path, tumor_mask_path)
    
    # Add case metadata
    metrics['case_id'] = case_id
    metrics['pet_path'] = str(pet_nifti_path)
    metrics['ct_path'] = str(ct_nifti_path)
    
    # --- Step 7: Save metrics ---
    # Save as JSON
    metrics_json_path = out_dir / f"{case_id}_metrics.json"
    with open(metrics_json_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Saved metrics to {metrics_json_path}")
    
    # Save as CSV
    import csv
    metrics_csv_path = out_dir / f"{case_id}_metrics.csv"
    with open(metrics_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        for key, value in metrics.items():
            writer.writerow([key, value])
    logger.info(f"Saved metrics to {metrics_csv_path}")
    
    logger.info(f"Case {case_id} processing complete")
    
    return metrics


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    import sys
    if len(sys.argv) >= 4:
        pet_path = sys.argv[1]
        ct_path = sys.argv[2]
        output_dir = sys.argv[3]
        case_id = sys.argv[4] if len(sys.argv) > 4 else "case"
        
        metrics = process_case(pet_path, ct_path, output_dir, case_id)
        print(f"\nComputed metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
    else:
        print("Usage: python Lung_ASP.py <pet_nifti> <ct_nifti> <output_dir> [case_id]")
