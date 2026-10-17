# Alternative Protocol Assessment

**Phase:** 1.6 — Independent Review and Alternative Evaluation Design  
**Date:** 2026-10-17  
**Status:** NO-GO remains in force. No model has been trained.

---

## Overview

This document evaluates four alternative evaluation protocols for the planned brain-tumour MRI classifier reliance research. The goal is to determine which protocol(s) can produce scientifically defensible results given the 236 unresolved cross-patient/cross-fold near-duplicate candidates.

The research question is: *To what extent does a brain-tumour MRI classifier rely on tumour-region evidence versus surrounding context?*

No protocol is selected or rejected based on expected accuracy. The evaluation criteria are: scientific defensibility, leakage risk control, statistical adequacy, and suitability for the tumour-versus-context research question.

---

## Current state summary

| Property | Value |
|---|---|
| Total samples | 3064 |
| Patients | 233 (0 overlapping across folds) |
| Folds | 5 patient-grouped folds (~612 samples/fold) |
| Candidate pairs | 236 cross-patient/cross-fold |
| Confirmed duplicates | 0 |
| Confirmed non-duplicates | 0 |
| SSIM ≥ 0.80 | 2 pairs |
| Source file or array equality | 0 pairs |
| Patient IDs involved in candidates | 123 of 233 |
| Samples involved in candidates | 291 of 3064 |

---

## Protocol A: Existing patient-grouped five-fold evaluation

### Description

Use the current patient-grouped 5-fold cross-validation as-is. Each patient (by `cjdata.PID`) is assigned to exactly one fold. Train on 3 folds, validate on 1, test on 1, rotating across all 5 folds.

### Scientific assumptions

1. The `cjdata.PID` field reliably identifies unique patients.
2. Different PIDs represent different patients (i.e., no patient appears under multiple PIDs).
3. No acquisition-level information leaks between folds beyond what PID grouping prevents.

### Leakage risk

**Moderate to high (unquantified).** If any of the 236 candidate pairs represent the same patient under different PIDs, patient-level leakage occurs. The risk is concentrated in:
- 2 pairs with SSIM ≥ 0.80
- 25 pairs with SSIM 0.75–0.80
- PID suffix variants (e.g., MR024780B vs MR024780G) that might represent the same individual

Without acquisition-level identifiers, the magnitude of leakage cannot be bounded.

### Patient and class balance

**Maintained.** The existing split has excellent balance:

| Fold | Patients | Slices | Meningioma | Glioma | Pituitary |
|---|---|---|---|---|---|
| 1 | 47 | 613 | 142 | 286 | 185 |
| 2 | 47 | 614 | 142 | 286 | 186 |
| 3 | 46 | 611 | 142 | 284 | 185 |
| 4 | 46 | 613 | 141 | 285 | 187 |
| 5 | 47 | 613 | 141 | 285 | 187 |

### Sample size impact

None. All 3064 samples are used.

### Statistical uncertainty

Standard 5-fold CV variance applies. Patient-cluster bootstrap (2000 replicates) planned for confidence intervals. With ~612 test samples per fold across 3 classes, per-class precision/recall estimates have reasonable statistical power.

### Suitability for tumour-versus-context research

**Suitable in principle** — the 5-fold structure supports the intervention comparison (original vs tumour-only vs tumour-removed vs placebo). However, if leakage inflates baseline accuracy, intervention effect estimates may be biased (the model may appear to rely less on tumour evidence because it partially memorizes patient identity).

### Missing evidence

- Verified PID reliability
- Resolution of 236 candidate pairs
- Confirmation that PID suffix variants are distinct patients

### Assessment

⚠️ **Proceeds only if PID reliability can be assumed.** Without evidence that the 236 candidates are false positives, this protocol carries an unquantified leakage risk that could undermine the core research question.

---

## Protocol B: Conservative grouping protocol

### Description

Group candidate-related samples together for evaluation. If sample X (in fold A) is a candidate match with sample Y (in fold B), assign both patients' entire slice sets to the same fold. This creates "super-patients" that are conservatively kept together.

**Critical constraint:** The grouping rule must be justified without claiming patient identity. The justification is: "These samples have automated similarity above a screening threshold; we group them to ensure that even if they are related, no information leaks across folds."

### Scientific assumptions

1. Grouping by automated similarity is a conservative precaution, not an identity claim.
2. The grouping does not need to be correct in every case — it needs to be safe (false groupings reduce power but do not introduce leakage).
3. The grouping criterion (pHash ≤ 4/64 AND cross-patient AND cross-fold) was defined before any model was trained.

### Leakage risk

**Minimal for grouped pairs.** Any genuinely related samples are now in the same fold. However:
- The grouping only covers pairs detected by the pHash screening. If related samples exist with pHash > 4, they are missed.
- Grouping by transitive closure could create large "super-patient" clusters that distort fold balance.
- The grouping rule is based on automated measures, not verified identity, which may produce false positives (unnecessarily large groups).

### Patient and class balance impact

**Potentially significant.** Need to quantify:
- How many transitive groups are formed from the 236 pairs
- Whether any group spans more than 2 folds (requiring reassignment of samples from multiple folds into one)
- Whether regrouping causes substantial class imbalance

Preliminary concern: 123 of 233 patient IDs (53%) are involved in at least one candidate pair. Aggressive transitive grouping could cluster a majority of the dataset into a few folds.

### Sample size impact

**No samples are excluded.** All 3064 samples remain. However, fold sizes may become uneven, reducing effective test-set size in some folds.

### Statistical uncertainty

**Increased** relative to Protocol A due to potential fold-size imbalance and correlation between grouped patients. Patient-cluster bootstrap should account for the super-patient groups rather than original PIDs.

### Suitability for tumour-versus-context research

**Suitable if balance is maintained.** The intervention comparison (original vs masked vs placebo) is conducted within each test fold, so fold-balance asymmetry affects statistical power but not the validity of the comparison — provided each fold retains all three classes with reasonable counts.

### Missing evidence

- Transitive closure analysis of the 236 pairs (how many groups, what size)
- Fold-balance analysis after regrouping
- Whether the grouping criterion is too broad (pHash ≤ 4 may capture anatomy-level similarity, not patient-level)
- Justification that this specific grouping threshold is appropriate (vs. a tighter threshold)

### Assessment

⚠️ **Feasible in principle but requires careful implementation.** The transitive closure must be computed and its impact on fold balance assessed before committing. If the resulting groups are small and balance is maintained, this is the strongest safety-first option. If transitive closure creates massive clusters, it may be impractical.

---

## Protocol C: Sensitivity analysis design

### Description

Do not choose a single grouping. Instead, define a family of evaluation protocols parameterized by the grouping assumption:

1. **Baseline (no grouping):** Protocol A.
2. **Conservative grouping (Tier 1 only):** Group only the 2 SSIM ≥ 0.80 pairs.
3. **Conservative grouping (Tier 1+2):** Group pairs with SSIM ≥ 0.75 (27 pairs).
4. **Conservative grouping (all candidates):** Group all 236 pairs (Protocol B).
5. **Maximum exclusion:** Exclude all 291 samples involved in any candidate pair.

Report results under all assumptions. If the tumour-versus-context findings are robust across all grouping assumptions, the conclusion is defensible regardless of which pairs are genuine. If findings change substantially, the specific pairs driving the change are identified and prioritized for human review.

### Scientific assumptions

1. No single grouping assumption can be validated without acquisition-level metadata.
2. Robustness across assumptions is stronger evidence than results under any single assumption.
3. The sensitivity range (from no grouping to full exclusion) brackets the true leakage.

### Leakage risk

**Explicitly bounded.** The sensitivity analysis characterizes the impact of leakage rather than trying to eliminate it. If results are stable across protocols, leakage either does not exist or does not affect the conclusions.

### Patient and class balance

**Varies by assumption.** Must be reported for each scenario. The maximum-exclusion scenario removes 291/3064 samples (9.5%) and 123/233 patients (53%), which may cause severe class imbalance.

### Sample size impact

| Scenario | Samples | Patients |
|---|---|---|
| Baseline (A) | 3064 | 233 |
| Tier 1 only | 3064 (regrouped) | 233 (4 patients regrouped) |
| Tier 1+2 | 3064 (regrouped) | 233 (≤54 patients regrouped) |
| All candidates | 3064 (regrouped) | 233 (≤123 patients regrouped) |
| Maximum exclusion | 2773 | 110 |

### Statistical uncertainty

**Increases with exclusion/regrouping aggressiveness.** The sensitivity analysis should report confidence intervals for each scenario, making the uncertainty-precision trade-off explicit.

### Suitability for tumour-versus-context research

**Strongly suitable.** The tumour-versus-context research question is about relative changes (original accuracy vs masked accuracy). If this relative change is consistent across grouping assumptions, the finding is robust. The sensitivity analysis directly tests whether the conclusion depends on leakage assumptions.

### Missing evidence

- Transitive closure analysis for each grouping threshold
- Class balance under each scenario
- Whether the relative tumour-vs-context effect size changes across scenarios (unknown until model is trained — but the protocol is pre-registered)

### Assessment

✅ **Scientifically strongest option.** Pre-registering a family of analyses and reporting all results is the most transparent approach. It acknowledges uncertainty rather than resolving it with unjustified assumptions. However, it requires careful implementation:
- The grouping scenarios must be defined before training.
- The model must be trained independently under each scenario (separate splits, separate training runs).
- The computational cost is approximately 5× Protocol A.

---

## Protocol D: Independently reviewed subset

### Description

Restrict evaluation to a subset of the dataset that an independent human reviewer has verified is free of cross-fold contamination. Exclude any pair (and potentially the patients involved) that the reviewer cannot confidently classify.

### Scientific assumptions

1. The independent reviewer can reliably distinguish genuine duplicates from false positives.
2. The exclusion criterion is defined before model training.
3. The remaining subset is representative of the full dataset.

### Leakage risk

**Low for reviewed pairs, unknown for unreviewed pairs.** If the reviewer examines all 236 pairs and makes confident decisions, the remaining dataset has a documented provenance. Unreviewed pairs within the same fold are not a leakage concern (they only matter if they cross folds).

### Patient and class balance

**Depends on reviewer decisions.** If the reviewer excludes many patients, balance may suffer. If the reviewer confirms most pairs as non-duplicates, the dataset is nearly intact.

### Sample size impact

**Unknown until review is complete.** Worst case (all 291 involved samples excluded): 2773 samples, 110 patients. Best case (all pairs cleared): 3064 samples, 233 patients.

### Statistical uncertainty

**Depends on exclusion rate.** If substantial exclusions occur, per-class sample sizes may be too small for reliable tumour-versus-context comparisons.

### Suitability for tumour-versus-context research

**Suitable if the reviewed subset is large enough and class-balanced.** The tumour-versus-context research question does not inherently require all 3064 samples, but it does require enough samples per class and per fold to measure effect sizes with reasonable confidence intervals.

### Missing evidence

- Independent reviewer availability
- Reviewer qualification criteria
- Timeline for review completion
- Exclusion criteria and their impact on balance
- Whether the reviewer's expertise covers the specific imaging modality and pathology

### Assessment

⚠️ **Ideal in principle but blocked by logistics.** This is the gold standard — actual expert adjudication — but requires a qualified reviewer who can dedicate time to examining 236 pairs with contact sheets and provenance data. The review must be completed before training begins.

---

## Comparative summary

| Criterion | A: Existing | B: Conservative grouping | C: Sensitivity analysis | D: Reviewed subset |
|---|---|---|---|---|
| Leakage risk | Unquantified | Minimal (for detected pairs) | Bounded | Low (for reviewed pairs) |
| PID reliability assumed | Yes | No (grouped conservatively) | Tested across assumptions | Verified by reviewer |
| Patient/class balance | ✅ Excellent | ⚠️ Needs verification | ⚠️ Varies | ⚠️ Depends on exclusions |
| Sample size | 3064 | 3064 | 3064–2773 | Unknown |
| Computational cost | 1× | 1× | ~5× | 1× |
| Pre-training requirements | None | Transitive closure analysis | Scenario definitions | Expert review completion |
| Scientific transparency | Low | Moderate | High | High |
| Suitable for tumour-vs-context | ⚠️ If leakage-free | ✅ If balanced | ✅ Strongest | ✅ If sufficient data |
| Missing evidence blocking | PID verification | Cluster analysis | None (pre-registerable) | Reviewer availability |

---

## Recommendation

### Primary: Protocol C (Sensitivity Analysis) — CONDITIONAL-GO

Protocol C is the most scientifically defensible option available without external expert review or acquisition-level metadata. It:

1. **Acknowledges uncertainty** rather than resolving it with unjustified assumptions.
2. **Pre-registers** the analysis family before training, preventing post-hoc selection.
3. **Bounds the leakage impact** by showing whether conclusions change across grouping assumptions.
4. **Does not require** patient identity claims, external reviewer access, or dataset-provider cooperation.
5. **Supports the core research question** directly — if tumour-versus-context reliance is robust across leakage assumptions, the finding is stronger than any single-protocol result.

### Conditions for Protocol C

Before training can begin:

1. **Transitive closure analysis** must be completed for each grouping threshold to verify fold-balance feasibility.
2. **All grouping scenarios** must be defined and documented before any model training.
3. **Class balance** under each scenario must be verified as sufficient (each class in each fold).
4. **The sensitivity analysis plan** must be recorded in the experiment configuration.
5. **The existing pretraining gate** must pass under at least the baseline scenario.
6. **No labels, fold assignments, or patient IDs** are changed in the authoritative dataset; regrouping scenarios are implemented as separate split manifests.

### Secondary: Protocol D (Expert Review) — parallel track

If an independent reviewer with appropriate qualifications becomes available, Protocol D provides stronger evidence for individual pair resolution. It can complement Protocol C: reviewer decisions on Tier 1 and Tier 2 pairs would reduce the sensitivity range and strengthen conclusions.

### Not recommended as standalone

- **Protocol A** cannot be defended without PID reliability evidence.
- **Protocol B** without sensitivity analysis makes an implicit claim about the correct grouping threshold.

---

## What evidence is still missing

| Evidence | Required for | Obtainable? |
|---|---|---|
| Transitive closure analysis of candidate groups | Protocols B, C | Yes (from existing data) |
| Fold balance under each grouping scenario | Protocols B, C | Yes (from existing data) |
| Independent expert pair review | Protocol D | Requires external reviewer |
| Acquisition-level metadata from dataset provider | All protocols | Unlikely ("no further details available") |
| Verified `cvind.mat` mapping | Not required (unused) | Low priority |
| Literature review of prior Cheng dataset leakage analyses | All protocols | Yes (web search) |

---

## Next steps

1. Implement transitive closure analysis for the 236 candidate pairs at multiple SSIM thresholds.
2. Generate candidate regrouped split manifests and assess fold balance.
3. Pre-register the sensitivity analysis plan with explicit scenario definitions.
4. If all balance checks pass, update the pretraining gate to accept the sensitivity-analysis protocol.
5. In parallel, prepare the expert review package (this phase) for any available independent reviewer.
