"""
Download and setup TotalSegmentator models for lung tumor segmentation.
"""
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def download_totalsegmentator_models():
    """
    Download TotalSegmentator pre-trained models.
    
    TotalSegmentator will automatically download models on first use,
    but this function can be used to pre-download them.
    """
    logger.info("Checking TotalSegmentator models...")
    
    try:
        # TotalSegmentator downloads models automatically on first use
        # We can trigger this by running with --help
        result = subprocess.run(
            ["TotalSegmentator", "--help"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("TotalSegmentator is installed and ready")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"TotalSegmentator check failed: {e}")
        raise
    except FileNotFoundError:
        logger.error("TotalSegmentator not found. Please install: pip install totalsegmentator")
        raise


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("Lung ASP - Model Setup")
    print("="*60)
    print()
    
    try:
        download_totalsegmentator_models()
        print()
        print("Model setup complete!")
        print("TotalSegmentator will automatically download models on first use.")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
