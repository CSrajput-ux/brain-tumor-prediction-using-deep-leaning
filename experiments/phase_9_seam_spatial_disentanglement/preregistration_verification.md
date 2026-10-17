# Preregistration Verification & Pre-Execution Gate Audit

**Document ID:** `PHASE_9_PREREGISTRATION_VERIFICATION`  
**Project:** Cheng Brain Tumor MRI Classification Robustness Study  
**Phase:** 9 — Controlled Experiment: Seam Artifacts vs. Spatial-Layout Disruption  
**Date:** 2026-10-17  
**Authoritative Standard:** Strict Pre-Execution Protocol Verification  
**Gate Decision:** **`PRE-EXECUTION GATE PASSED`**  

---

## 1. Authoritative Protocol Verification

Prior to generating new image conditions or running model inference, the experimental specification was cross-referenced against authoritative Phase 8 and Phase 6 artifacts:
- [`proposed_preregistration.md`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_8_novelty_discovery/proposed_preregistration.md)
- [`minimum_experiment_decision.md`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_8_novelty_discovery/minimum_experiment_decision.md)
- [`selected_research_direction.md`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_8_novelty_discovery/selected_research_direction.md)
- [`limitations_and_unresolved_questions.md`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_8_novelty_discovery/limitations_and_unresolved_questions.md)
- [`PHASE_6_REPORT.md`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_6_spatial_controls/PHASE_6_REPORT.md)
- [`PHASE_6_1_CLAIM_SANITY_REPORT.md`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_6_1_claim_sanity/PHASE_6_1_CLAIM_SANITY_REPORT.md)

---

## 2. Locked Experimental Specifications

| Protocol Dimension | Preregistered Specification | Phase 9 Implementation | Status |
| :--- | :--- | :--- | :---: |
| **Dataset Cohort** | Jun Cheng Figshare 1512427 (3,064 2D T1-CE slices, 233 patient IDs) | Exactly identical: 3,064 slices loaded from `prepared_full_run/` | **VERIFIED** |
| **Diagnostic Classes** | Meningioma ($n=708$), Glioma ($n=1,426$), Pituitary ($n=930$) | Integer mapping: 0: meningioma, 1: glioma, 2: pituitary | **VERIFIED** |
| **Checkpoints** | 15 frozen ResNet-50 checkpoints across S0, S1, S2 (5 folds each) | Loaded strictly read-only from `experiments/phase_2_baseline/` | **VERIFIED** |
| **Preprocessing** | 512x512 native $\to$ bilinear resize to 224x224 $\to$ ImageNet normalization | Identical torchvision evaluation pipeline | **VERIFIED** |
| **Primary Metric** | Macro-Averaged F1 Score (Macro-F1) | Arithmetic mean of per-class F1 scores: $\frac{1}{3}\sum_{c=0}^2 F1_c$ | **VERIFIED** |
| **Statistical Unit** | Paired patient/cluster bootstrap ($B=2,000$, seed=42) | Synchronized cluster resampling across all 4 conditions concurrently | **VERIFIED** |
| **Decision Thresholds** | $\Delta \ge 0.150$ (Layout reliance); $\Delta < 0.030$ (Artifact dominance) | Locked without post-hoc modification | **VERIFIED** |

---

## 3. Four Locked Condition Definitions

1. **C0 — Original Baseline ($I_{\text{orig}}$):**
   - Unmanipulated test image baseline.
   - Serves as the reference standard.
2. **C1 — Seam-Only Control ($I_{\text{seam\_only}}$):**
   - Introduces artificial tile-boundary step discontinuities at the exact same $16 \times 16$ tile boundaries without rearranging underlying anatomical content.
   - Evaluates whether high-frequency grid seams alone cause diagnostic degradation.
   - *Invariants:* Tumor core and 15px margin have **0 pixels altered**.
3. **C2 — Seam-Suppressed Spatial Rearrangement ($I_{\text{seamless}}$):**
   - Scrambles the $16 \times 16$ distant tiles outside the 15px protected margin (identical permutation to C5LP), but smoothly suppresses the artificial tile-boundary seams using cross-fade boundary blending (ksize=9, sigma=2.5) along the 2-pixel seam grid.
   - Reduces the artificial seam Sobel jump by over 60% while preserving macroscopic spatial rearrangement.
   - *Invariants:* Tumor core and 15px margin have **0 pixels altered**.
4. **C3 — Original C5LP Scramble ($I_{\text{C5LP}}$):**
   - Re-evaluates the historical Phase 6 condition ($16 \times 16$ patch scrambling with exact mean and variance preservation).
   - Replicates the reference performance drop ($\Delta \approx +0.42$).

---

## 4. Locked Hypotheses

- **$H_1$ (Seam-Artifact Dominance):** Seam artifacts alone in C1 cause substantial degradation ($\Delta_{\text{C1}} \ge 0.150$), and eliminating seams in C2 eliminates the degradation ($\Delta_{\text{C2}} < 0.030$).
- **$H_2$ (True Spatial-Layout Dominance):** Seams alone have negligible effect ($\Delta_{\text{C1}} < 0.030$), while seam-suppressed rearrangement in C2 maintains a catastrophic drop ($\Delta_{\text{C2}} \ge 0.150$).
- **$H_3$ (Mixed Mechanism):** Both seam artifacts and spatial layout contribute significantly ($0.030 \le \Delta_{\text{C1}} < \Delta_{\text{C3}}$ and $0.080 \le \Delta_{\text{C2}} < \Delta_{\text{C3}}$).
- **$H_0$ (Inconclusive / No Demonstrated Spatial Effect):** Neither condition shows a reliable, interpretable effect.

---

## 5. Pre-Execution Gate Ruling

**`PRE-EXECUTION GATE: PASS`**

All baseline definitions, condition formulas, sample counts, checkpoint hashes, and decision thresholds are verified and frozen. Execution of the controlled experiment is authorized.
