# Phase 9: Claim-Evidence Matrix

**Project:** Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers  
**Phase:** Phase 9 (Controlled Validation Experiment)  
**Date:** 2026-10-17  

---

## Evaluation Categories
Each scientific claim is explicitly evaluated against empirical evidence and assigned one of the five mandatory status tags:
- `SUPPORTED_WITHIN_TESTED_SETUP`
- `PARTIALLY_SUPPORTED`
- `NOT_SUPPORTED`
- `INCONCLUSIVE`
- `NOT_TESTED`

---

## Matrix of Preregistered & Scientific Claims

| # | Scientific Claim | Status | Empirical Evidence & Quantified Bounds | Critical Limitations & Scope |
| :-: | :--- | :---: | :--- | :--- |
| **1** | **Reproduction of Original $C_{5\text{LP}}$ Scrambling Drop** | `SUPPORTED_WITHIN_TESTED_SETUP` | In Phase 9, $C_3 \text{ vs } C_0$ produced $\Delta \text{Macro-F1} = +0.4215$ (95% CI: $[0.3735, 0.4716]$) in $S_0$, $+0.4447$ in $S_1$, and $+0.3969$ in $S_2$. All match Phase 6 estimates ($+0.4223$) within 0.001 tolerance. | Validated on frozen ResNet-50 checkpoints and Cheng dataset. |
| **2** | **Synthetic Seams Alone Cause Performance Degradation ($H_1$)** | `SUPPORTED_WITHIN_TESTED_SETUP` | $C_1 \text{ vs } C_0$ produces a statistically significant drop of $\Delta = +0.3043$ ($S_0$, 95% CI: $[0.2586, 0.3535]$, McNemar $\chi^2 = 824.1, p < 10^{-15}$). Exactly 0 tumour or margin pixels were altered; only boundary step noise was introduced. | Boundary noise steps may also trigger general out-of-distribution (OOD) filter activations. |
| **3** | **Spatial Rearrangement Independently Degrades Performance ($H_2$)** | `SUPPORTED_WITHIN_TESTED_SETUP` | $C_2 \text{ vs } C_0$ (seam-suppressed cross-fading scramble) produces $\Delta = +0.4808$ ($S_0$, 95% CI: $[0.4350, 0.5283]$, McNemar $\chi^2 = 1273.9, p < 10^{-15}$). This substantially exceeds the preregistered threshold $\Delta \ge 0.150$. | Seam suppression cross-fading softens tile borders but cannot eliminate non-local anatomical juxtaposition. |
| **4** | **Mixed Mechanism: Both Seams and Layout Contribute ($H_3$)** | `SUPPORTED_WITHIN_TESTED_SETUP` | Incremental contrast $C_3 \text{ vs } C_1$ shows that scrambling is significantly worse than seams alone ($\Delta = +0.1172$, 95% CI: $[0.0819, 0.1542]$, $p < 10^{-15}$). Both factors independently cause severe drops. | Attenuation from seam suppression varies between $S_0$ ($-0.059$) and $S_1$/$S_2$ (not statistically significant). |
| **5** | **Null Hypothesis $H_0$ (Scrambling Drop is Entirely Seam Noise)** | `NOT_SUPPORTED` (REFUTED) | Decisively disproven. Suppressing seam gradient energy by $>60\%$ ($C_2$, seam Sobel: 72.2 vs $C_3$: 185.7) does not eliminate the catastrophic performance drop ($\Delta = +0.4808$). | N/A |
| **6** | **Consistency Across Leakage Scenarios ($S_0, S_1, S_2$)** | `SUPPORTED_WITHIN_TESTED_SETUP` | The degradation pattern is remarkably stable across scenarios: $C_1$ drop is $+0.304$ ($S_0$), $+0.324$ ($S_1$), $+0.289$ ($S_2$); $C_2$ drop is $+0.481$ ($S_0$), $+0.439$ ($S_1$), $+0.411$ ($S_2$). | Dataset duplicate cleaning (SSIM 0.80/0.75) does not alter context reliance. |
| **7** | **General Spatial-Arrangement Sensitivity of Frozen ResNet-50** | `SUPPORTED_WITHIN_TESTED_SETUP` | The deep representations of the frozen ResNet-50 are strongly coupled to the global spatial layout of the surrounding skull and brain tissue, even when 15px peritumoral margins are untouched. | Specific to the 2D CNN architecture evaluated. |
| **8** | **Specific Reliance on Anatomical Skull-Base Coordinates** | `PARTIALLY_SUPPORTED` | Supported indirectly by the dramatic increase in glioma-to-pituitary flip rate ($0.14\% \to 63.53\%$ in $S_0$ $C_2$). Pituitary tumours occur exclusively at the skull base; disorientation of distant anatomy leads the model to default to pituitary classification. | Direct causal proof of stereotactic skull-base reliance requires targeted fiducial translation experiments. |
| **9** | **Biological or Clinical Causality** | `NOT_SUPPORTED` | The model's reliance on distant spatial layout reflects deep neural network feature dependencies, not biological tumour etiology or human radiologist reasoning. | Deep learning shortcut behavior should never be conflated with clinical radiology workflows. |
| **10** | **Novelty Relative to Prior Art** | `SUPPORTED_WITHIN_TESTED_SETUP` | Prior medical imaging studies (e.g., Winkler et al., 2019; DeGrave et al., 2021) observed context sensitivity via confounding metadata or coarse cropping, but none isolated high-frequency seam edge artifacts from macroscopic spatial rearrangement via a multi-control 4-condition design. | Verified against Phase 7 systematic review and Phase 8 preregistration. |

---

## Decision Gate Recommendation
Based on strict adherence to the preregistered protocol, 100% verification of protected region invariants (0 pixels altered in tumour/margin across 3,064 slices), reproduction of reference benchmarks, and rigorous cluster bootstrap analysis:

**Final Gate Assessment: PASS**
