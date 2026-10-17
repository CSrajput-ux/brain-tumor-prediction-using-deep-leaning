# PHASE 9.2 AUDIT REPORT: MANUSCRIPT READINESS AND SCIENTIFIC CLAIM AUDIT

**Project:** Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers: A Multi-Control Spatial Intervention Study  
**Dataset:** Original Cheng Brain Tumor MRI dataset (Figshare article 1512427; 3,064 2D T1-CE slices, 233 patient clusters, 3 classes: meningioma, glioma, pituitary)  
**Models Audited:** 15 Frozen ResNet-50 checkpoints (Scenarios $S_0, S_1, S_2 \times 5$ folds)  
**Audit Directory:** [experiments/phase_9_2_manuscript_readiness/](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/)  
**Date:** 2026-10-17  
**Gate Decision:** **READY-WITH-LIMITATIONS**  

---

## 1. Executive Summary & Gate Verdict

This audit provides a comprehensive, read-only, evidence-driven pre-manuscript verification of the completed brain MRI spatial intervention study. All underlying code, checkpoint inventories, prediction matrices, bootstrap resamples, and intervention diagnostics were traced from first principles.

### Gate Verdict: READY-WITH-LIMITATIONS

**Justification:**
- **Readiness Criteria Passed:** Data provenance, sample accounting, cross-validation isolation, and pixel-level protected invariants are verified with 100% precision. Statistical contrast estimates, paired cluster bootstraps ($B=2,000$), and Holm-Bonferroni FWER multiplicity adjustments are mathematically sound and reproducible.
- **Mandatory Manuscript Limitations:**
  1. *No Clinical or Biological Causality:* The model's reliance on cranial context reflects deep convolutional inductive biases and dataset class correlations, not biological tumour etiology or human radiologist diagnostic reasoning.
  2. *No Unqualified Causal Proportion:* The "72% explained by seams" statement must be phrased strictly as a descriptive ratio of marginal drops ($\Delta_{C1} / \Delta_{C3} = 72.2\%$), not an additive causal variance decomposition, because intervention effects are non-linear and interactive ($\Delta_{C1} + \Delta_{C2} = 0.785 \gg 0.422$).
  3. *No Broad Generalization Claim:* Findings are established for 2D ResNet-50 models on the Cheng Figshare cohort and must not be extrapolated to 3D volumetric architectures, Vision Transformers, or external multi-center cohorts without future empirical testing.
  4. *No Continuous Stereotactic Coordinate Mapping:* The surge in glioma-to-pituitary flip rate ($0.14\% \to 63.5\%$) proves categorical disorientation relative to skull-base priors, not continuous metric coordinate localization.

---

## 2. Resolution of Prediction Accounting

The audit reconciled the relationship between the 15 frozen checkpoints and the 36,768 saved prediction records in [prediction_accounting.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/prediction_accounting.csv):

### Architectural & Evaluation Structure
1. **Checkpoint Inventory:**
   - 3 Scenarios: $S_0$ (Patient-Disjoint), $S_1$ (Duplicate-Cleaned SSIM 0.80), $S_2$ (Aggressive Grouping SSIM 0.75).
   - 5 Folds per scenario $\implies 3 \times 5 = 15$ frozen ResNet-50 checkpoints.
   - All 15 checkpoints originate from Phase 2 baseline training; their weights and SHA-256 hashes are bit-for-bit identical to authoritative Phase 2 checkpoints.
2. **Out-of-Fold (OOF) Prediction Pipeline:**
   - For each scenario and fold, the corresponding checkpoint evaluated **only its designated held-out test fold**.
   - Held-out test fold sizes across folds 1–5:
     - Fold 1: 618 slices
     - Fold 2: 616 slices
     - Fold 3: 612 slices
     - Fold 4: 610 slices
     - Fold 5: 608 slices
     - **Sum of held-out folds:** $618 + 616 + 612 + 610 + 608 = 3,064$ slices (100% of the dataset).
3. **Absence of Test-Time Ensembling or Leakage:**
   - Checkpoints were evaluated independently. Predictions were never ensembled or averaged across checkpoints.
   - For any slice $i$, exactly one checkpoint per scenario-condition generated its prediction (the checkpoint trained on the other 4 folds).
4. **Exact Total Forward Evaluations:**
   $$\text{Total Records} = 3\text{ scenarios} \times 4\text{ conditions} \times 3,064\text{ out-of-fold slices} = 36,768\text{ predictions}$$
   There are zero duplicated prediction records, zero training-fold evaluations included in test matrices, and zero cross-fold leakage.

---

## 3. Canonical Statistical Contrasts and Multiplicity Audit

Contrasts were recalculated under the single unified convention:
$$\text{signed\_difference\_A\_minus\_B} = \text{Macro-F1}_A - \text{Macro-F1}_B$$
A positive value signifies that condition $B$ produced a performance drop relative to condition $A$.

### Table 1: Canonical Recalculated Contrasts (Available in `canonical_contrasts.csv`)

| Scenario | Contrast ID | Condition A | Condition B | Macro-F1 A | Macro-F1 B | Signed Diff $(A - B)$ | Bootstrap 95% Cl | Fold Std | McNemar $\chi^2$ | $p$-value | Holm FWER Status ($\alpha=0.05$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9333 | 0.5118 | **+0.4215** | $[+0.3734, +0.4726]$ | 0.0939 | 1145.1 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_0$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9333 | 0.6290 | **+0.3043** | $[+0.2547, +0.3510]$ | 0.0901 | 824.1 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_0$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9333 | 0.4525 | **+0.4808** | $[+0.4361, +0.5292]$ | 0.0390 | 1273.9 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_0$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6290 | 0.5118 | **+0.1172** | $[+0.0838, +0.1536]$ | 0.0607 | 170.5 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_0$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4525 | 0.5118 | **-0.0593** | $[-0.0836, -0.0354]$ | 0.0782 | 52.8 | $3.6 \times 10^{-13}$ | REJECT $H_0$ (Significant) |
| **$S_1$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9332 | 0.4884 | **+0.4447** | $[+0.3972, +0.4929]$ | 0.0929 | 1262.2 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_1$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9332 | 0.6094 | **+0.3237** | $[+0.2771, +0.3695]$ | 0.1570 | 920.5 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_1$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9332 | 0.4941 | **+0.4390** | $[+0.3925, +0.4875]$ | 0.0617 | 1233.1 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_1$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6094 | 0.4884 | **+0.1210** | $[+0.0964, +0.1447]$ | 0.0815 | 250.3 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_1$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4941 | 0.4884 | **+0.0057** | $[-0.0102, +0.0219]$ | 0.0472 | 2.38 | 0.123 | FAIL TO REJECT (Not sig.) |
| **$S_2$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9273 | 0.5303 | **+0.3969** | $[+0.3423, +0.4568]$ | 0.0524 | 1068.1 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_2$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9273 | 0.6385 | **+0.2887** | $[+0.2281, +0.3542]$ | 0.0994 | 744.3 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_2$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9273 | 0.5159 | **+0.4114** | $[+0.3565, +0.4691]$ | 0.0703 | 1080.7 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_2$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6385 | 0.5303 | **+0.1082** | $[+0.0801, +0.1351]$ | 0.0879 | 196.0 | $< 10^{-15}$ | REJECT $H_0$ (Significant) |
| **$S_2$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.5159 | 0.5303 | **-0.0144** | $[-0.0337, +0.0039]$ | 0.0430 | 2.20 | 0.138 | FAIL TO REJECT (Not sig.) |

### Key Methodological Insights from Statistical Audit:
1. **Fold-Level Stability:** The standard deviation across folds for $C_2 \text{ vs } C_0$ is remarkably small ($0.039$ in $S_0$, $0.062$ in $S_1$, $0.070$ in $S_2$), proving that the spatial scrambling collapse is not an artifact of an isolated outlier fold.
2. **Contrast $C_3 \text{ vs } C_2$ Directionality:** In $S_0$, $\text{Macro-F1}(C_2) - \text{Macro-F1}(C_3) = -0.0593$. Seam smoothing did not recover performance; $C_2$ experienced an even steeper drop from baseline ($+0.4808$) than raw scrambling ($+0.4215$). In $S_1$ and $S_2$, the difference was statistically indistinguishable from zero ($p=0.123$ and $p=0.138$).
3. **McNemar Test Scope:** McNemar $\chi^2$ tests evaluate paired sample-level classification disagreement symmetry. They confirm highly non-random transition dynamics ($p < 10^{-15}$), but do not replace cluster-bootstrap confidence intervals on Macro-F1.

---

## 4. Intervention Validity and Artifact Audit

Detailed in [intervention_validity_matrix.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/intervention_validity_matrix.csv):

| Condition | Target Modification | Protected Invariant | Seam Sobel Energy | Tile Interior Sobel | Excess HF Fourier Energy Suppressed | Control Validity Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **$C_0$** (Baseline) | None | 100% Intact | $31.48$ | $30.89$ | Baseline ($379.8$) | Reference Benchmark |
| **$C_1$** (Seam-Only) | Tile boundary step noise | Core + 15px Margin (0 altered) | **$120.58$** | $25.39$ | 0% (Spike to $2,038.1$) | **VALID SEAM CONTROL** (matches $C_3$ seam Sobel within 7.2%) |
| **$C_2$** (Seam-Suppressed) | Permuted tiles + 4px cross-fade | Core + 15px Margin (0 altered) | **$76.00$** | $33.24$ | **84.9% Suppressed** ($715.4$) | **VALID OPERATIONAL CONTROL** (seam spike suppressed) |
| **$C_3$** (Raw Scramble) | Permuted tiles (hard edges) | Core + 15px Margin (0 altered) | **$129.90$** | **$30.89$** | Dual Confound ($2,597.4$) | Historical Benchmark |

### Verification of Radiometric Invariants
- **Interior Natural Texture Preservation:** Inside the $16\times16$ tiles, Sobel energy in $C_3$ is bit-for-bit identical to baseline natural brain tissue ($30.892316 \equiv 30.892316$). 100% of the gradient energy spike in tile scrambling is localized to the 1-pixel boundary grid.
- **Fairness of $C_1$ as Seam Control:** $C_1$ matches the boundary Sobel energy of $C_3$ ($120.58$ vs $129.90$) while keeping interior brain anatomy 100% static.
- **Fairness of $C_2$ as Layout Control:** $C_2$ suppresses $84.9\%$ of the high-frequency spectral spike, yet frozen ResNet-50 performance still collapses by $+0.4808$ Macro-F1.

---

## 5. Reassessment of Core Scientific Claims

Audited against [claim_evidence_matrix.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/claim_evidence_matrix.csv):

1. **Synthetic Seams Alone Cause Performance Decline ($H_1$):**
   - **Verdict:** `SUPPORTED`
   - *Evidence:* $C_1$ produces $\Delta \text{Macro-F1} = +0.3043$ ($S_0$, 95% CI: $[0.2547, 0.3510]$, $p < 10^{-15}$). Deep CNNs are fragile to high-frequency grid step edges.
2. **Distant-Context Scrambling Causes Performance Decline ($H_2$):**
   - **Verdict:** `SUPPORTED`
   - *Evidence:* $C_3$ produces $\Delta = +0.4215$ ($S_0$, 95% CI: $[0.3734, 0.4726]$, $p < 10^{-15}$), replicating Phase 6 within 0.001.
3. **Seams Alone Explain the Scrambling Drop ($H_0$):**
   - **Verdict:** `NOT SUPPORTED` (Empirically Refuted)
   - *Evidence:* $C_3 \text{ vs } C_1$ shows scrambling is significantly worse than seams alone ($\Delta = +0.1172, p < 10^{-15}$). Suppressing seams in $C_2$ does not recover performance ($\Delta = +0.4808$).
4. **Independent Spatial-Layout Isolation:**
   - **Verdict:** `PARTIALLY SUPPORTED`
   - *Evidence:* Sensitivity to spatial arrangement is proven beyond seam spikes, but patch permutation also creates non-local tissue juxtapositions and boundary blur.
5. **Specific Skull-Base Coordinate Shortcut:**
   - **Verdict:** `PARTIALLY SUPPORTED`
   - *Evidence:* Glioma-to-pituitary flip rate surges from $0.14\%$ to $63.53\%$ under $C_2$, reflecting categorical disorientation relative to the pituitary skull-base prior. Continuous stereotactic metric mapping was not directly isolated.
6. **External Generalization Beyond Dataset / Model:**
   - **Verdict:** `UNRESOLVED`
   - *Evidence:* Validated exclusively on 2D ResNet-50 checkpoints on Figshare 1512427. Generalization to 3D models, Vision Transformers, or other hospital cohorts requires future research.
7. **Methodological Novelty:**
   - **Verdict:** `SUPPORTED`
   - *Evidence:* Verified against Phase 7 systematic review: 4-condition seam vs layout disentanglement has no precedent in published medical imaging shortcut studies.

---

## 6. Preregistration Fidelity & Integrity Audit

Audited against [preregistration_deviation_log.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/preregistration_deviation_log.md):
- **Model Checkpoints:** Exact 15 frozen checkpoints loaded; zero retraining.
- **Metric & Geometry:** Macro-F1 out-of-fold; 0 pixels altered in tumour core or 15px margin.
- **Resampling:** Patient-level ($S_0$) and duplicate-group-level ($S_1, S_2$) cluster bootstrap ($B=2,000$, seed 42) executed exactly as preregistered.
- **Threshold Adherence:** Practical threshold ($\Delta \ge 0.150$) was locked in Phase 8 prior to Phase 9 execution. Observed $\Delta = +0.4808 \gg 0.150$.
- **Deviations:** Zero protocol violations. All minor report clarifications have been documented.

---

## 7. Deliverables Summary

All 10 required Phase 9.2 deliverables have been compiled in [experiments/phase_9_2_manuscript_readiness/](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/):

1. [PHASE_9_2_READINESS_REPORT.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/PHASE_9_2_READINESS_REPORT.md)
2. [prediction_accounting.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/prediction_accounting.csv)
3. [canonical_contrasts.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/canonical_contrasts.csv)
4. [statistical_audit.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/statistical_audit.csv)
5. [intervention_validity_matrix.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/intervention_validity_matrix.csv)
6. [claim_evidence_matrix.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/claim_evidence_matrix.csv)
7. [preregistration_deviation_log.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/preregistration_deviation_log.md)
8. [reproducibility_manifest.json](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/reproducibility_manifest.json)
9. [manuscript_claims_allowed.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_2_manuscript_readiness/manuscript_claims_allowed.md)
10. `test_results.txt` (via pytest suite)
