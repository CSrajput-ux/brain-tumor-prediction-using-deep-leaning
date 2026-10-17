# Intervention Quality Audit: Phase 6 Spatial Controls

**Document ID:** `PHASE_6_INTERVENTION_QUALITY_AUDIT`  
**Phase:** 6 — Targeted Spatial Control Validation  
**Authoritative Standard:** Pixel-level Geometry, Radiometry, and Boundary Invariant Verification  
**Date:** 2026-10-17  

---

## 1. Executive Summary

This quality audit inspects the mathematical implementation and empirical pixel distributions of all 14 experimental conditions across all 3,064 MRI slices in Phase 6.

### Primary Audit Verdict: `PASS`
- **Tumour Core Invariant:** 100% bit-preservation of the segmented tumor core in all distant-context ($C_5, C_{5\text{LP}}$) and margin interventions ($C_3, C_4, C_{3\text{NS}}$). Zero bleeding into the tumor interior.
- **Protected Zone Invariant:** In $C_{5\text{LP}}$, all pixels in the 15-pixel dilated tumor zone ($M_{\text{dil15}}$) are 100% bit-identical to the original image ($I_{\text{orig}}$).
- **Global Radiometric Invariant:** In $C_{5\text{LP}}$, mean slice intensity ($39.79$) and standard deviation ($40.93$) are strictly bit-preserved to 0.000000 difference relative to $I_{\text{orig}}$.
- **Boundary Smoothing Invariant:** In $C_{3\text{NS}}$ (Navier-Stokes PDE inpainting), the unnatural step-edge gradient is reduced by **83.6%** ($236.66 \to 38.87$), fully eliminating the artificial high-frequency boundary artifact present in zero-filled margin ablation.

---

## 2. Invariant Verification by Condition

| Condition Code | Condition Name | Total Altered Px (Mean) | Tumour Core Overlap | Protected Zone Overlap | Mean Intensity | Intensity Std | Boundary Step Gradient | Verification Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C0** | `I_orig` | 0.0 | N/A | N/A | 39.79 | 40.93 | 0.00 | **PASS** (Bit-identical) |
| **C1** | `I_tumor_removed` | 4,421.7 | 100.0% | N/A | 38.42 | 40.64 | 219.51 | **PASS** (Exact ablation) |
| **C2** | `I_placebo_focal` | 4,410.0 | 0.0% | N/A | 38.64 | 40.91 | 221.04 | **PASS** (0 tumor overlap) |
| **C5** | `I_distant_perturbed` | 213,320.6 | 0.0% | 0.0% | 20.91 (-47.5%) | 22.84 (-44.2%) | 0.00 | **PASS** (Exact 50% scaling) |
| **C5LP** | `I_distant_luminance_preserved` | 231,861.4 | 0.0% | 0.0% | 39.79 (0.00%) | 40.93 (0.00%) | 0.00 | **PASS** (100% luminance invariant) |
| **C3_r15** | `I_margin_r15_removed` | 4,337.9 | 0.0% | N/A | 38.72 | 40.95 | 236.66 | **PASS** (15px dilation ring) |
| **C3NS** | `I_margin_r15_ns_inpaint` | 4,058.3 | 0.0% | N/A | 39.88 | 40.97 | 38.87 (-83.6%) | **PASS** (Smooth inpainting) |
| **C4_r15** | `I_margin_r15_placebo` | 4,167.1 | 0.0% | N/A | 38.70 | 40.92 | 65.07 | **PASS** (Matched placebo ring) |
| **C3_r05** | `I_margin_r05_removed` | 1,311.1 | 0.0% | N/A | 39.46 | 40.94 | 224.18 | **PASS** (5px sweep) |
| **C4_r05** | `I_margin_r05_placebo` | 1,295.1 | 0.0% | N/A | 39.45 | 40.93 | 64.12 | **PASS** (5px placebo) |
| **C3_r10** | `I_margin_r10_removed` | 2,754.5 | 0.0% | N/A | 39.11 | 40.95 | 231.05 | **PASS** (10px sweep) |
| **C4_r10** | `I_margin_r10_placebo` | 2,682.7 | 0.0% | N/A | 39.09 | 40.93 | 64.88 | **PASS** (10px placebo) |
| **C3_r20** | `I_margin_r20_removed` | 6,111.3 | 0.0% | N/A | 38.27 | 40.93 | 240.52 | **PASS** (20px sweep) |
| **C4_r20** | `I_margin_r20_placebo` | 5,806.4 | 0.0% | N/A | 38.27 | 40.90 | 65.49 | **PASS** (20px placebo) |

---

## 3. Detailed Audit Findings

### Experiment A: Luminance-Preserved Distant Spatial Scrambling ($C_{5\text{LP}}$)
- **Patch Resolution:** $16 \times 16$ non-overlapping tiles.
- **Invariance:** Across all 3,064 slices, an average of $905.7 \pm 48.2$ patches fell strictly outside $M_{\text{dil15}}$. These patches were permuted deterministically using sample-specific PRNG seeds.
- **Zero Protected Bleeding:** $\max(|I_{C5\text{LP}}[M_{\text{dil15}}] - I_{\text{orig}}[M_{\text{dil15}}|) \equiv 0$.
- **Zero Radiometric Bias:** Mean intensity difference = $0.0000 \pm 0.0000$. Standard deviation difference = $0.0000 \pm 0.0000$.

### Experiment B: Navier-Stokes Boundary-Controlled Infill ($C_{3\text{NS}}$)
- **Algorithm:** Navier-Stokes fluid-dynamics PDE inpainting ([Bertalmio et al., 2001]) using 3-pixel neighborhood propagation along isophotes.
- **Tumor Boundary Preservation:** Unlike the Gaussian blurring of Phase 5 ($C_6$), which bled $1,390$ px into the tumor interior, Navier-Stokes inpainting strictly confines all intensity modifications to $M_{\text{margin}}$. Overlap with $M_{\text{tumor}}$ is exactly **0 pixels**.
- **Step Discontinuity Suppression:** The artificial boundary step gradient drops from $236.66$ (zero-fill $C_3$) down to $38.87$ ($C_{3\text{NS}}$), which is lower than the natural parenchymal-tumor transition ($72.54$).

### Experiment C: Margin Thickness Sweep Geometry
- The 4 discrete radii ($r \in \{5, 10, 15, 20\}$ pixels, equivalent to approx. $2.1\text{ mm}$, $4.3\text{ mm}$, $6.5\text{ mm}$, and $8.7\text{ mm}$) expand monotonically:
  - $r=5$: $1,311.1$ pixels (~$0.5\%$ slice area)
  - $r=10$: $2,754.5$ pixels (~$1.0\%$ slice area)
  - $r=15$: $4,337.9$ pixels (~$1.7\%$ slice area)
  - $r=20$: $6,111.3$ pixels (~$2.3\%$ slice area)
- Contralateral placebo rings achieved an area match ratio of $0.963 \pm 0.041$ across all radii, with **0.00% overlap with the true tumor mask**.
