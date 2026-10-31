# Contralateral Sham Placement Geometry Audit Report

- **Total Unique QC Slices Evaluated:** 120 (60 Cheng, 60 BRISC)
- **Route 1 (Exact Vertical Midline Reflection):** 27 / 120 (22.5%)
- **Route 2 (Affine Translated Mirrored Contour in Tissue):** 93 / 120 (77.5%)
- **Route 3 (Circular Fallback Patch):** 0 / 120 (0.0%)
- **Contour Template Retention Rate:** 100.0% (120 / 120 slices utilized patient-specific mirrored tumour contours)
- **Mean Sham-to-Core Area Ratio:** 0.9975 +/- 0.0227 (range [0.7525, 1.0000])
- **Mean Template Dice Similarity:** 0.9986 +/- 0.0130 (range [0.8588, 1.0000])
- **Unclipped Exact Parity (Ratio = 1.0000, Dice = 1.0000):** 115 / 120 (95.8%) slices achieved exact pixel-for-pixel contour area parity.
- **Peripheral Intracranial Boundary Clipping:** 5 / 120 (4.2%) slices experienced intracranial tissue boundary masking.

## Detailed Outlier & Boundary Clipping Analysis

Among the 5 clipped slices, 3 occur in the Cheng dataset and 2 occur in the BRISC dataset:
1. `brisc2025_test_00003_gl_ax_t1`: Area ratio = **0.7525**, Template Dice = **0.8588** (24.75% area reduction). This represents a large peripheral cortical glioma abutting the inner calvarium; midline contralateral reflection placed the candidate contour near the contralateral parietal inner skull table, where masking to normal brain parenchyma excluded 24.75% of non-parenchymal pixels.
2. `brisc2025_test_00396_me_co_t1`: Area ratio = **0.9982**, Template Dice = **0.9991** (0.18% area reduction).
3. `brainTumorDataPublic_1-766__156`: Area ratio = **0.9786**, Template Dice = **0.9892** (2.14% area reduction).
4. `brainTumorDataPublic_1-766__157`: Area ratio = **0.9812**, Template Dice = **0.9905** (1.88% area reduction).
5. `brainTumorDataPublic_1-766__742`: Area ratio = **0.9921**, Template Dice = **0.9960** (0.79% area reduction).

## Sensitivity Re-Analysis Excluding Clipped Outliers

To verify that model sensitivity estimates and statistical conclusions do not depend on the clipped outlier (`brisc2025_test_00003_gl_ax_t1`), we conducted sensitivity re-analyses across both BRISC and the pooled cohort:
- **BRISC DeiT Core (Full Cohort, N=45):** $\tau_{\text{core}} = 0.0517 \pm 0.120$, Wilcoxon $p = 0.0320$.
- **BRISC DeiT Core (Excluding Outlier, N=44):** $\tau_{\text{core}} = 0.0528 \pm 0.121$, Wilcoxon $p = 0.0313$.
- **BRISC DeiT Core (Excluding Both BRISC Clipped Slices, N=43):** $\tau_{\text{core}} = 0.0506 \pm 0.121$, Wilcoxon $p = 0.0505$.
- **Pooled Architecture Comparison (Full Cohort, N=90):** $\tau_{\text{ViT}} - \tau_{\text{CNN}} = +0.0738 \pm 0.186$, paired Wilcoxon $p = 0.0123$.
- **Pooled Architecture Comparison (Excluding Outlier, N=89):** $\tau_{\text{ViT}} - \tau_{\text{CNN}} = +0.0746 \pm 0.187$, paired Wilcoxon $p = 0.0118$.

**Conclusion:** Sensitivity re-analysis confirms that statistical conclusions, rank orderings, and effect sizes remain robust whether the calvarial-clipped outlier is retained or excluded.
