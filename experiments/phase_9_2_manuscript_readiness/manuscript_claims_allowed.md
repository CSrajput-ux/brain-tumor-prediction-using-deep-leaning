# Manuscript Claims Guide: Allowed vs. Prohibited Statements

**Project:** Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers  
**Audit Phase:** Phase 9.2 Manuscript Readiness Audit  
**Date:** 2026-10-17  

---

## 1. CLAIMS ALLOWED IN MANUSCRIPT

The following statements are fully supported by empirical data, replicated across 36,768 predictions, and verified by cluster bootstrap confidence intervals:

1. **Mixed-Mechanism Degradation:**
   - *"The catastrophic classification degradation observed under distant-context tile scrambling is driven by both synthetic high-frequency tile-boundary discontinuities and disruption of macroscopic spatial layout."*
2. **Fragility to Synthetic Tile Boundaries:**
   - *"Introducing synthetic step discontinuities along tile boundaries without altering the underlying anatomical content causes a significant drop in frozen ResNet-50 performance ($\Delta 	ext{Macro-F1} = +0.3043$ in $S_0$, 95% CI: $[0.2547, 0.3510]$, $p < 10^{-15}$)."*
3. **Independent Spatial-Layout Sensitivity:**
   - *"Even when tile-seam edge discontinuities are substantially suppressed (>60% reduction in seam Sobel energy, 84.9% reduction in excess high-frequency Fourier energy), permuting distant-context tiles still causes a severe performance collapse ($\Delta 	ext{Macro-F1} = +0.4808$ in $S_0$, 95% CI: $[0.4361, 0.5292]$, $p < 10^{-15}$)."*
4. **Refutation of the Artifact-Only Null Hypothesis ($H_0$):**
   - *"The hypothesis that performance collapse under tile scrambling is merely an artifact of artificial boundary edge noise is decisively refuted ($C_3 	ext{ vs } C_1$ shows an incremental drop of $+0.1172$, $p < 10^{-15}$)."*
5. **Categorical Glioma-to-Pituitary Prior Collapse:**
   - *"Disrupting cranial spatial layout causes glioma recall to collapse from 95.0% to 8.6%, with over 63% of gliomas misclassified as pituitary tumours. Because pituitary tumours in this dataset are anatomically localized to the skull base, scrambling cranial geometry impairs the model's ability to distinguish supratentorial brain parenchyma from the sella turcica."*
6. **Robustness Across Leakage Regimes:**
   - *"The multi-control disentanglement findings reproduce consistently across patient-disjoint ($S_0$), duplicate-cleaned ($S_1$, SSIM 0.80), and aggressively grouped ($S_2$, SSIM 0.75) evaluation splits."*
7. **Methodological Contribution:**
   - *"Our four-condition experimental paradigm establishes a new benchmark for spatial shortcut validation by explicitly controlling for high-frequency boundary artifacts introduced by spatial permutations."*

---

## 2. CLAIMS STRICTLY PROHIBITED IN MANUSCRIPT

The following claims are mathematically, scientifically, or clinically unsupported and must NOT appear in the manuscript:

1. **NO Causal Proportion Claim:**
   - *PROHIBITED:* "Seam artifacts causally account for 72% of the scrambling effect."
   - *REASON:* The effects are interactive and non-linear ($\Delta_{C1} + \Delta_{C2} = 0.785 \gg 0.422$).
   - *ALLOWED PHRASING:* "The seam-only control produced a performance decline whose magnitude was 72% as large as the raw scrambling decline."
2. **NO Biological or Clinical Causality Claim:**
   - *PROHIBITED:* "Our findings show that intracranial brain anatomy is biologically essential for tumour diagnosis."
   - *REASON:* The observed context reliance reflects deep convolutional network statistical feature dependencies, not human radiological reasoning or tumour biology.
3. **NO Continuous Stereotactic Coordinate Mapping Claim:**
   - *PROHIBITED:* "ResNet-50 learns precise stereotactic (x, y, z) brain coordinates."
   - *REASON:* The experiment demonstrates categorical sensitivity to cranial layout disruption, not a continuous stereotactic localization mechanism.
4. **NO Broad Architectural or Clinical Generalization Claim:**
   - *PROHIBITED:* "All medical AI classifiers rely on cranial context shortcuts."
   - *REASON:* The experiment was evaluated exclusively on 2D ResNet-50 checkpoints on Figshare 1512427. It has not been tested on 3D CNNs, Vision Transformers, or external clinical cohorts (TCGA/BraTS).
5. **NO Claim of Equivalence from Non-Significant Tests:**
   - *PROHIBITED:* "In $S_1$ and $S_2$, seam-suppressed scramble is equivalent to raw scramble."
   - *REASON:* $p = 0.123$ and $p = 0.138$ mean the null hypothesis was not rejected; they do not prove equivalence.
