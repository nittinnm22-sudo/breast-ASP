# -*- mode: python ; coding: utf-8 -*-
"""
Portable PyInstaller spec for Breast-ASP executable build.
This spec file is designed to be platform-independent and uses relative paths.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the directory containing this spec file
spec_root = os.path.dirname(os.path.abspath(SPEC))

# Collect data files and hidden imports
totalseg_datas = collect_data_files('totalsegmentator')
nnunet_datas = collect_data_files('nnunetv2')

# Hidden imports required for dynamic loading
hiddenimports = [
    'scipy.spatial.transform._rotation_groups',
    'scipy.special.cython_special',
    'skimage.feature._orb_descriptor_positions',
    'torch',
    'torchvision',
    'dynamic_network_architectures',
    'dynamic_network_architectures.architectures.unet',
    'dynamic_network_architectures.building_blocks.residual_encoders',
    'dynamic_network_architectures.building_blocks.helper',
    'acvl_utils',
    'acvl_utils.cropping_and_padding.padding',
    'batchgenerators',
    'batchgenerators.transforms',
    'nnunetv2',
    'nnunetv2.inference',
    'nnunetv2.inference.predict_from_raw_data',
    'nnunetv2.imageio',
    'nnunetv2.paths',
    'totalsegmentator',
    'totalsegmentator.python_api',
    'totalsegmentator.libs',
]

# Add all submodules
hiddenimports += collect_submodules('dynamic_network_architectures')
hiddenimports += collect_submodules('nnunetv2')
hiddenimports += collect_submodules('totalsegmentator')
hiddenimports += collect_submodules('acvl_utils')
hiddenimports += collect_submodules('batchgenerators')

# Analysis
a = Analysis(
    [os.path.join(spec_root, 'Breast_ASP_GUI.py')],
    pathex=[spec_root],
    binaries=[],
    datas=totalseg_datas + nnunet_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tensorflow',
        'tensorboard',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'tkinter.test',
    ],
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
    name='BreastASP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed mode (set to True for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BreastASP',
)
