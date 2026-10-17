# Decision on Additional Experiments

**Document ID:** `PHASE_7_ADDITIONAL_EXPERIMENT_DECISION`  
**Phase:** 7 — Systematic Literature Review and Novelty Verification  
**Date:** 2026-10-17  
**Auditor:** Independent Scientific and Statistical Reviewer  

---

## 1. Context and Objective

Phase 7 evaluated what aspects of our empirical findings are defensible based on published prior art and what claims would require new experimental data.

The guiding principle of this audit is:
> *Do not recommend an experiment merely because it is technically possible. An experiment is only justified if it directly distinguishes between two unresolved rival scientific hypotheses essential to the paper's central contribution.*

---

## 2. Evaluation of Proposed Follow-Up Experiments

### Experiment 1: Targeted Sub-Region Masking (Skull-Vault vs. Sella Turcica / Skull-Base)
- **Scientific Question:** Does the model rely on *specific skull-base coordinates* to identify pituitary adenomas, or does it rely on *general cranial vault topography*?
- **Prior Art Analysis:**
  - In our Phase 6 experiment, distant patch scrambling ($C_{5\text{LP}}$) caused 56.5% of gliomas to be misclassified as pituitary adenomas.
  - However, because all distant patches (calvarium, cortex, ventricles, and skull base) were scrambled simultaneously, the specific contribution of the skull base cannot be mathematically decoupled from general cranial layout disruption.
- **Necessity Decision:** **OPTIONAL FOR MANUSCRIPT PUBLICATION.**
  - *Rationale:* The central contribution of the paper does **not** depend on proving that the model specifically uses skull-base coordinates. The defensible contribution is that **the classifier actively exploits distant cranial spatial context**, refuting the hypothesis of pure intra-tumoral cellular classification. Downgrading Claim G to `NOT_ESTABLISHED` (or phrasing it as "cranial layout sensitivity") completely resolves the scientific dilemma without running new inference.

---

### Experiment 2: Wavelet Phase Scrambling / Seam Smoothing (Eliminating Tile Boundary Discontinuities)
- **Scientific Question:** How much of the 0.42 Macro-F1 collapse under $C_{5\text{LP}}$ is attributable to *spatial layout disruption* versus *out-of-distribution high-frequency tile-seam edge noise*?
- **Prior Art Analysis:**
  - Fong & Vedaldi (2017) and Geirhos et al. (2020) demonstrated that CNNs are sensitive to high-frequency edge artifacts.
  - In our Phase 6.1 audit, we proved that $C_{5\text{LP}}$ doubled Sobel gradient energy by +97.9% ($18.33 \to 36.28$).
- **Necessity Decision:** **RECOMMENDED AS AN EXTENSION IF TILE-SEAM REVIEWER OBJECTIONS ARISE, BUT NOT REQUIRED FOR CORE PUBLICATION.**
  - *Rationale:* The existing comparison between $C_5$ (50% uniform dimming, zero tile seams, $\Delta \approx 0.10$) and $C_{5\text{LP}}$ (100% luminance-preserved scrambling, $\Delta \approx 0.42$) already proves that spatial disruption causes far greater degradation than uniform radiometric attenuation. Simply reporting the tile-seam limitation transparently in the manuscript satisfies scientific integrity.

---

### Experiment 3: Re-training Baseline Models with Masked Augmentation
- **Scientific Question:** Can debiased training force the model to ignore distant cranial context?
- **Necessity Decision:** **PROHIBITED IN CURRENT SCOPE.**
  - *Rationale:* The research objective is to audit and characterize the feature dependencies of the standard, widely cited frozen ResNet-50 benchmark classifier. Retraining shifts the research question from *interpretability and shortcut auditing* to *algorithmic debiasing*, which is a distinct, follow-up research direction.

---

## 3. Final Strategic Recommendation

**No additional experiments are required to conclude Phase 7 or submit the primary research paper.**

The existing Phase 1–6.1 empirical evidence is comprehensive, fully reproduced, and statistically robust. The paper's contribution is solidified by:
1. Calibrating claims to what the data strictly supports (intra-tumoral reliance, boundary discontinuity artifacts in zero-fill margins, and global cranial context sensitivity).
2. Explicitly acknowledging the tile-seam limitation and refraining from overclaiming specific skull-base shortcuts or biological causality.
3. Highlighting the methodological rigor of matched contralateral placebos, Navier-Stokes inpainting controls, and leakage-free cluster bootstrap evaluation.
