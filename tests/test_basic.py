"""Basic tests for breast-ASP package."""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from breast_asp.segmentation import BreastTumorSegmenter
from breast_asp.exclusion import AxillaryExcluder
from breast_asp.radiomics import MetabolicRadiomics, ShapeRadiomics
from breast_asp.pipeline import BreastTumorPipeline


def create_test_data(shape=(50, 64, 64)):
    """Create simple test data."""
    pet_image = np.random.normal(1.0, 0.5, shape).astype(np.float32)
    pet_image = np.maximum(pet_image, 0)
    
    # Add a tumor
    z, y, x = 25, 32, 32
    r = 5
    for zi in range(max(0, z-r), min(shape[0], z+r)):
        for yi in range(max(0, y-r), min(shape[1], y+r)):
            for xi in range(max(0, x-r), min(shape[2], x+r)):
                if (zi-z)**2 + (yi-y)**2 + (xi-x)**2 < r**2:
                    pet_image[zi, yi, xi] = 8.0
    
    ct_image = np.random.normal(-200, 50, shape).astype(np.float32)
    spacing = (3.0, 2.0, 2.0)
    
    return pet_image, ct_image, spacing


def test_segmentation():
    """Test tumor segmentation."""
    print("Testing segmentation...")
    pet_image, ct_image, spacing = create_test_data()
    
    segmenter = BreastTumorSegmenter(suv_threshold=2.5, min_volume_mm3=50.0)
    mask = segmenter.segment(pet_image, spacing)
    
    assert mask is not None, "Segmentation failed"
    assert mask.shape == pet_image.shape, "Mask shape mismatch"
    assert np.sum(mask) > 0, "No tumor detected"
    print(f"  ✓ Segmented {np.sum(mask)} voxels")


def test_exclusion():
    """Test axillary exclusion."""
    print("Testing axillary exclusion...")
    pet_image, ct_image, spacing = create_test_data()
    
    segmenter = BreastTumorSegmenter(suv_threshold=2.5)
    mask = segmenter.segment(pet_image, spacing)
    
    excluder = AxillaryExcluder()
    filtered_mask = excluder.apply_all_exclusions(mask, pet_image, ct_image, spacing)
    
    assert filtered_mask is not None, "Exclusion failed"
    assert filtered_mask.shape == mask.shape, "Filtered mask shape mismatch"
    assert np.sum(filtered_mask) <= np.sum(mask), "Exclusion should not add voxels"
    print(f"  ✓ Excluded {np.sum(mask) - np.sum(filtered_mask)} voxels")


def test_metabolic_radiomics():
    """Test metabolic radiomics extraction."""
    print("Testing metabolic radiomics...")
    pet_image, _, spacing = create_test_data()
    
    segmenter = BreastTumorSegmenter(suv_threshold=2.5)
    mask = segmenter.segment(pet_image, spacing)
    
    extractor = MetabolicRadiomics()
    features = extractor.extract_features(pet_image, mask, spacing)
    
    assert features is not None, "Feature extraction failed"
    assert 'SUVmax' in features, "SUVmax missing"
    assert 'SUVmean' in features, "SUVmean missing"
    assert 'MTV_ml' in features, "MTV missing"
    assert 'TLG' in features, "TLG missing"
    assert features['SUVmax'] > 0, "SUVmax should be positive"
    print(f"  ✓ Extracted {len(features)} metabolic features")
    print(f"    SUVmax: {features['SUVmax']:.2f}, MTV: {features['MTV_ml']:.2f} mL")


def test_shape_radiomics():
    """Test shape radiomics extraction."""
    print("Testing shape radiomics...")
    pet_image, _, spacing = create_test_data()
    
    segmenter = BreastTumorSegmenter(suv_threshold=2.5)
    mask = segmenter.segment(pet_image, spacing)
    
    extractor = ShapeRadiomics()
    features = extractor.extract_features(mask, spacing)
    
    assert features is not None, "Feature extraction failed"
    assert 'Volume_ml' in features, "Volume missing"
    assert 'SurfaceArea_mm2' in features, "Surface area missing"
    assert 'Sphericity' in features, "Sphericity missing"
    assert features['Volume_ml'] > 0, "Volume should be positive"
    print(f"  ✓ Extracted {len(features)} shape features")
    print(f"    Volume: {features['Volume_ml']:.2f} mL, Sphericity: {features['Sphericity']:.3f}")


def test_pipeline():
    """Test complete pipeline."""
    print("Testing complete pipeline...")
    pet_image, ct_image, spacing = create_test_data()
    
    pipeline = BreastTumorPipeline(suv_threshold=2.5)
    results = pipeline.process(pet_image, ct_image, spacing)
    
    assert results is not None, "Pipeline failed"
    assert 'tumor_mask' in results, "Tumor mask missing"
    assert 'metabolic_features' in results, "Metabolic features missing"
    assert 'shape_features' in results, "Shape features missing"
    assert 'combined_features' in results, "Combined features missing"
    
    n_combined = len(results['combined_features'])
    print(f"  ✓ Pipeline completed successfully")
    print(f"    Extracted {n_combined} total features")


def test_empty_mask():
    """Test handling of empty masks."""
    print("Testing empty mask handling...")
    pet_image = np.ones((20, 20, 20)) * 0.5  # Low SUV, no tumor
    spacing = (2.0, 2.0, 2.0)
    
    segmenter = BreastTumorSegmenter(suv_threshold=5.0)  # High threshold
    mask = segmenter.segment(pet_image, spacing)
    
    extractor = MetabolicRadiomics()
    features = extractor.extract_features(pet_image, mask, spacing)
    
    assert features is not None, "Should handle empty mask"
    assert features['SUVmax'] == 0.0, "Empty mask should have zero features"
    print(f"  ✓ Empty mask handled correctly")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("RUNNING BREAST-ASP UNIT TESTS")
    print("="*70 + "\n")
    
    tests = [
        test_segmentation,
        test_exclusion,
        test_metabolic_radiomics,
        test_shape_radiomics,
        test_pipeline,
        test_empty_mask
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
