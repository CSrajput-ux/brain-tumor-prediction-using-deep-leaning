# Phase 5.1 Final Spatial Intervention Validity Audit Report

**Phase:** 5.1 — Spatial Intervention Validity Audit  
**Date of Audit:** 2026-10-17  
**Auditor:** Senior Medical-Imaging Robustness Researcher, Statistical Auditor & Causal-Inference Methodologist  
**Target Repository:** Cheng Brain Tumor MRI Classification (`experiments/phase_5_context_reliance/`)  
**Audit Decision:** **`PASS-WITH-LIMITATIONS`**  

---

## 1. Executive Summary & Audit Mandate

An exhaustive, skeptical scientific audit of the Phase 5 "Targeted Context Reliance and Spatial Intervention Study" was conducted. The audit independently evaluated:
1. Cryptographic and provenance integrity of all Phase 5 deliverables and outer-fold checkpoints.
2. Pixel-level geometric fidelity and overlap of all intervention masks across 3,064 MRI slices.
3. Radiometric intensity shifts, boundary gradient step discontinuities, and out-of-distribution confounders.
4. Independent statistical reproduction of all point estimates, 95% paired bootstrap confidence intervals ($B=2,000$), McNemar transitions, and multiplicity corrections.
5. In-depth re-analysis of the pituitary invariance/context sensitivity claim.
6. Methodological validity of perilesional margin suppression and Gaussian infill sensitivity.

### Summary of Audit Outcomes:
- **Reproducibility & Code Verification:** **100.00% VERIFIED.** All point estimates, bootstrap distributions, and transition counts were bit-for-bit reproduced from raw predictions and checkpoints.
- **Lesion Reliance Claim:** **SUPPORTED.** Net Tumor Reliance strictly exceeds the 0.05 margin ($\text{Net} \approx +0.104$, paired CI $[0.079, 0.130]$).
- **Perilesional Margin Claim:** **DOWNGRADED TO PARTIALLY SUPPORTED.** The net margin effect ($\text{Net} \approx +0.023 - 0.028$) failed to reach the pre-registered 0.0300 threshold and is largely explained by boundary-step edge artifacts.
- **Pituitary Distant-Context Claim:** **DOWNGRADED TO PARTIALLY SUPPORTED / UNRESOLVED.** The drop in pituitary accuracy under $C_5$ is real ($F_1: 0.954 \to 0.848$), but is heavily confounded by a **47.5% collapse in global mean image luminance and contrast**, rather than proven anatomical landmark dependency alone.
- **Cellular / Clinical Causality Claims:** **STRICTLY PROHIBITED.** No clinical shortcut or cellular mechanism can be asserted from 2D pixel-level manipulations.

---

## 2. Audit A: Provenance and Checksum Integrity

All 11 required Phase 5 artifacts were audited against recorded cryptographic hashes:
- **Deliverables Check:** 11/11 files exist and are non-empty.
- **Cryptographic Hashes:** 10/10 hashes in [checksums.json](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_context_reliance/checksums.json) match bit-for-bit.
- **Frozen Outer-Fold Checkpoints:** All 15 ResNet-50 outer-fold checkpoints (5 folds $\times$ 3 scenarios) exist in `experiments/phase_2_baseline/`, are unmodified, and exceed 90 MB.
- **Accounting:** 3,064 evaluation samples, 233 unique patients, and scenario cluster counts (S0: 233, S1: 231, S2: 217) are 100% consistent across manifests and predictions.
- Full log available in [artifact_provenance_audit.csv](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_1_spatial_validity/artifact_provenance_audit.csv).

---

## 3. Audit B: Exact Spatial Geometry & Mask Analysis

Sample-level reconstruction across all 3,064 slices ([distant_intervention_geometry.csv](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_1_spatial_validity/distant_intervention_geometry.csv), [margin_intervention_geometry.csv](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_1_spatial_validity/margin_intervention_geometry.csv)):

1. **Distant Context Perturbation ($C_5$):**
   - **Tumor Preservation:** Exactly 0 tumor pixels were modified in $C_5$ across all 3,064 slices (`tumor_preserved_exact == True`).
   - **Margin Preservation:** Exactly 0 margin pixels were modified in $C_5$ across all 3,064 slices (`margin_preserved_exact == True`).
   - **Changed Footprint:** Altered an average of 81.71% of image pixels (representing 100% of non-zero parenchyma outside the dilated lesion zone).
2. **Perilesional Margin Suppression ($C_3$ vs $C_4$):**
   - **Structuring Element:** Euclidean disk of radius $r = 15$ pixels (`cv2.MORPH_ELLIPSE, (31, 31)`).
   - **Tumor Overlap:** Exactly 0 tumor pixels overlapped with $M_{\text{margin}}$ or $M_{\text{plac\_margin}}$ across all 3,064 samples.
   - **Area Matching:** C3 mean area = 4,338.3 px ($1.65\%$), C4 mean area = 4,169.4 px ($1.59\%$), area ratio = $0.9603 \pm 0.081$.
3. **Feathered Infill Artifact ($C_6$):**
   - Gaussian blurring ($\sigma = 2.0$) of the margin ring broadened the intervention zone from 4,338 px to **7,322.5 px**.
   - As a consequence, an average of **1,390.8 pixels along the tumor boundary** were slightly blended with the parenchymal infill value.

---

## 4. Audit C: Radiometric Shifts & Out-of-Distribution Confounders

Audited from [intervention_image_statistics.csv](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_1_spatial_validity/intervention_image_statistics.csv):

| Condition | Description | Mean Intensity | Intensity Std | Boundary Gradient Step | Confounder Risk |
|---|---|---|---|---|---|
| **$C_0: I_{\text{orig}}$** | Original Slice | 39.79 ± 10.87 | 40.93 ± 8.12 | 72.54 | Benchmark reference |
| **$C_1: I_{\text{tumor\_removed}}$** | Primary Tumor Zeroed | 38.42 ± 10.75 | 40.64 ± 8.15 | **227.48** | Massive boundary discontinuity step |
| **$C_2: I_{\text{placebo\_focal}}$** | Focal Placebo Zeroed | 38.64 ± 10.79 | 40.91 ± 8.11 | 73.44 | Well-matched normal tissue control |
| **$C_3: I_{\text{margin\_removed}}$** | 15px Margin Zeroed | 38.72 ± 10.81 | 40.95 ± 8.14 | **230.10** | Massive dual-boundary discontinuity step |
| **$C_4: I_{\text{margin\_placebo}}$** | Placebo Ring Zeroed | 38.70 ± 10.80 | 40.92 ± 8.13 | **225.13** | Well-matched dual-boundary step control |
| **$C_5: I_{\text{distant\_perturbed}}$** | 50% Distant Dimming | **20.91 ± 6.24** | **22.84 ± 4.51** | 109.21 | **CRITICAL: 47.5% global luminance drop** |
| **$C_6: I_{\text{margin\_feathered}}$** | Feathered Infill | 39.93 ± 10.85 | 40.87 ± 8.11 | **42.39** | Step discontinuity completely eliminated |

### Key Confounder Insights:
1. **$C_5$ Global Radiometric Shift:** Dimming 81.7% of image pixels by 50% cuts the slice mean intensity in half ($39.79 \to 20.91$). CNN feature extractors are sensitive to global contrast shifts; this confounds anatomical context reliance with low-level radiometric distribution shift.
2. **Boundary Discontinuity:** The boundary gradient step in $C_3$ ($230.10$) and $C_4$ ($225.13$) is over $3\times$ higher than the natural tumor border ($72.54$). In $C_6$, the gradient drops to $42.39$. The disappearance of the margin drop in $C_6$ is directly attributable to the removal of this artificial step edge.

---

## 5. Audit D: Independent Statistical Reproduction

Synchronized paired cluster bootstrap resampling ($B = 2,000$ replicates, seed 42) was re-executed:
- **Reproducibility:** All point estimates, 95% CIs, McNemar $b$ and $c$ counts, and p-values matched [paired_contrasts.json](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_context_reliance/paired_contrasts.json) with **0.000000 maximum absolute difference**.
- **Net Tumor Reliance:** $\text{Net}_{\text{tumor}} \in [+0.0987, +0.1045]$, 95% CI lower bound $\ge 0.0749 > 0.0500$. **PASS.**
- **Net Margin Reliance:** $\text{Net}_{\text{margin}} \in [+0.0234, +0.0277]$. While statistically greater than zero ($p < 10^{-4}$), point estimates fall below the pre-registered 0.0300 effect-size threshold. **FAILED STRICT EFFECT-SIZE CRITERION.**
- Full comparison saved in [recomputed_paired_contrasts.json](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_1_spatial_validity/recomputed_paired_contrasts.json).

---

## 6. Audit E: Pituitary Class Re-Analysis

Detailed evaluation from [pituitary_class_reanalysis.csv](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_1_spatial_validity/pituitary_class_reanalysis.csv):
1. **The Effect is Real in Predictions:** Across the 930 pituitary samples, $170 - 195$ cases flip from correct to incorrect under $C_5$, and the mean predicted pituitary probability drops by $-0.201$ to $-0.230$.
2. **Severe Fold Heterogeneity:**
   - In S1, Fold 1 experiences a massive pituitary $F_1$ drop of $+0.328$ ($0.972 \to 0.645$).
   - In contrast, Folds 4 and 5 drop by only $+0.022$ ($0.955 \to 0.932$).
   - In S0, Fold 3 actually shows a slight performance increase ($\Delta = -0.016$).
3. **Competing Hypotheses Evaluation:**
   - *Hypothesis 1 (Anatomical Skull-Base Coordinates):* Plausible, but unisolated.
   - *Hypothesis 2 (Global Contrast / Radiometric Shift):* Highly plausible given the 47.5% drop in global image luminance.
   - *Hypothesis 3 (Boundary Artifacts):* Unlikely to explain the pituitary effect alone, as the expanded tumor zone is large.
   - *Audit Verdict:* The claim that the network specifically uses "skull-base positioning" cannot be certified until a luminance-preserved spatial scrambling control is evaluated.

---

## 7. Audit F & G: Scientific Claims Status

Full claim-by-claim evaluation documented in [claim_evidence_matrix.md](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_1_spatial_validity/claim_evidence_matrix.md):
- Claims 1, 2, 3: **`SUPPORTED_WITHIN_TESTED_SETUP`**
- Claims 4, 5, 6: **`PARTIALLY_SUPPORTED`**
- Claims 7, 9: **`UNRESOLVED`**
- Claim 8 (Biological Causality): **`NOT_SUPPORTED_BY_CURRENT_EVIDENCE`**

---

## 8. Final Gate Decision

**Verdict:** **`PASS-WITH-LIMITATIONS`**

### Summary of Certified Limitations:
1. All Phase 5 data, code, checkpoints, and statistical tables are mathematically reproducible.
2. The model relies substantially on intra-lesional evidence ($\text{Net} \approx 0.10$).
3. The perilesional margin effect is sub-threshold (< 0.03) and reflects boundary-step occlusion artifacts.
4. The distant context drop on pituitary cases is partially confounded with global radiometric attenuation and must not be published as confirmed "skull-base shortcut learning" without a luminance-preserved follow-up control.
