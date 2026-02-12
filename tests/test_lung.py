"""Unit tests for lung_asp package."""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lung_asp.lung_segmentation import LungTumorSegmenter
from lung_asp.lung_exclusion import MediastinalExcluder
from lung_asp.lung_radiomics import LungMetabolicRadiomics, LungShapeRadiomics, AdvancedMetrics
from lung_asp.lung_pipeline import LungTumorPipeline


def create_test_data(shape=(30, 40, 40)):
    """Create simple test data with peripheral tumor."""
    pet_image = np.ones(shape, dtype=np.float32) * 0.5
    # Add peripheral tumor (very lateral/right side, clearly non-mediastinal)
    # Place at extreme right: x=36 (center=20, distance=16, >30% threshold)
    pet_image[13:16, 10:13, 36:39] = 8.0
    ct_image = np.random.normal(-700, 100, shape).astype(np.float32)
    spacing = (3.0, 2.5, 2.5)
    return pet_image, ct_image, spacing


def test_lung_segmentation():
    """Test lung tumor segmentation."""
    print("Testing lung tumor segmentation...")
    pet_image, ct_image, spacing = create_test_data()
    
    segmenter = LungTumorSegmenter(suv_threshold=3.0, min_volume_mm3=20.0, 
                                   use_random_walker=False)
    mask = segmenter.segment(pet_image, ct_image, spacing)
    
    assert mask is not None, "Segmentation failed"
    assert mask.shape == pet_image.shape, "Mask shape mismatch"
    assert np.sum(mask) > 0, "No tumor detected"
    print(f"  ✓ Segmented {np.sum(mask)} voxels")


def test_mediastinal_exclusion():
    """Test mediastinal exclusion."""
    print("Testing mediastinal exclusion...")
    pet_image, ct_image, spacing = create_test_data()
    
    segmenter = LungTumorSegmenter(suv_threshold=3.0)
    mask = segmenter.segment(pet_image, ct_image, spacing)
    
    excluder = MediastinalExcluder()
    filtered_mask = excluder.apply_all_exclusions(mask, pet_image, ct_image, spacing)
    
    assert filtered_mask is not None, "Exclusion failed"
    assert filtered_mask.shape == mask.shape, "Filtered mask shape mismatch"
    assert np.sum(filtered_mask) <= np.sum(mask), "Exclusion should not add voxels"
    print(f"  ✓ Excluded {np.sum(mask) - np.sum(filtered_mask)} voxels")


def test_metabolic_radiomics():
    """Test metabolic radiomics extraction."""
    print("Testing metabolic radiomics...")
    pet_image, _, spacing = create_test_data()
    
    segmenter = LungTumorSegmenter(suv_threshold=3.0)
    mask = segmenter.segment(pet_image, None, spacing)
    mask = segmenter.get_largest_lesion(mask)
    
    extractor = LungMetabolicRadiomics()
    features = extractor.extract_features(pet_image, mask, spacing, mtv_threshold_percent=41)
    
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
    
    segmenter = LungTumorSegmenter(suv_threshold=3.0)
    mask = segmenter.segment(pet_image, None, spacing)
    mask = segmenter.get_largest_lesion(mask)
    
    extractor = LungShapeRadiomics(isotropic_spacing=1.0)
    features = extractor.extract_features(mask, spacing, resample_isotropic=True)
    
    assert features is not None, "Feature extraction failed"
    assert 'Volume_ml' in features, "Volume missing"
    assert 'SurfaceArea_mm2' in features, "Surface area missing"
    assert 'Sphericity' in features, "Sphericity missing"
    assert 'Asphericity' in features, "Asphericity missing"
    assert features['Volume_ml'] > 0, "Volume should be positive"
    print(f"  ✓ Extracted {len(features)} shape features")
    print(f"    Volume: {features['Volume_ml']:.2f} mL, Sphericity: {features['Sphericity']:.3f}")


def test_advanced_metrics():
    """Test advanced metrics calculation."""
    print("Testing advanced metrics...")
    pet_image, _, spacing = create_test_data()
    
    segmenter = LungTumorSegmenter(suv_threshold=3.0)
    mask = segmenter.segment(pet_image, None, spacing)
    mask = segmenter.get_largest_lesion(mask)
    
    calculator = AdvancedMetrics()
    features = calculator.extract_all_advanced_metrics(mask, pet_image, spacing, getu_a=1.0)
    
    assert features is not None, "Advanced metrics failed"
    assert 'NHOCmax' in features, "NHOCmax missing"
    assert 'NHOPmax' in features, "NHOPmax missing"
    assert 'Dmax_mm' in features, "Dmax missing"
    assert 'gETU' in features, "gETU missing"
    print(f"  ✓ Extracted {len(features)} advanced metrics")
    print(f"    NHOCmax: {features['NHOCmax']:.4f}, Dmax: {features['Dmax_mm']:.2f} mm")


def test_pipeline():
    """Test complete pipeline."""
    print("Testing complete pipeline...")
    pet_image, ct_image, spacing = create_test_data()
    
    pipeline = LungTumorPipeline(suv_threshold=3.0, min_volume_mm3=20.0, use_random_walker=False)
    results = pipeline.process(pet_image, ct_image, spacing, generate_qc=False)
    
    assert results is not None, "Pipeline failed"
    assert 'tumor_mask' in results, "Tumor mask missing"
    assert 'metabolic_features' in results, "Metabolic features missing"
    assert 'shape_features' in results, "Shape features missing"
    assert 'advanced_features' in results, "Advanced features missing"
    assert 'combined_features' in results, "Combined features missing"
    
    n_combined = len(results['combined_features'])
    print(f"  ✓ Pipeline completed successfully")
    print(f"    Extracted {n_combined} total features")


def test_empty_mask():
    """Test handling of empty masks."""
    print("Testing empty mask handling...")
    pet_image = np.ones((20, 30, 30)) * 0.5  # Low SUV, no tumor
    spacing = (2.0, 2.0, 2.0)
    
    segmenter = LungTumorSegmenter(suv_threshold=10.0, use_random_walker=False)  # High threshold
    mask = segmenter.segment(pet_image, None, spacing)
    
    extractor = LungMetabolicRadiomics()
    features = extractor.extract_features(pet_image, mask, spacing)
    
    assert features is not None, "Should handle empty mask"
    assert features['SUVmax'] == 0.0, "Empty mask should have zero features"
    print(f"  ✓ Empty mask handled correctly")


def test_getu_different_parameters():
    """Test gETU with different power parameters."""
    print("Testing gETU with different parameters...")
    pet_image, _, spacing = create_test_data()
    
    segmenter = LungTumorSegmenter(suv_threshold=3.0)
    mask = segmenter.segment(pet_image, None, spacing)
    mask = segmenter.get_largest_lesion(mask)
    
    calculator = AdvancedMetrics()
    
    # Test different a values
    a_values = [0.5, 1.0, 2.0]
    getu_values = []
    for a in a_values:
        result = calculator.calculate_getu(pet_image, mask, spacing, a=a)
        getu_values.append(result['gETU'])
        assert result['gETU'] > 0, f"gETU should be positive for a={a}"
    
    print(f"  ✓ gETU values for different a: {getu_values}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("RUNNING LUNG_ASP UNIT TESTS")
    print("="*70 + "\n")
    
    tests = [
        test_lung_segmentation,
        test_mediastinal_exclusion,
        test_metabolic_radiomics,
        test_shape_radiomics,
        test_advanced_metrics,
        test_pipeline,
        test_empty_mask,
        test_getu_different_parameters
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
