# Publication Figure Captions

**Manuscript Title:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Study

---

### Figure 1: Representative Brain MRI Slices and Protective Mask Overlays.
Axial T1-weighted contrast-enhanced brain MRI slices from the Cheng et al. Figshare benchmark dataset across the three primary intracranial diagnostic categories: meningioma (Patient ID 108514), glioma (Patient ID 100142), and pituitary tumour (Patient ID 101188).  
**(Top Row) Raw MRI Acquisitions:** Normalized grayscale intensity representations demonstrating baseline tissue morphology and pathology.  
**(Bottom Row) Lesion Masks and Protective Margins:** Exact manual tumour contours (red overlay) delineated by board-certified radiologists, surrounded by an automated 15-pixel dilation margin ring (cyan overlay). In all subsequent spatial intervention experiments, 100% of the pixels within both the tumour core and the peritumoral margin are preserved bit-for-bit, guaranteeing zero direct modification of pathological features.

---

### Figure 2: End-to-End Experimental Methodology and Governance Framework.
Vector schematic illustrating the complete experimental methodology: (1) Data governance audit and patient-level duplicate grouping across three evaluation scenarios ($S_0$: Patient-Disjoint, $S_1$: SSIM 0.80 Cleaned, $S_2$: SSIM 0.75 Grouped); (2) Supervised baseline training of ResNet-50 models across 5 folds per scenario and parameter freezing; (3) Multi-condition spatial intervention pipeline generating six standardized image states ($C_0$: Original Baseline, $C_{1\text{,historical\_dc\_offset}}$: Historical Whole-Tile DC-Offset Control, $C_{1\text{,true\_seam\_w2}}$: Pure 2-Pixel Boundary Seam Control, $C_{1\text{,true\_seam\_w3}}$: Amplified Boundary Seam Control (gain 1.8; legacy identifier w3), $C_2$: Seam-Suppressed Rearrangement, $C_3$: Raw Historical Scramble); (4) Out-of-fold inference yielding 55,152 matched forward evaluations; and (5) Paired statistical inference using synchronized cluster bootstrapping ($B=25,000$ resamples) with family-wise Holm-Bonferroni FWER multiplicity control and exact binomial McNemar calculations.

---

### Figure 3: Spatial Intervention Geometry Across Six Standardized Conditions.
Visual panels demonstrating representative experimental conditions on a single representative patient slice:  
**(A) Condition $C_0$ (Baseline):** Original, unmodified slice evaluated through standard preprocessing.  
**(B) Condition $C_{1\text{,true\_seam\_w2}}$:** Pure boundary step adjustments restricted strictly to a 1-pixel boundary strip on each side of adjacent tile interfaces ($w=2$), preserving 81.35% of pixels bit-for-bit.  
**(C) Condition $C_{1\text{,true\_seam\_w3}}$:** Amplified amplified boundary step adjustments (gain 1.8; legacy identifier w3) along tile interfaces ($w=3$), testing sensitivity to seam-adjustment gain while preserving 81.35% of pixels.  
**(D) Condition $C_{1\text{,historical\_dc\_offset}}$:** Inter-tile DC offsets matching the scrambling intervention injected across entire $16\times16$ tiles while holding underlying anatomical structures stationary.  
**(E) Condition $C_2$ (Seam-Suppressed Rearrangement):** Eligible distant-context $16\times16$ tiles are permuted with distance-weighted Gaussian cross-fading, suppressing tile boundary step energy.  
**(F) Condition $C_3$ (Raw Scramble):** Historical tile scramble, in which distant tiles are permuted without boundary smoothing (introducing 1-pixel hard step edges).  
Notice that in all conditions, the central lesion core and 15-pixel peritumoral margin are 100% identical bit-for-bit.

---

### Figure 4: Baseline Model Classification Performance Across Evaluation Scenarios.
Classification metrics of frozen ResNet-50 models under baseline conditions ($C_0$) across the three cross-validation scenarios ($S_0$: Patient-Disjoint, $S_1$: Candidate Duplicate-Cleaned at SSIM 0.80, and $S_2$: Aggressively Grouped at SSIM 0.75). Bars depict out-of-fold Macro-F1 (deep blue), Balanced Accuracy (cyan), and Overall Accuracy (navy blue). Baseline performance remains stable above 0.92 across all leakage-cleaning scenarios.

---

### Figure 5: Multi-Condition Macro-F1 Performance Across Six Standardized Conditions.
Classification performance across experimental conditions in scenarios $S_0, S_1,$ and $S_2$. Condition bars: $C_0$ Original Baseline (blue), $C_{1\text{,true\_seam\_w2}}$ Pure Boundary Seam w=2 (teal), $C_{1\text{,true\_seam\_w3}}$ Amplified Boundary Seam (gain 1.8; legacy identifier w3) (gold), $C_{1\text{,historical\_dc\_offset}}$ Whole-Tile DC (orange), $C_2$ Seam-Suppressed Rearrangement (purple), and $C_3$ Raw Scramble (pink). In all scenarios, pure boundary seams alone ($C_{1\text{,true\_seam\_w2}}$) induce a moderate decline ($\Delta = +0.1206$ in $S_0$), whereas rearranging tiles under suppressed seams ($C_2$) results in a severe collapse ($\Delta = +0.4808$), demonstrating that spatial rearrangement independently degrades classification performance by fourfold more than boundary seams alone.

---

### Figure 6: Forest Plot of Paired Statistical Contrasts Across Scenarios.
Paired performance differences ($\Delta = \text{Macro-F1}_A - \text{Macro-F1}_B$) with 95% cluster-bootstrap confidence intervals ($B=25,000$ resamples, seed 42) for primary confirmatory and control contrasts across $S_0$ (blue), $S_1$ (green), and $S_2$ (orange). Contrast labels:  
- **$C_3 \text{ vs } C_0$:** Raw scrambling drop replicating historical benchmarks ($\Delta = +0.4215, p < 10^{-15}$).  
- **$C_{1\text{,hist}} \text{ vs } C_0$:** Historical whole-tile DC-offset perturbation effect ($\Delta = +0.3043, p < 10^{-15}$).  
- **$C_{1\text{,true\_w2}} \text{ vs } C_0$:** Pure 2-pixel boundary seam effect ($\Delta = +0.1206, p < 10^{-15}$).  
- **$C_{1\text{,true\_w3}} \text{ vs } C_0$:** Amplified amplified boundary seam (gain 1.8; legacy identifier w3) effect ($\Delta = +0.1522, p < 10^{-15}$).  
- **$C_2 \text{ vs } C_0$:** Seam-suppressed spatial rearrangement effect ($p < 10^{-15}$, substantially exceeding the pre-defined 0.150 threshold indicated by the red dotted line).  
- **$C_3 \text{ vs } C_2$:** Sensitivity to seam smoothing (negative in $S_0$ indicating $C_2$ was worse than $C_3$; non-significant in $S_1$ and $S_2$).  
- **$C_3 \text{ vs } C_{1\text{,true\_w2}}$:** Incremental scrambling effect beyond pure boundary seams alone ($\Delta = +0.3009, p < 10^{-15}$).

---

### Figure 7: Confusion Matrices Across Six Standardized Conditions in Scenario $S_0$.
Out-of-fold confusion matrices for the 3,064 slices of Scenario $S_0$ under baseline and all five intervention conditions ($2\times3$ grid). Heatmap intensity reflects row-normalized recall; overlaid integer values denote raw sample counts. Under baseline conditions ($C_0$), errors are minimal (95.0% glioma recall). Under pure boundary seams ($C_1$), misclassification increases moderately. Under spatial scrambling ($C_2$ and $C_3$), glioma classification collapses catastrophically (8.6% recall in $C_2$), with the majority of true glioma cases misclassified as pituitary tumours.

---

### Figure 8: Edge, Spectral, and Area Preservation Diagnostics Across Conditions.
Quantitative image diagnostics computed across all 3,064 slices in source $512\times512$ space and model input $224\times224$ space from canonical Table 7:  
**C2 diagnostic status:** The previous Figure 8 diagnostics used a C2 generation operator that did not match the evaluated predictions. Figure 8 is withheld until the corrected `scripts/run_dual_resolution_diagnostics.py` has been run on all 3,064 slices and the regenerated table has been reconciled. Do not use or quote previous C2 seam/Spectral-energy values.  
**(Right) Pixel Preservation Area Fraction:** True-seam controls ($w=2, w=3$) bit-for-bit preserve 81.35% of all image pixels (and 64.12% in $224\times224$ space) alongside 100% of tumour core and margin pixels, whereas tile permutation conditions ($C_2, C_3$) alter approximately 89% of image area.

---

### Figure 9: Mechanistic Prior Collapse: Glioma-to-Pituitary Misclassification Rate.
Percentage of true glioma cases ($N=1,426$) misclassified as pituitary tumour across standardized conditions in $S_0$: $C_0$ Baseline (0.14%), $C_{1\text{,true\_seam\_w2}}$ (16.48%), $C_{1\text{,true\_seam\_w3}}$ (23.35%), $C_{1\text{,historical\_dc\_offset}}$ (31.28%), $C_{3\text{,c5lp\_scramble}}$ (56.45%), and $C_{2\text{,seam\_suppressed}}$ (63.53%). This monotonic dose-response confirms that increasing cranial spatial disorientation causes the model to collapse into its default skull-base pituitary prior.

---

### Figure 10: Cross-Validation Fold Stability of Seam-Suppressed Scrambling.
Out-of-fold performance drops ($\Delta \text{Macro-F1}$) for seam-suppressed scrambling ($C_2 \text{ vs } C_0$) broken down by individual cross-validation folds (Fold 1 through Fold 5) across $S_0$ (blue), $S_1$ (green), and $S_2$ (orange). In all 15 evaluated folds, the performance drop reliably exceeds the pre-defined 0.150 threshold (red dotted line), with a remarkably low fold standard deviation ($\text{std} = 0.039$ in $S_0$), demonstrating that spatial context sensitivity is not an artifact of an isolated cross-validation fold.
