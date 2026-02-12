"""
TotalSegmentor Integration Module

Wrapper for TotalSegmentor to provide body part segmentation
and anatomical structure identification for lung tumor analysis.
"""

import os
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TotalSegmentorWrapper:
    """
    Wrapper for TotalSegmentor functionality.
    
    Provides anatomical segmentation to help with:
    - Lung region identification
    - Mediastinal structure exclusion
    - Body region masking
    """
    
    def __init__(self, model_dir=None):
        """
        Initialize TotalSegmentor wrapper.
        
        Args:
            model_dir (str): Directory containing TotalSegmentor models
        """
        self.model_dir = model_dir
        self._totalseg_available = False
        self._initialize_totalsegmentor()
        
    def _initialize_totalsegmentor(self):
        """Check if TotalSegmentor is available and initialize."""
        try:
            import totalsegmentor
            from totalsegmentor.python_api import totalsegmentor as ts_segment
            self.totalsegmentor = totalsegmentor
            self.ts_segment = ts_segment
            self._totalseg_available = True
            logger.info("TotalSegmentor initialized successfully")
        except ImportError:
            logger.warning("TotalSegmentor not available. Anatomical segmentation disabled.")
            self._totalseg_available = False
    
    def is_available(self):
        """Check if TotalSegmentor is available."""
        return self._totalseg_available
    
    def segment_ct(self, ct_path, output_path=None, fast=True, roi_subset=None):
        """
        Segment CT image using TotalSegmentor.
        
        Args:
            ct_path (str): Path to CT NIfTI file
            output_path (str): Path for output segmentation
            fast (bool): Use fast mode (lower resolution)
            roi_subset (list): List of specific ROIs to segment
                             (e.g., ['lung_upper_lobe_left', 'lung_lower_lobe_left'])
        
        Returns:
            np.ndarray: Segmentation mask or None if failed
        """
        if not self._totalseg_available:
            logger.warning("TotalSegmentor not available")
            return None
        
        try:
            # Default ROI subset for lung analysis
            if roi_subset is None:
                roi_subset = [
                    'lung_upper_lobe_left',
                    'lung_lower_lobe_left', 
                    'lung_middle_lobe_left',
                    'lung_upper_lobe_right',
                    'lung_middle_lobe_right',
                    'lung_lower_lobe_right',
                    'heart',
                    'trachea',
                    'pulmonary_artery'
                ]
            
            logger.info(f"Running TotalSegmentor on {ct_path}")
            
            # Run segmentation
            if output_path is None:
                output_path = str(Path(ct_path).parent / "totalseg_output.nii.gz")
            
            # Call TotalSegmentor
            self.ts_segment(
                ct_path,
                output_path,
                ml=True,  # Use multilabel output
                fast=fast,
                roi_subset=roi_subset,
                statistics=False
            )
            
            logger.info(f"Segmentation saved to {output_path}")
            
            # Load and return segmentation
            import nibabel as nib
            seg_img = nib.load(output_path)
            seg_data = seg_img.get_fdata()
            
            return seg_data
            
        except Exception as e:
            logger.error(f"TotalSegmentor segmentation failed: {e}")
            return None
    
    def extract_lung_mask(self, segmentation):
        """
        Extract combined lung mask from TotalSegmentor output.
        
        Args:
            segmentation (np.ndarray): TotalSegmentor segmentation output
            
        Returns:
            np.ndarray: Binary lung mask
        """
        if segmentation is None:
            return None
        
        # TotalSegmentor lung label IDs (this may vary by version)
        # Check TotalSegmentor documentation for exact label mapping
        lung_labels = [1, 2, 3, 4, 5, 6]  # Placeholder - update with actual labels
        
        lung_mask = np.isin(segmentation, lung_labels)
        return lung_mask.astype(np.uint8)
    
    def extract_mediastinal_mask(self, segmentation):
        """
        Extract mediastinal structures mask from TotalSegmentor output.
        
        Args:
            segmentation (np.ndarray): TotalSegmentor segmentation output
            
        Returns:
            np.ndarray: Binary mediastinal mask
        """
        if segmentation is None:
            return None
        
        # Mediastinal structure labels (heart, major vessels, etc.)
        mediastinal_labels = [7, 8]  # Placeholder - update with actual labels
        
        mediastinal_mask = np.isin(segmentation, mediastinal_labels)
        return mediastinal_mask.astype(np.uint8)
    
    def get_thoracic_body_mask(self, ct_image, segmentation=None):
        """
        Get thoracic body mask, optionally using TotalSegmentor output.
        
        Args:
            ct_image (np.ndarray): CT image array
            segmentation (np.ndarray): Optional TotalSegmentor segmentation
            
        Returns:
            np.ndarray: Binary body mask
        """
        # Simple threshold-based body mask
        body_mask = (ct_image > -500) & (ct_image < 1000)
        
        # Could be refined using TotalSegmentor output if available
        if segmentation is not None:
            # Use any segmented structure to define body region
            body_mask = body_mask | (segmentation > 0)
        
        return body_mask.astype(np.uint8)


def download_totalsegmentor_models(output_dir=None):
    """
    Download TotalSegmentor pre-trained models.
    
    Args:
        output_dir (str): Directory to save models
        
    Returns:
        bool: True if successful
    """
    try:
        from totalsegmentor.libs import download_pretrained_weights
        
        if output_dir is None:
            # Use default TotalSegmentor directory
            output_dir = Path.home() / ".totalsegmentor" / "nnunet" / "results"
        
        logger.info(f"Downloading TotalSegmentor models to {output_dir}")
        download_pretrained_weights(str(output_dir))
        logger.info("Models downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download models: {e}")
        return False
