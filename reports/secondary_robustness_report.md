# Secondary Experiments, Replication & Robustness Analysis

Date: 2026-10-29 (Asia/Kolkata)  
Auditors: Multidisciplinary Research Team (Computer-Vision Engineer, Biostatistician)  
Scope: Architecture Comparison, Method Invariance, Plane Stratification, Tumour Biology Heterogeneity

---

## 1. Architectural Inductive Bias: ResNet-50 (CNN) vs DeiT-Small (ViT)

Hypothesis: Vision Transformers (global self-attention) exhibit greater intra-lesional core reliance than Convolutional Neural Networks (localized receptive fields), while remaining robust to distant context shortcuts.

| Region | Perturbation Method | CNN Sham-Corrected (τ) | ViT Sham-Corrected (τ) | Difference (ViT - CNN) | Raw Wilcoxon p | Holm-Adjusted p | Cohen's d_z |
|---|---|---|---|---|---|---|---|
| `core` | telea_inpaint | 0.0161 ± 0.046 | 0.0900 ± 0.196 | **+0.0738** | 0.0123 | 0.0980 | 0.362 |
| `immediate` | telea_inpaint | 0.0061 ± 0.039 | 0.0226 ± 0.080 | **+0.0166** | 0.1124 | 0.7870 | 0.184 |
| `outer` | telea_inpaint | 0.0064 ± 0.071 | 0.0182 ± 0.085 | **+0.0118** | 0.1732 | 1.0000 | 0.117 |
| `remote` | telea_inpaint | 0.0062 ± 0.027 | 0.0134 ± 0.060 | **+0.0072** | 0.9087 | 1.0000 | 0.114 |
| `core` | matched_texture_fill | 0.0567 ± 0.162 | 0.1006 ± 0.173 | **+0.0439** | 0.0164 | 0.1147 | 0.198 |
| `immediate` | matched_texture_fill | 0.0424 ± 0.171 | 0.0131 ± 0.099 | **-0.0293** | 0.6023 | 1.0000 | -0.140 |
| `outer` | matched_texture_fill | 0.0600 ± 0.176 | 0.0454 ± 0.088 | **-0.0146** | 0.7369 | 1.0000 | -0.072 |
| `remote` | matched_texture_fill | 0.0100 ± 0.203 | -0.0038 ± 0.065 | **-0.0138** | 0.5236 | 1.0000 | -0.064 |

*Note on Multiplicity: While the pooled paired difference in Method A Core sensitivity is nominally significant at raw p = 0.0123 (and cluster-level p = 0.0162 across 55 units), the multi-region step-down Holm-adjusted p-value is p_adj = 0.0980. Therefore, Vision Transformer architectural superiority is qualified as an exploratory finding rather than a confirmatory proof of universal superiority.*

---

## 2. Perturbation Engine Invariance: Method A (Inpainting) vs Method B (Texture Fill)

Hypothesis: Region sensitivity rank order (Core > Immediate > Outer > Remote) is concordant across edit engines.

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

Evaluating regional sensitivity across Axial, Coronal, and Sagittal slice orientations under the primary benchmark model (DeiT-Small, Method A Inpainting):

| Imaging Plane | Sample Count (N) | Mean Core Sensitivity (τ_core) | Mean Immediate Margin (τ_immed) | Mean Outer Margin (τ_outer) | Mean Remote (τ_remote) |
|---|---|---|---|---|---|
| **Axial** | 15 | **0.0492** | 0.0283 | 0.0469 | 0.0312 |
| **Coronal** | 15 | **0.0370** | 0.0118 | 0.0175 | 0.0027 |
| **Sagittal** | 15 | **0.0690** | 0.0317 | 0.0259 | 0.0082 |

*Pooled Architecture Reference: When pooling across both architectures (ResNet-50 and DeiT-Small) and both perturbation methods, mean BRISC core sensitivities are 0.0337 (Axial), 0.0298 (Coronal), and 0.0582 (Sagittal).*

---

## 4. Lesion Boundary Biology & Class Heterogeneity

Exploratory evaluation of regional sensitivity across Cheng tumour classes under DeiT-Small (Method A):

| Tumour Class | Sample Count (N) | Core Sensitivity (τ_core) | Immediate Margin (τ_immed) | Outer Margin (τ_outer) | Remote Context (τ_remote) | Margin-to-Core Ratio (%) |
|---|---|---|---|---|---|---|
| **Glioma** | 15 | **0.0398** | 0.0268 | -0.0066 | 0.0218 | **67.2%** |
| **Meningioma** | 15 | **0.3438** | 0.0338 | -0.0136 | 0.0165 | **9.8%** |
| **Pituitary** | 15 | **0.0009** | 0.0034 | 0.0392 | 0.0001 | **360.2%** |

*Cross-Dataset Reference: When pooling across all 90 slices from both datasets, architectures, and methods, unweighted margin-to-core ratios are 35.0% for gliomas, 33.1% for meningiomas, and 15.1% for pituitary adenomas.*

---

## 5. Duplicate Leakage Impact Summary

- **BRISC Contaminated Benchmark ($N=1,000$):** 10.1% exact training duplicates artificially inflate performance metrics and suppress true out-of-distribution uncertainty.
- **BRISC Clean Test ($N=899$):** Zero train-test leakage enables an uncontaminated evaluation of regional sensitivity.
