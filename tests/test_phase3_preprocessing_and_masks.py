"""Automated test suite for Phase 3: Preprocessing, resizing, mask alignment, and PyTorch dataset loaders."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import torch
import pytest

ROOT = Path(__file__).resolve().parents[1]
from src.data.preprocessing import (
    scale_intensity,
    resize_and_pad,
    to_model_tensor,
    apply_mild_augmentation,
    preprocess_sample,
    IMAGENET_MEAN,
    IMAGENET_STD,
)
from src.data.cheng_dataset import ChengDataset
from src.data.brisc_dataset import BriscDataset


def test_scale_intensity_bounds() -> None:
    # Random normal values with positive and negative range
    arr = np.random.randn(100, 100) * 50.0 + 120.0
    scaled = scale_intensity(arr)
    assert scaled.min() >= 0.0
    assert scaled.max() <= 1.0
    assert scaled.dtype == np.float32

    # Constant array
    constant_arr = np.ones((50, 50), dtype=np.float32) * 42.0
    scaled_const = scale_intensity(constant_arr)
    assert np.all(scaled_const == 0.0)


def test_resize_and_pad_square() -> None:
    img = np.ones((512, 512), dtype=np.float32)
    mask = np.zeros((512, 512), dtype=np.uint8)
    mask[200:300, 200:300] = 1

    out_img, out_mask, meta = resize_and_pad(img, mask, target_size=(224, 224))
    assert out_img.shape == (224, 224)
    assert out_mask.shape == (224, 224)
    assert meta["scale_factor"] == pytest.approx(224.0 / 512.0)
    assert meta["pad_offsets"] == (0, 0, 0, 0)
    assert meta["is_binary"] is True
    assert not meta["mask_disappeared"]
    assert meta["resized_area_pixels"] > 0


def test_resize_and_pad_non_square() -> None:
    # Non-square input: 512 height x 256 width
    img = np.ones((512, 256), dtype=np.float32)
    mask = np.zeros((512, 256), dtype=np.uint8)
    mask[100:200, 50:150] = 1

    out_img, out_mask, meta = resize_and_pad(img, mask, target_size=(224, 224))
    assert out_img.shape == (224, 224)
    assert out_mask.shape == (224, 224)
    # Scale factor determined by max dimension (512 -> 224)
    assert meta["scale_factor"] == pytest.approx(224.0 / 512.0)
    # Scaled width = 256 * (224/512) = 112. Padding = 224 - 112 = 112 (56 left, 56 right)
    pad_top, pad_bottom, pad_left, pad_right = meta["pad_offsets"]
    assert pad_top == 0 and pad_bottom == 0
    assert pad_left == 56 and pad_right == 56


def test_mask_binary_invariance() -> None:
    mask = np.zeros((512, 512), dtype=np.uint8)
    mask[150:350, 150:350] = 1

    _, out_mask, meta = resize_and_pad(np.zeros((512, 512)), mask, target_size=(224, 224))
    unique_vals = set(np.unique(out_mask))
    assert unique_vals.issubset({0, 1})
    assert meta["is_binary"] is True


def test_to_model_tensor_normalization() -> None:
    # Uniform 0.5 image
    img = np.full((224, 224), 0.5, dtype=np.float32)
    tensor = to_model_tensor(img, normalize_imagenet=True)
    assert tensor.shape == (3, 224, 224)
    assert tensor.dtype == np.float32

    # Check Channel 0: (0.5 - 0.485) / 0.229
    expected_c0 = (0.5 - 0.485) / 0.229
    assert tensor[0, 0, 0] == pytest.approx(expected_c0, abs=1e-4)


def test_mild_augmentation_properties() -> None:
    img = np.random.uniform(0.1, 0.9, (224, 224)).astype(np.float32)
    mask = np.zeros((224, 224), dtype=np.uint8)
    mask[80:140, 80:140] = 1

    rng = np.random.default_rng(42)
    aug_img, aug_mask = apply_mild_augmentation(img, mask, rng=rng)

    assert aug_img.shape == (224, 224)
    assert aug_mask.shape == (224, 224)
    assert aug_img.min() >= 0.0 and aug_img.max() <= 1.0
    assert set(np.unique(aug_mask)).issubset({0, 1})


def test_preprocessing_determinism() -> None:
    raw_img = np.random.uniform(0, 1000, (512, 512)).astype(np.float32)
    raw_mask = np.zeros((512, 512), dtype=np.uint8)
    raw_mask[200:300, 200:300] = 1

    t1, m1, d1, meta1 = preprocess_sample(raw_img, raw_mask, is_training=False)
    t2, m2, d2, meta2 = preprocess_sample(raw_img, raw_mask, is_training=False)

    np.testing.assert_array_equal(t1, t2)
    np.testing.assert_array_equal(m1, m2)
    np.testing.assert_array_equal(d1, d2)
    assert meta1["resized_area_pixels"] == meta2["resized_area_pixels"]


def test_cheng_torch_dataset_loader() -> None:
    dataset = ChengDataset(split="fold_1")
    assert len(dataset) == 645

    sample = dataset[0]
    assert isinstance(sample["image"], torch.Tensor)
    assert sample["image"].shape == (3, 224, 224)
    assert sample["image"].dtype == torch.float32
    assert isinstance(sample["mask"], torch.Tensor)
    assert sample["mask"].shape == (224, 224)
    assert sample["label"] in {0, 1, 2}
    assert sample["class_label"] in {"glioma", "meningioma", "pituitary"}
    assert sample["patient_id"] != ""


def test_brisc_torch_dataset_loader() -> None:
    dataset = BriscDataset(split="test", clean_only=True)
    assert len(dataset) == 899

    sample = dataset[0]
    assert isinstance(sample["image"], torch.Tensor)
    assert sample["image"].shape == (3, 224, 224)
    assert sample["image"].dtype == torch.float32
    assert sample["label"] in {0, 1, 2, 3}
    assert sample["class_label"] in {"glioma", "meningioma", "pituitary", "no_tumor"}
    assert sample["plane"] in {"axial", "coronal", "sagittal"}

