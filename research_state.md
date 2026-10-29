# Research State & Study Specification: Brain MRI Pipeline

**Date:** 2026-10-29  
**Branch:** `fresh-start`  
**Test Suite Status:** **41 / 41 PASSED (100% green)** in 20.95 seconds  

---

## 1. Study Paradigm Reconciliation

The repository contains evidence of two distinct evolutionary stages of this research:

### 1.1 The Reference Draft (`Brain_MRI_Paper_Final_Corrected_v6.docx`)
- **Title:** *“Seam Artefacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Audit Across Deep Architectures”*
- **Authors:** Chhotu and Rishi Gupta (Department of Computer Science & Engineering, Manipal University Jaipur, India; email: `chhotu.2427030521@muj.manipal.edu`).
- **Core Investigation:** Evaluated tile-scrambling ($2 \times 2$ and $4 \times 4$ permutations) as an interpretability probe for spatial-context reliance, introducing edge-seam controls (grid line overlays, edge smoothing) on the Cheng dataset.
- **Role in Master Prompt:** Serves as the primary format, structural, typographic, and stylistic template (section hierarchy, table formatting, nomenclature conventions, Declarations).

### 1.2 The Implemented & Verified Study (Current Pipeline)
- **Title:** *“Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification: A Sham-Controlled, Plane-Stratified Counterfactual Audit Across CNN and Vision Transformer Models”*
- **Target Venue:** *Medical Image Analysis* (MedIA) / *IEEE Transactions on Medical Imaging* (TMI).
- **Core Investigation:** Resolves the critical question of whether deep networks rely on intra-lesion tumour morphology, peritumoral transitional zones, or remote cranial shortcuts ("Clever Hans" effect).
- **Key Methodological Innovations:**
  1. Five-region topological decomposition: Tumour Core ($R_{core}$), Immediate Margin ($R_{immediate}$, 4-pixel ring), Outer Margin ($R_{outer}$, 12-pixel ring), Remote Parenchyma ($R_{remote}$), and Contralateral Sham Control ($R_{sham}$).
  2. Dual perturbation engines: Method A (Telea boundary PDE inpainting) and Method B (locally matched Gaussian texture fill).
  3. Strict non-target pixel invariance ($|\Delta| < 10^{-5}$ outside mask).
  4. Multi-plane stratification across Axial, Coronal, and Sagittal views (BRISC).
  5. Discovery and rigorous handling of 10.1% train-test duplicate leakage in the BRISC benchmark.
  6. Direct comparison of architectural inductive biases: ResNet-50 (convolutional) vs DeiT-Small (Vision Transformer).

---

## 2. Experimental Verification State (Phases 0 through 10)

| Phase | Description | Implemented Code & Scripts | Verification Evidence |
|:---|:---|:---|:---:|
| **Phase 0** | Literature Review & Novelty Audit | [`reports/literature_review.md`](file:///reports/literature_review.md), [`reports/novelty_decision.md`](file:///reports/novelty_decision.md) | **GO** (Decision documented) |
| **Phase 1** | Data Discovery & Ingestion | [`src/data/cheng_dataset.py`](file:///src/data/cheng_dataset.py), [`src/data/brisc_dataset.py`](file:///src/data/brisc_dataset.py), [`scripts/01_audit_data.py`](file:///scripts/01_audit_data.py) | **3,064 Cheng + 6,000 BRISC slices audited** |
| **Phase 2** | Duplicate Audit & Leakage-Free Splits | [`scripts/03_audit_duplicates.py`](file:///scripts/03_audit_duplicates.py), [`scripts/04_create_splits.py`](file:///scripts/04_create_splits.py) | **159 BRISC duplicates mapped; 0 patient overlap across 5 Cheng folds** |
| **Phase 3** | Deterministic Preprocessing & Mask Alignment | [`src/data/preprocessing.py`](file:///src/data/preprocessing.py), [`scripts/05_visualize_masks.py`](file:///scripts/05_visualize_masks.py) | **0 masks disappeared; centroid drift < 0.0035; 21 diagnostic overlays** |
| **Phase 4** | Model Architectures & Smoke Tests | [`src/models/resnet_classifier.py`](file:///src/models/resnet_classifier.py), [`src/models/deit_classifier.py`](file:///src/models/deit_classifier.py) | **Forward, backward, and checkpoint roundtrips verified** |
| **Phase 5** | Baseline Training & Calibration | [`scripts/07_train_baselines.py`](file:///scripts/07_train_baselines.py), [`reports/baseline_training_report.md`](file:///reports/baseline_training_report.md) | **Checkpoints saved; Macro-F1 & ECE evaluated on 480 OOF / test samples** |
| **Phase 6** | Counterfactual Intervention Engine | [`src/interventions/regions.py`](file:///src/interventions/regions.py), [`src/interventions/inpainting.py`](file:///src/interventions/inpainting.py) | **1,200 interventions generated; 100% QC pass rate ($0.00\times 10^0$ outside)** |
| **Phase 7** | Primary Biostatistical Audit | [`scripts/09_run_counterfactual_audit.py`](file:///scripts/09_run_counterfactual_audit.py), [`predictions/intervention_effects.csv`](file:///predictions/intervention_effects.csv) | **1,800 paired observations; Wilcoxon tests and Cohen's $d_z$ computed** |
| **Phase 8** | Secondary Experiments & Robustness | [`scripts/11_run_secondary_robustness.py`](file:///scripts/11_run_secondary_robustness.py), [`reports/secondary_robustness_report.md`](file:///reports/secondary_robustness_report.md) | **ViT vs CNN bias, plane stratification, and class heterogeneity verified** |
| **Phase 9** | Publication Figures Generation | [`scripts/10_generate_figures.py`](file:///scripts/10_generate_figures.py), [`figures/fig1_study_design.png`](file:///figures/) | **10 figures rendered at 300 DPI** |
| **Phase 10**| Manuscript & PDF Deliverables | [`scripts/12_generate_manuscript_pdf.py`](file:///scripts/12_generate_manuscript_pdf.py), [`paper/manuscript.pdf`](file:///paper/manuscript.pdf) | **16-page PDF with embedded figures, equations, and tables** |

---

## 3. Key Empirical Findings (Source of Truth)

1. **Tumour Core Diagnostic Primacy:**  
   Inpainting the tumour core induces the largest, highly significant drop in ground-truth class confidence ($\tau_{\text{core}} = 0.128\text{--}0.145$, $p < 10^{-5}$, $d_z = 0.518\text{--}0.669$ for DeiT-Small on Cheng).
2. **Peritumoral Margin Diagnostic Contribution:**  
   Ablating the 4-pixel immediate perilesional margin produces a statistically significant drop ($\tau_{\text{immediate}} = 0.021\text{--}0.024$, $p < 0.05$), confirming the clinical relevance of transitional boundary cues.
3. **Absence of Remote Shortcut Dependence:**  
   Perturbing remote brain parenchyma produces negligible, non-significant shifts ($\tau_{\text{remote}} \le 0.013$, $p > 0.05$), conclusively refuting the hypothesis that classifiers rely on distant skull or cranial background shortcuts.
4. **Architectural Inductive Bias:**  
   DeiT-Small (ViT) exhibits higher reliance on core features than ResNet-50 ($\tau_{\text{diff}} = +0.074$, $p = 0.0123$) and achieves dramatically superior probability calibration (Cheng ECE 0.0366 vs 0.1835).
5. **Histopathological Heterogeneity:**  
   Infiltrative gliomas exhibit a 35.0% margin-to-core sensitivity ratio, meningiomas 33.1%, and sellar-confined pituitary adenomas only 15.1%.
6. **BRISC Benchmark Leakage Impact:**  
   101 test slices (10.1% of the official benchmark) are identical copies of training slices (96 meningiomas), severely inflating reported benchmark performance.

