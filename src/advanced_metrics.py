"""
Complete radiomics feature extraction for lung tumor segmentation.
Computes SUV metrics, MTV, TLG, shape metrics, and advanced uptake patterns.
"""
import numpy as np
import nibabel as nib
from scipy import ndimage
from scipy.spatial.distance import cdist
import logging

logger = logging.getLogger(__name__)


def compute_all_metrics(pet_nifti_path, tumor_mask_nifti_path):
    """
    Compute comprehensive radiomics metrics for tumor VOI.
    
    Parameters
    ----------
    pet_nifti_path : str or Path
        Path to PET NIfTI file (in SUV units)
    tumor_mask_nifti_path : str or Path
        Path to binary tumor mask NIfTI
        
    Returns
    -------
    dict
        Dictionary containing all computed metrics with standardized keys
    """
    # Load PET and mask
    pet_img = nib.load(str(pet_nifti_path))
    pet_data = pet_img.get_fdata()
    pet_affine = pet_img.affine
    
    mask_img = nib.load(str(tumor_mask_nifti_path))
    tumor_mask = mask_img.get_fdata().astype(bool)
    
    if not np.any(tumor_mask):
        logger.warning("Empty tumor mask - returning zero metrics")
        return _zero_metrics()
    
    # Extract voxel spacing
    voxel_spacing = np.abs(np.diag(pet_affine)[:3])  # mm
    voxel_volume_ml = np.prod(voxel_spacing) / 1000.0  # Convert mm³ to mL
    
    # Extract tumor SUV values
    tumor_suvs = pet_data[tumor_mask]
    
    # --- Basic SUV Statistics ---
    suv_max = float(np.max(tumor_suvs))
    suv_mean = float(np.mean(tumor_suvs))
    
    # --- SUVpeak: Mean SUV in 1 cm³ sphere centered on SUVmax (PERCIST) ---
    suv_peak = compute_suv_peak(pet_data, tumor_mask, pet_affine)
    
    # --- MTV: Metabolic Tumor Volume at 41% of SUVmax ---
    mtv_threshold = 0.41 * suv_max
    mtv_mask = (pet_data >= mtv_threshold) & tumor_mask
    mtv_voxel_count = np.sum(mtv_mask)
    mtv_ml = float(mtv_voxel_count * voxel_volume_ml)
    
    # --- TLG: Total Lesion Glycolysis ---
    tlg_g = float(suv_mean * mtv_ml)
    
    # --- Tumor Volume (mm³) ---
    tumor_volume_mm3 = float(np.sum(tumor_mask) * np.prod(voxel_spacing))
    
    # --- Intra-lesion Dmax: Maximum 3D diameter ---
    dmax_mm = compute_dmax(tumor_mask, pet_affine)
    
    # --- NHOCmax: Normalized Hotspot-to-Centroid distance ---
    nhoc_max = compute_nhoc_max(pet_data, tumor_mask, pet_affine)
    
    # --- NHOPmax: Normalized Hotspot-to-Perimeter distance ---
    nhop_max = compute_nhop_max(pet_data, tumor_mask, pet_affine)
    
    # --- gETU: Generalized Effective Tumor Uptake ---
    getu_metrics = compute_getu(tumor_suvs, voxel_volume_ml)
    
    # --- Sphericity and Asphericity ---
    sphericity, asphericity = compute_sphericity_asphericity(tumor_mask, pet_affine)
    
    # Compile all metrics
    metrics = {
        'SUVmax': suv_max,
        'SUVmean': suv_mean,
        'SUVpeak': suv_peak,
        'MTV_ml': mtv_ml,
        'TLG_g': tlg_g,
        'tumor_volume_mm3': tumor_volume_mm3,
        'Dmax_mm': dmax_mm,
        'NHOCmax': nhoc_max,
        'NHOPmax': nhop_max,
        'sphericity': sphericity,
        'asphericity': asphericity,
    }
    
    # Add gETU metrics
    metrics.update(getu_metrics)
    
    return metrics


def compute_suv_peak(pet_data, tumor_mask, affine):
    """
    Compute SUVpeak: mean SUV in a 1 cm³ sphere centered on SUVmax location.
    Uses PERCIST definition.
    
    Parameters
    ----------
    pet_data : ndarray
        3D PET SUV data
    tumor_mask : ndarray
        Binary tumor mask
    affine : ndarray
        Affine transformation matrix
        
    Returns
    -------
    float
        SUVpeak value
    """
    # Find SUVmax location in tumor
    tumor_suvs = pet_data.copy()
    tumor_suvs[~tumor_mask] = 0
    max_idx = np.unravel_index(np.argmax(tumor_suvs), tumor_suvs.shape)
    
    # Get voxel spacing
    voxel_spacing = np.abs(np.diag(affine)[:3])  # mm
    
    # Calculate sphere radius in voxels for 1 cm³ = 1000 mm³
    # Volume = (4/3) * π * r³
    # r = (3V / 4π)^(1/3)
    sphere_radius_mm = (3 * 1000 / (4 * np.pi)) ** (1/3)  # ~6.2 mm
    sphere_radius_voxels = sphere_radius_mm / voxel_spacing
    
    # Create spherical ROI
    i, j, k = np.ogrid[:pet_data.shape[0], :pet_data.shape[1], :pet_data.shape[2]]
    distances_voxels = np.sqrt(
        ((i - max_idx[0]) / sphere_radius_voxels[0]) ** 2 +
        ((j - max_idx[1]) / sphere_radius_voxels[1]) ** 2 +
        ((k - max_idx[2]) / sphere_radius_voxels[2]) ** 2
    )
    
    sphere_mask = distances_voxels <= 1.0
    sphere_values = pet_data[sphere_mask & tumor_mask]
    
    if len(sphere_values) > 0:
        return float(np.mean(sphere_values))
    else:
        # Fallback to SUVmax if sphere is empty
        return float(np.max(pet_data[tumor_mask]))


def compute_dmax(tumor_mask, affine, random_seed=42):
    """
    Compute maximum 3D Euclidean diameter between any two surface voxels.
    
    Parameters
    ----------
    tumor_mask : ndarray
        Binary tumor mask
    affine : ndarray
        Affine transformation matrix
    random_seed : int, optional
        Random seed for reproducible sampling (default: 42)
        
    Returns
    -------
    float
        Maximum diameter in mm
    """
    # Extract surface voxels (boundary)
    eroded = ndimage.binary_erosion(tumor_mask)
    boundary = tumor_mask & ~eroded
    
    # Get boundary voxel coordinates
    boundary_coords_voxel = np.array(np.where(boundary)).T
    
    if len(boundary_coords_voxel) < 2:
        return 0.0
    
    # Convert to physical coordinates (mm)
    boundary_coords_mm = nib.affines.apply_affine(affine, boundary_coords_voxel)
    
    # Compute pairwise distances (optimized for large sets)
    if len(boundary_coords_mm) > 1000:
        # Sample subset for efficiency with fixed seed for reproducibility
        rng = np.random.RandomState(random_seed)
        idx = rng.choice(len(boundary_coords_mm), 1000, replace=False)
        boundary_coords_mm = boundary_coords_mm[idx]
    
    distances = cdist(boundary_coords_mm, boundary_coords_mm, metric='euclidean')
    dmax = float(np.max(distances))
    
    return dmax


def compute_nhoc_max(pet_data, tumor_mask, affine):
    """
    Compute NHOCmax: Normalized Hotspot-to-Centroid distance.
    NHOCmax = d(x_SUVmax, x_centroid) / R
    where R = equivalent-volume sphere radius = (3V / 4π)^(1/3)
    
    Parameters
    ----------
    pet_data : ndarray
        3D PET SUV data
    tumor_mask : ndarray
        Binary tumor mask
    affine : ndarray
        Affine transformation matrix
        
    Returns
    -------
    float
        NHOCmax value (dimensionless)
    """
    # Find SUVmax location
    tumor_suvs = pet_data.copy()
    tumor_suvs[~tumor_mask] = 0
    max_idx = np.unravel_index(np.argmax(tumor_suvs), tumor_suvs.shape)
    
    # Compute tumor centroid
    coords = np.array(np.where(tumor_mask)).T
    centroid_voxel = np.mean(coords, axis=0)
    
    # Convert to physical space (mm)
    max_pos_mm = nib.affines.apply_affine(affine, [max_idx])[0]
    centroid_mm = nib.affines.apply_affine(affine, [centroid_voxel])[0]
    
    # Distance from hotspot to centroid
    distance_mm = np.linalg.norm(max_pos_mm - centroid_mm)
    
    # Compute equivalent sphere radius
    voxel_spacing = np.abs(np.diag(affine)[:3])
    volume_mm3 = np.sum(tumor_mask) * np.prod(voxel_spacing)
    equiv_radius_mm = (3 * volume_mm3 / (4 * np.pi)) ** (1/3)
    
    if equiv_radius_mm > 0:
        nhoc_max = float(distance_mm / equiv_radius_mm)
    else:
        nhoc_max = 0.0
    
    return nhoc_max


def compute_nhop_max(pet_data, tumor_mask, affine):
    """
    Compute NHOPmax: Normalized Hotspot-to-Perimeter distance.
    NHOPmax = d_min(x_SUVmax, ∂VOI) / R
    where d_min is minimum distance from SUVmax voxel to tumor boundary.
    
    Parameters
    ----------
    pet_data : ndarray
        3D PET SUV data
    tumor_mask : ndarray
        Binary tumor mask
    affine : ndarray
        Affine transformation matrix
        
    Returns
    -------
    float
        NHOPmax value (dimensionless)
    """
    # Find SUVmax location
    tumor_suvs = pet_data.copy()
    tumor_suvs[~tumor_mask] = 0
    max_idx = np.unravel_index(np.argmax(tumor_suvs), tumor_suvs.shape)
    
    # Compute distance transform from boundary
    # distance_transform_edt gives distance from each voxel to nearest background
    voxel_spacing = np.abs(np.diag(affine)[:3])
    distance_map = ndimage.distance_transform_edt(tumor_mask, sampling=voxel_spacing)
    
    # Distance from SUVmax to boundary
    min_distance_mm = distance_map[max_idx]
    
    # Compute equivalent sphere radius
    volume_mm3 = np.sum(tumor_mask) * np.prod(voxel_spacing)
    equiv_radius_mm = (3 * volume_mm3 / (4 * np.pi)) ** (1/3)
    
    if equiv_radius_mm > 0:
        nhop_max = float(min_distance_mm / equiv_radius_mm)
    else:
        nhop_max = 0.0
    
    return nhop_max


def compute_getu(tumor_suvs, voxel_volume_ml):
    """
    Compute gETU (Generalized Effective Tumor Uptake) for multiple alpha values.
    
    gETU(a) = (Δv × Σ u_i^a)^(1/a)
    
    where Δv = voxel volume in mL, u_i = SUV of voxel i.
    For numerical stability with small a: gETU = exp((1/a) × ln(S))
    
    Parameters
    ----------
    tumor_suvs : ndarray
        Array of SUV values in tumor
    voxel_volume_ml : float
        Volume of a single voxel in mL
        
    Returns
    -------
    dict
        Dictionary with gETU values for each alpha
    """
    alpha_values = [0.25, 0.5, 1.0, 2.0, 4.0]
    getu_metrics = {}
    
    for alpha in alpha_values:
        if alpha == 1.0:
            # For alpha=1, gETU = Δv × Σ u_i = TLG
            getu = voxel_volume_ml * np.sum(tumor_suvs)
        else:
            # Use log-space for numerical stability
            # gETU = exp((1/a) × ln(Δv × Σ u_i^a))
            #      = exp((1/a) × (ln(Δv) + ln(Σ u_i^a)))
            powered_suvs = np.power(tumor_suvs, alpha)
            sum_powered = np.sum(powered_suvs)
            
            if sum_powered > 0:
                log_sum = np.log(voxel_volume_ml * sum_powered)
                getu = np.exp(log_sum / alpha)
            else:
                getu = 0.0
        
        # Format key as gETU_a025, gETU_a050, etc.
        # Scale alpha to integer (e.g., 0.25 -> 25) and format with 3 digits
        alpha_scaled = int(alpha * 100)
        key = f'gETU_a{alpha_scaled:03d}'
        getu_metrics[key] = float(getu)
    
    return getu_metrics


def compute_sphericity_asphericity(tumor_mask, affine):
    """
    Compute sphericity and asphericity using the correct clinical formula.
    
    Ψ = π^(1/3) × (6V)^(2/3) / A
    ASP = 1 − Ψ
    
    where V = tumor volume (mm³), A = tumor surface area (mm²).
    
    Parameters
    ----------
    tumor_mask : ndarray
        Binary tumor mask
    affine : ndarray
        Affine transformation matrix
        
    Returns
    -------
    tuple
        (sphericity, asphericity)
    """
    try:
        from skimage import measure
        import trimesh
        
        # Resample to isotropic 1mm grid for accurate mesh extraction
        voxel_spacing = np.abs(np.diag(affine)[:3])
        target_spacing = np.array([1.0, 1.0, 1.0])
        zoom_factors = voxel_spacing / target_spacing
        
        from scipy.ndimage import zoom
        tumor_mask_iso = zoom(tumor_mask.astype(float), zoom_factors, order=0) > 0.5
        
        # Compute volume (mm³)
        volume_mm3 = float(np.sum(tumor_mask_iso) * np.prod(target_spacing))
        
        # Extract surface mesh using marching cubes
        try:
            verts, faces, normals, values = measure.marching_cubes(
                tumor_mask_iso.astype(float),
                level=0.5,
                spacing=target_spacing
            )
            
            # Create trimesh object
            mesh = trimesh.Trimesh(vertices=verts, faces=faces)
            
            # Compute surface area (mm²)
            surface_area_mm2 = float(mesh.area)
            
            # Compute sphericity: Ψ = π^(1/3) × (6V)^(2/3) / A
            if surface_area_mm2 > 0 and volume_mm3 > 0:
                sphericity = (np.pi ** (1/3)) * ((6 * volume_mm3) ** (2/3)) / surface_area_mm2
                sphericity = float(np.clip(sphericity, 0, 1))  # Clamp to [0, 1]
            else:
                sphericity = 0.0
            
            # Asphericity: ASP = 1 - Ψ
            asphericity = float(1.0 - sphericity)
            
        except Exception as e:
            logger.warning(f"Marching cubes failed: {e}")
            sphericity = 0.0
            asphericity = 1.0
        
    except ImportError as e:
        logger.warning(f"Missing dependencies for sphericity computation: {e}")
        sphericity = 0.0
        asphericity = 1.0
    
    return sphericity, asphericity


def _zero_metrics():
    """Return dictionary of zero metrics for empty masks."""
    return {
        'SUVmax': 0.0,
        'SUVmean': 0.0,
        'SUVpeak': 0.0,
        'MTV_ml': 0.0,
        'TLG_g': 0.0,
        'tumor_volume_mm3': 0.0,
        'Dmax_mm': 0.0,
        'NHOCmax': 0.0,
        'NHOPmax': 0.0,
        'gETU_a025': 0.0,
        'gETU_a050': 0.0,
        'gETU_a100': 0.0,
        'gETU_a200': 0.0,
        'gETU_a400': 0.0,
        'sphericity': 0.0,
        'asphericity': 1.0,
    }
