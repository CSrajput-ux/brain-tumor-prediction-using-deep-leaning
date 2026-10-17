# Statistical Validity Audit: Phase 6 Spatial Controls

**Document ID:** `PHASE_6_1_STATISTICAL_VALIDITY_AUDIT`  
**Phase:** 6.1 — Claim and Result Sanity Audit  
**Target:** Synchronized Paired Patient-Cluster Bootstrap and McNemar Testing  
**Date:** 2026-10-17  
**Auditor:** Independent Scientific and Statistical Reviewer  

---

## 1. Audit of the Resampling Protocol

### A. Cluster Definition and Integrity
- **Scenario S0:** Grouped by `patient_id` (233 clusters across 3,064 slices).
- **Scenario S1:** Grouped by `combined_group_id` (231 clusters, SSIM $\ge 0.80$ duplicate components merged).
- **Scenario S2:** Grouped by `combined_group_id` (217 clusters, SSIM $\ge 0.75$ duplicate components merged).
- **Audit Check:** Verified. Resampling entire patient/component clusters prevents within-patient leakage from artificially narrowing confidence intervals.

### B. Synchronization across Conditions
- **Protocol:** In each bootstrap iteration $b \in \{1, \dots, 2000\}$, a single set of resampled cluster indices was drawn using PRNG seed 42.
- **Audit Verification:** The exact same resampled clusters were used to sum the confusion matrices of all 14 conditions simultaneously. This ensures that paired differences ($\Delta = \text{Macro-F1}(C_A) - \text{Macro-F1}(C_B)$) reflect paired sample-level variation rather than between-resample noise.

---

## 2. Metric Computation & Multiple-Comparison Review

### A. Exact Macro-F1 Recomputation
- Macro-F1 was recalculated at each bootstrap replicate directly from the pooled resampled $3 \times 3$ confusion matrix:
  $$\text{Macro-F1} = \frac{1}{3} \sum_{k=1}^3 \frac{2 \cdot \text{TP}_k}{2 \cdot \text{TP}_k + \text{FP}_k + \text{FN}_k}$$
- Recomputing metrics on the aggregated confusion matrix avoids harmonic-mean distortion that occurs when averaging per-sample F1 scores.

### B. McNemar Test Implementation
- Paired classification transitions were tabulated into $2 \times 2$ contingency tables:
  - $n_{10}$: Correct under $C_A$, Incorrect under $C_B$
  - $n_{01}$: Incorrect under $C_A$, Correct under $C_B$
- Evaluated using Edwards' continuity correction:
  $$\chi^2 = \frac{(|n_{10} - n_{01}| - 1)^2}{n_{10} + n_{01}}$$
- **Audit Finding:** The McNemar tests were calculated strictly and accurately.

---

## 3. Strict Interpretation Rules Audit

1. **Equivalence from Spanning Zero:**
   - In S0 and S2, the 95% bootstrap CI for $C_{3\text{NS}}$ spans zero (e.g., S0: $[-0.0086, +0.0045]$).
   - In S1, the 95% CI is $[+0.0006, +0.0153]$, which nominally excludes zero.
   - **Audit Verdict:** Phase 6 properly reported that the drop under $C_{3\text{NS}}$ is $< 0.008$, which is well below the pre-registered meaningful effect-size threshold ($0.0300$). However, the report must avoid phrasing such as "proves exact zero reliance" and instead use: "demonstrates no practically meaningful performance degradation within statistical precision."

2. **Dose-Response Monotonicity:**
   - Net margin reliance across radii $r \in \{5, 10, 15, 20\}$ pixels was $0.0309 \to 0.0249 \to 0.0234 \to 0.0116$ (S0).
   - Phase 6 correctly reported the absence of a monotonic dose-response curve and avoided inventing post-hoc rationalizations.
