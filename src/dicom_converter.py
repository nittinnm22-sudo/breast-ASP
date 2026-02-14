"""
DICOM to NIfTI Conversion Module.

Converts DICOM directories to NIfTI format, preserving image orientation 
and voxel geometry for PET and CT imaging.
"""
import logging
from pathlib import Path
import pydicom
import numpy as np
import nibabel as nib
from typing import Union, Tuple

logger = logging.getLogger(__name__)


def convert_dicom_to_nifti(dicom_dir: Union[str, Path], 
                           output_path: Union[str, Path],
                           modality: str = "CT") -> Path:
    """
    Convert DICOM directory to NIfTI format.
    
    Preserves image orientation and voxel geometry using standard DICOM tags.
    
    Parameters
    ----------
    dicom_dir : str or Path
        Directory containing DICOM files
    output_path : str or Path
        Output path for NIfTI file (e.g., 'output.nii.gz')
    modality : str, optional
        Imaging modality ('CT' or 'PET'), default 'CT'
        
    Returns
    -------
    Path
        Path to created NIfTI file
        
    Raises
    ------
    ValueError
        If no DICOM files found or conversion fails
    """
    dicom_dir = Path(dicom_dir)
    output_path = Path(output_path)
    
    logger.info(f"Converting DICOM from {dicom_dir} to NIfTI...")
    logger.info(f"Modality: {modality}")
    
    # Get all DICOM files
    dicom_files = sorted(dicom_dir.glob("*.dcm"))
    if not dicom_files:
        # Try without extension
        dicom_files = sorted([f for f in dicom_dir.iterdir() if f.is_file()])
        # Filter by reading first few bytes
        dicom_files = [f for f in dicom_files if _is_dicom_file(f)]
    
    if not dicom_files:
        raise ValueError(f"No DICOM files found in {dicom_dir}")
    
    logger.info(f"Found {len(dicom_files)} DICOM files")
    
    # Try using dicom2nifti first (preferred method)
    try:
        import dicom2nifti
        import dicom2nifti.settings as settings
        
        # Enable resampling to preserve geometry
        settings.disable_validate_slice_increment()
        settings.enable_resampling()
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert using dicom2nifti
        dicom2nifti.convert_directory(str(dicom_dir), str(output_path.parent), 
                                      compression=True, reorient=True)
        
        # Find the created file (dicom2nifti may create with different name)
        created_files = list(output_path.parent.glob("*.nii.gz"))
        if not created_files:
            created_files = list(output_path.parent.glob("*.nii"))
        
        if created_files:
            # Rename to desired output path if different
            latest_file = max(created_files, key=lambda p: p.stat().st_mtime)
            if latest_file != output_path:
                latest_file.rename(output_path)
            logger.info(f"Successfully converted using dicom2nifti")
            return output_path
            
    except ImportError:
        logger.warning("dicom2nifti not available, using fallback method")
    except Exception as e:
        logger.warning(f"dicom2nifti conversion failed: {e}, using fallback method")
    
    # Fallback: Manual conversion
    return _manual_dicom_to_nifti(dicom_files, output_path, modality)


def _is_dicom_file(filepath: Path) -> bool:
    """Check if file is a DICOM file by reading header."""
    try:
        with open(filepath, 'rb') as f:
            f.seek(128)  # Skip preamble
            return f.read(4) == b'DICM'
    except:
        return False


def _manual_dicom_to_nifti(dicom_files: list, 
                           output_path: Path,
                           modality: str) -> Path:
    """
    Manual DICOM to NIfTI conversion as fallback.
    
    Reads DICOM files, constructs 3D volume, and creates NIfTI with proper affine.
    """
    logger.info("Using manual DICOM to NIfTI conversion...")
    
    # Read all DICOM files and sort by slice location
    slices = []
    for dcm_file in dicom_files:
        try:
            ds = pydicom.dcmread(str(dcm_file))
            slices.append(ds)
        except Exception as e:
            logger.warning(f"Failed to read {dcm_file}: {e}")
    
    if not slices:
        raise ValueError("No valid DICOM files could be read")
    
    # Sort slices by ImagePositionPatient (Z coordinate)
    try:
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    except:
        logger.warning("Could not sort by ImagePositionPatient, using instance number")
        slices.sort(key=lambda x: int(x.InstanceNumber) if hasattr(x, 'InstanceNumber') else 0)
    
    logger.info(f"Loaded {len(slices)} slices")
    
    # Get image dimensions
    ref_slice = slices[0]
    rows = int(ref_slice.Rows)
    cols = int(ref_slice.Columns)
    num_slices = len(slices)
    
    # Create 3D volume
    pixel_array = np.zeros((rows, cols, num_slices), dtype=np.float32)
    
    for i, slice_ds in enumerate(slices):
        pixel_data = slice_ds.pixel_array.astype(np.float32)
        
        # Apply rescale slope and intercept
        if hasattr(slice_ds, 'RescaleSlope') and hasattr(slice_ds, 'RescaleIntercept'):
            slope = float(slice_ds.RescaleSlope)
            intercept = float(slice_ds.RescaleIntercept)
            pixel_data = pixel_data * slope + intercept
        
        pixel_array[:, :, i] = pixel_data
    
    # Construct affine matrix
    affine = _construct_affine_matrix(slices[0], slices[-1] if len(slices) > 1 else slices[0], num_slices)
    
    # Create NIfTI image
    nifti_img = nib.Nifti1Image(pixel_array, affine)
    
    # Set proper header information
    nifti_img.header.set_xyzt_units(2, 8)  # mm and seconds
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(nifti_img, str(output_path))
    
    logger.info(f"Successfully created NIfTI file: {output_path}")
    logger.info(f"Image shape: {pixel_array.shape}")
    logger.info(f"Voxel spacing: {nifti_img.header.get_zooms()}")
    
    return output_path


def _construct_affine_matrix(first_slice, last_slice, num_slices: int) -> np.ndarray:
    """
    Construct affine transformation matrix from DICOM metadata.
    
    Uses ImageOrientationPatient and ImagePositionPatient to properly
    orient the image in RAS (Right-Anterior-Superior) coordinate system.
    """
    # Get pixel spacing (in-plane)
    pixel_spacing = first_slice.PixelSpacing  # [row_spacing, col_spacing]
    
    # Get image orientation (direction cosines)
    orientation = first_slice.ImageOrientationPatient
    row_cosine = np.array(orientation[:3])  # X direction
    col_cosine = np.array(orientation[3:])  # Y direction
    
    # Calculate slice direction (cross product)
    slice_cosine = np.cross(row_cosine, col_cosine)
    
    # Calculate slice spacing
    if num_slices > 1:
        pos_first = np.array(first_slice.ImagePositionPatient)
        pos_last = np.array(last_slice.ImagePositionPatient)
        slice_spacing = np.linalg.norm(pos_last - pos_first) / (num_slices - 1)
    else:
        # Single slice
        if hasattr(first_slice, 'SliceThickness'):
            slice_spacing = float(first_slice.SliceThickness)
        else:
            slice_spacing = 1.0
    
    # Construct affine matrix
    affine = np.eye(4)
    
    # Set rotation/scaling
    affine[0, 0] = row_cosine[0] * pixel_spacing[1]  # column spacing
    affine[1, 0] = row_cosine[1] * pixel_spacing[1]
    affine[2, 0] = row_cosine[2] * pixel_spacing[1]
    
    affine[0, 1] = col_cosine[0] * pixel_spacing[0]  # row spacing
    affine[1, 1] = col_cosine[1] * pixel_spacing[0]
    affine[2, 1] = col_cosine[2] * pixel_spacing[0]
    
    affine[0, 2] = slice_cosine[0] * slice_spacing
    affine[1, 2] = slice_cosine[1] * slice_spacing
    affine[2, 2] = slice_cosine[2] * slice_spacing
    
    # Set origin (position of first voxel)
    position = first_slice.ImagePositionPatient
    affine[0, 3] = position[0]
    affine[1, 3] = position[1]
    affine[2, 3] = position[2]
    
    return affine


def check_gpu_availability() -> dict:
    """
    Check GPU availability and return configuration info.
    
    Returns
    -------
    dict
        Dictionary with GPU information including:
        - available: bool
        - device_name: str
        - memory_total: float (GB)
        - memory_free: float (GB)
        - cuda_version: str
    """
    gpu_info = {
        'available': False,
        'device_name': 'N/A',
        'memory_total': 0,
        'memory_free': 0,
        'cuda_version': 'N/A'
    }
    
    try:
        import torch
        
        if torch.cuda.is_available():
            gpu_info['available'] = True
            gpu_info['device_name'] = torch.cuda.get_device_name(0)
            gpu_info['memory_total'] = torch.cuda.get_device_properties(0).total_memory / 1e9
            gpu_info['memory_free'] = (torch.cuda.get_device_properties(0).total_memory - 
                                       torch.cuda.memory_allocated(0)) / 1e9
            gpu_info['cuda_version'] = torch.version.cuda
            
            logger.info(f"GPU detected: {gpu_info['device_name']}")
            logger.info(f"CUDA version: {gpu_info['cuda_version']}")
            logger.info(f"Total VRAM: {gpu_info['memory_total']:.2f} GB")
            logger.info(f"Free VRAM: {gpu_info['memory_free']:.2f} GB")
        else:
            logger.warning("CUDA not available, will use CPU")
            
    except ImportError:
        logger.warning("PyTorch not installed, GPU support unavailable")
    except Exception as e:
        logger.warning(f"Error checking GPU: {e}")
    
    return gpu_info
