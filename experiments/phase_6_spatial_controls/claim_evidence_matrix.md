# Claim-Evidence Matrix: Phase 6 Spatial Controls Study

**Document ID:** `PHASE_6_CLAIM_EVIDENCE_MATRIX`  
**Phase:** 6 — Targeted Spatial Control Validation  
**Date:** 2026-10-17  
**Evaluation Standards:** Synchronized Paired Patient-Cluster Bootstrap ($B=2,000$), Controlled Radiometry, Boundary Gradient Step Analysis  

---

## 1. Permitted Scientific Statuses
- `SUPPORTED_WITHIN_TESTED_SETUP`: Supported by direct, unconfounded experimental evidence under the audited protocol.
- `PARTIALLY_SUPPORTED`: Supported in some aspects or scenarios, but qualified by specific edge effects or effect-size limits.
- `UNRESOLVED`: Conflicting evidence, unresolved rival hypotheses, or insufficient statistical discrimination.
- `NOT_SUPPORTED_BY_CURRENT_EVIDENCE`: Directly refuted or lacking empirical verification.
- `NOT_ASSESSED`: Not systematically evaluated in this phase.

---

## 2. Claim-by-Claim Evaluation

### Claim 1: The classifier relies heavily on evidence located inside the segmented tumor core.
- **Audited Data:** Tumor excision ($C_1$) produces an enormous drop in Macro-F1 across all scenarios ($\Delta = +0.1130$ to $+0.1160$, $p < 10^{-65}$). In contrast, the matched focal contralateral placebo ($C_2$) produces a minor drop ($\Delta = +0.0114$ to $+0.0142$). Net Tumor Reliance is $+0.0990$ to $+0.1044$ ($95\%$ CI $[0.0786, 0.1302]$).
- **Relevant Controls:** Matched contralateral focal placebo ($C_2$).
- **Main Confounders Assessed:** Area matching, midline crossing, lesion size.
- **Statistical Uncertainty:** Decisively excludes zero and exceeds pre-registered threshold ($0.0500$).
- **Current Evidence Status:** **`SUPPORTED_WITHIN_TESTED_SETUP`**
- **Safest Publishable Wording:** "Under the tested cross-validation scenarios, the frozen ResNet-50 classifier exhibits substantial reliance on intra-lesional image features, with excision reducing Macro-F1 by approximately 0.10 net points relative to matched contralateral ablation."
- **Additional Evidence Needed:** None within this experimental scope.

---

### Claim 2: The model relies on distant cranial anatomical context to classify brain tumors.
- **Audited Data:** Under luminance-preserved distant spatial scrambling ($C_{5\text{LP}}$), Macro-F1 collapses precipitously by $+0.3969$ to $+0.4447$ ($95\%$ CIs $[0.342, 0.493]$). Glioma accuracy collapses to $18.3\%$, with 805 glioma cases erroneously predicted as pituitary adenoma and 360 as meningioma.
- **Relevant Controls:** Original baseline ($C_0$), 50% distant dimming ($C_5$), and 100% luminance/variance-invariant patch permutation ($C_{5\text{LP}}$).
- **Main Confounders Assessed:** Global mean intensity collapse, dynamic range loss, batch-norm covariate shift.
- **Statistical Uncertainty:** Decisively positive ($p < 10^{-100}$).
- **Current Evidence Status:** **`SUPPORTED_WITHIN_TESTED_SETUP`**
- **Safest Publishable Wording:** "Perturbing the spatial organization of distant cranial parenchyma while strictly preserving global image luminance and variance induces severe classification collapse across all tumor classes, confirming that the network actively utilizes global spatial layout and distant cranial landmarks."
- **Additional Evidence Needed:** Sub-region masking (e.g., skull-vault vs cranial base ablation) to localize specific landmark coordinates.

---

### Claim 3: The Phase 5 pituitary vulnerability under distant-context dimming was purely a global radiometric artifact.
- **Audited Data:** In Phase 5, dimming distant tissue by 50% ($C_5$) caused pituitary F1 to drop by $0.0866$ to $0.1048$. When the distant region was scrambled with 100% luminance preservation ($C_{5\text{LP}}$), pituitary F1 collapsed by an even greater **$0.3309$ to $0.3919$** ($95\%$ CI $[0.252, 0.477]$). 
- **Relevant Controls:** Comparison between $C_5$ (radiometric + spatial) and $C_{5\text{LP}}$ (spatial only, zero radiometric shift).
- **Main Confounders Assessed:** Global intensity attenuation vs spatial structure destruction.
- **Statistical Uncertainty:** The drop under $C_{5\text{LP}}$ is statistically significantly larger than under $C_5$ ($p < 10^{-20}$).
- **Current Evidence Status:** **`NOT_SUPPORTED_BY_CURRENT_EVIDENCE`** (i.e., the hypothesis that it was *only* a dimming artifact is refuted; the classifier truly requires distant spatial structure).
- **Safest Publishable Wording:** "The sensitivity of pituitary classifications to distant tissue alterations cannot be attributed merely to global radiometric attenuation; spatial scrambling of distant parenchyma with strict luminance preservation induces a substantially larger diagnostic collapse."
- **Additional Evidence Needed:** None.

---

### Claim 4: The classifier genuinely relies on biological parenchymal signal within the 15-pixel perilesional margin.
- **Audited Data:** When the 15-pixel perilesional margin is removed with a zero-filled ring ($C_{3\_r15}$), Macro-F1 drops by $0.0442$ to $0.0639$ (net $0.0234$ to $0.0277$). However, when the exact same 15-pixel margin is infilled smoothly using Navier-Stokes PDE inpainting ($C_{3\text{NS}}$), the performance drop completely disappears ($\Delta = -0.0016$ to $+0.0077$, $95\%$ CI $[-0.0086, +0.0153]$).
- **Relevant Controls:** Zero-filled margin ($C_{3\_r15}$), matched zero-filled placebo ring ($C_{4\_r15}$), and boundary-smooth Navier-Stokes infill ($C_{3\text{NS}}$).
- **Main Confounders Assessed:** Boundary step discontinuity ($236.66 \to 38.87$), zero-fill intensity shift, tumor bleeding (0 px in $C_{3\text{NS}}$).
- **Statistical Uncertainty:** Inpainting contrast $\Delta(C_0, C_{3\text{NS}})$ spans zero across S0 and S2 and is $< 0.008$ in S1, falling far below the pre-registered $0.0300$ threshold.
- **Current Evidence Status:** **`NOT_SUPPORTED_BY_CURRENT_EVIDENCE`**
- **Safest Publishable Wording:** "The modest performance degradation observed during zero-fill perilesional margin excision is an artifact of artificial boundary step-edge discontinuities; when perilesional tissue is replaced with smooth, texture-consistent infilling, classifier performance is virtually indistinguishable from baseline."
- **Additional Evidence Needed:** None.

---

### Claim 5: Net perilesional margin reliance exhibits a monotonic biological dose-response relationship with margin thickness.
- **Audited Data:** Across 4 radii ($r \in \{5, 10, 15, 20\}$ pixels):
  - Scenario S0: Net Margin = $0.0309 \to 0.0249 \to 0.0234 \to 0.0116$ (**decreasing trend**)
  - Scenario S1: Net Margin = $0.0247 \to 0.0260 \to 0.0277 \to 0.0235$ (**flat / non-monotonic**)
  - Scenario S2: Net Margin = $0.0223 \to 0.0284 \to 0.0262 \to 0.0225$ (**flat / non-monotonic**)
- **Relevant Controls:** Matched contralateral placebo rings ($C_{4\_r05}, C_{4\_r10}, C_{4\_r15}, C_{4\_r20}$).
- **Main Confounders Assessed:** Placebo area scaling, midline proximity, expanding intervention footprint.
- **Statistical Uncertainty:** Confidence intervals across all radii heavily overlap between $0.010$ and $0.040$.
- **Current Evidence Status:** **`NOT_SUPPORTED_BY_CURRENT_EVIDENCE`**
- **Safest Publishable Wording:** "Net perilesional margin reliance does not scale monotonically with margin thickness; instead, the net effect remains flat (~0.022–0.030) or diminishes at wider radii as contralateral placebo rings ablate increasingly large fractions of normal brain parenchyma."
- **Additional Evidence Needed:** None.

---

### Claim 6: The experimental findings establish a causal biological mechanism or clinical diagnostic process.
- **Audited Data:** Image-space masking and inpainting interventions perturb network activations, but do not provide histopathological ground truth or biological causal mechanisms.
- **Relevant Controls:** N/A.
- **Current Evidence Status:** **`NOT_SUPPORTED_BY_CURRENT_EVIDENCE`**
- **Safest Publishable Wording:** "These spatial interventions probe empirical feature dependencies in a frozen deep learning model and do not establish biological causal mechanisms, tumor histology understanding, or clinical diagnostic validity."
- **Additional Evidence Needed:** Multicenter cohorts with external pathological ground truth.
