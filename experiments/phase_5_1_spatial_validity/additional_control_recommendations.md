# Phase 5.1 Additional Control Recommendations

**Document ID:** `PHASE_5_1_RECOMMENDED_CONTROLS`  
**Phase:** 5.1 — Spatial Intervention Validity Audit  
**Authoritative Standard:** Justified Causal Disentanglement based on Audit Findings  
**Date:** 2026-10-17  

---

## 1. Justification Principles

In accordance with Phase 5.1 rules, additional experiments must **not** be proposed as an open-ended battery. Every recommended control below is directly necessitated by an identified confound or unresolved limitation in the Phase 5 audit:

---

## 2. Recommended Follow-Up Controls

### Control 1: Luminance-Preserved Distant Spatial Scrambling
- **Direct Audit Motive:**
  - Audit C revealed that $C_5$ ($I_{\text{distant\_perturbed}}$) reduced global slice mean intensity by **47.5%** ($39.79 \to 20.91$) and standard deviation by **44.2%** ($40.93 \to 22.84$).
  - As a result, the observed drop in pituitary classification ($F_1: 0.954 \to 0.848$) is completely confounded between **loss of distant anatomical landmarks** and **sensitivity to global radiometric / contrast collapse**.
- **Specification:**
  - Reconstruct $C_5$ using spatial block permutation ($16 \times 16$ pixel patches) or Fourier phase randomization strictly outside the 15-pixel dilated tumor zone ($M_{\text{dilated}}$).
  - *Invariant Guaranteed:* Exactly 0.00% change in global mean intensity, standard deviation, and dynamic range.
  - *Target Hypothesis:* If pituitary accuracy collapses under luminance-preserved block scrambling, anatomical landmark dependency is confirmed. If pituitary accuracy remains high, the Phase 5 drop was a global contrast artifact.

### Control 2: Parametric Dose-Response Margin Thickness Sweep
- **Direct Audit Motive:**
  - Audit B and D confirmed that the 15-pixel dilation margin produced a Net Margin Reliance of $+0.0234$ to $+0.0277$, which fell short of the pre-registered 0.0300 effect-size threshold.
  - Furthermore, $r=15$ pixels physical representation (~6.5 mm) is arbitrary without a dose-response verification.
- **Specification:**
  - Evaluate matched paired margins at discrete radii: $r \in \{5, 10, 15, 20, 30\}$ pixels ($2.1\text{ mm}$ to $13.0\text{ mm}$).
  - *Target Hypothesis:* Test whether perilesional reliance exhibits a monotonic dose-response curve ($\text{Net}(r_1) < \text{Net}(r_2) < \text{Net}(r_3)$) or plateaus immediately, which would indicate generic edge occlusion.

### Control 3: Boundary-Constrained Texture-Synthesized Margin Infill
- **Direct Audit Motive:**
  - Audit B revealed that applying Gaussian blur ($\sigma = 2.0$) to the margin ring mask caused the intervention footprint to expand from 4,338 pixels to 7,322 pixels, unintentionally blurring an average of **1,390.8 pixels inside the true tumor boundary**.
  - In addition, infilling with a flat constant mean value ($74.29$) artificially eliminates all high-frequency parenchymal texture.
- **Specification:**
  - Apply constrained exemplar-based texture synthesis (e.g. PatchMatch or bi-harmonic PDE inpainting) restricted strictly to $M_{\text{margin}}$ with zero bleeding into the tumor ($M_{\text{tumor}} \cap \Delta I = \emptyset$).
  - *Target Hypothesis:* Cleanly disentangles whether the vanishing drop in $C_6$ was caused by smoothing the step discontinuity or by slight tumor border alteration and texture obliteration.
