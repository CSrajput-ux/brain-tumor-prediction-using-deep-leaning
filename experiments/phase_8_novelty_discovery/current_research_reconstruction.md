# Current Research Reconstruction & Epistemic Audit

**Document ID:** `CURRENT_RESEARCH_RECONSTRUCTION`  
**Project:** Cheng Brain Tumor MRI Classification Robustness Study  
**Phase:** 8 — Deep Novelty Discovery, Research Redesign & Contribution Validation  
**Date:** 2026-10-17  
**Authoritative Standard:** Read-Only Artifact Inspection & Epistemic Boundary Audit  

---

## 1. Original Locked Research Question

The project investigates how a deep convolutional neural network (ResNet-50) trained on brain MRI slices depends on:
1. Intra-tumoral image evidence (lesion pathology).
2. Focal non-tumour comparison regions (contralateral control tissue).
3. Peritumoral margin interventions (immediate 5–20 px parenchymal penumbra).
4. Distant image context (remote intracranial brain tissue outside the lesion).
5. Spatial organization outside the lesion (anatomical coordinate layout).
6. Image-editing artifacts and distribution shifts caused by interventions.

**The Central Scientific Question:**
> *"How can the dependence of a brain MRI classifier on tumour-region evidence and surrounding spatial context be quantified using controlled interventions, matched controls, patient-aware evaluation, and paired statistical comparisons?"*

Critically, the protocol locks the premise that performance alterations must **not** be automatically interpreted as biological mechanisms, cellular pathology, or proven anatomical shortcuts.

---

## 2. Exact Experimental Protocol Reconstructed from Frozen Artifacts

| Protocol Dimension | Specification in Frozen Repository | Authoritative Source Artifact |
| :--- | :--- | :--- |
| **Dataset Source** | Jun Cheng Brain Tumor Dataset, Figshare article `1512427` (v5) | `data/raw/` |
| **Image Cohort** | 3,064 2D T1-weighted contrast-enhanced (T1-CE) axial/coronal/sagittal MRI slices | `experiments/baseline/` |
| **Patient Population** | 233 unique patient IDs (confirmed via slice-level metadata) | `experiments/phase_1_7/` |
| **Diagnostic Classes** | 3 classes: Meningioma ($n=708$), Glioma ($n=1,426$), Pituitary Adenoma ($n=930$) | `experiments/phase_1_8/` |
| **Evaluation Splits** | 5-fold cross-validation under 3 distinct leakage-free scenarios: <br>• **$S_0$**: Strict patient-grouped split (233 patient clusters)<br>• **$S_1$**: Near-duplicate candidate grouping at SSIM $\ge 0.80$<br>• **$S_2$**: Near-duplicate candidate grouping at SSIM $\ge 0.75$ | `experiments/phase_2_baseline/` |
| **Model Checkpoints** | 15 frozen ResNet-50 checkpoints (5 folds $\times$ 3 scenarios), trained with cross-entropy loss, SGD with momentum, input resolution $224 \times 224 \times 3$ | `experiments/phase_2_baseline/S{0,1,2}/fold_{0..4}/` |
| **Intervention Suite** | 14 experimental conditions evaluated out-of-fold across all 15 checkpoints ($128,688$ forward passes):<br>1. $I_{\text{orig}}$: Unmodified test image baseline<br>2. $I_{\text{tumor}}$: Complete intra-tumoral excision (zero-filled)<br>3. $I_{\text{tumor\_only}}$: Complete background excision (tumor-only preserved)<br>4. $I_{\text{placebo}}$: Matched contralateral focal placebo excision<br>5. $I_{\text{distant}}$: 50% distant-context dimming<br>6. $I_{\text{C5LP}}$: Luminance-preserved $16 \times 16$ distant patch scrambling<br>7. $I_{\text{margin,15}}$: 15-pixel perilesional margin zero-fill<br>8. $I_{\text{C3NS}}$: 15-pixel margin Navier-Stokes PDE inpainting<br>9–12. $I_{\text{margin,}\{5,10,15,20\}}$: Margin thickness sweep<br>13–14. Matched placebo margin rings | `experiments/phase_6_spatial_controls/matched_predictions.csv` |
| **Statistical Unit** | Synchronized paired patient-cluster bootstrap ($B=2,000$ replicates, random seed 42) recomputing full confusion matrices and Macro-F1 per replicate concurrently across conditions | `experiments/phase_4_1_reconciliation/`, `experiments/phase_6_spatial_controls/paired_contrasts.json` |

---

## 3. Primary Outcomes and Quantitative Findings

All point estimates and 95% bootstrap confidence intervals reproduce with **0.000000 numerical discrepancy** across repository checks:

### Summary of Point Estimates and Synchronized Bootstrap CIs (Scenario $S_0$)

| Intervention Contrast | Condition A | Condition B | Target Metric | Point Estimate ($\Delta$) | 95% Cluster Bootstrap CI | McNemar $\chi^2$ | P-Value |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Tumor Excision Effect** | $I_{\text{orig}}$ | $I_{\text{tumor}}$ | Macro-F1 | $+0.1159$ | $[+0.0934, +0.1412]$ | $311.2$ | $p < 10^{-65}$ |
| **Focal Placebo Effect** | $I_{\text{orig}}$ | $I_{\text{placebo}}$ | Macro-F1 | $+0.0114$ | $[+0.0031, +0.0210]$ | $14.1$ | $p = 0.00017$ |
| **Net Tumor Reliance** | $(I_{\text{orig}} - I_{\text{tumor}}) - (I_{\text{orig}} - I_{\text{placebo}})$ | — | Macro-F1 | **$+0.1045$** | **$[+0.0792, +0.1304]$** | — | **$p < 10^{-65}$** |
| **Distant Context Dimming** | $I_{\text{orig}}$ | $I_{\text{distant}}$ | Macro-F1 | $+0.0960$ | $[+0.0629, +0.1328]$ | $153.2$ | $p < 10^{-34}$ |
| **Luminance-Preserved Scramble** | $I_{\text{orig}}$ | $I_{\text{C5LP}}$ | Macro-F1 | **$+0.4215$** | **$[+0.3734, +0.4726]$** | **$1,124.6$** | **$p < 10^{-240}$** |
| **Pituitary F1 under $C_{5\text{LP}}$** | $I_{\text{orig}}$ | $I_{\text{C5LP}}$ | Pituitary F1 | **$+0.3650$** | **$[+0.2926, +0.4434]$** | $182.4$ | $p < 10^{-40}$ |
| **Zero-Fill Margin Ablation** | $I_{\text{orig}}$ | $I_{\text{margin,15}}$ | Macro-F1 | $+0.0449$ | $[+0.0270, +0.0645]$ | $41.3$ | $p < 10^{-9}$ |
| **Navier-Stokes Inpainting** | $I_{\text{orig}}$ | $I_{\text{C3NS}}$ | Macro-F1 | **$-0.0016$** | **$[-0.0086, +0.0045]$** | **$0.4$** | **$p = 0.527$** |
| **Margin Step Discontinuity** | $I_{\text{C3NS}}$ | $I_{\text{margin,15}}$ | Macro-F1 | **$+0.0465$** | **$[+0.0289, +0.0668]$** | **$44.1$** | **$p < 10^{-10}$** |

---

## 4. Confirmed Methodological Weaknesses and Confounders

Auditing across Phase 5.1 and Phase 6.1 identified five critical methodological vulnerabilities in the current empirical design:

1. **Tile-Seam Edge Confound in Distant Patch Scrambling ($C_{5\text{LP}}$):**
   - While $C_{5\text{LP}}$ strictly preserved global mean intensity ($39.79$) and variance ($40.93$), dividing the brain into $16 \times 16$ permutation tiles introduced grid seams that nearly **doubled the high-frequency Sobel gradient energy** (+97.9%, from $18.33$ to $36.28$).
   - Convolutional layers in ResNet-50 (particularly `conv1` $7 \times 7$ kernels) are known to be sensitive to high-frequency periodic discontinuities. Consequently, the catastrophic performance collapse ($\Delta \approx +0.42$) cannot be cleanly isolated as pure loss of macroscopic anatomical layout; it is partly confounded by out-of-distribution high-frequency edge noise.
2. **Synthetic Texture Infill vs. Biological Penumbra ($C_{3\text{NS}}$):**
   - Navier-Stokes PDE inpainting successfully removed 83.6% of the step-edge gradient ($236.66 \to 38.87$) without bleeding into the tumor core.
   - However, inpainting synthesizes a mathematically smooth interpolation of surrounding pixels. While this proves that the neural network does not exploit genuine perilesional parenchymal texture, it cannot prove that biological peritumoral tissue in living human brains lacks diagnostic pathology.
3. **Absence of Sub-Region Specificity for Distant Context:**
   - In Phase 6, patch scrambling permuted all non-tumor tiles simultaneously across the entire cranial volume.
   - Although 56.5% of gliomas flipped into pituitary predictions under scrambling, the experiment did not ablate skull-base coordinates independently of cerebral calvarium. Therefore, attributing the effect specifically to a "skull-base coordinate shortcut" remains an unsubstantiated inference.
4. **2D Slice Representation of 3D Volumetric Anatomy:**
   - The Cheng dataset consists of arbitrary 2D cross-sections without complete 3D volumes or slice thickness standardization. Interventions performed on 2D slices cannot account for out-of-plane anatomical continuity.
5. **Frozen Backbone Limitation:**
   - All Phase 3–6.1 experiments evaluated a single frozen architecture (ResNet-50). Whether Vision Transformers (ViTs), Swin Transformers, or ConvNeXt exhibit identical spatial vulnerability remains untested in this repository.

---

## 5. Claims Withdrawn, Downgraded, or Prohibited

The following claim revisions have been formally ratified in `experiments/phase_6_1_claim_sanity/` and `experiments/phase_7_literature_review/`:

| Original Claim | Revised Epistemic Status | Scientific Justification |
| :--- | :---: | :--- |
| *"The classifier relies specifically on skull-base coordinates."* | **DOWNGRADED TO `UNRESOLVED`** | Scrambling disrupted the entire brain simultaneously, and tile-boundary seams introduced significant high-frequency noise. Specific skull-base localization was never isolated. |
| *"Proves the absence of biological peritumoral information."* | **DOWNGRADED TO `NOT_SUPPORTED_BY_CURRENT_EVIDENCE`** | In silico inpainting measures the internal feature reliance of a deep CNN; it has zero epistemic authority over histopathological or microscopic tumor biology. |
| *"Establishes a causal biological mechanism."* | **DOWNGRADED TO `NOT_SUPPORTED_BY_CURRENT_EVIDENCE`** | Pixel-level ablations probe computational representations, not biological etiology (Castro et al., 2020). |
| *"First-ever framework to test medical shortcut learning."* | **PROHIBITED OVERCLAIM** | Direct precedent exists in dermatology (Bissoto 2019), radiology (DeGrave 2021, Zech 2018), and computer vision (Fong 2017, Xiao 2021). |

---

## 6. What the Existing Study Defensibly Concludes

### Defensible Conclusions:
1. **Intra-tumoral reliance is decisive in the trained model:** Excision of the primary tumor induces a large, statistically robust performance collapse ($\Delta = +0.1045$, $p < 10^{-65}$) that cannot be accounted for by non-specific tissue area loss (placebo drop is only $+0.0114$).
2. **Naive zero-fill margin removal is an artificial step-edge artifact:** The apparent performance degradation observed when excising a 15-pixel margin vanishes ($\Delta \le 0.0077$, CI spans zero) when artificial step gradients are suppressed via smooth PDE inpainting.
3. **Distant context sensitivity is real and distinct from radiometric dimming:** Preserving global mean and variance does not prevent catastrophic collapse ($\Delta \approx +0.42$) when spatial arrangement is permuted.

### What the Existing Study Cannot Conclude:
1. Cannot conclude that the model uses a specific anatomical coordinate (e.g., sella turcica coordinates) rather than general cranial edge orientation.
2. Cannot conclude that tile scrambling isolates spatial arrangement from high-frequency edge-seam artifacts.
3. Cannot conclude clinical validity or generalization to external hospital MRI datasets.
4. Cannot conclude biological or pathological absence of disease markers in perilesional brain tissue.
