# Phase 7 Systematic Literature Review & Novelty Verification Report

**Document ID:** `PHASE_7_SYSTEMATIC_REVIEW_REPORT`  
**Project:** Cheng Brain Tumor MRI Classification Robustness Study  
**Phase:** 7 — Systematic Literature Review and Novelty Verification  
**Authoritative Standard:** PRISMA-Informed Prior-Art Synthesis and Claim Calibration  
**Date:** 2026-10-17  
**Final Gate Decision:** **`PASS`**  

---

## 1. Executive Summary

This systematic literature review establishes the state of the art surrounding shortcut learning, lesion interventions, context confounding, and evaluation rigor in medical image classification. It benchmarks the experimental protocol developed in Phases 1–6.1 against published prior art to verify what is already known, what remains unresolved, and what claims our evidence can defensibly support.

### Key Gate Findings:
- **Search Execution & Traceability:** **441 initial records** retrieved across 10 systematic search queries in 6 families; **257 unique records** screened; **20 full-text studies** evaluated; **16 core studies** fully verified and synthesized in [`prior_art_matrix.csv`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_7_literature_review/prior_art_matrix.csv).
- **Closest Direct Prior Art:** [Bissoto et al. (2019, *CVPRW*)](https://arxiv.org/abs/1903.04033) (lesion vs. background masking in dermoscopy), [DeGrave et al. (2021, *Nature Machine Intelligence*)](https://doi.org/10.1038/s42256-021-00338-7) (shortcut learning in COVID-19 radiographs), [Fong & Vedaldi (2017, *ICCV*)](https://doi.org/10.1109/ICCV.2017.371) (meaningful perturbation and boundary artifact smoothing), [Cheng et al. (2015, *PLOS ONE*)](https://doi.org/10.1371/journal.pone.0140381) (the original benchmark dataset and concentric ring dilation), and [Vangala et al. (2026, *arXiv:2610.00421*)](https://arxiv.org/abs/2610.00421) (audit of patient and near-duplicate leakage on the Cheng benchmark).
- **Novelty Assessment:** While individual components have conceptual precedent, **the complete multi-control spatial intervention protocol has not been identified in the reviewed medical imaging literature.**
- **Scientific Claim Calibration:** Core empirical claims (intra-tumoral feature reliance, boundary step discontinuity artifacts in zero-fill margins, and distant context spatial sensitivity beyond luminance) are solidly supported. Overclaims attributing predictions specifically to "skull-base shortcuts" or claiming proof of "zero biological margin reliance" or "causal biological mechanisms" are explicitly prohibited.

---

## 2. Top Five Most Relevant Direct-Prior-Art Studies

1. **[Bissoto et al. (2019, *CVPR Workshops*)](https://arxiv.org/abs/1903.04033): *(De)Constructing Bias on Skin Lesion Datasets***
   - *Relevance:* Demonstrated that deep classifiers achieve high diagnostic accuracy even when the diseased lesion is completely excised ("Skin-Only"), proving that models exploit background texture and acquisition shortcuts.
   - *Contrast with Our Work:* Bissoto evaluated dermoscopy without matched spatial placebos, perilesional margin inpainting, or cluster-synchronized bootstrap uncertainty estimation.
2. **[DeGrave et al. (2021, *Nature Machine Intelligence*)](https://doi.org/10.1038/s42256-021-00338-7): *AI for radiographic COVID-19 detection frequently relies on superficial shortcuts***
   - *Relevance:* Landmark demonstration that medical CNNs exploit non-pathological shortcuts (hospital text markers, border padding, patient positioning) rather than lung pathology.
   - *Contrast with Our Work:* Focused on chest radiographs; did not examine concentric perilesional margin sweeps, inpainting boundary controls, or distant spatial tile scrambling.
3. **[Fong & Vedaldi (2017, *ICCV*)](https://doi.org/10.1109/ICCV.2017.371): *Interpretable Explanations of Black Boxes by Meaningful Perturbation***
   - *Relevance:* Proved that naive zero-filling introduces artificial high-frequency step discontinuities that trigger artifactual CNN filter responses, establishing the necessity of smooth boundary perturbations.
   - *Contrast with Our Work:* Framed as an optimization algorithm for saliency heatmaps in natural vision; we adapt smooth inpainting into a hypothesis-driven medical intervention audit.
4. **[Cheng et al. (2015, *PLOS ONE*)](https://doi.org/10.1371/journal.pone.0140381): *Enhanced Performance of Brain Tumor Classification via Tumor Region Augmentation and Partition***
   - *Relevance:* Created the exact Figshare 1512427 dataset evaluated in our study and introduced the concept of concentric ring-form dilation margins to capture surrounding tissue clues.
   - *Contrast with Our Work:* Cheng used concentric rings as positive feature extractors for classical SVMs evaluated on random slice splits; we evaluate concentric rings as negative ablation targets for deep CNNs under strict patient-disjoint splits.
5. **[Vangala et al. (2026, *arXiv:2610.00421*)](https://arxiv.org/abs/2610.00421): *Scores That Hold, Benchmarks That Leak: Measuring Dataset Contamination in Public Brain-Tumor MRI Classification***
   - *Relevance:* Audited the Cheng Figshare benchmark and established that 95.5% of traceable test slices share patient overlap with training sets, proving that reported >98% benchmark scores are inflated by data leakage.
   - *Contrast with Our Work:* Vangala focused on dataset contamination auditing; our study applies controlled spatial interventions to frozen models evaluated on verified leakage-free splits.

---

## 3. What is Already Established vs. Defensible Contributions

### Well-Established in Prior Art (Cannot Be Claimed as Novel):
- Deep neural networks in computer vision and medical imaging frequently exploit background shortcuts and spurious correlations [Geirhos 2020; DeGrave 2021; Xiao 2021].
- Random slice splitting on public brain MRI benchmarks produces severe patient-level data leakage [Vangala 2026].
- Naive zero-fill image occlusion creates artificial step-edge boundary artifacts that distort convolutional neural network activations [Fong & Vedaldi 2017].
- Dilating tumor masks into concentric rings captures perilesional tissue regions [Cheng 2015].

### Defensible Novel Contributions of This Study:
1. **The Multi-Control Spatial Intervention Framework:**
   Unifying lesion excision with **matched contralateral focal placebos**, **parametric margin thickness sweeps (5–20 px)**, **Navier-Stokes PDE boundary inpainting**, and **luminance-preserved patch scrambling** within a single, coherent audit protocol.
2. **Resolution of the Perilesional Margin Confound in Deep MRI Classifiers:**
   Proving empirically that the performance drop observed during zero-fill margin excision ($\Delta \approx +0.025$) is an artifact of artificial boundary step-edge gradients ($236.7$), and vanishes completely ($\Delta < 0.008$) when boundary continuity is restored via inpainting without altering the tumor core.
3. **Decoupling Spatial Context Sensitivity from Global Radiometric Attenuation:**
   Proving that classifier vulnerability to distant tissue perturbation is not a brightness dimming artifact: 100% luminance-preserved spatial scrambling causes a far more catastrophic diagnostic collapse ($\Delta \approx +0.42$) and drives 56.5% of glioma cases to be misclassified as pituitary adenoma.
4. **Methodological Rigor and Artifact Traceability:**
   Executing all analyses under frozen ResNet-50 checkpoints across three leakage-free scenarios ($S_0, S_1, S_2$) with synchronized paired patient-cluster bootstrap resampling ($B=2,000$).

---

## 4. Prohibited Overclaims

The manuscript must strictly avoid the following claims:
- ❌ **Do NOT claim that this is the "first study to explore shortcut learning in brain MRI."** (DeGrave, Vangala, and others have analyzed medical shortcuts and benchmark leakage).
- ❌ **Do NOT claim to have proven a "skull-base coordinate shortcut."** (Tile scrambling scrambled the entire brain simultaneously; tile-seam edge noise partially confounds the drop).
- ❌ **Do NOT claim that peritumoral brain tissue contains "no biological or diagnostic information."** (Proving that a 2D ResNet-50 does not exploit margin texture does not determine human pathological ground truth).
- ❌ **Do NOT claim to have established a "causal biological mechanism."** (In silico pixel manipulations probe deep learning representations, not human cellular pathology; Castro et al., 2020).

---

## 5. Decision on Additional Experiments

**No additional experiments are required.**

The decision analysis in [`additional_experiment_decision.md`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_7_literature_review/additional_experiment_decision.md) concludes that:
- The existing empirical evidence across Phases 1–6.1 is fully reproducible and sufficient to support all calibrated claims.
- The tile-seam limitation and the in silico epistemic boundary are appropriately addressed through transparent reporting and calibrated phrasing rather than open-ended experiment generation.

---

## 6. Final Gate Decision: `PASS`

The literature review has successfully identified, mapped, and verified the relevant prior art across 6 search families, established an evidence-backed research gap, calibrated all proposed claims against published literature, and confirmed the readiness of the project for manuscript drafting.
