"""Phase 2 — Controlled Baseline Training Pipeline.

Trains ResNet-50 baseline on unmanipulated MRI images (I_orig) across three approved scenarios:
- S0: Authoritative patient-grouped baseline (prepared_full_run/patient_splits.csv)
- S1: SSIM threshold 0.80 candidate-grouped evaluation (split_regrouped_ssim_0_80.csv)
- S2: SSIM threshold 0.75 candidate-grouped evaluation (split_regrouped_ssim_0_75.csv)

Follows strict 5-fold outer cross-validation with cyclic inner-validation fold,
patient-level / combined-group cluster bootstrap uncertainty estimation,
and zero test-set hyperparameter leakage.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
import torchvision.models as models
import torchvision.transforms as T

# Environment & Paths
ROOT = Path(__file__).resolve().parents[1]
METADATA_CSV = ROOT / "prepared_full_run" / "metadata.csv"
OUTPUT_DIR = ROOT / "experiments" / "phase_2_baseline"
CACHE_CKPT = Path.home() / ".cache" / "torch" / "hub" / "checkpoints" / "resnet50-11ad3fa6.pth"

CLASS_NAMES = ["meningioma", "glioma", "pituitary"]
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS = {idx: name for idx, name in enumerate(CLASS_NAMES)}

SCENARIO_CONFIGS = [
    {
        "scenario": "S0",
        "description": "Authoritative patient-grouped baseline",
        "manifest_path": ROOT / "prepared_full_run" / "patient_splits.csv",
        "group_col": "patient_id",
    },
    {
        "scenario": "S1",
        "description": "SSIM >= 0.80 candidate-grouped evaluation",
        "manifest_path": ROOT / "experiments" / "phase_1_7" / "candidate_grouped_manifests" / "split_regrouped_ssim_0_80.csv",
        "group_col": "combined_group_id",
    },
    {
        "scenario": "S2",
        "description": "SSIM >= 0.75 candidate-grouped evaluation",
        "manifest_path": ROOT / "experiments" / "phase_1_7" / "candidate_grouped_manifests" / "split_regrouped_ssim_0_75.csv",
        "group_col": "combined_group_id",
    },
]


class CachedChengDataset(torch.utils.data.Dataset):
    """In-memory dataset serving preloaded PIL images with on-the-fly transforms."""

    def __init__(self, samples: list[dict], image_cache: dict[str, Image.Image], transform: T.Compose):
        self.samples = samples
        self.image_cache = image_cache
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        record = self.samples[idx]
        sample_id = record["sample_id"]
        img = self.image_cache[sample_id]
        x = self.transform(img)
        y = CLASS_TO_IDX[record["class"]]
        return x, y, sample_id


def build_model(device: torch.device) -> nn.Module:
    """Instantiate ResNet-50 from verified cached weights and attach 3-class linear head."""
    state_dict = torch.load(CACHE_CKPT, map_location="cpu", weights_only=True)
    model = models.resnet50()
    model.load_state_dict(state_dict)

    # Replace final linear layer deterministically
    torch.manual_seed(42)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, len(CLASS_NAMES))
    nn.init.xavier_uniform_(model.fc.weight)
    nn.init.zeros_(model.fc.bias)

    return model.to(device)


def run_training_pipeline():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for sc in SCENARIO_CONFIGS:
        (OUTPUT_DIR / sc["scenario"]).mkdir(parents=True, exist_ok=True)

    # 1. Hardware and Runtime Audit
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None (CPU)"
    vram_gib = (
        torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if torch.cuda.is_available()
        else 0.0
    )
    print(f"Executing on device: {device} ({gpu_name}, {vram_gib:.2f} GiB VRAM)")

    # 2. Preload all images into RAM (RGB 224x224)
    print("Preloading and caching all 3,064 images into memory...")
    t0_cache = time.time()
    with open(METADATA_CSV, newline="", encoding="utf-8-sig") as f:
        meta_rows = list(csv.DictReader(f))

    image_cache = {}
    for r in meta_rows:
        img_p = ROOT / "prepared_full_run" / r["image_output_path"]
        with Image.open(img_p) as raw_img:
            image_cache[r["sample_id"]] = raw_img.convert("RGB").resize(
                (224, 224), Image.Resampling.BILINEAR
            )
    print(f"Cached {len(image_cache)} images in {time.time() - t0_cache:.2f}s.")

    # 3. Define Transforms
    train_transform = T.Compose(
        [
            T.RandomHorizontalFlip(p=0.5),
            T.RandomRotation(degrees=10),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    eval_transform = T.Compose(
        [
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    batch_size = 16
    max_epochs = 20
    early_stopping_patience = 5
    lr = 1e-4
    weight_decay = 1e-4

    all_fold_metrics = []
    all_oof_predictions = []
    all_training_logs = []
    scenario_metrics = {}

    start_total_time = time.time()

    # 4. Scenario Execution Loop
    for sc_info in SCENARIO_CONFIGS:
        scenario = sc_info["scenario"]
        manifest_path = sc_info["manifest_path"]
        group_col = sc_info["group_col"]
        print(f"\n=======================================================")
        print(f"Starting Scenario {scenario}: {sc_info['description']}")
        print(f"Manifest: {manifest_path.name}")
        print(f"=======================================================")

        with open(manifest_path, newline="", encoding="utf-8-sig") as f:
            manifest_rows = list(csv.DictReader(f))

        samples_by_id = {r["sample_id"]: r for r in manifest_rows}
        folds = [f"fold_{i}" for i in range(1, 6)]

        scenario_oof_preds = []

        for outer_idx, test_fold in enumerate(folds, 1):
            val_fold = folds[outer_idx % 5]  # cyclic next fold
            train_folds = [f for f in folds if f not in (test_fold, val_fold)]

            test_records = [r for r in manifest_rows if r["fold"] == test_fold]
            val_records = [r for r in manifest_rows if r["fold"] == val_fold]
            train_records = [r for r in manifest_rows if r["fold"] in train_folds]

            print(
                f"\n--- [{scenario}] {test_fold} | Train: {len(train_records)}, Val ({val_fold}): {len(val_records)}, Test: {len(test_records)} ---"
            )

            # Verification of disjoint grouping
            train_groups = {r.get(group_col, r["patient_id"]) for r in train_records}
            val_groups = {r.get(group_col, r["patient_id"]) for r in val_records}
            test_groups = {r.get(group_col, r["patient_id"]) for r in test_records}

            assert train_groups.isdisjoint(val_groups), f"Train/Val group leakage in {scenario} {test_fold}!"
            assert train_groups.isdisjoint(test_groups), f"Train/Test group leakage in {scenario} {test_fold}!"
            assert val_groups.isdisjoint(test_groups), f"Val/Test group leakage in {scenario} {test_fold}!"

            train_ds = CachedChengDataset(train_records, image_cache, train_transform)
            val_ds = CachedChengDataset(val_records, image_cache, eval_transform)
            test_ds = CachedChengDataset(test_records, image_cache, eval_transform)

            train_loader = torch.utils.data.DataLoader(
                train_ds, batch_size=batch_size, shuffle=True, pin_memory=True
            )
            val_loader = torch.utils.data.DataLoader(
                val_ds, batch_size=batch_size, shuffle=False, pin_memory=True
            )
            test_loader = torch.utils.data.DataLoader(
                test_ds, batch_size=batch_size, shuffle=False, pin_memory=True
            )

            # Class weights on train fold: w_c = N_train / (3 * N_train_c)
            train_class_counts = Counter(r["class"] for r in train_records)
            weights = [
                len(train_records) / (len(CLASS_NAMES) * train_class_counts[c_name])
                for c_name in CLASS_NAMES
            ]
            class_weights_tensor = torch.tensor(weights, dtype=torch.float32, device=device)

            criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

            # Re-seed deterministically before model instantiation
            torch.manual_seed(42 + outer_idx)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(42 + outer_idx)

            model = build_model(device)
            optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
            scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))

            best_val_macro_f1 = -1.0
            best_val_loss = float("inf")
            best_epoch = -1
            best_ckpt_path = OUTPUT_DIR / scenario / f"{test_fold}_best_checkpoint.pt"
            patience_counter = 0

            train_start_t = time.time()

            for epoch in range(1, max_epochs + 1):
                ep_start_t = time.time()
                model.train()
                train_loss_accum = 0.0
                train_preds, train_trues = [], []

                for x, y, _ in train_loader:
                    x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
                    optimizer.zero_grad()
                    with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                        logits = model(x)
                        loss = criterion(logits, y)

                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()

                    train_loss_accum += loss.item() * len(y)
                    preds = torch.argmax(logits, dim=1)
                    train_preds.extend(preds.cpu().numpy())
                    train_trues.extend(y.cpu().numpy())

                train_loss = train_loss_accum / len(train_records)
                train_macro_f1 = f1_score(train_trues, train_preds, average="macro", zero_division=0)
                train_acc = accuracy_score(train_trues, train_preds)

                # Validation
                model.eval()
                val_loss_accum = 0.0
                val_preds, val_trues = [], []
                with torch.no_grad():
                    for x, y, _ in val_loader:
                        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
                        with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                            logits = model(x)
                            loss = criterion(logits, y)
                        val_loss_accum += loss.item() * len(y)
                        preds = torch.argmax(logits, dim=1)
                        val_preds.extend(preds.cpu().numpy())
                        val_trues.extend(y.cpu().numpy())

                val_loss = val_loss_accum / len(val_records)
                val_macro_f1 = f1_score(val_trues, val_preds, average="macro", zero_division=0)
                val_acc = accuracy_score(val_trues, val_preds)
                ep_duration = time.time() - ep_start_t

                # Checkpoint selection: higher val_macro_f1, tie-breaker: lower val_loss
                is_best = False
                if (val_macro_f1 > best_val_macro_f1) or (
                    np.isclose(val_macro_f1, best_val_macro_f1, atol=1e-5) and val_loss < best_val_loss
                ):
                    best_val_macro_f1 = val_macro_f1
                    best_val_loss = val_loss
                    best_epoch = epoch
                    is_best = True
                    patience_counter = 0
                    torch.save(
                        {
                            "epoch": epoch,
                            "scenario": scenario,
                            "fold": test_fold,
                            "val_macro_f1": val_macro_f1,
                            "val_loss": val_loss,
                            "model_state_dict": model.state_dict(),
                        },
                        best_ckpt_path,
                    )
                else:
                    patience_counter += 1

                all_training_logs.append(
                    {
                        "scenario": scenario,
                        "fold": test_fold,
                        "epoch": epoch,
                        "train_loss": f"{train_loss:.6f}",
                        "train_macro_f1": f"{train_macro_f1:.6f}",
                        "train_acc": f"{train_acc:.6f}",
                        "val_loss": f"{val_loss:.6f}",
                        "val_macro_f1": f"{val_macro_f1:.6f}",
                        "val_acc": f"{val_acc:.6f}",
                        "epoch_duration_sec": f"{ep_duration:.2f}",
                        "is_best": is_best,
                    }
                )

                if epoch % 5 == 0 or is_best:
                    print(
                        f"  Ep {epoch:02d} | Train F1: {train_macro_f1:.4f}, Loss: {train_loss:.4f} | Val F1: {val_macro_f1:.4f}, Loss: {val_loss:.4f} {'*' if is_best else ''}"
                    )

                if patience_counter >= early_stopping_patience:
                    print(f"  Early stopping triggered at epoch {epoch} (best epoch: {best_epoch}).")
                    break

            train_duration = time.time() - train_start_t

            # Outer Test Evaluation strictly with Best Checkpoint
            saved_ckpt = torch.load(best_ckpt_path, map_location=device, weights_only=True)
            model.load_state_dict(saved_ckpt["model_state_dict"])
            model.eval()

            test_preds, test_trues, test_probs, test_ids = [], [], [], []
            t0_inf = time.time()
            with torch.no_grad():
                for x, y, s_ids in test_loader:
                    x = x.to(device, non_blocking=True)
                    with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                        logits = model(x)
                        probs = torch.softmax(logits, dim=1)
                    test_preds.extend(torch.argmax(logits, dim=1).cpu().numpy())
                    test_trues.extend(y.numpy())
                    test_probs.extend(probs.cpu().numpy())
                    test_ids.extend(s_ids)

            inf_duration = time.time() - t0_inf

            # Fold Test Metrics
            test_macro_f1 = f1_score(test_trues, test_preds, average="macro", zero_division=0)
            test_bal_acc = balanced_accuracy_score(test_trues, test_preds)
            test_acc = accuracy_score(test_trues, test_preds)
            prec_scores, rec_scores, f1_scores, _ = precision_recall_fscore_support(
                test_trues, test_preds, labels=[0, 1, 2], zero_division=0
            )

            cm = confusion_matrix(test_trues, test_preds, labels=[0, 1, 2]).tolist()
            cm_path = OUTPUT_DIR / scenario / f"{test_fold}_confusion_matrix.json"
            with open(cm_path, "w", encoding="utf-8") as cmf:
                json.dump(
                    {
                        "scenario": scenario,
                        "fold": test_fold,
                        "classes": CLASS_NAMES,
                        "confusion_matrix": cm,
                        "macro_f1": test_macro_f1,
                    },
                    cmf,
                    indent=2,
                )

            # Record predictions for this fold
            fold_pred_rows = []
            ckpt_id = f"resnet50_{scenario}_{test_fold}_ep{best_epoch}"
            for sid, t_cls, p_cls, p_arr in zip(test_ids, test_trues, test_preds, test_probs):
                sample_rec = samples_by_id[sid]
                pred_dict = {
                    "scenario": scenario,
                    "fold": test_fold,
                    "sample_id": sid,
                    "patient_id": sample_rec["patient_id"],
                    "combined_group_id": sample_rec.get("combined_group_id", f"grp_{sample_rec['patient_id']}"),
                    "true_class": IDX_TO_CLASS[t_cls],
                    "true_label": t_cls,
                    "pred_class": IDX_TO_CLASS[p_cls],
                    "pred_label": p_cls,
                    "prob_meningioma": f"{p_arr[0]:.6f}",
                    "prob_glioma": f"{p_arr[1]:.6f}",
                    "prob_pituitary": f"{p_arr[2]:.6f}",
                    "checkpoint_id": ckpt_id,
                }
                fold_pred_rows.append(pred_dict)
                scenario_oof_preds.append(pred_dict)
                all_oof_predictions.append(pred_dict)

            # Save fold predictions CSV
            pred_csv_path = OUTPUT_DIR / scenario / f"{test_fold}_test_predictions.csv"
            with open(pred_csv_path, "w", newline="", encoding="utf-8-sig") as pf:
                writer = csv.DictWriter(pf, fieldnames=list(fold_pred_rows[0].keys()))
                writer.writeheader()
                writer.writerows(fold_pred_rows)

            all_fold_metrics.append(
                {
                    "scenario": scenario,
                    "fold": test_fold,
                    "num_train_samples": len(train_records),
                    "num_val_samples": len(val_records),
                    "num_test_samples": len(test_records),
                    "num_test_patients": len({r["patient_id"] for r in test_records}),
                    "num_test_groups": len(test_groups),
                    "best_epoch": best_epoch,
                    "val_macro_f1": f"{best_val_macro_f1:.6f}",
                    "val_loss": f"{best_val_loss:.6f}",
                    "test_macro_f1": f"{test_macro_f1:.6f}",
                    "test_balanced_acc": f"{test_bal_acc:.6f}",
                    "test_accuracy": f"{test_acc:.6f}",
                    "test_f1_meningioma": f"{f1_scores[0]:.6f}",
                    "test_f1_glioma": f"{f1_scores[1]:.6f}",
                    "test_f1_pituitary": f"{f1_scores[2]:.6f}",
                    "test_prec_meningioma": f"{prec_scores[0]:.6f}",
                    "test_prec_glioma": f"{prec_scores[1]:.6f}",
                    "test_prec_pituitary": f"{prec_scores[2]:.6f}",
                    "test_rec_meningioma": f"{rec_scores[0]:.6f}",
                    "test_rec_glioma": f"{rec_scores[1]:.6f}",
                    "test_rec_pituitary": f"{rec_scores[2]:.6f}",
                    "train_duration_sec": f"{train_duration:.2f}",
                    "inference_latency_sec": f"{inf_duration:.2f}",
                }
            )

            print(
                f"  Test Results: Macro-F1 = {test_macro_f1:.4f}, BalAcc = {test_bal_acc:.4f}, Acc = {test_acc:.4f} (Inf time: {inf_duration:.2f}s)"
            )

        # 5. Global Pooled OOF Metrics for Scenario
        assert len(scenario_oof_preds) == 3064
        global_trues = [r["true_label"] for r in scenario_oof_preds]
        global_preds = [r["pred_label"] for r in scenario_oof_preds]

        glob_macro_f1 = f1_score(global_trues, global_preds, average="macro", zero_division=0)
        glob_bal_acc = balanced_accuracy_score(global_trues, global_preds)
        glob_acc = accuracy_score(global_trues, global_preds)
        glob_prec, glob_rec, glob_f1s, glob_sup = precision_recall_fscore_support(
            global_trues, global_preds, labels=[0, 1, 2], zero_division=0
        )
        glob_cm = confusion_matrix(global_trues, global_preds, labels=[0, 1, 2]).tolist()

        # 6. Patient-Cluster Bootstrap Uncertainty Estimation (B = 2,000)
        print(f"Computing patient-cluster bootstrap (B = 2,000) for {scenario}...")
        clusters = defaultdict(list)
        for idx, r in enumerate(scenario_oof_preds):
            cluster_id = r["combined_group_id"]
            clusters[cluster_id].append((r["true_label"], r["pred_label"]))

        cluster_keys = list(clusters.keys())
        n_clusters = len(cluster_keys)

        np.random.seed(42)
        b_f1s, b_bal_accs, b_accs = [], [], []

        for b in range(2000):
            resampled_keys = np.random.choice(cluster_keys, size=n_clusters, replace=True)
            b_trues, b_preds = [], []
            for k in resampled_keys:
                for t_val, p_val in clusters[k]:
                    b_trues.append(t_val)
                    b_preds.append(p_val)
            b_f1s.append(f1_score(b_trues, b_preds, average="macro", zero_division=0))
            b_bal_accs.append(balanced_accuracy_score(b_trues, b_preds))
            b_accs.append(accuracy_score(b_trues, b_preds))

        ci_f1 = [float(np.percentile(b_f1s, 2.5)), float(np.percentile(b_f1s, 97.5))]
        ci_bal_acc = [float(np.percentile(b_bal_accs, 2.5)), float(np.percentile(b_bal_accs, 97.5))]
        ci_acc = [float(np.percentile(b_accs, 2.5)), float(np.percentile(b_accs, 97.5))]

        # Fold dispersion
        fold_f1_vals = [float(r["test_macro_f1"]) for r in all_fold_metrics if r["scenario"] == scenario]
        fold_f1_mean = float(np.mean(fold_f1_vals))
        fold_f1_std = float(np.std(fold_f1_vals, ddof=1))

        scenario_metrics[scenario] = {
            "description": sc_info["description"],
            "total_samples": 3064,
            "clusters_count": n_clusters,
            "pooled_macro_f1": float(glob_macro_f1),
            "pooled_macro_f1_95ci": ci_f1,
            "pooled_balanced_acc": float(glob_bal_acc),
            "pooled_balanced_acc_95ci": ci_bal_acc,
            "pooled_accuracy": float(glob_acc),
            "pooled_accuracy_95ci": ci_acc,
            "fold_macro_f1_mean": fold_f1_mean,
            "fold_macro_f1_std": fold_f1_std,
            "per_class": {
                CLASS_NAMES[i]: {
                    "precision": float(glob_prec[i]),
                    "recall": float(glob_rec[i]),
                    "f1": float(glob_f1s[i]),
                    "support": int(glob_sup[i]),
                }
                for i in range(len(CLASS_NAMES))
            },
            "confusion_matrix": glob_cm,
        }

        print(f"=== {scenario} Summary: Pooled Macro-F1 = {glob_macro_f1:.4f} (95% CI: [{ci_f1[0]:.4f}, {ci_f1[1]:.4f}]) ===")

    total_pipeline_time = time.time() - start_total_time

    # 7. Write Summary Files
    # A. training_log.csv
    with open(OUTPUT_DIR / "training_log.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_training_logs[0].keys()))
        writer.writeheader()
        writer.writerows(all_training_logs)

    # B. fold_metrics.csv
    with open(OUTPUT_DIR / "fold_metrics.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_fold_metrics[0].keys()))
        writer.writeheader()
        writer.writerows(all_fold_metrics)

    # C. pooled_oof_predictions.csv
    with open(OUTPUT_DIR / "pooled_oof_predictions.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_oof_predictions[0].keys()))
        writer.writeheader()
        writer.writerows(all_oof_predictions)

    # D. Paired Comparison Across Scenarios
    print("Computing paired scenario comparisons on matched samples...")
    # Alignment check: sample_id order across S0, S1, S2
    s0_preds = {r["sample_id"]: r for r in all_oof_predictions if r["scenario"] == "S0"}
    s1_preds = {r["sample_id"]: r for r in all_oof_predictions if r["scenario"] == "S1"}
    s2_preds = {r["sample_id"]: r for r in all_oof_predictions if r["scenario"] == "S2"}

    paired_comparisons = {}
    for pair_name, dict_a, dict_b in [("S0_vs_S1", s0_preds, s1_preds), ("S0_vs_S2", s0_preds, s2_preds), ("S1_vs_S2", s1_preds, s2_preds)]:
        diff_f1 = scenario_metrics[pair_name[:2]]["pooled_macro_f1"] - scenario_metrics[pair_name[-2:]]["pooled_macro_f1"]
        # Pre-group samples by patient ID for vectorized cluster bootstrap
        patient_to_samples = defaultdict(list)
        for sid, r in dict_a.items():
            patient_to_samples[r["patient_id"]].append((r["true_label"], r["pred_label"], dict_b[sid]["pred_label"]))

        patient_keys = list(patient_to_samples.keys())
        n_pts = len(patient_keys)
        np.random.seed(42)
        b_diffs = []
        for b in range(2000):
            resamp_pids = np.random.choice(patient_keys, size=n_pts, replace=True)
            t_a, p_a, p_b = [], [], []
            for pid in resamp_pids:
                for t_val, pa_val, pb_val in patient_to_samples[pid]:
                    t_a.append(t_val)
                    p_a.append(pa_val)
                    p_b.append(pb_val)
            f1_a = f1_score(t_a, p_a, average="macro", zero_division=0)
            f1_b = f1_score(t_a, p_b, average="macro", zero_division=0)
            b_diffs.append(f1_a - f1_b)
        paired_comparisons[pair_name] = {
            "macro_f1_difference": float(diff_f1),
            "paired_95ci": [float(np.percentile(b_diffs, 2.5)), float(np.percentile(b_diffs, 97.5))],
        }

    # E. metrics.json
    final_metrics_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "2_controlled_baseline_training",
        "total_training_duration_sec": total_pipeline_time,
        "hardware": {
            "device": str(device),
            "gpu_name": gpu_name,
            "vram_gib": vram_gib,
            "python_version": platform.python_version(),
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
        },
        "scenarios": scenario_metrics,
        "paired_comparisons": paired_comparisons,
    }

    with open(OUTPUT_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(final_metrics_payload, f, indent=2)

    # F. config.yaml
    config_yaml_content = f"""# Phase 2 Baseline Training Configuration (Locked)
phase: 2_controlled_baseline_training
date_utc: "{datetime.now(timezone.utc).isoformat()}"
status: execution_complete

dataset:
  prepared_directory: "prepared_full_run"
  num_samples: 3064
  classes:
    0: meningioma
    1: glioma
    2: pituitary

scenarios:
  - S0: Authoritative patient-grouped baseline (patient_splits.csv)
  - S1: SSIM >= 0.80 candidate-grouped evaluation (split_regrouped_ssim_0_80.csv)
  - S2: SSIM >= 0.75 candidate-grouped evaluation (split_regrouped_ssim_0_75.csv)

model:
  architecture: resnet50
  pretrained_weights: ResNet50_Weights.IMAGENET1K_V2
  cached_checkpoint_file: "{CACHE_CKPT}"
  cached_checkpoint_sha256: 11ad3fa62ca79e40addfd354a8ec4b7c75143b3038b8d2a807fbc68deab379ca
  output_classes: 3

training:
  seed: 42
  batch_size: {batch_size}
  optimizer: AdamW
  learning_rate: {lr}
  weight_decay: {weight_decay}
  max_epochs: {max_epochs}
  early_stopping_patience: {early_stopping_patience}
  loss: class_weighted_cross_entropy
  amp_enabled: {device.type == 'cuda'}

hardware_used:
  device: "{device}"
  gpu: "{gpu_name}"
  vram_gib: {vram_gib:.2f}
  total_duration_sec: {total_pipeline_time:.2f}
"""
    with open(OUTPUT_DIR / "config.yaml", "w", encoding="utf-8") as f:
        f.write(config_yaml_content)

    print(f"\nAll baseline training runs successfully completed in {total_pipeline_time:.2f}s ({total_pipeline_time/60:.2f} min)!")
    return final_metrics_payload


if __name__ == "__main__":
    run_training_pipeline()
