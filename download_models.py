#!/usr/bin/env python
"""
Model Download Helper for Lung-ASP

This script helps download and setup pre-trained models for:
- TotalSegmentor
- nnU-Net

Models are stored in appropriate directories for the executable to use.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_totalsegmentor_models(output_dir=None):
    """Download TotalSegmentor models."""
    logger.info("="*70)
    logger.info("Downloading TotalSegmentor Models")
    logger.info("="*70)
    
    try:
        # Check if totalsegmentor is installed
        import totalsegmentor
        logger.info("TotalSegmentor package found")
        
        # Run the download command
        logger.info("Starting model download...")
        logger.info("This may take 10-30 minutes depending on your connection...")
        
        result = subprocess.run(
            ['totalsegmentor', '--download_models'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✓ TotalSegmentor models downloaded successfully!")
            
            # Show model location
            model_dir = Path.home() / ".totalsegmentor"
            logger.info(f"Models stored in: {model_dir}")
            return True
        else:
            logger.error("Model download failed!")
            logger.error(result.stderr)
            return False
            
    except ImportError:
        logger.error("TotalSegmentor not installed!")
        logger.error("Install with: pip install totalsegmentor")
        return False
    except Exception as e:
        logger.error(f"Error downloading models: {e}")
        return False


def download_nnunet_models(model_url=None, output_dir=None):
    """Download nnU-Net models."""
    logger.info("="*70)
    logger.info("nnU-Net Model Setup")
    logger.info("="*70)
    
    if output_dir is None:
        try:
            from nnunetv2.paths import nnUNet_results
            output_dir = Path(nnUNet_results)
        except:
            output_dir = Path.home() / ".nnunet" / "results"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"nnU-Net models directory: {output_dir}")
    
    if model_url:
        logger.info(f"Downloading from: {model_url}")
        # Add download logic here
        logger.warning("Automatic download not implemented yet")
        logger.info("Please manually download models and place them in:")
        logger.info(f"  {output_dir}")
        return False
    else:
        logger.warning("No model URL provided")
        logger.info("To use nnU-Net models:")
        logger.info("1. Obtain pre-trained lung tumor models")
        logger.info("2. Place them in the nnU-Net results directory:")
        logger.info(f"   {output_dir}")
        logger.info("3. Ensure they follow the structure:")
        logger.info("   DatasetXXX_LungTumor/")
        logger.info("     └── nnUNetTrainer__nnUNetPlans/")
        logger.info("         └── fold_X/")
        logger.info("             ├── checkpoint_best.pth")
        logger.info("             └── ...")
        return False


def check_models():
    """Check if models are installed."""
    logger.info("="*70)
    logger.info("Checking Installed Models")
    logger.info("="*70)
    
    # Check TotalSegmentor
    ts_dir = Path.home() / ".totalsegmentor"
    if ts_dir.exists() and any(ts_dir.glob("**/*.pkl")):
        logger.info("✓ TotalSegmentor models found")
        logger.info(f"  Location: {ts_dir}")
    else:
        logger.warning("✗ TotalSegmentor models not found")
    
    # Check nnU-Net
    try:
        from nnunetv2.paths import nnUNet_results
        nnunet_dir = Path(nnUNet_results)
    except:
        nnunet_dir = Path.home() / ".nnunet" / "results"
    
    if nnunet_dir.exists() and any(nnunet_dir.glob("**/checkpoint*.pth")):
        logger.info("✓ nnU-Net models found")
        logger.info(f"  Location: {nnunet_dir}")
    else:
        logger.warning("✗ nnU-Net models not found")
        logger.info(f"  Expected location: {nnunet_dir}")


def setup_for_executable(dist_dir):
    """Setup models for inclusion in executable."""
    logger.info("="*70)
    logger.info("Setting Up Models for Executable")
    logger.info("="*70)
    
    dist_dir = Path(dist_dir)
    models_dir = dist_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Copying models to: {models_dir}")
    
    # Copy TotalSegmentor models
    ts_dir = Path.home() / ".totalsegmentor"
    if ts_dir.exists():
        logger.info("Copying TotalSegmentor models...")
        import shutil
        ts_target = models_dir / "totalsegmentor"
        if not ts_target.exists():
            shutil.copytree(ts_dir, ts_target)
            logger.info(f"✓ TotalSegmentor models copied")
        else:
            logger.info("  Models already exist, skipping")
    else:
        logger.warning("  TotalSegmentor models not found")
    
    # Copy nnU-Net models
    try:
        from nnunetv2.paths import nnUNet_results
        nnunet_dir = Path(nnUNet_results)
    except:
        nnunet_dir = Path.home() / ".nnunet" / "results"
    
    if nnunet_dir.exists():
        logger.info("Copying nnU-Net models...")
        import shutil
        nnunet_target = models_dir / "nnunet"
        if not nnunet_target.exists():
            shutil.copytree(nnunet_dir, nnunet_target)
            logger.info(f"✓ nnU-Net models copied")
        else:
            logger.info("  Models already exist, skipping")
    else:
        logger.warning("  nnU-Net models not found")
    
    logger.info(f"\nModels directory: {models_dir}")
    logger.info("These models will be bundled with the executable")


def main():
    parser = argparse.ArgumentParser(
        description='Download and setup models for Lung-ASP',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--download-totalseg', action='store_true',
                       help='Download TotalSegmentor models')
    parser.add_argument('--download-nnunet', action='store_true',
                       help='Download nnU-Net models (requires URL)')
    parser.add_argument('--nnunet-url', type=str,
                       help='URL for nnU-Net models')
    parser.add_argument('--check', action='store_true',
                       help='Check which models are installed')
    parser.add_argument('--setup-exe', type=str,
                       help='Setup models for executable (provide dist directory)')
    parser.add_argument('--all', action='store_true',
                       help='Download all models')
    
    args = parser.parse_args()
    
    if args.check or (not args.download_totalseg and not args.download_nnunet 
                     and not args.setup_exe and not args.all):
        check_models()
    
    if args.download_totalseg or args.all:
        download_totalsegmentor_models()
    
    if args.download_nnunet or args.all:
        download_nnunet_models(args.nnunet_url)
    
    if args.setup_exe:
        setup_for_executable(args.setup_exe)
    
    logger.info("\nDone!")


if __name__ == '__main__':
    main()
