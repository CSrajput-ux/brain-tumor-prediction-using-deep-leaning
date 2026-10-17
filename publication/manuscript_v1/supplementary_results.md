# Supplementary Results

**Manuscript Title:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Study  
**Publication Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17  

---

## 1. Per-Fold Performance Breakdown Across Checkpoints

To evaluate whether the observed sensitivity to spatial rearrangement is uniform or driven by specific cross-validation splits, out-of-fold performance was evaluated separately across all 15 checkpoints ($S_0, S_1, S_2 \times 5$ folds).

### Table S1: Checkpoint-Level Macro-F1 Performance by Fold and Condition

| Scenario | Fold ID | Held-Out Slices | $C_0$ Baseline | $C_1$ Seam-Only | $C_2$ Seam-Suppressed | $C_3$ Raw Scramble | Seam Drop ($C_1 \text{ vs } C_0$) | Seam-Suppressed Drop ($C_2 \text{ vs } C_0$) | Raw Scramble Drop ($C_3 \text{ vs } C_0$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | Fold 1 | 618 | 0.9452 | 0.5709 | 0.4661 | 0.4912 | +0.3743 | +0.4791 | +0.4540 |
| **$S_0$** | Fold 2 | 616 | 0.9168 | 0.6632 | 0.5007 | 0.6303 | +0.2536 | +0.4161 | +0.2865 |
| **$S_0$** | Fold 3 | 612 | 0.9416 | 0.5845 | 0.4285 | 0.4422 | +0.3571 | +0.5131 | +0.4994 |
| **$S_0$** | Fold 4 | 610 | 0.9328 | 0.7558 | 0.4254 | 0.5637 | +0.1770 | +0.5074 | +0.3691 |
| **$S_0$** | Fold 5 | 608 | 0.9304 | 0.5481 | 0.4660 | 0.4240 | +0.3823 | +0.4644 | +0.5064 |
| **$S_1$** | Fold 1 | 618 | 0.9238 | 0.6208 | 0.4930 | 0.5402 | +0.3030 | +0.4308 | +0.3836 |
| **$S_1$** | Fold 2 | 616 | 0.9442 | 0.5197 | 0.4685 | 0.4619 | +0.4245 | +0.4757 | +0.4823 |
| **$S_1$** | Fold 3 | 612 | 0.9261 | 0.7220 | 0.5195 | 0.5045 | +0.2041 | +0.4066 | +0.4216 |
| **$S_1$** | Fold 4 | 610 | 0.9575 | 0.4128 | 0.4446 | 0.3592 | +0.5447 | +0.5129 | +0.5983 |
| **$S_1$** | Fold 5 | 608 | 0.9142 | 0.7488 | 0.5608 | 0.5435 | +0.1654 | +0.3534 | +0.3707 |
| **$S_2$** | Fold 1 | 618 | 0.9515 | 0.5266 | 0.5001 | 0.4867 | +0.4249 | +0.4514 | +0.4648 |
| **$S_2$** | Fold 2 | 616 | 0.9521 | 0.5988 | 0.4638 | 0.5500 | +0.3533 | +0.4883 | +0.4021 |
| **$S_2$** | Fold 3 | 612 | 0.9025 | 0.6263 | 0.5347 | 0.5503 | +0.2762 | +0.3678 | +0.3522 |
| **$S_2$** | Fold 4 | 610 | 0.9221 | 0.7459 | 0.4735 | 0.4907 | +0.1762 | +0.4486 | +0.4314 |
| **$S_2$** | Fold 5 | 608 | 0.9085 | 0.6830 | 0.5921 | 0.5679 | +0.2255 | +0.3164 | +0.3406 |

### Observations:
1. In all 15 evaluated checkpoints, seam-suppressed scrambling ($C_2$) produced a substantial performance decline exceeding $+0.316$ Macro-F1 (far above the preregistered practical threshold of $0.150$).
2. The standard deviation across folds for $C_2 \text{ vs } C_0$ is low: $0.039$ in $S_0$, $0.062$ in $S_1$, and $0.070$ in $S_2$.
3. This confirms that sensitivity to spatial arrangement is a robust property of the learned representations across training folds, not an artifact of an isolated cross-validation fold.

---

## 2. Complete Confusion Matrix Transition Dynamics

### Table S2: Complete Raw Confusion Matrix Cell Counts Across Conditions

| Scenario | Condition | True Meningioma $\to$ Pred [Men, Gli, Pit] | True Glioma $\to$ Pred [Men, Gli, Pit] | True Pituitary $\to$ Pred [Men, Gli, Pit] |
| :---: | :--- | :---: | :---: | :---: |
| **$S_0$** | $C_0$ Baseline | [639, 26, 43] | [69, 1355, 2] | [28, 13, 889] |
| **$S_0$** | $C_1$ Seam-Only | [605, 28, 75] | [374, 606, 446] | [147, 71, 712] |
| **$S_0$** | $C_2$ Seam-Suppressed | [546, 0, 162] | [397, 123, 906] | [114, 0, 816] |
| **$S_0$** | $C_3$ Raw Scramble | [567, 2, 139] | [360, 261, 805] | [140, 8, 782] |
| **$S_1$** | $C_0$ Baseline | [624, 37, 47] | [50, 1371, 5] | [31, 8, 891] |
| **$S_1$** | $C_1$ Seam-Only | [542, 3, 163] | [311, 547, 568] | [147, 1, 782] |
| **$S_1$** | $C_2$ Seam-Suppressed | [526, 0, 182] | [356, 257, 813] | [155, 0, 775] |
| **$S_1$** | $C_3$ Raw Scramble | [495, 0, 213] | [302, 259, 865] | [149, 1, 780] |
| **$S_2$** | $C_0$ Baseline | [630, 40, 38] | [74, 1348, 4] | [33, 9, 888] |
| **$S_2$** | $C_1$ Seam-Only | [620, 2, 86] | [460, 508, 458] | [85, 0, 845] |
| **$S_2$** | $C_2$ Seam-Suppressed | [555, 1, 152] | [413, 227, 786] | [62, 0, 868] |
| **$S_2$** | $C_3$ Raw Scramble | [543, 0, 165] | [345, 264, 817] | [63, 0, 867] |

### Key Clinical & Representational Insights:
1. **Glioma Specificity Collapse:** Under baseline conditions, only 2 out of 1,426 gliomas in $S_0$ were misclassified as pituitary tumour (0.14%). Under seam-suppressed scrambling ($C_2$), 906 out of 1,426 gliomas were misclassified as pituitary tumour (63.53%).
2. **Selective Asymmetry:** Pituitary tumours were almost never misclassified as glioma under scrambling (0 in $C_2$ across $S_0, S_1, S_2$). The confusion is highly directional: supratentorial gliomas collapse into the skull-base pituitary prior, but skull-base pituitary tumours do not flip to glioma.
3. This asymmetry provides compelling mechanistic evidence that the model relies on intact supratentorial brain parenchyma as a necessary condition to predict glioma. When the cranial context is permuted, the network fails to verify intra-axial parenchymal localization and defaults to the skull-base lesion class.
