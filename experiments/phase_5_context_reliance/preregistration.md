# Phase 5 Pre-Registration Protocol: Targeted Context Reliance and Spatial Intervention Study

**Phase:** 5 — Targeted Context Reliance and Spatial Intervention Study  
**Date Locked:** 2026-10-17  
**Status:** **FROZEN AND RATIFIED PRIOR TO INTERVENTION EXECUTION**  
**Lead Evaluator:** Senior Medical-Imaging ML Researcher, Causal-Inference Methodologist & Reproducibility Engineer  
**Reference Baselines:** Reconciled Phase 4.1 Outcomes (`RECONCILED`, 115 passing tests)  
**Evaluated Models:** Strictly frozen ResNet-50 checkpoints from Phase 2 across Scenarios S0, S1, and S2 (15 checkpoints total). No retraining, fine-tuning, or hyperparameter adjustment.

---

## 1. Scientific Objective and Core Hypotheses

### Objective:
Following the Phase 4.1 reconciliation—which demonstrated that the frozen classifier retains 81.7% Macro-F1 upon tumor excision ($\Delta_{\text{removal}} = 0.1156$) with an empirical placebo artifact of $\sim 1.1\%$ ($\Delta_{\text{placebo}} = 0.0108$)—Phase 5 investigates **which specific image-space context compartments contribute to the model's predictions**.

### Core Hypotheses:
1. **$H_{\text{perilesional}}$ (Immediate Perilesional Margin Hypothesis):**
   The residual diagnostic performance of the classifier is driven by immediate perilesional parenchymal features (e.g. peritumoral vasogenic edema, dural tail contact, infiltrative boundary texture) situated in the immediate vicinity of the lesion mask.
   - *Prediction:* Suppressing an image-space peritumoral ring ($I_{\text{margin}}$) causes a significant performance drop that substantially exceeds a matched contralateral ring control ($I_{\text{margin\_placebo}}$).
2. **$H_{\text{distant}}$ (Global Cranial / Remote Anatomical Shortcut Hypothesis):**
   The residual diagnostic performance is driven by global cranial geometry, skull-base landmarks, and ventricle position distant from the lesion.
   - *Prediction:* Suppressing or perturbing distant cranial context while keeping the tumor and its immediate margin completely intact impairs classification, particularly for skull-base neoplasms (Pituitary).
3. **$H_{\text{null\_margin}}$ (Margin Invariance / Boundary Artifact Hypothesis):**
   Perilesional margin suppression causes no degradation beyond the generic artifact induced by ring-shaped occlusion ($|\Delta_{\text{margin}} - \Delta_{\text{margin\_placebo}}| < 0.02$).

---

## 2. Spatial Information Audit & Epistemic Labelling

> [!WARNING]
> **EPISTEMIC LABELING: APPROXIMATE IMAGE-SPACE REGIONS VS ANATOMICAL GROUND TRUTH**
>
> The authoritative Cheng dataset provides ONLY:
> 1. Whole-slice 2D MRI images ($512 \times 512$ uint8, contrast-enhanced T1-weighted).
> 2. Manual binary tumor boundary contours (`cjdata.tumorMask`).
>
> **The dataset contains ZERO certified anatomical annotations for brain ventricles, skull base, sulcal CSF, gray matter, white matter, or vasogenic edema.**
>
> Therefore, all derived regions in Phase 5 are formally designated as **Approximate Image-Space Morphological Compartments**, NOT verified anatomical compartments.

---

## 3. Targeted 6-Condition Matched Intervention Battery

Every test slice is evaluated under 6 matched conditions (+ 1 feathered sensitivity condition):

| Condition ID | Name | Mathematical Definition | Purpose |
|---|---|---|---|
| **$C_0$** | **$I_{\text{orig}}$** | Unmanipulated original MRI slice ($512 \times 512$) | Benchmark reference performance |
| **$C_1$** | **$I_{\text{tumor\_removed}}$** | $\text{img} \times (1 - M_{\text{tumor}})$ | Reconciled primary lesion ablation baseline |
| **$C_2$** | **$I_{\text{placebo\_focal}}$** | $\text{img} \times (1 - M_{\text{placebo}})$ (contralateral equal-area mask) | Focal boundary/intensity artifact control |
| **$C_3$** | **$I_{\text{margin\_removed}}$** | $\text{img} \times (1 - M_{\text{margin}})$, where $M_{\text{margin}} = \text{dilate}(M_{\text{tumor}}, r=15) \setminus M_{\text{tumor}}$ | Tests immediate perilesional margin dependency (tumor intact) |
| **$C_4$** | **$I_{\text{margin\_placebo}}$** | $\text{img} \times (1 - M_{\text{plac\_margin}})$, where $M_{\text{plac\_margin}} = \text{dilate}(M_{\text{placebo}}, r=15) \setminus M_{\text{placebo}}$ | Matched control for ring-shaped occlusion artifact |
| **$C_5$** | **$I_{\text{distant\_perturbed}}$** | Tumor and margin ($M_{\text{tumor}} \cup M_{\text{margin}}$) intact; all pixels outside dimmed by 50% contrast scaling | Tests reliance on remote cranial geometry |
| **$C_6$** | **$I_{\text{margin\_feathered}}$** | $M_{\text{margin}}$ ablated with 5-pixel Gaussian border feathering and mean parenchymal infilling | Artifact sensitivity check for boundary steps |

### Geometric Parameter Specifications:
- **Dilation Radius ($r = 15$ pixels):**
  - In a $512 \times 512$ brain MRI covering a $\sim 220 \times 220\text{ mm}$ field of view, 1 pixel $\approx 0.43\text{ mm}$.
  - A 15-pixel morphological dilation represents a physical radius of **$\sim 6.5\text{ mm}$** around the tumor boundary, corresponding to the typical radiologic zone of peritumoral edema, glial reaction, and adjacent dural tail.
- **Contralateral Placebo Margin Matching:**
  - The placebo margin is created by applying the identical 15-pixel morphological dilation to the verified contralateral placebo mask.
  - Guarantees matched ring geometry, matched area, and strict zero overlap with the ground-truth tumor.

---

## 4. Evaluation Protocol and Synchronized Paired Bootstrap

1. **Checkpoints:** The 15 frozen outer-fold checkpoints from Phase 2 are used exclusively.
2. **Synchronized Paired Cluster Resampling:**
   - In accordance with Phase 4.1 findings, bootstrap resampling **MUST be synchronized across conditions**: for replicate $b$, exactly one random cluster draw is sampled and evaluated across all matched conditions simultaneously.
   - Number of replicates: $B = 2,000$.
   - Cluster units: `patient_id` for S0 (233 clusters); `combined_group_id` for S1 (231 clusters) and S2 (217 clusters).
3. **Primary Metric:** Pooled Macro-Averaged F1 score ($\text{Macro-F1}$).
4. **Planned Primary Contrasts:**
   - **Perilesional Margin Effect:** $\Delta_{\text{margin}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{margin\_removed}})$
   - **Placebo Margin Effect:** $\Delta_{\text{margin\_placebo}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{margin\_placebo}})$
   - **Net Perilesional Margin Reliance:** $\text{Net}_{\text{margin}} = \Delta_{\text{margin}} - \Delta_{\text{margin\_placebo}}$ (computed on identical bootstrap draws)
   - **Distant Context Sensitivity:** $\Delta_{\text{distant}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{distant\_perturbed}})$
5. **Multiple Testing Correction:**
   - Primary hypothesis family: 4 planned contrasts across primary scenarios S0, S1, S2 (12 statistical comparisons).
   - Benjamini-Hochberg procedure controlling FDR at $q = 0.05$.
   - Holm-Bonferroni FWER control at $\alpha = 0.05$.
6. **Decision Standard for Margin Reliance:**
   - Pre-registered threshold: $\text{Net}_{\text{margin}} \ge 0.03$ with paired 95% CI lower bound $> 0.00$.

---

## 5. Mandatory Epistemic Safeguards

1. No claim of cellular biological discovery or clinical diagnostic readiness.
2. No post-hoc alteration of dilation radius $r = 15$ or contrast scaling factor $0.50$ after viewing model outputs.
3. If an intervention produces an unexpected outcome, it will be reported transparently as-is without protocol dredging.
