# Formal Pre-Registration: Disentangling Anatomical Context from Edge Artifacts

**Document ID:** `PROPOSED_PREREGISTRATION`  
**Phase:** 8 — Deep Novelty Discovery, Research Redesign & Contribution Validation  
**Date:** 2026-10-17  
**Authoritative Standard:** Preregistered Intervention Protocol for Medical AI Audits  
**Status:** DRAFT PRE-REGISTRATION (Frozen Prior to Execution of Any New Experiments)  

---

## 1. Study Information & Research Questions

### Study Title:
Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers: A Multi-Control Spatial Intervention Study.

### Primary Research Question:
Does the catastrophic performance collapse observed under distant spatial patch scrambling ($\Delta \approx +0.42$ Macro-F1 in $C_{5\text{LP}}$) reflect a true neural network dependency on macroscopic cranial landmark topography, or is it an artifact of out-of-distribution high-frequency tile-seam edge noise?

---

## 2. Hypotheses & Confirmatory Decisions

### Confirmatory Hypotheses:

- **Hypothesis $H_1$ (True Anatomical Layout Reliance):**
  When distant cranial tissue is permuted using a seamless, frequency-matched transformation that strictly holds global mean, global variance, and Sobel high-frequency gradient energy within $\pm 5\%$ of the original unmanipulated image ($I_{\text{orig}}$), the model will maintain a statistically significant Macro-F1 drop:
  $$\Delta_{\text{seamless}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{seamless}}) \ge 0.150$$
  with paired cluster-bootstrap $p < 10^{-10}$.

- **Hypothesis $H_0$ (Artifact Confound Dominance / Refutation):**
  If the observed degradation under patch scrambling was entirely driven by tile-seam edge noise, then eliminating boundary seams will restore performance to near-baseline levels:
  $$\Delta_{\text{seamless}} < 0.030$$
  with the 95% bootstrap confidence interval spanning zero.

### Exploratory Analyses:
1. Per-class sensitivity: Testing whether glioma-to-pituitary diagnostic inversion persists when tile seams are removed.
2. Anatomical compartment stratification: Testing whether extra-axial tumors (pituitary adenomas and meningiomas) exhibit greater layout sensitivity than intra-axial gliomas.
3. Frequency-band decomposition: Evaluating performance degradation across low-frequency spatial phase randomization versus high-frequency phase randomization.

---

## 3. Dataset Characteristics & Leakage Prevention

### Dataset Cohort:
- **Source:** Jun Cheng Brain Tumor Dataset, Figshare identifier `1512427` (v5).
- **Inclusion:** All 3,064 2D T1-contrast-enhanced MRI slices ($512 \times 512$ native resolution downsampled to $224 \times 224$).
- **Patient Population:** 233 distinct patient identifiers verified against metadata.
- **Diagnostic Classes:**
  - Class 0: Meningioma ($n=708$)
  - Class 1: Glioma ($n=1,426$)
  - Class 2: Pituitary Adenoma ($n=930$)

### Leakage-Free Splitting:
- All evaluations will strictly utilize the pre-existing 5-fold cross-validation splits under:
  - **Scenario $S_0$ (Primary):** Strict patient-grouped split (233 clusters).
  - **Scenario $S_1$ (Sensitivity):** Near-duplicate candidate groups formed at SSIM $\ge 0.80$.
  - **Scenario $S_2$ (Sensitivity):** Near-duplicate candidate groups formed at SSIM $\ge 0.75$.
- No model retraining or parameter updates will occur during evaluation. All predictions are generated using the 15 frozen ResNet-50 checkpoints.

---

## 4. Intervention Design & Artifact Controls

### Condition Suite:
1. **$I_{\text{orig}}$ (Baseline Control):** Unmodified original test slice.
2. **$I_{\text{C5LP}}$ (Tile-Scrambled Comparator):** Permuting $16 \times 16$ distant tiles with bit-exact mean ($39.79$) and variance ($40.93$) preservation (Phase 6 condition; $+97.9\%$ Sobel gradient energy).
3. **$I_{\text{seamless}}$ (Primary Test Condition):** Distance-preserving spatial permutation with boundary seam suppression via:
   - Multiresolution wavelet sub-band shuffling (permuting spatial coefficients in low-frequency approximation sub-bands while retaining high-frequency horizontal/vertical/diagonal detail bands); OR
   - Poisson seamless blending across tile boundaries to eliminate step-edge contrast gradients.
4. **$I_{\text{phase\_matched}}$ (Negative Artifact Control):** High-frequency edge noise injection without macroscopic spatial permutation (introducing synthetic grid lines matching the Sobel energy of $C_{5\text{LP}}$ onto unpermuted images).

### Invariance Verifications Required Prior to Evaluation:
- **Tumor Core Invariance:** Exactly 0 pixels altered within the primary tumor mask ($100\%$ bit-identity).
- **Global Radiometric Invariance:** Global mean intensity and standard deviation must match $I_{\text{orig}}$ within $\pm 0.5\%$.
- **High-Frequency Invariance:** In $I_{\text{seamless}}$, whole-image Sobel gradient energy must match $I_{\text{orig}}$ within $\pm 10\%$ (suppressing the $+97.9\%$ seam spike observed in $C_{5\text{LP}}$).

---

## 5. Statistical Inference & Decision Rules

### Primary Metric:
- **Macro-Averaged F1 Score (Macro-F1):** Arithmetic mean of per-class F1 scores, unweighted by class prevalence.

### Secondary Metrics:
- Balanced Accuracy, Per-Class F1, McNemar transition $\chi^2$ and p-values, Confusion Matrix error flows.

### Resampling Unit & Bootstrap Protocol:
- **Cluster Bootstrap:** Paired patient-cluster bootstrap with $B=2,000$ replicates, random seed 42.
- In each replicate $b \in \{1, \dots, 2,000\}$, full patient clusters are sampled with replacement. Out-of-fold predictions for all conditions ($I_{\text{orig}}, I_{\text{C5LP}}, I_{\text{seamless}}$) are evaluated concurrently on the exact same patient sample.
- Macro-F1 is recomputed directly from the resampled confusion matrix (avoiding sample-averaging approximations).
- Two-sided 95% bootstrap confidence intervals are computed using the empirical 2.5th and 97.5th percentiles of $\Delta_b$.

### Decision Thresholds:
| Outcome Condition | Statistical Threshold | Scientific Interpretation |
| :--- | :--- | :--- |
| **Full Layout Reliance Confirmed** | $\Delta_{\text{seamless}} \ge 0.250$ AND $95\% \text{ CI} > 0.200$ | Catastrophic collapse is driven almost entirely by cranial layout disruption. Seams play a minor role. |
| **Partial Layout Reliance Confirmed** | $0.080 \le \Delta_{\text{seamless}} < 0.250$ AND $p < 10^{-5}$ | Both cranial layout and edge-seam artifacts contribute significantly to model vulnerability. |
| **Artifact Dominance (Hypothesis Refuted)** | $\Delta_{\text{seamless}} < 0.030$ OR 95% CI spans zero | The previous $C_{5\text{LP}}$ collapse was an artifact of tile-seam edge noise. Neural networks do not rely on cranial layout. |

---

## 6. Falsification & Stopping Rules

1. **Geometry Violation Rule:** If any slice in the generated test set exhibits $>0$ altered pixels within the primary tumor mask, the run must be aborted immediately and regenerated.
2. **Frequency Matching Rule:** If the proposed seamless permutation fails to reduce the Sobel edge-energy spike by at least 70% relative to $C_{5\text{LP}}$, the method is rejected as insufficiently controlled.
3. **Study Abandonment Condition:** If independent search discovers a published paper executing frequency-matched, seamless spatial scrambling on brain MRI with cluster bootstrap, this experiment will be abandoned in favor of Backup Direction A.
