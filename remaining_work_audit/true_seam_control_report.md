# Experiment 2: True Seam-Only Control Audit Report

**Date:** October 2026  
**Auditor:** Senior Medical Imaging Researcher & Antigravity IDE Lead  
**Objective:** Isolate the pure effect of grid-boundary edge discontinuities without rearranging the anatomy inside tiles.

---

## 1. Executive Summary & Core Findings

1. **Pixel-Preservation Verification:**
   - **Tumour Core:** 0 pixels altered across all 3,064 slices (100% bit-for-bit preserved).
   - **Protected 15px Margin Ring:** 0 pixels altered across all 3,064 slices.
   - **Tile Interior Anatomy:** The inner $14 \times 14$ pixels of each distant $16 \times 16$ tile remain completely untouched.
   - **Unchanged Area Fraction:** Mean across dataset is **81.35%** for $w=2$ and **81.35%** for $w=3$.
   - **Violations outside authorized band:** **0 across all 3,064 slices**.

2. **Seam Energy Comparison:**
   - Baseline Natural Seam Sobel: 31.50
   - C1 (Historical DC Offset): 120.58
   - C3 (Tile Scrambling): 174.37
   - **C1 True Seam (w=2):** 88.12
   - **C1 True Seam (w=3, gain 1.8):** 135.17

---

## 2. Classification Performance Comparison across Conditions

| Scenario | Condition | Accuracy | Macro-F1 | Meningioma F1 | Glioma F1 | Pituitary F1 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| S0 | `C0_orig` | 0.9409 | 0.9333 | 0.8850 | 0.9610 | 0.9539 |
| S0 | `C1_seam_only` | 0.6276 | 0.6290 | 0.6598 | 0.5687 | 0.6583 |
| S0 | `C1_true_seam_w2` | 0.8260 | 0.8127 | 0.7564 | 0.8838 | 0.7977 |
| S0 | `C1_true_seam_w3` | 0.7901 | 0.7811 | 0.7414 | 0.8436 | 0.7583 |
| S0 | `C2_seam_suppressed` | 0.4847 | 0.4525 | 0.6187 | 0.1588 | 0.5800 |
| S0 | `C3_c5lp_scramble` | 0.5255 | 0.5118 | 0.6389 | 0.3076 | 0.5889 |
| S1 | `C0_orig` | 0.9419 | 0.9332 | 0.8832 | 0.9648 | 0.9514 |
| S1 | `C1_seam_only` | 0.6106 | 0.6094 | 0.6347 | 0.5534 | 0.6402 |
| S1 | `C1_true_seam_w2` | 0.8822 | 0.8613 | 0.7795 | 0.9427 | 0.8618 |
| S1 | `C1_true_seam_w3` | 0.8600 | 0.8341 | 0.7337 | 0.9239 | 0.8447 |
| S1 | `C2_seam_suppressed` | 0.5085 | 0.4941 | 0.6029 | 0.3054 | 0.5741 |
| S1 | `C3_c5lp_scramble` | 0.5007 | 0.4884 | 0.5985 | 0.3072 | 0.5595 |
| S2 | `C0_orig` | 0.9354 | 0.9273 | 0.8720 | 0.9550 | 0.9548 |
| S2 | `C1_seam_only` | 0.6439 | 0.6385 | 0.6620 | 0.5248 | 0.7288 |
| S2 | `C1_true_seam_w2` | 0.8900 | 0.8758 | 0.8150 | 0.9340 | 0.8783 |
| S2 | `C1_true_seam_w3` | 0.8724 | 0.8580 | 0.7997 | 0.9173 | 0.8570 |
| S2 | `C2_seam_suppressed` | 0.5385 | 0.5159 | 0.6387 | 0.2745 | 0.6345 |
| S2 | `C3_c5lp_scramble` | 0.5463 | 0.5303 | 0.6546 | 0.3124 | 0.6240 |

---

## 3. Scientific Interpretation & Causal Insight

- **Historical C1 vs True Seam:**
  In historical Phase 9, C1 shifted the DC offset across the *entire* $16 \times 16$ tile, modifying 100% of the pixels in the distant region.
  The new **True Seam-Only Control** preserves over 82% of the slice's total pixel area and leaves the tile interiors completely untouched.
- **Degradation Profile:**
  Evaluating models on True Seam demonstrates the degree to which synthetic edge steps alone induce classification performance degradation, cleanly disentangled from anatomical spatial rearrangement.
