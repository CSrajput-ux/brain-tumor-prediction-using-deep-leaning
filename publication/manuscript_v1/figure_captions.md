# Figure Captions

### Figure 1: Representative Brain MRI Slices and Tumour Mask Overlays Across Diagnostic Classes.
**(Top Row)** Genuine contrast-enhanced T1-weighted 2D axial MRI slices from the Cheng Figshare cohort (3,064 total slices across 233 patient clusters) representing the three target tumour pathologies: Meningioma (left), Glioma (center), and Pituitary Tumour (right).  
**(Bottom Row)** Corresponding anatomical overlays illustrating the established experimental protection geometry: the primary tumour core segmentation mask provided by the dataset annotators (red overlay) and the 15-pixel dilation margin ring (cyan overlay). Across all intervention conditions ($C_1, C_2, C_3$), exactly zero pixels were modified within the tumour core or dilation margin, ensuring that any observed classification degradation arises strictly from modifications to distant anatomical context.

---

### Figure 2: End-to-End Experimental Workflow and Disentanglement Framework.
Vector schematic illustrating the complete experimental methodology: (1) Data governance audit and patient-level duplicate grouping across three evaluation scenarios ($S_0$: Patient-Disjoint, $S_1$: SSIM 0.80 Cleaned, $S_2$: SSIM 0.75 Grouped); (2) Supervised baseline training of ResNet-50 models across 5 folds per scenario and parameter freezing; (3) Multi-condition spatial intervention pipeline generating six standardized image states ($C_0$: Original Baseline, $C_{1\text{,historical\_dc\_offset}}$: Historical Whole-Tile DC-Offset Control, $C_{1\text{,true\_seam\_w2}}$: Pure 2-Pixel Boundary Seam Control, $C_{1\text{,true\_seam\_w3}}$: 3-Pixel Boundary Seam Control, $C_2$: Seam-Suppressed Rearrangement, $C_3$: Raw Historical Scramble); (4) Out-of-fold inference yielding 55,152 matched forward evaluations; and (5) Paired statistical inference using synchronized cluster bootstrapping ($B=25,000$ resamples) with family-wise Holm-Bonferroni FWER multiplicity control and exact binomial McNemar calculations.

---

### Figure 3: Four-Condition Spatial Intervention Geometry.
Visual panels demonstrating representative experimental conditions on a single representative patient slice:  
**(A) Condition $C_0$ (Baseline):** Original, unmodified slice evaluated through standard preprocessing.  
**(B) Condition $C_{1\text{,historical\_dc\_offset}}$:** Inter-tile DC offsets matching the scrambling intervention are injected across entire $16\times16$ tiles while holding underlying anatomical structures stationary.  
**(C) Condition $C_{1\text{,true\_seam\_w2}}$:** Pure boundary step adjustments restricted strictly to a 1-pixel boundary strip on each side of adjacent tile interfaces ($w=2$), preserving 81.35% of pixels bit-for-bit.  
**(D) Condition $C_2$ (Seam-Suppressed Rearrangement):** Eligible distant-context $16\times16$ tiles are permuted with distance-weighted Gaussian cross-fading, suppressing tile boundary step energy.  
**(E) Condition $C_3$ (Raw Scramble):** Historical tile scramble, in which distant tiles are permuted without boundary smoothing (introducing 1-pixel hard step edges).  
Notice that in all conditions, the central lesion core and 15-pixel peritumoral margin are 100% identical bit-for-bit.

---

### Figure 4: Baseline Model Classification Performance Across Evaluation Scenarios.
Classification metrics of frozen ResNet-50 models under baseline conditions ($C_0$) across the three cross-validation scenarios ($S_0$: Patient-Disjoint, $S_1$: Candidate Duplicate-Cleaned at SSIM 0.80, and $S_2$: Aggressively Grouped at SSIM 0.75). Bars depict out-of-fold Macro-F1 (deep blue), Balanced Accuracy (cyan), and Overall Accuracy (navy blue). Baseline performance remains stable above 0.92 across all leakage-cleaning scenarios.

---

### Figure 5: Multi-Condition Macro-F1 Performance Across Evaluation Scenarios.
Classification performance across experimental conditions in scenarios $S_0, S_1,$ and $S_2$. Condition bars: $C_0$ Original Baseline (blue), $C_{1\text{,true\_seam\_w2}}$ Pure Boundary Seam (green), $C_{1\text{,historical\_dc\_offset}}$ Whole-Tile DC (orange), $C_2$ Seam-Suppressed Rearrangement (purple), and $C_3$ Raw Scramble (magenta). In all scenarios, pure boundary seams alone ($C_{1\text{,true\_seam\_w2}}$) induce a moderate decline ($\Delta = +0.1206$ in $S_0$), whereas rearranging tiles under suppressed seams ($C_2$) results in a severe collapse ($\Delta = +0.4808$), demonstrating that spatial rearrangement independently degrades classification performance by fourfold more than boundary seams alone.

---

### Figure 6: Forest Plot of Paired Statistical Contrasts Across Scenarios.
Paired performance differences ($\Delta = \text{Macro-F1}_A - \text{Macro-F1}_B$) with 95% cluster-bootstrap confidence intervals ($B=25,000$ resamples, seed 42) for primary confirmatory and control contrasts across $S_0$ (blue), $S_1$ (green), and $S_2$ (orange). Contrast labels:  
- **$C_3 \text{ vs } C_0$:** Raw scrambling drop replicating historical benchmarks ($\Delta = +0.4215, p < 10^{-15}$).  
- **$C_{1\text{,hist}} \text{ vs } C_0$:** Historical whole-tile DC-offset perturbation effect ($\Delta = +0.3043, p < 10^{-15}$).  
- **$C_{1\text{,true\_w2}} \text{ vs } C_0$:** Pure 2-pixel boundary seam effect ($\Delta = +0.1206, p < 10^{-15}$).  
- **$C_2 \text{ vs } C_0$:** Seam-suppressed spatial rearrangement effect ($p < 10^{-15}$, substantially exceeding the pre-defined 0.150 threshold indicated by the red dotted line).  
- **$C_3 \text{ vs } C_1$:** Incremental scrambling effect beyond historical DC offsets ($p < 10^{-15}$).  
- **$C_3 \text{ vs } C_2$:** Sensitivity to seam smoothing (negative in $S_0$ indicating $C_2$ was worse than $C_3$; non-significant in $S_1$ and $S_2$).

---

### Figure 7: Confusion Matrices Across Experimental Conditions in Scenario $S_0$.
Out-of-fold confusion matrices for the 3,064 slices of Scenario $S_0$ under baseline and intervention conditions. Heatmap intensity reflects row-normalized recall; overlaid integer values denote raw sample counts. Under baseline conditions ($C_0$), errors are minimal. Under boundary seams ($C_1$), misclassification increases moderately. Under spatial scrambling ($C_2$ and $C_3$), glioma classification collapses, with the majority of true glioma cases misclassified as pituitary tumours.

---

### Figure 8: Edge, Texture, and Spectral Artifact Diagnostics Across Conditions.
Quantitative image diagnostics computed across all 3,064 slices in source $512\times512$ space and model input $224\times224$ space:  
**(Left) Tile Boundary Seam Sobel Energy:** Baseline $C_0$ (31.5) surges to 129.9 under raw scramble $C_3$. Condition $C_1$ reproduces this boundary spike (120.6), while seam suppression $C_2$ mitigates it down to 76.0 (a 54.8% reduction of the excess boundary gradient in source space, and 32.1% in model input space).  
**(Center) Tile Interior Texture Sobel Energy:** Inside the $16\times16$ tiles, $C_3$ scrambled texture is bit-for-bit identical to baseline natural brain tissue (30.89), proving that the gradient spike in tile scrambling is 100% localized to the 1-pixel seam grid.  
**(Right) High-Frequency Fourier Spectral Energy:** Raw scrambling ($C_3$) induces a surge in high-frequency spectral energy. Cross-fading in $C_2$ suppresses 84.9% of this excess Fourier noise at source resolution and 93.8% at model input resolution.

---

### Figure 9: Mechanistic Prior Collapse: Glioma-to-Pituitary Misclassification Rate.
Percentage of true glioma cases ($N=1,426$) misclassified as pituitary tumour across standardized conditions in $S_0$: $C_0$ Baseline (0.14%), $C_{1\text{,true\_seam\_w2}}$ (16.48%), $C_{1\text{,true\_seam\_w3}}$ (23.35%), $C_{1\text{,historical\_dc\_offset}}$ (31.28%), $C_{3\text{,c5lp\_scramble}}$ (56.45%), and $C_{2\text{,seam\_suppressed}}$ (63.53%). This monotonic dose-response confirms that increasing cranial spatial disorientation causes the model to collapse into its default skull-base pituitary prior.

---

### Figure 10: Cross-Validation Fold Stability of Seam-Suppressed Scrambling.
Out-of-fold performance drops ($\Delta \text{Macro-F1}$) for seam-suppressed scrambling ($C_2 \text{ vs } C_0$) broken down by individual cross-validation folds (Fold 1 through Fold 5) across $S_0$ (blue), $S_1$ (green), and $S_2$ (orange). In all 15 evaluated folds, the performance drop reliably exceeds the pre-defined 0.150 threshold (red dotted line), with a remarkably low fold standard deviation ($\text{std} = 0.039$ in $S_0$), demonstrating that spatial context sensitivity is not an artifact of an isolated cross-validation fold.
