# Preregistration Document: Phase 6 Spatial Controls Study

**Study Title:** Targeted Spatial Control Validation: Disentangling Luminance, Boundary Discontinuity, and Intervention Thickness in Brain MRI Shortcut Learning  
**Date:** 2026-10-17  
**Phase:** 6  
**Status:** PREREGISTERED  
**Protocol Version:** 1.0  

---

## 1. Background and Motivation

Phase 5 identified two prominent findings regarding spatial context reliance in frozen ResNet-50 brain tumor MRI classifiers:
1. Distant context dimming ($C_5$) led to a substantial degradation in pituitary classification performance ($F_1 \approx 0.954 \to 0.848$), while tumor core excision ($C_1$) had virtually no effect ($F_1 \approx 0.954 \to 0.943$).
2. Perilesional margin excision ($C_3$, 15-pixel zero-fill ring) produced a modest Macro-F1 drop ($\Delta \approx +0.038$), but this effect completely vanished under Gaussian-feathered infilling ($C_6$, $\Delta \approx +0.001$).

However, the independent Phase 5.1 audit revealed critical methodological confounds:
- **Global Radiometric Collapse:** $C_5$ dimming reduced whole-slice mean pixel intensity by **47.5%** and standard deviation by **44.2%**, heavily confounding anatomical context reliance with low-level radiometric attenuation.
- **Boundary Discontinuity Artifacts:** $C_3$ zero-filling induced an unnatural boundary gradient step ($230.10 \pm 10.38$) over $3\times$ steeper than natural tumor borders ($72.54 \pm 23.41$), whereas $C_6$ Gaussian blurring altered $1,390 \pm 1,293$ pixels inside the true tumor boundary.
- **Arbitrary Thickness:** The 15-pixel ring (~6.5 mm) lacked a parametric dose-response verification.

Phase 6 preregisters targeted spatial controls to isolate these mechanisms cleanly.

---

## 2. Experimental Conditions

The study evaluates the following conditions across all 3,064 out-of-fold MRI slices:

| Condition Code | Name | Type | Mathematical Definition & Spatial Geometry |
| :--- | :--- | :--- | :--- |
| **C0** | `I_orig` | Reference Baseline | Unmanipulated original 512x512 MRI slice. |
| **C1** | `I_tumor_removed` | Lesion Ablation | Primary segmented tumor core zeroed out: $I \cdot (1 - M_{\text{tumor}})$. |
| **C2** | `I_placebo_focal` | Focal Spatial Control | Matched contralateral focal region zeroed out: $I \cdot (1 - M_{\text{placebo}})$. |
| **C5** | `I_distant_perturbed` | Distant Attenuation | Remote context scaled by 0.50 outside 15px dilated tumor: $I \cdot M_{\text{dil15}} + 0.50 I \cdot (1 - M_{\text{dil15}})$. |
| **C5LP** | `I_distant_luminance_preserved` | Experiment A: Luminance Control | Non-overlapping $16 \times 16$ spatial patch permutation strictly outside $M_{\text{dil15}}$. **Guarantees 0.00% change in global mean and variance.** |
| **C3_r15** | `I_margin_r15_removed` | Margin Ablation (15px) | 15px Euclidean perilesional ring zeroed out: $I \cdot (1 - M_{\text{margin,15}})$. ($= C_3$). |
| **C3NS** | `I_margin_r15_ns_inpaint` | Experiment B: Boundary Control | 15px perilesional ring filled using Navier-Stokes PDE inpainting ($r_{\text{inpaint}}=3$). **Tumor core and distant tissue 100% bit-preserved.** Smooth boundary gradient step. |
| **C4_r15** | `I_margin_r15_placebo` | Placebo Ring (15px) | Contralateral 15px ring zeroed out: $I \cdot (1 - M_{\text{plac\_margin,15}})$. ($= C_4$). |
| **C3_r05** | `I_margin_r05_removed` | Margin Sweep (5px) | 5px perilesional ring zeroed out ($11 \times 11$ ellipse structuring element). |
| **C4_r05** | `I_margin_r05_placebo` | Placebo Ring (5px) | Contralateral 5px ring zeroed out. |
| **C3_r10** | `I_margin_r10_removed` | Margin Sweep (10px) | 10px perilesional ring zeroed out ($21 \times 21$ ellipse structuring element). |
| **C4_r10** | `I_margin_r10_placebo` | Placebo Ring (10px) | Contralateral 10px ring zeroed out. |
| **C3_r20** | `I_margin_r20_removed` | Margin Sweep (20px) | 20px perilesional ring zeroed out ($41 \times 41$ ellipse structuring element). |
| **C4_r20** | `I_margin_r20_placebo` | Placebo Ring (20px) | Contralateral 20px ring zeroed out. |

---

## 3. Preregistered Hypotheses & Primary Contrasts

### Experiment A: Distant Context vs Global Radiometric Shift
- **Primary Contrast:** $\Delta F_{1,\text{Macro}}(C_0, C_{5\text{LP}}) = \text{Macro-F1}(C_0) - \text{Macro-F1}(C_{5\text{LP}})$
- **Target Subclass Contrast:** $\Delta F_{1,\text{Pituitary}}(C_0, C_{5\text{LP}}) = F_{1,\text{Pituitary}}(C_0) - F_{1,\text{Pituitary}}(C_{5\text{LP}})$ vs $\Delta F_{1,\text{Pituitary}}(C_0, C_5)$.
- **Decision Rule:**
  - If $\Delta F_{1,\text{Pituitary}}(C_0, C_{5\text{LP}}) \ge 0.050$ with $95\%$ CI excluding zero, distant anatomical spatial semantics are **SUPPORTED**.
  - If $\Delta F_{1,\text{Pituitary}}(C_0, C_{5\text{LP}}) < 0.030$ or $95\%$ CI spans zero while $C_5$ drops by $\approx 0.106$, the Phase 5 drop is **CONFIRMED AS A RADIOMETRIC ARTIFACT**.

### Experiment B: Perilesional Margin Reliance vs Step Discontinuity
- **Primary Contrast:** $\Delta F_{1,\text{Macro}}(C_0, C_{3\text{NS}}) = \text{Macro-F1}(C_0) - \text{Macro-F1}(C_{3\text{NS}})$
- **Decision Rule:**
  - If $\Delta F_{1,\text{Macro}}(C_0, C_{3\text{NS}}) \ge 0.0300$ (the pre-registered threshold) with $95\%$ CI excluding zero, true perilesional parenchymal reliance is **SUPPORTED**.
  - If $\Delta F_{1,\text{Macro}}(C_0, C_{3\text{NS}}) < 0.0150$ or $95\%$ CI spans zero while $C_{3\_r15}$ drops by $\approx 0.038$, the margin effect is **CONFIRMED AS A BOUNDARY DISCONTINUITY ARTIFACT**.

### Experiment C: Margin Thickness Dose-Response Sweep
- **Primary Contrasts:** Net margin reliance across radii $r \in \{5, 10, 15, 20\}$ pixels:
  $$\text{Net Margin}(r) = \Delta F_{1,\text{Macro}}(C_0, C_{3\_r}) - \Delta F_{1,\text{Macro}}(C_0, C_{4\_r})$$
- **Decision Rule:**
  - Monotonicity test: Evaluate whether $\text{Net Margin}(5) < \text{Net Margin}(10) < \text{Net Margin}(15) < \text{Net Margin}(20)$.
  - Distinguish biological dose-response from step-edge geometry.

---

## 4. Statistical Protocol

1. **Unit of Analysis:** Synchronized paired patient-cluster bootstrap ($B = 2,000$ replicates, random seed 42).
2. **Cluster Grouping:**
   - S0: `patient_id` (233 clusters)
   - S1: `combined_group_id` (231 clusters, SSIM 0.80)
   - S2: `combined_group_id` (217 clusters, SSIM 0.75)
3. **Resampling Synchronization:** For every bootstrap replicate $b$, the exact same resampled clusters are evaluated across all conditions simultaneously.
4. **Primary Outcome:** Macro-F1 across 3 classes (meningioma, glioma, pituitary).
5. **No p-hacking / Equivalence claims:** CIs spanning zero are interpreted strictly as "effect cannot be distinguished from zero within statistical precision," not as proof of zero biological effect.
