"""
Example script demonstrating breast tumor segmentation with axillary exclusion.

This script shows how to use the breast-ASP package to:
1. Segment primary breast tumors from FDG PET/CT images
2. Exclude axillary and axillary lymph node regions
3. Calculate metabolic and shape radiomics features
"""

import numpy as np
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from breast_asp.pipeline import BreastTumorPipeline
from breast_asp.segmentation import BreastTumorSegmenter
from breast_asp.exclusion import AxillaryExcluder
from breast_asp.radiomics import MetabolicRadiomics, ShapeRadiomics


def create_synthetic_pet_ct_data(shape=(100, 128, 128)):
    """
    Create synthetic PET/CT data for demonstration.
    
    Args:
        shape (tuple): Image shape (z, y, x)
        
    Returns:
        tuple: (pet_image, ct_image, spacing)
    """
    print("Creating synthetic PET/CT data...")
    
    # Create synthetic PET image with a breast tumor
    pet_image = np.random.normal(1.0, 0.5, shape).astype(np.float32)
    pet_image = np.maximum(pet_image, 0)  # Ensure non-negative
    
    # Add a primary breast tumor (high SUV, central location)
    z_center, y_center, x_center = 50, 64, 64
    tumor_radius = 10
    
    for z in range(max(0, z_center - tumor_radius), min(shape[0], z_center + tumor_radius)):
        for y in range(max(0, y_center - tumor_radius), min(shape[1], y_center + tumor_radius)):
            for x in range(max(0, x_center - tumor_radius), min(shape[2], x_center + tumor_radius)):
                dist = np.sqrt((z - z_center)**2 + (y - y_center)**2 + (x - x_center)**2)
                if dist < tumor_radius:
                    pet_image[z, y, x] = 8.0 + np.random.normal(0, 0.5)
    
    # Add axillary lymph nodes (lateral, superior, smaller SUV)
    # Left axillary node
    left_node_z, left_node_y, left_node_x = 30, 70, 30
    node_radius = 4
    for z in range(max(0, left_node_z - node_radius), min(shape[0], left_node_z + node_radius)):
        for y in range(max(0, left_node_y - node_radius), min(shape[1], left_node_y + node_radius)):
            for x in range(max(0, left_node_x - node_radius), min(shape[2], left_node_x + node_radius)):
                dist = np.sqrt((z - left_node_z)**2 + (y - left_node_y)**2 + (x - left_node_x)**2)
                if dist < node_radius:
                    pet_image[z, y, x] = 5.0 + np.random.normal(0, 0.3)
    
    # Right axillary node
    right_node_z, right_node_y, right_node_x = 30, 70, 98
    for z in range(max(0, right_node_z - node_radius), min(shape[0], right_node_z + node_radius)):
        for y in range(max(0, right_node_y - node_radius), min(shape[1], right_node_y + node_radius)):
            for x in range(max(0, right_node_x - node_radius), min(shape[2], right_node_x + node_radius)):
                dist = np.sqrt((z - right_node_z)**2 + (y - right_node_y)**2 + (x - right_node_x)**2)
                if dist < node_radius:
                    pet_image[z, y, x] = 5.5 + np.random.normal(0, 0.3)
    
    # Create synthetic CT image (simplified)
    ct_image = np.random.normal(-200, 50, shape).astype(np.float32)
    # Add breast tissue region (higher density)
    ct_image[30:70, 40:90, 40:88] = np.random.normal(20, 30, (40, 50, 48))
    
    # Voxel spacing (mm)
    spacing = (3.0, 2.0, 2.0)  # z, y, x
    
    print(f"Created synthetic data with shape {shape}, spacing {spacing}")
    print(f"PET SUV range: {pet_image.min():.2f} - {pet_image.max():.2f}")
    
    return pet_image, ct_image, spacing


def example_basic_usage():
    """Demonstrate basic usage of the pipeline."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Pipeline Usage")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_pet_ct_data()
    
    # Initialize pipeline with default parameters
    pipeline = BreastTumorPipeline(
        suv_threshold=2.5,
        min_volume_mm3=100.0,
        exclusion_margin_mm=20.0
    )
    
    # Process images
    print("\nProcessing images...")
    results = pipeline.process(pet_image, ct_image, spacing)
    
    # Display results
    print("\n--- Segmentation Results ---")
    print(f"Tumor voxels before exclusion: {np.sum(results['tumor_mask_before_exclusion'])}")
    print(f"Tumor voxels after axillary exclusion: {np.sum(results['tumor_mask'])}")
    print(f"Excluded voxels: {np.sum(results['tumor_mask_before_exclusion']) - np.sum(results['tumor_mask'])}")
    
    print("\n--- Metabolic Features ---")
    for key, value in results['metabolic_features'].items():
        print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\n--- Shape Features ---")
    for key, value in results['shape_features'].items():
        print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
    
    return results


def example_component_usage():
    """Demonstrate usage of individual components."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Individual Component Usage")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_pet_ct_data()
    
    # Step 1: Segmentation
    print("\nStep 1: Tumor Segmentation")
    segmenter = BreastTumorSegmenter(suv_threshold=2.5, min_volume_mm3=100.0)
    tumor_mask = segmenter.segment_primary_breast_region(pet_image, ct_image, spacing)
    print(f"  Initial tumor voxels: {np.sum(tumor_mask)}")
    
    # Step 2: Axillary Exclusion
    print("\nStep 2: Axillary Region Exclusion")
    excluder = AxillaryExcluder(exclusion_margin_mm=20.0)
    filtered_mask = excluder.apply_all_exclusions(tumor_mask, pet_image, ct_image, spacing)
    print(f"  Tumor voxels after exclusion: {np.sum(filtered_mask)}")
    print(f"  Excluded voxels: {np.sum(tumor_mask) - np.sum(filtered_mask)}")
    
    # Step 3: Metabolic Radiomics
    print("\nStep 3: Metabolic Radiomics Extraction")
    metabolic_extractor = MetabolicRadiomics()
    metabolic_features = metabolic_extractor.extract_features(pet_image, filtered_mask, spacing)
    print(f"  SUVmax: {metabolic_features['SUVmax']:.2f}")
    print(f"  SUVmean: {metabolic_features['SUVmean']:.2f}")
    print(f"  MTV: {metabolic_features['MTV_ml']:.2f} mL")
    print(f"  TLG: {metabolic_features['TLG']:.2f}")
    
    # Step 4: Shape Radiomics
    print("\nStep 4: Shape Radiomics Extraction")
    shape_extractor = ShapeRadiomics()
    shape_features = shape_extractor.extract_features(filtered_mask, spacing)
    print(f"  Volume: {shape_features['Volume_ml']:.2f} mL")
    print(f"  Surface Area: {shape_features['SurfaceArea_mm2']:.2f} mm²")
    print(f"  Sphericity: {shape_features['Sphericity']:.3f}")
    print(f"  Max Diameter: {shape_features['MaxDiameter_mm']:.2f} mm")


def example_with_explicit_exclusion():
    """Demonstrate usage with explicit axillary region definition."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Explicit Axillary Region Exclusion")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_pet_ct_data()
    
    # Define explicit axillary bounding boxes
    # Format: (z_min, z_max, y_min, y_max, x_min, x_max)
    axillary_bbox = {
        'left': (20, 40, 60, 80, 20, 40),  # Left axillary region
        'right': (20, 40, 60, 80, 88, 108)  # Right axillary region
    }
    
    # Initialize and run pipeline
    pipeline = BreastTumorPipeline()
    results = pipeline.process(pet_image, ct_image, spacing, axillary_bbox=axillary_bbox)
    
    print("\nUsing explicit axillary bounding boxes:")
    print(f"  Left axillary box: z[{axillary_bbox['left'][0]}:{axillary_bbox['left'][1]}], "
          f"y[{axillary_bbox['left'][2]}:{axillary_bbox['left'][3]}], "
          f"x[{axillary_bbox['left'][4]}:{axillary_bbox['left'][5]}]")
    print(f"  Right axillary box: z[{axillary_bbox['right'][0]}:{axillary_bbox['right'][1]}], "
          f"y[{axillary_bbox['right'][2]}:{axillary_bbox['right'][3]}], "
          f"x[{axillary_bbox['right'][4]}:{axillary_bbox['right'][5]}]")
    
    print(f"\nTumor voxels after exclusion: {np.sum(results['tumor_mask'])}")
    print(f"Excluded voxels: {np.sum(results['tumor_mask_before_exclusion']) - np.sum(results['tumor_mask'])}")


def example_save_features():
    """Demonstrate saving features to CSV."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Save Features to CSV")
    print("="*70)
    
    # Create synthetic data
    pet_image, ct_image, spacing = create_synthetic_pet_ct_data()
    
    # Initialize pipeline
    pipeline = BreastTumorPipeline()
    
    # Process and save features
    output_path = "/tmp/breast_tumor_features.csv"
    print(f"\nProcessing and saving features to: {output_path}")
    results = pipeline.process_and_save_features(pet_image, output_path, ct_image, spacing)
    
    print(f"Features saved successfully!")
    print(f"Total features extracted: {len(results['combined_features'])}")
    
    # Display saved file
    try:
        import pandas as pd
        df = pd.read_csv(output_path)
        print(f"\nSaved CSV preview:")
        print(df.to_string())
    except Exception as e:
        print(f"Note: Could not display CSV preview: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("BREAST TUMOR SEGMENTATION WITH AXILLARY EXCLUSION")
    print("FDG PET/CT Radiomics Analysis Examples")
    print("="*70)
    
    try:
        # Run examples
        example_basic_usage()
        example_component_usage()
        example_with_explicit_exclusion()
        example_save_features()
        
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
