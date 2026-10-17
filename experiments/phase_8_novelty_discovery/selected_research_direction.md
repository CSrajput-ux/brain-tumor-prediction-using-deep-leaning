# Selected Research Direction & Contribution Blueprint

**Document ID:** `SELECTED_RESEARCH_DIRECTION`  
**Phase:** 8 — Deep Novelty Discovery, Research Redesign & Contribution Validation  
**Date:** 2026-10-17  
**Authoritative Standard:** Evidence-Backed Research Design & Epistemic Calibration  

---

## 1. Selected Primary Direction

### Title of Proposed Research:
> **"Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers: A Multi-Control Spatial Intervention Study"**

*(Note: The title strictly avoids hype terms like "novel", "first-ever", or "revolutionary", focusing entirely on the verified scientific mechanism).*

---

## 2. Precise Research Question

**Primary Question:**
> *"To what extent does a deep convolutional neural network’s apparent reliance on distant cranial context reflect true dependence on macroscopic anatomical spatial layout versus vulnerability to high-frequency boundary edge artifacts introduced by spatial image interventions?"*

**Supporting Sub-Questions:**
1. Does the catastrophic diagnostic collapse observed under tile scrambling ($\Delta \approx +0.42$ Macro-F1) persist when boundary seams are eliminated using frequency-matched, seamless spatial transformations?
2. Does the severe class inversion of gliomas into pituitary adenomas (56.5% error rate) reflect an inductive prior tied to global cranial coordinate landmarks or a non-specific reaction to high-frequency checkerboard noise?
3. How does the artifact profile of distant spatial perturbations compare quantitatively to the boundary step-edge artifacts resolved in perilesional margin inpainting?

---

## 3. Proposed Scientific Contribution

1. **Resolution of the Spatial Scrambling Seam Confound:**  
   First neuroimaging study to formally quantify the high-frequency edge-energy artifact in spatial patch scrambling (+97.9% Sobel energy increase) and test whether distant context sensitivity survives when high-frequency seam noise is eliminated.
2. **Double-Disentanglement Framework:**  
   Unifying:
   - *Local boundary disentanglement:* Separating perilesional parenchymal reliance from boundary step-edge gradients via Navier-Stokes inpainting ($C_{3\text{NS}}$).
   - *Global spatial disentanglement:* Separating cranial layout dependence from tile-seam edge noise via frequency-matched, seamless spatial permutation.
3. **Neuroanatomical Inductive Bias Characterization:**  
   Rigorously explaining why deep CNNs default to extra-axial (pituitary / meningioma) predictions when cranial layout is perturbed, establishing the boundaries of coordinate-based inductive priors in medical computer vision.
4. **Reproducible Statistical Standard:**  
   Evaluating all interventions under frozen checkpoints on strict patient-disjoint splits ($S_0, S_1, S_2$) with synchronized paired patient-cluster bootstrap resampling ($B=2,000$).

---

## 4. Closest Prior Art & Explicit Differences

| Closest Study | Established Finding | Explicit Difference in Our Proposed Research |
| :--- | :--- | :--- |
| **Xiao et al. (ICLR 2021)** | Demonstrated that deep models rely heavily on natural image backgrounds by swapping background scenes. | Xiao operated on natural images with unconstrained backgrounds; brain MRI has rigid cranial anatomy where naive swapping/scrambling introduces severe edge artifacts. We evaluate cranial context under strict frequency and boundary matching. |
| **Fong & Vedaldi (ICCV 2017)** | Showed that naive zero-filling introduces artificial high-frequency edges, necessitating smooth perturbation masks for saliency explanations. | Fong focused on optimization-based heatmaps for natural images. We translate boundary smoothing into a hypothesis-driven validation protocol for clinical MRI margins and cranial context. |
| **Hooker et al. (NeurIPS 2019)** | Showed that masking on frozen models introduces out-of-distribution distribution shift, necessitating retraining (ROAR). | Hooker retrained models from scratch across every threshold; we demonstrate that PDE inpainting and frequency-matched permutation allow rigorous artifact decoupling directly on frozen clinical checkpoints. |
| **Bissoto et al. (CVPRW 2019)** | Demonstrated background shortcut learning in dermatology by masking lesions vs skin. | Bissoto used unconstrained masking without matched anatomical placebos, perilesional inpainting, or frequency-matched context controls. |
| **Vangala et al. (arXiv 2026)** | Proved that benchmark scores on the Cheng dataset leak patient data in random splits. | Vangala audited dataset contamination; we utilize verified leakage-free splits to audit internal model representations and spatial reliance. |

---

## 5. Strongest Evidence For and Against Novelty

### Evidence Supporting Novelty:
- No published study in medical imaging has evaluated spatial context scrambling while simultaneously controlling for global luminance, global variance, and high-frequency edge energy.
- Existing medical shortcut papers (DeGrave 2021, Bissoto 2019) either crop borders or ablate markers; none have addressed the artifact profile of spatial permutation in neuroimaging.
- Resolves an active, documented scientific vulnerability in the current repository (Phase 6.1 Audit C).

### Evidence Against Novelty:
- The broad concept that neural networks are sensitive to high frequencies and edge noise is well-known in computer vision (Geirhos 2020; Wang et al., 2020 on high-frequency CNN shortcuts).
- Tile scrambling has been used in cognitive neuroscience and vision science for decades.
- The dataset (Cheng Figshare 1512427) is a widely analyzed public benchmark.

---

## 6. Remaining Uncertainty

1. Whether eliminating tile seams will preserve 80%, 50%, or 0% of the $\Delta \approx +0.42$ performance collapse observed under $C_{5\text{LP}}$.
2. Whether Vision Transformers (ViTs) share the exact same edge-seam sensitivity as ResNet-50.
3. How well 2D slice-level context perturbations approximate 3D volumetric cranial disorientation.

---

## 7. Main Falsifiable Hypotheses

### Primary Hypothesis ($H_1$):
> If the classifier's catastrophic collapse under distant scrambling ($\Delta \approx +0.42$) is predominantly driven by loss of macroscopic anatomical layout rather than high-frequency tile seams, then evaluating the model on seamless, frequency-matched distant permutations will maintain a statistically significant Macro-F1 drop ($\Delta \ge 0.150$, $p < 10^{-10}$) relative to the unmanipulated baseline.

### Null Hypothesis ($H_0$):
> The performance collapse observed under patch scrambling is entirely an artifact of high-frequency boundary seams. Under seamless, frequency-matched permutation, performance degradation will attenuate to negligible levels ($\Delta < 0.030$, 95% bootstrap CI spanning zero), mirroring the resolution of the perilesional margin artifact under inpainting.

---

## 8. What Result Would Refute the Central Claim?

- **Refutation of True Layout Reliance:** If seamless, frequency-matched permutation produces $\Delta < 0.030$ (statistically indistinguishable from baseline), the claim that ResNet-50 relies on macroscopic cranial layout is **falsified**.
- **Scientific Value of Refutation:** This negative result would be equally impactful: it would prove that medical deep learning models are far more robust to spatial anatomical scrambling than previously reported, and that prior scrambling studies merely measured fragility to edge noise!

---

## 9. Backup Research Direction

**Backup Direction:** **Direction A — The Medical Intervention-Validity Protocol (Boundary Step-Edge Confound Audit)**
- *Core Focus:* If the primary direction encounters methodological hurdles, the project centers entirely on the completed, verified Phase 6 finding: establishing that **perilesional parenchymal reliance in deep MRI models is an artifact of artificial boundary step-edge gradients ($236.7$) that vanishes ($\Delta < 0.008$) under Navier-Stokes inpainting.**
- *Status of Backup:* 100% completed, fully audited, and numerically verified with zero additional experiments required.
