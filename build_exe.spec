# -*- mode: python ; coding: utf-8 -*-
"""
Portable PyInstaller spec for Breast-ASP executable build.
This spec file is designed to be platform-independent and uses relative paths.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Increase recursion limit for deep import trees
sys.setrecursionlimit(10000)

block_cipher = None

# Get the directory containing this spec file
spec_root = os.path.dirname(os.path.abspath(SPEC))

# Collect data files and hidden imports
totalseg_datas = collect_data_files('totalsegmentator')
nnunet_datas = collect_data_files('nnunetv2')
nibabel_datas = collect_data_files('nibabel')
pydicom_datas = collect_data_files('pydicom')
certifi_datas = collect_data_files('certifi')
matplotlib_datas = collect_data_files('matplotlib')
simpleitk_datas = collect_data_files('SimpleITK')

# Combine all data files
all_datas = (
    totalseg_datas + 
    nnunet_datas + 
    nibabel_datas + 
    pydicom_datas + 
    certifi_datas + 
    matplotlib_datas + 
    simpleitk_datas
)

# Add application Python files as data files
all_datas += [
    (os.path.join(spec_root, 'Breast_ASP.py'), '.'),
    (os.path.join(spec_root, 'advanced_metrics.py'), '.'),
    (os.path.join(spec_root, 'Mask_QC.py'), '.'),
]

# Hidden imports required for dynamic loading
hiddenimports = [
    # scipy modules
    'scipy.spatial.transform._rotation_groups',
    'scipy.special.cython_special',
    'scipy.ndimage',
    'scipy.spatial.distance',
    'scipy.optimize',
    # skimage modules
    'skimage.feature._orb_descriptor_positions',
    'skimage.segmentation',
    'skimage.morphology',
    'skimage.measure',
    # torch modules
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torch.autograd',
    'torch.cuda',
    'torch.backends.cudnn',
    'torch.amp',
    'torch.serialization',
    'torch._C',
    'torch._utils',
    # nibabel modules
    'nibabel.processing',
    'nibabel.nifti1',
    'nibabel.loadsave',
    'nibabel.imageclasses',
    # pydicom modules
    'pydicom',
    'pydicom.data',
    # SimpleITK
    'SimpleITK',
    # matplotlib modules
    'matplotlib.pyplot',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_tkagg',
    # PIL
    'PIL',
    'PIL.Image',
    # trimesh modules
    'trimesh',
    'trimesh.exchange',
    'trimesh.exchange.stl',
    # dynamic network architectures
    'dynamic_network_architectures',
    'dynamic_network_architectures.architectures.unet',
    'dynamic_network_architectures.building_blocks.residual_encoders',
    'dynamic_network_architectures.building_blocks.helper',
    # acvl_utils
    'acvl_utils',
    'acvl_utils.cropping_and_padding.padding',
    # batchgenerators
    'batchgenerators',
    'batchgenerators.transforms',
    # nnunetv2 modules
    'nnunetv2',
    'nnunetv2.inference',
    'nnunetv2.inference.predict_from_raw_data',
    'nnunetv2.imageio',
    'nnunetv2.paths',
    'nnunetv2.utilities',
    'nnunetv2.preprocessing',
    'nnunetv2.architecture',
    # totalsegmentator modules
    'totalsegmentator',
    'totalsegmentator.python_api',
    'totalsegmentator.libs',
    'totalsegmentator.config',
    'totalsegmentator.nifti_ext_header',
    'totalsegmentator.map_to_binary',
    # utility modules
    'pandas',
    'psutil',
    'platformdirs',
    'requests',
    'certifi',
    'charset_normalizer',
    'urllib3',
    'idna',
    # standard library modules that may need explicit inclusion
    'json',
    'csv',
    'threading',
    'datetime',
    'pathlib',
    # tkinter modules
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinter.ttk',
]

# Add all submodules for comprehensive inclusion
hiddenimports += collect_submodules('dynamic_network_architectures')
hiddenimports += collect_submodules('nnunetv2')
hiddenimports += collect_submodules('totalsegmentator')
hiddenimports += collect_submodules('acvl_utils')
hiddenimports += collect_submodules('batchgenerators')
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('nibabel')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('skimage')

# Analysis
a = Analysis(
    [os.path.join(spec_root, 'Breast_ASP_GUI.py')],
    pathex=[spec_root],
    binaries=[],
    datas=all_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(spec_root, 'runtime_hook.py')],
    excludes=[
        'tensorflow',
        'tensorboard',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'tkinter.test',
        'torchvision',  # Not needed, adds ~500MB
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
    upx=False,  # Disable UPX to prevent PyTorch DLL corruption on Windows
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
    upx=False,  # Disable UPX to prevent PyTorch DLL corruption on Windows
    upx_exclude=[],
    name='BreastASP',
)
