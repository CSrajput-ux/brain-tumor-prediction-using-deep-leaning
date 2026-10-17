# Study Pre-Registration Protocol (Draft)

**Title:** Reliance of Brain-Tumor MRI Deep Learning Classifiers on Intratumoral Features versus Surrounding Parenchymal and Anatomical Context  
**Phase:** 1.7 — Sensitivity Analysis and Pre-Registration  
**Date:** 2026-10-17  
**Pre-Registration Status:** **DRAFT — PENDING RESEARCHER APPROVAL OF NUMERIC EFFECT SIZE BOUNDS**  
**Lead Author / Evaluator:** Independent Evaluation Specialist & Reproducibility Auditor  
**Authoritative Split Baseline:** `prepared_full_run/patient_splits.csv` (SHA-256: `c45e0eea02f0...`)  
**Sensitivity Family:** Protocols S0, S1 (SSIM ≥ 0.80), S2 (SSIM ≥ 0.75), S3 (SSIM ≥ 0.70)  

---

## 1. Primary Research Question and Hypotheses

### Primary Research Question
Do deep neural network MRI classifiers trained on the Cheng brain tumor dataset distinguish tumor classes (glioma, meningioma, pituitary) by leveraging pathognomonic evidence inside the tumor boundary, or do they rely substantially on non-tumoral surrounding brain parenchyma, cranial anatomy, or acquisition shortcuts?

### Formal Hypotheses
- **$H_1$ (Intratumoral Reliance Hypothesis):** The classifier relies primarily on intratumoral imaging features.
  - *Operational Prediction:* Removal of the tumor region ($I_{\text{removed}}$) will cause a substantial, statistically significant drop in diagnostic performance ($\Delta_{\text{removal}} > \tau_{\text{meaningful}}$), while isolating the tumor region ($I_{\text{tumor}}$) will retain high diagnostic discriminability. A placebo excision in normal tissue ($I_{\text{placebo}}$) will produce negligible degradation ($|\Delta_{\text{placebo}}| \approx 0$).
- **$H_0$ (Context Reliance / Shortcut Learning Hypothesis):** The classifier relies predominantly on surrounding parenchymal context, slice level, cranial contours, or acquisition artifacts.
  - *Operational Prediction:* Removal of the tumor region ($I_{\text{removed}}$) will produce little or no performance degradation, while isolating the tumor ($I_{\text{tumor}}$) will cause severe diagnostic collapse towards baseline class frequency. Controlled context changes ($I_{\text{context\_shift}}$) will disrupt classification despite an unaltered tumor interior.

---

## 2. Evaluation Metrics and Aggregation Design

### Primary Metric
- **Macro-Averaged F1 Score ($\text{Macro-F1}$):**
  $$\text{Macro-F1} = \frac{1}{C} \sum_{c=1}^{C} F1_c = \frac{1}{3} \left( F1_{\text{glioma}} + F1_{\text{meningioma}} + F1_{\text{pituitary}} \right)$$
  Macro-F1 assigns equal weight to all three diagnostic classes regardless of sample prevalence, penalizing classifiers that ignore minority classes (meningioma: 708 slices, pituitary: 930 slices vs glioma: 1,426 slices).

### Secondary Metrics
1. **Balanced Accuracy:** Average of per-class recall (sensitivity):
   $$\text{BalAcc} = \frac{1}{3} \sum_{c=1}^{3} \text{Recall}_c$$
2. **Per-Class Precision, Recall, and F1 Score:** Reported separately for glioma, meningioma, and pituitary.
3. **Multi-Class Confusion Matrix:** Absolute counts and normalized row-stochastic contingency tables.
4. **Log-Loss / Cross-Entropy Loss:** Probabilistic calibration metric evaluated on test folds.

### Unit of Evaluation and Aggregation
- **Primary Aggregation:** Pooled out-of-fold sample-level evaluation. In 5-fold cross-validation, every sample $s \in \{1, \dots, 3064\}$ is in exactly one held-out test fold. The model predictions across all 3,064 out-of-fold evaluations are pooled to compute global Macro-F1, Balanced Accuracy, and Confusion Matrices.
- **Cross-Fold Dispersion:** In addition, the fold-level metric mean and sample standard deviation across the 5 validation folds ($\mu_{\text{fold}} \pm \sigma_{\text{fold}}$) are reported to quantify cross-fold stability.

### Confidence Interval Methodology
- **Primary CI:** 95% Percentile Bootstrap Confidence Interval computed on pooled out-of-fold predictions with $B = 1,000$ bootstrap replicates, stratified by true class label.
- **Fold CI:** Studentized $t$-interval with $df = 4$ across the 5 fold scores:
  $$\text{CI}_{95\%} = \bar{x} \pm t_{0.975, 4} \cdot \frac{s}{\sqrt{5}} \approx \bar{x} \pm 2.776 \cdot \frac{s}{\sqrt{5}}$$

---

## 3. Intervention Battery and Experimental Contrasts

To isolate the spatial origin of model decisions, each model is evaluated on five matched image conditions for every test sample:

| Intervention Code | Visual Manipulation | Expected Effect if Intratumoral Reliance ($H_1$) | Expected Effect if Context Reliance ($H_0$) |
|---|---|---|---|
| **$I_{\text{orig}}$** | Original unaltered MRI slice | Baseline performance ($F1_{\text{orig}}$) | Baseline performance ($F1_{\text{orig}}$) |
| **$I_{\text{tumor}}$** | Background zeroed; tumor interior unchanged | Retains high performance ($F1_{\text{tumor}} \approx F1_{\text{orig}}$) | Performance collapses towards chance |
| **$I_{\text{removed}}$** | Tumor interior zeroed/infilled; surrounding context unchanged | Severe performance collapse ($F1_{\text{removed}} \ll F1_{\text{orig}}$) | Retains high performance ($F1_{\text{removed}} \approx F1_{\text{orig}}$) |
| **$I_{\text{placebo}}$** | Contralateral equal-area brain region zeroed; tumor untouched | Negligible change ($|\Delta_{\text{placebo}}| \approx 0$) | Variable or moderate drop |
| **$I_{\text{context\_shift}}$** | Context noise / contrast shift; tumor untouched | Robust ($|\Delta_{\text{shift}}| \approx 0$) | Severe degradation ($F1$ collapses) |

### Formal Planned Contrasts
1. **Intratumoral Evidentiary Impact Contrast ($\Delta_{\text{removal}}$):**
   $$\Delta_{\text{removal}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{removed}})$$
2. **Context Sufficiency Contrast ($\Delta_{\text{context}}$):**
   $$\Delta_{\text{context}} = \text{Macro-F1}(I_{\text{removed}}) - \text{Chance-F1} \quad (\text{Chance} \approx 0.333)$$
3. **Placebo Specificity Contrast ($\Delta_{\text{placebo}}$):**
   $$\Delta_{\text{placebo}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{placebo}})$$

---

## 4. Minimum Practically Meaningful Effect Size

> [!IMPORTANT]
> **DECISION REQUIRING EXPLICIT RESEARCHER APPROVAL — NOT FINALIZED**
>
> In accordance with scientific integrity guidelines, an effect size bound must NOT be arbitrarily fabricated. We delineate the evidence and options below; final numeric lock requires formal researcher sign-off before training begins.

### Candidate Effect Size Thresholds
- **Candidate Bound A ($\tau_{\Delta} = 0.10$ Macro-F1):** A performance drop $\ge 10\%$ points upon tumor removal is considered strong evidence of primary tumor reliance. Any drop $< 5\%$ points indicates predominant context reliance.
- **Candidate Bound B ($\tau_{\Delta} = 0.05$ Macro-F1):** A drop $\ge 5\%$ points upon tumor removal is considered evidence of nontrivial tumor reliance.
- **Evidence Gap:** Because no prior published study has measured the exact distribution of tumor-versus-context ablation deltas on this specific 3-class Cheng dataset under leakage-free patient grouping, empirical variance under ablation remains uncalibrated.
- **Requirement for Completion:** Condition C3/C6 is **NOT complete** until the supervising researcher reviews pilot literature or confirms one of the candidate bounds.

---

## 5. Multiple-Comparison and Error Control

When evaluating planned contrasts across 4 intervention conditions and 4 sensitivity scenarios:
- **Multiple Comparison Correction:** Benjamini-Hochberg procedure controlling the False Discovery Rate (FDR) at $q = 0.05$.
- **Family of Hypotheses:** The four primary contrasts ($\Delta_{\text{removal}}$, $\Delta_{\text{tumor}}$, $\Delta_{\text{placebo}}$, $\Delta_{\text{context\_shift}}$) evaluated under each sensitivity scenario.

---

## 6. Execution, Model Selection, and Checkpoint Rules

### Model Architecture and Preprocessing
- **Architectures:** ResNet-18 and ConvNeXt-Tiny (standard CNN benchmarks) or simple Vision Transformer.
- **Preprocessing:** Per-image min-max uint8 grayscale scaling, resized to $512 \times 512$ with bilinear interpolation.
- **Data Augmentation:** Standard rotation ($\pm 15^\circ$), horizontal flip ($p = 0.5$), subtle intensity jitter ($\pm 5\%$). No synthetic tumor pasting or artificial boundary alterations during training.

### Inner Validation Split (Strict Model Selection Separation)
- In each fold $k \in \{1, \dots, 5\}$, the training pool comprises the remaining 4 folds (80% of data).
- The training pool is partitioned into an inner train set (80% of pool) and an inner validation set (20% of pool) respecting the exact same combined evaluation groups.
- The outer test fold is **NEVER accessed** for training, early stopping, hyperparameter tuning, or threshold selection.

### Checkpoint and Hyperparameter Locking
- **Primary Seed:** 42 (reproducibility confirmation with seeds 43 and 44).
- **Optimization:** AdamW ($\beta_1 = 0.9, \beta_2 = 0.999$, weight decay $10^{-4}$), initial learning rate $10^{-4}$ with cosine annealing.
- **Checkpoint Selection:** The model checkpoint achieving the minimum inner validation cross-entropy loss is locked. Early stopping patience = 10 epochs.

---

## 7. Protocol C Sensitivity Analysis Family

To address uncertainty regarding the 236 candidate near-duplicate pairs, all hypotheses and contrasts will be evaluated across four pre-registered grouping scenarios:

1. **Scenario S0 (Baseline):** Authoritative patient-grouped 5-fold split (`prepared_full_run/patient_splits.csv`).
2. **Scenario S1 (Conservative $\tau = 0.80$):** Manifest `split_regrouped_ssim_0_80.csv` (4 patients regrouped).
3. **Scenario S2 (Conservative $\tau = 0.75$):** Manifest `split_regrouped_ssim_0_75.csv` (23 patients regrouped).
4. **Scenario S3 (Exploratory Confirmation $\tau = 0.70$):** Manifest `split_regrouped_ssim_0_70.csv` (36 patients regrouped).
5. **Scenario S3b ($\tau = 0.60$ Stress Test):** Manifest `split_regrouped_ssim_0_60.csv` reported with explicit documentation of the 807-slice giant component percolation artifact.

### Robustness Criterion
The scientific conclusion regarding tumor versus context reliance is declared **ROBUST** if and only if the direction and significance of the primary contrast $\Delta_{\text{removal}}$ are consistent across Scenarios S0, S1, and S2.

---

## 8. Invalidation Conditions and Reporting Policy

### Invalidation Conditions
An experiment or fold is immediately declared INVALID and aborted if:
1. Any training or inner-validation sample is present in the outer test fold (leakage violation).
2. Any class has 0 true test samples in a fold.
3. Training yields numerical instability (NaN / Inf loss).
4. Deterministic repeatability fails (re-running seed 42 yields divergent predictions).

### Policy for Null, Negative, and Inconclusive Findings
- If the 95% bootstrap confidence interval of $\Delta_{\text{removal}}$ encompasses 0, the study will explicitly conclude that the model shows no detectable reliance on intratumoral features.
- If results differ drastically across Scenarios S0, S1, and S2, the study will conclude that evaluation findings are contingent on dataset leakage assumptions, reporting this as a primary scientific finding rather than attempting post-hoc model tuning.
