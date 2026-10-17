# PHASE 9.1 AUDIT REPORT: INDEPENDENT RESULT, CONTRAST-SIGN AND INTERVENTION-VALIDITY AUDIT

**Project:** Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers: A Multi-Control Spatial Intervention Study  
**Dataset:** Original Cheng Brain Tumor MRI dataset (Figshare 1512427; 3,064 2D T1-CE slices, 233 patient clusters, 3 classes: meningioma, glioma, pituitary)  
**Models Audited:** 15 Frozen ResNet-50 checkpoints (Scenarios $S_0, S_1, S_2 \times 5$ folds)  
**Audit Directory:** [experiments/phase_9_1_independent_audit/](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_1_independent_audit/)  
**Audit Date:** 2026-10-17  
**Gate Assessment:** **PASS-WITH-LIMITATIONS**  

---

## 1. Executive Summary & Audit Verdict

This independent audit rigorously verified the empirical outputs, statistical calculations, contrast signs, image diagnostics, and scientific claims generated during Phase 9.

### Key Audit Findings:
1. **Provenance & Checksum Integrity (PASS):**
   All 20 authoritative files in `experiments/phase_9_seam_spatial_disentanglement/` match their recorded SHA-256 checksums and byte sizes with 100% precision. The 36,768 matched prediction records are complete, unique, and strictly disjoint across folds.
2. **Protected Invariant Verification (PASS):**
   Pixel-level examination of all 3,064 slices across conditions $C_1, C_2,$ and $C_3$ confirms that exactly **0 pixels** were altered within the tumour core or the 15-pixel dilation margin ring.
3. **Statistical Metric Reproduction (PASS):**
   Macro-F1, balanced accuracy, overall accuracy, and per-class metrics recalculated independently from raw predictions match Phase 9 reports with a maximum absolute discrepancy of $3.33 \times 10^{-16}$.
4. **Contrast Sign & Label Reconciliation (AUDIT CORRECTION):**
   The contrast $C_3 \text{ vs } C_2$ ("Sensitivity to Seam Suppression") was reported in Phase 9 with $\Delta = -0.0593$ in $S_0$. Under the canonical formula $\text{Macro-F1}_A - \text{Macro-F1}_B$ ($A = C_2, B = C_3$), this negative sign reflects that $C_2$ (seam-suppressed scramble, $\text{F1}=0.4525$) performed *worse* than $C_3$ (raw scramble, $\text{F1}=0.5118$). Seam smoothing did not recover performance; the drop relative to baseline in $S_0$ was actually $+0.4808$ for $C_2$ versus $+0.4215$ for $C_3$.
5. **Audit of the "72% Explained by Seams" Statement (LIMITATION RESTRICTION):**
   The ratio $\Delta_{\text{Macro-F1}}(C_1) / \Delta_{\text{Macro-F1}}(C_3)$ is $72.20\%$ in $S_0$, $72.80\%$ in $S_1$, and $72.74\%$ in $S_2$. **The audit strictly prohibits interpreting this as a causal proportion of the scrambling effect.** Intervention effects on deep neural networks are non-linear and non-additive: $\Delta_{C1} + \Delta_{C2} = 0.3043 + 0.4808 = 0.7851 \gg 0.4215$. This number is solely a *descriptive ratio of marginal performance drops*.
6. **Multiplicity & Statistical Testing (PASS):**
   Applying Holm-Bonferroni Family-Wise Error Rate (FWER) and Benjamini-Hochberg False Discovery Rate (FDR) adjustments across all 15 contrasts confirms that all primary contrasts ($C_3 \text{ vs } C_0$, $C_1 \text{ vs } C_0$, $C_2 \text{ vs } C_0$, and $C_3 \text{ vs } C_1$) remain statistically significant at $p < 10^{-15}$. The contrast $C_3 \text{ vs } C_2$ is significant in $S_0$ ($p = 3.62 \times 10^{-13}$), but not significant in $S_1$ ($p = 0.123$) or $S_2$ ($p = 0.138$).

---

## 2. Provenance and Checksum Audit

All files in `experiments/phase_9_seam_spatial_disentanglement/checksums.json` were independently hashed:

- Total files verified: 20
- SHA-256 match rate: 100% (20/20)
- Byte-size match rate: 100% (20/20)
- Duplicate sample-condition-checkpoint records: 0
- Manifest sample accounting: 3,064 slices $\times$ 4 conditions $\times$ 3 scenarios = 36,768 records.
- Unique patient clusters: 233 across all scenarios.

---

## 3. Canonical Recalculated Metrics

Metrics independently recomputed using `scikit-learn` from `matched_predictions.csv`:

### Table 1: Canonical Recalculated Metrics (Available in `canonical_metrics_recalculated.csv`)

| Scenario | Condition | Macro-F1 | Balanced Acc | Overall Acc | F1 Meningioma | F1 Glioma | F1 Pituitary |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | $C_0$ (Baseline) | **0.9333** | 0.9362 | 0.9409 | 0.8850 | 0.9610 | 0.9539 |
| **$S_0$** | $C_1$ (Seam-Only) | **0.6290** | 0.6817 | 0.6276 | 0.6598 | 0.5687 | 0.6583 |
| **$S_0$** | $C_2$ (Seam-Suppressed) | **0.4525** | 0.5783 | 0.4847 | 0.6187 | 0.1588 | 0.5800 |
| **$S_0$** | $C_3$ (Raw Scramble) | **0.5118** | 0.6082 | 0.5255 | 0.6389 | 0.3076 | 0.5889 |
| **$S_1$** | $C_0$ (Baseline) | **0.9332** | 0.9336 | 0.9419 | 0.8832 | 0.9648 | 0.9514 |
| **$S_1$** | $C_1$ (Seam-Only) | **0.6094** | 0.6633 | 0.6106 | 0.6347 | 0.5534 | 0.6402 |
| **$S_1$** | $C_2$ (Seam-Suppressed) | **0.4941** | 0.5855 | 0.5085 | 0.6029 | 0.3054 | 0.5741 |
| **$S_1$** | $C_3$ (Raw Scramble) | **0.4884** | 0.5732 | 0.5007 | 0.5985 | 0.3072 | 0.5595 |
| **$S_2$** | $C_0$ (Baseline) | **0.9273** | 0.9230 | 0.9354 | 0.8720 | 0.9550 | 0.9548 |
| **$S_2$** | $C_1$ (Seam-Only) | **0.6385** | 0.7135 | 0.6439 | 0.6620 | 0.5248 | 0.7288 |
| **$S_2$** | $C_2$ (Seam-Suppressed) | **0.5159** | 0.6255 | 0.5385 | 0.6387 | 0.2745 | 0.6345 |
| **$S_2$** | $C_3$ (Raw Scramble) | **0.5303** | 0.6281 | 0.5463 | 0.6546 | 0.3124 | 0.6240 |

Discrepancy with reported values: $\le 3.33 \times 10^{-16}$ across all metrics.

---

## 4. Canonical Recalculated Contrasts & Sign Reconciliation

To eliminate ambiguity, contrasts are reported with explicit mathematical formulas:
- $\text{signed\_difference\_A\_minus\_B} = \text{Macro-F1}_A - \text{Macro-F1}_B$
- $\text{performance\_drop\_B\_relative\_to\_A} = \text{Macro-F1}_A - \text{Macro-F1}_B$

### Table 2: Canonical Recalculated Contrasts (Available in `canonical_contrasts_recalculated.csv`)

| Scenario | Contrast ID | Condition A | Condition B | Macro-F1 A | Macro-F1 B | Signed Diff $(A - B)$ | Bootstrap 95% Cl | McNemar $\chi^2$ | $p$-value | Multiple Testing Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9333 | 0.5118 | **+0.4215** | $[+0.3734, +0.4726]$ | 1145.1 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_0$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9333 | 0.6290 | **+0.3043** | $[+0.2547, +0.3510]$ | 824.1 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_0$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9333 | 0.4525 | **+0.4808** | $[+0.4361, +0.5292]$ | 1273.9 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_0$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6290 | 0.5118 | **+0.1172** | $[+0.0838, +0.1536]$ | 170.5 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_0$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4525 | 0.5118 | **-0.0593** | $[-0.0836, -0.0354]$ | 52.8 | $3.6 \times 10^{-13}$ | REJECT $H_0$ (Holm FWER) |
| **$S_1$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9332 | 0.4884 | **+0.4447** | $[+0.3972, +0.4929]$ | 1262.2 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_1$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9332 | 0.6094 | **+0.3237** | $[+0.2771, +0.3695]$ | 920.5 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_1$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9332 | 0.4941 | **+0.4390** | $[+0.3925, +0.4875]$ | 1233.1 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_1$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6094 | 0.4884 | **+0.1210** | $[+0.0964, +0.1447]$ | 250.3 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_1$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4941 | 0.4884 | **+0.0057** | $[-0.0102, +0.0219]$ | 2.38 | 0.123 | FAIL TO REJECT (Not sig.) |
| **$S_2$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9273 | 0.5303 | **+0.3969** | $[+0.3423, +0.4568]$ | 1068.1 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_2$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9273 | 0.6385 | **+0.2887** | $[+0.2281, +0.3542]$ | 744.3 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_2$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9273 | 0.5159 | **+0.4114** | $[+0.3565, +0.4691]$ | 1080.7 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_2$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6385 | 0.5303 | **+0.1082** | $[+0.0801, +0.1351]$ | 196.0 | $< 10^{-15}$ | REJECT $H_0$ (Holm FWER) |
| **$S_2$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.5159 | 0.5303 | **-0.0144** | $[-0.0337, +0.0039]$ | 2.20 | 0.138 | FAIL TO REJECT (Not sig.) |

### Sign Reconciliation Details for $C_3 \text{ vs } C_2$:
- **In $S_0$:** $\text{Macro-F1}(C_2) - \text{Macro-F1}(C_3) = 0.4525 - 0.5118 = -0.0593$. The negative value signifies that seam-suppressed scramble was actually **worse** than raw scramble by $0.0593$ F1 points. Seam cross-fading did not mitigate the scrambling drop; it exacerbated it in $S_0$.
- **In $S_1$:** $\text{Macro-F1}(C_2) - \text{Macro-F1}(C_3) = 0.4941 - 0.4884 = +0.0057$ ($p=0.123$, non-significant).
- **In $S_2$:** $\text{Macro-F1}(C_2) - \text{Macro-F1}(C_3) = 0.5159 - 0.5303 = -0.0144$ ($p=0.138$, non-significant).
- **Auditor Note on Equivalence:** The non-significant p-values in $S_1$ and $S_2$ indicate that the null hypothesis (equal performance between $C_2$ and $C_3$) cannot be rejected. **This does not prove that $C_2$ and $C_3$ are equivalent.**

---

## 5. Statistical Inference & McNemar Test Clarification

1. **Bootstrap Uncertainty:**
   The cluster bootstrap ($B=2,000$) provides confidence intervals for the paired differences in Macro-F1. All reproduced confidence intervals matched the reported Phase 9 intervals within expected numerical resampling tolerance ($< 0.003$).
2. **McNemar Tests vs Macro-F1 Intervals:**
   McNemar tests evaluate paired sample-level classification disagreement:
   $$\chi^2 = \frac{(|n_{10} - n_{01}| - 1)^2}{n_{10} + n_{01}}$$
   McNemar test evaluates whether discordant sample transitions between condition $A$ and condition $B$ are symmetric. It is an exact test of sample-level prediction flip asymmetry, **not a substitute for Macro-F1 confidence intervals.**

---

## 6. Audit of the "72% Explained by Seams" Statement

Phase 9 states:
> *"Synthetic boundary discontinuities alone account for ~72% of the total scrambling decline."*

### Recalculation:
- $S_0$: $\frac{\Delta_{\text{Macro-F1}}(C_1)}{\Delta_{\text{Macro-F1}}(C_3)} = \frac{0.3043}{0.4215} = 72.20\%$
- $S_1$: $\frac{0.3237}{0.4447} = 72.80\%$
- $S_2$: $\frac{0.2887}{0.3969} = 72.74\%$

### Critical Audit Mandate:
1. **Descriptive Ratio Only:** The 72% figure is strictly a descriptive arithmetic ratio between two marginal performance declines.
2. **Prohibition of Causal Interpretation:** Deep convolutional networks are highly non-linear feature extractors. The degradation caused by seams and the degradation caused by spatial rearrangement are non-additive:
   $$\Delta_{C1} + \Delta_{C2} = 0.3043 + 0.4808 = 0.7851 \gg 0.4215 (\Delta_{C3})$$
   Because the sum of marginal effects is 1.86 times the raw scrambling effect, the two interventions exhibit substantial non-linear interaction. It is mathematically invalid to interpret $72\%$ as a "proportion of causal variance explained."
3. **Requirement:** Any future manuscript or report must clearly phrase this as: *"The seam-only control produced a performance decline whose magnitude was 72% as large as the original scrambling decline,"* explicitly noting that intervention effects are interactive.

---

## 7. Intervention Validity Summary

(See full audit in [intervention_validity_reassessment.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_9_1_independent_audit/intervention_validity_reassessment.md))

1. **Condition $C_1$ (Seam-Only):**
   - Successfully introduced boundary discontinuities matching $C_3$ seam Sobel energy within 7.2% ($120.58$ vs $129.90$).
   - Kept interior anatomical content 100% static.
   - Preserved 100% of tumour core and margin pixels (0 altered).
2. **Condition $C_2$ (Seam-Suppressed Scramble):**
   - Suppressed boundary seam Sobel energy by $54.8\%$ and excess high-frequency spectral energy by $84.9\%$ ($715.37$ vs $2,597.43$).
   - Preserved 100% of tumour core and margin pixels (0 altered).
   - Produced residual blurring along tile borders due to cross-fading, which is an expected consequence of spatial smoothing.

---

## 8. Claim-Evidence Matrix

| Claim ID | Claim Summary | Audit Status | Key Empirical Basis & Limitation |
| :---: | :--- | :---: | :--- |
| **CLM_1** | Historical Scrambling Reproduction | **SUPPORTED** | $C_3 \text{ vs } C_0$ drop matches Phase 6 within 0.001 across $S_0, S_1, S_2$. |
| **CLM_2** | Sensitivity to Synthetic Seams ($H_1$) | **SUPPORTED** | $C_1$ produces $\Delta = +0.3043$ ($p < 10^{-15}$) with 0 tumour/margin pixels altered. |
| **CLM_3** | Sensitivity to Seam-Suppressed Rearrangement ($H_2$) | **SUPPORTED** | $C_2$ produces $\Delta = +0.4808 \gg 0.150$ ($p < 10^{-15}$). Spatial disruption causes collapse even without seam spikes. |
| **CLM_4** | Seams Alone Explain the Entire Decline ($H_0$) | **NOT_SUPPORTED** | Decisively refuted. Scrambling is significantly worse than seams alone ($C_3 \text{ vs } C_1 = +0.1172, p < 10^{-15}$). |
| **CLM_5** | Pure Anatomical Context Isolation | **PARTIALLY_SUPPORTED** | While layout reliance is confirmed, tile-scrambling also disrupts high-order textures and spatial frequencies. |
| **CLM_6** | Specific Skull-Base Coordinate Reliance | **PARTIALLY_SUPPORTED** | Supported by massive glioma-to-pituitary flip rate ($0.14\% \to 63.5\%$), but continuous stereotactic mapping was not isolated. |
| **CLM_7** | Methodological Novelty | **SUPPORTED** | Systematic review verified that 4-condition seam vs layout disentanglement has no direct precedent in medical imaging shortcuts. |

---

## 9. Final Gate Decision: PASS-WITH-LIMITATIONS

### Justification:
- **PASS Criteria Met:** All provenance checksums, sample accounting, prediction matrices, metric recalculations, and cluster bootstrap confidence intervals reproduced with complete fidelity.
- **Limitations Identified & Locked:**
  1. The "72% explained by seams" statement must be restricted to a descriptive ratio of marginal declines, not a causal variance decomposition.
  2. Contrast signs for $C_3 \text{ vs } C_2$ must be documented with explicit reference to condition ordering: seam smoothing exacerbated the decline in $S_0$ and showed null differences in $S_1$ and $S_2$.
  3. Non-significance in $S_1$ and $S_2$ for $C_3 \text{ vs } C_2$ must not be claimed as proof of equivalence.

The empirical data are solid, reproducible, and ready for publication with the documented epistemic boundaries.
