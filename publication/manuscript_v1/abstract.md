# Abstract

**Title:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Study

**Authors:** [Author Names Anonymized for Peer Review]

---

## 1. Journal Submission Abstract (Structured, 244 Words — Springer JIIM / MBEC Compliant)

- **Purpose:** Deep convolutional neural networks achieve high diagnostic accuracy in brain tumour MRI classification, but may exploit non-tumour context shortcuts. While spatial tile scrambling severely degrades model performance, it inadvertently injects synthetic high-frequency boundary seams. We investigate whether this performance collapse reflects genuine reliance on macroscopic cranial layout or an artifactual vulnerability to artificial edge discontinuities.
- **Methods:** On the 3,064-slice Cheng Figshare dataset (233 patient clusters; meningioma, glioma, pituitary tumour), 15 frozen ResNet-50 checkpoints were evaluated across three patient-aware cross-validation scenarios ($S_0, S_1, S_2$) under matched conditions: original baseline ($C_0$), seam-only control ($C_1$), seam-suppressed spatial rearrangement ($C_2$), and raw tile scrambling ($C_3$), alongside a pure boundary-step control leaving tile interiors 100% untouched. Tumour core and 15-pixel margin rings were bit-for-bit protected. Uncertainty was quantified using synchronized paired patient-cluster bootstrapping ($B=25,000$) with Holm-Bonferroni FWER control.
- **Results:** Raw tile scrambling degraded Macro-F1 from 0.9333 to 0.5118 ($\Delta = +0.4215$, $p < 10^{-15}$). Pure boundary-seam steps alone induced a modest drop ($\Delta = +0.1206$), while historical DC offsets reduced Macro-F1 to 0.6290 ($\Delta = +0.3043$). Crucially, seam-suppressed tile permutation ($C_2$) still caused a severe collapse to 0.4525 ($\Delta = +0.4808$, 95% CI: $[0.4360, 0.5280]$)—fourfold larger than boundary seams alone. Spatial scrambling flipped 63.5% of true supratentorial gliomas to skull-base pituitary tumour.
- **Conclusion:** Performance degradation is governed by a dual-factor mechanism: while CNNs exhibit measurable sensitivity to high-frequency seams, macroscopic cranial layout is independently essential for classification. Destroying anatomical geometry collapses the classifier into skull-base priors. Spatial perturbation studies must explicitly control for synthetic seams.

**Keywords:** Brain tumour classification; Convolutional neural networks; Magnetic resonance imaging; Shortcut learning; Spatial context; Image perturbation; Artifact disentanglement; Reproducibility.

---

## 2. Extended Comprehensive Abstract (Archival / Preprint)

### Background
Deep neural networks achieve high diagnostic accuracy in brain tumour MRI classification, yet emerging evidence warns that high performance can be inflated by shortcut learning on non-tumour image features. Spatial perturbation studies, such as tile scrambling, have reported severe performance collapses when distant cranial contexts are rearranged, suggesting heavy model reliance on macroscopic anatomical layout. However, spatial tile scrambling simultaneously introduces prominent synthetic high-frequency step discontinuities along tile seams, creating a critical methodological confound: does the model failure reflect true reliance on cranial spatial organization, or is it an artifactual vulnerability to synthetic edge discontinuities?

### Methods
We conducted a controlled, preregistered multi-intervention study on the Cheng Figshare brain tumour MRI cohort (3,064 2D T1-contrast-enhanced slices across 233 patient clusters, encompassing meningioma, glioma, and pituitary tumour). Using 15 frozen ResNet-50 checkpoints evaluated across three cross-validation scenarios ($S_0$: patient-disjoint, $S_1$: near-duplicate cleaned at SSIM 0.80, and $S_2$: aggressive grouping at SSIM 0.75), we operationalized four matched conditions: (1) $C_0$ original baseline; (2) $C_1$ seam-only control, injecting boundary step discontinuities matching scrambled DC offsets onto unpermuted anatomy; (3) $C_2$ seam-suppressed spatial rearrangement, permuting distant tiles while cross-fading seams (suppressing boundary Sobel energy by 54.8% and excess high-frequency Fourier energy by 84.9%); and (4) $C_3$ raw tile scrambling, supplemented by True Seam controls ($w=2, 3$) modifying strictly boundary pixels. In all conditions, the tumour core and a 15-pixel dilation margin ring were 100% protected (zero pixels altered). Across 36,768 matched out-of-fold forward evaluations, uncertainty was quantified using synchronized paired cluster bootstrapping ($B=25,000$ resamples) and Holm-Bonferroni Family-Wise Error Rate (FWER) multiplicity control.

### Results
In the patient-disjoint split ($S_0$), the raw scrambling drop replicated with high fidelity ($\Delta \text{Macro-F1} = +0.4215$, 95% CI: $[0.3722, 0.4713]$, $p < 10^{-15}$). Synthetic seams alone ($C_1$) induced a statistically significant drop of $\Delta \text{Macro-F1} = +0.3043$ (95% CI: $[0.2581, 0.3530]$, $p < 10^{-15}$), while pure 2-pixel boundary steps dropped Macro-F1 to 0.8127 ($\Delta = +0.1206$). Crucially, seam-suppressed tile permutation ($C_2$) still caused a severe performance collapse of $\Delta \text{Macro-F1} = +0.4808$ (95% CI: $[0.4360, 0.5280]$, $p < 10^{-15}$), far exceeding our preregistered practical significance threshold of $0.150$ and exceeding the pure boundary seam effect by fourfold. Mechanistic transition analysis revealed that cranial disorientation collapsed glioma recall from 95.0% to 8.6%, with 63.5% of gliomas misclassified as pituitary tumour—a skull-base lesion.

### Conclusions
Our findings demonstrate that performance collapse under tile scrambling is driven by a mixed mechanism: while artificial boundary discontinuities alone degrade CNN feature extraction, macroscopic spatial layout is independently essential for brain tumour classification in this architecture. Permuting cranial anatomy destroys the global coordinate anchor separating supratentorial glioma from skull-base pituitary tumour, collapsing the classifier into its prior. These results establish that perturbation studies must explicitly control for high-frequency intervention artifacts, and emphasize that deep medical classifiers rely heavily on extracranial context shortcuts rather than autonomous tumour pathology.
