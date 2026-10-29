"""Primary counterfactual audit metrics and sensitivity estimands.

Complies with Part 9:
- Computes baseline model predictions and probabilities.
- Computes counterfactual prediction vectors across region edits.
- Calculates raw sensitivity: Delta_r = p_y(x) - p_y(x_{edit, r}).
- Calculates sham-corrected sensitivity: tau_r = Delta_r - Delta_sham.
- Tracks prediction flips F_r and relative evidence drops.
"""
from __future__ import annotations

from typing import Any
import numpy as np
import torch
import torch.nn as nn
from src.data.preprocessing import to_model_tensor


def evaluate_counterfactual_sensitivity(
    model: nn.Module,
    device: torch.device,
    original_image: np.ndarray,
    edited_images: dict[str, np.ndarray],
    true_class_id: int,
    class_names: list[str],
) -> list[dict[str, Any]]:
    """Compute baseline and counterfactual probabilities and sensitivity estimands.

    Args:
        model: Evaluated PyTorch classification model in eval mode.
        device: CPU or CUDA device.
        original_image: (224, 224) float32 unnormalized image in [0.0, 1.0].
        edited_images: Dict mapping '<region>_<method>' to (224, 224) float32 edited images.
        true_class_id: Ground-truth target class index.
        class_names: List of class names.
    Returns:
        List of audit records for each region and intervention method.
    """
    model.eval()

    # 1. Baseline prediction
    with torch.no_grad():
        x_base = torch.from_numpy(to_model_tensor(original_image, normalize_imagenet=True)).unsqueeze(0).to(device)
        logits_base = model(x_base)
        probs_base = torch.softmax(logits_base, dim=1).cpu().numpy()[0]

    base_pred_id = int(np.argmax(probs_base))
    base_true_prob = float(probs_base[true_class_id])
    base_confidence = float(np.max(probs_base))

    # Evaluate all interventions
    records: list[dict[str, Any]] = []

    # First get sham deltas for each method to calculate sham-corrected sensitivity
    sham_deltas: dict[str, float] = {}
    for method in ["telea_inpaint", "matched_texture_fill"]:
        key_suffix = "method_a" if method == "telea_inpaint" else "method_b"
        sham_key = f"sham_{key_suffix}"
        if sham_key in edited_images:
            x_sham = torch.from_numpy(to_model_tensor(edited_images[sham_key], normalize_imagenet=True)).unsqueeze(0).to(device)
            with torch.no_grad():
                probs_sham = torch.softmax(model(x_sham), dim=1).cpu().numpy()[0]
            sham_deltas[method] = base_true_prob - float(probs_sham[true_class_id])
        else:
            sham_deltas[method] = 0.0

    target_regions = ["core", "immediate", "outer", "remote", "sham"]
    for reg in target_regions:
        for method in ["telea_inpaint", "matched_texture_fill"]:
            key_suffix = "method_a" if method == "telea_inpaint" else "method_b"
            edit_key = f"{reg}_{key_suffix}"

            if edit_key not in edited_images:
                continue

            edit_img = edited_images[edit_key]
            x_edit = torch.from_numpy(to_model_tensor(edit_img, normalize_imagenet=True)).unsqueeze(0).to(device)
            with torch.no_grad():
                probs_edit = torch.softmax(model(x_edit), dim=1).cpu().numpy()[0]

            edit_pred_id = int(np.argmax(probs_edit))
            edit_true_prob = float(probs_edit[true_class_id])
            edit_confidence = float(np.max(probs_edit))

            delta_raw = base_true_prob - edit_true_prob
            delta_sham = sham_deltas[method]
            tau_sham_corrected = delta_raw - delta_sham if reg != "sham" else 0.0

            is_flipped = bool(edit_pred_id != base_pred_id)
            rel_evidence_drop = float(delta_raw / max(base_true_prob, 1e-4))

            records.append({
                "region": reg,
                "method": method,
                "base_pred_class": class_names[base_pred_id],
                "base_true_prob": base_true_prob,
                "base_confidence": base_confidence,
                "edit_pred_class": class_names[edit_pred_id],
                "edit_true_prob": edit_true_prob,
                "edit_confidence": edit_confidence,
                "delta_raw": float(delta_raw),
                "delta_sham": float(delta_sham),
                "tau_sham_corrected": float(tau_sham_corrected),
                "is_flipped": is_flipped,
                "rel_evidence_drop": rel_evidence_drop,
            })

    return records



def compute_paired_stats(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Compute Wilcoxon signed-rank test and paired Cohen's d_z effect size."""
    import scipy.stats as stats
    diff = x - y
    n = len(diff)
    if n < 3:
        return {"p_value": 1.0, "stat": 0.0, "cohens_d": 0.0, "mean_diff": float(np.mean(diff))}

    # Wilcoxon signed-rank test
    try:
        w_res = stats.wilcoxon(diff, alternative="two-sided")
        pval = float(w_res.pvalue)
        stat = float(w_res.statistic)
    except Exception:
        pval = 1.0
        stat = 0.0

    # Cohen's d_z for paired samples: mean(diff) / std(diff)
    std_diff = float(np.std(diff, ddof=1))
    mean_diff = float(np.mean(diff))
    cohens_d = (mean_diff / std_diff) if std_diff > 1e-6 else 0.0

    return {
        "p_value": pval,
        "stat": stat,
        "cohens_d": float(cohens_d),
        "mean_diff": mean_diff,
    }
