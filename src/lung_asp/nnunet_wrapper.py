"""
nnU-Net Integration Module

Wrapper for nnU-Net to provide advanced lung tumor segmentation
using pre-trained deep learning models.
"""

import os
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NnUNetWrapper:
    """
    Wrapper for nnU-Net functionality.
    
    Provides deep learning-based segmentation for:
    - Lung tumor detection
    - Precise boundary delineation
    - Multi-class tissue segmentation
    """
    
    def __init__(self, model_dir=None, model_name='Task001_LungTumor'):
        """
        Initialize nnU-Net wrapper.
        
        Args:
            model_dir (str): Directory containing nnU-Net models
            model_name (str): Name of the model to use
        """
        self.model_dir = model_dir
        self.model_name = model_name
        self._nnunet_available = False
        self._initialize_nnunet()
        
    def _initialize_nnunet(self):
        """Check if nnU-Net is available and initialize."""
        try:
            from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
            from nnunetv2.paths import nnUNet_results
            
            self.nnUNetPredictor = nnUNetPredictor
            self.nnUNet_results = nnUNet_results
            self._nnunet_available = True
            logger.info("nnU-Net initialized successfully")
            
        except ImportError:
            logger.warning("nnU-Net not available. Deep learning segmentation disabled.")
            self._nnunet_available = False
    
    def is_available(self):
        """Check if nnU-Net is available."""
        return self._nnunet_available
    
    def predict(self, input_path, output_path=None, fold='all', checkpoint='checkpoint_best.pth'):
        """
        Run nnU-Net prediction on input image.
        
        Args:
            input_path (str): Path to input NIfTI file or directory
            output_path (str): Path for output segmentation
            fold (str): Which fold to use ('all', 0, 1, 2, 3, 4)
            checkpoint (str): Checkpoint file name
        
        Returns:
            np.ndarray: Segmentation mask or None if failed
        """
        if not self._nnunet_available:
            logger.warning("nnU-Net not available")
            return None
        
        try:
            logger.info(f"Running nnU-Net prediction on {input_path}")
            
            # Initialize predictor
            predictor = self.nnUNetPredictor(
                tile_step_size=0.5,
                use_gaussian=True,
                use_mirroring=True,
                perform_everything_on_gpu=True,
                device='cuda:0' if self._check_cuda() else 'cpu',
                verbose=False,
                verbose_preprocessing=False,
                allow_tqdm=True
            )
            
            # Setup model
            model_folder = self._get_model_folder()
            if model_folder is None:
                logger.error("Model folder not found")
                return None
            
            predictor.initialize_from_trained_model_folder(
                model_folder,
                use_folds=(fold,) if fold != 'all' else None,
                checkpoint_name=checkpoint,
            )
            
            # Prepare output
            if output_path is None:
                output_path = str(Path(input_path).parent / "nnunet_output.nii.gz")
            
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run prediction
            predictor.predict_from_files(
                [[input_path]],  # List of list of input files
                [str(output_path)],  # List of output files
                save_probabilities=False,
                overwrite=True,
                num_processes_preprocessing=2,
                num_processes_segmentation_export=2,
                folder_with_segs_from_prev_stage=None,
                num_parts=1,
                part_id=0,
            )
            
            logger.info(f"Prediction saved to {output_path}")
            
            # Load and return segmentation
            import nibabel as nib
            seg_img = nib.load(output_path)
            seg_data = seg_img.get_fdata()
            
            return seg_data
            
        except Exception as e:
            logger.error(f"nnU-Net prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_model_folder(self):
        """Get the model folder path."""
        if self.model_dir is not None:
            return Path(self.model_dir)
        
        # Try to find in default nnU-Net results directory
        try:
            results_dir = Path(self.nnUNet_results)
            # Typical structure: nnUNet_results/DatasetXXX_Name/Trainer__Plans/
            # This is a simplified search - adjust based on actual structure
            model_folders = list(results_dir.glob(f"**/{self.model_name}*"))
            if model_folders:
                return model_folders[0]
        except:
            pass
        
        return None
    
    def _check_cuda(self):
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def convert_to_binary_mask(self, segmentation, tumor_label=1):
        """
        Convert multi-class segmentation to binary tumor mask.
        
        Args:
            segmentation (np.ndarray): Multi-class segmentation
            tumor_label (int): Label ID for tumor class
            
        Returns:
            np.ndarray: Binary tumor mask
        """
        if segmentation is None:
            return None
        
        binary_mask = (segmentation == tumor_label).astype(np.uint8)
        return binary_mask
    
    def post_process_segmentation(self, segmentation, min_size=100):
        """
        Post-process segmentation to remove small components.
        
        Args:
            segmentation (np.ndarray): Segmentation mask
            min_size (int): Minimum component size in voxels
            
        Returns:
            np.ndarray: Cleaned segmentation
        """
        from skimage.measure import label
        from skimage.morphology import remove_small_objects
        
        # Label connected components
        labeled = label(segmentation, connectivity=3)
        
        # Remove small objects
        try:
            cleaned = remove_small_objects(labeled, max_size=min_size-1)
        except TypeError:
            # Older API
            cleaned = remove_small_objects(labeled, min_size=min_size)
        
        # Convert back to binary
        return (cleaned > 0).astype(np.uint8)


def download_nnunet_models(model_name='Task001_LungTumor', output_dir=None):
    """
    Download nnU-Net pre-trained models.
    
    Note: This is a placeholder. Actual model download would require:
    1. Models hosted on a server (Zenodo, Hugging Face, etc.)
    2. Download logic using requests/wget
    3. Model extraction and placement in correct directory
    
    Args:
        model_name (str): Name of the model to download
        output_dir (str): Directory to save models
        
    Returns:
        bool: True if successful
    """
    try:
        import requests
        from pathlib import Path
        
        if output_dir is None:
            # Use default nnU-Net directory
            try:
                from nnunetv2.paths import nnUNet_results
                output_dir = Path(nnUNet_results)
            except:
                output_dir = Path.home() / ".nnunet" / "results"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Model download for {model_name}")
        logger.info(f"Target directory: {output_dir}")
        
        # Placeholder for actual download logic
        logger.warning("Model download not implemented. Please manually place models in:")
        logger.warning(f"  {output_dir}")
        logger.warning("Models should follow nnU-Net directory structure:")
        logger.warning("  DatasetXXX_Name/Trainer__Plans/fold_X/")
        
        return False
        
    except Exception as e:
        logger.error(f"Failed to download models: {e}")
        return False
