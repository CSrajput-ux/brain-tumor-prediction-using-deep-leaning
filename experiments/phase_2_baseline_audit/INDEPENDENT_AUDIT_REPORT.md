# Phase 2.1 — Independent Baseline Completion Audit Report

**Phase:** 2.1 — Independent Baseline Completion Audit  
**Date:** 2026-10-17  
**Auditor:** Independent Medical-Imaging ML Auditor & Statistical Reviewer  
**Audited Directory:** `experiments/phase_2_baseline/`  
**Final Audit Decision:** **AUDIT-PASS-WITH-LIMITATIONS**  

---

## 1. Executive Summary

We conducted an independent audit and complete numerical recomputation of the Phase 2 baseline models on the Cheng brain tumor MRI dataset across Scenarios S0, S1, and S2.

### Audit Findings:
1. **Cryptographic Checksum Verification:** 100% pass (51 of 51 artifacts in `experiments/phase_2_baseline/checksums.json` verified byte-for-byte).
2. **Prediction Record Integrity:** All 9,192 prediction records ($3,064 \times 3$ scenarios) contain unique, properly aligned sample IDs, valid finite probabilities that sum to 1.0, and exact `pred_label` alignment with $\text{argmax}(\text{probs})$.
3. **Metric Reconciliation:** 102 out of 102 reported fold-level and pooled metrics match independently recomputed values with **zero mismatches** ($\Delta < 10^{-5}$).
4. **Partition Isolation & Early Stopping Audit:** Zero patient overlap and zero component overlap between train, validation, and test sets across all 15 runs. Outer test data was never evaluated during epoch iterations or used for checkpoint selection.
5. **Statistical Stability:** Paired cluster-bootstrap comparisons demonstrate that Macro-F1 varies by less than 0.6 percentage points across grouping assumptions (S0 vs S1: $\Delta = -0.0002$, S0 vs S2: $\Delta = +0.0057$, S1 vs S2: $\Delta = +0.0059$).

---

## 2. Artifact and Checksum Audit

All 51 primary files and model checkpoints were inspected directly:
- **15 Checkpoints:** `S0/fold_{1..5}_best_checkpoint.pt`, `S1/fold_{1..5}_best_checkpoint.pt`, `S2/fold_{1..5}_best_checkpoint.pt`.
  - All checkpoints exist, are non-empty ($> 90$ MB each), load cleanly into PyTorch, and match the ResNet-50 linear head structure (`fc.weight`: $3 \times 2048$).
- **15 Prediction CSVs:** Match outer test fold samples exactly.
- **15 Confusion Matrix JSONs:** Match test ground truth and predicted classes.
- **Summary Files:** `fold_metrics.csv`, `pooled_oof_predictions.csv`, `training_log.csv`, `metrics.json`, `config.yaml`.
- **Integrity Status:** Authoritative files `patient_splits.csv` and `metadata.csv` match recorded baselines.

---

## 3. Independent Metric Recomputation and Reconciliation

From `pooled_oof_predictions.csv`, all metrics were independently recomputed:

### Recomputed Global Metrics Across Scenarios

| Metric | Scenario S0 (Reported / Recomputed) | Scenario S1 (Reported / Recomputed) | Scenario S2 (Reported / Recomputed) | Status |
|---|---|---|---|---|
| **Total Test Samples** | 3,064 / 3,064 | 3,064 / 3,064 | 3,064 / 3,064 | EXACT MATCH |
| **Unique Sample IDs** | 3,064 / 3,064 | 3,064 / 3,064 | 3,064 / 3,064 | EXACT MATCH |
| **Pooled Macro-F1** | 0.9330 / **0.9330** | 0.9332 / **0.9332** | 0.9273 / **0.9273** | EXACT MATCH |
| **95% Cluster Bootstrap CI** | [0.9060, 0.9549] / **[0.9060, 0.9549]** | [0.9049, 0.9562] / **[0.9049, 0.9562]** | [0.8982, 0.9503] / **[0.8982, 0.9503]** | EXACT MATCH |
| **Pooled Balanced Accuracy** | 0.9360 / **0.9360** | 0.9336 / **0.9336** | 0.9300 / **0.9300** | EXACT MATCH |
| **Pooled Overall Accuracy** | 0.9406 / **0.9406** | 0.9419 / **0.9419** | 0.9354 / **0.9354** | EXACT MATCH |
| **Fold Macro-F1 Mean ± Std** | $0.9328 \pm 0.0236$ | $0.9328 \pm 0.0285$ | $0.9274 \pm 0.0204$ | EXACT MATCH |
| **Meningioma F1 (Support: 708)** | 0.8844 / **0.8844** | 0.8832 / **0.8832** | 0.8720 / **0.8720** | EXACT MATCH |
| **Glioma F1 (Support: 1,426)** | 0.9606 / **0.9606** | 0.9648 / **0.9648** | 0.9550 / **0.9550** | EXACT MATCH |
| **Pituitary F1 (Support: 930)** | 0.9539 / **0.9539** | 0.9514 / **0.9514** | 0.9548 / **0.9548** | EXACT MATCH |

*Full reconciliation table archived in [metric_reconciliation.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_2_baseline_audit/metric_reconciliation.csv) (102 / 102 metrics verified).*

---

## 4. Evaluation Isolation and Leakage Audit

We audited the data flow across all 15 fold runs to verify that no test leakage occurred:

1. **Patient Disjointness:**
   - For every fold $k$, $\text{Patients}(\text{Train}) \cap \text{Patients}(\text{Val}) = \emptyset$.
   - $\text{Patients}(\text{Train}) \cap \text{Patients}(\text{Test}) = \emptyset$.
   - $\text{Patients}(\text{Val}) \cap \text{Patients}(\text{Test}) = \emptyset$.
   - Verified across all 15 runs. Zero patient IDs cross partitions.
2. **Component Disjointness:**
   - In S1 ($\tau = 0.80$) and S2 ($\tau = 0.75$), indivisible combined evaluation groups do not cross partitions. Zero components cross folds.
3. **Early Stopping & Checkpoint Selection Integrity:**
   - In `training_log.csv`, every saved checkpoint corresponds to the epoch where `val_macro_f1` was maximized on inner validation data.
   - Outer test fold samples were never passed to `model.forward()` during training epochs.
4. **Input Feature Sanitization:**
   - Predictive inputs were strictly pixel tensors ($224 \times 224 \times 3$).
   - Patient IDs, filenames, fold labels, and masks were completely excluded from model inputs.

*Detailed partition statistics archived in [split_isolation_audit.json](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_2_baseline_audit/split_isolation_audit.json).*

---

## 5. Statistical Uncertainty and Paired Comparisons Audit

### Paired Differences Across Scenarios
Using matched sample predictions on all 3,064 slices:
- **S0 vs S1:** $\Delta = -0.00018$ (95% CI: $[-0.0140, +0.0139]$)
- **S0 vs S2:** $\Delta = +0.00570$ (95% CI: $[-0.0070, +0.0182]$)
- **S1 vs S2:** $\Delta = +0.00588$ (95% CI: $[-0.0088, +0.0195]$)

> [!IMPORTANT]
> **STATISTICAL INTERPRETATION OF ZERO-CROSSING INTERVALS**
>
> A paired confidence interval crossing zero does **NOT** prove that two models or scenarios are biologically or clinically equivalent.
>
> It demonstrates that within the statistical power of 233 patient clusters, the observed performance delta is smaller than the sampling noise. We conclude that baseline performance is robust against the candidate regrouping assumptions tested, not that identical representations are learned.

---

## 6. Training Execution and Hardware Audit

- **Execution Mode:** CUDA mixed precision (`torch.amp.autocast('cuda')`) on NVIDIA GeForce RTX 4050 Laptop GPU.
- **Total Training Duration:** 2,611.92 seconds (43.53 minutes). Average per-epoch duration: ~15–20 seconds.
- **Convergence:** All 15 runs triggered early stopping between epochs 4 and 14 (out of 20 maximum), confirming convergence without overtraining.
- **Numerical Stability:** Zero NaN or Inf losses observed across all 15 runs.
- **RAM Caching Audit:** Pre-caching into RAM was verified to perform only deterministic PIL resizing and RGB conversion. Preprocessing matches ImageNet normalization.

---

## 7. Documented Limitations and Epistemic Scope

While the baseline models pass technical verification, we document the following critical scientific limitations:
1. **Unmanipulated Baseline Only:** High accuracy (~0.933 Macro-F1) confirms that ResNet-50 can separate brain tumor categories on intact slices. It provides **zero evidence** that the network uses intratumoral features rather than surrounding brain anatomy.
2. **Missing Clinical Provenance:** Original acquisition-level DICOM headers remain unavailable in the public Figshare dataset.
3. **Screening Horizon:** Grouping controls candidate pairs with pHash distance $\le 4/64$; unknown near-duplicates with higher divergence remain unmodeled.
4. **2D Representation Constraint:** Slices are evaluated independently; 3D volumetric volumetric spatial continuity is unmodeled.

---

## 8. Final Audit Decision: **AUDIT-PASS-WITH-LIMITATIONS**

The Phase 2 baseline models and evaluation artifacts are **fully verified, mathematically reconciled, and scientifically defensible**.

This audit authorizes the research project to consider progressing to **Phase 3 (Controlled Intervention & Ablation Experiments)** under the frozen pre-registration protocol.
