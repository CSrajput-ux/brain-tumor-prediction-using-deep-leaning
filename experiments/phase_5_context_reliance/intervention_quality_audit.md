# Phase 5 — Spatial Intervention Quality & Morphological Audit Report

**Phase:** 5 — Targeted Context Reliance and Spatial Intervention Study  
**Date:** 2026-10-17  
**Status:** **AUDITED AND CERTIFIED**  
**Audit Standard:** Causal Intervention Consistency, Exact Spatial Geometry, and Numerical Integrity  
**Evaluated Cohort:** 3,064 whole-slice T1-CE brain MRI slices across 233 unique patients  

---

## 1. Executive Summary & Epistemic Audit

An exhaustive audit of the 2D spatial annotations and derived intervention masks was conducted across all 3,064 evaluation samples.

> [!WARNING]
> ### Epistemic Audit: Available Spatial Information vs Ground Truth
> - **Dataset Reality:** The Cheng dataset provides exclusively whole-slice 2D contrast-enhanced T1-weighted images ($512 \times 512$ uint8) and manual binary contours of the primary lesion (`cjdata.tumorMask`).
> - **Zero Anatomical Ground Truth:** The dataset contains **zero** expert segmentations for brain ventricles, sulcal CSF, skull base, sella turcica, dura mater, cerebral cortex, white matter tracts, or vasogenic edema.
> - **Mandatory Epistemic Label:** Any derived anatomical compartments in Phase 5 are formally designated as **Approximate Image-Space Morphological Compartments**. Claims of discovering biological mechanisms or cellular pathological interactions must not be asserted from image-space pixel manipulations alone.

---

## 2. Quantitative Geometric & Radiometric Verification

Across the 3,064 slices, spatial parameters and intensity distributions were audited from [intervention_manifest.csv](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_context_reliance/intervention_manifest.csv):

| Intervention Region | Mean Area (px) | Area Std (px) | Mean Slice Fraction | Intensity (Mean ± SD) | Parenchymal Reference Match |
|---|---|---|---|---|---|
| **Primary Tumor ($M_{\text{tumor}}$)** | 4,421.7 | 3,618.5 | 1.69% | 88.33 ± 29.15 | Hyperintense (T1-CE Gd uptake) |
| **Perilesional Margin ($M_{\text{margin}}$)** | 4,338.3 | 1,669.1 | 1.65% | 62.98 ± 12.93 | Closely matches brain parenchyma |
| **Contralateral Placebo Focal ($M_{\text{placebo}}$)** | 4,413.4 | 3,593.8 | 1.68% | 71.45 ± 11.20 | Normal contralateral tissue |
| **Contralateral Placebo Margin ($M_{\text{plac\_margin}}$)** | 4,169.4 | 1,609.4 | 1.59% | 67.83 ± 12.87 | Matched within 4.85 intensity units |
| **Distant Context Zone ($M_{\text{distant}}$)** | 253,384.0 | 5,229.0 | 96.66% | Scaled by 0.50 | Peripheral cranial reference frame |
| **Brain Parenchyma ($I > 20$)** | — | — | — | 74.29 ± 10.87 | Baseline tissue benchmark |

### Key Geometric Findings:
1. **Area Matching:** The 15-pixel morphological dilation margin ($M_{\text{margin}}$) has an average area of 4,338 pixels ($1.65\%$ of the image), closely matching the primary lesion area ($1.69\%$).
2. **Contralateral Control Matching:** The placebo margin ($M_{\text{plac\_margin}}$) captures an average of 4,169 pixels ($1.59\%$), achieving near-identical spatial scale to the perilesional margin.
3. **Tumor Separation & Cross-Contamination Prevention:**
   - Tumor vs Placebo Focal overlap: **0 slices** (100% disjoint).
   - In 1,500 midline-adjacent cases, vertical shifting was applied to prevent hemispheric cross-talk (mean shift: 66.5 pixels).
   - In 1,747 cases where a naive 15-pixel dilation of the placebo ring would have impinged upon the true tumor, the true tumor mask was explicitly subtracted from the placebo margin ring ($M_{\text{plac\_margin}} \cap M_{\text{tumor}} = \emptyset$). This guaranteed **zero unintended tumor ablation** in the placebo condition.

---

## 3. Contact Sheet Audit

A high-resolution contact sheet was generated across representative cases from each tumor class:
[spatial_intervention_contact_sheet.png](file:///C:/Users/jkgga/Downloads/ChengResearch/experiments/phase_5_context_reliance/spatial_intervention_contact_sheet.png)

1. **Row 1 (Meningioma, Sample 1):** Dural-based convexity lesion. Perilesional margin cleanly encircles the lesion without encroaching on bone or contralaterally.
2. **Row 2 (Glioma, Sample 100):** Intra-axial parenchymal infiltrative mass. Perilesional margin samples surrounding white matter / putative vasogenic edema zone.
3. **Row 3 (Pituitary, Sample 1500):** Sellar / suprasellar mass. Sits on the midline skull base. Matched placebo is shifted into upper cranial vault; distant context perturbation darkens peripheral calvarium while keeping the skull base and chiasmatic region intact.

---

## 4. Boundary Sensitivity & Infill Analysis

- **Sharp Step Edges ($I_{\text{margin\_removed}}$):** Zeroing the margin creates an artificial high-contrast step discontinuity at both the inner tumor border and outer margin boundary.
- **Feathered Parenchymal Infill ($I_{\text{margin\_feathered}}$):** Using 5-pixel Gaussian feathering with mean parenchymal infill ($74.29$ intensity units) eliminates high-frequency boundary steps.
- **Audit Conclusion:** The comparison between $I_{\text{margin\_removed}}$ and $I_{\text{margin\_feathered}}$ directly reveals whether performance degradation is driven by lost biological margin features or edge-discontinuity artifacts.
