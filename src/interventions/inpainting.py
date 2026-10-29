"""Counterfactual perturbation and filling engines for brain MRI intervention.

Implements two complementary methods specified in Part 8.2:
- Method A: Seamless local inpainting using Telea / Navier-Stokes (cv2.inpaint).
- Method B: Locally matched intensity and Gaussian texture fill with edge feathering.

Both methods enforce strict non-target pixel invariance:
    edited_image[mask == 0] == original_image[mask == 0]
"""
from __future__ import annotations

from typing import Literal
import cv2
import numpy as np


def inpaint_region_telea(
    image: np.ndarray,
    mask: np.ndarray,
    inpaint_radius: int = 3,
    method: Literal["telea", "ns"] = "telea",
) -> np.ndarray:
    """Method A: Inpaint targeted region from surrounding tissue using cv2.inpaint.

    Args:
        image: (H, W) float32 array in [0.0, 1.0].
        mask: (H, W) uint8 binary mask in {0, 1} designating intervention area.
        inpaint_radius: Neighborhood diameter for inpainting algorithm.
        method: 'telea' for Fast Marching Method or 'ns' for Navier-Stokes.
    Returns:
        (H, W) float32 array in [0.0, 1.0] with mask region inpainted and 
        all non-mask pixels bitwise/numerically identical to input.
    """
    if np.count_nonzero(mask) == 0:
        return image.copy()

    # Convert to 8-bit uint8 for OpenCV inpainting
    img_u8 = np.clip(image * 255.0, 0.0, 255.0).astype(np.uint8)
    mask_u8 = (mask > 0).astype(np.uint8) * 255

    flag = cv2.INPAINT_TELEA if method == "telea" else cv2.INPAINT_NS
    inpainted_u8 = cv2.inpaint(img_u8, mask_u8, inpaintRadius=inpaint_radius, flags=flag)

    inpainted_float = inpainted_u8.astype(np.float32) / 255.0

    # Strict pixel preservation outside mask
    result = image.copy()
    result[mask > 0] = inpainted_float[mask > 0]
    return np.clip(result, 0.0, 1.0)


def fill_region_matched_texture(
    image: np.ndarray,
    mask: np.ndarray,
    tissue_mask: np.ndarray | None = None,
    border_width: int = 5,
    feather_radius: int = 2,
    seed: int = 42,
) -> np.ndarray:
    """Method B: Fill targeted region with local surrounding mean and Gaussian texture.

    Args:
        image: (H, W) float32 array in [0.0, 1.0].
        mask: (H, W) uint8 binary mask in {0, 1} designating intervention area.
        tissue_mask: Optional intracranial tissue support mask to restrict surrounding sample.
        border_width: Width in pixels of surrounding ring used to estimate local statistics.
        feather_radius: Gaussian boundary smoothing radius to prevent high-frequency step edges.
        seed: Random seed for deterministic Gaussian noise.
    Returns:
        (H, W) float32 array in [0.0, 1.0] with mask region texture-filled and 
        all non-mask pixels bitwise/numerically identical to input.
    """
    if np.count_nonzero(mask) == 0:
        return image.copy()

    mask_bool = (mask > 0)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * border_width + 1, 2 * border_width + 1))
    dilated = cv2.dilate(mask.astype(np.uint8), kernel)
    surround = (dilated > 0) & (~mask_bool)

    if tissue_mask is not None:
        surround = surround & (tissue_mask > 0)

    # If surrounding tissue pixels exist, estimate mean and standard deviation
    if np.count_nonzero(surround) > 0:
        local_mean = float(np.mean(image[surround]))
        local_std = float(np.std(image[surround]))
        local_std = max(local_std, 1e-3)
    else:
        # Fallback to entire image tissue mean
        valid_pixels = image[tissue_mask > 0] if tissue_mask is not None else image[image > 0.05]
        local_mean = float(np.mean(valid_pixels)) if len(valid_pixels) > 0 else 0.5
        local_std = float(np.std(valid_pixels)) if len(valid_pixels) > 0 else 0.05

    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=local_mean, scale=local_std, size=image.shape).astype(np.float32)
    noise = np.clip(noise, 0.0, 1.0)

    # Optional feathering near boundary to avoid high-frequency cliff artifacts
    if feather_radius > 0:
        dist_in = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 3)
        # Weight ramps from 0.0 at boundary to 1.0 at feather_radius depth
        alpha = np.clip(dist_in / float(feather_radius), 0.0, 1.0)
        # Interpolate between local mean at boundary and noisy texture in core
        fill_val = (1.0 - alpha) * local_mean + alpha * noise
    else:
        fill_val = noise

    result = image.copy()
    result[mask_bool] = fill_val[mask_bool]
    return np.clip(result, 0.0, 1.0)

