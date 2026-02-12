"""
Lung Tumor Segmentation Package for FDG PET/CT Imaging

This package provides tools for:
- DICOM to NIfTI conversion with geometry preservation
- Primary lung tumor segmentation using random walker algorithm
- Mediastinal region exclusion
- Advanced metabolic and shape radiomics feature extraction
- Quality control visualization
"""

__version__ = "1.0.0"
__author__ = "Lung ASP Project"

from .dicom_converter import DICOMConverter
from .lung_segmentation import LungTumorSegmenter
from .lung_exclusion import MediastinalExcluder
from .lung_radiomics import LungMetabolicRadiomics, LungShapeRadiomics, AdvancedMetrics
from .lung_pipeline import LungTumorPipeline
from .qc_visualization import QCVisualizer

__all__ = [
    'DICOMConverter',
    'LungTumorSegmenter',
    'MediastinalExcluder',
    'LungMetabolicRadiomics',
    'LungShapeRadiomics',
    'AdvancedMetrics',
    'LungTumorPipeline',
    'QCVisualizer'
]
