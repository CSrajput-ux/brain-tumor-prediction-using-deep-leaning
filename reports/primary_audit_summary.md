# Primary Counterfactual Audit Report: Region-Resolved Evidence Analysis

Date: 2026-10-29 (Asia/Kolkata)  
Auditors: Multidisciplinary Research Team (Computer-Vision Engineer, Biostatistician)  
Evaluation Protocols: Sham-Controlled Region Interventions (Core, Immediate, Outer, Remote, Sham)

---

## 1. Executive Summary & Core vs Non-Tumour Evidence

| Dataset | Architecture | Method | Region | Raw Sensitivity (Δ) | Sham-Corrected (τ) | Flip Rate | Wilcoxon p-value | Cohen's d_z |
|---|---|---|---|---|---|---|---|---|
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `core` | 0.0783 ± 0.112 | **0.0563 ± 0.100** | 15.6% | 1.6348e-04 | 0.559 |
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `immediate` | 0.0390 ± 0.075 | **0.0169 ± 0.082** | 8.9% | 0.1313 | 0.205 |
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `outer` | 0.0784 ± 0.106 | **0.0564 ± 0.094** | 15.6% | 2.8760e-04 | 0.595 |
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `remote` | 0.0082 ± 0.031 | **-0.0139 ± 0.064** | 4.4% | 0.1597 | -0.214 |
| **BRISC** | `deit_small_patch16_224` | matched_texture_fill | `sham` | 0.0221 ± 0.053 | **0.0000 ± 0.000** | 11.1% | Ref | Ref |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `core` | 0.0367 ± 0.095 | **0.0517 ± 0.118** | 8.9% | 0.0320 | 0.432 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `immediate` | 0.0089 ± 0.048 | **0.0239 ± 0.062** | 6.7% | 0.0152 | 0.381 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `outer` | 0.0150 ± 0.064 | **0.0301 ± 0.070** | 11.1% | 0.0049 | 0.425 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `remote` | -0.0010 ± 0.017 | **0.0140 ± 0.056** | 6.7% | 0.2815 | 0.249 |
| **BRISC** | `deit_small_patch16_224` | telea_inpaint | `sham` | -0.0150 ± 0.056 | **0.0000 ± 0.000** | 8.9% | Ref | Ref |
| **BRISC** | `resnet50` | matched_texture_fill | `core` | -0.0095 ± 0.090 | **0.0531 ± 0.173** | 24.4% | 0.0950 | 0.304 |
| **BRISC** | `resnet50` | matched_texture_fill | `immediate` | 0.0075 ± 0.027 | **0.0702 ± 0.165** | 22.2% | 0.0252 | 0.421 |
| **BRISC** | `resnet50` | matched_texture_fill | `outer` | -0.0019 ± 0.135 | **0.0608 ± 0.152** | 46.7% | 0.0061 | 0.394 |
| **BRISC** | `resnet50` | matched_texture_fill | `remote` | -0.0189 ± 0.065 | **0.0438 ± 0.172** | 15.6% | 0.6069 | 0.251 |
| **BRISC** | `resnet50` | matched_texture_fill | `sham` | -0.0627 ± 0.168 | **0.0000 ± 0.000** | 33.3% | Ref | Ref |
| **BRISC** | `resnet50` | telea_inpaint | `core` | -0.0006 ± 0.018 | **0.0012 ± 0.024** | 15.6% | 0.7885 | 0.049 |
| **BRISC** | `resnet50` | telea_inpaint | `immediate` | -0.0022 ± 0.015 | **-0.0004 ± 0.021** | 11.1% | 0.8845 | -0.018 |
| **BRISC** | `resnet50` | telea_inpaint | `outer` | -0.0001 ± 0.027 | **0.0017 ± 0.030** | 13.3% | 0.6069 | 0.056 |
| **BRISC** | `resnet50` | telea_inpaint | `remote` | 0.0010 ± 0.006 | **0.0028 ± 0.013** | 2.2% | 0.1885 | 0.219 |
| **BRISC** | `resnet50` | telea_inpaint | `sham` | -0.0018 ± 0.014 | **0.0000 ± 0.000** | 6.7% | Ref | Ref |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `core` | 0.1577 ± 0.238 | **0.1449 ± 0.214** | 8.9% | 3.0881e-08 | 0.669 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `immediate` | 0.0220 ± 0.118 | **0.0093 ± 0.114** | 13.3% | 0.0190 | 0.080 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `outer` | 0.0471 ± 0.090 | **0.0344 ± 0.080** | 8.9% | 0.0014 | 0.425 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `remote` | 0.0190 ± 0.046 | **0.0063 ± 0.064** | 4.4% | 0.7122 | 0.097 |
| **CHENG** | `deit_small_patch16_224` | matched_texture_fill | `sham` | 0.0127 ± 0.074 | **0.0000 ± 0.000** | 4.4% | Ref | Ref |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `core` | 0.1212 ± 0.241 | **0.1282 ± 0.245** | 13.3% | 9.1269e-06 | 0.518 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `immediate` | 0.0143 ± 0.081 | **0.0213 ± 0.095** | 8.9% | 0.0267 | 0.222 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `outer` | -0.0007 ± 0.090 | **0.0063 ± 0.097** | 8.9% | 0.2866 | 0.064 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `remote` | 0.0058 ± 0.029 | **0.0128 ± 0.064** | 2.2% | 0.0801 | 0.196 |
| **CHENG** | `deit_small_patch16_224` | telea_inpaint | `sham` | -0.0070 ± 0.057 | **0.0000 ± 0.000** | 2.2% | Ref | Ref |
| **CHENG** | `resnet50` | matched_texture_fill | `core` | 0.0844 ± 0.132 | **0.0603 ± 0.150** | 31.1% | 0.0173 | 0.396 |
| **CHENG** | `resnet50` | matched_texture_fill | `immediate` | 0.0387 ± 0.103 | **0.0146 ± 0.172** | 22.2% | 0.3294 | 0.084 |
| **CHENG** | `resnet50` | matched_texture_fill | `outer` | 0.0834 ± 0.191 | **0.0592 ± 0.196** | 71.1% | 0.0782 | 0.298 |
| **CHENG** | `resnet50` | matched_texture_fill | `remote` | 0.0003 ± 0.071 | **-0.0238 ± 0.225** | 24.4% | 0.7543 | -0.105 |
| **CHENG** | `resnet50` | matched_texture_fill | `sham` | 0.0241 ± 0.217 | **0.0000 ± 0.000** | 51.1% | Ref | Ref |
| **CHENG** | `resnet50` | telea_inpaint | `core` | 0.0264 ± 0.040 | **0.0311 ± 0.056** | 8.9% | 6.5388e-04 | 0.548 |
| **CHENG** | `resnet50` | telea_inpaint | `immediate` | 0.0079 ± 0.036 | **0.0125 ± 0.050** | 6.7% | 0.0621 | 0.248 |
| **CHENG** | `resnet50` | telea_inpaint | `outer` | 0.0064 ± 0.094 | **0.0111 ± 0.096** | 13.3% | 0.4136 | 0.114 |
| **CHENG** | `resnet50` | telea_inpaint | `remote` | 0.0049 ± 0.014 | **0.0095 ± 0.036** | 2.2% | 0.0950 | 0.262 |
| **CHENG** | `resnet50` | telea_inpaint | `sham` | -0.0046 ± 0.033 | **0.0000 ± 0.000** | 6.7% | Ref | Ref |

---

## 2. Model Architecture Comparison (ResNet-50 vs DeiT-Small)

Differences in sham-corrected sensitivity ($	au_{core}$ and $	au_{margin}$) between CNN and Vision Transformer:
- Evaluates whether Vision Transformers demonstrate greater reliance on remote context or peritumoral margins compared to localized CNN receptive fields.
- Stratified by both inpainting (Method A) and texture fill (Method B).

## 3. Imaging-Plane Stratification (BRISC)

Examining sensitivity variation across Axial, Coronal, and Sagittal slice orientations.
