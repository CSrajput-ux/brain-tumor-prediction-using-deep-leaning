# Limitations, Search Blind Spots, and Scientific Uncertainty

**Document ID:** `PHASE_7_LIMITATIONS_AND_UNCERTAINTY`  
**Phase:** 7 — Systematic Literature Review and Novelty Verification  
**Date:** 2026-10-17  
**Auditor:** Independent Scientific and Robustness Reviewer  

---

## 1. Search Coverage and Database Blind Spots

While this systematic review searched major scientific repositories (PubMed, Europe PMC, arXiv, OpenReview, IEEE Xplore, Google Scholar, and top-tier publisher archives), several inherent search limitations must be explicitly acknowledged:

1. **Proprietary Database Paywalls:**
   - Full automated text mining of Scopus and Web of Science was constrained by institutional API access limits. Although Crossref and Google Scholar captured the vast majority of cross-indexed literature, specialized regional medical imaging conference workshops (e.g., non-indexed workshop proceedings) may have escaped discovery.
2. **Terminology Divergence:**
   - The field of medical AI suffers from fragmented terminology. Relevant studies may describe spatial interventions using terms such as *"counterfactual editing," "region-of-interest ablation," "background masking," "saliency erasing," "feature occlusion," "adversarial patch removal,"* or *"inpainting-based explainability"* rather than *"shortcut learning"* or *"placebo control."* While our search queries were broadened across Families A–F, non-standard terminology remains an unavoidable blind spot.
3. **Publication Lag and Grey Literature:**
   - Preprints on arXiv, bioRxiv, and OpenReview reflect cutting-edge ML work as of late 2026, but unposted clinical conference abstracts (e.g., RSNA, ASNR) that have not deposited digital preprints are underrepresented.

---

## 2. Inherent Methodological Uncertainties

### A. The Epistemic Boundary of *In Silico* Image Interventions
- Image masking, inpainting, and patch scrambling are **algorithmic interventions in 2D pixel space**.
- They test the **inductive representations and decision surfaces of a specific deep neural network (ResNet-50)**.
- **Critical Uncertainty:** Image-level interventions can never prove or disprove human biological ground truth. Proving that a ResNet-50 classifier does not utilize perilesional margin texture does not mean that perilesional tissue lacks diagnostic histological value for a human neuropathologist evaluating whole-slide microscopy.

### B. The Navier-Stokes Inpainting Assumption
- Navier-Stokes inpainting propagates surrounding parenchymal texture into the 15-pixel margin, reducing the artificial step-edge gradient by 83.6% and restoring Macro-F1 to baseline levels ($\Delta < 0.008$).
- **Critical Uncertainty:** Inpainting synthesizes visually plausible textures based on surrounding normal brain parenchyma. If an infiltrative tumor had subtle biological penumbral changes that closely resembled normal parenchyma, Navier-Stokes inpainting would replace it with normal parenchyma without triggering a model drop. Thus, inpainting demonstrates that the network is satisfied by synthetic normal texture, but cannot definitively prove that biological infiltration is absent.

### C. The Tile-Seam Edge Confound in Distant Scrambling ($C_{5\text{LP}}$)
- In $C_{5\text{LP}}$, 16x16 patch permutation preserved 100% of global slice luminance and variance while causing a catastrophic 0.42 drop in Macro-F1 and a 56.5% misclassification of gliomas into pituitary adenomas.
- **Critical Uncertainty:** Patch permutation inevitably introduces artificial grid seams across the entire image, doubling Sobel high-frequency gradient energy (+97.9%). While this proves that the network's drop in Phase 5 was not merely a brightness dimming artifact, it leaves unresolved what fraction of the collapse is due to **loss of global anatomical landmarks** versus **sensitivity to artificial grid seam noise**.
