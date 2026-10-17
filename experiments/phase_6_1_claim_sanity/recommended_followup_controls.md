# Recommended Follow-Up Controls

**Document ID:** `PHASE_6_1_FOLLOWUP_CONTROLS`  
**Phase:** 6.1 — Claim and Result Sanity Audit  
**Date:** 2026-10-17  
**Auditor:** Independent Scientific and Statistical Reviewer  

---

## 1. Context and Purpose

Phase 6 cleanly resolved the radiometric confound ($C_{5\text{LP}}$ vs $C_5$) and the boundary discontinuity artifact ($C_{3\text{NS}}$ vs $C_3$). However, the Phase 6.1 Claim Sanity Audit identified two remaining mechanistic ambiguities that should be evaluated if specific anatomical shortcut claims are to be made in publication:

---

## 2. Recommended Follow-Up Controls

### Control 1: Anatomically Targeted Sub-Region Ablation (Skull-Vault vs. Sella Turcica / Skull-Base)
- **Problem Identified in Audit:**
  - $C_{5\text{LP}}$ scrambled all distant patches uniformly across both the cranial vault, cerebral hemispheres, and skull base.
  - While this induced massive glioma-to-pituitary misclassification (56.5% of gliomas predicted as pituitary), it remains unresolved whether the model was utilizing **skull-base coordinates specifically** or general **cranial vault boundaries**.
- **Proposed Protocol:**
  - Divide the non-tumoral distant space into two anatomically registered zones:
    1. *Zone A (Skull-Base / Sella Turcica):* Inferior cranial base bounding box.
    2. *Zone B (Calvarium / Cranial Vault):* Superior cerebral cortex and skull perimeter.
  - Apply luminance-preserved scrambling or Navier-Stokes inpainting to Zone A while keeping Zone B intact, and vice versa.
  - **Hypothesis:** If scrambling Zone A alone produces the glioma-to-pituitary inversion while scrambling Zone B does not, specific skull-base coordinate reliance is definitively proven.

---

### Control 2: Seam-Smoothed / Wavelet Phase Scrambling (Eliminating Tile Boundary Discontinuities)
- **Problem Identified in Audit:**
  - $C_{5\text{LP}}$ tile permutation increased Sobel gradient energy by **+97.9%** ($18.33 \to 36.28$) due to artificial $16 \times 16$ tile seams.
  - Deep CNN convolutional layers (especially Conv1 filters) are sensitive to high-frequency checkerboard edges. It remains possible that part of the 0.42 Macro-F1 collapse was caused by out-of-distribution high-frequency edge noise rather than pure anatomical dislocation.
- **Proposed Protocol:**
  - Implement Continuous Wavelet / Fourier Phase Randomization strictly outside the dilated tumor zone, or apply a smooth Gaussian tapered window across tile seams.
  - **Hypothesis:** If smooth phase scrambling produces the same ~0.40 collapse, the effect is 100% spatial arrangement; if smooth scrambling causes a smaller drop (e.g., ~0.20), the difference represents vulnerability to tile-seam edge noise.

---

## 3. Timing Recommendation

These follow-up controls are **not required to conclude Phase 6.1**, as all primary Phase 6 computations are verified and reproducible. Rather, they represent targeted follow-up experiments that can be executed during Phase 7/8 if reviewers request sub-anatomical localization.
