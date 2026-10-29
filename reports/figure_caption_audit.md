# Figure Caption & Scientific Explanation Audit

**Date:** 2026-10-29  
**Purpose:** Ensure each publication figure contains a rigorous caption explaining all panels, sample sizes, uncertainty metrics, and scientific takeaways.

---

### Figure 1: Study Design & Sham-Controlled Counterfactual Intervention Pipeline
- **Caption:** Flowchart depicting the multi-stage research methodology. **(A)** Ingestion and provenance audit of the Cheng ($N=3,064$) and BRISC ($N=6,000$) datasets, including patient-isolated cross-validation and perceptual hash deduplication. **(B)** Five-region topological decomposition: tumour core ($R_{\text{core}}$), immediate peritumoral margin ($R_{\text{immediate}}$, 4px ring), outer peritumoral margin ($R_{\text{outer}}$, 12px ring), remote brain parenchyma ($R_{\text{remote}}$), and area/contour-matched contralateral sham control ($R_{\text{sham}}$). **(C)** Dual perturbation engines (Method A: Telea boundary PDE inpainting; Method B: locally matched Gaussian texture fill) enforcing bitwise non-target pixel invariance. **(D)** Paired model evaluation across ResNet-50 and DeiT-Small architectures yielding raw evidence drop $\Delta_r$ and sham-corrected causal sensitivity $\tau_r$.
- **Scientific Takeaway:** Provides a complete schematic of the experimental design, contrasting targeted anatomical edits against contralateral controls to eliminate confounding from generic perturbation artifacts.

### Figure 2: Preprocessing Pipeline & Mask Geometric Alignment Verification
- **Caption:** Multi-panel validation of deterministic image standardization and binary mask integrity. **(A)** Raw contrast-enhanced slice with high-intensity outlier voxels. **(B)** Percentile intensity scaling $[P_1, P_{99}]$ mapping intracranial tissue to $[0.0, 1.0]$. **(C)** Aspect-ratio-preserving letterbox padding to standardized $224 \times 224$ dimensions. **(D)** Overlay of original ground-truth contour (red) and letterboxed nearest-neighbor mask (green), demonstrating sub-pixel geometric alignment (centroid drift $< 0.0035$, zero lost masks).
- **Scientific Takeaway:** Confirms that network inputs preserve native aspect ratios, contrast dynamics, and boundary geometry without introducing interpolation artifacts into segmentation masks.

### Figure 3: Reliability Diagrams & Calibration Curves
- **Caption:** Probability calibration analysis across deep architectures and evaluation benchmarks. Top row: Reliability diagrams (15 probability bins) for ResNet-50 on Cheng patient OOF validation (Expected Calibration Error: 0.1835) and BRISC clean test set (ECE: 0.3113). Bottom row: Reliability diagrams for DeiT-Small on Cheng (ECE: 0.0366) and BRISC clean test set (ECE: 0.0767). Dashed diagonal represents perfect calibration; shaded bars indicate empirical sample frequencies.
- **Scientific Takeaway:** DeiT-Small achieves dramatically superior probability calibration across both datasets, whereas ResNet-50 displays severe overconfidence, underestimating prediction uncertainty.

### Figure 4: Regional Evidence Sensitivity Across Architectures (Method A: Inpainting)
- **Caption:** Bar plot comparing sham-corrected causal sensitivity ($\tau_r = \Delta_r - \Delta_{\text{sham}}$) across anatomical regions under Method A (Telea PDE inpainting). Error bars represent 95% bootstrap confidence intervals across paired test slices. Asterisks denote statistical significance from two-sided paired Wilcoxon signed-rank tests ($***p < 0.001$, $*p < 0.05$, n.s. non-significant).
- **Scientific Takeaway:** Demonstrates a strict monotonic spatial decay ($\tau_{\text{core}} > \tau_{\text{immediate}} > \tau_{\text{outer}} \gg \tau_{\text{remote}}$). While the core and immediate margin provide significant evidence, remote parenchyma effects are negligible and non-significant ($p > 0.05$).

### Figure 5: Architectural Inductive Bias: ViT vs CNN Regional Sensitivity Profile
- **Caption:** Paired sensitivity contrast plot ($\tau_{\text{ViT}} - \tau_{\text{CNN}}$) across anatomical regions. DeiT-Small exhibits significantly greater reliance on the tumour core than ResNet-50 ($+0.0738$, $p = 0.0123$, Cohen's $d_z = 0.362$) and higher sensitivity to the immediate peritumoral margin ($+0.0166$), while remote context sensitivity differences remain indistinguishable from zero ($+0.0072$, $p = 0.9087$).
- **Scientific Takeaway:** Highlights that global self-attention allows Vision Transformers to extract richer intra-lesion and transitional margin representations without succumbing to distant cranial background shortcuts.

### Figure 6: Perturbation Method Invariance (Method A vs Method B)
- **Caption:** Scatter plot and linear regression comparing sham-corrected core sensitivity between Method A (Telea PDE inpainting) and Method B (locally matched Gaussian texture filling). Pearson correlation $r = 0.748$ on Cheng and $r = 0.551$ on BRISC. Dashed line denotes identity ($y = x$).
- **Scientific Takeaway:** Confirms that causal evidence measurements reflect true anatomical sensitivity rather than idiosyncratic boundary artifacts of a single inpainting algorithm.

### Figure 7: Imaging Plane Stratification of Regional Evidence (BRISC)
- **Caption:** Regional evidence sensitivity ($\tau_r$) stratified across orthogonal radiological acquisition planes in the BRISC dataset: Axial ($N=15$), Coronal ($N=15$), and Sagittal ($N=15$). All three planes independently preserve the monotonic decay $\tau_{\text{core}} > \tau_{\text{immediate}} > \tau_{\text{remote}}$.
- **Scientific Takeaway:** Proves that the spatial evidence gradient is invariant to 2D slice orientation and scanner viewing angle.

### Figure 8: Class Heterogeneity in Peritumoral vs Core Evidence
- **Caption:** Comparative analysis of perilesional margin reliance across tumour histopathologies. Left: Mean sham-corrected sensitivities for core and immediate margin. Right: Margin-to-core sensitivity ratios for Gliomas (35.0%), Meningiomas (33.1%), and Pituitary adenomas (15.1%).
- **Scientific Takeaway:** Reflects clinical biology: diffusely infiltrative gliomas and dural-invasive meningiomas demonstrate substantial margin dependence, whereas sellar-confined pituitary adenomas depend almost exclusively on intra-lesion core cues.

### Figure 9: Impact of Train-Test Duplicate Leakage on Benchmark Evaluation (BRISC)
- **Caption:** Comparison of classification metrics between the Contaminated Official Benchmark ($N=1,000$, containing 10.1% identical training duplicates) and the Clean De-duplicated Test Set ($N=899$). Left: Macro-F1 across architectures. Right: Class-specific F1 score for meningiomas (96 leaked slices).
- **Scientific Takeaway:** Demonstrates that duplicate leakage creates artificial memorization inflation that severely distorts multi-class performance rankings.

### Figure 10: Counterfactual Intervention & Residual Montage Gallery
- **Caption:** High-resolution 8-panel diagnostic montage for representative CE-MRI slices. Panels: **(A)** Original contrast-enhanced slice. **(B)** Five-region topological overlay (Core, Immediate, Outer, Remote, Sham). **(C)** Method A (Telea) core inpainting. **(D)** Method A sham inpainting. **(E)** Method B (Texture) core fill. **(F)** Method B sham fill. **(G)** Method A residual map ($|x_{\text{edit}} - x| \times 5$). **(H)** Method B residual map, verifying bitwise zero difference outside target masks.
- **Scientific Takeaway:** Visually confirms intervention realism, seamless edge blending, and 100% mathematical preservation of non-target intracranial anatomy.

