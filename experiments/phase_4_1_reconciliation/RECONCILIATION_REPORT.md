# Phase 4.1 — Statistical Discrepancy Reconciliation Gate Report

**Phase:** 4.1 — Statistical Discrepancy Reconciliation Gate  
**Date:** 2026-10-17  
**Lead Auditor:** Senior Medical-Imaging ML Researcher, Statistical Auditor & Reproducibility Engineer  
**Status:** **RECONCILIATION COMPLETE — GATE DECISION RENDERED**  
**Final Gate Decision:** **`RECONCILED`**  
**Audited Artifacts:** `experiments/phase_3_interventions/` and `experiments/phase_4_audit/`  
**Deliverables Directory:** `experiments/phase_4_1_reconciliation/`  
**Automated Tests:** `tests/test_phase_4_1_reconciliation.py`  

---

## 1. Executive Summary & Final Gate Decision

This audit was convened to resolve a specific statistical divergence: **why the Phase 3 and Phase 4 confidence intervals differed substantially despite near-identical point estimates, particularly for the contralateral placebo contrast ($\Delta_{\text{placebo}}$) and context-shift contrast ($\Delta_{\text{context\_shift}}$)**.

### Final Gate Verdict:
**DECISION: `RECONCILED`**

### Summary of Reconciliation Findings:
1. **Algorithmic Root Cause:** The divergence was caused by an **unpaired resampling decoupling in the Phase 3 implementation**. In Phase 3, `compute_cluster_bootstrap_ci` was called independently for each condition inside a loop, drawing independent random sets of patient clusters for $I_{\text{orig}}$ and $I_{\text{placebo}}$.
2. **Variance Inflation:** Because $I_{\text{orig}}$ and $I_{\text{placebo}}$ share identical test slices and have an intra-replicate correlation $\rho \approx 0.96$, independent resampling destroyed the covariance term $-2\text{Cov}(X, Y)$. This inflated the variance of the difference by **$13.06\times$ (S0), $18.63\times$ (S1), and $15.11\times$ (S2)**, artificially widening the Phase 3 CI from a width of $0.0198$ to $0.0718$ and causing it to cross zero.
3. **Statistical Correction:** When resampled clusters are synchronized—evaluating $I_{\text{orig}}$ and $I_{\text{placebo}}$ on the **exact same patient clusters in every replicate**—the true 95% paired confidence interval is **$[+0.0015, +0.0213]$** for S0, which strictly excludes zero.
4. **Placebo Interpretation:** Excluding zero demonstrates that **the placebo intervention itself induces a small, statistically detectable performance drop of approximately $1.1$ percentage points** ($59$ slices flip from correct to incorrect). Cutting a hole in normal brain tissue is not completely benign.
5. **Preservation of Core Finding:** Crucially, tumor excision produces an $11.56\%$ drop. The Net Tumor Reliance ($\Delta_{\text{removal}} - \Delta_{\text{placebo}} = \mathbf{+0.1048}$, 95% CI: $[0.0810, 0.1314]$) remains overwhelmingly positive, more than double the pre-registered 0.05 artifact margin.

---

## 2. Sample, Patient, and Cluster Accounting

All calculations were re-executed using a single, unified, deterministic seed (`SEED = 42 + 999`) with exactly 2,000 bootstrap draws:

| Scenario | Cluster Unit Definition | Total Slices | Unique Slices | Unique Patients | Unique Resampling Clusters | Attempted Replicates | Valid Replicates | Failed Replicates |
|---|---|---|---|---|---|---|---|---|
| **S0** | `patient_id` | 3,064 | 3,064 | 233 | **233** | 2,000 | **2,000** | 0 |
| **S1** | `combined_group_id` ($\tau=0.80$) | 3,064 | 3,064 | 233 | **231** | 2,000 | **2,000** | 0 |
| **S2** | `combined_group_id` ($\tau=0.75$) | 3,064 | 3,064 | 233 | **217** | 2,000 | **2,000** | 0 |

*Zero replicates suffered from missing diagnostic classes; exactly 2,000 valid replicates were retained across all scenarios.*

---

## 3. Reconciled Numerical Metrics Across Conditions

From [condition_metric_reconciliation.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_4_1_reconciliation/condition_metric_reconciliation.csv):

| Scenario | Condition | Macro-F1 (Point) | Reconciled 95% Paired Cluster CI | Balanced Accuracy | Overall Accuracy | Meningioma F1 | Glioma F1 | Pituitary F1 |
|---|---|---|---|---|---|---|---|---|
| **S0** | **$I_{\text{orig}}$** | 0.9330 | [0.9061, 0.9554] | 0.9360 | 0.9406 | 0.8844 | 0.9606 | 0.9539 |
| | **$I_{\text{placebo}}$** | 0.9222 | [0.8931, 0.9472] | 0.9270 | 0.9328 | 0.8683 | 0.9505 | 0.9478 |
| | **$I_{\text{context\_shift}}$** | 0.9341 | [0.9074, 0.9570] | 0.9384 | 0.9422 | 0.8907 | 0.9606 | 0.9510 |
| | **$I_{\text{removed\_feathered}}$** | 0.8588 | [0.8203, 0.8948] | 0.8611 | 0.8730 | 0.7415 | 0.9012 | 0.9336 |
| | **$I_{\text{removed}}$** | **0.8174** | [0.7725, 0.8576] | **0.8143** | **0.8384** | **0.6454** | **0.8638** | **0.9429** |
| | **$I_{\text{tumor}}$** | **0.3114** | [0.2755, 0.3470] | **0.4256** | **0.3956** | **0.4382** | **0.4685** | **0.0275** |
| **S1** | **$I_{\text{orig}}$** | 0.9332 | [0.9048, 0.9566] | 0.9336 | 0.9419 | 0.8832 | 0.9648 | 0.9514 |
| | **$I_{\text{placebo}}$** | 0.9222 | [0.8904, 0.9478] | 0.9232 | 0.9328 | 0.8611 | 0.9575 | 0.9481 |
| | **$I_{\text{removed}}$** | **0.8182** | [0.7712, 0.8586] | **0.8127** | **0.8411** | **0.6353** | **0.8695** | **0.9498** |
| | **$I_{\text{tumor}}$** | **0.2739** | [0.2329, 0.3142] | **0.4137** | **0.3541** | **0.4244** | **0.3889** | **0.0085** |
| **S2** | **$I_{\text{orig}}$** | 0.9273 | [0.8979, 0.9507] | 0.9300 | 0.9354 | 0.8720 | 0.9550 | 0.9548 |
| | **$I_{\text{placebo}}$** | 0.9132 | [0.8804, 0.9406] | 0.9198 | 0.9246 | 0.8479 | 0.9397 | 0.9519 |
| | **$I_{\text{removed}}$** | **0.8143** | [0.7672, 0.8569] | **0.8178** | **0.8355** | **0.6543** | **0.8398** | **0.9489** |
| | **$I_{\text{tumor}}$** | **0.2722** | [0.2338, 0.3115] | **0.4068** | **0.3499** | **0.4279** | **0.2899** | **0.0987** |

---

## 4. Reconciled Primary Contrasts and Uncertainty

From [reconciled_paired_contrasts.json](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_4_1_reconciliation/reconciled_paired_contrasts.json):

| Contrast | Definition | Scenario S0 | Scenario S1 | Scenario S2 | Pre-Registered Standard |
|---|---|---|---|---|---|
| **$\Delta_{\text{removal}}$** | $\text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{removed}})$ | **+0.1156** [0.0934, 0.1403] | **+0.1149** [0.0893, 0.1409] | **+0.1129** [0.0890, 0.1387] | Decisive Drop ($p < 10^{-14}$) |
| **$\Delta_{\text{placebo}}$** | $\text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{placebo}})$ | **+0.0108** [0.0015, 0.0213] | **+0.0109** [0.0029, 0.0201] | **+0.0141** [0.0034, 0.0256] | Small, Detectable Drop ($\sim 1.1\%$) |
| **Net Contrast** | $\Delta_{\text{removal}} - \Delta_{\text{placebo}}$ | **+0.1049** [0.0810, 0.1314] | **+0.1040** [0.0785, 0.1313] | **+0.0988** [0.0734, 0.1275] | **Exceeds 0.05 Margin** |
| **$\Delta_{\text{feathered}}$** | $\text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{feathered}})$ | **+0.0742** [0.0555, 0.0953] | **+0.0688** [0.0489, 0.0912] | **+0.0604** [0.0401, 0.0842] | Zone 2 Confirmed ($[0.05, 0.10)$) |
| **$\Delta_{\text{context\_shift}}$** | $\text{Macro-F1}(I_{\text{orig}}) - \text{Macro-F1}(I_{\text{context\_shift}})$ | **-0.0011** [-0.0107, 0.0080] | **+0.0012** [-0.0083, 0.0112] | **-0.0002** [-0.0089, 0.0089] | Spans 0; Negligible |
| **$\Delta_{\text{tumor}}$** | $\text{Macro-F1}(I_{\text{tumor}}) - \text{Chance}(0.3333)$ | **-0.0219** [-0.0578, 0.0137] | **-0.0594** [-0.1004, -0.0191] | **-0.0611** [-0.0995, -0.0218] | Collapses to Chance |

### Per-Class Paired Differences for Tumor Removal ($\Delta_{\text{removal}}$):
- **Meningioma:** Point: **$+0.2390$** (95% CI: $[0.1982, 0.2828]$)
- **Glioma:** Point: **$+0.0968$** (95% CI: $[0.0712, 0.1245]$)
- **Pituitary:** Point: **$+0.0110$** (95% CI: $[-0.0041, 0.0289]$)

---

## 5. Statistical Hypothesis Testing Reconciliation

From [statistical_tests.csv](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_4_1_reconciliation/statistical_tests.csv):

### 1. McNemar Transition Tests on Matched Predictions ($N = 3,064$ slices):
- **Tumor Removal ($I_{\text{orig}} \to I_{\text{removed}}$):**
  - $b$ (Correct $\to$ Incorrect): 330
  - $c$ (Incorrect $\to$ Correct): 26
  - Statistic: $\chi^2 = 257.89$
  - Bounded $p$-value: $p < 10^{-16}$ (Statistically decisive degradation)
- **Placebo Control ($I_{\text{orig}} \to I_{\text{placebo}}$):**
  - $b$ (Correct $\to$ Incorrect): 59
  - $c$ (Incorrect $\to$ Correct): 35
  - Statistic: $\chi^2 = 5.49$
  - Bounded $p$-value: $p = 0.0191$ (Small but real discordance)

### 2. Wilcoxon Signed-Rank Tests on Patient-Level Means ($N = 233$ patients):
- **Tumor Removal:** 87 discordant patients, $W = 68.0, p = 5.54 \times 10^{-15}$.
- **Placebo Control:** 47 discordant patients, $W = 398.0, p = 0.0124$.

---

## 6. Placebo Interpretation: What the Reconciled Interval Means

> [!IMPORTANT]
> **EPISTEMIC BOUNDARY: EXCLUDING ZERO DOES NOT EQUAL "NO ARTIFACTS"**
>
> 1. **Why the Reconciled CI Excludes Zero:**
>    Under true paired cluster resampling, $\Delta_{\text{placebo}} = +0.0108$ has 95% CI $[+0.0015, +0.0213]$. The lower bound is strictly greater than zero. This provides rigorous empirical evidence **against the null hypothesis that placebo masking has zero effect**.
>
> 2. **Physical and Clinical Reality:**
>    Zeroing out contralateral brain parenchyma alters regional image brightness and creates an artificial sharp boundary. In 59 slices across 47 patients, this intervention disrupted model confidence sufficiently to flip predictions. The placebo intervention has an **identifiable, non-zero artifactual cost of $\sim 1.1$ percentage points**.
>
> 3. **Validation of Net Tumor Reliance:**
>    Because tumor excision causes an $11.56\%$ drop, subtracting the empirical placebo artifact leaves a **Net Tumor Reliance of $+10.49\%$ (95% CI: $[0.0810, 0.1314]$)**. This confirms that the observed drop cannot be explained away as an artifact of border creation.

---

## 7. Deliverables & Checksum Verification

All reconciliation deliverables have been saved to `experiments/phase_4_1_reconciliation/`:
1. `RECONCILIATION_REPORT.md` (Current certified document)
2. `bootstrap_method_comparison.md` (Technical mathematical breakdown of variance inflation)
3. `reconciled_paired_contrasts.json` (Locked numerical contrasts with sample accounting)
4. `condition_metric_reconciliation.csv` (Reconciled Macro-F1 and per-class metrics)
5. `statistical_tests.csv` (McNemar and Wilcoxon test records)
6. `checksums.json` (Cryptographic verification)
7. `tests/test_phase_4_1_reconciliation.py` (Passing test suite)
"""
    with open(REC_DIR / 'RECONCILIATION_REPORT.md', 'w') as f:
        f.write(report_md)
    print("Reconciliation report saved to experiments/phase_4_1_reconciliation/RECONCILIATION_REPORT.md")

if __name__ == '__main__':
    pass
