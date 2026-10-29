# Figure Caption & Scientific Explanation Audit

**Date:** 2026-10-29 (Updated 2026-10-30)  
**Purpose:** Ensure each publication figure contains a rigorous caption explaining all panels, sample sizes, uncertainty metrics, and calibrated scientific takeaways.

---

### Figure 1: Study Design & Sham-Controlled Counterfactual Intervention Pipeline
- **Caption:** Flowchart depicting the multi-stage research methodology. **(A)** Ingestion and provenance audit of the Cheng ($N=3,064$) and BRISC ($N=6,000$) datasets, including patient-isolated cross-validation and perceptual hash deduplication. **(B)** Five-region topological decomposition: tumour core ($R_{\text{core}}$), immediate peritumoral margin ($R_{\text{immediate}}$, 4px ring), outer peritumoral margin ($R_{\text{outer}}$, 12px ring), remote brain parenchyma ($R_{\text{remote}}$), and area/contour-matched contralateral sham control ($R_{\text{sham}}$). **(C)** Dual perturbation engines (Method A: Telea boundary PDE inpainting; Method B: locally matched Gaussian texture fill) enforcing bitwise non-target pixel invariance. **(D)** Paired model evaluation across ResNet-50 and DeiT-Small architectures yielding raw evidence drop $\Delta_r$ and sham-corrected region sensitivity $\tau_r$.
- **Scientific Takeaway:** Provides a complete schematic of the experimental design, contrasting targeted anatomical edits against contralateral controls to isolate lesion-specific evidence from non-specific perturbation artifacts.

### Figure 2: Preprocessing Pipeline & Mask Geometric Alignment Verification
- **Caption:** Multi-panel validation of deterministic image standardization and binary mask integrity. **(A)** Raw contrast-enhanced slice with high-intensity outlier voxels. **(B)** Percentile intensity scaling $[P_1, P_{99}]$ mapping intracranial tissue to $[0.0, 1.0]$. **(C)** Aspect-ratio-preserving letterbox padding to standardized $224 \times 224$ dimensions. **(D)** Overlay of original ground-truth contour (red) and letterboxed nearest-neighbor mask (green), demonstrating sub-pixel geometric alignment (centroid drift $< 0.0035$, zero lost masks).
- **Scientific Takeaway:** Confirms that network inputs preserve native aspect ratios, contrast dynamics, and boundary geometry without introducing interpolation artifacts into segmentation masks.

### Figure 3: Reliability Diagrams & Calibration Curves
- **Caption:** Probability calibration analysis across deep architectures and evaluation benchmarks. Top row: Reliability diagrams (10 probability bins) for ResNet-50 on Cheng patient held-out Fold 1 validation (Expected Calibration Error: 0.1835) and BRISC clean test set (ECE: 0.3113). Bottom row: Reliability diagrams for DeiT-Small on Cheng (ECE: 0.0366) and BRISC clean test set (ECE: 0.0767). Dashed diagonal represents perfect calibration; shaded bars indicate empirical sample frequencies.
- **Scientific Takeaway:** DeiT-Small achieves dramatically superior probability calibration across both datasets, whereas ResNet-50 displays severe overconfidence, underestimating prediction uncertainty.

### Figure 4: Regional Evidence Sensitivity Across Architectures (Method A: Inpainting)
- **Caption:** Bar plot comparing sham-corrected region sensitivity ($\tau_r = \Delta_r - \Delta_{\text{sham}}$) across anatomical regions under Method A (Telea PDE inpainting). Error bars represent standard errors of the mean (SEM) across paired test slices. Asterisks denote statistical significance from two-sided paired Wilcoxon signed-rank tests ($***p < 0.001$, $*p < 0.05$, n.s. non-significant).
- **Scientific Takeaway:** Demonstrates that diagnostic evidence is concentrated in the lesion core and immediate margins ($\tau_{\text{core}} > \tau_{\text{immediate}}$), whereas remote parenchyma effects are negligible and non-significant ($p > 0.05$).

### Figure 5: Architectural Inductive Bias: ViT vs CNN Regional Sensitivity Profile (Method A)
- **Caption:** Paired sensitivity contrast plot ($\tau_{\text{ViT}} - \tau_{\text{CNN}}$) across anatomical regions under Method A (Telea inpainting, $N=90$ pooled slices). DeiT-Small exhibits significantly greater reliance on the tumour core than ResNet-50 ($+0.0738$, paired Wilcoxon $p = 0.0123$, Cohen's $d_z = 0.362$; cluster-robust $p = 0.0162$) and higher sensitivity to the immediate peritumoral margin ($+0.0166$), while remote context sensitivity differences remain indistinguishable from zero ($+0.0072$, $p = 0.9087$).
- **Scientific Takeaway:** Highlights that global self-attention allows Vision Transformers to extract richer intra-lesion core and transitional margin representations without succumbing to distant cranial background shortcuts.

### Figure 6: Perturbation Method Concordance: Telea Inpaint vs Matched Texture Fill
- **Caption:** Comparative sensitivity across perturbation mechanisms for ResNet-50 **(A)** and DeiT-Small **(B)** across anatomical regions. DeiT-Small shows high cross-method correlation on core evidence ($r = 0.881$ on Cheng, $r = 0.704$ on BRISC). Pooled Cheng core correlation is $r = 0.748$ ($\rho = 0.541$).
- **Scientific Takeaway:** Confirms that measured regional evidence hierarchies are concordant across distinct inpainting mechanisms, with attention models showing higher algorithm invariance than localized convolutional kernels.

### Figure 7: Imaging Plane Stratification of Regional Evidence (BRISC)
- **Caption:** Regional evidence sensitivity ($\tau_r$) stratified across orthogonal radiological acquisition planes in the BRISC dataset: Axial ($N=15$), Coronal ($N=15$), and Sagittal ($N=15$). All three planes independently preserve the hierarchy $\tau_{\text{core}} > \tau_{\text{immediate}} > \tau_{\text{remote}}$.
- **Scientific Takeaway:** Demonstrates that the directional evidence hierarchy is consistently observed across orthogonal imaging planes and scanner viewing orientations.

### Figure 8: Class Heterogeneity in Peritumoral vs Core Evidence
- **Caption:** Comparative analysis of perilesional margin reliance across tumour classes. Mean sham-corrected sensitivities for core and immediate margin across Gliomas ($N=15$, margin-to-core ratio: 35.0%), Meningiomas ($N=15$, ratio: 33.1%), and Pituitary adenomas ($N=15$, ratio: 15.1%).
- **Scientific Takeaway:** Reflects clinical radiological features: diffusely infiltrative gliomas and dural-invasive meningiomas demonstrate substantial margin dependence, whereas sellar-confined pituitary adenomas depend almost exclusively on intra-lesion core cues.

### Figure 9: Impact of Train-Test Duplicate Leakage on Benchmark Evaluation (BRISC)
- **Caption:** Benchmark comparison between the Contaminated Official Benchmark ($N=1,000$, containing 10.1% identical training duplicates in the archive release) and the Clean De-duplicated Test Set ($N=899$) across DeiT-Small **(A)** and ResNet-50 **(B)** for Accuracy, Balanced Accuracy, and Macro-F1. Deduplication shifted class balance (meningiomas reduced from 30.6% to 23.4%), causing Macro-F1 to increase from 0.3566 to 0.5999 for DeiT-Small and from 0.3460 to 0.4181 for ResNet-50.
- **Scientific Takeaway:** Demonstrates that duplicate leakage severely distorts multi-class benchmark evaluations primarily through class-prior shifts rather than uniform performance inflation.

### Figure 10: Counterfactual Intervention & Residual Montage Gallery
- **Caption:** High-resolution 8-panel diagnostic montage for representative CE-MRI slices. Panels: **(A)** Original contrast-enhanced slice. **(B)** Five-region topological overlay (Core, Immediate, Outer, Remote, Sham). **(C)** Method A (Telea) core inpainting. **(D)** Method A sham inpainting. **(E)** Method B (Texture) core fill. **(F)** Method B sham fill. **(G)** Method A residual map ($|x_{\text{edit}} - x| \times 5$). **(H)** Method B residual map, verifying bitwise zero difference outside target masks.
- **Scientific Takeaway:** Visually confirms intervention realism, seamless edge blending, and 100% mathematical preservation of non-target intracranial anatomy.
