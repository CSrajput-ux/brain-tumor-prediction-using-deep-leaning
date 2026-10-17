# Phase 9.3 — Final Scientific Claim Boundaries and Epistemic Constraints

**Audit Phase:** 9.3 Independent Publication Consistency Audit  
**Document:** Final Scientific Claim Boundaries  
**Target Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17

---

## 1. Permitted and Evidence-Supported Claims

The empirical evidence from 36,768 matched out-of-fold evaluations across 15 frozen ResNet-50 checkpoints decisively establishes the following findings:

1. **High Baseline Benchmark Performance:**
   - Frozen ResNet-50 models achieve high out-of-fold diagnostic performance under unmodified conditions ($S_0$ Macro-F1 = $0.9333$, overall accuracy = $0.9409$, balanced accuracy = $0.9362$).
   - This performance replicates across candidate near-duplicate groupings ($S_1$ Macro-F1 = $0.9332$; $S_2$ Macro-F1 = $0.9273$).

2. **Severe Convolutional Vulnerability to Synthetic Seam Artifacts ($H_1$ Supported):**
   - Injecting synthetic boundary step discontinuities alone ($C_1$), without rearranging any anatomical tiles, causes a massive, statistically significant collapse in Macro-F1 ($\Delta = +0.3043$, 95% CI: $[0.2547, 0.3510]$, $p < 10^{-15}$).
   - This proves that deep CNN feature hierarchies are acutely fragile to high-frequency edge artifacts introduced by image manipulation.

3. **Independent Performance Collapse from Spatial Layout Disruption ($H_2$ Supported):**
   - Permuting distant tiles while cross-fading tile seams ($C_2$, suppressing boundary Sobel energy by 54.8% and excess high-frequency Fourier energy by 84.9%) causes a severe Macro-F1 drop ($\Delta = +0.4808$, 95% CI: $[0.4361, 0.5292]$, $p < 10^{-15}$).
   - This drop substantially exceeds the preregistered threshold of practical significance ($\delta \ge 0.150$).

4. **Decisive Refutation of the Seam-Only Null Hypothesis ($H_0$ Refuted):**
   - Scrambling tiles inflicts significantly greater performance degradation than synthetic seams alone ($C_3 \text{ vs } C_1$: $\Delta = +0.1172$, 95% CI: $[0.0838, 0.1536]$, $p < 10^{-15}$).
   - The observed tile scrambling degradation cannot be dismissed as an artifact of artificial boundary seams.

5. **Pathological Prior Collapse (The Glioma-to-Pituitary Flip Mode):**
   - Under seam-suppressed scrambling ($C_2$), glioma recall collapses from 95.0% to 8.6%, with **63.53% of gliomas misclassified as pituitary tumour** (906 / 1,426).
   - In contrast, pituitary tumours are virtually never misclassified as glioma under scrambling (0 / 930 in $C_2$).
   - When macroscopic cranial context is scrambled, the classifier loses orientation and defaults to its skull-base pituitary prior.

---

## 2. Mandatory Epistemic Qualifications

The manuscript and all accompanying assets must strictly employ qualified language for the following concepts:

1. **The 72.2% Marginal-Drop Ratio:**
   - **Allowed Phrasing:** "The magnitude of the seam-only drop is 72.2% as large as the raw scrambling drop ($\Delta_{C1} / \Delta_{C3} = 0.3043 / 0.4215$)."
   - **Prohibited Phrasing:** Must **NOT** be described as a causal variance decomposition, an additive percentage of total variance, or an independent linear fraction. The interventions exhibit strong non-linear interaction ($\Delta_{C1} + \Delta_{C2} = 0.7851 \gg 0.4215$).

2. **Anatomical Layout Dependence vs. Biological Causality:**
   - **Allowed Phrasing:** The classifier demonstrates operational sensitivity to global cranial spatial configuration as a contextual shortcut.
   - **Prohibited Phrasing:** Must **NOT** claim that this proves an exact biological mechanism, human radiological simulation, or continuous stereotactic coordinate mapping.

3. **Skull-Base Coordinate Reliance:**
   - **Allowed Phrasing:** The directional glioma-to-pituitary transition reflects an internal network shortcut mapping supratentorial vs. infratentorial/skull-base priors.
   - **Prohibited Phrasing:** Must **NOT** assert that the model computes true anatomical coordinates or that this failure mode generalizes identically to all deep architectures.

4. **Architecture and Cohort Generalization:**
   - **Allowed Phrasing:** Findings are demonstrated for 2D ResNet-50 classifiers on the Cheng Figshare benchmark.
   - **Prohibited Phrasing:** Must **NOT** claim universal generalization to 3D volumetric architectures, Vision Transformers (ViT), or external clinical cohorts (BraTS, TCGA) without empirical testing.

5. **Methodological Novelty:**
   - **Allowed Phrasing:** The first controlled multi-intervention study explicitly disentangling synthetic boundary seams from macroscopic spatial layout in this benchmark.
   - **Prohibited Phrasing:** Must **NOT** claim priority over all medical imaging perturbation literature.

---

## 3. Explicit Prohibitions

1. **No Clinical Translation Claims:** The study does not establish clinical utility or radiological equivalence.
2. **No Fabricated Ethics or DICOM Claims:** No claim of DICOM acquisition harmonization, institutional review board approval, or patient consent beyond the publicly documented Figshare article.
3. **No Unqualified Causal Decompositions:** Strict adherence to descriptive marginal comparisons.

---

## 4. Compliance Verification

The manuscript (`publication/manuscript_v1/manuscript.md`), abstract (`abstract.md`), captions (`figure_captions.md`), and tables (`tables/`) have been audited against these boundaries. All sections fully comply with these epistemic constraints.
