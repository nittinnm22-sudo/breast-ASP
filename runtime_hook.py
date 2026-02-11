#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
runtime_hook.py - PyInstaller runtime hook for TotalSegmentator and nnU-Net

This hook is executed at runtime when the frozen application starts.
It sets up the necessary environment variables and paths for TotalSegmentator
and nnU-Net to function correctly within a PyInstaller bundle.
"""

import os
import sys

if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = sys._MEIPASS
    
    # Add bundle dir to path so bundled packages can be found
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    
    # Set environment for TotalSegmentator
    home = os.path.expanduser("~")
    totalseg_home = os.path.join(home, ".totalsegmentator")
    os.makedirs(totalseg_home, exist_ok=True)
    os.environ["TOTALSEG_HOME_DIR"] = totalseg_home
    
    # Set nnU-Net paths
    nnunet_results = os.path.join(home, ".nnunet")
    os.makedirs(nnunet_results, exist_ok=True)
    os.environ["nnUNet_results"] = nnunet_results
    os.environ["nnUNet_raw"] = os.path.join(nnunet_results, "raw")
    os.environ["nnUNet_preprocessed"] = os.path.join(nnunet_results, "preprocessed")
    
    # Set TotalSegmentator weights path for model downloads
    totalseg_weights = os.path.join(totalseg_home, "nnunet", "results")
    os.makedirs(totalseg_weights, exist_ok=True)
    os.environ["TOTALSEG_WEIGHTS_PATH"] = totalseg_weights
    
    # Ensure PATH includes the bundle directory for DLL loading (Windows)
    os.environ["PATH"] = bundle_dir + os.pathsep + os.environ.get("PATH", "")
