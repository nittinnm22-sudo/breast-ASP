"""
Validation script to check code logic and structure.
This doesn't require actual data - just validates the code structure.
"""
import ast
import sys
from pathlib import Path


def check_function_signature(filepath, function_name, expected_params):
    """Check if a function has the expected parameters."""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.args.args:
            if node.name == function_name:
                actual_params = [arg.arg for arg in node.args.args]
                print(f"  Function '{function_name}' has params: {actual_params}")
                for expected in expected_params:
                    if expected in actual_params:
                        print(f"    ✓ Has expected param: {expected}")
                    else:
                        print(f"    ✗ Missing expected param: {expected}")
                return actual_params
    
    print(f"  ✗ Function '{function_name}' not found")
    return None


def check_value_in_code(filepath, value, description):
    """Check if a specific value appears in code."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    if str(value) in content:
        print(f"  ✓ Contains {description}: {value}")
        return True
    else:
        print(f"  ✗ Missing {description}: {value}")
        return False


def main():
    print("="*60)
    print("LUNG ASP VALIDATION SCRIPT")
    print("="*60)
    print()
    
    src_dir = Path("src")
    
    # Check 1: Lung_ASP.py fixes
    print("[1] Checking Lung_ASP.py fixes...")
    lung_asp = src_dir / "Lung_ASP.py"
    
    # Check undefined variable fix (out_dir instead of out_root)
    check_value_in_code(lung_asp, "out_dir", "out_dir usage")
    
    # Check correct thresholds
    check_value_in_code(lung_asp, "0.05", "5% foreground threshold")
    check_value_in_code(lung_asp, "0.02", "2% background threshold")
    check_value_in_code(lung_asp, "beta=5", "beta=5 parameter")
    check_value_in_code(lung_asp, "tol=1e-2", "tolerance=1e-2")
    
    # Check Path wrapping
    check_value_in_code(lung_asp, "Path(run_totalsegmentator", "Path() wrapping")
    
    # Check process_case signature
    check_function_signature(
        lung_asp,
        "process_case",
        ["pet_nifti_path", "ct_nifti_path", "out_dir", "case_id"]
    )
    
    print()
    
    # Check 2: advanced_metrics.py completeness
    print("[2] Checking advanced_metrics.py completeness...")
    metrics = src_dir / "advanced_metrics.py"
    
    # Check sphericity formula
    check_value_in_code(metrics, "π^(1/3)", "correct sphericity formula (comment)")
    check_value_in_code(metrics, "np.pi ** (1/3)", "correct sphericity formula (code)")
    check_value_in_code(metrics, "(6 * volume_mm3) ** (2/3)", "correct sphericity formula (6V)^(2/3)")
    
    # Check all required metrics
    metrics_to_check = [
        'SUVmax', 'SUVmean', 'SUVpeak',
        'MTV_ml', 'TLG_g',
        'Dmax_mm', 'NHOCmax', 'NHOPmax',
        'gETU', 'sphericity', 'asphericity'
    ]
    for metric in metrics_to_check:
        check_value_in_code(metrics, f"'{metric}'", f"metric {metric}")
    
    # Check gETU alpha values
    for alpha in [0.25, 0.5, 1.0, 2.0, 4.0]:
        check_value_in_code(metrics, str(alpha), f"gETU alpha={alpha}")
    
    print()
    
    # Check 3: Anatomical exclusion completeness
    print("[3] Checking anatomical exclusion completeness...")
    
    required_structures = [
        'heart', 'aorta', 'esophagus', 'trachea', 'pulmonary_vein',
        'vertebrae_T1', 'vertebrae_T12', 'vertebrae_C7', 'vertebrae_L1',
        'rib_left_1', 'rib_left_12', 'rib_right_1', 'rib_right_12',
        'sternum', 'scapula_left', 'scapula_right',
        'liver', 'spleen', 'stomach', 'kidney_left', 'kidney_right',
        'subclavian', 'thyroid', 'inferior_vena_cava', 'superior_vena_cava'
    ]
    
    for structure in required_structures:
        check_value_in_code(lung_asp, structure, f"exclusion structure {structure}")
    
    print()
    
    # Check 4: CLI function call
    print("[4] Checking lung_asp_cli.py function call...")
    cli = src_dir / "lung_asp_cli.py"
    
    check_value_in_code(cli, "pet_nifti_path=", "keyword arg pet_nifti_path")
    check_value_in_code(cli, "ct_nifti_path=", "keyword arg ct_nifti_path")
    check_value_in_code(cli, "out_dir=", "keyword arg out_dir")
    check_value_in_code(cli, "case_id=", "keyword arg case_id")
    
    print()
    
    # Check 5: GUI metric keys
    print("[5] Checking Lung_ASP_GUI.py metric keys...")
    gui = src_dir / "Lung_ASP_GUI.py"
    
    gui_metrics = [
        'SUVmax', 'SUVmean', 'SUVpeak',
        'MTV_ml', 'TLG_g',
        'Dmax_mm', 'NHOCmax', 'NHOPmax',
        'sphericity', 'asphericity',
        'gETU_a025', 'gETU_a050', 'gETU_a100', 'gETU_a200', 'gETU_a400'
    ]
    
    for metric in gui_metrics:
        check_value_in_code(gui, f"'{metric}'", f"GUI metric key {metric}")
    
    print()
    
    # Check 6: setup.py configuration
    print("[6] Checking setup.py configuration...")
    setup = Path("setup.py")
    
    check_value_in_code(setup, 'lung-asp', "package name lung-asp")
    check_value_in_code(setup, 'Lung Tumor Segmentation', "lung tumor in description")
    
    print()
    
    # Check 7: File structure
    print("[7] Checking file structure...")
    required_files = [
        'src/Lung_ASP.py',
        'src/advanced_metrics.py',
        'src/Mask_QC.py',
        'src/totalseg_safe.py',
        'src/lung_asp_cli.py',
        'src/Lung_ASP_GUI.py',
        'src/download_models.py',
        'setup.py',
        'requirements.txt',
        '.gitignore',
        'build_full.sh',
        'build_full.bat',
        'RUN_GUI.bat'
    ]
    
    for filepath in required_files:
        if Path(filepath).exists():
            print(f"  ✓ {filepath} exists")
        else:
            print(f"  ✗ {filepath} missing")
    
    print()
    print("="*60)
    print("VALIDATION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
