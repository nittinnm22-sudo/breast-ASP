#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced PET radiomics metrics for breast tumor analysis.
Computes MTV, TLG, SUVpeak, Dmax, NHOCmax, NHOPmax, gETU.
"""

import numpy as np
from scipy.spatial.distance import cdist
from scipy import ndimage as ndi


def compute_advanced_metrics(pet_array, tumor_mask, affine, getu_a_values=None):
    if getu_a_values is None:
        getu_a_values = [0.25, 0.5, 1.0, 2.0, 4.0]

    results = {}
    mask = tumor_mask.astype(bool)
    n_voxels = int(mask.sum())

    if n_voxels == 0:
        results["mtv_ml"] = 0.0
        results["tlg"] = 0.0
        results["suv_mean"] = 0.0
        results["suv_peak"] = 0.0
        results["dmax_mm"] = 0.0
        results["nhoc_max"] = 0.0
        results["nhop_max"] = 0.0
        for a in getu_a_values:
            results["getu_a{:.2f}".format(a)] = 0.0
        return results

    voxel_sizes = np.sqrt(np.sum(affine[:3, :3] ** 2, axis=0))
    voxel_vol_mm3 = float(np.prod(voxel_sizes))
    voxel_vol_ml = voxel_vol_mm3 / 1000.0

    suv_values = pet_array[mask]

    mtv_ml = n_voxels * voxel_vol_ml
    results["mtv_ml"] = float(mtv_ml)

    suv_mean = float(np.mean(suv_values))
    results["suv_mean"] = suv_mean

    tlg = suv_mean * mtv_ml
    results["tlg"] = float(tlg)

    suv_max_val = float(np.max(suv_values))
    results["suv_max"] = suv_max_val

    max_idx = np.unravel_index(
        np.argmax(pet_array * mask.astype(float)), pet_array.shape
    )
    max_ijk = np.array(max_idx, dtype=float)
    max_xyz = affine[:3, :3].dot(max_ijk) + affine[:3, 3]

    suv_peak = _compute_suv_peak(pet_array, mask, max_ijk, voxel_sizes, voxel_vol_ml)
    results["suv_peak"] = float(suv_peak)

    tumor_ijk = np.array(np.where(mask)).T
    tumor_xyz = (affine[:3, :3].dot(tumor_ijk.T) + affine[:3, 3:4]).T

    centroid_xyz = np.mean(tumor_xyz, axis=0)

    volume_mm3 = n_voxels * voxel_vol_mm3
    R_eq = (3.0 * volume_mm3 / (4.0 * np.pi)) ** (1.0 / 3.0)
    results["equivalent_sphere_radius_mm"] = float(R_eq)

    eroded = ndi.binary_erosion(mask, structure=ndi.generate_binary_structure(3, 1))
    surface_mask = mask & ~eroded
    surface_ijk = np.array(np.where(surface_mask)).T
    surface_xyz = (affine[:3, :3].dot(surface_ijk.T) + affine[:3, 3:4]).T

    n_surface = surface_xyz.shape[0]

    if n_surface > 1:
        dmax = _compute_dmax(surface_xyz)
    else:
        dmax = 0.0
    results["dmax_mm"] = float(dmax)

    if R_eq > 0:
        dist_to_centroid = np.linalg.norm(max_xyz - centroid_xyz)
        nhoc_max = dist_to_centroid / R_eq
    else:
        nhoc_max = 0.0
    results["nhoc_max"] = float(nhoc_max)

    if n_surface > 0 and R_eq > 0:
        dists_to_surface = np.linalg.norm(surface_xyz - max_xyz[np.newaxis, :], axis=1)
        min_dist_to_surface = float(np.min(dists_to_surface))
        nhop_max = min_dist_to_surface / R_eq
    else:
        nhop_max = 0.0
    results["nhop_max"] = float(nhop_max)

    for a in getu_a_values:
        getu = _compute_getu(suv_values, voxel_vol_ml, a)
        results["getu_a{:.2f}".format(a)] = float(getu)

    return results


def _compute_suv_peak(pet_array, mask, max_ijk, voxel_sizes, voxel_vol_ml):
    radius_mm = (3.0 * 1000.0 / (4.0 * np.pi)) ** (1.0 / 3.0)

    radius_vox = np.ceil(radius_mm / voxel_sizes).astype(int) + 1

    shape = pet_array.shape
    ci = int(round(max_ijk[0]))
    cj = int(round(max_ijk[1]))
    ck = int(round(max_ijk[2]))

    imin = max(0, ci - radius_vox[0])
    imax = min(shape[0], ci + radius_vox[0] + 1)
    jmin = max(0, cj - radius_vox[1])
    jmax = min(shape[1], cj + radius_vox[1] + 1)
    kmin = max(0, ck - radius_vox[2])
    kmax = min(shape[2], ck + radius_vox[2] + 1)

    ii, jj, kk = np.mgrid[imin:imax, jmin:jmax, kmin:kmax]
    di = (ii - max_ijk[0]) * voxel_sizes[0]
    dj = (jj - max_ijk[1]) * voxel_sizes[1]
    dk = (kk - max_ijk[2]) * voxel_sizes[2]
    dist = np.sqrt(di**2 + dj**2 + dk**2)

    sphere_mask = dist <= radius_mm
    tumor_sub = mask[imin:imax, jmin:jmax, kmin:kmax]
    valid = sphere_mask & tumor_sub

    if valid.sum() == 0:
        return float(pet_array[ci, cj, ck])

    return float(np.mean(pet_array[imin:imax, jmin:jmax, kmin:kmax][valid]))


def _compute_dmax(surface_xyz):
    n = surface_xyz.shape[0]

    if n <= 5000:
        dists = cdist(surface_xyz, surface_xyz)
        return float(np.max(dists))
    else:
        try:
            from scipy.spatial import ConvexHull
            hull = ConvexHull(surface_xyz)
            hull_pts = surface_xyz[hull.vertices]
            dists = cdist(hull_pts, hull_pts)
            return float(np.max(dists))
        except Exception:
            idx = np.random.choice(n, min(5000, n), replace=False)
            sub = surface_xyz[idx]
            dists = cdist(sub, sub)
            return float(np.max(dists))


def _compute_getu(suv_values, voxel_vol_ml, a):
    valid = suv_values[suv_values > 0]
    if len(valid) == 0:
        return 0.0

    dv = voxel_vol_ml

    if a == 0:
        return float(len(valid) * dv)

    log_ui_a = a * np.log(valid)
    max_log = np.max(log_ui_a)
    log_sum = max_log + np.log(np.sum(np.exp(log_ui_a - max_log)))
    log_dv_sum = np.log(dv) + log_sum
    getu = np.exp(log_dv_sum / a)

    return float(getu)
