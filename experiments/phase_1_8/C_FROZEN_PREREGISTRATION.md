# C — Frozen Pre-Registration Protocol

**Phase:** 1.8 — Final Protocol Ratification  
**Status:** **FROZEN AND RATIFIED PRIOR TO MODEL TRAINING**  
**Date Locked:** 2026-10-17  
**Project:** Investigating Brain-Tumour MRI Classifier Reliance on Tumour-Region Evidence versus Surrounding Anatomical Context  
**Lead Auditor / Evaluator:** Independent Evaluation Specialist & Reproducibility Auditor  
**Primary Sensitivity Manifests:**  
- Scenario S0 (Baseline): `prepared_full_run/patient_splits.csv`
- Scenario S1 (SSIM ≥ 0.80): `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_80.csv`
- Scenario S2 (SSIM ≥ 0.75): `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_75.csv`
- Exploratory Boundary: `split_regrouped_ssim_0_60.csv` (Scenario S3b Stress Test)

---

## 1. Primary Research Question and Hypotheses

### Research Objective
To quantitatively determine whether deep convolutional and attention-based neural networks trained on brain MRI slices to classify intracranial neoplasms (glioma, meningioma, pituitary tumor) rely on pathognomonic visual evidence inside the annotated tumor region or on surrounding parenchymal, ventricular, and cranial anatomical context.

### Pre-Registered Hypotheses
- **$H_1$ (Intratumoral Reliance Hypothesis):** Diagnostic performance depends primarily on intratumoral features. Masking the tumor interior ($I_{\text{removed}}$) causes a decisive performance collapse ($\Delta_{\text{removal}} \ge 0.10$ Macro-F1), while isolating the tumor ($I_{\text{tumor}}$) retains high accuracy. Placebo masking in normal tissue ($I_{\text{placebo}}$) produces negligible change.
- **$H_0$ (Context Shortcut Hypothesis):** Diagnostic performance relies predominantly on surrounding anatomical context, slice level, or acquisition shortcuts. Masking the tumor interior causes little degradation ($\Delta_{\text{removal}} < 0.05$ Macro-F1), while isolating the tumor causes severe performance collapse.

---

## 2. Evaluation Metrics and Primary Contrast

### Primary Metric: Macro-Averaged F1 Score ($\text{Macro-F1}$)
$$\text{Macro-F1} = \frac{1}{3} \left( F1_{\text{glioma}} + F1_{\text{meningioma}} + F1_{\text{pituitary}} \right)$$
Evaluated on pooled out-of-fold predictions across all 3,064 test evaluations.

### Secondary Metrics
1. **Balanced Accuracy:** Unweighted average of per-class sensitivity (recall).
2. **Per-Class Metrics:** Precision, Recall, and F1 score for each of the three diagnostic classes.
3. **Confusion Matrix:** Full $3 \times 3$ contingency table of ground-truth vs predicted classes.
4. **Brier Score / Cross-Entropy Loss:** Probabilistic calibration metrics.

### Primary Experimental Contrasts
1. **Intratumoral Reliance Contrast ($\Delta_{\text{removal}}$):**
   $$\Delta_{\text{removal}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{removed}})$$
2. **Tumor Sufficiency Contrast ($\Delta_{\text{tumor}}$):**
   $$\Delta_{\text{tumor}} = \text{Macro-F1}(I_{\text{tumor}}) - \text{Chance-F1} \quad (\text{Chance} \approx 0.333)$$
3. **Placebo Specificity Contrast ($\Delta_{\text{placebo}}$):**
   $$\Delta_{\text{placebo}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{placebo}})$$
4. **Context Robustness Contrast ($\Delta_{\text{context\_shift}}$):**
   $$\Delta_{\text{context\_shift}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{context\_shift}})$$

---

## 3. Matched 5-Condition Intervention Battery

Every test slice $s$ is evaluated under five matched conditions:

| Condition | Visual Operation | Purpose |
|---|---|---|
| **$I_{\text{orig}}$** | Original prepared MRI slice ($512 \times 512$) | Benchmark performance baseline |
| **$I_{\text{tumor}}$** | All pixels outside binary tumor mask set to zero | Tests sufficiency of tumor alone |
| **$I_{\text{removed}}$** | Pixels inside binary tumor mask set to zero / infilled | Tests necessity of tumor interior |
| **$I_{\text{placebo}}$** | Equal-area non-tumoral region in contralateral hemisphere masked | Controls for sharp border masking artifacts |
| **$I_{\text{context\_shift}}$** | Context contrast perturbed ($\pm 20\%$) with tumor unchanged | Tests sensitivity to context drift |

---

## 4. Paired Comparison and Patient-Aware Uncertainty Estimation

### Paired Comparison on Matched Samples
Because every model evaluates identical test slices across all five intervention conditions, independent-sample tests are invalid. We employ **paired statistical comparisons**:
1. **Paired Cluster Bootstrap Difference:** Resample clusters with replacement ($B = 1,000$). For each bootstrap replicate $b$, compute:
   $$\Delta_{\text{removal}}^{(b)} = \text{Macro-F1}(I_{\text{orig}})^{(b)} - \text{Macro-F1}(I_{\text{removed}})^{(b)}$$
   The 95% Percentile Confidence Interval is $[\Delta_{0.025}, \Delta_{0.975}]$.
2. **McNemar's Paired Discordance Test:** For binary correct/incorrect classification outcomes between $I_{\text{orig}}$ and $I_{\text{removed}}$, evaluating whether tumor removal significantly alters classification outcomes.
3. **Wilcoxon Signed-Rank Test:** Conducted on per-patient mean F1 differences across the 233 patients.

### Patient-Aware Cluster Bootstrap (Preventing Slice-Leakage in CIs)
Slices originating from the same patient share correlated brain anatomy. Resampling at the individual slice level artificially inflates statistical significance.
- **Pre-Registered Rule:** Bootstrap resampling **MUST be performed at the cluster level** (Patient ID or Combined Evaluation Group).
- In each bootstrap draw $b$, clusters are sampled with replacement until the resampled dataset matches original sample size, preserving intra-patient slice correlations.

---

## 5. Multiple-Comparison Handling

When testing the battery of 4 planned contrasts ($\Delta_{\text{removal}}, \Delta_{\text{tumor}}, \Delta_{\text{placebo}}, \Delta_{\text{context\_shift}}$) across the primary sensitivity scenarios (S0, S1, S2):
- **Primary Control:** Benjamini-Hochberg procedure controlling False Discovery Rate (FDR) at $q = 0.05$.
- **Conservative Sensitivity Check:** Holm-Bonferroni family-wise error rate control at $\alpha = 0.05$.

---

## 6. Model Selection and Strict Test-Set Isolation

1. **Outer 5-Fold Partition:** Fixed by the ratified manifest. Test folds are **strictly sealed** until training is finalized.
2. **Inner Train/Validation Split:** Within the 4 training folds (80% of data), an inner 80/20 train/validation split is created respecting combined evaluation group boundaries.
3. **Checkpoint Locking:** The model checkpoint achieving the minimum cross-entropy loss on the inner validation set is selected.
4. **Single Test Evaluation:** The locked checkpoint is evaluated exactly once on the held-out test fold. No test-set performance feedback is used to tune hyperparameters, learning rates, epochs, or architectures.

---

## 7. Assessment of Intervention Artifacts and Distribution Shifts

### Critical Causal Caveat: Confidence Changes Are Not Direct Causal Proof
> [!WARNING]
> **EVIDENTIARY BOUNDARY ON OCCLUSION & ATTRIBUTION**
>
> Do not treat a confidence change after masking as definitive causal proof. A decrease in model softmax probability following tumor masking does NOT constitute definitive causal proof that the model understood or used pathognomonic tumor features.
>
> Deep neural networks are sensitive to Out-of-Distribution (OOD) covariate shift. Setting an image region to zero introduces artificial high-frequency sharp borders, alters local image statistics, and disrupts convolutional feature maps. A model may fail on $I_{\text{removed}}$ simply because a black hole was cut into the image, not because it was using tumor histology.

### Mandatory Artifact Controls
To guard against this confounder:
1. **Placebo Contrast Calibration:**
   If $\Delta_{\text{placebo}} \approx \Delta_{\text{removal}}$, the performance loss is an **artifact of artificial mask insertion**, NOT tumor reliance. Intratumoral reliance is supported only if:
   $$\Delta_{\text{removal}} - \Delta_{\text{placebo}} \ge 0.05$$
2. **Smooth Boundary Sensitivity Check:**
   In addition to sharp binary masking, a subset evaluation with 5-pixel Gaussian border feathering and mean parenchymal infilling will be evaluated to verify that edge discontinuities do not drive the observed effect.

---

## 8. Missing Data and Failed-Run Policy

1. **Missing Data Policy:** All 3,064 images are verified and present. Zero missing values or dropped test samples are tolerated.
2. **Failed Run Policy:** If a training run crashes due to hardware failure or out-of-memory error:
   - The run is re-initialized with the identical fixed seed (Seed 42) after clearing GPU cache.
   - If numerical divergence (NaN loss) occurs, the failure is logged and the run is aborted. No hyperparameters or seeds may be silently swapped.
3. **Seed Battery:** Primary results are reported for Seed 42. Confirmation runs with Seeds 43 and 44 will be executed to verify numerical stability.

---

## 9. Policy for Reporting Null, Negative, and Inconclusive Findings

- **Null Result:** If the 95% cluster-bootstrap CI for $\Delta_{\text{removal}}$ spans zero or is bounded below 0.05, the study will explicitly conclude that the model demonstrates no evidence of primary intratumoral reliance.
- **Dual Reliance:** If $\Delta_{\text{removal}} \in [0.05, 0.10)$ and $F1_{\text{removed}} \gg \text{Chance}$, the study will conclude that the model operates via dual pathways, utilizing both context and lesion features.
- **Inconclusive Result:** If the 95% CI spans across the 0.05 or 0.10 boundary thresholds, or if findings contradict between Scenario S1 and Scenario S2, the study will report the outcome as inconclusive and sensitive to leakage assumptions.
- **No Post-Hoc Data Dredging:** No protocol, threshold, or model subsetting may be altered after viewing test outcomes.
