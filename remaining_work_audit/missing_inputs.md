# Remaining Work Audit: Missing Inputs, Blockers, and Constraints

**Date:** October 2026  
**Auditor:** Senior Medical Imaging Researcher & Antigravity IDE Lead  
**Scope:** Verification of all required inputs across Stage 1 to Stage 5.

---

## 1. Status of Reported Missing Files

### A. `prepared_full_run/patient_splits.csv`
- **Reported Status in Prompt:** Missing file.
- **Actual Audit Finding:** **PRESENT AND FULLY VERIFIED ON DISK**.
- **Path:** `prepared_full_run/patient_splits.csv`
- **Row Count:** Exactly 3,064 rows across 233 unique patients.
- **Fold Breakdown:**
  - Fold 1: 613 slices
  - Fold 2: 614 slices
  - Fold 3: 611 slices
  - Fold 4: 613 slices
  - Fold 5: 613 slices
  - Total: 3,064 slices
- **Equivalence Check:** 100% bit-for-bit and sample-for-sample match with `experiments/phase_2_baseline/S0/fold_{1..5}_test_predictions.csv`.
- **Verdict:** Canonical S0 split manifest is completely intact.

### B. `experiment_config.yaml`
- **Location in Repo:** `experiments/phase_9_seam_spatial_disentanglement/experiment_config.yaml`
- **Size:** 1,892 bytes.
- **Status:** Present, intact, and configuration parameters match Phase 9 pipeline.

---

## 2. Definitive Blocker: Anatomical Plane / Orientation Metadata (Task 1)

- **Dataset Limitation:** The original Cheng Figshare 1512427 dataset (`brainTumorDataPublic_*.zip`, 3,064 `.mat` files) contains strictly five fields in each `.mat` file:
  `cjdata.PID`, `cjdata.image`, `cjdata.label`, `cjdata.tumorBorder`, `cjdata.tumorMask`.
- **Missing Information:**
  - No DICOM acquisition headers.
  - No anatomical plane tags (axial, coronal, sagittal).
  - No slice sequence numbers or patient orientation vectors.
- **Author Statement in `README 2024.txt`:**
  *"No further details are available due to the long passage of time."*
- **Scientific Impact on Task 1:**
  - True plane-stratified quantitative evaluation is **strictly unsupported** by the dataset ground truth.
  - As mandated by the protocol: We **refuse to hallucinate or heuristically infer** anatomical plane from slice appearance or tumour class.
  - Task 1 deliverable `plane_metadata_audit.csv` establishes this definitive provenance constraint.

---

## 3. Hardware & Compute Constraints (Task 4)

- **Current Environment Execution:**
  - Python: 3.10.11 / 3.14.6
  - PyTorch: 2.14.0+cpu
  - CUDA Available: **False** (0 GPU devices available in current shell session).
- **Scientific Impact on Task 4 (Multi-seed Retraining):**
  - Full retraining of 15 ResNet-50 models per seed across 5 folds and 3 scenarios (45 models for 3 seeds, 75 models for 5 seeds) is computationally infeasible on local CPU.
  - Protocol Compliance: In accordance with Section 4 (Experiment 4): *"If this experiment is infeasible, document the compute limitation. Do not fabricate multi-seed results."*
  - Re-analysis tasks (Tasks 5–9), external verification (Tasks 10–12), reproducibility fixes (Tasks 13–16), and new frozen-checkpoint intervention controls (Task 2 & 3) do NOT require full retraining and will proceed immediately.

---

## 4. Discrepancy Needing Table 2 Regeneration

- **Table 2 Discrepancy:** `publication/manuscript_v1/tables/table2_evaluation_scenarios.csv` lists fold sample sizes as `618, 616, 612, 610, 608`.
- **Actual Canonical Fold Counts:**
  - **S0:** 613, 614, 611, 613, 613 (Sum = 3,064)
  - **S1:** 612, 614, 613, 612, 613 (Sum = 3,064)
  - **S2:** 613, 612, 614, 612, 613 (Sum = 3,064)
- **Remediation Action:** Table 2 must be regenerated from the actual manifests using a verified script.
