# Research Reproducibility Checklist

**Project:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification  
**Target Publication Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17  

---

### 1. Data Governance & Provenance
- [x] **Authoritative Dataset Identified:** Cheng Brain Tumor MRI dataset (Figshare article 1512427).
- [x] **Complete Slice Accounting:** Exactly 3,064 2D T1-CE slices accounted for across all splits. Acquisition plane is unannotated in source metadata (**UNRESOLVED — DATASET LIMITATION**).
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
- [x] **Total Evaluation Records:** Exactly 55,152 unique predictions ($3\text{ scenarios} \times 6\text{ conditions} \times 3,064\text{ slices}$). Zero duplicated rows.

---

### 3. Intervention Geometry & Radiometric Invariants
- [x] **Protected Zone Verified:** Exactly 0 pixels altered within the tumour core and within the 15-pixel dilation margin ring across all 3,064 slices in all conditions.
- [x] **Deterministic Permutation:** Permutations seeded per slice using SHA-256 slice hash + fixed master seed (42).
- [x] **Within-Tile Texture Preservation:** Inside $16\times16$ tiles, Sobel energy in $C_3$ is bit-for-bit identical to baseline natural brain tissue ($30.892316 \equiv 30.892316$).
- [x] **Boundary Seam Controls in $C_{1\text{,w2}}$ and $C_{1\text{,w3}}$:** 81.35% pixel preservation; inner $14\times14$ tile pixels completely unaltered.
- [x] **Seam Suppression in $C_2$:** At source $512\times512$, excess boundary seam Sobel reduced by 26.0% and excess HF Fourier energy reduced by 53.9%. At model input $224\times224$, excess seam Sobel reduced by 10.5% and excess HF Fourier energy reduced by 41.2%.

---

### 4. Statistical Inference & Multiplicity Control
- [x] **Unified Contrast Convention:** $\Delta = \text{Macro-F1}_A - \text{Macro-F1}_B$.
- [x] **Clustered Resampling Unit:** Resampled by patient clusters ($S_0$, 233 clusters) and duplicate-group clusters ($S_1$, 219; $S_2$, 178) with $B=25,000$ resamples and fixed random seed 42. Zero degenerate iterations.
- [x] **Paired Synchronization:** Identical cluster index sequences used for Condition A and Condition B within every bootstrap replicate.
- [x] **Primary Uncertainty:** 95% percentile confidence intervals $[\text{CI}_{2.5\%}, \text{CI}_{97.5\%}]$.
- [x] **Exact Log-Space McNemar Test:** Exact two-sided binomial p-values computed via `scipy.special.logsumexp`; extreme values preserved in `mcnemar_exact_log10_p` without float underflow. Asymptotic $\chi^2$ kept separate, never substituted for exact p.
- [x] **Multiplicity Control:** Holm-Bonferroni step-down FWER procedure applied within declared families: Primary Confirmatory ($M=12$), True-Seam Controls ($M=12$), Exploratory ($M=3$).

---

### 5. Epistemic Claim Boundaries
- [x] **Causal Ratio Restriction:** The 28.6% true-seam ratio and 72.2% historical DC-offset ratio are strictly described as empirical ratios of marginal drops, NOT an additive causal variance decomposition.
- [x] **No Biological Causality Claim:** Model behavior is recognized as deep CNN feature dependency, not medical tumour biology.
- [x] **No Continuous Coordinate Claim:** Acknowledged as categorical cranial disorientation relative to pituitary prior, not continuous stereotactic localization.
- [x] **Acquisition Plane Confound Explicitly Unresolved:** Marked as UNRESOLVED — DATASET LIMITATION; resolution stratification does not resolve plane confounding.
- [x] **No Generalization Overstatement:** Acknowledged as established strictly on 2D ResNet-50 models on the Figshare cohort.

---

### 6. Code & Script Traceability
- [x] **Data Generator Script:** `scripts/generate_publication_figures_and_tables.py` preserved in `publication/manuscript_v1/figure_source/`.
- [x] **Direct Regeneration:** All 10 figures and all tables can be reproduced with a single command:
  `python publication/manuscript_v1/figure_source/generate_figures_and_tables.py`
- [x] **Automated Regression Suite:** 178 repository tests passing across all test suites.
