"""Region taxonomy and extraction for brain MRI counterfactual interventions.

Defines non-overlapping regions according to Part 8.1:
- R_core: Ground-truth annotated tumor region M.
- R_immediate: 4-pixel morphological dilation ring outside core, restricted to tissue mask S.
- R_outer: 12-pixel morphological dilation ring (4 to 16 pixels), restricted to tissue mask S.
- R_remote: Contralateral or distance-isolated tissue region within S.
- R_sham: Area- and shape-matched control region in normal parenchyma with zero tumor overlap.
"""
from __future__ import annotations

from typing import Any, Tuple
import cv2
import numpy as np


def extract_tissue_mask(image: np.ndarray, min_intensity: float = 0.05) -> np.ndarray:
    """Extract brain tissue support mask S, excluding background air and padding.
    
    Args:
        image: (H, W) float32 array in [0.0, 1.0].
        min_intensity: Intensity threshold separating tissue from background air/padding.
    Returns:
        (H, W) uint8 binary mask where 1 indicates brain/head tissue parenchyma.
    """
    raw_mask = (image > min_intensity).astype(np.uint8)
    
    # Morphological closing to fill small ventricles / internal cavities
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    closed = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel)
    
    # Keep largest connected component (intracranial compartment)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(closed)
    if num_labels <= 1:
        return raw_mask
    
    # Background label is 0; find largest non-zero component
    largest_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    tissue_mask = (labels == largest_label).astype(np.uint8)
    
    # Fill any remaining holes inside the intracranial contour
    contours, _ = cv2.findContours(tissue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        cv2.drawContours(tissue_mask, contours, -1, color=1, thickness=-1)
        
    return tissue_mask


def generate_regions(
    tumor_mask: np.ndarray,
    image: np.ndarray,
    d1: int = 4,
    d2: int = 16,
) -> dict[str, np.ndarray]:
    """Construct mutually exclusive intervention regions for a given tumor mask.
    
    Args:
        tumor_mask: (H, W) binary uint8 mask {0, 1} for tumor core.
        image: (H, W) float32 array in [0.0, 1.0].
        d1: Radius for immediate margin (default 4 pixels).
        d2: Radius for outer margin (default 16 pixels).
    Returns:
        Dictionary mapping region name to (H, W) uint8 binary mask {0, 1}:
        - core: R_core
        - immediate: R_immediate
        - outer: R_outer
        - remote: R_remote
        - sham: R_sham (matched shape/area control)
        - tissue_mask: Brain parenchyma support S
    """
    h, w = tumor_mask.shape
    core = (tumor_mask > 0).astype(np.uint8)
    tissue = extract_tissue_mask(image)
    
    # 1. Immediate margin: Dilate by d1, subtract core, intersect with tissue
    k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * d1 + 1, 2 * d1 + 1))
    dilated_1 = cv2.dilate(core, k1)
    immediate = ((dilated_1 == 1) & (core == 0) & (tissue == 1)).astype(np.uint8)
    
    # 2. Outer margin: Dilate by d2, subtract dilated_1, intersect with tissue
    k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * d2 + 1, 2 * d2 + 1))
    dilated_2 = cv2.dilate(core, k2)
    outer = ((dilated_2 == 1) & (dilated_1 == 0) & (tissue == 1)).astype(np.uint8)
    
    # Exclusion zone: core + immediate + outer
    exclusion = (dilated_2 == 1) | (core == 1)
    
    # 3. Sham control: Mirror core across vertical midline (contralateral hemisphere)
    sham_candidate = np.fliplr(core)
    
    # If sham candidate overlaps exclusion zone or falls outside tissue, find best fit translation
    overlap = np.count_nonzero((sham_candidate == 1) & (exclusion == 1))
    outside_tissue = np.count_nonzero((sham_candidate == 1) & (tissue == 0))
    core_area = int(np.count_nonzero(core))
    
    sham = np.zeros_like(core)
    if core_area > 0:
        if overlap == 0 and outside_tissue < 0.2 * core_area:
            sham = (sham_candidate == 1) & (tissue == 1)
            sham = sham.astype(np.uint8)
        else:
            # Search for best vertical / horizontal shift that minimizes overlap and maximizes tissue overlap
            best_score = -float("inf")
            best_shifted = None
            
            # Compute centroid of core
            M = cv2.moments(core)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                target_cx = w - 1 - cx
                target_cy = cy
            else:
                target_cx, target_cy = w // 2, h // 2
                
            # Scan candidate shifts
            for dy in range(-h // 3, h // 3, 4):
                for dx in range(-w // 4, w // 4, 4):
                    trans_mat = np.float32([[1, 0, dx], [0, 1, dy]])
                    shifted = cv2.warpAffine(sham_candidate, trans_mat, (w, h), flags=cv2.INTER_NEAREST)
                    curr_overlap = np.count_nonzero((shifted == 1) & (exclusion == 1))
                    curr_in_tissue = np.count_nonzero((shifted == 1) & (tissue == 1))
                    
                    if curr_overlap == 0:
                        score = curr_in_tissue
                        if score > best_score:
                            best_score = score
                            best_shifted = (shifted == 1) & (tissue == 1)
                            
            if best_shifted is not None and best_score > 0.5 * core_area:
                sham = best_shifted.astype(np.uint8)
            else:
                # Fallback: Area-matched circular patch in free tissue space furthest from tumor
                dist_map = cv2.distanceTransform((exclusion == 0).astype(np.uint8) * tissue, cv2.DIST_L2, 5)
                _, max_val, _, max_loc = cv2.minMaxLoc(dist_map)
                radius = int(np.sqrt(core_area / np.pi)) if core_area > 0 else 5
                radius = max(3, min(radius, int(max_val) - 1 if max_val > 4 else 3))
                sham = np.zeros_like(core)
                cv2.circle(sham, max_loc, radius, color=1, thickness=-1)
                sham = ((sham == 1) & (exclusion == 0) & (tissue == 1)).astype(np.uint8)
                
    # 4. Remote context: Patch distant from tumor (> d2 away) in tissue
    dist_from_tumor = cv2.distanceTransform((core == 0).astype(np.uint8), cv2.DIST_L2, 5)
    valid_remote_tissue = ((dist_from_tumor > (2 * d2)) & (tissue == 1) & (sham == 0)).astype(np.uint8)
    
    remote_area = int(np.count_nonzero(valid_remote_tissue))
    remote = np.zeros_like(core)
    if remote_area > 0:
        # Place patch of same radius as sham at highest distance point in contralateral hemisphere
        _, _, _, max_remote_loc = cv2.minMaxLoc(dist_from_tumor * valid_remote_tissue)
        rem_radius = max(4, int(np.sqrt(core_area / np.pi))) if core_area > 0 else 6
        cv2.circle(remote, max_remote_loc, rem_radius, color=1, thickness=-1)
        remote = ((remote == 1) & (valid_remote_tissue == 1)).astype(np.uint8)
        
    # Strictly enforce zero overlap guarantees
    assert np.count_nonzero(core & immediate) == 0, "Core and immediate margin overlap"
    assert np.count_nonzero(core & outer) == 0, "Core and outer margin overlap"
    assert np.count_nonzero(immediate & outer) == 0, "Immediate and outer margin overlap"
    assert np.count_nonzero(core & sham) == 0, "Core and sham control overlap"
    assert np.count_nonzero(immediate & sham) == 0, "Immediate margin and sham control overlap"
    assert np.count_nonzero(outer & sham) == 0, "Outer margin and sham control overlap"

    return {
        "core": core,
        "immediate": immediate,
        "outer": outer,
        "remote": remote,
        "sham": sham,
        "tissue_mask": tissue,
    }

