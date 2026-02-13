# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Lung-ASP executable (Lite version)
This version excludes heavy ML dependencies for faster building
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect essential data files only
datas = []
try:
    datas += collect_data_files('skimage', subdir='data')
except:
    pass

try:
    datas += collect_data_files('dicom2nifti')
except:
    pass

# Collect essential submodules
hiddenimports = []
hiddenimports += collect_submodules('lung_asp')
hiddenimports += collect_submodules('breast_asp')

# Additional hidden imports that might be needed
hiddenimports += [
    'numpy',
    'numpy.core',
    'numpy.lib',
    'pandas',
    'pydicom',
    'nibabel',
    'nibabel.filebasedimages',
    'nibabel.nifti1',
    'SimpleITK',
    'scipy',
    'scipy.ndimage',
    'scipy.spatial',
    'scipy.spatial.distance',
    'scipy.linalg',
    'skimage',
    'skimage.measure',
    'skimage.morphology',
    'skimage.filters',
    'skimage.segmentation',
    'skimage.util',
    'skimage.transform',
    'trimesh',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_agg',
    'PIL',
    'PIL.Image',
    'tqdm',
    'colorama',
]

a = Analysis(
    ['lung_asp_cli.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'PyQt5',
        'totalsegmentor',
        'nnunetv2',
        'torch',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-folder distribution (recommended)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='lung_asp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lung_asp',
)
