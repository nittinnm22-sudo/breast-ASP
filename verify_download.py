"""
File verification script for Lung ASP build.
Checks that all required files are present before building the standalone executable.

Usage:
    python verify_download.py
"""
import os
from pathlib import Path
import sys


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (Need 3.10+)"


def get_file_size_str(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    print("=" * 80)
    print("  LUNG ASP - FILE VERIFICATION FOR BUILD")
    print("=" * 80)
    print()
    
    # Check Python version first
    py_ok, py_version = check_python_version()
    print(f"Python Version: {py_version}")
    if not py_ok:
        print("  ❌ ERROR: Python 3.10 or higher required")
        print("  Download from: https://www.python.org/downloads/")
        print()
        return 1
    else:
        print("  ✓ Python version compatible")
    print()
    
    # Required files
    required_files = {
        "Source Code (src/)": [
            "src/__init__.py",
            "src/Lung_ASP.py",
            "src/Lung_ASP_GUI.py",
            "src/lung_asp_cli.py",
            "src/advanced_metrics.py",
            "src/Mask_QC.py",
            "src/totalseg_safe.py",
            "src/download_models.py",
            "src/dicom_converter.py",
        ],
        "Build Configuration (REQUIRED)": [
            "requirements-full.txt",
            "lung_asp_gui.spec",
            "build_executable.bat",
            "build_executable.sh",
        ],
        "Setup Files": [
            "setup.py",
            ".gitignore",
        ],
        "Documentation (Optional)": [
            "BUILD_INSTRUCTIONS.md",
            "PACKAGE_LIST.md",
            "QUICK_BUILD_GUIDE.md",
            "README.md",
            "COMPLETE_DOWNLOAD_BUILD_GUIDE.md",
        ]
    }
    
    all_required_present = True
    missing_required = []
    total_size = 0
    
    for category, files in required_files.items():
        is_optional = "Optional" in category
        
        print(f"{category}:")
        print("-" * 80)
        
        category_ok = True
        for filepath in files:
            path = Path(filepath)
            if path.exists():
                size = path.stat().st_size
                total_size += size
                size_str = get_file_size_str(size)
                print(f"  ✓ {filepath:<45} {size_str:>12}")
            else:
                print(f"  ✗ MISSING: {filepath}")
                if not is_optional:
                    category_ok = False
                    all_required_present = False
                    missing_required.append(filepath)
        
        if not category_ok and not is_optional:
            print(f"  ⚠️  Some required files missing in this category!")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total size of present files: {get_file_size_str(total_size)}")
    print()
    
    if all_required_present:
        print("✅ SUCCESS: All required files are present!")
        print()
        print("You are ready to build the standalone executable!")
        print()
        print("Next steps:")
        print("  Windows:   build_executable.bat")
        print("  Mac/Linux: chmod +x build_executable.sh && ./build_executable.sh")
        print()
        print("Estimated build time: 20-30 minutes")
        print("Required disk space: ~15 GB free")
        print()
        return 0
    else:
        print("❌ ERROR: Some required files are missing!")
        print()
        print("Missing files:")
        for f in missing_required:
            print(f"  - {f}")
        print()
        print("Solutions:")
        print("  1. Re-download the repository:")
        print("     git clone https://github.com/nittinnm22-sudo/breast-ASP.git")
        print()
        print("  2. Or download ZIP from:")
        print("     https://github.com/nittinnm22-sudo/breast-ASP")
        print("     Click 'Code' → 'Download ZIP'")
        print()
        return 1
    
    print("=" * 80)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
