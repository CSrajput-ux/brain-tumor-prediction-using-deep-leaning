# Phase 9: Statistical Validity Report & Hypothesis Evaluation

**Project:** Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers: A Multi-Control Spatial Intervention Study  
**Phase:** Phase 9 (Controlled Validation Experiment)  
**Date:** 2026-10-17  
**Execution Environment:** CUDA (RTX 4050), PyTorch 2.15, 15 Frozen Checkpoints ($S_0, S_1, S_2 \times 5$ folds)  

---

## 1. Executive Summary

Phase 9 executed a controlled, four-condition disentanglement experiment to resolve whether the severe classifier degradation observed under distant-context patch scrambling ($C_{5\text{LP}}$, Phase 6) was driven by **high-frequency artificial tile seams** ($H_1$), **disruption of macroscopic cranial spatial layout** ($H_2$), or a **mixed mechanism** ($H_3$).

Across all three evaluation scenarios ($S_0$ Patient-Disjoint, $S_1$ Leakage-Cleaned SSIM 0.80, and $S_2$ Aggressive Grouping SSIM 0.75) and 36,768 matched forward passes:

1. **Synthetic Tile Seams Alone Cause Severe Degradation ($H_1$ Supported):**
   - Injecting tile boundary step discontinuities without permuting underlying anatomy ($C_1$) causes a statistically significant collapse of $\Delta \text{Macro-F1} = +0.3043$ in $S_0$ (95% CI: $[0.2586, 0.3535]$, McNemar $\chi^2 = 824.1, p < 10^{-15}$).
   - Boundary step artifacts alone explain approximately 72% of the raw scrambling drop.

2. **Spatial Layout Disruption Independently Degrades Performance ($H_2$ Supported):**
   - Rearranging distant-context tiles with seam cross-fading suppression ($C_2$) results in $\Delta \text{Macro-F1} = +0.4808$ in $S_0$ (95% CI: $[0.4350, 0.5283]$, McNemar $\chi^2 = 1273.9, p < 10^{-15}$).
   - This effect substantially exceeds the preregistered threshold for practical significance ($\Delta \ge 0.150$).

3. **Decisive Empirical Support for Mixed Mechanism ($H_3$ Confirmed):**
   - Scrambling is significantly and reliably more destructive than seams alone: $C_3 \text{ vs } C_1$ shows $\Delta = +0.1172$ ($S_0$, 95% CI: $[0.0819, 0.1542]$, $p < 10^{-15}$).
   - Concurrently, seam suppression alone ($C_2$) does not rescue the network from spatial scrambling collapse ($\Delta = +0.4808$).
   - The null hypothesis $H_0$ (that spatial rearrangement has no independent effect once seams are controlled) is decisively refuted.

---

## 2. Experimental Conditions & Invariants

| Condition Code | Condition Name | Description | Tumour Core Pixels Altered | Margin (15px) Pixels Altered | Mean Seam Sobel Energy |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **$C_0$** | Original Baseline | Unmodified test slice | 0 | 0 | 27.12 |
| **$C_1$** | Seam-Only Control | Boundary step discontinuity injected onto unpermuted tiles | 0 | 0 | 179.84 |
| **$C_2$** | Seam-Suppressed Scramble | Permuted $16\times16$ tiles with distance-weighted cross-fading | 0 | 0 | 72.18 |
| **$C_3$** | Historical $C_{5\text{LP}}$ | Unmodified distant-context tile scrambling | 0 | 0 | 185.70 |

### Invariant Verification
- **Protected Core & Margin:** In all 3,064 slices across all conditions, exactly **0 pixels** were altered inside the tumour core and inside the 15-pixel dilation margin ring.
- **Luminance & Variance Matching:** Global mean intensity and global standard deviation between $C_0$ and $C_3$ matched with difference $< 10^{-5}$ across all slices.

---

## 3. Primary Metrics Across Conditions

Performance is evaluated using Macro-F1, Balanced Accuracy, Overall Accuracy, and per-class metrics across all 15 frozen checkpoints:

### Scenario $S_0$ (Patient-Disjoint 5-Fold CV)
| Condition | Macro-F1 | Balanced Acc | Overall Acc | F1 Meningioma | F1 Glioma | F1 Pituitary |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| $C_0$ (Baseline) | **0.9333** | 0.9362 | 0.9409 | 0.8850 | 0.9610 | 0.9539 |
| $C_1$ (Seam-Only) | **0.6290** | 0.6817 | 0.6276 | 0.6598 | 0.5687 | 0.6583 |
| $C_2$ (Seam-Suppressed) | **0.4525** | 0.5783 | 0.4847 | 0.6187 | 0.1588 | 0.5800 |
| $C_3$ (C5LP Scramble) | **0.5118** | 0.6082 | 0.5255 | 0.6389 | 0.3076 | 0.5889 |

### Scenario $S_1$ (Duplicate-Cleaned SSIM 0.80)
| Condition | Macro-F1 | Balanced Acc | Overall Acc | F1 Meningioma | F1 Glioma | F1 Pituitary |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| $C_0$ (Baseline) | **0.9332** | 0.9336 | 0.9419 | 0.8832 | 0.9648 | 0.9514 |
| $C_1$ (Seam-Only) | **0.6094** | 0.6633 | 0.6106 | 0.6347 | 0.5534 | 0.6402 |
| $C_2$ (Seam-Suppressed) | **0.4941** | 0.5855 | 0.5085 | 0.6029 | 0.3054 | 0.5741 |
| $C_3$ (C5LP Scramble) | **0.4884** | 0.5732 | 0.5007 | 0.5985 | 0.3072 | 0.5595 |

### Scenario $S_2$ (Aggressive Grouping SSIM 0.75)
| Condition | Macro-F1 | Balanced Acc | Overall Acc | F1 Meningioma | F1 Glioma | F1 Pituitary |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| $C_0$ (Baseline) | **0.9273** | 0.9230 | 0.9354 | 0.8720 | 0.9550 | 0.9548 |
| $C_1$ (Seam-Only) | **0.6385** | 0.7135 | 0.6439 | 0.6620 | 0.5248 | 0.7288 |
| $C_2$ (Seam-Suppressed) | **0.5159** | 0.6255 | 0.5385 | 0.6387 | 0.2745 | 0.6345 |
| $C_3$ (C5LP Scramble) | **0.5303** | 0.6281 | 0.5463 | 0.6546 | 0.3124 | 0.6240 |

---

## 4. Preregistered Paired Contrasts & Bootstrap Analysis

Bootstrapping was conducted using $B=2,000$ patient/combined-group cluster resamplings (seed 42).

$$\Delta_{\text{contrast}} = \text{Macro-F1}_A - \text{Macro-F1}_B$$

| Scenario | Contrast ID | Contrast Comparison | Point Estimate $\Delta$ | 95% Cl Lower | 95% Cl Upper | McNemar $\chi^2$ | $p$-value |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | **C3 vs C0** | Scrambling Reproduction | **+0.4215** | +0.3735 | +0.4716 | 1145.1 | $< 10^{-15}$ |
| **$S_0$** | **C1 vs C0** | Seam-Only Effect | **+0.3043** | +0.2586 | +0.3535 | 824.1 | $< 10^{-15}$ |
| **$S_0$** | **C2 vs C0** | Seam-Suppressed Effect | **+0.4808** | +0.4350 | +0.5283 | 1273.9 | $< 10^{-15}$ |
| **$S_0$** | **C3 vs C1** | Scramble vs Seam Difference | **+0.1172** | +0.0819 | +0.1542 | 170.5 | $< 10^{-15}$ |
| **$S_0$** | **C3 vs C2** | Sensitivity to Seam Smoothing | **-0.0593** | -0.0815 | -0.0365 | 52.8 | $3.6 \times 10^{-13}$ |
| **$S_1$** | **C3 vs C0** | Scrambling Reproduction | **+0.4447** | +0.3968 | +0.4957 | 1262.2 | $< 10^{-15}$ |
| **$S_1$** | **C1 vs C0** | Seam-Only Effect | **+0.3237** | +0.2757 | +0.3740 | 920.5 | $< 10^{-15}$ |
| **$S_1$** | **C2 vs C0** | Seam-Suppressed Effect | **+0.4390** | +0.3928 | +0.4889 | 1233.1 | $< 10^{-15}$ |
| **$S_1$** | **C3 vs C1** | Scramble vs Seam Difference | **+0.1210** | +0.0977 | +0.1454 | 250.3 | $< 10^{-15}$ |
| **$S_1$** | **C3 vs C2** | Sensitivity to Seam Smoothing | **+0.0057** | -0.0095 | +0.0219 | 2.38 | $0.123$ (n.s.) |
| **$S_2$** | **C3 vs C0** | Scrambling Reproduction | **+0.3969** | +0.3425 | +0.4548 | 1068.1 | $< 10^{-15}$ |
| **$S_2$** | **C1 vs C0** | Seam-Only Effect | **+0.2887** | +0.2289 | +0.3522 | 744.3 | $< 10^{-15}$ |
| **$S_2$** | **C2 vs C0** | Seam-Suppressed Effect | **+0.4114** | +0.3576 | +0.4682 | 1080.7 | $< 10^{-15}$ |
| **$S_2$** | **C3 vs C1** | Scramble vs Seam Difference | **+0.1082** | +0.0844 | +0.1338 | 196.0 | $< 10^{-15}$ |
| **$S_2$** | **C3 vs C2** | Sensitivity to Seam Smoothing | **-0.0144** | -0.0339 | +0.0034 | 2.20 | $0.138$ (n.s.) |

---

## 5. Class Transitions & Prediction Flips

Inspection of confusion matrices and per-class recall uncovers the mechanical driver of the collapse:

| Scenario | Condition | Glioma Total | Glioma $\to$ Pituitary Flips | Transition Rate | Glioma $\to$ Meningioma Flips | Transition Rate |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | $C_0$ (Baseline) | 1,426 | 2 | 0.14% | 69 | 4.84% |
| **$S_0$** | $C_1$ (Seam-Only) | 1,426 | 446 | 31.28% | 374 | 26.23% |
| **$S_0$** | $C_2$ (Seam-Suppressed) | 1,426 | 906 | 63.53% | 397 | 27.84% |
| **$S_0$** | $C_3$ (C5LP Scramble) | 1,426 | 805 | 56.45% | 360 | 25.25% |

### Key Mechanistic Insight
- Under baseline conditions ($C_0$), the network rarely confuses glioma for pituitary tumour ($< 0.35\%$).
- Introducing high-frequency seam noise ($C_1$) disrupts confident feature extraction, causing a 31.3% flip to pituitary and 26.2% flip to meningioma.
- Scrambling spatial coordinates ($C_2$ and $C_3$), regardless of seam suppression, produces a catastrophic collapse in glioma recall ($95.0\% \to 8.6\%$ in $S_0$ $C_2$, $18.0\%$ in $S_1$ $C_2$), with **over 55% to 63% of all glioma cases misclassified as pituitary tumour**.
- Because pituitary tumours in the Cheng dataset are anatomically localized to the sella turcica at the skull base, disrupting the cranial layout prevents the model from verifying that the tumour is located in supratentorial brain parenchyma, collapsing the classifier into its prior.

---

## 6. Preregistered Decision Rule Evaluation

Referring to the preregistered decision criteria in `preregistration_verification.md`:

1. **Threshold Check:** Is $\Delta_{\text{C2 vs C0}} \ge 0.150$?
   - Observed $\Delta = +0.4808$ ($S_0$), $+0.4390$ ($S_1$), $+0.4114$ ($S_2$).
   - Lower bound of 95% CI is $+0.3576 \gg 0.150$.
   - **Result:** Threshold met with overwhelming statistical significance.

2. **Seam Effect Check:** Is $\Delta_{\text{C1 vs C0}} > 0$?
   - Observed $\Delta = +0.3043$ ($S_0$), $+0.3237$ ($S_1$), $+0.2887$ ($S_2$).
   - Lower bound of 95% CI is $+0.2289 \gg 0$.
   - **Result:** Significant seam artifact effect confirmed.

3. **Incremental Scrambling Effect Check:** Is $\Delta_{\text{C3 vs C1}} > 0$?
   - Observed $\Delta = +0.1172$ ($S_0$), $+0.1210$ ($S_1$), $+0.1082$ ($S_2$).
   - Lower bound of 95% CI is $+0.0819 \gg 0$.
   - **Result:** Permuting tiles degrades performance significantly beyond seam artifacts.

**Outcome Classification: Outcome A & Outcome E (Mixed Mechanism / Dual-Factor Degradation).**  
Both high-frequency artificial edges and macroscopic spatial arrangement disruption contribute significantly to performance collapse. The hypothesis that tile scrambling was merely an edge artifact is decisively disproven.
