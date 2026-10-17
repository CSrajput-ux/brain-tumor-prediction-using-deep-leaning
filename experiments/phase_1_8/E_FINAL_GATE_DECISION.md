# E — Final Gate Decision: Protocol Ratification

**Phase:** 1.8 — Final Protocol Ratification  
**Date:** 2026-10-17  
**Auditor:** Independent Medical Imaging & ML Evaluation Specialist  
**Evaluated Manifests:** S0 (`patient_splits.csv`), S1 (`split_regrouped_ssim_0_80.csv`), S2 (`split_regrouped_ssim_0_75.csv`)  
**Decision:** **GO-FOR-BASELINE-ONLY**  

---

## 1. Decision Justification

We issue a **GO-FOR-BASELINE-ONLY** decision.

This decision permits the training of initial baseline classification models on unmanipulated MRI slices ($I_{\text{orig}}$) across the pre-registered sensitivity scenarios (S0, S1, S2) strictly within the locked cross-validation splits. The intervention study ($I_{\text{tumor}}, I_{\text{removed}}, I_{\text{placebo}}, I_{\text{context\_shift}}$) remains **separately gated** and will be unlocked only after baseline checkpoints are frozen and verified.

### Criteria Fulfilled for GO-FOR-BASELINE-ONLY:
1. **Pre-Registration Frozen and Locked:**
   - Formal pre-registration protocol is finalized in [C_FROZEN_PREREGISTRATION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/C_FROZEN_PREREGISTRATION.md).
   - Primary metric (Macro-F1), secondary metrics, paired cluster-bootstrap inference, multiple-comparison corrections (FDR $q = 0.05$), and test-set isolation rules are fully defined before observing any model output.
2. **Interpretive Framework Pre-Registered:**
   - The 3-zone inferential framework ($\Delta < 0.05$ Context Reliance; $0.05 \le \Delta < 0.10$ Dual Reliance; $\Delta \ge 0.10$ Intratumoral Reliance) is locked in [B_EFFECT_SIZE_DECISION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/B_EFFECT_SIZE_DECISION.md), eliminating post-hoc threshold selection.
3. **Sensitivity Protocol Independently Ratified:**
   - Scenarios S1 ($\tau = 0.80$) and S2 ($\tau = 0.75$) achieve complete zero-leakage partitions with perfect sample accounting (3,064 slices), zero patient crossings, zero component crossings, and robust fold balance (max disparity = 2 slices).
   - The percolation artifact at SSIM 0.60 is formally bounded and isolated to exploratory stress-testing in [A_SENSITIVITY_DESIGN_RATIFICATION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/A_SENSITIVITY_DESIGN_RATIFICATION.md).
4. **Scenario Gate Verification Satisfied (`COND-3`):**
   - Verified in [SCENARIO_GATE_VERIFICATION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_7/SCENARIO_GATE_VERIFICATION.md). Under each scenario's threshold, residual cross-fold candidate leakage above $\tau$ is exactly zero.
5. **Epistemic Boundaries Explicitly Documented:**
   - All controlled risks versus fundamentally unknowable factors (missing DICOM headers, unverified cross-hospital identities) are documented and accepted in [D_UNRESOLVED_RISK_RECORD.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/D_UNRESOLVED_RISK_RECORD.md).
6. **Authoritative State Immutability:**
   - Authoritative files (`patient_splits.csv`, `metadata.csv`, `duplicate_pair_review.csv`) remain 100% byte-identical to pre-investigation baselines.
7. **Verification Test Suite:**
   - Full test suite passes 100% across all 60 tests.

---

## 2. Scope and Boundaries of GO-FOR-BASELINE-ONLY

### Permitted Actions Under This Decision:
- Setting up baseline model architectures (e.g., standard ResNet-18 or ConvNeXt-Tiny) on unmanipulated slices ($I_{\text{orig}}$).
- Executing 5-fold cross-validation training under Scenario S0, Scenario S1, and Scenario S2 using fixed random seed 42.
- Evaluating inner-validation loss for early stopping and checkpoint selection.
- Performing single-pass out-of-fold inference on the locked test sets to record baseline Macro-F1.

### Strictly Prohibited Actions (Gated to Next Phase):
- **NO model training occurred in this phase.**
- **NO intervention ablation runs** ($I_{\text{tumor}}, I_{\text{removed}}, I_{\text{placebo}}$) may be conducted until baseline training logs, loss curves, and convergence diagnostics pass an independent Baseline Completion Gate.
- **NO test-set feedback** may be used to alter model architectures, learning rates, or data augmentations.
- **NO claims of clinical diagnostic safety or generalizability** may be made outside the documented epistemic boundaries.

---

## 3. Phase 1.8 Deliverables Map

- [A_SENSITIVITY_DESIGN_RATIFICATION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/A_SENSITIVITY_DESIGN_RATIFICATION.md)
- [B_EFFECT_SIZE_DECISION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/B_EFFECT_SIZE_DECISION.md)
- [C_FROZEN_PREREGISTRATION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/C_FROZEN_PREREGISTRATION.md)
- [D_UNRESOLVED_RISK_RECORD.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/D_UNRESOLVED_RISK_RECORD.md)
- [E_FINAL_GATE_DECISION.md](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/E_FINAL_GATE_DECISION.md)
- [phase_1_8_checksums.json](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_1_8/phase_1_8_checksums.json)
