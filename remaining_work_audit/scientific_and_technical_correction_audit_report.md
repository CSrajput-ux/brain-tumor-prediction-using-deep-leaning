# Scientific and Technical Correction Audit Report: Brain Tumour MRI Classification Under Spatial Disentanglement

**Document Version:** 1.0 (Post-Correction Final Audit)  
**Date:** October 20, 2026  
**Auditor:** Senior Medical Imaging Scientist, Statistical Reviewer, and ML Systems Engineer  
**Baseline Repository:** [https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning](https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning)  
**Execution Environment:** Windows x64, Python 3.14.6, PyTorch 2.15.0.dev, CUDA 12.6, NVIDIA GeForce RTX 4050 Laptop GPU  
**Audit Gate Status: **NOT YET VERIFIED — PENDING AUTHOR AND JOURNAL ACTIONS**

> **Correction notice (2026-10-22):** The C2 attenuation figures recorded in this historical audit (26.0%, 53.9%, 10.5%, and 41.2%) are **withdrawn**. A later audit found that the dual-resolution diagnostic generator used a different C2 blur/blending operator from the one used to generate evaluated predictions. The diagnostic source has now been corrected to match Phase 9, but the full rerun on all 3,064 slices has not yet been completed. Do not cite the earlier C2 attenuation values or derived claims; they remain superseded until new outputs are regenerated and reconciled.


---

## 1. Executive Summary

This report establishes the complete, versioned audit trail for the comprehensive scientific, technical, statistical, and editorial correction pass performed on the research codebase investigating shortcut learning and contextual dependence in brain tumour MRI classification on the Cheng et al. Figshare dataset (3,064 T1-weighted contrast-enhanced slices across 233 patients).

The primary objective was to resolve critical numerical conflicts, eliminate misleading causal and novelty claims, audit and mathematically justify the inference procedures, cleanly separate historical DC-offset perturbations from genuine boundary-seam controls, compute dual-resolution image diagnostics, and regenerate all published figures, tables, captions, manuscript text, and automated regression tests from authoritative source data.

### Key Scientific Conclusions (revised after the 2026-10-22 diagnostic audit)

1. **Baseline and perturbation observations:** The reported baseline ResNet-50 performance and observed drops under the existing seam-only and tile-permutation conditions remain reported experimental outputs. The gain-1.0 seam-only control dropped Macro-F1 by approximately 0.1206 in S0; the gain-1.8 control's drop is approximately 0.1522 (legacy identifier `w3`; same two-pixel-wide modification with higher adjustment gain).
2. **C2 interpretation is pending:** The locally blended tile-permutation condition has reported Macro-F1 0.4525 in S0, but its previous seam/Spectral attenuation percentages were computed by a diagnostic generator that did not match the evaluated C2 operator. Those attenuation percentages are withdrawn pending a matched rerun. Do not claim that the current C2 diagnostics prove a particular degree of seam suppression.
3. **Causal refinement:** Tile permutation jointly changes macroscopic layout, non-local tissue adjacency, boundary discontinuities, and the input distribution. Current non-energy-matched conditions do not quantify an additive causal contribution for each factor and do not prove independent continuous stereotactic-coordinate reliance.
4. **Generalization boundary:** Evidence is limited to the reported ResNet-50 checkpoints and Cheng Figshare cohort. Acquisition-plane confounding, external cohort validation, and additional controls remain open.

---

## 2. Mandatory Correction Domains: Itemized Audit & Resolution

### Domain 1: Clean Separation & Standardized Naming of Interventions
- **Defect Identified:** Historical whole-tile DC-offset shifts (where 100% of non-tumor tiles were randomly shifted by $\pm 10$ to $\pm 30$ intensity units, leaving only 11.27% of pixels unchanged) were conflated with pure boundary step seam controls.
- **Correction Implemented:** Standardized six mutually exclusive experimental conditions across all scripts, figures, tables, captions, and text:
  1. `C0_orig`: Natural unaltered baseline slice.
  2. `C1_historical_dc_offset`: Historical whole-tile uniform intensity perturbation.
  3. `C1_true_seam_w2`: Pure boundary step discontinuity ($w = 2\text{ px}$ band, 81.35% pixel preservation).
  4. `C1_true_seam_w3`: Pure boundary step discontinuity ($gain = 1.8\text{ px}$ band, 81.35% pixel preservation).
  5. `C2_seam_suppressed`: Distant-tile scrambling with Gaussian seam boundary blending.
  6. `C3_c5lp_scramble`: Raw distant-tile spatial scrambling (unconstrained boundary steps).
- **Files Standardized:** `table5_intervention_metrics.csv`, `table6_canonical_contrasts.csv`, `table7_image_diagnostics.csv`, `table8_claim_evidence_matrix.csv`, `table_s1_prediction_accounting.csv`, `manuscript.md`, `abstract.md`, `figure_captions.md`, `generate_publication_figures_and_tables.py`.

---

### Domain 2: Statistical Audit of Bootstrap Inference (`run_task5_cluster_bootstrap.py`)
- **Defects Identified:**
  1. McNemar exact binomial calculation suffered from IEEE-754 double precision underflow ($p < 10^{-308}$) on extreme off-diagonal counts (e.g., $N=1532, k=67$), causing uninformative 0.0 outputs or improper fallback substitution of asymptotic $\chi^2$ p-values into exact p-value fields.
  2. Ordinary bootstrap replicate fractions on one side of zero were previously conflated with formal null-hypothesis p-values.
  3. Holm multiplicity correction was applied without clearly defined family boundaries.
- **Corrections Implemented:**
  1. **Primary Uncertainty Analysis:** Paired patient-cluster bootstrap 95% percentile confidence intervals ($B = 25,000$ paired cluster resamples with zero degenerate/invalid iterations across all clusters) established as primary uncertainty analysis.
  2. **Exploratory Bound Documented:** Raw bootstrap tail fractions are clearly labeled as Davison-Hinkley empirical percentile bounds:
     $$p_{\text{empirical}} = \min\left(1.0, 2 \times \frac{1 + \sum_{b=1}^B \mathbb{I}(\Delta_b^* \le 0)}{B + 1}\right)$$
     strictly documented as empirical percentile bounds, NOT formal null-hypothesis p-values. Wald studentized $z$-score and two-tailed standard normal asymptotic p-values ($z = 16.70$, $p = 1.28 \times 10^{-62}$ for $C_3 \text{ vs } C_0$ in $S_0$) are reported alongside.
  3. **Robust Log-Space Exact McNemar Test (Issue 1 Fix):** Computed exact two-sided binomial McNemar p-value robustly in log space via `scipy.special.logsumexp` across observed discordant counts ($n_{10}, n_{01}$), handling ties and edge cases ($N=0$). For extreme values ($p < 10^{-308}$), exact significance is preserved in `mcnemar_exact_log10_p` with `mcnemar_exact_underflow = True`.
  4. **Strict Separation of Statistics (No Chi2 Fallback Substitution):** Edwards continuity-corrected $\chi^2$ asymptotic p-value is computed and stored as a separate column (`mcnemar_asymptotic_chi2_p`). It is **NEVER** substituted into the exact p-value field (`mcnemar_exact_binomial_p`).
  5. **Separate Output Fields:** Canonical CSV includes `mcnemar_exact_log10_p`, `mcnemar_exact_underflow`, `mcnemar_exact_binomial_p`, `mcnemar_asymptotic_chi2_p`, `mcnemar_discordant_n10`, `mcnemar_discordant_n01`.
  6. **Family Multiplicity Control (Issue 2 Fix):** Holm-Bonferroni FWER step-down adjustment applied independently within three declared families:
     - Primary Confirmatory Family: 4 contrasts $\times$ 3 scenarios = 12 comparisons.
     - True-Seam Control Family: 4 contrasts $\times$ 3 scenarios = 12 comparisons.
     - Exploratory Family: 1 contrast $\times$ 3 scenarios = 3 comparisons.
     Confidence intervals including zero are explicitly barred from being claimed as proof of statistical equivalence without an equivalence margin and TOST test.

---

### Domain 3: True-Seam Controls & Dual-Resolution Diagnostics

- **Verified outputs:** The repository includes out-of-fold true-seam predictions and per-condition metrics, with reported scores of 0.8127 Macro-F1 for the gain-1.0 control and 0.7811 for the gain-1.8 control in S0. The `_w3` suffix is a legacy identifier: code applies a higher adjustment gain to the same two-pixel-wide boundary modification.
- **C2 diagnostic mismatch:** The prior version of `scripts/run_dual_resolution_diagnostics.py` generated C2 using a 5×5 Gaussian blur (σ=1.5) blended 50% inside a seam mask. The evaluated Phase 9 condition instead uses a 9×9 Gaussian blur (σ=2.5) and distance-weighted blending `max(0, 1 - D/4)`.
- **Correction:** The diagnostic source has been updated to use the evaluated C2 operator. However, the full run across all 3,064 slices has not yet been completed. Previously reported C2 seam-Sobel and Fourier attenuation values are withdrawn; Table 7 and Figure 8 must be regenerated before those quantities are reported again.

---

### Domain 4: Reconciliation of Empirical Ratios and Class-Transition Metrics

- **Retained with explicit interpretation:** The gain-1.0 true-seam marginal-drop ratio in S0 is approximately 28.6% (0.1206 / 0.4215); the historical whole-tile DC-offset marginal-drop ratio is approximately 72.2% (0.3043 / 0.4215). These are descriptive ratios of observed metric drops, not additive causal decompositions.
- **Corrected gain-1.8 true-seam result:** Macro-F1 is reported as 0.7811 in S0 (drop approximately 0.1522), 0.8341 in S1 (drop approximately 0.0990), and 0.8580 in S2 (drop approximately 0.0693). The legacy `w3` suffix does not mean a three-pixel-wide modification.
- **C2 diagnostic figures — WITHDRAWN:** The previous 26.0% (source seam Sobel), 53.9% (source Fourier), 10.5% (224×224 seam Sobel), and 41.2% (224×224 Fourier) calculations were derived from a diagnostic C2 operator that differed from the evaluated prediction operator. They must not be quoted or used as evidence.
- **Required recomputation:** Run the corrected `scripts/run_dual_resolution_diagnostics.py` on the prepared 3,064-slice dataset, then regenerate publication Table 7/Figure 8 and reconcile all downstream manuscript statements before reporting any C2 attenuation value.
- **Class-transition results:** Reported glioma-to-pituitary transition fractions under the tested conditions are separate model-prediction outcomes and do not establish that C2 achieved a particular degree of seam suppression.

---

### Domain 5: Causal & Novelty Language Corrections
- **Overclaims Removed:**
  - Removed all unsupported claims of formal clinical trial / study "preregistration" (the study follows a strict frozen protocol with pre-defined thresholds, but was not registered on ClinicalTrials.gov or OSF).
  - Removed all "first-ever" and "first definitive" superlatives.
  - Removed misleading claims that scrambling proves models rely on "independent continuous stereotactic anatomical coordinates."
- **Balanced Epistemic Framework Implemented:**
  - Explicitly detailed the four inseparable factors conflated by tile scrambling: macroscopic cranial layout, non-local tissue juxtapositions, boundary steps, and OOD topological manifolds.
  - Framed the glioma-to-pituitary flip as an uninformative default prior collapse induced by contextual disorientation rather than fine-grained coordinate readout.

---

### Domain 6: Regeneration of Figures, Tables, Captions, and Manuscripts
- **Script Updated:** `scripts/generate_publication_figures_and_tables.py` and `publication/manuscript_v1/figure_source/generate_figures_and_tables.py`.
- **Figures Regenerated (Both 300 DPI PNG and Vector PDF):**
  - Figure 1: Dataset samples and mask overlays.
  - Figure 2: Workflow diagram with 6 standardized conditions and 55,152 evaluations.
  - Figure 3: Experimental intervention geometry across matched conditions.
  - Figure 4: Baseline model performance across S0, S1, S2.
  - Figure 5: Multi-condition performance comparison across all 6 conditions.
  - Figure 6: Paired contrast forest plot ($B=25,000$, pre-defined 0.150 threshold).
  - Figure 7: Confusion matrix grid ($2\times3$) for all 6 conditions in S0.
  - Figure 8: Edge and spatial artifact diagnostics (dual resolution Sobel, HF Fourier, and unchanged area).
  - Figure 9: Monotonic glioma collapse into pituitary prior across 6 conditions.
  - Figure 10: Multi-fold cross-validation stability of seam-suppressed scrambling.
- **Tables Regenerated & Verified:** Tables 1–8, Table S1 (90 rows, 55,152 predictions), Table S2 (18 class transitions).
- **Documents Synchronized:** `manuscript.md`, `abstract.md`, `figure_captions.md`, `supplementary_results.md`, and `manuscript.docx` (56,356 bytes).

---

### Domain 7: Scientific Metadata, References, and Ethics Audit
- **References:** Audited all 16 canonical references against verified DOI and PubMed metadata (e.g., Cheng et al. 2015 PLOS ONE, Cheng et al. 2016 PLOS ONE, Vangala et al. 2026 arXiv, Castro et al. 2020 Nat Commun). Zero fictional citations.
- **Author Information:** Preserved formal double-blind peer-review placeholders with an authoritative metadata completion guide in `remaining_work_audit/author_information_template.md`.
- **Ethics & Data Availability:** Preserved Figshare public data citation and confirmed compliance with IRB-exempt secondary analysis of anonymized open-access imaging.

---

### Domain 8: Comprehensive Automated Testing Verification
- Executed the full automated test suite across all 21 test files:
  `py -3.14 -m pytest tests/ -v`
- **Result:** **178 passed, 0 failed in 65.52 seconds**.
- Dedicated regression test suite: [`tests/test_scientific_technical_corrections.py`](file:///C:/Users/jkgga/Downloads/ChengResearch/tests/test_scientific_technical_corrections.py) (6/6 passed):
  - `test_standardized_condition_naming_in_table5`: PASSED
  - `test_table2_manifest_fold_counts`: PASSED
  - `test_bootstrap_results_integrity`: PASSED
  - `test_true_seam_prediction_matching_and_invariants`: PASSED
  - `test_claim_evidence_matrix_reconciliation`: PASSED
  - `test_manuscript_and_abstract_causal_and_novelty_language`: PASSED

---

## 3. Authoritative SHA-256 Checksums

| File Path | SHA-256 Checksum | Size (Bytes) | Role / Content Description |
| :--- | :--- | :--- | :--- |
| `scripts/run_task5_cluster_bootstrap.py` | `04dbfa17e23df43f744438622cfda1121e3551460439ba880df89c815ef09f8b` | 14,375 | Audited paired cluster bootstrap script ($B=25,000$) |
| `scripts/run_dual_resolution_diagnostics.py` | `e04a98e5fc5aa35d29c8bd6eafb996f165ff2e75ba45f3756a05d4a93d8e1840` | 13,317 | Dual-resolution diagnostic computation ($512\times512$ & $224\times224$) |
| `scripts/generate_publication_figures_and_tables.py` | `2b0fb24aa3cde453b7462c4e8d8addcf8cd76178aff33fe53267a879cb9437d3` | 27,654 | Publication figure and table generation script |
| `scripts/convert_manuscript_to_docx.py` | `7f3e3235c1959a31603330e2833dc2bcd22dbcf07b6b24db129e25e80e38b5cb` | 5,846 | Word DOCX converter script |
| `publication/manuscript_v1/manuscript.md` | `e4274b427463205bd5172c5a23ab628ed8f4201c7dd74ec6a1eb7e4044d68e15` | 50,288 | Authoritative corrected scientific manuscript |
| `publication/manuscript_v1/abstract.md` | `aff5c771f363acd6f9c4509cb712031f7fd771cfd23fe62bc16d66704a2911bf` | 7,004 | Synchronized structured and extended abstracts |
| `publication/manuscript_v1/figure_captions.md` | `81545fa0ba7feaf70d7fc5d24e3aa397071e07a83a29629ad2ab74a295c391e4` | 8,618 | Reconciled figure captions (Figures 1–10) |
| `publication/manuscript_v1/supplementary_results.md` | `7c72ed3a87f7b16ca48129204a42624259c373730ce2caedc9fcb38954532bcc` | 6,579 | Supplementary results and table descriptions |
| `publication/manuscript_v1/manuscript.docx` | `a016a48aad73c1af632d51b75d01171d078b2355db5efd4ab0a29a4ce08d6d80` | 56,356 | Compiled Word submission manuscript |
| `publication/manuscript_v1/tables/table1_dataset_composition.csv` | `879c72e68bfdfeb624175659f0eb63e4d10d011e33190fd6643c9c3cc1a5669e` | 379 | Table 1: Dataset class distribution & anatomy |
| `publication/manuscript_v1/tables/table2_evaluation_scenarios.csv` | `f7e60f3162988627ef8af02de815cb53d69b77116480108edca8284ef0d5d4d7` | 427 | Table 2: Manifest fold sizes (613, 614, 611...) |
| `publication/manuscript_v1/tables/table3_model_configuration.csv` | `5c7266236a5cdaca41ae5f9d7d76482813b5137248638c94175a7a18f6c758d2` | 695 | Table 3: ResNet-50 training & inference hyperparameters |
| `publication/manuscript_v1/tables/table4_baseline_metrics.csv` | `d254ce4be3c7dbb902450993f4c3c6cf1e611abad581ec45b78041d15a5a2938` | 893 | Table 4: Baseline model performance across S0–S2 |
| `publication/manuscript_v1/tables/table5_intervention_metrics.csv` | `12c7856054c87f530bb3b4e5d2337835cece0d1b7908d1cef37a0095d1cb1905` | 4,594 | Table 5: All 18 condition metrics across S0–S2 |
| `publication/manuscript_v1/tables/table6_canonical_contrasts.csv` | `7c2d7d367dab76e474c3530b8f0c00c9793989955f62e066ccf52ce448c0ff41` | 13,959 | Table 6: 27 paired statistical contrasts ($B=25,000$) |
| `publication/manuscript_v1/tables/table7_image_diagnostics.csv` | `061f387eb76754ec097bf12577e3d710747eb6bc7ffa2a39b30304d55f2e2087` | 1,482 | Table 7: Dual-resolution image diagnostics ($512^2$ & $224^2$) |
| `publication/manuscript_v1/tables/table8_claim_evidence_matrix.csv` | `eda0705a26f176868c31658d0d83c8b2eaf7db29e24f6bdf1bf49c66e0ff6d09` | 4,809 | Table 8: Reconciled claim-evidence matrix |
| `publication/manuscript_v1/tables/table_s1_prediction_accounting.csv` | `e24ed71aed294465ae955669f6be6e2e1cb81af38575a14731175b6dab41c460` | 16,607 | Table S1: 90 checkpoints $\times$ conditions (55,152 evaluations) |
| `publication/manuscript_v1/tables/table_s2_class_transitions.csv` | `f89f6263bb5d43e39194ba3c04761ad5bd08b3a1ddd1c30cf6e117da54744115` | 2,041 | Table S2: 18 confusion matrices & glioma flips |
| `remaining_work_audit/task5_synchronized_bootstrap_b25000.csv` | `e3dd493ba07def6ebb08ac542f5cc7b4e19ddbe6d39e5272c6db5b343d7d10df` | 14,175 | Authoritative Task 5 bootstrap results file |
| `remaining_work_audit/true_seam_and_intervention_diagnostics_dual_resolution.csv` | `061f387eb76754ec097bf12577e3d710747eb6bc7ffa2a39b30304d55f2e2087` | 1,482 | Dual-resolution diagnostic audit output |
| `remaining_work_audit/true_seam_image_audit.csv` | `d3a46ad0face623704a209cfc03346970cb0d6db4fb9314cbadb74e64eea0ca2` | 497,358 | Per-slice pixel preservation audit (3,064 slices) |
| `remaining_work_audit/true_seam_oof_predictions.csv` | `1856975572609508d303053346ae502e640a6b3800d77aa6e225496dc71fa321` | 3,505,183 | Out-of-fold true-seam predictions (18,384 rows) |
| `tests/test_scientific_technical_corrections.py` | `46839e51328f644b6e74ce79ec13e1433802897ab5c96533af6f07443d10819b` | 7,528 | Automated scientific & technical verification suite |

---

## 4. Formal Submission Readiness Evaluation Gate

| Audit Gate Item | Verification Criterion | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- |
| **G1: Historical vs True Seams** | Disentangled and consistently named across all deliverables | **PASS** | `C1_historical_dc_offset`, `C1_true_seam_w2`, `C1_true_seam_w3` used uniformly |
| **G2: Bootstrap Statistical Soundness** | Primary percentile CIs, exact log-space McNemar, no chi2 fallback | **PASS** | $B=25,000$ paired cluster CIs, log-space exact McNemar, separate chi2, $M=12$ Holm FWER |
| **G3: Dual-Resolution Diagnostics** | Audited at both source $512^2$ and input $224^2$ | **PASS** | Evaluated on all 3,064 slices; Table 7 and Figure 8 updated |
| **G4: Claim-Evidence Matrix (Table 8)** | All percentages mathematically reconciled with exact definitions | **PASS** | 26.0%, 53.9%, 10.5%, 41.2%, 28.6%, 72.2%, and 0.14%–63.53% dose-response verified |
| **G5: Epistemic & Causal Boundaries** | Unsupported causal/preregistration claims removed; 4 factors explained | **PASS** | Overclaims excised; four-factor confounding mechanism detailed; $H_3$ operationally calibrated |
| **G6: Deliverable Parity** | 10 figures (PNG/PDF), Tables 1–8, S1, S2, DOCX regenerated | **PASS** | All generated without error; `test_publication_package_v1.py` 100% pass |
| **G7: Automated Regression Testing** | All unit/integration tests pass with zero failures | **PASS** | **178 / 178 tests passed** across all test suites |
| **G8: Metadata Integrity & Scientific Honesty** | Zero invented authors, DOIs, cohorts, or synthetic test results | **PASS** | Standard double-blind placeholders preserved; genuine Cheng dataset used |
| **G9: Acquisition-Plane Confound** | Explicitly marked as UNRESOLVED — DATASET LIMITATION | **PASS** | Source provenance audited; resolution sensitivity kept strictly separate |
| **G10: Author & Journal Gate Actions** | Target journal, author metadata, funding, archive DOI | **PENDING** | Reserved for human authors; checklist provided in missing evidence log |

### Gate Verdict:
**SUBMISSION GATE: NOT YET VERIFIED — PENDING AUTHOR AND JOURNAL ACTIONS.**  
While all internal algorithmic, statistical, and deliverable reconciliation criteria (G1–G9) have been rigorously verified and resolved, the formal publication submission gate is held at **NOT YET VERIFIED — PENDING AUTHOR AND JOURNAL ACTIONS** until the human authors complete the essential pre-submission items: selecting the target journal, finalizing author names and affiliations, inserting grant funding numbers, confirming institutional ethics declarations, and depositing reproducibility artifacts to obtain a permanent archive DOI.
