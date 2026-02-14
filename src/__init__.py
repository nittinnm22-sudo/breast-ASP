"""
Lung ASP - FDG PET/CT Lung Tumor Segmentation with Mediastinal Exclusion

Main package initialization.
"""

__version__ = "1.0.0"
__author__ = "Research Team"
__description__ = "FDG PET/CT Lung Tumor Segmentation with Mediastinal Exclusion"

from .Lung_ASP import process_case
from .advanced_metrics import compute_all_metrics
from .Mask_QC import generate_qc_overlays

__all__ = [
    'process_case',
    'compute_all_metrics',
    'generate_qc_overlays',
]
