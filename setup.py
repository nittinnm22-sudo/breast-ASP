"""Setup configuration for breast-ASP package."""

import os
from setuptools import setup, find_packages

# Read long description
long_description = ""
try:
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
except Exception:
    long_description = "FDG PET/CT Breast and Lung Tumor Segmentation"

# Read requirements
requirements = []
try:
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except Exception:
    # Fallback requirements if file can't be read
    requirements = [
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "scikit-image>=0.18.0",
        "SimpleITK>=2.1.0",
        "pandas>=1.3.0",
        "nibabel>=3.2.0",
        "dicom2nifti>=2.4.0",
        "trimesh>=3.20.0",
        "matplotlib>=3.5.0",
        "pydicom>=2.3.0",
    ]

setup(
    name="breast-asp",
    version="1.0.0",
    author="Breast ASP Project",
    description="FDG PET/CT Breast and Lung Tumor Segmentation with Radiomics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nittinnm22-sudo/breast-ASP",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-cov>=3.0.0"],
    },
)
