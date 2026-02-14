# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Lung ASP GUI executable.

This spec file configures PyInstaller to bundle all dependencies including:
- TotalSegmentator
- nnU-Net
- All Python packages
- GUI resources

Usage:
    pyinstaller lung_asp_gui.spec
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

# Collect all submodules and data files for key packages
datas = []
binaries = []
hiddenimports = []

# Core packages
packages_to_collect = [
    'nibabel',
    'numpy',
    'scipy',
    'skimage',
    'sklearn',
    'trimesh',
    'matplotlib',
    'PIL',
    'pydicom',
    'SimpleITK',
    'totalsegmentator',
    'nnunetv2',
]

for package in packages_to_collect:
    try:
        tmp_ret = collect_all(package)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print(f"Warning: Could not collect {package}: {e}")

# Manually add hidden imports that might be missed
hiddenimports += [
    'sklearn.utils._cython_blas',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree._utils',
    'scipy.special.cython_special',
    'scipy._lib.messagestream',
    'PIL._tkinter_finder',
    'torch',
    'torchvision',
]

# Add all source modules
hiddenimports += [
    'Lung_ASP',
    'advanced_metrics',
    'Mask_QC',
    'totalseg_safe',
    'lung_asp_cli',
    'download_models',
]

# Analysis
a = Analysis(
    ['src/Lung_ASP_GUI.py'],
    pathex=[os.path.join(os.getcwd(), 'src')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LungASP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for GUI-only (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add .ico file path here if you have an icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LungASP',
)
