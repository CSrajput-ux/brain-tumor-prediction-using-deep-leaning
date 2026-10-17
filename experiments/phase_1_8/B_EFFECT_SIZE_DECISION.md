# B — Effect-Size Decision and Interpretive Framework

**Phase:** 1.8 — Final Protocol Ratification  
**Date:** 2026-10-17  
**Status:** Dual-Threshold Interpretive Framework Established; Final Threshold Policy Formally Locked  

---

## 1. Context and Problem Statement

When evaluating whether brain-tumor MRI classifiers rely on intratumoral evidence versus surrounding context, we measure the performance ablation contrast:
$$\Delta_{\text{removal}} = \text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{removed}})$$
A fundamental principle of open science and pre-registration is establishing **what constitutes a practically meaningful effect size** before inspecting model outputs.

Two candidate thresholds have been proposed in earlier phases:
- **Threshold $\tau_1 = 0.05$ (5.0 percentage points Macro-F1)**
- **Threshold $\tau_2 = 0.10$ (10.0 percentage points Macro-F1)**

---

## 2. Assessment of Proposed Thresholds

### Threshold 1: $\Delta = 0.05$ (5.0% Macro-F1 Drop)
- **Mathematical Meaning:** Across the 3,064 out-of-fold test samples (~613 test samples per fold), a 0.05 drop in Macro-F1 corresponds to approximately 30 to 45 test slices flipping from correct to incorrect diagnoses (or a ~5% drop in harmonic mean precision/recall across classes).
- **Clinical/Diagnostic Meaning:** In medical imaging, a diagnostic classifier that loses 5 percentage points in Macro-F1 when the tumor is completely masked out is demonstrably utilizing the tumor region. However, if the classifier *retains* 95% of its original performance despite having the entire tumor excised, it reveals that the surrounding context provides sufficient shortcut signals to make accurate predictions in the vast majority of cases.
- **Scientific Limitation:** A 5% drop is sensitive, but on high-dimensional noisy MRI datasets, subtle boundary shifts or distribution degradation caused by masking edges can occasionally produce 2–4% drops even when context dominates.

### Threshold 2: $\Delta = 0.10$ (10.0% Macro-F1 Drop)
- **Mathematical Meaning:** Corresponds to approximately 60 to 90 test slices flipping diagnoses, representing a major diagnostic disruption across multiple folds.
- **Clinical/Diagnostic Meaning:** A 10 percentage point drop provides unambiguous evidence that intratumoral features are primary drivers of classification decisions. Under this conservative standard, small masking artifacts or minor texture perturbations cannot mistakenly trigger a finding of tumor reliance.
- **Scientific Limitation:** If a genuine clinical model relies on both tumor pathology (e.g. contrast enhancement) and contextual cues (e.g. anatomical location/edema), setting the threshold strictly at 0.10 might classify a real 7% tumor reliance as "context-driven."

---

## 3. Pre-Registered 3-Zone Interpretive Framework

Rather than arbitrarily forcing a single binary cutoff without empirical test-set data, we adopt a **rigorous three-zone inferential framework** pre-registered prior to training:

```
                  Delta = Macro-F1(I_orig) - Macro-F1(I_removed)
       0.00                               0.05                               0.10
<-------|-----------------------------------|----------------------------------|-------->
     Zone 1: Predominant Context         Zone 2: Dual / Shared             Zone 3: Primary Intratumoral
     Shortcut Reliance                   Reliance                          Reliance
     (Tumor is largely dispensable)      (Both tumor and context           (Tumor region is essential;
                                         provide distinct signal)          performance collapses without it)
```

### Zone Definitions and Scientific Interpretations:
1. **Zone 1: Predominant Context Reliance ($\Delta_{\text{removal}} < 0.05$):**
   - *Inference:* Masking the tumor interior causes less than a 5% drop in Macro-F1. The classifier achieves nearly its full diagnostic capability using surrounding brain tissue, cranial geometry, slice position, or acquisition shortcuts alone.
   - *Scientific Conclusion:* The model relies predominantly on non-tumoral context. Intratumoral evidence is not the primary diagnostic driver.
2. **Zone 2: Dual / Shared Reliance ($0.05 \le \Delta_{\text{removal}} < 0.10$):**
   - *Inference:* The tumor region provides non-trivial diagnostic evidence, but surrounding context also retains strong autonomous discriminability ($\text{Macro-F1}(I_{\text{removed}}) \gg \text{Chance}$).
   - *Scientific Conclusion:* The model utilizes both intratumoral and contextual features. Context serves as a co-primary diagnostic pathway.
3. **Zone 3: Primary Intratumoral Reliance ($\Delta_{\text{removal}} \ge 0.10$):**
   - *Inference:* Excising the tumor produces a massive drop ($\ge 10\%$) in Macro-F1, accompanied by high performance on the tumor-only condition ($\text{Macro-F1}(I_{\text{tumor}}) \approx \text{Macro-F1}(I_{\text{orig}})$) and negligible drop on the placebo control ($|\Delta_{\text{placebo}}| < 0.02$).
   - *Scientific Conclusion:* The model relies primarily on intratumoral evidence.

---

## 4. Formal Ratification and Integrity Safeguards

1. **No Post-Hoc Selection:** This 3-zone framework is locked before baseline training. Threshold boundaries (0.05 and 0.10) will **not be modified, tuned, or shifted** based on observed test-set performance.
2. **Cluster-Bootstrap Uncertainty:** The observed $\Delta_{\text{removal}}$ will be reported with its 95% Patient-Cluster Bootstrap Confidence Interval ($B = 1,000$). If the confidence interval spans across zones, the result will be formally reported as *inconclusive between adjacent reliance regimes*.
3. **No False Certainty:** Neither 0.05 nor 0.10 is claimed as an intrinsic biological constant; rather, they serve as pre-registered operational standards that prevent confirmation bias.
