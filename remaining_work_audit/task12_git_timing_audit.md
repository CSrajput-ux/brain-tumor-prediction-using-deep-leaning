# Task 12: Git History, Commit Timestamps, and Hypothesis Timing Audit

**Audit Date:** October 2026  
**Auditor:** Independent Scientific Audit Lead (Antigravity IDE)  
**Target Invariants:** Prospective specification vs post hoc exploration verification.

---

## 1. Commit History Traceability

We inspected the complete Git commit log across the relevant scripts, configuration files, and prediction outputs:

| Artifact | First Commit Hash | Commit Timestamp | Commit Message |
| :--- | :--- | :--- | :--- |
| `scripts/run_phase_9_seam_spatial_disentanglement.py` | `79eb73d` | 2026-10-17 22:12:15 +0530 | `feat(core): initial commit with root configs, README, and pipeline scripts` |
| `experiments/phase_8_novelty_discovery/proposed_preregistration.md` | `e906e71` | 2026-10-17 22:40:28 +0530 | `experiments: batch 17/22 (10 files)` |
| `experiments/phase_9_seam_spatial_disentanglement/experiment_config.yaml` | `415df14` | 2026-10-17 22:40:30 +0530 | `experiments: batch 21/22 (10 files)` |
| `experiments/phase_9_seam_spatial_disentanglement/matched_predictions.csv` | `415df14` | 2026-10-17 22:40:30 +0530 | `experiments: batch 21/22 (10 files)` |
| `experiments/phase_9_seam_spatial_disentanglement/primary_metrics.csv` | `415df14` | 2026-10-17 22:40:30 +0530 | `experiments: batch 21/22 (10 files)` |
| `publication/manuscript_v1/manuscript.md` | `10526e0` | 2026-10-17 22:40:21 +0530 | `publication: batch 8/22 (10 files)` |

---

## 2. Epistemic Timing Determination

1. **Batch Commit Timing Constraint:**
   - Both `experiment_config.yaml` and the corresponding prediction table `matched_predictions.csv` were introduced into git version control within the same automated batch commit (`415df14`) at `2026-10-17 22:40:30 +0530`.
   - The proposed preregistration document (`proposed_preregistration.md`) was committed in batch 17 (`e906e71`) at `2026-10-17 22:40:28 +0530` (two seconds prior).
   - Because all files were committed during a unified repository staging process, git history timestamps alone cannot independently prove that the configuration was locked before prediction execution commenced.

2. **Classification of Claims:**
   - **Primary Spatial Sensitivity Contrasts ($C_3 \text{ vs } C_0$, $C_1 \text{ vs } C_0$, $C_2 \text{ vs } C_0$, $C_3 \text{ vs } C_1$):**
     *Status:* **Documented before analysis within internal phase milestone reports, but git timing uncertain.**
     *Evidence:* Outlined in Phase 8 (`proposed_preregistration.md`) with explicit numeric thresholds ($\Delta \ge 0.150$ for scrambling, $\Delta < 0.030$ for seam equivalence).
   - **Seam Suppression Sensitivity Contrast ($C_3 \text{ vs } C_2$):**
     *Status:* **Exploratory / Post hoc.**
     *Evidence:* Evaluated to explore residual edge sensitivity; nonsignificant in Scenarios $S_1$ and $S_2$.
   - **True Seam-Only Control (Width $w=2, 3$ with unpermuted interior):**
     *Status:* **Prospectively specified in remaining work audit protocol; newly implemented in Stage 3.**

---

## 3. Mandatory Manuscript Epistemic Guardrail

In accordance with scientific integrity guidelines:
- We **refuse to claim** formal public pre-registration on an external registry (such as OSF or ClinicalTrials.gov) since none exists.
- The manuscript must strictly describe these thresholds as:
  *"Internally locked milestone decision criteria pre-specified in the project's phased research protocol prior to model execution, but not deposited on an immutable external registry."*
