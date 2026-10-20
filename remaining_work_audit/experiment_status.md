# Research Project Status & Experiment Verification Report

**Project:** Brain MRI Spatial Disentanglement & Shortcut Learning Study  
**Dataset:** Cheng Figshare 1512427 (3,064 T1-CE slices, 233 patients, 3 classes)  
**Audit Directory:** `remaining_work_audit/`  
**Date:** October 2026  

---

## 1. Inventory of Phases and Execution Records

| Phase / Component | Canonical Script / Location | Output Artifacts | Checkpoint / Preds Verified | Execution Status |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: Dataset Audit & Preprocessing** | `scripts/prepare_cheng_dataset.py` | `prepared_full_run/` (3,064 images, masks, npz) | All 3,064 samples verified with SHA-256 | **COMPLETED & LOCKED** |
| **Phase 1.6 & 1.7: Duplicate Audit & SSIM Grouping** | `scripts/investigate_duplicates.py` | `experiments/phase_1_7/candidate_grouped_manifests/` | Split manifests for SSIM 0.80, 0.75, 0.70, 0.60 | **COMPLETED & LOCKED** |
| **Phase 2: Baseline ResNet-50 Training** | `scripts/train_baseline.py` | `experiments/phase_2_baseline/` | 15 checkpoints (.pt) & 15 test predictions (.csv) | **COMPLETED & VERIFIED** |
| **Phase 3: Initial Spatial Interventions** | `scripts/run_phase_3_interventions.py` | `experiments/phase_3_interventions/` | 55,152 matched predictions (6 conditions x 3064 x 3) | **COMPLETED & VERIFIED** |
| **Phase 4 & 4.1: Statistical Reconciliation** | `scripts/run_phase_4_statistical_and_robustness_audit.py` | `experiments/phase_4_audit/` | Paired cluster bootstrap metrics (B=2,000) | **COMPLETED & VERIFIED** |
| **Phase 5 & 5.1: Context Reliance & Spatial Validity** | `scripts/run_phase_5_context_reliance.py` | `experiments/phase_5_context_reliance/` | 64,344 matched predictions (7 conditions x 3064 x 3) | **COMPLETED & VERIFIED** |
| **Phase 6 & 6.1: Spatial Controls & Inpainting** | `scripts/run_phase_6_spatial_controls.py` | `experiments/phase_6_spatial_controls/` | 128,688 matched predictions (14 conditions x 3064 x 3) | **COMPLETED & VERIFIED** |
| **Phase 7: Systematic Literature Review** | `experiments/phase_7_literature_review/` | PRISMA logs, bibliography, claim matrices | Reference verification table | **COMPLETED & VERIFIED** |
| **Phase 8: Novelty Discovery & Preregistration** | `experiments/phase_8_novelty_discovery/` | Proposed preregistration & hypothesis gates | Pre-registered thresholds locked | **COMPLETED & LOCKED** |
| **Phase 9: Seam-Spatial Disentanglement** | `scripts/run_phase_9_seam_spatial_disentanglement.py` | `experiments/phase_9_seam_spatial_disentanglement/` | 36,768 matched predictions (C0, C1, C2, C3 x 3064 x 3) | **COMPLETED & VERIFIED** |
| **Phase 9.1: Independent Re-computation Audit** | `scripts/run_phase_9_1_independent_audit.py` | `experiments/phase_9_1_independent_audit/` | Exact reproduction of primary metrics | **COMPLETED & VERIFIED** |
| **Phase 9.2: Manuscript Readiness Audit** | `scripts/run_phase_9_2_manuscript_readiness_audit.py` | `experiments/phase_9_2_manuscript_readiness/` | Canonical contrasts table, claim boundaries | **COMPLETED & VERIFIED** |
| **Phase 9.3: Publication Package v1** | `publication/manuscript_v1/` | Manuscript (MD & DOCX), Figures 1-10, Tables 1-8 | 172 automated regression tests passing | **COMPLETED & READY FOR AUDIT** |

---

## 2. Checkpoint and Prediction Verification Summary

1. **Checkpoints:** All 15 ResNet-50 checkpoints are present in `experiments/phase_2_baseline/`:
   - `S0/fold_{1..5}_best_checkpoint.pt`
   - `S1/fold_{1..5}_best_checkpoint.pt`
   - `S2/fold_{1..5}_best_checkpoint.pt`
2. **Out-of-Fold Baseline Predictions:** All 15 prediction CSVs exist, summing to exactly 3,064 unique slices per scenario.
3. **Intervention Predictions:** All conditions evaluated in Phase 9 (`C0_orig`, `C1_seam_only`, `C2_seam_suppressed`, `C3_c5lp_scramble`) have full out-of-fold probability vectors and true labels across all 3 scenarios (36,768 rows).
4. **Split Manifests:**
   - **S0:** `prepared_full_run/patient_splits.csv` (233 patients, verified 100% match to predictions).
   - **S1:** `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_80.csv` (219 clusters).
   - **S2:** `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_75.csv` (178 clusters).

---

## 3. Immediate Action Plan for Remaining Work

- **Stage 1 (Audit):** Complete with 4 canonical audit files generated in `remaining_work_audit/`.
- **Stage 2 (Re-analysis without retraining):**
  - **Task 5:** Execute synchronized paired cluster bootstrap with $B = 25,000$ (exceeding $B \ge 20,000$) on existing frozen OOF predictions.
  - **Task 6 & 7:** Diagnostics at actual 224x224 model input (seam gradient energy, unchanged-area fraction, mask overlap).
  - **Task 8:** High-frequency Fourier diagnostics at model input resolution.
  - **Task 9:** Source image size analysis (256x256 vs 512x512).
- **Stage 3 (New Experiments):**
  - **Task 1:** Finalize plane metadata audit report (established as unsupported by source data; no inference).
  - **Task 2:** True Seam-Only Control (construct pixel-preservation masks, gradient energy matching).
- **Stage 4 (External Verification & Reproducibility):**
  - **Task 10 & 11:** Verify Vangala et al. and update reference verification CSV.
  - **Task 13:** Fix test suite count documentation (167 vs 172) in reproducibility checklist.
  - **Task 16:** S0 manifest verification completed (verified present at `prepared_full_run/patient_splits.csv`).
