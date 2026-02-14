from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lung-asp",
    version="1.0.0",
    author="Research Team",
    description="FDG PET/CT Lung Tumor Segmentation with Mediastinal Exclusion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nittinnm22-sudo/lung-ASP",
    package_dir={"": "src"},
    py_modules=[
        "Lung_ASP",
        "advanced_metrics",
        "Mask_QC",
        "totalseg_safe",
        "lung_asp_cli",
        "Lung_ASP_GUI",
        "download_models",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "nibabel>=5.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "scikit-image>=0.20.0",
        "trimesh>=3.20.0",
        "matplotlib>=3.7.0",
        "pillow>=9.5.0",
        "pydicom>=2.3.0",
        "SimpleITK>=2.2.0",
        "totalsegmentator>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "lung-asp=lung_asp_cli:main",
        ],
    },
)
