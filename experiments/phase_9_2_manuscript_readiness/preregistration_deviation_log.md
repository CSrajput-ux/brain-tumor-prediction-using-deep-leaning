# Phase 9.2: Preregistration Deviation & Protocol Audit Log

**Project:** Disentangling Anatomical Context from High-Frequency Edge Artifacts in Brain MRI Deep Classifiers  
**Audit Phase:** Phase 9.2 Manuscript Readiness Audit  
**Date:** 2026-10-17  

---

## 1. Audit Against Phase 8 Locked Preregistration

The experimental protocol executed in Phase 9 was audited against the locked preregistration in `experiments/phase_8_novelty_discovery/proposed_preregistration.md`:

| Protocol Dimension | Preregistered Specification | Actual Execution in Phase 9 | Deviation Status | Epistemic Impact |
| :--- | :--- | :--- | :---: | :--- |
| **Model Checkpoints** | 15 frozen ResNet-50 checkpoints from Phase 2 ($S_0, S_1, S_2 	imes 5$ folds) | Exactly the 15 frozen checkpoints loaded; no retraining or parameter updates | **NO DEVIATION** | None; strict provenance preserved. |
| **Primary Metric** | Macro-F1 across 3 tumour classes | Macro-F1 computed out-of-fold across held-out test splits | **NO DEVIATION** | None; metric identical to Phase 2–6. |
| **Protected Zone** | Tumour core + 15-pixel dilation margin untouched | 0 pixels altered in tumour core or 15px margin across all 3,064 slices | **NO DEVIATION** | None; verified with 100% precision. |
| **Resampling Unit** | Patient ID ($S_0$), Combined Group ID ($S_1, S_2$), $B=2,000$ | Patient ID ($S_0$), Combined Group ID ($S_1, S_2$), $B=2,000$, seed 42 | **NO DEVIATION** | None; cluster bootstrap completely faithful. |
| **Practical Threshold** | $\Delta_{	ext{C2 vs C0}} \ge 0.150$ | Evaluated against 0.150; observed $\Delta = +0.4808$ ($S_0$), $+0.4390$ ($S_1$), $+0.4114$ ($S_2$) | **NO DEVIATION** | Substantially exceeds locked threshold. |
| **Contrast Sign Convention** | Drop defined as $\Delta = 	ext{Macro-F1}_A - 	ext{Macro-F1}_B$ | In Phase 9 report, $C_3 	ext{ vs } C_2$ was reported as $-0.0593$ with $A=C_2, B=C_3$. In text, this was referred to as "Sensitivity to Seam Suppression". | **CLARIFIED IN AUDIT** | No empirical impact; clarified that negative sign reflects $C_2$ performing worse than $C_3$. |
| **Causal Ratio Language** | Report described seam drop as "accounting for ~72% of the decline" | Ratio $\Delta_{C1}/\Delta_{C3} = 72.2\%$. Audit mandates treating this as a descriptive marginal ratio, not an additive causal decomposition. | **RESTRICTED IN AUDIT** | Essential epistemic boundary: non-linear interaction prohibited causal decomposition claim. |

---

## 2. Summary Audit Finding
There were **zero protocol violations** regarding data handling, model training, sample selection, or protected geometry. The minor points of clarification identified during Phase 9.1 and Phase 9.2 concern report phrasing and contrast sign labeling, all of which have been documented and reconciled.
