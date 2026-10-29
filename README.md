# Brain MRI: Region-Resolved Counterfactual Audit Pipeline

[![Pytest Status](https://img.shields.io/badge/pytest-41%2F41%20passed-brightgreen.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)]()

> **Title:** *Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification: A Sham-Controlled, Plane-Stratified Counterfactual Audit Across CNN and Vision Transformer Models*  
> **Authors:** Chhotu$^{1*}$ and Rishi Gupta$^{2}$  
> **Affiliation:** Manipal University Jaipur, Jaipur, Rajasthan, India  
> **Target Venue:** *Medical Image Analysis (MedIA) / IEEE Transactions on Medical Imaging (TMI)*  
> **Full Manuscript:** [`Brain_MRI_Research_Paper_Final.md`](file:///Brain_MRI_Research_Paper_Final.md) | [`paper/manuscript.md`](file:///paper/manuscript.md)

This repository contains the complete implementation, audit manifests, trained checkpoints, counterfactual interventions, biostatistical analysis, and high-resolution publication figures for our sham-controlled counterfactual audit of deep neural networks in contrast-enhanced brain MRI classification.

---

## Key Scientific Findings

1. **Benchmark Duplicate Leakage Audit in BRISC:**
   - Systematic pixel matrix and SHA-256 hashing across the local downloaded dataset archive revealed **101 out of 1,000 official test slices (10.1%) sharing bitwise identical pixel arrays with training/validation slices**, heavily concentrated in meningiomas (96/101).
   - In light of the official BRISC descriptor (Fateh et al., 2026) indicating pre-split deduplication and varying external hash reports, we treat this finding as an archive-specific empirical observation and report both the official benchmark ($N=1,000$) and the de-duplicated clean benchmark ($N=899$; 759 mask-supported) side-by-side. Deduplication rebalances class priors (meningiomas falling from 30.6% to 23.4%), altering macro-F1 (DeiT: 0.3566 official vs 0.5999 clean; ResNet: 0.3460 official vs 0.4181 clean).
2. **Region-Resolved Diagnostic Evidence & Methodological Sensitivity:**
   - Intra-lesion tumour core perturbations induce the largest evidence loss under boundary PDE inpainting ($\tau_{\text{core}} = 0.128 \pm 0.245$, $p < 10^{-5}$ on Cheng), whereas remote brain parenchyma edits yield negligible shifts indistinguishable from sham controls ($p > 0.05$).
   - However, spatial decay is condition- and architecture-dependent: under locally matched Gaussian texture filling and in skull-stripped scans, outer margin (12-pixel ring) edits frequently produce effects comparable to or exceeding the core ($\tau \approx 0.056\text{--}0.070$), reflecting both large annular mask tissue volume covering vasogenic perilesional edema and convolutional kernel sensitivity to high-frequency boundary textures.
3. **Peritumoral Transitional Margins Provide Critical Diagnostic Evidence:**
   - Modifying a 4-pixel immediate transitional margin ($R_{\text{immediate}}$) surrounding the primary lesion induces statistically significant evidence drops ($\tau = 0.021\text{--}0.024$, $p < 0.05$).
4. **Inductive Bias Disparity (ViT vs. CNN):**
   - DeiT-Small exhibits significantly greater reliance on intra-tumoral core evidence than ResNet-50 in the pooled multi-cohort ($\tau_{\text{diff}} = +0.0738$, paired Wilcoxon $p = 0.0123$, $d_z = 0.362$) and achieves substantially superior probability calibration (Cheng Expected Calibration Error: 0.0366 vs 0.1835).
5. **Exploratory Radiological Heterogeneity Across Tumour Subtypes:**
   - Infiltrative gliomas exhibit a substantial margin-to-core sensitivity ratio (35.0%), consistent with radiological perilesional border signals, whereas sellar-confined pituitary adenomas show minimal peripheral dependence (15.1%).

---

## Phased Project Architecture

| Phase | Description | Deliverables / Artifacts | Status |
|:---|:---|:---|:---:|
| **Phase 0** | Literature Review & Novelty Audit | [`reports/literature_review.md`](file:///reports/literature_review.md), [`reports/literature_matrix.csv`](file:///reports/literature_matrix.csv), [`reports/novelty_decision.md`](file:///reports/novelty_decision.md) | **COMPLETE** |
| **Phase 1** | Data Discovery & Ingestion | [`src/data/cheng_dataset.py`](file:///src/data/cheng_dataset.py), [`src/data/brisc_dataset.py`](file:///src/data/brisc_dataset.py), [`manifests/cheng_manifest.csv`](file:///manifests/cheng_manifest.csv), [`manifests/brisc_manifest.csv`](file:///manifests/brisc_manifest.csv) | **COMPLETE** |
| **Phase 2** | Duplicate Audit & Leakage-Free Splits | [`manifests/duplicate_pairs.csv`](file:///manifests/duplicate_pairs.csv), [`manifests/cheng_splits.csv`](file:///manifests/cheng_splits.csv), [`manifests/brisc_splits.csv`](file:///manifests/brisc_splits.csv), [`reports/duplicate_audit.md`](file:///reports/duplicate_audit.md) | **COMPLETE** |
| **Phase 3** | Deterministic Preprocessing & Mask Alignment | [`src/data/preprocessing.py`](file:///src/data/preprocessing.py), [`reports/preprocessing_report.md`](file:///reports/preprocessing_report.md), [`reports/diagnostic_overlays/`](file:///reports/diagnostic_overlays/) | **COMPLETE** |
| **Phase 4** | Model Architectures & Smoke Tests | [`src/models/resnet_classifier.py`](file:///src/models/resnet_classifier.py), [`src/models/deit_classifier.py`](file:///src/models/deit_classifier.py), [`src/models/training.py`](file:///src/models/training.py) | **COMPLETE** |
| **Phase 5** | Baseline Model Training & Calibration | Checkpoints in [`checkpoints/`](file:///checkpoints/), [`predictions/oof_predictions_*.csv`](file:///predictions/), [`reports/baseline_training_report.md`](file:///reports/baseline_training_report.md) | **COMPLETE** |
| **Phase 6** | Counterfactual Intervention Engine | [`src/interventions/regions.py`](file:///src/interventions/regions.py), [`src/interventions/inpainting.py`](file:///src/interventions/inpainting.py), [`manifests/intervention_qc.csv`](file:///manifests/intervention_qc.csv), [`reports/intervention_montages/`](file:///reports/intervention_montages/) | **COMPLETE** |
| **Phase 7** | Primary Biostatistical Counterfactual Audit | [`scripts/09_run_counterfactual_audit.py`](file:///scripts/09_run_counterfactual_audit.py), [`predictions/intervention_effects.csv`](file:///predictions/intervention_effects.csv), [`reports/primary_audit_summary.md`](file:///reports/primary_audit_summary.md) | **COMPLETE** |
| **Phase 8** | Secondary Experiments & Robustness | [`scripts/11_run_secondary_robustness.py`](file:///scripts/11_run_secondary_robustness.py), [`reports/secondary_robustness_report.md`](file:///reports/secondary_robustness_report.md) | **COMPLETE** |
| **Phase 9** | Publication Figures Generation | 10 high-resolution publication figures (300 DPI) in [`figures/`](file:///figures/) | **COMPLETE** |
| **Phase 10**| Full Research Manuscript | Publication-grade manuscripts in [`Brain_MRI_Research_Paper_Final.md`](file:///Brain_MRI_Research_Paper_Final.md) and [`paper/manuscript.md`](file:///paper/manuscript.md) | **COMPLETE** |

---

## Repository Structure

```
brain/
|-- configs/                        # YAML experiment and model configurations
|   `-- training.yaml               # AdamW, lr=1e-4/5e-5, batch_size=16, epochs=5
|-- manifests/                      # Audited metadata, split manifests, duplicate mappings
|   |-- cheng_manifest.csv          # 3,064 Cheng records with patient IDs
|   |-- brisc_manifest.csv          # 6,000 BRISC records with official partition labels
|   |-- cheng_splits.csv            # 5-fold patient-isolated cross-validation splits
|   |-- brisc_splits.csv            # Leakage-annotated clean benchmark splits
|   |-- duplicate_pairs.csv         # 159 identified exact duplicate pairs
|   |-- duplicate_groups.csv        # Clustered duplicate components
|   `-- intervention_qc.csv         # 1,200 counterfactual intervention QC logs
|-- checkpoints/                    # Saved model weights (.pt)
|-- predictions/                    # OOF, test, and counterfactual prediction records
|   |-- oof_predictions_*.csv       # Patient-isolated held-out fold 1 records (N=480)
|   |-- test_predictions_*.csv      # Mask-supported BRISC neoplasm test subset (N=480)
|   `-- intervention_effects.csv    # 1,800 paired intervention observations (N=90 slices)
|-- figures/                        # 300-DPI publication figures (Fig 1 through Fig 10)
|-- reports/                        # Detailed clinical and statistical audit reports
|-- paper/                          # Research manuscript documents
|   |-- manuscript.md               # Synchronized markdown manuscript
|   |-- manuscript.html             # Rendered HTML
|   `-- manuscript.pdf              # Generated publication PDF
|-- src/                            # Modular source code
|-- scripts/                        # Phased execution scripts (01 through 14)
`-- tests/                          # Automated Pytest validation test suite (41 tests)
```

---

## Reproduction Guide

### 1. Environment Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run the Full Phased Pipeline

```powershell
# Phase 1: Data Discovery & Manifest Generation
python scripts\02_build_manifests.py
python scripts\01_audit_data.py

# Phase 2: Duplicate Identification & Leakage-Free Split Creation
python scripts\03_audit_duplicates.py
python scripts\04_create_splits.py

# Phase 3: Preprocessing, Geometric Mask Alignment & Diagnostic Montages
python scripts\05_visualize_masks.py

# Phase 4: Model Architecture Validation & Smoke Testing
python scripts\06_smoke_test_models.py

# Phase 5: Baseline Training & Probability Calibration
python scripts\07_train_baseline.py

# Phase 6: Counterfactual Intervention Engine & Quality Control
python scripts\08_generate_interventions.py

# Phase 7: Primary Biostatistical Counterfactual Audit
python scripts\09_run_counterfactual_audit.py

# Phase 8: Secondary Replication, Plane Stratification & Robustness
python scripts\11_run_secondary_robustness.py

# Phase 9: Publication Figures Generation (300 DPI)
python scripts\10_generate_figures.py

# Phase 10: Publication Document Generation (DOCX & PDF)
python scripts\13_generate_final_docx.py
python scripts\14_generate_final_pdf.py
```

### 3. Verify Entire Test Suite

```powershell
python -m pytest tests -v
```
*Current test suite status: **41/41 passed (100% green)**.*

---

## Citation

If you use this codebase, audit methodologies, or counterfactual intervention framework in your research, please cite:

```bibtex
@article{chhotu2026braincounterfactual,
  title={Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification: A Sham-Controlled, Plane-Stratified Counterfactual Audit Across CNN and Vision Transformer Models},
  author={Chhotu and Gupta, Rishi},
  journal={Medical Image Analysis},
  year={2026}
}
```
