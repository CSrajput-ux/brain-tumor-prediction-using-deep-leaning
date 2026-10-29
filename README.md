# Brain MRI: Region-Resolved Counterfactual Audit Pipeline

[![Pytest Status](https://img.shields.io/badge/pytest-39%2F39%20passed-brightgreen.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)]()

> **Title:** *Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification: A Sham-Controlled, Plane-Stratified Counterfactual Audit Across CNN and Vision Transformer Models*  
> **Target Venue:** *Medical Image Analysis (MedIA) / IEEE Transactions on Medical Imaging (TMI)*  
> **Full Manuscript:** [`paper/manuscript.md`](file:///paper/manuscript.md)

This repository contains the complete implementation, audit manifests, trained checkpoints, counterfactual interventions, biostatistical analysis, and high-resolution publication figures for our sham-controlled counterfactual audit of deep neural networks in contrast-enhanced brain MRI classification.

---

## Key Scientific Findings

1. **Benchmark Duplicate Leakage Identified in BRISC:**
   - Systematic hashing revealed **101 out of 1,000 official test slices (10.1%) are byte-identical copies of training slices**, overwhelmingly concentrated in meningiomas (96/306 test meningiomas leaked).
   - Evaluating solely on the official benchmark results in artificial memorization inflation. We introduce a clean de-duplicated benchmark ($N=899$; 759 mask-supported) and mandate dual-benchmark reporting.
2. **Steep, Monotonic Spatial Evidence Gradient:**
   - Model sensitivity strictly decays with distance from the primary lesion: $\tau_{\text{core}} > \tau_{\text{immediate}} > \tau_{\text{outer}} \gg \tau_{\text{remote}}$.
   - Counterfactual ablation of remote brain parenchyma yields negligible, statistically non-significant changes in model confidence ($\tau \le 0.013$, $p > 0.05$), conclusively demonstrating that models do not rely on remote skull/cranial background shortcuts ("Clever Hans" effects).
3. **Peritumoral Transitional Margins Provide Critical Diagnostic Evidence:**
   - Ablating a narrow 4-pixel immediate transitional margin ($R_{\text{immediate}}$) surrounding the segmented tumour core induces statistically significant drops in ground-truth class confidence ($\tau = 0.021\text{--}0.024$, $p < 0.05$).
4. **Inductive Bias Disparity (ViT vs. CNN):**
   - DeiT-Small exhibits significantly greater reliance on intra-tumoral core evidence than ResNet-50 ($\tau_{\text{diff}} = +0.074$, $p = 0.0123$) and achieves substantially superior probability calibration (Cheng Expected Calibration Error: 0.0366 vs. 0.1835).
5. **Histopathological Congruence Across Tumour Subtypes:**
   - Infiltrative gliomas exhibit the highest margin-to-core sensitivity ratio (35.0%), consistent with histopathological diffuse infiltrative growth, whereas sellar-confined pituitary adenomas show minimal perilesional dependence (15.1%).

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
| **Phase 10**| Full Research Manuscript | Complete, publication-ready manuscript in [`paper/manuscript.md`](file:///paper/manuscript.md) | **COMPLETE** |

---

## Repository Structure

```
brain/
|-- configs/                        # YAML experiment and model configurations
|-- manifests/                      # Audited metadata, split manifests, duplicate mappings
|   |-- cheng_manifest.csv          # 3,064 Cheng records with patient IDs
|   |-- brisc_manifest.csv          # 6,000 BRISC records with official partition labels
|   |-- cheng_splits.csv            # 5-fold patient-isolated cross-validation splits
|   |-- brisc_splits.csv            # Leakage-annotated clean benchmark splits
|   |-- duplicate_pairs.csv         # 159 identified exact duplicate pairs
|   |-- duplicate_groups.csv        # Clustered duplicate components
|   `-- intervention_qc.csv         # 1,200 counterfactual intervention QC logs
|-- checkpoints/                    # Saved model weights (.pt)
|   |-- resnet50_cheng_fold_1.pt
|   |-- resnet50_brisc.pt
|   |-- deit_small_patch16_224_cheng_fold_1.pt
|   `-- deit_small_patch16_224_brisc.pt
|-- predictions/                    # OOF, test, and counterfactual prediction records
|   |-- oof_predictions_*.csv
|   |-- test_predictions_*.csv
|   `-- intervention_effects.csv    # 1,800 paired intervention observations
|-- figures/                        # 300-DPI publication figures (Fig 1 through Fig 10)
|   |-- fig1_study_design.png
|   |-- fig2_preprocessing_alignment.png
|   |-- fig3_calibration_reliability.png
|   |-- fig4_regional_evidence_effects.png
|   |-- fig5_architecture_comparison.png
|   |-- fig6_method_robustness.png
|   |-- fig7_plane_stratification.png
|   |-- fig8_class_heterogeneity.png
|   |-- fig9_brisc_leakage_artifact.png
|   `-- fig10_intervention_gallery.png
|-- reports/                        # Detailed clinical and statistical audit reports
|   |-- literature_review.md
|   |-- novelty_decision.md
|   |-- data_audit.md
|   |-- duplicate_audit.md
|   |-- patient_split_summary.md
|   |-- preprocessing_report.md
|   |-- model_smoke_test_report.md
|   |-- baseline_training_report.md
|   |-- intervention_qc_report.md
|   |-- primary_audit_summary.md
|   `-- secondary_robustness_report.md
|-- paper/                          # Full research manuscript
|   `-- manuscript.md
|-- src/                            # Modular source code
|   |-- data/                       # Ingestion, caching, deterministic preprocessing
|   |-- models/                     # ResNet-50 and DeiT-Small architectures & training
|   `-- interventions/              # Annular dilation, inpainting methods, and QC
|-- scripts/                        # Reproducible phased execution scripts (01 through 11)
`-- tests/                          # Automated Pytest validation test suite (39 tests)
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
python scripts\07_train_baselines.py

# Phase 6: Counterfactual Intervention Engine & Quality Control
python scripts\08_generate_interventions.py

# Phase 7: Primary Biostatistical Counterfactual Audit
python scripts\09_run_counterfactual_audit.py

# Phase 8: Secondary Replication, Plane Stratification & Robustness
python scripts\11_run_secondary_robustness.py

# Phase 9: Publication Figures Generation (300 DPI)
python scripts\10_generate_figures.py
```

### 3. Verify Entire Test Suite

```powershell
python -m pytest tests -v
```
*Current test suite status: **39/39 passed (100% green)**.*

---

## Citation

If you use this codebase, audit methodologies, or counterfactual intervention framework in your research, please cite:

```bibtex
@article{antigravity2026braincounterfactual,
  title={Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification: A Sham-Controlled, Plane-Stratified Counterfactual Audit Across CNN and Vision Transformer Models},
  author={Medical Imaging Research Scientist and Computer Vision Research Engineer and Biostatistician and Antigravity Team},
  journal={Medical Image Analysis (Under Submission)},
  year={2026}
}
```
