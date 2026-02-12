"""
DICOM to NIfTI Conversion Module

This module handles conversion of DICOM PET/CT images to NIfTI format
with preservation of image orientation and voxel geometry.
"""

import os
import numpy as np
import nibabel as nib
import dicom2nifti
import pydicom
from pathlib import Path


class DICOMConverter:
    """
    Converts DICOM PET/CT images to NIfTI format with geometry preservation.
    """
    
    def __init__(self, output_dir=None):
        """
        Initialize the DICOM converter.
        
        Args:
            output_dir (str): Directory to save converted NIfTI files
        """
        self.output_dir = output_dir or os.getcwd()
        os.makedirs(self.output_dir, exist_ok=True)
        
    def convert_dicom_to_nifti(self, dicom_dir, output_filename="PET_converted.nii.gz",
                               modality="PT"):
        """
        Convert DICOM series to NIfTI format.
        
        Args:
            dicom_dir (str): Directory containing DICOM files
            output_filename (str): Output NIfTI filename
            modality (str): Modality to convert ("PT" for PET, "CT" for CT)
            
        Returns:
            str: Path to converted NIfTI file
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # Use dicom2nifti for conversion with geometry preservation
            dicom2nifti.convert_directory(
                dicom_dir, 
                self.output_dir,
                compression=True,
                reorient=False  # Preserve original orientation
            )
            
            # Rename to desired filename if needed
            nifti_files = list(Path(self.output_dir).glob("*.nii.gz"))
            if nifti_files and not os.path.exists(output_path):
                os.rename(str(nifti_files[0]), output_path)
                
        except Exception as e:
            print(f"Warning: dicom2nifti failed, using fallback method: {e}")
            self._convert_dicom_fallback(dicom_dir, output_path, modality)
        
        return output_path
    
    def _convert_dicom_fallback(self, dicom_dir, output_path, modality="PT"):
        """
        Fallback DICOM to NIfTI conversion using pydicom and nibabel.
        
        Args:
            dicom_dir (str): Directory containing DICOM files
            output_path (str): Output NIfTI file path
            modality (str): Modality to convert
        """
        # Read all DICOM files
        dicom_files = sorted([
            os.path.join(dicom_dir, f) for f in os.listdir(dicom_dir)
            if f.endswith('.dcm') or not f.startswith('.')
        ])
        
        if not dicom_files:
            raise ValueError(f"No DICOM files found in {dicom_dir}")
        
        # Read first slice to get metadata
        first_slice = pydicom.dcmread(dicom_files[0])
        
        # Filter by modality if multiple modalities present
        if hasattr(first_slice, 'Modality'):
            dicom_files = [
                f for f in dicom_files
                if pydicom.dcmread(f, stop_before_pixels=True).Modality == modality
            ]
        
        # Sort by instance number or slice location
        slices = []
        for dcm_file in dicom_files:
            ds = pydicom.dcmread(dcm_file)
            slices.append(ds)
        
        # Sort slices
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        
        # Create 3D volume
        img_shape = (slices[0].Rows, slices[0].Columns, len(slices))
        volume = np.zeros(img_shape, dtype=np.float32)
        
        for i, dcm_slice in enumerate(slices):
            volume[:, :, i] = dcm_slice.pixel_array.astype(np.float32)
            
            # Apply rescale slope and intercept if present
            if hasattr(dcm_slice, 'RescaleSlope'):
                volume[:, :, i] = volume[:, :, i] * dcm_slice.RescaleSlope
            if hasattr(dcm_slice, 'RescaleIntercept'):
                volume[:, :, i] = volume[:, :, i] + dcm_slice.RescaleIntercept
        
        # Get voxel spacing
        pixel_spacing = slices[0].PixelSpacing
        slice_thickness = float(slices[0].SliceThickness) if hasattr(slices[0], 'SliceThickness') else 1.0
        
        # Calculate slice spacing from positions if available
        if len(slices) > 1:
            pos1 = np.array(slices[0].ImagePositionPatient)
            pos2 = np.array(slices[1].ImagePositionPatient)
            slice_spacing = np.linalg.norm(pos2 - pos1)
        else:
            slice_spacing = slice_thickness
        
        # Create affine matrix
        spacing = [float(pixel_spacing[0]), float(pixel_spacing[1]), slice_spacing]
        affine = np.diag([spacing[0], spacing[1], spacing[2], 1.0])
        
        # Get image position for proper origin
        if hasattr(slices[0], 'ImagePositionPatient'):
            origin = slices[0].ImagePositionPatient
            affine[0, 3] = origin[0]
            affine[1, 3] = origin[1]
            affine[2, 3] = origin[2]
        
        # Create NIfTI image
        nifti_img = nib.Nifti1Image(volume, affine)
        
        # Save
        nib.save(nifti_img, output_path)
        print(f"Converted DICOM to NIfTI: {output_path}")
        print(f"  Shape: {volume.shape}")
        print(f"  Spacing: {spacing}")
    
    def load_nifti(self, nifti_path):
        """
        Load NIfTI file and return image data and metadata.
        
        Args:
            nifti_path (str): Path to NIfTI file
            
        Returns:
            tuple: (image_data, affine, spacing)
        """
        nifti_img = nib.load(nifti_path)
        image_data = nifti_img.get_fdata()
        affine = nifti_img.affine
        
        # Extract spacing from affine
        spacing = np.sqrt(np.sum(affine[:3, :3]**2, axis=0))
        
        return image_data, affine, spacing
    
    def save_nifti(self, image_data, affine, output_path):
        """
        Save image data as NIfTI file.
        
        Args:
            image_data (np.ndarray): Image data
            affine (np.ndarray): Affine transformation matrix
            output_path (str): Output file path
        """
        nifti_img = nib.Nifti1Image(image_data, affine)
        nib.save(nifti_img, output_path)
