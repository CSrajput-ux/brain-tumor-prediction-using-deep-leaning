# Claim Audit: Luminance-Preserved Distant Spatial Scrambling (C5LP)

**Document ID:** `PHASE_6_1_C5LP_CLAIM_AUDIT`  
**Phase:** 6.1 — Claim and Result Sanity Audit  
**Target Intervention:** $C_{5\text{LP}}$ (`I_distant_luminance_preserved`)  
**Date:** 2026-10-17  
**Auditor:** Independent Scientific and Statistical Reviewer  

---

## 1. Mathematical and Algorithmic Reconstruction

The $C_{5\text{LP}}$ intervention was designed to test whether the classifier's performance degradation under distant-context dimming ($C_5$) was caused by global radiometric attenuation or true spatial layout sensitivity.

### Exact Implementation Parameters:
1. **Resolution & Grid:** Original $512 \times 512$ single-channel uint8 MRI slice partitioned into a uniform $32 \times 32$ grid of $16 \times 16$ pixel patches ($1,024$ patches total).
2. **Protected Exclusion Zone:** The primary tumor binary mask $M_{\text{tumor}}$ was dilated by a 15-pixel radius Euclidean structuring element ($31 \times 31$ ellipse kernel) to form $M_{\text{dil15}}$.
3. **Tile Filtering:** A patch was classified as "purely distant" if and only if:
   $$\forall (y, x) \in \text{Patch}_{(i, j)}, \quad M_{\text{dil15}}(y, x) = 0$$
   Across all 3,064 slices, an average of $905.7 \pm 48.2$ patches (out of 1,024) met this criterion.
4. **Deterministic Spatial Permutation:** The array of distant patches was pseudo-randomly permuted using NumPy's `RandomState` seeded deterministically with:
   $$\text{Seed} = (42 + \text{int}(\text{SHA256}(\text{sample\_id})[:8], 16)) \pmod{2^{32}}$$
5. **Reassembly & Scaling:** The permuted patches were written back into their original spatial grid slots, and the resulting slice was converted to 3-channel RGB and resized to $224 \times 224$ via bilinear interpolation for ResNet-50 inference.

---

## 2. Invariant Verification: What is Preserved vs. What is Destroyed

A rigorous audit requires distinguishing between four fundamentally distinct properties:

| Property | Claimed in Phase 6 | Audited Reality | Mathematical Justification & Audit Finding |
| :--- | :---: | :---: | :--- |
| **Global Intensity Statistics** | Exactly Preserved | **VERIFIED EXACT** | Mean intensity and variance are bit-identical ($\Delta \mu = 0.000000, \Delta \sigma = 0.000000$). Global pixel histogram is 100% identical because it is an exact permutation of existing pixel values. |
| **Tumor Core & Margin Integrity** | Strictly Preserved | **VERIFIED EXACT** | $\max(|I_{\text{C5LP}}[M_{\text{dil15}}] - I_{\text{orig}}[M_{\text{dil15}}|) \equiv 0$. Zero pixels in the tumor or 15-pixel margin are altered. |
| **Local Parenchymal Texture** | Assumed Intact within Tiles | **QUALIFIED / PARTIAL** | Texture *inside* each $16 \times 16$ patch is intact. However, patch boundaries introduce **new artificial step discontinuities** across all tile seams. |
| **High-Frequency Gradient Energy** | Unassessed | **DOUBLED (+97.9%)** | Sobel gradient magnitude increases from $18.33 \pm 4.12$ ($I_{\text{orig}}$) to $36.28 \pm 6.81$ ($I_{\text{C5LP}}$) due to artificial grid seams. |
| **Training Distribution Adherence** | Presumed Valid | **VIOLATED (OOD)** | Deep CNNs trained exclusively on natural smooth brain parenchyma encounter unnatural checkerboard block boundaries, which activate edge-detecting convolutional filters across the entire image. |

---

## 3. Claim-by-Claim Scientific Audit

### Claim 1: "The classifier is highly sensitive to C5LP."
- **Audit Verdict:** **`SUPPORTED_WITHIN_TESTED_SETUP`**
- **Evidence:** Across all 3 scenarios, Macro-F1 drops precipitously from $\sim 0.933$ to $\sim 0.512$ ($\Delta \approx +0.42$, $p < 10^{-100}$). This is a reproducible empirical observation.

### Claim 2: "The sensitivity of pituitary classification cannot be explained merely by global radiometric dimming."
- **Audit Verdict:** **`SUPPORTED_WITHIN_TESTED_SETUP`**
- **Evidence:** Phase 5 dimming ($C_5$) reduced brightness by 47.5% and caused an F1 drop of $\approx 0.096$. $C_{5\text{LP}}$ kept brightness 100% constant and produced an F1 drop of $\approx 0.365$. Thus, low-level brightness reduction was not the sole or primary driver of the Phase 5 distant drop.

### Claim 3: "The model relies specifically on cranial landmarks and skull-base coordinates."
- **Audit Verdict:** **`UNRESOLVED` (DOWNGRADED)**
- **Evidence & Critique:** While $C_{5\text{LP}}$ demonstrates that disrupting spatial arrangement outside the lesion degrades predictions, it scrambles *all* distant patches uniformly across both the cranial vault, cerebral cortex, ventricles, and skull base simultaneously. In addition, the massive increase in high-frequency edge artifacts (+97.9% Sobel energy) means the network could be failing due to **out-of-distribution high-frequency edge noise** rather than loss of anatomical landmark coordinates. To specifically claim "skull-base coordinate reliance," an ablation isolating the skull base while leaving the rest of the brain un-scrambled would be required.

### Claim 4: "C5LP establishes a causal anatomical mechanism."
- **Audit Verdict:** **`NOT_SUPPORTED_BY_CURRENT_EVIDENCE` (DOWNGRADED)**
- **Evidence & Critique:** Perturbing pixels in a 2D image and observing CNN prediction changes is a test of model representation, not of human biology or anatomical causation. Deep learning shortcuts are statistical correlations in feature space.

---

## 4. Auditor Conclusion on C5LP

$C_{5\text{LP}}$ is a mathematically clean control for global luminance and contrast, proving that the network is acutely sensitive to spatial structure outside the tumor. However, the Phase 6 report overstated this finding by interpreting it as definitive proof of "skull-base coordinate reliance." The safest scientific interpretation is:
> *"The classifier's predictions depend strongly on the spatial organization of image content outside the perilesional zone, though this sensitivity reflects a combination of global topological arrangement and vulnerability to unnatural high-frequency tile boundary discontinuities."*
