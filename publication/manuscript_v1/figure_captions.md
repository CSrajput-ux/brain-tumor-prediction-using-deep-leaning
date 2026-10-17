# Figure Captions

### Figure 1: Representative Brain MRI Slices and Tumour Mask Overlays Across Diagnostic Classes.
**(Top Row)** Genuine contrast-enhanced T1-weighted 2D axial MRI slices from the Cheng Figshare cohort (3,064 total slices across 233 patient clusters) representing the three target tumour pathologies: Meningioma (left), Glioma (center), and Pituitary Tumour (right).  
**(Bottom Row)** Corresponding anatomical overlays illustrating the established experimental protection geometry: the primary tumour core segmentation mask provided by the dataset annotators (red overlay) and the 15-pixel dilation margin ring (cyan overlay). Across all intervention conditions ($C_1, C_2, C_3$), exactly zero pixels were modified within the tumour core or dilation margin, ensuring that any observed classification degradation arises strictly from modifications to distant anatomical context.

---

### Figure 2: End-to-End Experimental Workflow and Disentanglement Framework.
Vector schematic illustrating the complete experimental methodology: (1) Data governance audit and patient-level duplicate grouping across three evaluation scenarios ($S_0$: Patient-Disjoint, $S_1$: SSIM 0.80 Cleaned, $S_2$: SSIM 0.75 Grouped); (2) Supervised baseline training of ResNet-50 models across 5 folds per scenario and parameter freezing; (3) Multi-condition spatial intervention pipeline generating four matched image states ($C_0$: Original Baseline, $C_1$: Seam-Only Control, $C_2$: Seam-Suppressed Rearrangement, $C_3$: Raw Historical Scramble); (4) Out-of-fold inference yielding 36,768 matched forward evaluations; and (5) Paired statistical inference using synchronized cluster bootstrapping ($B=2,000$ resamples) and Holm-Bonferroni FWER multiplicity control.

---

### Figure 3: Four-Condition Spatial Intervention Geometry.
Visual panels demonstrating the four experimental conditions on a single representative patient slice:  
**(A) Condition $C_0$ (Baseline):** Original, unmodified slice evaluated through standard preprocessing.  
**(B) Condition $C_1$ (Seam-Only Control):** Local inter-tile DC offsets matching the scrambling intervention are injected along the $16\times16$ grid boundaries while holding the underlying anatomical tissue completely stationary.  
**(C) Condition $C_2$ (Seam-Suppressed Rearrangement):** Eligible distant-context $16\times16$ tiles are permuted with distance-weighted 4-pixel Gaussian cross-fading, suppressing tile boundary step energy.  
**(D) Condition $C_3$ (Raw Scramble):** Historical $C_{5\text{LP}}$ scramble, in which distant tiles are permuted without boundary smoothing (introducing 1-pixel hard step edges).  
Notice that in all four conditions, the central lesion and peritumoral margin are identical bit-for-bit.

---

### Figure 4: Baseline Model Classification Performance Across Evaluation Scenarios.
Classification metrics of frozen ResNet-50 models under baseline conditions ($C_0$) across the three cross-validation scenarios ($S_0$: Patient-Disjoint, $S_1$: Candidate Duplicate-Cleaned at SSIM 0.80, and $S_2$: Aggressively Grouped at SSIM 0.75). Bars depict out-of-fold Macro-F1 (deep blue), Balanced Accuracy (cyan), and Overall Accuracy (navy blue). Baseline performance remains stable above 0.92 across all leakage-cleaning scenarios.

---

### Figure 5: Multi-Condition Macro-F1 Performance Across Evaluation Scenarios.
Classification performance under all four experimental conditions across scenarios $S_0, S_1,$ and $S_2$. Condition bars: $C_0$ Original Baseline (blue), $C_1$ Seam-Only Control (orange), $C_2$ Seam-Suppressed Rearrangement (purple), and $C_3$ Raw Scramble (magenta). In all scenarios, injecting artificial seams alone ($C_1$) reduces Macro-F1 from ~0.93 to ~0.61–0.63. Rearranging tiles under suppressed seams ($C_2$) results in a catastrophic collapse to ~0.45–0.51, demonstrating that spatial rearrangement independently degrades classification performance even when boundary seams are eliminated.

---

### Figure 6: Forest Plot of Paired Statistical Contrasts Across Scenarios.
Paired performance differences ($\Delta = \text{Macro-F1}_A - \text{Macro-F1}_B$) with 95% cluster-bootstrap confidence intervals ($B=2,000$ resamples, seed 42) for five confirmatory contrasts across $S_0$ (blue), $S_1$ (green), and $S_2$ (orange). Contrast labels:  
- **$C_3 \text{ vs } C_0$:** Raw scrambling drop replicating historical Phase 6 findings.  
- **$C_1 \text{ vs } C_0$:** Seam-only perturbation effect ($p < 10^{-15}$).  
- **$C_2 \text{ vs } C_0$:** Seam-suppressed spatial rearrangement effect ($p < 10^{-15}$, substantially exceeding the preregistered 0.150 threshold indicated by the red dotted line).  
- **$C_3 \text{ vs } C_1$:** Incremental scrambling effect beyond artificial seams ($p < 10^{-15}$).  
- **$C_3 \text{ vs } C_2$:** Sensitivity to seam smoothing (negative in $S_0$ indicating $C_2$ was worse than $C_3$; non-significant in $S_1$ and $S_2$).

---

### Figure 7: Confusion Matrices Across Experimental Conditions in Scenario $S_0$.
Out-of-fold confusion matrices for the 3,064 slices of Scenario $S_0$ under $C_0$ Baseline, $C_1$ Seam-Only, $C_2$ Seam-Suppressed Rearrangement, and $C_3$ Raw Scramble. Heatmap intensity reflects row-normalized recall; overlaid integer values denote raw sample counts. Under baseline conditions ($C_0$), errors are minimal. Under $C_1$ (seams alone), misclassification increases across all classes. Under spatial scrambling ($C_2$ and $C_3$), glioma classification collapses, with the majority of true glioma cases misclassified as pituitary tumours.

---

### Figure 8: Edge, Texture, and Spectral Artifact Diagnostics Across Conditions.
Quantitative image diagnostics computed across all 3,064 slices:  
**(Left) Tile Boundary Seam Sobel Energy:** Baseline $C_0$ (31.5) surges to 129.9 under raw scramble $C_3$. Condition $C_1$ successfully reproduces this boundary spike (120.6), while seam suppression $C_2$ mitigates it down to 76.0 (a 54.8% reduction of the excess boundary gradient).  
**(Center) Tile Interior Texture Sobel Energy:** Inside the $16\times16$ tiles, $C_3$ scrambled texture is bit-for-bit identical to baseline natural brain tissue (30.89), proving that the gradient spike in tile scrambling is 100% localized to the 1-pixel seam grid.  
**(Right) High-Frequency Fourier Spectral Energy:** Raw scrambling ($C_3$) induces a 6.8-fold surge in high-frequency spectral energy. Cross-fading in $C_2$ suppresses 84.9% of this excess Fourier noise.

---

### Figure 9: Mechanistic Prior Collapse: Glioma-to-Pituitary Misclassification Rate.
Percentage of true glioma cases ($N=1,426$) misclassified as pituitary tumour across conditions $C_0, C_1, C_2,$ and $C_3$ in scenarios $S_0, S_1,$ and $S_2$. Under baseline conditions ($C_0$), glioma-to-pituitary confusion is virtually non-existent (<0.35%). Under seam-only perturbation ($C_1$), the rate rises to ~31–40%. Under spatial context scrambling ($C_2$ and $C_3$), the rate surges to **55%–64%**, demonstrating that spatial disorientation collapses the network into its skull-base pituitary prior.

---

### Figure 10: Cross-Validation Fold Stability of Seam-Suppressed Scrambling.
Out-of-fold performance drops ($\Delta \text{Macro-F1}$) for seam-suppressed scrambling ($C_2 \text{ vs } C_0$) broken down by individual cross-validation folds (Fold 1 through Fold 5) across $S_0$ (blue), $S_1$ (green), and $S_2$ (orange). In all 15 evaluated folds, the performance drop reliably exceeds the 0.150 preregistered threshold (red dotted line), with a remarkably low fold standard deviation ($\text{std} = 0.039$ in $S_0$), demonstrating that spatial context sensitivity is not an artifact of an isolated cross-validation fold.
