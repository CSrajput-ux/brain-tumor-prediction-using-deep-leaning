# Minimum Experiment Decision & Resource Justification

**Document ID:** `MINIMUM_EXPERIMENT_DECISION`  
**Phase:** 8 — Deep Novelty Discovery, Research Redesign & Contribution Validation  
**Date:** 2026-10-17  
**Authoritative Standard:** Falsifiable Experimental Parsimony & Confound Isolation  

---

## 1. Executive Decision on Experimental Execution

### **Core Ruling:**
**NO EXPERIMENTS ARE AUTHORIZED OR EXECUTED DURING PHASE 8.**

Phase 8 is strictly dedicated to deep novelty discovery, research redesign, prior-art auditing, and preregistration drafting. 

This document establishes the precise boundary between:
1. Questions that are **already decisively resolved** from existing Phase 1–7 evidence and literature.
2. The **single minimum decisive experiment** that would be required if the project owner authorizes experimental Phase 9.
3. Unnecessary or ill-posed experiments that must be explicitly rejected.

---

## 2. What is Already Answered from Literature and Existing Repository Evidence

The following questions require **zero new experiments**:

| Scientific Question | Resolution Source | Decisive Evidence Already Established |
| :--- | :--- | :--- |
| **Intra-Tumoral Reliance** | Phase 6 & Phase 6.1 audits; Bissoto (2019) | Net tumor reliance is $+0.1045$ ($p < 10^{-65}$). Contralateral placebo drop is only $+0.0114$. Proved conclusively that intra-tumoral features are the dominant classification driver. |
| **Perilesional Margin Step-Edge Artifact** | Phase 6 Navier-Stokes inpainting; Fong & Vedaldi (2017) | Navier-Stokes inpainting reduces boundary step gradients by 83.6% ($236.7 \to 38.9$) and completely eliminates the margin performance drop ($\Delta \le 0.0077$, CI spans zero). Proves that zero-fill margin drops were edge artifacts. |
| **Margin Thickness Dose-Response** | Phase 6 parametric sweep ($r=5,10,15,20\text{px}$) | Proved that margin reliance does not increase monotonically with thickness; wider radii ablate normal cortex in contralateral controls. |
| **Radiometric Brightness vs Context** | Phase 6 Luminance-Preserved Scrambling ($C_{5\text{LP}}$) | Holding global mean and variance 100% bit-constant still produces a 4-fold worse collapse ($\Delta \approx +0.42$) than 50% uniform dimming ($\Delta \approx +0.10$). Proves that dimming was not the primary driver of the distant drop. |
| **Benchmark Leakage Sensitivity** | Phase 2 baseline; Vangala et al. (2026) | All results reproduce consistently across $S_0$ (strict patient split), $S_1$ (SSIM 0.80), and $S_2$ (SSIM 0.75), demonstrating that findings are not artifacts of near-duplicate leakage. |

---

## 3. The Single Minimum Decisive Experiment (If Authorized for Phase 9)

### The Unresolved Question:
> *"Does the $\Delta \approx +0.42$ collapse under patch scrambling reflect true reliance on macroscopic cranial layout, or is it an artifact of the +97.9% spike in high-frequency tile-seam edge noise?"*

### Why Literature Alone Cannot Resolve This:
While computer vision literature (e.g., Wang et al., 2020) proves that CNNs are sensitive to high-frequency periodic patterns, no existing study has measured how much of the $C_{5\text{LP}}$ collapse in brain MRI is attributable to tile seams versus cranial layout.

### The Minimum Experimental Design:
Rather than generating an expansive, unfocused experimental battery, exactly **one controlled pair of conditions** is needed:

1. **Condition 1: Seamless Frequency-Matched Distant Permutation ($I_{\text{seamless}}$):**
   - Non-tumor distant tiles are permuted to disrupt macroscopic spatial layout.
   - Boundaries between tiles are blended via Poisson reconstruction (or spatial phase coefficients are shuffled in low-frequency wavelet sub-bands).
   - *Invariants:* Mean intensity matches $I_{\text{orig}}$ ($\pm 0.5\%$), variance matches ($\pm 0.5\%$), and whole-image Sobel gradient energy matches $I_{\text{orig}}$ ($\pm 10\%$). Exactly 0 tumor pixels altered.
2. **Condition 2: Synthetic Seam-Noise Control on Unpermuted Images ($I_{\text{seam\_only}}$):**
   - The unmanipulated image $I_{\text{orig}}$ has artificial grid seams added at the exact same $16 \times 16$ tile boundaries without permuting any spatial content.
   - Matches the Sobel energy spike of $C_{5\text{LP}}$ (+97.9%) while keeping macroscopic anatomy 100% intact.

### How This Isolates the Rival Explanations:
$$\Delta_{\text{total}} = \underbrace{\Delta_{\text{layout}}}_{I_{\text{orig}} - I_{\text{seamless}}} + \underbrace{\Delta_{\text{seam\_artifact}}}_{I_{\text{orig}} - I_{\text{seam\_only}}}$$

- If $\Delta_{\text{seamless}} \ge 0.20$ and $\Delta_{\text{seam\_only}} \le 0.05$: **Cranial landmark layout reliance is conclusively confirmed.**
- If $\Delta_{\text{seamless}} \le 0.05$ and $\Delta_{\text{seam\_only}} \ge 0.35$: **The scrambling result was entirely an edge-noise artifact.**
- If both are moderate ($\sim 0.15$): **Both factors contribute in quantifiable proportions.**

---

## 4. Distinction Between Removal and Synthetic Replacement in Inpainting

A critical review question addresses perilesional margin inpainting ($C_{3\text{NS}}$):
> *"Does inpainting show that margin tissue has no evidence, or does it replace real evidence with synthetic evidence that tricks the model?"*

### Literature-Backed Distinction:
- Navier-Stokes inpainting does **not** generate novel complex biological textures; it solves a partial differential equation (PDE) that smoothly transports surrounding pixel intensities into the target ring along isophote lines.
- It restores mathematical continuity (suppressing the boundary step gradient from $236.7$ to $38.9$).
- If the deep classifier relied on specialized histological or parenchymal features (such as subtle edema margins or micro-infiltration gradients) that were wiped out by inpainting, the model’s performance would drop regardless of boundary smoothness.
- The fact that $C_{3\text{NS}}$ achieves **identical Macro-F1 to unmanipulated original images** ($\Delta = -0.0016$ in S0, $+0.0002$ in S2) proves that the ResNet-50 model never required specialized parenchymal margin textures; it only required the absence of an artificial step-edge discontinuity.

---

## 5. Rejected Experimental Proposals

The following experiments were considered and **formally rejected**:

1. **Retraining 15 New Models with Heavy Augmentations:**  
   *Reason for Rejection:* Violates the research question, which investigates what the *current* standard benchmark models have learned. Retraining changes the inductive bias and does not explain the frozen model.
2. **Training Vision Transformers (ViTs):**  
   *Reason for Rejection:* Does not resolve whether the ResNet-50 results are sound; simply expands computational scope without resolving the primary confound.
3. **Evaluating Cross-Dataset Transfer on BraTS:**  
   *Reason for Rejection:* Incompatible label spaces (BraTS is 100% glioma; lacks pituitary adenomas and meningiomas) and prohibitive computational cost.
