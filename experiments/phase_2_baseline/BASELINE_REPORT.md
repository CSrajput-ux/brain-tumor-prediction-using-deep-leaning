# Phase 2 — Controlled Baseline Training Report

**Phase:** 2 — Controlled Baseline Training  
**Date:** 2026-10-17  
**Auditor / Engineer:** Senior Medical-Imaging ML Engineer & Reproducibility Researcher  
**Final Phase Decision:** **BASELINE-COMPLETE-PENDING-INDEPENDENT-AUDIT**  
**Training Status:** **15 / 15 Folds Successfully Completed** (5 folds across Scenarios S0, S1, S2)  
**Total GPU Training Duration:** 2,611.92 s (43.53 min) on NVIDIA GeForce RTX 4050 Laptop GPU  

---

## 1. Executive Summary and Authorization Verification

In Phase 2, we established the unmanipulated baseline classification performance on the Cheng brain tumor MRI dataset across the three ratified sensitivity scenarios (S0, S1, S2).

All training was conducted **strictly on original, unmanipulated images ($I_{\text{orig}}$)**. In accordance with frozen research integrity rules, **zero intervention experiments** (tumour-only, tumour-removed, placebo masking, context shifting) were conducted in this phase.

### Verification of Frozen Inputs and Authoritative Artifacts
- Frozen Pre-Registration: `experiments/phase_1_8/C_FROZEN_PREREGISTRATION.md` verified.
- Unresolved Risk Record: `experiments/phase_1_8/D_UNRESOLVED_RISK_RECORD.md` verified.
- Final Gate Authorization: `experiments/phase_1_8/E_FINAL_GATE_DECISION.md` (GO-FOR-BASELINE-ONLY) verified.
- Authoritative baseline manifests and splits were **not modified**.

---

## 2. Audit of Critical Experimental Precautions

We explicitly confirm adherence to the five core experimental safeguards:

1. **Test-Set Isolation and Checkpoint Selection:**
   - Outer test folds were **NEVER evaluated during training**.
   - Model checkpoints were selected **strictly and exclusively using the inner validation fold** (`monitored_metric: val_macro_f1`, tie-breaker: `val_loss`).
   - The outer test fold was evaluated exactly once per fold with the saved frozen checkpoint.
2. **Zero Failed Folds / Zero Skipped Runs:**
   - All 15 fold training runs (5 folds $\times$ 3 scenarios) converged and logged complete metrics. Zero runs were skipped, aborted, or omitted.
3. **Hardware Throughput vs Scientific Validity Separation:**
   - High training throughput (RTX 4050 AMP execution) is reported purely as an engineering runtime metric. It is not treated as evidence of model quality or scientific validity.
4. **Strict Ablation Gating:**
   - No tumor-region masking, excision, infilling, placebo-region ablation, or context-shift experiments were initiated. The intervention battery remains securely gated for Phase 3.
5. **RAM Caching Data Integrity Check:**
   - Pre-caching into RAM was performed solely to eliminate Windows disk I/O bottlenecks.
   - Preprocessing and normalization were verified to match the frozen configuration: 512x512 grayscale images converted to 3-channel RGB, resized to $224 \times 224$ bilinear, scaled to $[0, 1]$, and normalized with standard ImageNet parameters ($\mu = [0.485, 0.456, 0.406], \sigma = [0.229, 0.224, 0.225]$).
   - Training augmentations (RandomHorizontalFlip, RandomRotation(10)) were applied dynamically in-memory during training only. Validation and test sets used deterministic evaluation transforms with no augmentation.

---

## 3. Hardware and Software Environment

| Component | Value / Specification |
|---|---|
| **GPU Model** | NVIDIA GeForce RTX 4050 Laptop GPU |
| **VRAM Available** | 6.00 GiB (Peak allocation during training: 1,024 MiB) |
| **CUDA / Driver** | CUDA 12.6 / Driver 591.86 |
| **Python Environment** | Python 3.14.6 |
| **PyTorch / Torchvision** | PyTorch 2.15.0.dev20260907+cu126, Torchvision 0.30.0.dev20260906+cu126 |
| **Model Architecture** | ResNet-50 (ImageNet V2 pretrained weights, cached SHA-256: `11ad3fa6...`) |
| **Output Head** | 3 classes: meningioma (0), glioma (1), pituitary (2) |
| **Optimization** | AdamW ($\text{lr} = 10^{-4}, \text{weight\_decay} = 10^{-4}$), Batch size 16 |
| **Loss Function** | Class-weighted CrossEntropyLoss ($w_c = \frac{N_{\text{train}}}{3 \cdot N_{\text{train}, c}}$) |
| **Mixed Precision** | PyTorch AMP (`torch.amp.autocast('cuda')`) enabled |

---

## 4. Quantitative Results Across Scenarios

All 3,064 out-of-fold test samples were evaluated across Scenarios S0, S1, and S2:

### Summary Comparison Table

| Metric | Scenario S0 (Baseline) | Scenario S1 (SSIM ≥ 0.80) | Scenario S2 (SSIM ≥ 0.75) |
|---|---|---|---|
| **Grouping Unit** | Clinical Patient ID (233 groups) | Combined Group (231 groups) | Combined Group (217 groups) |
| **Pooled Macro-F1** | **0.9330** | **0.9332** | **0.9273** |
| **95% Cluster Bootstrap CI** | **[0.9060, 0.9549]** | **[0.9049, 0.9562]** | **[0.8982, 0.9503]** |
| **Pooled Balanced Accuracy** | 0.9360 [0.9103, 0.9578] | 0.9336 [0.9058, 0.9560] | 0.9300 [0.9029, 0.9526] |
| **Pooled Accuracy** | 0.9406 [0.9179, 0.9603] | 0.9419 [0.9174, 0.9624] | 0.9354 [0.9108, 0.9564] |
| **Fold Macro-F1 Mean ± Std** | $0.9328 \pm 0.0236$ | $0.9328 \pm 0.0285$ | $0.9274 \pm 0.0204$ |
| **Meningioma F1 / Precision / Recall** | 0.8844 / 0.8670 / 0.9025 | 0.8832 / 0.8851 / 0.8814 | 0.8720 / 0.8548 / 0.8898 |
| **Glioma F1 / Precision / Recall** | 0.9606 / 0.9720 / 0.9495 | 0.9648 / 0.9682 / 0.9614 | 0.9550 / 0.9649 / 0.9453 |
| **Pituitary F1 / Precision / Recall** | 0.9539 / 0.9518 / 0.9559 | 0.9514 / 0.9449 / 0.9581 | 0.9548 / 0.9548 / 0.9548 |

---

## 5. Fold-Wise Breakdown

### Scenario S0: Authoritative Patient-Grouped Baseline
- **Fold 1:** Test F1 = 0.9354, BalAcc = 0.9449, Acc = 0.9413 (Best Ep: 5, Train Time: 123.64s)
- **Fold 2:** Test F1 = 0.9096, BalAcc = 0.9093, Acc = 0.9169 (Best Ep: 8, Train Time: 161.94s)
- **Fold 3:** Test F1 = 0.9706, BalAcc = 0.9707, Acc = 0.9755 (Best Ep: 6, Train Time: 140.70s)
- **Fold 4:** Test F1 = 0.9170, BalAcc = 0.9120, Acc = 0.9331 (Best Ep: 4, Train Time: 140.66s)
- **Fold 5:** Test F1 = 0.9316, BalAcc = 0.9429, Acc = 0.9364 (Best Ep: 14, Train Time: 321.50s)

### Scenario S1: SSIM ≥ 0.80 Regrouped Split
- **Fold 1:** Test F1 = 0.9710, BalAcc = 0.9691, Acc = 0.9739 (Best Ep: 14, Train Time: 235.00s)
- **Fold 2:** Test F1 = 0.9512, BalAcc = 0.9576, Acc = 0.9560 (Best Ep: 11, Train Time: 221.33s)
- **Fold 3:** Test F1 = 0.9020, BalAcc = 0.8943, Acc = 0.9217 (Best Ep: 7, Train Time: 119.90s)
- **Fold 4:** Test F1 = 0.9106, BalAcc = 0.9174, Acc = 0.9199 (Best Ep: 12, Train Time: 170.06s)
- **Fold 5:** Test F1 = 0.9291, BalAcc = 0.9297, Acc = 0.9380 (Best Ep: 13, Train Time: 179.72s)

### Scenario S2: SSIM ≥ 0.75 Regrouped Split
- **Fold 1:** Test F1 = 0.9383, BalAcc = 0.9397, Acc = 0.9429 (Best Ep: 13, Train Time: 180.30s)
- **Fold 2:** Test F1 = 0.9286, BalAcc = 0.9460, Acc = 0.9314 (Best Ep: 6, Train Time: 109.89s)
- **Fold 3:** Test F1 = 0.8952, BalAcc = 0.8972, Acc = 0.9072 (Best Ep: 8, Train Time: 130.15s)
- **Fold 4:** Test F1 = 0.9252, BalAcc = 0.9225, Acc = 0.9395 (Best Ep: 10, Train Time: 150.54s)
- **Fold 5:** Test F1 = 0.9498, BalAcc = 0.9448, Acc = 0.9560 (Best Ep: 9, Train Time: 154.30s)

---

## 6. Paired Scenario Sensitivity Analysis

To test whether candidate near-duplicate leakage distorted baseline classification performance, we conducted paired patient-cluster bootstrap comparisons on the 3,064 matched test predictions:

| Comparison | $\Delta \text{Macro-F1}$ | 95% Paired Cluster Bootstrap CI | Inference |
|---|---:|---|---|
| **S0 vs S1** | **-0.00018** (-0.02%) | **[-0.0140, +0.0139]** | Statistically indistinguishable from zero |
| **S0 vs S2** | **+0.00570** (+0.57%) | **[-0.0070, +0.0182]** | 95% CI encompasses zero; no significant change |
| **S1 vs S2** | **+0.00588** (+0.59%) | **[-0.0088, +0.0195]** | 95% CI encompasses zero; no significant change |

### Critical Scientific Finding:
The baseline model's classification performance is **exceptionally stable across leakage assumptions**:
- Regrouping candidate pairs at SSIM $\ge 0.80$ changes performance by less than 0.02 percentage points.
- Regrouping candidate pairs at SSIM $\ge 0.75$ changes performance by less than 0.60 percentage points.
- Because all paired confidence intervals encompass zero, **baseline classification performance is not driven by candidate cross-fold leakage**.

---

## 7. Confusion Matrices

### Scenario S0 Confusion Matrix (Rows: True, Columns: Predicted)
```
             Pred Meningioma    Pred Glioma    Pred Pituitary    Total True
True Mening         639              26              43             708
True Glioma          70            1354               2            1426
True Pituit          28              13             889             930
Total Pred          737            1393             934            3064
```

### Scenario S1 Confusion Matrix
```
             Pred Meningioma    Pred Glioma    Pred Pituitary    Total True
True Mening         624              37              47             708
True Glioma          50            1371               5            1426
True Pituit          31               8             891             930
Total Pred          705            1416             943            3064
```

### Scenario S2 Confusion Matrix
```
             Pred Meningioma    Pred Glioma    Pred Pituitary    Total True
True Mening         630              40              38             708
True Glioma          74            1348               4            1426
True Pituit          33               9             888             930
Total Pred          737            1397             930            3064
```

---

## 8. Epistemic Boundaries and Next Steps

> [!CAUTION]
> **BASELINE BENCHMARK ONLY — NO CAUSAL INFERENCE PERMITTED**
>
> A high baseline Macro-F1 (~0.933) confirms that the ResNet-50 network can reliably separate brain tumor classes on unmanipulated MRI slices.
>
> It does **NOT** prove that the network is looking at the tumor, that it understands tumor biology, or that it is safe for clinical deployment. The network may achieve 0.93 Macro-F1 purely by exploiting brain shape, slice level, or cranial contours.
>
> Whether the model relies on tumor pathology versus surrounding context will be determined strictly in Phase 3 through the pre-registered intervention contrast battery.

### Formal Decision: **BASELINE-COMPLETE-PENDING-INDEPENDENT-AUDIT**
- All 15 baseline checkpoints are archived and frozen.
- All fold metrics, training logs, and prediction CSVs are published.
- Intervention experiments remain locked pending independent audit of Phase 2 artifacts.
