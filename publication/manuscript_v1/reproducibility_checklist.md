# Research Reproducibility Checklist

**Project:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification  
**Target Publication Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17  

---

### 1. Data Governance & Provenance
- [x] **Authoritative Dataset Identified:** Cheng Brain Tumor MRI dataset (Figshare article 1512427).
- [x] **Complete Slice Accounting:** Exactly 3,064 2D T1-CE axial slices accounted for across all splits.
- [x] **Patient Cluster Identifiers:** 233 unique patient IDs preserved from original MATLAB structures.
- [x] **Split Separation:**
  - $S_0$: Strict patient-disjoint 5-fold CV (zero patient overlap between folds).
  - $S_1$: Candidate duplicate-cleaned split at SSIM 0.80 (219 clusters).
  - $S_2$: Aggressively grouped split at SSIM 0.75 (178 clusters).
- [x] **Authoritative Manifests Intact:** `authoritative_patient_manifest.csv` and `duplicate_cluster_manifest.csv` preserved with SHA-256 hashes.

---

### 2. Checkpoint & Inference Accounting
- [x] **Frozen Checkpoints:** Exactly 15 ResNet-50 checkpoints ($3\text{ scenarios} \times 5\text{ folds}$) trained in Phase 2 baseline.
- [x] **Weight Invariance:** Zero parameter fine-tuning, training, or gradient updates performed during intervention studies.
- [x] **Out-of-Fold Evaluation:** Checkpoints evaluated strictly on their held-out test fold partitions (no test-time ensembling).
- [x] **Total Evaluation Records:** Exactly 36,768 unique predictions ($3\text{ scenarios} \times 4\text{ conditions} \times 3,064\text{ slices}$). Zero duplicated rows.

---

### 3. Intervention Geometry & Radiometric Invariants
- [x] **Protected Zone Verified:** Exactly 0 pixels altered within the tumour core and within the 15-pixel dilation margin ring across all 3,064 slices in all conditions.
- [x] **Deterministic Permutation:** Permutations seeded per slice using SHA-256 slice hash + fixed master seed (42).
- [x] **Within-Tile Texture Preservation:** Inside $16\times16$ tiles, Sobel energy in $C_3$ is bit-for-bit identical to baseline natural brain tissue ($30.892316 \equiv 30.892316$).
- [x] **Seam Artifact Match in $C_1$:** Boundary seam Sobel energy matches $C_3$ within 7.2% ($120.58$ vs $129.90$).
- [x] **Seam Suppression in $C_2$:** Boundary seam Sobel energy reduced to $76.00$ ($54.8\%$ reduction of excess boundary gradient); excess high-frequency Fourier energy suppressed by $84.9\%$.

---

### 4. Statistical Inference & Multiplicity Control
- [x] **Unified Contrast Convention:** $\Delta = \text{Macro-F1}_A - \text{Macro-F1}_B$.
- [x] **Clustered Resampling Unit:** Resampled by patient clusters ($S_0$, 233 clusters) and duplicate-group clusters ($S_1$, 219; $S_2$, 178) with $B=2,000$ resamples and fixed random seed 42.
- [x] **Paired Synchronization:** Identical cluster index sequences used for Condition A and Condition B within every bootstrap replicate.
- [x] **Multiplicity Control:** Holm-Bonferroni step-down FWER procedure applied across all 15 confirmatory contrasts simultaneously ($\alpha=0.05$).
- [x] **McNemar Test Scope Clarified:** Acknowledged as paired classification disagreement test, not a substitute for Macro-F1 bootstrap intervals.

---

### 5. Epistemic Claim Boundaries
- [x] **Causal Ratio Restriction:** The 72% seam ratio is strictly described as an empirical ratio of marginal drops, NOT an additive causal variance decomposition.
- [x] **No Biological Causality Claim:** Model behavior is recognized as deep CNN feature dependency, not medical tumour biology.
- [x] **No Continuous Coordinate Claim:** Acknowledged as categorical cranial disorientation relative to pituitary prior, not continuous stereotactic localization.
- [x] **No Generalization Overstatement:** Acknowledged as established strictly on 2D ResNet-50 models on the Figshare cohort.

---

### 6. Code & Script Traceability
- [x] **Data Generator Script:** `scripts/generate_publication_figures_and_tables.py` preserved in `publication/manuscript_v1/figure_source/`.
- [x] **Direct Regeneration:** All 10 figures and all tables can be reproduced with a single command:
  `python publication/manuscript_v1/figure_source/generate_figures_and_tables.py`
- [x] **Automated Regression Suite:** 172 repository tests passing across all 11 phases.
