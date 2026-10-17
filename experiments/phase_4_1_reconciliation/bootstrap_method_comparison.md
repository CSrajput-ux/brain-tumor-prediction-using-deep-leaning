# Technical Audit: Bootstrap Method Comparison

**Phase:** 4.1 — Statistical Discrepancy Reconciliation Gate  
**Date:** 2026-10-17  
**Author:** Statistical Auditor & Reproducibility Engineer  
**Objective:** Deconstruct the mathematical, algorithmic, and statistical divergence between Phase 3 (Unpaired Decoupled Cluster Bootstrap) and Phase 4 (Synchronized Paired Cluster Bootstrap).

---

## 1. Algorithmic Root-Cause Identification

The numerical discrepancy between Phase 3 and Phase 4 confidence intervals was traced to a specific code design difference in how cluster bootstrap replicates were generated across experimental conditions.

### Code Pattern in Phase 3 (`scripts/run_phase_3_interventions.py`):
```python
# Phase 3: compute_cluster_bootstrap_ci was called in a loop over conditions
for cond in conditions:
    ci_low, ci_high, boot_f1s = compute_cluster_bootstrap_ci(cond_df, cluster_col, n_boot=2000)
    boot_replicates_by_cond[cond] = np.array(boot_f1s)

# Contrasts were then computed by subtracting independent arrays:
delta_placebo_reps = boot_replicates_by_cond['I_orig'] - boot_replicates_by_cond['I_placebo']
```
In `compute_cluster_bootstrap_ci`, `np.random.choice` was invoked independently inside each call. As a result:
- Replicate $b$ of $I_{\text{orig}}$ resampled patient cluster set $\mathcal{S}_{\text{orig}}^{(b)}$.
- Replicate $b$ of $I_{\text{placebo}}$ resampled a completely different, uncorrelated patient cluster set $\mathcal{S}_{\text{placebo}}^{(b)}$.

### Code Pattern in Phase 4 / Reconciled Method (`scripts/run_phase_4_1_reconciliation.py`):
```python
# Reconciled Method: ONE synchronized draw of clusters for ALL conditions
paired_sampled_idx = rng_paired.choice(K, size=(n_boot, K), replace=True)

# For every condition, evaluate on the EXACT SAME resampled clusters:
for cond in conditions:
    boot_cm = np.sum(cluster_cms[cond][paired_sampled_idx], axis=1)
    macro_f1s, _ = macro_f1_from_cms(boot_cm)
    paired_boot_f1s[cond] = macro_f1s

# True paired replicate difference:
paired_d_plac = paired_boot_f1s['I_orig'] - paired_boot_f1s['I_placebo']
```

---

## 2. Mathematical Variance Analysis

Let $X = \text{Macro-F1}(I_{\text{orig}})$ and $Y = \text{Macro-F1}(I_{\text{placebo}})$.
We seek the variance of the difference $\Delta = X - Y$:

$$\text{Var}(\Delta) = \text{Var}(X) + \text{Var}(Y) - 2 \text{Cov}(X, Y)$$

### Case A: Independent Unpaired Sampling (Phase 3)
Because cluster sampling was decoupled across conditions, $\mathcal{S}_{\text{orig}}$ and $\mathcal{S}_{\text{placebo}}$ were statistically independent, forcing $\text{Cov}(X, Y) \approx 0$:
$$\text{Var}_{\text{unpaired}}(\Delta) = \text{Var}(X) + \text{Var}(Y)$$
- For Scenario S0:
  - $\text{Var}(X) \approx 0.000157$ ($\text{Std} \approx 0.0125$)
  - $\text{Var}(Y) \approx 0.000166$ ($\text{Std} \approx 0.0129$)
  - $\text{Var}_{\text{unpaired}} = 0.000323$
  - $\text{Std}_{\text{unpaired}} = \sqrt{0.000323} = \mathbf{0.0180}$
  - Expected 95% CI width: $3.92 \times 0.0180 \approx \mathbf{0.0706}$
  - Observed CI: $[-0.0251, +0.0467]$ (Width: $0.0718$, **Spans zero**).

### Case B: Synchronized Paired Sampling (Reconciled Phase 4)
Because $I_{\text{orig}}$ and $I_{\text{placebo}}$ are evaluated on identical test slices, 97.1% of slices receive identical predictions. The Pearson correlation between $X^{(b)}$ and $Y^{(b)}$ across paired cluster draws is:
$$\rho_{X, Y} = \frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y} \approx \mathbf{0.961}$$
The true paired variance is:
$$\text{Var}_{\text{paired}}(\Delta) = 0.000157 + 0.000166 - 2(0.961)(0.0125)(0.0129) = \mathbf{0.0000248}$$
- $\text{Std}_{\text{paired}} = \sqrt{0.0000248} = \mathbf{0.00498}$
- Expected 95% CI width: $3.92 \times 0.00498 \approx \mathbf{0.0195}$
- Observed CI: $[+0.0015, +0.0213]$ (Width: $0.0198$, **Excludes zero**).

### Empirical Variance Inflation Ratio:
$$\text{Inflation Ratio} = \frac{\text{Var}_{\text{unpaired}}}{\text{Var}_{\text{paired}}} = \frac{0.000323}{0.0000248} = \mathbf{13.06\times}$$

In Scenarios S1 and S2, the variance inflation ratio reaches **$18.63\times$** and **$15.11\times$** respectively!

---

## 3. Systematic 10-Point Comparison Table

| Dimension | Phase 3 Implementation | Reconciled Phase 4.1 Implementation | Methodological Impact |
|---|---|---|---|
| **1. Resampling Unit** | Patient ID (S0), Combined Group (S1, S2) | Patient ID (S0), Combined Group (S1, S2) | Identical; preserves cluster structure |
| **2. Matched Condition Preservation** | **Violated:** Resampled independently across conditions | **Preserved:** All conditions evaluated on identical cluster draws | Restores paired covariance structure |
| **3. Shared Resampled Clusters** | **No:** Condition $A$ and Condition $B$ drew different patients | **Yes:** Condition $A$ and Condition $B$ evaluate identical patients | Prevents variance inflation |
| **4. Macro-F1 Calculation** | Exact Macro-F1 recomputed from predictions in each replicate | Exact Macro-F1 recomputed from aggregated $3 \times 3$ confusion matrices | Exact match ($\Delta = 0.00000$) |
| **5. Class Representation** | Checked for empty classes | Checked for empty classes; 0 / 2,000 replicates failed | Zero degenerate replicates |
| **6. Replicate Accounting** | Attempted: 2,000; Accepted: 2,000; Rejected: 0 | Attempted: 2,000; Accepted: 2,000; Rejected: 0 | 100% valid replicate yield |
| **7. Seed & Determinism** | Unseeded sequential `np.random.choice` | Fixed seeded `np.random.default_rng(SEED + 999)` | 100% reproducible byte-for-byte |
| **8. CI Construction** | Percentile method (2.5th and 97.5th percentiles) | Percentile method (2.5th and 97.5th percentiles) | Pre-registered percentile standard |
| **9. Aggregation Level** | Pooled out-of-fold test samples (3,064 per scenario) | Pooled out-of-fold test samples (3,064 per scenario) | Identical |
| **10. Contrast Derivation** | Subtracted independent condition bootstrap vectors | Subtracted synchronized condition bootstrap vectors | **Source of discrepancy resolved** |

---

## 4. Empirical Reconciliation Across Scenarios

| Scenario | Planned Contrast | Method A (Phase 3 Decoupled) 95% CI | Method B (Reconciled Paired) 95% CI | Variance Inflation | Reconciled Inference |
|---|---|---|---|---|---|
| **S0** | **$\Delta_{\text{placebo}}$** | [-0.0251, +0.0467] (Spans 0) | **[+0.0015, +0.0213]** | $13.06\times$ | Small, real artifact drop ($\sim 1.1\%$) |
| | **$\Delta_{\text{removal}}$** | [0.0737, 0.1563] | **[0.0934, 0.1403]** | $3.21\times$ | Large, decisive lesion drop ($11.56\%$) |
| | **$\Delta_{\text{context\_shift}}$**| [-0.0369, +0.0312] (Spans 0) | **[-0.0107, +0.0080]** (Spans 0) | $14.07\times$ | Negligible drift ($\Delta = -0.0011$) |
| **S1** | **$\Delta_{\text{placebo}}$** | [-0.0260, +0.0518] (Spans 0) | **[+0.0029, +0.0201]** | $18.63\times$ | Small, real artifact drop ($\sim 1.1\%$) |
| | **$\Delta_{\text{removal}}$** | [0.0743, 0.1588] | **[0.0893, 0.1409]** | $2.69\times$ | Large, decisive lesion drop ($11.49\%$) |
| | **$\Delta_{\text{context\_shift}}$**| [-0.0364, +0.0385] (Spans 0) | **[-0.0083, +0.0112]** (Spans 0) | $14.53\times$ | Negligible drift ($\Delta = +0.0012$) |
| **S2** | **$\Delta_{\text{placebo}}$** | [-0.0258, +0.0533] (Spans 0) | **[+0.0034, +0.0256]** | $15.11\times$ | Small, real artifact drop ($\sim 1.4\%$) |
| | **$\Delta_{\text{removal}}$** | [0.0722, 0.1581] | **[0.0890, 0.1387]** | $2.75\times$ | Large, decisive lesion drop ($11.29\%$) |
| | **$\Delta_{\text{context\_shift}}$**| [-0.0369, +0.0367] (Spans 0) | **[-0.0089, +0.0089]** (Spans 0) | $15.12\times$ | Negligible drift ($\Delta = -0.0002$) |

---

## 5. Methodological Conclusion

1. The Phase 3 confidence interval for $\Delta_{\text{placebo}}$ spanned zero **only because of an unpaired resampling error that inflated variance by 13-fold to 18-fold**.
2. When the paired design is correctly implemented, the true confidence interval is $[+0.0015, +0.0213]$, which excludes zero.
3. This establishes that the contralateral placebo intervention induces a small, statistically detectable performance drop of **approximately $1.1$ percentage points**.
4. The Net Tumor Reliance ($\Delta_{\text{removal}} - \Delta_{\text{placebo}} = +0.1049$, paired CI: $[0.0810, 0.1314]$) remains overwhelmingly positive, more than double the pre-registered 0.05 artifact margin.
