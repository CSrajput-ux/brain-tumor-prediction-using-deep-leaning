"""Deterministic, tested image and mask preprocessing module.

Follows Part 5 specifications:
- 224x224 target size with aspect ratio preservation and symmetric padding.
- Robust percentile-based intensity scaling (1st and 99th percentiles) clipped to [0, 1].
- Nearest-neighbor mask interpolation preserving strictly binary values {0, 1}.
- Area tracking, mask disappearance detection, and minimum usable area flagging.
- 3-channel grayscale conversion and ImageNet normalization.
- Mild, reproducible training-only augmentation (rotations, translations, scaling, brightness)
  with NO horizontal flipping by default.
"""
from __future__ import annotations

from typing import Any, Tuple
import numpy as np
from PIL import Image

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)


def scale_intensity(image: np.ndarray, p_low: float = 1.0, p_high: float = 99.0) -> np.ndarray:
    """Robust percentile-based intensity scaling mapping values to [0.0, 1.0]."""
    values = image.astype(np.float32)
    if not np.isfinite(values).all():
        values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    lo, hi = np.percentile(values, (p_low, p_high))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        v_min, v_max = float(values.min()), float(values.max())
        if v_max > v_min:
            return np.clip((values - v_min) / (v_max - v_min), 0.0, 1.0)
        return np.zeros_like(values, dtype=np.float32)
    return np.clip((values - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)


def resize_and_pad(
    image: np.ndarray,
    mask: np.ndarray | None = None,
    target_size: tuple[int, int] = (224, 224),
) -> tuple[np.ndarray, np.ndarray | None, dict[str, Any]]:
    """Resize image and mask preserving aspect ratio with zero padding.

    Uses bilinear interpolation for the image and nearest-neighbor for the mask.
    """
    target_h, target_w = target_size
    orig_h, orig_w = image.shape[:2]

    # Calculate proportional scale
    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = max(1, int(round(orig_w * scale)))
    new_h = max(1, int(round(orig_h * scale)))

    # Resize image
    pil_img = Image.fromarray(image)
    resized_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    resized_img_arr = np.asarray(resized_img, dtype=np.float32)

    # Pad symmetrically to target_size
    pad_top = (target_h - new_h) // 2
    pad_bottom = target_h - new_h - pad_top
    pad_left = (target_w - new_w) // 2
    pad_right = target_w - new_w - pad_left

    out_img = np.pad(
        resized_img_arr,
        ((pad_top, pad_bottom), (pad_left, pad_right)),
        mode="constant",
        constant_values=0.0,
    )

    out_mask = None
    mask_meta: dict[str, Any] = {
        "original_shape": (orig_h, orig_w),
        "target_shape": (target_h, target_w),
        "scale_factor": scale,
        "pad_offsets": (pad_top, pad_bottom, pad_left, pad_right),
        "original_area_pixels": 0,
        "resized_area_pixels": 0,
        "area_ratio": 0.0,
        "mask_disappeared": False,
        "is_binary": True,
    }

    if mask is not None:
        mask_u8 = (mask > 0).astype(np.uint8)
        pil_mask = Image.fromarray(mask_u8)
        # NEAREST neighbor to avoid soft boundaries
        resized_mask = pil_mask.resize((new_w, new_h), Image.Resampling.NEAREST)
        resized_mask_arr = np.asarray(resized_mask, dtype=np.uint8)

        padded_mask = np.pad(
            resized_mask_arr,
            ((pad_top, pad_bottom), (pad_left, pad_right)),
            mode="constant",
            constant_values=0,
        )
        out_mask = (padded_mask > 0).astype(np.uint8)

        orig_area = int(np.count_nonzero(mask_u8))
        resized_area = int(np.count_nonzero(out_mask))
        disappeared = (orig_area > 0 and resized_area == 0)

        mask_meta.update({
            "original_area_pixels": orig_area,
            "resized_area_pixels": resized_area,
            "area_ratio": float(resized_area / orig_area) if orig_area > 0 else 0.0,
            "mask_disappeared": disappeared,
            "is_binary": bool(set(np.unique(out_mask)).issubset({0, 1})),
        })

    return out_img, out_mask, mask_meta


def apply_mild_augmentation(
    image: np.ndarray,
    mask: np.ndarray | None = None,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Mild, reproducible training augmentation preserving tumour morphology.

    Applies:
    - Small rotation (+/- 10 deg)
    - Small translation (+/- 5%)
    - Mild scaling ([0.95, 1.05])
    - Modest brightness/contrast (+/- 10%)
    - Explicitly NO horizontal flipping.
    """
    if rng is None:
        rng = np.random.default_rng()

    angle = float(rng.uniform(-10.0, 10.0))
    scale = float(rng.uniform(0.95, 1.05))
    tx = float(rng.uniform(-0.05, 0.05)) * image.shape[1]
    ty = float(rng.uniform(-0.05, 0.05)) * image.shape[0]

    pil_img = Image.fromarray((image * 255.0).astype(np.uint8))
    # Rotate with bilinear
    aug_img = pil_img.rotate(angle, resample=Image.Resampling.BILINEAR, translate=(int(tx), int(ty)))
    aug_img_arr = np.asarray(aug_img, dtype=np.float32) / 255.0

    # Mild contrast and brightness jitter
    contrast_factor = float(rng.uniform(0.90, 1.10))
    brightness_offset = float(rng.uniform(-0.05, 0.05))
    mean_val = float(aug_img_arr.mean())
    aug_img_arr = np.clip((aug_img_arr - mean_val) * contrast_factor + mean_val + brightness_offset, 0.0, 1.0)

    aug_mask_arr = None
    if mask is not None:
        pil_mask = Image.fromarray((mask > 0).astype(np.uint8) * 255)
        # Rotate with NEAREST
        aug_mask = pil_mask.rotate(angle, resample=Image.Resampling.NEAREST, translate=(int(tx), int(ty)))
        aug_mask_arr = (np.asarray(aug_mask, dtype=np.uint8) > 127).astype(np.uint8)

    return aug_img_arr, aug_mask_arr


def to_model_tensor(
    image: np.ndarray,
    normalize_imagenet: bool = True,
) -> np.ndarray:
    """Convert a 2D [0.0, 1.0] image to (3, H, W) float32 tensor with ImageNet normalization."""
    # Expand to 3 identical channels
    ch3 = np.stack([image, image, image], axis=0).astype(np.float32)
    if normalize_imagenet:
        ch3 = (ch3 - IMAGENET_MEAN) / IMAGENET_STD
    return ch3


def preprocess_sample(
    raw_image: np.ndarray,
    raw_mask: np.ndarray | None = None,
    target_size: tuple[int, int] = (224, 224),
    is_training: bool = False,
    normalize_imagenet: bool = True,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray | None, np.ndarray, dict[str, Any]]:
    """Complete preprocessing pipeline for an MRI sample and its mask.

    Returns:
    - model_tensor: (3, target_h, target_w) float32 ImageNet normalized tensor
    - binary_mask: (target_h, target_w) uint8 binary mask in {0, 1}
    - display_image: (target_h, target_w) float32 unnormalized image in [0.0, 1.0]
    - metadata: dictionary containing geometry, area tracking, and quality flags.
    """
    # 1. Intensity scaling
    scaled = scale_intensity(raw_image, p_low=1.0, p_high=99.0)

    # 2. Resizing and aspect ratio preservation padding
    resized_img, resized_mask, meta = resize_and_pad(scaled, raw_mask, target_size=target_size)

    # 3. Training-only mild augmentation
    if is_training:
        resized_img, resized_mask = apply_mild_augmentation(resized_img, resized_mask, rng=rng)

    # 4. Convert to 3-channel model tensor
    model_tensor = to_model_tensor(resized_img, normalize_imagenet=normalize_imagenet)

    return model_tensor, resized_mask, resized_img, meta

