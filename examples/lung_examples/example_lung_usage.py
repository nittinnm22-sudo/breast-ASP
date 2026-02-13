"""
Example script demonstrating lung tumor segmentation with mediastinal exclusion.

This script shows how to use the lung_asp package to:
1. Segment primary lung tumors from FDG PET/CT images
2. Exclude mediastinal regions
3. Calculate comprehensive metabolic, shape, and advanced radiomics features
4. Generate quality control visualizations
"""

import numpy as np
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lung_asp.lung_pipeline import LungTumorPipeline
from lung_asp.lung_segmentation import LungTumorSegmenter
from lung_asp.lung_exclusion import MediastinalExcluder
from lung_asp.lung_radiomics import LungMetabolicRadiomics, LungShapeRadiomics, AdvancedMetrics
from lung_asp.qc_visualization import QCVisualizer


def create_synthetic_lung_pet_ct_data(shape=(100, 150, 150)):
    """
    Create synthetic PET/CT lung data for demonstration.
    
    Args:
        shape (tuple): Image shape (z, y, x)
        
    Returns:
        tuple: (pet_image, ct_image, spacing)
    """
    print("Creating synthetic lung PET/CT data...")
    
    # Create synthetic PET image with lung background
    pet_image = np.random.normal(1.0, 0.3, shape).astype(np.float32)
    pet_image = np.maximum(pet_image, 0)
    
    # Add a peripheral lung tumor (right upper lobe)
    tumor_z, tumor_y, tumor_x = 40, 60, 110  # Peripheral, right side
    tumor_radius = 8
    
    for z in range(max(0, tumor_z - tumor_radius), min(shape[0], tumor_z + tumor_radius)):
        for y in range(max(0, tumor_y - tumor_radius), min(shape[1], tumor_y + tumor_radius)):
            for x in range(max(0, tumor_x - tumor_radius), min(shape[2], tumor_x + tumor_radius)):
                dist = np.sqrt((z - tumor_z)**2 + (y - tumor_y)**2 + (x - tumor_x)**2)
                if dist < tumor_radius:
                    pet_image[z, y, x] = 10.0 + np.random.normal(0, 0.8)
    
    # Add mediastinal/hilar uptake (should be excluded)
    # Central chest structures
    mediastinal_z, mediastinal_y, mediastinal_x = 45, 75, 75  # Central
    med_radius = 5
    for z in range(max(0, mediastinal_z - med_radius), min(shape[0], mediastinal_z + med_radius)):
        for y in range(max(0, mediastinal_y - med_radius), min(shape[1], mediastinal_y + med_radius)):
            for x in range(max(0, mediastinal_x - med_radius), min(shape[2], mediastinal_x + med_radius)):
                dist = np.sqrt((z - mediastinal_z)**2 + (y - mediastinal_y)**2 + (x - mediastinal_x)**2)
                if dist < med_radius:
                    pet_image[z, y, x] = 6.0 + np.random.normal(0, 0.5)
    
    # Create synthetic CT image
    ct_image = np.random.normal(-800, 100, shape).astype(np.float32)  # Lung field
    
    # Add thoracic structures
    # Body outline (higher HU)
    body_mask = np.zeros(shape, dtype=bool)
    center_y, center_x = shape[1] // 2, shape[2] // 2
    for z in range(shape[0]):
        for y in range(shape[1]):
            for x in range(shape[2]):
                dist_from_center = np.sqrt((y - center_y)**2 + (x - center_x)**2)
                if dist_from_center < min(shape[1], shape[2]) * 0.45:
                    body_mask[z, y, x] = True
    
    ct_image[body_mask] = np.random.normal(-700, 200, np.sum(body_mask))
    
    # Mediastinum (soft tissue HU)
    ct_image[30:60, 60:90, 60:90] = np.random.normal(40, 20, (30, 30, 30))
    
    # Voxel spacing (mm)
    spacing = (3.0, 2.5, 2.5)  # z, y, x
    
    print(f"Created synthetic data with shape {shape}, spacing {spacing}")
    print(f"PET SUV range: {pet_image.min():.2f} - {pet_image.max():.2f}")
    print(f"CT HU range: {ct_image.min():.0f} - {ct_image.max():.0f}")
    
    return pet_image, ct_image, spacing


def example_basic_pipeline():
    """Demonstrate basic usage of the lung tumor pipeline."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Lung Tumor Pipeline Usage")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_lung_pet_ct_data()
    
    # Initialize pipeline
    pipeline = LungTumorPipeline(
        suv_threshold=2.5,
        min_volume_mm3=200.0,
        use_random_walker=True,
        mtv_threshold_percent=41,
        isotropic_spacing=1.0,
        getu_a=1.0
    )
    
    # Process images (disable QC for faster execution)
    print("\nProcessing images...")
    results = pipeline.process(pet_image, ct_image, spacing, generate_qc=False)
    
    # Display results
    print("\n--- Segmentation Results ---")
    print(f"Tumor voxels before exclusion: {np.sum(results['tumor_mask_before_exclusion'])}")
    print(f"Tumor voxels after mediastinal exclusion: {np.sum(results['tumor_mask'])}")
    print(f"Excluded voxels: {np.sum(results['tumor_mask_before_exclusion']) - np.sum(results['tumor_mask'])}")
    
    print("\n--- Metabolic Features ---")
    for key, value in results['metabolic_features'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n--- Shape Features ---")
    for key, value in results['shape_features'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n--- Advanced Metrics ---")
    for key, value in results['advanced_features'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    return results


def example_component_usage():
    """Demonstrate usage of individual components."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Individual Component Usage")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_lung_pet_ct_data()
    
    # Step 1: Segmentation
    print("\nStep 1: Lung Tumor Segmentation with Random Walker")
    segmenter = LungTumorSegmenter(suv_threshold=2.5, min_volume_mm3=200.0, 
                                   use_random_walker=True)
    tumor_mask = segmenter.segment(pet_image, ct_image, spacing)
    print(f"  Initial tumor voxels: {np.sum(tumor_mask)}")
    
    # Step 2: Mediastinal Exclusion
    print("\nStep 2: Mediastinal Region Exclusion")
    excluder = MediastinalExcluder()
    filtered_mask = excluder.apply_all_exclusions(tumor_mask, pet_image, ct_image, spacing)
    print(f"  Tumor voxels after exclusion: {np.sum(filtered_mask)}")
    print(f"  Excluded voxels: {np.sum(tumor_mask) - np.sum(filtered_mask)}")
    
    # Step 3: Metabolic Radiomics
    print("\nStep 3: Metabolic Radiomics Extraction")
    metabolic_extractor = LungMetabolicRadiomics()
    metabolic_features = metabolic_extractor.extract_features(pet_image, filtered_mask, 
                                                              spacing, mtv_threshold_percent=41)
    print(f"  SUVmax: {metabolic_features['SUVmax']:.2f}")
    print(f"  SUVmean: {metabolic_features['SUVmean']:.2f}")
    print(f"  SUVpeak: {metabolic_features['SUVpeak']:.2f}")
    print(f"  MTV (41% SUVmax): {metabolic_features['MTV_ml']:.2f} mL")
    print(f"  TLG: {metabolic_features['TLG']:.2f}")
    
    # Step 4: Shape Radiomics
    print("\nStep 4: Shape Radiomics Extraction (with Marching Cubes)")
    shape_extractor = LungShapeRadiomics(isotropic_spacing=1.0)
    shape_features = shape_extractor.extract_features(filtered_mask, spacing, 
                                                      resample_isotropic=True)
    print(f"  Volume: {shape_features['Volume_ml']:.2f} mL")
    print(f"  Surface Area: {shape_features['SurfaceArea_mm2']:.2f} mm²")
    print(f"  Sphericity (Ψ): {shape_features['Sphericity']:.3f}")
    print(f"  Asphericity (ASP): {shape_features['Asphericity']:.3f}")
    print(f"  Max Diameter: {shape_features['MaxDiameter_mm']:.2f} mm")
    
    # Step 5: Advanced Metrics
    print("\nStep 5: Advanced Geometric and Uptake Metrics")
    advanced_calc = AdvancedMetrics()
    advanced_features = advanced_calc.extract_all_advanced_metrics(
        filtered_mask, pet_image, spacing, getu_a=1.0
    )
    print(f"  NHOCmax (Hotspot-to-Centroid): {advanced_features['NHOCmax']:.4f}")
    print(f"  NHOPmax (Hotspot-to-Perimeter): {advanced_features['NHOPmax']:.4f}")
    print(f"  Dmax (Max 3D diameter): {advanced_features['Dmax_mm']:.2f} mm")
    print(f"  gETU (a=1.0): {advanced_features['gETU']:.2f}")


def example_advanced_getu():
    """Demonstrate gETU calculation with different parameters."""
    print("\n" + "="*70)
    print("EXAMPLE 3: gETU with Different Power Parameters")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_lung_pet_ct_data()
    
    # Segment tumor
    segmenter = LungTumorSegmenter(suv_threshold=2.5)
    tumor_mask = segmenter.segment(pet_image, ct_image, spacing)
    tumor_mask = segmenter.get_largest_lesion(tumor_mask)
    
    # Calculate gETU with different power parameters
    advanced_calc = AdvancedMetrics()
    
    print("\ngETU values with different power parameters:")
    print("(a=1 gives TLG-like, a→∞ emphasizes SUVmax, a→0 emphasizes volume)")
    
    a_values = [0.25, 0.5, 1.0, 2.0, 5.0]
    for a in a_values:
        getu_result = advanced_calc.calculate_getu(pet_image, tumor_mask, spacing, a=a)
        print(f"  a = {a:4.2f}: gETU = {getu_result['gETU']:10.4f}")


def example_with_qc():
    """Demonstrate pipeline with QC visualization."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Pipeline with Quality Control Visualization")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_lung_pet_ct_data()
    
    # Initialize pipeline
    pipeline = LungTumorPipeline(
        suv_threshold=2.5,
        min_volume_mm3=200.0,
        use_random_walker=True
    )
    
    # Set output directory for QC images
    qc_dir = "/tmp/lung_qc"
    pipeline.qc_visualizer.output_dir = qc_dir
    
    print(f"\nProcessing with QC generation (output: {qc_dir})...")
    results = pipeline.process(pet_image, ct_image, spacing, generate_qc=True)
    
    if results.get('qc_overlay_path'):
        print(f"  QC overlay saved: {results['qc_overlay_path']}")
    if results.get('qc_report_path'):
        print(f"  QC report saved: {results['qc_report_path']}")
    
    print(f"\nTotal features extracted: {len(results['combined_features'])}")


def example_save_results():
    """Demonstrate saving results to files."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Save Results to Files")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_lung_pet_ct_data()
    
    # Initialize pipeline
    pipeline = LungTumorPipeline()
    
    # Process and save
    output_dir = "/tmp/lung_results"
    print(f"\nProcessing and saving results to: {output_dir}")
    results = pipeline.process_and_save(
        pet_image, output_dir, ct_image, spacing,
        mask_filename="lung_tumor_mask.nii.gz",
        features_filename="lung_tumor_features.csv"
    )
    
    print(f"\nSaved files:")
    print(f"  Mask: {results['mask_path']}")
    print(f"  Features: {results['features_path']}")
    if results.get('qc_overlay_path'):
        print(f"  QC Overlay: {results['qc_overlay_path']}")
    if results.get('qc_report_path'):
        print(f"  QC Report: {results['qc_report_path']}")
    
    # Display saved features
    try:
        import pandas as pd
        df = pd.read_csv(results['features_path'])
        print(f"\nFeatures CSV preview:")
        print(f"Total features: {len(df.columns)}")
        print("\nSample features:")
        for col in list(df.columns)[:10]:
            print(f"  {col}: {df[col].values[0]}")
    except Exception as e:
        print(f"Note: Could not display CSV preview: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("LUNG TUMOR SEGMENTATION WITH MEDIASTINAL EXCLUSION")
    print("FDG PET/CT Advanced Radiomics Examples")
    print("="*70)
    
    try:
        # Run examples
        example_basic_pipeline()
        example_component_usage()
        example_advanced_getu()
        example_with_qc()
        example_save_results()
        
        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
