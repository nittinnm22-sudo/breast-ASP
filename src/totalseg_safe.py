"""
Safe wrapper for TotalSegmentator execution.
Ensures consistent Path object returns and error handling.
"""
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def run_totalsegmentator(
    ct_nifti_path: Path,
    output_dir: Path,
    fast: bool = False,
    force_split: bool = False,
    quiet: bool = False
) -> Path:
    """
    Run TotalSegmentator on CT NIfTI file.
    
    Parameters
    ----------
    ct_nifti_path : Path
        Path to CT NIfTI file
    output_dir : Path
        Output directory for segmentation masks
    fast : bool, optional
        Use fast mode (lower quality but faster)
    force_split : bool, optional
        Force split processing for large images
    quiet : bool, optional
        Suppress output
        
    Returns
    -------
    Path
        Path to output directory containing segmentation masks
    """
    ct_nifti_path = Path(ct_nifti_path)
    output_dir = Path(output_dir)
    
    if not ct_nifti_path.exists():
        raise FileNotFoundError(f"CT file not found: {ct_nifti_path}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "TotalSegmentator",
        "-i", str(ct_nifti_path),
        "-o", str(output_dir),
        "--ml"  # Use multilabel output
    ]
    
    if fast:
        cmd.append("--fast")
    
    if force_split:
        cmd.append("--force_split")
    
    if quiet:
        cmd.append("--quiet")
    
    try:
        logger.info(f"Running TotalSegmentator: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        if not quiet:
            logger.info("TotalSegmentator completed successfully")
        if result.stdout:
            logger.debug(f"TotalSegmentator stdout: {result.stdout}")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"TotalSegmentator failed: {e}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        raise RuntimeError(f"TotalSegmentator failed: {e}")
    
    return output_dir
