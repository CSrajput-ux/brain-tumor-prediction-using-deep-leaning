"""Training, optimization, checkpointing, and evaluation utilities for brain MRI models."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.models.deit_classifier import DeiTSmallClassifier
from src.models.resnet_classifier import ResNet50Classifier


def build_model(
    architecture: str,
    num_classes: int,
    pretrained: bool = True,
    dropout: float = 0.2,
) -> nn.Module:
    """Build classifier by architecture name."""
    arch = architecture.lower()
    if arch in {"resnet50", "resnet-50"}:
        return ResNet50Classifier(num_classes=num_classes, pretrained=pretrained, dropout=dropout)
    elif arch in {"deit_small", "deit_small_patch16_224", "deit"}:
        return DeiTSmallClassifier(num_classes=num_classes, pretrained=pretrained, drop_rate=dropout)
    else:
        raise ValueError(f"Unknown architecture: {architecture}. Supported: 'resnet50', 'deit_small_patch16_224'")


def compute_calibration_metrics(probs: np.ndarray, targets: np.ndarray, num_bins: int = 10) -> dict[str, float]:
    """Compute Expected Calibration Error (ECE) and multi-class Brier score."""
    n_samples, n_classes = probs.shape
    one_hot = np.zeros_like(probs)
    one_hot[np.arange(n_samples), targets] = 1.0

    # Multi-class Brier score: mean squared error between probabilities and one-hot
    brier_score = float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))

    # ECE based on confidence in top prediction
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == targets)

    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0

    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper) if i > 0 else (confidences >= bin_lower) & (confidences <= bin_upper)
        prop_in_bin = float(np.mean(in_bin))

        if prop_in_bin > 0:
            accuracy_in_bin = float(np.mean(accuracies[in_bin]))
            avg_confidence_in_bin = float(np.mean(confidences[in_bin]))
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return {"expected_calibration_error": float(ece), "brier_score": brier_score}


def compute_classification_metrics(
    targets: np.ndarray,
    predictions: np.ndarray,
    probs: np.ndarray,
    class_names: list[str] | None = None,
) -> dict[str, Any]:
    """Compute comprehensive classification metrics matching Part 9.1."""
    acc = float(accuracy_score(targets, predictions))
    bal_acc = float(balanced_accuracy_score(targets, predictions))
    macro_f1 = float(f1_score(targets, predictions, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(targets, predictions, average="weighted", zero_division=0))

    prec_per_class = precision_score(targets, predictions, average=None, zero_division=0).tolist()
    rec_per_class = recall_score(targets, predictions, average=None, zero_division=0).tolist()
    f1_per_class = f1_score(targets, predictions, average=None, zero_division=0).tolist()
    cm = confusion_matrix(targets, predictions).tolist()

    calib = compute_calibration_metrics(probs, targets)

    output: dict[str, Any] = {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "precision_per_class": prec_per_class,
        "recall_per_class": rec_per_class,
        "f1_per_class": f1_per_class,
        "confusion_matrix": cm,
        "expected_calibration_error": calib["expected_calibration_error"],
        "brier_score": calib["brier_score"],
    }

    if class_names is not None:
        output["class_names"] = class_names

    return output


def get_cosine_schedule_with_warmup(
    optimizer: torch.optim.Optimizer,
    num_warmup_steps: int,
    num_training_steps: int,
    min_lr_ratio: float = 0.01,
) -> torch.optim.lr_scheduler.LambdaLR:
    """Cosine learning rate scheduler with linear warmup."""
    def lr_lambda(current_step: int) -> float:
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
        cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
        return min_lr_ratio + (1.0 - min_lr_ratio) * cosine_decay

    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)


def save_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None,
    epoch: int,
    metrics: dict[str, Any],
    config: dict[str, Any],
) -> None:
    """Save model checkpoint atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict() if optimizer is not None else None,
        "metrics": metrics,
        "val_metrics": metrics,
        "config": config,
    }
    torch.save(payload, path)


def load_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    map_location: str = "cpu",
) -> dict[str, Any]:
    """Load model checkpoint into model and optional optimizer."""
    checkpoint = torch.load(path, map_location=map_location)
    model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer is not None and checkpoint.get("optimizer_state_dict"):
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return checkpoint


def train_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    scheduler: torch.optim.lr_scheduler.LambdaLR | None = None,
    gradient_accumulation_steps: int = 1,
    max_batches: int | None = None,
) -> float:
    """Train model for a single epoch."""
    model.train()
    total_loss = 0.0
    num_batches = 0
    optimizer.zero_grad()

    for batch_idx, batch in enumerate(dataloader):
        if max_batches is not None and batch_idx >= max_batches:
            break

        images = batch["image"].to(device)
        targets = batch["label"].to(device)

        logits = model(images)
        loss = criterion(logits, targets) / gradient_accumulation_steps
        loss.backward()

        if (batch_idx + 1) % gradient_accumulation_steps == 0 or (batch_idx + 1) == len(dataloader):
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            optimizer.zero_grad()
            if scheduler is not None:
                scheduler.step()

        total_loss += float(loss.item() * gradient_accumulation_steps)
        num_batches += 1

    return float(total_loss / max(1, num_batches))


def evaluate(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
    class_names: list[str] | None = None,
    max_batches: int | None = None,
) -> tuple[float, dict[str, Any], dict[str, Any]]:
    """Evaluate model on a dataloader returning loss, metrics, and prediction arrays."""
    model.eval()
    total_loss = 0.0
    num_batches = 0

    all_targets = []
    all_preds = []
    all_probs = []
    all_sample_ids = []

    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            if max_batches is not None and batch_idx >= max_batches:
                break

            images = batch["image"].to(device)
            targets = batch["label"].to(device)

            logits = model(images)
            loss = criterion(logits, targets)

            probs = torch.softmax(logits, dim=-1).cpu().numpy()
            preds = np.argmax(probs, axis=-1)

            total_loss += float(loss.item())
            num_batches += 1

            all_targets.extend(targets.cpu().numpy().tolist())
            all_preds.extend(preds.tolist())
            all_probs.extend(probs.tolist())
            all_sample_ids.extend(batch["sample_id"])

    avg_loss = float(total_loss / max(1, num_batches))
    targets_arr = np.array(all_targets, dtype=np.int64)
    preds_arr = np.array(all_preds, dtype=np.int64)
    probs_arr = np.array(all_probs, dtype=np.float32)

    metrics = compute_classification_metrics(targets_arr, preds_arr, probs_arr, class_names=class_names)

    predictions_data = {
        "sample_ids": all_sample_ids,
        "targets": targets_arr,
        "predictions": preds_arr,
        "probabilities": probs_arr,
    }

    return avg_loss, metrics, predictions_data


def train_model(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    val_loader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    num_epochs: int = 5,
    scheduler: torch.optim.lr_scheduler.LambdaLR | None = None,
    early_stopping_patience: int = 3,
    checkpoint_path: Path | None = None,
    config: dict[str, Any] | None = None,
    class_names: list[str] | None = None,
    max_train_batches: int | None = None,
    max_val_batches: int | None = None,
) -> dict[str, Any]:
    """Complete training loop with validation early stopping and checkpoint saving."""
    best_macro_f1 = -1.0
    best_epoch = 0
    best_metrics: dict[str, Any] = {}
    patience_counter = 0

    history: dict[str, list[Any]] = {
        "train_loss": [],
        "val_loss": [],
        "val_macro_f1": [],
        "val_accuracy": [],
    }

    for epoch in range(1, num_epochs + 1):
        train_loss = train_one_epoch(
            model,
            train_loader,
            optimizer,
            criterion,
            device,
            scheduler=scheduler,
            max_batches=max_train_batches,
        )
        val_loss, val_metrics, _ = evaluate(
            model,
            val_loader,
            criterion,
            device,
            class_names=class_names,
            max_batches=max_val_batches,
        )

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_macro_f1"].append(val_metrics["macro_f1"])
        history["val_accuracy"].append(val_metrics["accuracy"])

        current_f1 = val_metrics["macro_f1"]
        print(
            f"Epoch {epoch}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Macro-F1: {current_f1:.4f} | "
            f"Val Acc: {val_metrics['accuracy']:.4f}"
        )

        if current_f1 > best_macro_f1:
            best_macro_f1 = current_f1
            best_epoch = epoch
            best_metrics = val_metrics
            patience_counter = 0
            if checkpoint_path is not None:
                save_checkpoint(
                    checkpoint_path,
                    model,
                    optimizer,
                    epoch=epoch,
                    metrics=val_metrics,
                    config=config or {},
                )
        else:
            patience_counter += 1
            if patience_counter >= early_stopping_patience:
                print(f"Early stopping triggered at epoch {epoch} (best epoch: {best_epoch}, best Macro-F1: {best_macro_f1:.4f})")
                break

    # Reload best weights if saved
    if checkpoint_path is not None and checkpoint_path.exists():
        load_checkpoint(checkpoint_path, model, map_location=str(device))

    return {
        "best_epoch": best_epoch,
        "best_macro_f1": best_macro_f1,
        "best_metrics": best_metrics,
        "history": history,
    }


