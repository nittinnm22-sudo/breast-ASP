"""
Breast Tumor Segmentation Package for FDG PET/CT Imaging
with Axillary and Axillary Node Exclusion

This package provides tools for:
- Primary breast tumor segmentation from FDG PET/CT scans
- Axillary and axillary lymph node exclusion
- Metabolic and shape radiomics feature extraction
"""

__version__ = "1.0.0"
__author__ = "Breast ASP Project"

from .segmentation import BreastTumorSegmenter
from .radiomics import MetabolicRadiomics, ShapeRadiomics
from .exclusion import AxillaryExcluder
from .pipeline import BreastTumorPipeline

__all__ = [
    'BreastTumorSegmenter',
    'MetabolicRadiomics', 
    'ShapeRadiomics',
    'AxillaryExcluder',
    'BreastTumorPipeline'
]
