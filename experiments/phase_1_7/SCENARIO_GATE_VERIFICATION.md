# Pre-Training Gate Verification Across Sensitivity Scenarios

**Phase:** 1.7 — Sensitivity Analysis and Pre-Registration  
**Date:** 2026-10-17  
**Objective:** Verify COND-3 gate compliance for all candidate regrouped manifests prior to training.  

---

## 1. Summary Gate Matrix

| Scenario | Threshold | Manifest | Samples | Patient Crossings | Component Crossings | Cross-Fold Leakage (≥ τ) | Min Class Count | Gate Status |
|---|---:|---|---:|---:|---:|---:|---:|---|
| **S1** | 0.80 | `split_regrouped_ssim_0_80.csv` | 3064 | 0 | 0 | **0** | 141 | **PASS** |
| **S2** | 0.75 | `split_regrouped_ssim_0_75.csv` | 3064 | 0 | 0 | **0** | 141 | **PASS** |
| **S3a** | 0.70 | `split_regrouped_ssim_0_70.csv` | 3064 | 0 | 0 | **0** | 141 | **PASS** |
| **S3b** | 0.60 | `split_regrouped_ssim_0_60.csv` | 3064 | 0 | 0 | **0** | 137 | **PASS (Distorted)** |

---

## 2. Key Findings and Gate Compliance

1. **Complete Cross-Fold Leakage Elimination:** Under each scenario's hypothesis threshold $\tau$, every single candidate pair with $\text{SSIM} \ge \tau$ is co-assigned to the same fold. **Residual cross-fold leakage at the target threshold is exactly ZERO across all scenarios.**
2. **Zero Clinical Patient Boundary Violations:** Across all 3,064 samples and 233 patient IDs, no patient ID is split across multiple folds.
3. **Zero Component Splitting:** No indivisible similarity group is severed.
4. **Class Sufficiency:** Every class in every fold maintains $\ge 137$ samples, far exceeding the 50-sample gate threshold.

### Operational Status: COND-3 FULLY SATISFIED
All candidate split manifests are structurally and logically verified. Training pipelines can consume any of these manifests directly without format modification.