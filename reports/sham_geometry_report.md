# Contralateral Sham Placement Geometry Audit Report

- **Total Unique QC Slices Evaluated:** 120 (60 Cheng, 60 BRISC)
- **Route 1 (Exact Vertical Midline Reflection):** 27 / 120 (22.5%)
- **Route 2 (Affine Translated Mirrored Contour in Tissue):** 93 / 120 (77.5%)
- **Route 3 (Circular Fallback Patch):** 0 / 120 (0.0%)
- **Contour Template Retention Rate:** 100.0% (120 / 120 slices utilized patient-specific mirrored tumour contours)
- **Mean Sham-to-Core Area Ratio:** 0.9975 +/- 0.0227 (range [0.7525, 1.0000])
- **Mean Template Dice Similarity:** 0.9986 +/- 0.0130 (range [0.8588, 1.0000])
- **Unclipped Exact Parity (Ratio = 1.0000, Dice = 1.0000):** 115 / 120 (95.8%) slices achieved exact pixel-for-pixel contour area parity.
- **Peripheral Calvarial Boundary Masking:** 5 / 120 (4.2%) slices experienced boundary clipping against the tissue mask.

---

## 1. Region Area Characterization & Sham Scaling

Sham controls were geometrically constructed by reflecting the tumour core contour across the vertical midline. As a result, sham perturbation area is matched specifically to the tumour core, while other intervention regions have distinct areas:

| Region | Mean Area (Pixels) | Area Relative to Core Sham | Methodological Rationale & Area Caveat |
|---|---|---|---|
| **Core** ($R_{\text{core}}$) | 1,055 px | 1.00× (1,050 px) | Direct area- and shape-matched control. |
| **Immediate Margin** ($R_{\text{immed}}$) | 648 px | 0.62× | Subtraction of core sham baseline provides conservative control. |
| **Outer Margin** ($R_{\text{outer}}$) | 2,285 px | 2.18× | Perturbation footprint is 2.18× larger; effect size reflects both location and area. |
| **Remote Context** ($R_{\text{remote}}$) | 277 px | 0.26× | Distance-isolated contralateral patch. |

*Area Confounding Note: Because $\Delta_{\text{sham}}$ represents sensitivity to perturbing a core-scale tissue patch, outer-margin sensitivity reflects a composite of spatial location and larger perturbed footprint.*

---

## 2. Tissue Mask Methodology & Limitations

Tissue support masks $S$ were extracted using automated intensity thresholding ($I > 0.05$) combined with morphological closing and largest connected-component selection. Formal multi-atlas clinical skull-stripping was not performed on these public 2D slices. Consequently, near-calvarial cortical slices may intersect skull-adjacent boundaries, leading to the observed boundary clipping.

---

## 3. Detailed Outlier & Boundary Clipping Analysis

Among the 5 clipped slices, 3 occur in Cheng and 2 in BRISC:
1. `brisc2025_test_00003_gl_ax_t1`: Area ratio = **0.7525**, Template Dice = **0.8588** (24.75% area reduction). Large cortical glioma abutting the calvarium; contralateral reflection placed candidate contour near contralateral parietal skull table, where foreground masking excluded 24.75% of non-parenchymal pixels.
2. `brisc2025_test_00396_me_co_t1`: Area ratio = **0.9982**, Template Dice = **0.9991** (0.18% area reduction).
3. `brainTumorDataPublic_1-766__156`: Area ratio = **0.9786**, Template Dice = **0.9892** (2.14% area reduction).
4. `brainTumorDataPublic_1-766__157`: Area ratio = **0.9812**, Template Dice = **0.9905** (1.88% area reduction).
5. `brainTumorDataPublic_1-766__742`: Area ratio = **0.9921**, Template Dice = **0.9960** (0.79% area reduction).

---

## 4. Sensitivity Re-Analysis Excluding Clipped Outliers

To assess the impact of the calvarial-clipped slices, sensitivity re-analyses were conducted across BRISC and pooled cohorts:

| Analysis Scenario | Sample Size (N) | Mean Core Sensitivity (τ) | Wilcoxon Raw p | Inference at α = 0.05 |
|---|---|---|---|---|
| **BRISC DeiT Core (Full Benchmark)** | N = 45 | 0.0517 ± 0.120 | p = 0.0320 | Nominally significant |
| **BRISC DeiT Core (Excl. Outlier 00003)** | N = 44 | 0.0528 ± 0.121 | p = 0.0313 | Nominally significant |
| **BRISC DeiT Core (Excl. Both Clipped)** | N = 43 | 0.0506 ± 0.121 | p = 0.0505 | Not significant at α = 0.05 |
| **Pooled ViT - CNN Diff (Full Cohort)** | N = 90 | +0.0738 ± 0.186 | p = 0.0123 | Nominally significant |
| **Pooled ViT - CNN Diff (Excl. Outlier)** | N = 89 | +0.0746 ± 0.187 | p = 0.0118 | Nominally significant |

**Conclusion:** The estimated mean sensitivity was relatively stable under the reported exclusions ($\tau = 0.0506$ to $0.0528$), although statistical significance was not retained when both clipped BRISC samples were excluded ($p = 0.0505, N=43$).
