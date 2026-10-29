"""Automated test suite for Phase 4: Model architectures, gradients, checkpointing, and calibration."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
from src.models import (
    build_model,
    compute_calibration_metrics,
    compute_classification_metrics,
    load_checkpoint,
    save_checkpoint,
)


def test_resnet50_shapes() -> None:
    # 3 classes (Cheng)
    m3 = build_model("resnet50", num_classes=3, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    out3 = m3(x)
    assert out3.shape == (2, 3)

    feat = m3.forward_features(x)
    assert feat.shape == (2, 2048)

    # 4 classes (BRISC)
    m4 = build_model("resnet50", num_classes=4, pretrained=False)
    out4 = m4(x)
    assert out4.shape == (2, 4)


def test_deit_small_shapes() -> None:
    # 3 classes (Cheng)
    m3 = build_model("deit_small_patch16_224", num_classes=3, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    out3 = m3(x)
    assert out3.shape == (2, 3)

    feat = m3.forward_features(x)
    # in timm, forward_features for ViT returns (B, num_tokens, 384) or (B, 384)
    assert feat.shape[0] == 2
    assert feat.shape[-1] == 384

    # 4 classes (BRISC)
    m4 = build_model("deit_small_patch16_224", num_classes=4, pretrained=False)
    out4 = m4(x)
    assert out4.shape == (2, 4)


def test_model_gradients_flow() -> None:
    model = build_model("resnet50", num_classes=3, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    y = torch.tensor([0, 1])

    criterion = nn.CrossEntropyLoss()
    logits = model(x)
    loss = criterion(logits, y)
    loss.backward()

    # Check that classifier head parameters have non-zero gradients
    fc_weights = model.backbone.fc[1].weight if isinstance(model.backbone.fc, nn.Sequential) else model.backbone.fc.weight
    assert fc_weights.grad is not None
    assert fc_weights.grad.norm().item() > 0.0


def test_checkpoint_roundtrip(tmp_path: Path) -> None:
    model = build_model("resnet50", num_classes=3, pretrained=False)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
    model.eval()
    x = torch.randn(2, 3, 224, 224)

    with torch.no_grad():
        orig_logits = model(x).clone()

    ckpt_file = tmp_path / "model.pt"
    save_checkpoint(ckpt_file, model, opt, epoch=1, metrics={"acc": 0.95}, config={"name": "test"})

    model_reloaded = build_model("resnet50", num_classes=3, pretrained=False)
    loaded_data = load_checkpoint(ckpt_file, model_reloaded)
    model_reloaded.eval()

    with torch.no_grad():
        reloaded_logits = model_reloaded(x)

    torch.testing.assert_close(orig_logits, reloaded_logits)
    assert loaded_data["epoch"] == 1
    assert loaded_data["metrics"]["acc"] == 0.95


def test_calibration_and_classification_metrics() -> None:
    # 4 samples, 3 classes
    targets = np.array([0, 1, 2, 0])
    probs = np.array([
        [0.8, 0.1, 0.1],
        [0.2, 0.7, 0.1],
        [0.1, 0.1, 0.8],
        [0.4, 0.5, 0.1],  # Error: predicted 1 instead of 0
    ])
    preds = np.argmax(probs, axis=1)

    metrics = compute_classification_metrics(targets, preds, probs, class_names=["glioma", "meningioma", "pituitary"])
    assert metrics["accuracy"] == 0.75
    assert 0.0 <= metrics["expected_calibration_error"] <= 1.0
    assert metrics["brier_score"] >= 0.0
    assert len(metrics["precision_per_class"]) == 3
    assert len(metrics["confusion_matrix"]) == 3
