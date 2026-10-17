# Phase 9.1: Intervention Validity Reassessment

**Project:** Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers  
**Audit Phase:** Phase 9.1 Independent Scientific Audit  
**Date:** 2026-10-17  

---

## 1. Executive Summary of Reassessment

The Phase 9 controlled experiment was designed to decouple the high-frequency tile-boundary step discontinuities introduced by patch scrambling from the disruption of macroscopic spatial layout.

This independent audit evaluated:
1. Whether condition $C_1$ strictly isolates seam boundary discontinuities while holding underlying anatomical content stationary.
2. Whether condition $C_2$ meaningfully suppresses boundary seam artifacts without creating fatal out-of-distribution artifacts.
3. Whether global radiometric invariants (mean, variance) and gradient metrics were inappropriately conflated with complete distribution matching.

### Core Verdict
- **Intervention Integrity:** Verified with 100% precision across all 3,064 slices. In all conditions ($C_1, C_2, C_3$), exactly **0 pixels** were altered inside the tumour core and inside the 15-pixel peritumoral margin.
- **Seam-Only Control ($C_1$):** Successfully reproduced the local DC-offset boundary discontinuities of $C_3$ (seam Sobel: $120.58$ vs $129.90$ in $C_3$, high-frequency spectral energy: $2,038.1$ vs $2,597.4$) while leaving the interior anatomical tissue unpermuted.
- **Seam-Suppressed Rearrangement ($C_2$):** Successfully reduced boundary seam Sobel energy from $129.90$ to $76.00$ and suppressed excess high-frequency spectral energy by **$84.9\%$** ($715.37$ vs $2,597.43$).
- **Methodological Caveat:** While $C_1$ and $C_2$ isolate specific operationalized variables, neither intervention reproduces a natural brain MRI distribution. Global metric matching (e.g., mean and standard deviation) must never be conflated with preserving biological plausibility or natural anatomical texture.

---

## 2. Detailed Diagnostic Comparison Across Conditions ($N=3,064$ slices)

| Diagnostic Metric | $C_0$ (Baseline) | $C_1$ (Seam-Only) | $C_2$ (Seam-Suppressed) | $C_3$ (Raw Scramble) | Audit Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Global Mean Intensity** | $39.7875$ | $41.0611$ | $39.5260$ | $39.7875$ | $C_0$ and $C_3$ match to $10^{-6}$; $C_1$ and $C_2$ shift by $< 3.2\%$. |
| **Global Std Intensity** | $40.9263$ | $38.4352$ | $36.3549$ | $40.9263$ | $C_0$ and $C_3$ match exactly; $C_2$ has slight variance reduction due to cross-fading. |
| **Changed Pixel Count** | 0 | 231,734 | 237,003 | 231,861 | Fraction altered: ~88.7% to 90.7% (restricted strictly to distant context). |
| **Mean Absolute Difference** | 0.0000 | 34.8769 | 38.2766 | 40.0244 | Reflects substantial distant-context pixel value displacement in all 3 interventions. |
| **Whole Image Sobel Energy** | $31.4007$ | $56.1376$ | $49.3379$ | $62.7980$ | Step discontinuities drive substantial whole-image edge energy increase in $C_1$ and $C_3$. |
| **Tile Boundary Seam Sobel** | **$31.4755$** | **$120.5791$** | **$76.0016$** | **$129.8955$** | $C_1$ matches $C_3$ seam energy within 7.2%; $C_2$ suppresses excess seam energy by 54.8%. |
| **Tile Interior Sobel Energy** | **$30.8923$** | $25.3936$ | $33.2362$ | **$30.8923$** | Inside $16\times16$ tiles, $C_3$ is bit-for-bit identical to baseline natural brain tissue. |
| **High-Frequency Spectral Energy** | $379.79$ | $2038.10$ | $715.37$ | $2597.43$ | $C_2$ suppresses 84.9% of the artificial high-frequency Fourier energy spike. |
| **Tumour Core Altered Pixels** | **0** | **0** | **0** | **0** | 100% verified invariant across all slices. |
| **15px Margin Altered Pixels** | **0** | **0** | **0** | **0** | 100% verified invariant across all slices. |

---

## 3. Condition $C_1$ (Seam-Only Control) Audit

### 1. Invariance & Specificity
- **Tumour and Margin Protection:** Exactly 0 pixels were altered inside the tumour core and inside the 15-pixel margin mask across all 3,064 slices.
- **Anatomical Placement:** The underlying cranial anatomy in $C_1$ remained strictly stationary. No patches were permuted or translated.
- **Spatial Placement:** The synthetic seams were placed precisely along the identical $16\times16$ grid boundaries used by the distant scrambling intervention.

### 2. Seam Strength & Frequency Content
- **Edge Energy Distribution:** In $C_0$ baseline, seam grid Sobel energy is $31.48$. In $C_1$, seam grid Sobel energy surges to $120.58$, closely tracking the $129.90$ level in $C_3$.
- **High-Frequency Spectral Distribution:** Fourier high-frequency energy rose from $379.79$ to $2,038.10$, capturing $74.8\%$ of the high-frequency spectral spike observed in raw scrambling ($2,597.43$).
- **Conclusion:** $C_1$ is a valid, high-fidelity operationalization of tile-seam edge discontinuities. It establishes that high-frequency grid artifacts alone cause substantial model degradation ($\Delta \approx +0.30$ Macro-F1).

---

## 4. Condition $C_2$ (Seam-Suppressed Spatial Rearrangement) Audit

### 1. Efficacy of Seam Suppression
- **Sobel Boundary Energy:** Reduced from $129.90$ ($C_3$) down to $76.00$ ($C_2$).
- **Fourier High-Frequency Energy:** Reduced from $2,597.43$ ($C_3$) down to $715.37$ ($C_2$). The excess high-frequency energy above baseline was suppressed by **$84.9\%$**.
- **Visual Appearance:** The hard 1-pixel step edges prominent in $C_3$ are visibly smoothed into continuous 4-pixel transition bands in $C_2$.

### 2. Residual Artifacts & Out-of-Distribution Caveats
- **Residual Blur:** Gaussian cross-fading softens boundary transitions but introduces local interpolation blurring along the tile edges.
- **Non-Local Juxtaposition:** While boundary step edges are attenuated, the juxtaposition of anatomically incompatible tissues (e.g., parietal cortex juxtaposed against occipital bone) remains present.
- **Out-of-Distribution Status:** Both $C_2$ and $C_3$ are profoundly out-of-distribution relative to clean clinical brain MRI. The persistence of severe performance degradation in $C_2$ ($\Delta = +0.4808$ in $S_0$) demonstrates that the model is acutely dependent on macroscopic layout, but it also reflects the model's inability to process scrambled anatomical textures even when seams are smooth.

---

## 5. Methodological and Epistemic Principles

1. **Global Radiometric Invariants Are Insufficient:**
   Preserving global mean intensity ($39.7875$) and standard deviation ($40.9263$) between $C_0$ and $C_3$ proves only that the global histogram first and second moments are preserved. It does **not** prove that the joint pixel distribution, natural texture, or spatial autocorrelations are preserved.
2. **Gradient Energy Metrics Are Not Complete Texture Descriptions:**
   Matching or suppressing Sobel energy does not recreate natural MRI edge statistics. Natural anatomical boundaries have non-linear phase alignments and contextual continuity that synthetic blending cannot synthesize.
3. **Operational Disentanglement vs Biological Causality:**
   The experiment successfully demonstrates an operational disentanglement: the classifier degrades under high-frequency seams alone ($C_1$), but degrades even more severely when spatial arrangement is permuted under suppressed seams ($C_2$). This is a property of the convolutional neural network's learned feature representations, not evidence of biological brain tumour mechanisms.
