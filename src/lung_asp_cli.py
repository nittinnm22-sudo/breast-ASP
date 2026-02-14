"""
Command-line interface for Lung ASP segmentation pipeline.
"""
import argparse
import logging
from pathlib import Path
import sys

# Add src to path if running as script
sys.path.insert(0, str(Path(__file__).parent))

from Lung_ASP import process_case
from Mask_QC import generate_qc_overlays


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='FDG PET/CT Lung Tumor Segmentation with Mediastinal Exclusion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  lung-asp --pet pet.nii.gz --ct ct.nii.gz --output ./results --case patient001
        """
    )
    
    parser.add_argument(
        '--pet',
        type=str,
        required=True,
        help='Path to PET NIfTI file (SUV corrected)'
    )
    
    parser.add_argument(
        '--ct',
        type=str,
        required=True,
        help='Path to CT NIfTI file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory'
    )
    
    parser.add_argument(
        '--case',
        type=str,
        default='case',
        help='Case identifier (default: case)'
    )
    
    parser.add_argument(
        '--generate-qc',
        action='store_true',
        help='Generate QC overlay images'
    )
    
    parser.add_argument(
        '--qc-dpi',
        type=int,
        default=300,
        help='QC image DPI (default: 300)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Validate inputs
    pet_path = Path(args.pet)
    ct_path = Path(args.ct)
    output_dir = Path(args.output)
    
    if not pet_path.exists():
        logger.error(f"PET file not found: {pet_path}")
        sys.exit(1)
    
    if not ct_path.exists():
        logger.error(f"CT file not found: {ct_path}")
        sys.exit(1)
    
    # Run segmentation pipeline
    try:
        logger.info("Starting lung tumor segmentation pipeline...")
        
        # FIXED: Match actual function signature
        metrics = process_case(
            pet_nifti_path=pet_path,
            ct_nifti_path=ct_path,
            out_dir=output_dir,
            case_id=args.case
        )
        
        logger.info("Segmentation complete!")
        logger.info(f"Results saved to: {output_dir}")
        
        # Print metrics summary
        print("\n" + "="*60)
        print(f"METRICS SUMMARY - Case: {args.case}")
        print("="*60)
        print(f"SUVmax:        {metrics.get('SUVmax', 0):.2f}")
        print(f"SUVmean:       {metrics.get('SUVmean', 0):.2f}")
        print(f"SUVpeak:       {metrics.get('SUVpeak', 0):.2f}")
        print(f"MTV (mL):      {metrics.get('MTV_ml', 0):.2f}")
        print(f"TLG (g):       {metrics.get('TLG_g', 0):.2f}")
        print(f"Dmax (mm):     {metrics.get('Dmax_mm', 0):.2f}")
        print(f"NHOCmax:       {metrics.get('NHOCmax', 0):.3f}")
        print(f"NHOPmax:       {metrics.get('NHOPmax', 0):.3f}")
        print(f"Sphericity:    {metrics.get('sphericity', 0):.3f}")
        print(f"Asphericity:   {metrics.get('asphericity', 0):.3f}")
        print("="*60)
        
        # Generate QC overlays if requested
        if args.generate_qc:
            logger.info("Generating QC overlays...")
            
            pet_resampled_path = output_dir / f"{args.case}_pet_resampled.nii.gz"
            tumor_mask_path = output_dir / f"{args.case}_tumor_mask.nii.gz"
            body_mask_path = output_dir / f"{args.case}_body_mask.nii.gz"
            qc_output_path = output_dir / f"{args.case}_qc_overlay.png"
            
            generate_qc_overlays(
                pet_nifti_path=pet_resampled_path,
                ct_nifti_path=ct_path,
                tumor_mask_path=tumor_mask_path,
                constraint_mask_path=body_mask_path,
                output_path=qc_output_path,
                dpi=args.qc_dpi
            )
            
            logger.info(f"QC overlays saved to: {qc_output_path}")
        
        logger.info("All tasks completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
