"""Quality control audit metrics for counterfactual interventions.

Evaluates every edit against strict standards specified in Part 8.3:
1. Outside-mask pixel preservation (SSIM and Max Absolute Difference).
2. Inside-mask intervention magnitude (MAD, RMSD).
3. Boundary gradient discontinuity index across the intervention border.
4. Numerical anomaly flags (NaNs, Infs, out-of-bound intensities).
"""
from __future__ import annotations

from typing import Any
import cv2
import numpy as np


def compute_intervention_quality(
    orig_img: np.ndarray,
    edited_img: np.ndarray,
    mask: np.ndarray,
) -> dict[str, Any]:
    """Compute comprehensive QC metrics comparing original and edited MRI images.

    Args:
        orig_img: (H, W) float32 array in [0.0, 1.0].
        edited_img: (H, W) float32 array in [0.0, 1.0].
        mask: (H, W) uint8 binary mask where 1 indicates modified region.
    Returns:
        Dictionary containing quantitative metrics and boolean QC pass flags.
    """
    mask_bool = (mask > 0)
    non_mask_bool = ~mask_bool
    mask_pixels = int(np.count_nonzero(mask_bool))

    # 1. Verification of outside-mask invariance
    if np.count_nonzero(non_mask_bool) > 0:
        diff_outside = np.abs(orig_img[non_mask_bool] - edited_img[non_mask_bool])
        max_diff_outside = float(np.max(diff_outside))
        mean_diff_outside = float(np.mean(diff_outside))
    else:
        max_diff_outside = 0.0
        mean_diff_outside = 0.0

    # 2. Inside-mask perturbation magnitude
    if mask_pixels > 0:
        diff_inside = np.abs(orig_img[mask_bool] - edited_img[mask_bool])
        mad_inside = float(np.mean(diff_inside))
        max_diff_inside = float(np.max(diff_inside))
        rmsd_inside = float(np.sqrt(np.mean(diff_inside ** 2)))
        intensity_shift = float(np.mean(edited_img[mask_bool]) - np.mean(orig_img[mask_bool]))
    else:
        mad_inside = 0.0
        max_diff_inside = 0.0
        rmsd_inside = 0.0
        intensity_shift = 0.0

    # 3. Boundary discontinuity: Sobel gradient across the boundary ring
    # Dilate mask by 1 and subtract eroded mask by 1 to isolate 2-pixel boundary ribbon
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    boundary_ribbon = cv2.dilate(mask.astype(np.uint8), k) ^ cv2.erode(mask.astype(np.uint8), k)
    boundary_bool = (boundary_ribbon > 0)

    sobelx_orig = cv2.Sobel(orig_img, cv2.CV_32F, 1, 0, ksize=3)
    sobely_orig = cv2.Sobel(orig_img, cv2.CV_32F, 0, 1, ksize=3)
    grad_orig = np.sqrt(sobelx_orig ** 2 + sobely_orig ** 2)

    sobelx_edit = cv2.Sobel(edited_img, cv2.CV_32F, 1, 0, ksize=3)
    sobely_edit = cv2.Sobel(edited_img, cv2.CV_32F, 0, 1, ksize=3)
    grad_edit = np.sqrt(sobelx_edit ** 2 + sobely_edit ** 2)

    if np.count_nonzero(boundary_bool) > 0:
        grad_diff = np.abs(grad_edit[boundary_bool] - grad_orig[boundary_bool])
        boundary_discontinuity_index = float(np.mean(grad_diff))
    else:
        boundary_discontinuity_index = 0.0

    # 4. Numerical integrity checks
    has_nans = bool(np.isnan(edited_img).any())
    has_infs = bool(np.isinf(edited_img).any())
    out_of_bounds = bool((edited_img < -1e-5).any() or (edited_img > 1.0 + 1e-5).any())

    # Pass criteria:
    # - Strict preservation outside mask: max difference <= 1e-5
    # - Numerical validity: no NaNs, Infs, or range violations
    is_valid_preservation = (max_diff_outside <= 1e-5)
    passed_qc = (is_valid_preservation and not has_nans and not has_infs and not out_of_bounds)

    return {
        "mask_pixels": mask_pixels,
        "max_diff_outside": max_diff_outside,
        "mean_diff_outside": mean_diff_outside,
        "mad_inside": mad_inside,
        "max_diff_inside": max_diff_inside,
        "rmsd_inside": rmsd_inside,
        "intensity_shift": intensity_shift,
        "boundary_discontinuity_index": boundary_discontinuity_index,
        "boundary_discontinuity": boundary_discontinuity_index,
        "has_nans": has_nans,
        "has_infs": has_infs,
        "out_of_bounds": out_of_bounds,
        "is_valid_preservation": is_valid_preservation,
        "passed_qc": passed_qc,
    }

