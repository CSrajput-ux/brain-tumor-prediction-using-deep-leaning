# Phase 1.7 Decision — Sensitivity Analysis and Pre-Registration

**Evaluation Specialist:** Independent Medical Imaging & ML Evaluation Auditor  
**Date:** 2026-10-17  
**Phase:** 1.7 — Sensitivity Analysis and Pre-Registration  
**Decision:** **CONDITIONAL-GO**  

---

## 1. Decision Summary

We issue a **CONDITIONAL-GO** recommendation for the brain-tumor MRI classifier evaluation.

A feasible, scientifically rigorous evaluation design under **Protocol C (Sensitivity Analysis across Grouping Assumptions)** has been successfully established and verified:
1. **Transitive Closure Characterized (C1):** Evaluated across all four pre-registered SSIM thresholds [0.80, 0.75, 0.70, 0.60]. Group structure, component distributions, and percolation boundaries are mathematically and empirically documented.
2. **Regrouped Manifests Verified (C2):** Candidate 5-fold cross-validation manifests generated for all thresholds. Folds at SSIM ≥ 0.80, 0.75, and 0.70 achieve strict zero-leakage (0 patient crossings, 0 component crossings) with full sample accounting (3,064 slices) and robust class balance ($\ge 141$ slices per class per fold, far exceeding the 50-slice project threshold).
3. **Percolation Breakdown Identified (Scientific Honesty):** At SSIM ≥ 0.60, transitive closure undergoes percolation, producing an 807-slice giant component spanning distinct tumor classes (glioma and meningioma). We have demonstrated that this is an artifact of general brain anatomy rather than duplicate acquisitions, and have formally bounded the primary evaluation to $\tau \in [0.75, 0.80]$.
4. **Pre-Registration Draft Completed (C3/C6):** Hypotheses, primary metric (Macro-F1), secondary metrics, 5-intervention contrast battery, bootstrap CI methodology, and invalidation rules are rigorously pre-registered.

---

## 2. Mandatory Conditions Remaining for Final GO

Training remains **STRICTLY BLOCKED** until the following 3 conditions are resolved:

| ID | Mandatory Condition | Action Required | Status |
|---|---|---|---|
| **COND-1** | **Effect Size Bound Approval** | The supervising researcher must formally select and approve the minimum practically meaningful effect size bound $\tau_{\Delta}$ in `PREREGISTRATION_DRAFT.md` (candidate options: 0.05 or 0.10 Macro-F1). | **Pending Researcher Sign-Off** |
| **COND-2** | **Boundary Scope Ratification** | Formal agreement to bound the primary sensitivity family to Scenarios S0 (Baseline), S1 ($\tau = 0.80$), and S2 ($\tau = 0.75$), treating $\tau = 0.60$ strictly as a secondary boundary stress-test. | **Pending Researcher Sign-Off** |
| **COND-3** | **Pretraining Gate Verification** | Execute the automated pretraining gate script against the newly generated scenario manifests to confirm downstream training pipeline compatibility. | **Ready for Execution** |

---

## 3. Prohibited Actions During Phase 1.7

In strict compliance with evaluation integrity instructions:
- **No model has been trained.**
- **No GPU compute was utilized.**
- **No authoritative source data were altered:** Checksums of `patient_splits.csv`, `metadata.csv`, and all prior investigation reports match baselines 100%.
- **No candidate pairs were relabeled as verified duplicates.**
- **No component was split to force artificial fold symmetry.**
- **No sample was discarded or filtered.**
- **No research novelty or performance superiority was claimed.**

---

## 4. Deliverable Directory Map

All deliverables are archived in `experiments/phase_1_7/`:
- [C1_TRANSITIVE_CLOSURE_REPORT.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/C1_TRANSITIVE_CLOSURE_REPORT.md) — Detailed graph analysis, size distributions, and percolation findings.
- [C2_REGROUPED_FOLD_ASSESSMENT.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/C2_REGROUPED_FOLD_ASSESSMENT.md) — Fold distributions, class proportions, and balance metrics.
- [PREREGISTRATION_DRAFT.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/PREREGISTRATION_DRAFT.md) — Study pre-registration with planned contrasts and bootstrap methodology.
- [component_summary_by_threshold.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/component_summary_by_threshold.csv) — Machine-readable summary metrics across thresholds.
- [component_membership.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/component_membership.csv) — Complete 3,064-sample mapping across all component and group IDs.
- [candidate_grouped_manifests/](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/candidate_grouped_manifests/) — 4 deterministic regrouped 5-fold split manifests.
- [phase_1_7_checksums.json](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/phase_1_7_checksums.json) — Cryptographic SHA-256 verification of all 26 authoritative and phase artifacts.
