# Primary Counterfactual Audit Report: Region-Resolved Evidence Analysis

Date: 2026-10-29 (Updated 2026-10-30)  
Auditors: Multidisciplinary Research Team (Computer-Vision Engineer, Biostatistician)  
Evaluation Protocols: Sham-Controlled Region Interventions (Core, Immediate, Outer, Remote, Sham)

---

## 1. Executive Summary & Core vs Non-Tumour Evidence

| Dataset | Architecture | Method | Region | Raw Sensitivity (Δ) | Sham-Corrected (τ) | Flip Rate | Raw Wilcoxon p | Holm-Adjusted p | Cohen's d_z |
|---|---|---|---|---|---|---|---|---|---|
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `core` | 0.0783 ± 0.112 | **0.0563 ± 0.100** | 15.6% | 1.6348e-04 | 6.5391e-04 | 0.559 |
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `immediate` | 0.0390 ± 0.075 | **0.0169 ± 0.082** | 8.9% | 0.1313 | 0.2627 | 0.205 |
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `outer` | 0.0784 ± 0.106 | **0.0564 ± 0.094** | 15.6% | 2.8760e-04 | 8.6279e-04 | 0.595 |
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `remote` | 0.0082 ± 0.031 | **-0.0139 ± 0.064** | 4.4% | 0.1597 | 0.2627 | -0.214 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `core` | 0.0367 ± 0.095 | **0.0517 ± 0.118** | 8.9% | 0.0320 | 0.0639 | 0.432 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `immediate` | 0.0089 ± 0.048 | **0.0239 ± 0.062** | 6.7% | 0.0152 | 0.0455 | 0.381 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `outer` | 0.0150 ± 0.064 | **0.0301 ± 0.070** | 11.1% | 0.0049 | 0.0197 | 0.425 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `remote` | -0.0010 ± 0.017 | **0.0140 ± 0.056** | 6.7% | 0.2815 | 0.2815 | 0.249 |
| **BRISC** | `resnet50` | matched_texture_fill | `core` | -0.0095 ± 0.090 | **0.0531 ± 0.173** | 24.4% | 0.0950 | 0.1901 | 0.304 |
| **BRISC** | `resnet50` | matched_texture_fill | `immediate` | 0.0075 ± 0.027 | **0.0702 ± 0.165** | 22.2% | 0.0252 | 0.0755 | 0.421 |
| **BRISC** | `resnet50` | matched_texture_fill | `outer` | -0.0019 ± 0.135 | **0.0608 ± 0.152** | 46.7% | 0.0061 | 0.0246 | 0.394 |
| **BRISC** | `resnet50` | matched_texture_fill | `remote` | -0.0189 ± 0.065 | **0.0438 ± 0.172** | 15.6% | 0.6069 | 0.6069 | 0.251 |
| **BRISC** | `resnet50` | telea_inpaint | `core` | -0.0006 ± 0.018 | **0.0012 ± 0.024** | 15.6% | 0.7885 | 1.0000 | 0.049 |
| **BRISC** | `resnet50` | telea_inpaint | `immediate` | -0.0022 ± 0.015 | **-0.0004 ± 0.021** | 11.1% | 0.8845 | 1.0000 | -0.018 |
| **BRISC** | `resnet50` | telea_inpaint | `outer` | -0.0001 ± 0.027 | **0.0017 ± 0.030** | 13.3% | 0.6069 | 1.0000 | 0.056 |
| **BRISC** | `resnet50` | telea_inpaint | `remote` | 0.0010 ± 0.006 | **0.0028 ± 0.013** | 2.2% | 0.1885 | 0.7540 | 0.219 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `core` | 0.1577 ± 0.238 | **0.1449 ± 0.214** | 8.9% | 3.0881e-08 | 1.2352e-07 | 0.669 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `immediate` | 0.0220 ± 0.118 | **0.0093 ± 0.114** | 13.3% | 0.0190 | 0.0380 | 0.080 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `outer` | 0.0471 ± 0.090 | **0.0344 ± 0.080** | 8.9% | 0.0014 | 0.0042 | 0.425 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `remote` | 0.0190 ± 0.046 | **0.0063 ± 0.064** | 4.4% | 0.7122 | 0.7122 | 0.097 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `core` | 0.1212 ± 0.241 | **0.1282 ± 0.245** | 13.3% | 9.1269e-06 | 3.6507e-05 | 0.518 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `immediate` | 0.0143 ± 0.081 | **0.0213 ± 0.095** | 8.9% | 0.0267 | 0.0802 | 0.222 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `outer` | -0.0007 ± 0.090 | **0.0063 ± 0.097** | 8.9% | 0.2866 | 0.2866 | 0.064 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `remote` | 0.0058 ± 0.029 | **0.0128 ± 0.064** | 2.2% | 0.0801 | 0.1603 | 0.196 |
| **CHENG** | `resnet50` | matched_texture_fill | `core` | 0.0844 ± 0.132 | **0.0603 ± 0.150** | 31.1% | 0.0173 | 0.0691 | 0.396 |
| **CHENG** | `resnet50` | matched_texture_fill | `immediate` | 0.0387 ± 0.103 | **0.0146 ± 0.172** | 22.2% | 0.3294 | 0.6588 | 0.084 |
| **CHENG** | `resnet50` | matched_texture_fill | `outer` | 0.0834 ± 0.191 | **0.0592 ± 0.196** | 71.1% | 0.0782 | 0.2345 | 0.298 |
| **CHENG** | `resnet50` | matched_texture_fill | `remote` | 0.0003 ± 0.071 | **-0.0238 ± 0.225** | 24.4% | 0.7543 | 0.7543 | -0.105 |
| **CHENG** | `resnet50` | telea_inpaint | `core` | 0.0264 ± 0.040 | **0.0311 ± 0.056** | 8.9% | 6.5388e-04 | 0.0026 | 0.548 |
| **CHENG** | `resnet50` | telea_inpaint | `immediate` | 0.0079 ± 0.036 | **0.0125 ± 0.050** | 6.7% | 0.0621 | 0.1864 | 0.248 |
| **CHENG** | `resnet50` | telea_inpaint | `outer` | 0.0064 ± 0.094 | **0.0111 ± 0.096** | 13.3% | 0.4136 | 0.4136 | 0.114 |
| **CHENG** | `resnet50` | telea_inpaint | `remote` | 0.0049 ± 0.014 | **0.0095 ± 0.036** | 2.2% | 0.0950 | 0.1901 | 0.262 |

---

## 2. Patient-Clustered Statistical Inference (Cheng Cohort, N=10 Patients)

Because the 45 Cheng intervention slices originate from 10 distinct patient IDs, intra-patient slice correlation was accounted for by aggregating slice-level sensitivities into patient means:

- **DeiT-Small Core (Method A):**
  - Slice-level ($N=45$): mean $\tau = 0.1282$, Wilcoxon $p = 9.13 \times 10^{-6}$, Holm-adjusted $p = 2.74 \times 10^{-5}$
  - Patient-clustered ($N=10$): patient mean $\tau = 0.1349$, clustered Wilcoxon **$p = 0.0488$**, clustered t-test $p = 0.0534$
- **ResNet-50 Core (Method A):**
  - Slice-level ($N=45$): mean $\tau = 0.0311$, Wilcoxon $p = 6.54 \times 10^{-4}$, Holm-adjusted $p = 1.96 \times 10^{-3}$
  - Patient-clustered ($N=10$): patient mean $\tau = 0.0285$, clustered Wilcoxon **$p = 0.0488$**, clustered t-test $p = 0.0771$
- **Architectural Divergence on Cheng (ViT - CNN):**
  - Slice-level: difference $+0.0971$, Wilcoxon $p = 0.156$
  - Patient-clustered: difference $+0.1064$, clustered Wilcoxon $p = 0.232$, clustered t-test $p = 0.148$ (non-significant within single cohort)
