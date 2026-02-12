# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Lung-ASP executable
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files from packages
datas = []
datas += collect_data_files('totalsegmentor', include_py_files=True)
datas += collect_data_files('nnunetv2', include_py_files=True)
datas += collect_data_files('skimage', subdir='data')
datas += collect_data_files('dicom2nifti')

# Collect all submodules
hiddenimports = []
hiddenimports += collect_submodules('totalsegmentor')
hiddenimports += collect_submodules('nnunetv2')
hiddenimports += collect_submodules('lung_asp')
hiddenimports += collect_submodules('breast_asp')
hiddenimports += collect_submodules('nibabel')
hiddenimports += collect_submodules('SimpleITK')
hiddenimports += collect_submodules('skimage')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('trimesh')
hiddenimports += collect_submodules('matplotlib')

# Additional hidden imports that might be needed
hiddenimports += [
    'numpy',
    'pandas',
    'pydicom',
    'dicom2nifti',
    'torchio',
    'tqdm',
    'PIL',
    'colorama',
    'scipy.ndimage',
    'scipy.spatial',
    'scipy.linalg',
    'skimage.measure',
    'skimage.morphology',
    'skimage.filters',
    'skimage.segmentation',
    'matplotlib.backends.backend_agg',
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
        'tkinter',  # Exclude if not using GUI
        'PyQt5',    # Exclude if not using
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Option 1: One-folder distribution (recommended for large apps with models)
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
    console=True,  # Set to False for GUI mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
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

# Option 2: One-file distribution (uncomment to use instead)
# Note: This creates a single large exe file
# exe = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     [],
#     name='lung_asp',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=True,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
#     icon=None,
# )
