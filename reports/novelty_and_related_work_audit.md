# Novelty, Overlap, and Related Work Audit

**Date:** 2026-10-29  
**Audit Purpose:** Verify scholarly novelty claims and delineate boundaries between prior literature and our study.

---

## 1. Prior Art Comparison

| Prior Study | Method / Scope | Key Limitation Addressed in Current Study |
|:---|:---|:---|
| **Wallis & Buvat (2022)** | Masked out entire brain tissue compartment to show model classifies on background/skull. | Coarse binary occlusion (all tissue vs none). Did not resolve intra-lesion core vs peritumoral transitional margin vs remote normal parenchyma. |
| **Cheng et al. (2015)** | Evaluated tumour region augmentation and slice-level partitioning. | Did not isolate patient-level leakage; did not perform counterfactual interventions. |
| **Rossi et al. (2024, TACE)** | Counterfactual tumour insertion and removal. | Focused on generative synthesis without matched contralateral sham controls; did not systematically isolate annular peritumoral dilation rings. |
| **Sourget et al. (2025)** | Evaluated feature removal for model faithfulness. | Evaluated CNNs only; did not investigate Vision Transformer global attention inductive biases or multi-plane radiological invariance. |
| **Fateh et al. (2026, BRISC)** | Introduced 6,000-slice multi-plane benchmark. | Benchmark was not audited for duplicate contamination. 101 test duplicates (10.1%) remained undetected, inflating benchmark evaluations. |
| **Yagis et al. (2021)** | Audited patient leakage in random slice splitting. | Addressed cross-validation splitting but did not perform regional counterfactual audits. |

---

## 2. Specific, Verified Scientific Contributions

We avoid hyperbolic or unsubstantiated "first-ever" claims and define four precise, testable contributions:

1. **Sham-Controlled 5-Region Counterfactual Framework:** We formulate a topological decomposition separating tumour core ($R_{\text{core}}$), 4-pixel immediate margin ($R_{\text{immediate}}$), 12-pixel outer margin ($R_{\text{outer}}$), and remote parenchyma ($R_{\text{remote}}$), controlled against an area- and contour-matched contralateral normal tissue sham ($R_{\text{sham}}$) with guaranteed bitwise non-target pixel invariance ($0.00 \times 10^0$).
2. **Empirical Refutation of Clever Hans Remote Shortcuts:** We prove that remote parenchyma modifications produce near-zero, statistically non-significant evidence shifts ($\tau \le 0.013, p > 0.05$), demonstrating that classifiers do not rely on distant skull or cranial background shortcuts.
3. **Architectural Inductive Bias Disparity:** We provide quantitative biostatistical evidence demonstrating that Vision Transformers (DeiT-Small) exhibit significantly greater intra-lesion core reliance than CNNs (ResNet-50) ($\tau_{\text{diff}} = +0.074, p = 0.0123$) and achieve dramatically superior probability calibration (ECE 0.0366 vs 0.1835).
4. **Benchmark Integrity & Dual-Benchmark Reporting:** We discover and quantify a 10.1% train-test duplicate leakage in the official BRISC benchmark, establish the BRISC Clean Test Set ($N=899$), and demonstrate that duplicate contamination artificially inflates reported macro-F1 scores.

