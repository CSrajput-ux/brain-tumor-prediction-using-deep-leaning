# Manuscript Quality and Epistemic Integrity Audit

**Project:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification  
**Target Publication Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17  
**Audit Status:** **VERIFIED & COMPLIANT**  

---

### 1. Verification of Numerical Consistency
Every numerical result presented in the manuscript and abstract has been audited against the canonical result tables:
- **Baseline Macro-F1 ($C_0$):**
  - Reported: $S_0 = 0.9333$, $S_1 = 0.9332$, $S_2 = 0.9273$.
  - Canonical Source: `table4_baseline_metrics.csv` (Max diff: $0.0000$).
- **Seam-Only Macro-F1 ($C_1$):**
  - Reported: $S_0 = 0.6290$, $S_1 = 0.6094$, $S_2 = 0.6385$.
  - Canonical Source: `table5_intervention_metrics.csv` (Max diff: $0.0000$).
- **Seam-Suppressed Macro-F1 ($C_2$):**
  - Reported: $S_0 = 0.4525$, $S_1 = 0.4941$, $S_2 = 0.5159$.
  - Canonical Source: `table5_intervention_metrics.csv` (Max diff: $0.0000$).
- **Raw Scramble Macro-F1 ($C_3$):**
  - Reported: $S_0 = 0.5118$, $S_1 = 0.4884$, $S_2 = 0.5303$.
  - Canonical Source: `table5_intervention_metrics.csv` (Max diff: $0.0000$).
- **Contrasts and Confidence Intervals ($S_0$):**
  - $C_3 \text{ vs } C_0$: $+0.4215$ (95% CI: $[0.3734, 0.4726]$).
  - $C_1 \text{ vs } C_0$: $+0.3043$ (95% CI: $[0.2547, 0.3510]$).
  - $C_2 \text{ vs } C_0$: $+0.4808$ (95% CI: $[0.4361, 0.5292]$).
  - $C_3 \text{ vs } C_1$: $+0.1172$ (95% CI: $[0.0838, 0.1536]$).
  - $C_3 \text{ vs } C_2$: $-0.0593$ (95% CI: $[-0.0836, -0.0354]$).
  - Canonical Source: `table6_canonical_contrasts.csv` (100% matched).

---

### 2. Epistemic Phrasing & Claim Safeguards Audit
- **Audit Rule 1 (The 72% Statement):**  
  *Audit Check:* Did any section describe the 72% seam ratio as a causal percentage or variance decomposition?  
  *Result:* **PASSED.** The manuscript explicitly clarifies that $\frac{0.3043}{0.4215} = 72.2\%$ is strictly a descriptive arithmetic ratio of marginal declines, and highlights that the non-linear sum ($\Delta_{C1} + \Delta_{C2} = 0.7851 \gg 0.4215$) prohibits an additive causal decomposition.
- **Audit Rule 2 (Anatomical Mechanism):**  
  *Audit Check:* Did the text claim that intracranial skull-base coordinates or biological tumour causality were proven?  
  *Result:* **PASSED.** The text repeatedly emphasizes that ResNet-50 learns statistical correlations between peripheral image tiles and class priors, and that deep learning shortcuts must not be confused with biological disease mechanisms.
- **Audit Rule 3 (Equivalence from Non-Significance):**  
  *Audit Check:* Was non-significance in $S_1$ and $S_2$ for $C_3 \text{ vs } C_2$ claimed as proof of equivalence?  
  *Result:* **PASSED.** The manuscript explicitly documents that $p = 0.123$ and $p = 0.138$ indicate failure to reject the null hypothesis, which cannot be conflated with equivalence.

---

### 3. Bibliography and Citation Integrity
- All 16 citations in `references.bib` were verified against `reference_verification.csv`.
- Zero placeholder or invented citations exist.
- Key foundational prior art is correctly attributed:
  - Shortcut learning foundations: Geirhos et al. (2020).
  - Radiographic shortcut discovery: DeGrave et al. (2021), Zech et al. (2018).
  - Dermoscopic surgical mark confounds: Winkler et al. (2019), Bissoto et al. (2019).
  - Original dataset sources: Cheng et al. (2015, 2016).
  - Brain tumour dataset leakage audits: Vangala et al. (2026).
