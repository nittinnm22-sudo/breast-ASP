#!/usr/bin/env python
"""
Lung-ASP CLI Application
Standalone executable for lung tumor segmentation and radiomics analysis
"""

import argparse
import sys
import os
from pathlib import Path
import logging

# Add src to path if running from source
if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lung_asp.lung_pipeline import LungTumorPipeline
from lung_asp.dicom_converter import DICOMConverter


def setup_logging(verbose=False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('lung_asp_cli')


def process_dicom(args, logger):
    """Process DICOM files."""
    logger.info("Starting DICOM processing...")
    logger.info(f"PET DICOM directory: {args.pet_dicom}")
    
    # Initialize pipeline
    pipeline = LungTumorPipeline(
        suv_threshold=args.suv_threshold,
        min_volume_mm3=args.min_volume,
        use_random_walker=args.use_random_walker,
        mtv_threshold_percent=args.mtv_threshold,
        getu_a=args.getu_a
    )
    
    # Set output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Processing images...")
    
    try:
        # Process from DICOM
        results = pipeline.process_from_dicom(
            pet_dicom_dir=args.pet_dicom,
            ct_dicom_dir=args.ct_dicom,
            output_dir=str(output_dir),
            seed_point=None
        )
        
        logger.info("✓ Processing complete!")
        logger.info(f"Results saved to: {output_dir}")
        
        # Print summary
        if results.get('metabolic_features'):
            logger.info("\n=== Metabolic Features ===")
            logger.info(f"SUVmax: {results['metabolic_features']['SUVmax']:.2f}")
            logger.info(f"SUVmean: {results['metabolic_features']['SUVmean']:.2f}")
            logger.info(f"MTV: {results['metabolic_features']['MTV_ml']:.2f} mL")
            logger.info(f"TLG: {results['metabolic_features']['TLG']:.2f}")
        
        if results.get('shape_features'):
            logger.info("\n=== Shape Features ===")
            logger.info(f"Volume: {results['shape_features']['Volume_ml']:.2f} mL")
            logger.info(f"Sphericity: {results['shape_features']['Sphericity']:.3f}")
            logger.info(f"Asphericity: {results['shape_features']['Asphericity']:.3f}")
        
        if results.get('advanced_features'):
            logger.info("\n=== Advanced Metrics ===")
            logger.info(f"NHOCmax: {results['advanced_features']['NHOCmax']:.4f}")
            logger.info(f"NHOPmax: {results['advanced_features']['NHOPmax']:.4f}")
            logger.info(f"gETU: {results['advanced_features']['gETU']:.2f}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def process_nifti(args, logger):
    """Process NIfTI files."""
    logger.info("Starting NIfTI processing...")
    logger.info(f"PET NIfTI: {args.pet_nifti}")
    
    # Initialize pipeline
    pipeline = LungTumorPipeline(
        suv_threshold=args.suv_threshold,
        min_volume_mm3=args.min_volume,
        use_random_walker=args.use_random_walker,
        mtv_threshold_percent=args.mtv_threshold,
        getu_a=args.getu_a
    )
    
    # Load NIfTI files
    converter = DICOMConverter()
    
    try:
        logger.info("Loading PET image...")
        pet_image, pet_affine, pet_spacing = converter.load_nifti(args.pet_nifti)
        
        ct_image = None
        if args.ct_nifti:
            logger.info("Loading CT image...")
            ct_image, _, _ = converter.load_nifti(args.ct_nifti)
        
        # Set output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        pipeline.qc_visualizer.output_dir = str(output_dir)
        
        logger.info("Processing images...")
        
        # Process
        results = pipeline.process(
            pet_image, ct_image, pet_spacing,
            generate_qc=not args.no_qc
        )
        
        # Save results
        logger.info("Saving results...")
        mask_path = output_dir / "tumor_mask.nii.gz"
        converter.save_nifti(results['tumor_mask'].astype(float), pet_affine, str(mask_path))
        
        # Save features
        import pandas as pd
        features_path = output_dir / "tumor_features.csv"
        features_df = pd.DataFrame([results['combined_features']])
        features_df.to_csv(features_path, index=False)
        
        logger.info("✓ Processing complete!")
        logger.info(f"Mask saved: {mask_path}")
        logger.info(f"Features saved: {features_path}")
        
        # Print summary
        logger.info(f"\nTotal features extracted: {len(results['combined_features'])}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Lung-ASP: FDG PET/CT Lung Tumor Segmentation and Radiomics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process DICOM files
  lung_asp_cli --pet-dicom /path/to/pet --ct-dicom /path/to/ct --output /path/to/output
  
  # Process NIfTI files
  lung_asp_cli --pet-nifti pet.nii.gz --ct-nifti ct.nii.gz --output /path/to/output
  
  # Adjust parameters
  lung_asp_cli --pet-dicom /path/to/pet --suv-threshold 3.0 --mtv-threshold 50 --output /path/to/output
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--pet-dicom', type=str,
                            help='Path to PET DICOM directory')
    input_group.add_argument('--pet-nifti', type=str,
                            help='Path to PET NIfTI file')
    
    # Optional CT input
    parser.add_argument('--ct-dicom', type=str,
                       help='Path to CT DICOM directory (optional)')
    parser.add_argument('--ct-nifti', type=str,
                       help='Path to CT NIfTI file (optional)')
    
    # Output
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='Output directory for results')
    
    # Segmentation parameters
    parser.add_argument('--suv-threshold', type=float, default=2.5,
                       help='SUV threshold for segmentation (default: 2.5)')
    parser.add_argument('--min-volume', type=float, default=100.0,
                       help='Minimum tumor volume in mm³ (default: 100)')
    parser.add_argument('--use-random-walker', action='store_true', default=True,
                       help='Use random walker algorithm (default: True)')
    parser.add_argument('--no-random-walker', dest='use_random_walker', 
                       action='store_false',
                       help='Use threshold-based segmentation only')
    
    # Radiomics parameters
    parser.add_argument('--mtv-threshold', type=int, default=41,
                       help='MTV threshold as %% of SUVmax (default: 41)')
    parser.add_argument('--getu-a', type=float, default=1.0,
                       help='gETU power parameter (default: 1.0)')
    
    # QC options
    parser.add_argument('--no-qc', action='store_true',
                       help='Disable QC visualization generation')
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--version', action='version', version='Lung-ASP 1.0.0')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Display header
    logger.info("="*70)
    logger.info("Lung-ASP: FDG PET/CT Lung Tumor Segmentation")
    logger.info("Version 1.0.0")
    logger.info("="*70)
    
    # Process based on input type
    if args.pet_dicom:
        return process_dicom(args, logger)
    elif args.pet_nifti:
        return process_nifti(args, logger)
    else:
        logger.error("No input specified. Use --help for usage information.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
