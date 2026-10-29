# Secondary Experiments, Replication & Robustness Analysis

Date: 2026-10-29 (Updated 2026-10-30)  
Auditors: Multidisciplinary Research Team (Computer-Vision Engineer, Biostatistician)  
Scope: Architecture Comparison, Method Invariance, Plane Stratification, Tumour Biology Heterogeneity

---

## 1. Architectural Inductive Bias: ResNet-50 (CNN) vs DeiT-Small (ViT)

Hypothesis: Vision Transformers exhibit greater sensitivity to core and margin evidence without increasing remote shortcut dependence.

| Region | Perturbation Method | CNN Sham-Corrected (τ) | ViT Sham-Corrected (τ) | Difference (ViT - CNN) | Raw Wilcoxon p | Holm-Adjusted p | Cohen's d_z |
|---|---|---|---|---|---|---|---|
| `core` | telea_inpaint | 0.0161 ± 0.046 | 0.0900 ± 0.196 | **+0.0738** | 0.0123 | 0.0980 | 0.362 |
| `immediate` | telea_inpaint | 0.0061 ± 0.039 | 0.0226 ± 0.080 | **+0.0166** | 0.1124 | 0.6746 | 0.184 |
| `outer` | telea_inpaint | 0.0064 ± 0.071 | 0.0182 ± 0.085 | **+0.0118** | 0.1732 | 0.8660 | 0.117 |
| `remote` | telea_inpaint | 0.0062 ± 0.027 | 0.0134 ± 0.060 | **+0.0072** | 0.9087 | 1.0000 | 0.114 |
| `core` | matched_texture_fill | 0.0567 ± 0.162 | 0.1006 ± 0.173 | **+0.0439** | 0.0164 | 0.1147 | 0.198 |
| `immediate` | matched_texture_fill | 0.0424 ± 0.171 | 0.0131 ± 0.099 | **-0.0293** | 0.6023 | 1.0000 | -0.140 |
| `outer` | matched_texture_fill | 0.0600 ± 0.176 | 0.0454 ± 0.088 | **-0.0146** | 0.7369 | 1.0000 | -0.072 |
| `remote` | matched_texture_fill | 0.0100 ± 0.203 | -0.0038 ± 0.065 | **-0.0138** | 0.5236 | 1.0000 | -0.064 |

### Clustered Multi-Cohort Inference (Pooled N=90 across 55 Independent Clusters)
Accounting for clustering (10 Cheng patient clusters + 45 independent BRISC cases = 55 clusters):
- **Slice-Level Core Difference (Method A):** $+0.0738$, slice-level Wilcoxon $p = 0.0123$, Holm-adjusted $p = 0.0980$
- **Cluster-Level Wilcoxon Test:** Cluster mean difference $+0.0607$, Wilcoxon **$p = 0.0162$**
- **Cluster-Level One-Sample t-test:** $t = 3.29$, **$p = 0.00177$**
- **Linear Mixed-Effects Model ($N=180$, 55 clusters):** Fixed effect $\beta_{\text{ViT}} = +0.074$ (SE: $0.020$, $z = 3.756$, $p < 0.001$).
Confirms architectural divergence is robust under cluster-level inference.

---

## 2. Perturbation Engine Invariance: Method A (Inpainting) vs Method B (Texture Fill)

Hypothesis: Region sensitivity rank order is generally preserved across edit engines, though localized texture filling introduces edge effects in outer margins.

| Dataset | Region | Method A (Telea) τ | Method B (Texture) τ | Pearson Correlation (r) | Spearman Rank (ρ) | Paired Bias |
|---|---|---|---|---|---|---|
| **CHENG** | `core` | 0.0796 | 0.1026 | **0.748** | **0.541** | +0.0230 |
| **CHENG** | `immediate` | 0.0169 | 0.0119 | **0.264** | **0.270** | -0.0050 |
| **CHENG** | `outer` | 0.0087 | 0.0468 | **-0.053** | **0.031** | +0.0381 |
| **CHENG** | `remote` | 0.0112 | -0.0088 | **0.251** | **0.168** | -0.0199 |
| **BRISC** | `core` | 0.0265 | 0.0547 | **0.300** | **0.332** | +0.0282 |
| **BRISC** | `immediate` | 0.0118 | 0.0435 | **0.068** | **0.250** | +0.0318 |
| **BRISC** | `outer` | 0.0159 | 0.0586 | **0.082** | **0.065** | +0.0427 |
| **BRISC** | `remote` | 0.0084 | 0.0149 | **0.087** | **0.067** | +0.0065 |

---

## 3. Imaging-Plane Stratification (BRISC)

Evaluating regional sensitivity across Axial, Coronal, and Sagittal slice orientations:

| Imaging Plane | Sample Count (N) | Mean Core Sensitivity (τ) | Mean Immediate Margin (τ) | Mean Remote (τ) |
|---|---|---|---|---|
| **Axial** | 15 | **0.0337** | 0.0241 | 0.0137 |
| **Coronal** | 15 | **0.0298** | 0.0127 | 0.0036 |
| **Sagittal** | 15 | **0.0582** | 0.0461 | 0.0178 |

---

## 4. Lesion Boundary Biology & Class Heterogeneity

Comparing infiltrative neoplasms (Gliomas) vs circumscribed extra-axial lesions (Meningiomas) vs sellar lesions (Pituitary):

| Tumour Class | Presumed Boundary Infiltration | Core Sensitivity (τ) | Immediate Margin Sensitivity (τ) | Margin-to-Core Ratio |
|---|---|---|---|---|
| **Meningioma** | Low (well-circumscribed) | **0.1443** | **0.0478** | **33.1%** |
| **Glioma** | High (diffuse infiltration) | **0.0366** | **0.0128** | **35.0%** |
| **Pituitary** | Low (well-circumscribed) | **0.0167** | **0.0025** | **15.1%** |

---

## 5. Duplicate Leakage Impact Summary

- **BRISC Contaminated Benchmark (=1,000$):** 10.1% exact training duplicates in the downloaded archive release alter evaluation metrics through class-prior shifts (meningiomas dropping from 30.6% to 23.4% upon deduplication).
- **BRISC Clean Test (=899$):** De-duplicated evaluation provides an uncontaminated benchmark comparison, yielding Macro-F1 of 0.8344 for DeiT-Small and 0.6991 for ResNet-50 across the full 4-class test set.

