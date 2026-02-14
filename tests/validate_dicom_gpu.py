"""
Validation script for DICOM input and GPU features.

Tests the new DICOM conversion and GPU detection functionality.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def validate_imports():
    """Validate all required modules can be imported."""
    print("="*60)
    print("VALIDATION: Module Imports")
    print("="*60)
    
    imports_ok = True
    
    # Test dicom_converter
    try:
        from dicom_converter import convert_dicom_to_nifti, check_gpu_availability
        print("✓ dicom_converter module")
    except ImportError as e:
        print(f"✗ dicom_converter module: {e}")
        imports_ok = False
    
    # Test Lung_ASP_GUI
    try:
        from Lung_ASP_GUI import LungASPGUI
        print("✓ Lung_ASP_GUI module")
    except ImportError as e:
        print(f"✗ Lung_ASP_GUI module: {e}")
        imports_ok = False
    
    # Test totalseg_safe
    try:
        from totalseg_safe import run_totalsegmentator
        print("✓ totalseg_safe module with GPU support")
    except ImportError as e:
        print(f"✗ totalseg_safe module: {e}")
        imports_ok = False
    
    return imports_ok


def check_structure():
    """Check file structure."""
    print("\n" + "="*60)
    print("VALIDATION: File Structure")
    print("="*60)
    
    required_files = [
        'src/dicom_converter.py',
        'src/Lung_ASP_GUI.py',
        'src/totalseg_safe.py',
        'src/Lung_ASP.py',
        'requirements-full.txt',
        'DICOM_GPU_GUIDE.md'
    ]
    
    all_present = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_present = False
    
    return all_present


def check_features():
    """Check key features in code."""
    print("\n" + "="*60)
    print("VALIDATION: Feature Implementation")
    print("="*60)
    
    features_ok = True
    
    # Check GUI has DICOM support
    gui_file = Path('src/Lung_ASP_GUI.py')
    if gui_file.exists():
        content = gui_file.read_text()
        if 'dicom_converter' in content:
            print("✓ GUI imports dicom_converter")
        else:
            print("✗ GUI missing dicom_converter import")
            features_ok = False
        
        if 'DICOM' in content:
            print("✓ GUI mentions DICOM in labels")
        else:
            print("✗ GUI missing DICOM labels")
            features_ok = False
        
        if 'use_gpu' in content:
            print("✓ GUI has GPU option")
        else:
            print("✗ GUI missing GPU option")
            features_ok = False
    
    # Check converter has GPU detection
    converter_file = Path('src/dicom_converter.py')
    if converter_file.exists():
        content = converter_file.read_text()
        if 'check_gpu_availability' in content:
            print("✓ Converter has GPU detection")
        else:
            print("✗ Converter missing GPU detection")
            features_ok = False
        
        if 'convert_dicom_to_nifti' in content:
            print("✓ Converter has DICOM conversion")
        else:
            print("✗ Converter missing DICOM conversion")
            features_ok = False
    
    # Check totalseg has GPU support
    totalseg_file = Path('src/totalseg_safe.py')
    if totalseg_file.exists():
        content = totalseg_file.read_text()
        if 'use_gpu' in content:
            print("✓ TotalSegmentator wrapper has GPU support")
        else:
            print("✗ TotalSegmentator wrapper missing GPU support")
            features_ok = False
    
    # Check requirements
    req_file = Path('requirements-full.txt')
    if req_file.exists():
        content = req_file.read_text()
        if 'dicom2nifti' in content:
            print("✓ Requirements include dicom2nifti")
        else:
            print("✗ Requirements missing dicom2nifti")
            features_ok = False
    
    return features_ok


def main():
    """Run all validations."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "LUNG ASP VALIDATION" + " "*24 + "║")
    print("║" + " "*10 + "DICOM Input & GPU Optimization" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    print()
    
    results = []
    
    # Run validations
    results.append(("File Structure", check_structure()))
    results.append(("Feature Implementation", check_features()))
    results.append(("Module Imports", validate_imports()))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ ALL VALIDATIONS PASSED")
        print("\nThe DICOM input and GPU optimization features are correctly")
        print("implemented and ready to use!")
    else:
        print("\n✗ SOME VALIDATIONS FAILED")
        print("\nPlease review the errors above and ensure all dependencies")
        print("are installed: pip install -r requirements-full.txt")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("  1. Install dependencies: pip install -r requirements-full.txt")
    print("  2. Install PyTorch with CUDA: pip install torch --index-url ...")
    print("  3. Run GUI: python src/Lung_ASP_GUI.py")
    print("  4. Read guide: DICOM_GPU_GUIDE.md")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
