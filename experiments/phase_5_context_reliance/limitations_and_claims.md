# Phase 5: Scientific Limitations, Boundary Claims, and Epistemic Governance

**Document ID:** `PHASE_5_LIMITATIONS_AND_CLAIMS`  
**Phase:** 5 — Targeted Context Reliance and Spatial Intervention Study  
**Authoritative Standard:** Epistemic Humility, Causal Identification Rigor, and Reproducibility Engineering  
**Date:** 2026-10-17  

---

## 1. Permitted Scientific Claims

Based strictly on the audited empirical evidence from Phase 5 (64,344 forward passes, 2,000 synchronized paired cluster bootstrap draws across S0, S1, S2), the following claims are **scientifically certified**:

1. **Intra-Lesional Evidence Reliance is Real and Substantial:**
   - Excision of the primary annotated tumor boundary ($I_{\text{tumor\_removed}}$) causes a consistent and statistically decisive performance decline ($\Delta_{\text{tumor}} \approx 0.113 - 0.116$, $p < 10^{-65}$).
   - The effect exceeds the focal placebo control by an absolute margin of $\sim 0.10$ Macro-F1 points ($\text{Net}_{\text{tumor}} = +0.1041$, 95% CI $[0.0791, 0.1302]$).
   - This proves that intra-lesional image features are actively utilized by the frozen ResNet-50 network and are not completely redundant with background context.

2. **Distant Context Reliance is Comparable in Magnitude to Tumor Ablation:**
   - Perturbing image pixels outside the 15-pixel expanded tumor margin ($I_{\text{distant\_perturbed}}$) causes a large and statistically decisive Macro-F1 drop ($\Delta_{\text{distant}} = +0.096$ to $+0.129$, $p < 10^{-51}$).
   - This proves that the frozen classifier does not function as an isolated lesion segment-and-classify system; its classification decisions are intimately tied to global cranial geometry and distant pixel distributions.

3. **Pituitary Invariance is Resolved as Distant Context Anchoring:**
   - In prior phases, pituitary classification was observed to be virtually invariant to tumor excision ($\Delta_{\text{pituitary}} \approx 0.011$).
   - Phase 5 establishes that pituitary classification collapses by over 10 points ($F_1$ drops from $0.954 \to 0.848$) when distant context is perturbed.
   - This demonstrates that the model identifies pituitary cases predominantly via anatomical location coordinates, cranial reference frames, and skull-base spatial positioning.

4. **Perilesional Margin Effects are Modest and Artifact-Prone:**
   - Zeroing out a 15-pixel perilesional margin produces a modest net drop ($\text{Net}_{\text{margin}} = +0.023$ to $+0.028$), which falls short of the pre-registered effect-size threshold ($0.030$).
   - When boundary discontinuities are eliminated via feathered parenchymal infill ($I_{\text{margin\_feathered}}$), no statistically significant degradation is observed ($\Delta \in [-0.006, +0.007]$).
   - Therefore, the raw margin drop is primarily an artificial edge-step artifact rather than evidence of specialized perilesional feature reliance.

---

## 2. Expressly Forbidden Claims (Epistemic Safeguards)

To maintain scientific integrity, the following claims are **expressly prohibited**:

1. **NO Claim of Discovering Clinical "Shortcuts":**
   - The observed reliance on distant cranial context must NOT be described as an "anatomical shortcut" or "dataset defect."
   - In clinical neuroradiology, anatomical location (e.g. sella turcica for pituitary adenoma, extra-axial dural attachment for meningioma, intra-axial white matter for glioma) is legitimate, essential diagnostic information.
   - Calling global cranial location reliance a "shortcut" confuses clinical inductive bias with spurious artifacts.

2. **NO Claim of Anatomical or Biological Segmentation Ground Truth:**
   - The Cheng dataset contains **only** whole-slice 2D MRI images and binary tumor boundary masks.
   - It contains **zero** segmentations for ventricles, edema, skull base, sulci, or parenchyma.
   - Derived regions (such as the 15-pixel dilated ring) are strictly **approximate image-space morphological zones**, not certified histological or anatomical compartments.

3. **NO Claim of Biological Invariance or Equivalence from Non-Significance:**
   - The observation that $I_{\text{margin\_feathered}}$ produced a non-significant contrast ($p = 0.052$ to $0.83$) does **not** prove that the classifier is invariant to peritumoral edema or parenchymal infiltration.
   - A non-significant p-value means the observed difference is consistent with chance under this specific infill method; it does not establish proof of equivalence.

4. **NO Claim of Clinical Utility or Diagnostic Readiness:**
   - This research evaluated frozen research models on single 2D slices from a retrospective dataset.
   - Performance metrics and intervention responses in this study cannot be generalized to 3D volumetric clinical workflows, prospective patient triage, or therapeutic decision-making.

---

## 3. Methodological Limitations

1. **2D Slices vs 3D Volumetric Anatomy:**
   - Real brain tumors and edema compartments are 3D structures. Evaluating 2D slices loses through-plane context and partial-volume continuity.
2. **Artificial Infill Approximations:**
   - Zeroing out pixels or filling with mean parenchymal intensity introduces distribution shifts that differ from natural imaging noise.
3. **Contrast-Enhanced T1 Weighting Exclusivity:**
   - Peritumoral vasogenic edema is predominantly visible on T2/FLAIR sequences, which are absent in this dataset. T1-CE primarily highlights blood-brain barrier disruption, limiting the physical interpretation of the 15-pixel margin.
