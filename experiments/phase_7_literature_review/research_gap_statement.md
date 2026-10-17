# Defensible Research Gap Statement

**Document ID:** `PHASE_7_RESEARCH_GAP_STATEMENT`  
**Phase:** 7 — Systematic Literature Review and Novelty Verification  
**Date:** 2026-10-17  
**Authoritative Standard:** Evidence-Backed Prior-Art Synthesis  

---

## The Core Research Gap

Although deep learning models for brain tumor MRI classification frequently report near-perfect test performance (>98%) on public benchmarks such as the Cheng Figshare dataset [Cheng et al., 2015; Vangala et al., 2026], the degree to which these models rely on genuine intra-tumoral pathological evidence versus surrounding brain parenchyma and distant cranial context remains poorly understood and critically confounded.

Existing literature suffers from three major unaddressed limitations:

1. **Uncontrolled Lesion Occlusion and Area Confounding:**
   Prior occlusion and lesion masking studies in medical imaging [Bissoto et al., 2019; DeGrave et al., 2021; Rossi et al., 2024] evaluate performance drops after masking diseased tissue without providing anatomically matched spatial placebo controls in unaffected tissue. Consequently, observed performance degradations cannot be cleanly separated from generic loss of image area, disruption of normal brain parenchyma, or non-specific reduction in feature activation volume.

2. **Confounding by Boundary Step-Edge Discontinuities in Perilesional Analysis:**
   While early computer-aided diagnosis studies proposed that dilating tumor margins into concentric rings captures peritumoral contextual cues [Cheng et al., 2015], modern deep learning evaluations that ablate perilesional margins using zero-filling introduce severe, unnatural high-frequency step discontinuities [Fong & Vedaldi, 2017]. Prior medical imaging literature has failed to determine whether observed perilesional margin effects reflect true reliance on parenchymal tissue texture or artifactual network vulnerability to sharp, artificial boundary gradients.

3. **Conflation of Distant Context Reliance with Global Radiometric Shift:**
   While deep neural networks are known to exploit global scene context [Xiao et al., 2021; Geirhos et al., 2020], existing studies testing context sensitivity in neuroimaging rely on uniform dimming, blurring, or cropping, which drastically alter global image luminance, contrast, and standard deviation. No prior brain MRI study has evaluated distant context reliance using a transformation that strictly preserves global image luminance and variance while perturbing spatial layout.

---

## Our Evidence-Backed Contribution

To address this gap, this study provides an independently audited, multi-control spatial intervention framework applied to frozen ResNet-50 classifiers across three leakage-free, patient-disjoint evaluation scenarios ($S_0, S_1, S_2$) on the Cheng benchmark. By coupling:
- **Intra-tumoral excision** against **matched contralateral focal placebos**,
- **Zero-fill perilesional margin ablation** against **Navier-Stokes PDE boundary inpainting**, and
- **Distant context dimming** against **luminance-preserved patch scrambling**,

evaluated with **synchronized paired patient-cluster bootstrap resampling ($B=2,000$)**, we demonstrate that:
1. Intra-tumoral reliance is decisive and robust ($\Delta \approx +0.104$ Macro-F1 net drop, $p < 10^{-65}$).
2. The apparent perilesional margin reliance ($\Delta \approx +0.025$) is an artifact of boundary step-edge discontinuities and vanishes ($\Delta < 0.008$) under smooth inpainting.
3. Distant spatial context provides an essential inductive prior separating intra-axial from extra-axial lesions, inducing severe diagnostic inversion when scrambled, which cannot be explained by global radiometric attenuation alone.
