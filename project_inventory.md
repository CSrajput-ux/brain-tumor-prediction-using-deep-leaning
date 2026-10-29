# Project Evidence Inventory: Brain MRI Research Pipeline

**Audit Date:** 2026-10-29  
**Auditor Persona:** Senior Medical-Imaging Researcher, CV/ML Scientist, Biostatistician, Research-Integrity Auditor  
**Machine-Readable Inventory:** [`project_inventory.csv`](file:///c:/Users/jkgga/Downloads/brain/project_inventory.csv) (143 catalogued artifact files)  

---

## 1. Inventory Summary by Functional Domain

| Functional Domain | File Count | Total Size | Primary Role & Source of Truth |
|:---|:---:|:---:|:---|
| **Raw Datasets (On-Disk)** | 97,537 files | ~2.15 GB | Ground-truth contrast-enhanced T1 brain MRI slices and masks (`cheng/` 3,064 .mat; `brisc/` 6,000 slices) |
| **Reference Paper Draft** | 1 file | 4.72 MB | [`paper/Brain_MRI_Paper_Final_Corrected_v6.docx`](file:///c:/Users/jkgga/Downloads/brain/paper/Brain_MRI_Paper_Final_Corrected_v6.docx) (Chhotu & Rishi Gupta, Manipal University Jaipur) |
| **Dataset Manifests** | 7 files | 3.42 MB | Audited sample registries, patient grouping, 159 duplicate pairs, and 1,200 intervention QC logs |
| **Core Source Code (`src/`)** | 14 files | 84.5 KB | Modular pipelines for data loading, deterministic preprocessing, ResNet-50, DeiT-Small, and 5-region interventions |
| **Execution Scripts (`scripts/`)** | 12 files | 52.8 KB | Phased execution pipeline from Phase 1 (Ingestion) to Phase 12 (PDF compilation) |
| **Model Checkpoints (`checkpoints/`)** | 8 files | 694.2 MB | Binary PyTorch weights (.pt) for ResNet-50 (23.5M params) and DeiT-Small (21.7M params) |
| **Predictions & Effects (`predictions/`)** | 5 files | 148.6 KB | Empirical probability distributions, out-of-fold records, and 1,800 paired counterfactual observations |
| **Reports & Audits (`reports/`)** | 18 files | 420.5 KB | Literature matrix, novelty decision, data audit, duplicate audit, baseline training, biostatistics |
| **Diagnostic Montages** | 45 images | ~12.8 MB | High-contrast visual overlays (`reports/diagnostic_overlays/` and `reports/intervention_montages/`) |
| **Publication Figures (`figures/`)** | 10 files | 3.50 MB | 300-DPI publication figures (Figures 1 through 10) |
| **Automated Test Suite (`tests/`)** | 10 files | 38.6 KB | 41 unit and regression tests, 100% green passing status |
| **Final Manuscript Exports (`paper/`)** | 4 files | 5.58 MB | Full manuscript in Markdown, HTML, and print-ready 16-page PDF |
| **Configs & Root Documentation** | 5 files | 18.2 KB | Experiment configurations, dependency manifests (`requirements.txt`), and repository documentation |

---

## 2. Key Artifact Catalogue

### 2.1 Reference Document
- **File:** [`paper/Brain_MRI_Paper_Final_Corrected_v6.docx`](file:///c:/Users/jkgga/Downloads/brain/paper/Brain_MRI_Paper_Final_Corrected_v6.docx) (4,715,135 bytes, modified 2026-10-28 23:32:33).
- **Authors:** Chhotu and Rishi Gupta (Department of Computer Science & Engineering, Manipal University Jaipur, India; email: `chhotu.2427030521@muj.manipal.edu`).
- **Original Study Focus:** Seam artefacts and spatial-context sensitivity in brain MRI tumour classification using tile-scrambling interventions and edge-seam controls on the Cheng dataset.
- **Role in Current Audit:** Presentation reference for scientific tone, typography, equation layout, section numbering, table styling, and declarations. All numerical claims are verified against our empirical code and result ledger.

### 2.2 Audited Manifests (`manifests/`)
1. [`manifests/cheng_manifest.csv`](file:///c:/Users/jkgga/Downloads/brain/manifests/cheng_manifest.csv) (3,064 rows): Verified slice paths, embedded patient IDs, ground-truth tumour labels, mask pixel areas, bounding boxes, and SHA-256 hashes.
2. [`manifests/brisc_manifest.csv`](file:///c:/Users/jkgga/Downloads/brain/manifests/brisc_manifest.csv) (6,000 rows): Official training ($N=5,000$) and test ($N=1,000$) partitions, 4 classes, acquisition planes (Axial, Coronal, Sagittal), and test mask availability ($N=860$).
3. [`manifests/cheng_splits.csv`](file:///c:/Users/jkgga/Downloads/brain/manifests/cheng_splits.csv) (3,064 rows): Patient-isolated 5-fold cross-validation split with **zero patient leakage**.
4. [`manifests/brisc_splits.csv`](file:///c:/Users/jkgga/Downloads/brain/manifests/brisc_splits.csv) (6,000 rows): Clean benchmark definition isolating 101 duplicate-leaked test slices from the clean test cohort ($N=899$).
5. [`manifests/duplicate_pairs.csv`](file:///c:/Users/jkgga/Downloads/brain/manifests/duplicate_pairs.csv) (159 pairs): Exact perceptual hash duplicate pairs identified in BRISC, including 110 pairs crossing the official train-test split boundary.
6. [`manifests/duplicate_groups.csv`](file:///c:/Users/jkgga/Downloads/brain/manifests/duplicate_groups.csv) (278 records): Clustered duplicate components.
7. [`manifests/intervention_qc.csv`](file:///c:/Users/jkgga/Downloads/brain/manifests/intervention_qc.csv) (1,200 records): Machine-readable verification log for all counterfactual interventions, confirming $0.00 \times 10^0$ outside-mask difference.

### 2.3 Model Weights & Checkpoints (`checkpoints/`)
- `checkpoints/resnet50_cheng_fold_1.pt` (94.4 MB): ResNet-50 trained on Cheng Fold 1 (3 classes).
- `checkpoints/resnet50_brisc.pt` (94.4 MB): ResNet-50 trained on BRISC training set (4 classes).
- `checkpoints/deit_small_patch16_224_cheng_fold_1.pt` (87.1 MB): DeiT-Small trained on Cheng Fold 1.
- `checkpoints/deit_small_patch16_224_brisc.pt` (87.1 MB): DeiT-Small trained on BRISC clean split.
- `checkpoints/smoke_test_*.pt` (4 files): Validated smoke test checkpoints for pipeline verification.

### 2.4 Empirical Predictions & Results (`predictions/`)
- `predictions/oof_predictions_cheng_fold_1_resnet50.csv` (480 rows): Probabilities and predictions for ResNet-50 on Cheng OOF validation.
- `predictions/oof_predictions_cheng_fold_1_deit_small.csv` (480 rows): Probabilities and predictions for DeiT-Small on Cheng OOF validation.
- `predictions/test_predictions_brisc_resnet50.csv` (480 rows): Probabilities for ResNet-50 across BRISC official and clean test subsets.
- `predictions/test_predictions_brisc_deit_small.csv` (480 rows): Probabilities for DeiT-Small across BRISC official and clean test subsets.
- [`predictions/intervention_effects.csv`](file:///c:/Users/jkgga/Downloads/brain/predictions/intervention_effects.csv) (1,800 rows): Paired counterfactual observations recording original probabilities $p_y(x)$, edited probabilities $p_y(x_{edit, r})$, raw drop $\Delta_r$, and sham-corrected causal sensitivity $\tau_r$.

### 2.5 Publication Figures (`figures/`)
- `fig1_study_design.png` (228 KB, 300 DPI): End-to-end study design, data ingestion, 5-region intervention engine, and dual perturbation methods.
- `fig2_preprocessing_alignment.png` (175 KB, 300 DPI): Intensity scaling $[P_1, P_{99}]$, letterbox padding, and binary mask alignment.
- `fig3_calibration_reliability.png` (244 KB, 300 DPI): Empirical reliability curves and ECE for ResNet-50 vs DeiT-Small.
- `fig4_regional_evidence_effects.png` (126 KB, 300 DPI): Sham-corrected sensitivity ($\tau_r$) across regions with paired Wilcoxon significance.
- `fig5_architecture_comparison.png` (114 KB, 300 DPI): Inductive bias difference plot ($\tau_{\text{ViT}} - \tau_{\text{CNN}}$).
- `fig6_method_robustness.png` (138 KB, 300 DPI): Perturbation method concordance (Telea boundary PDE vs Gaussian texture fill).
- `fig7_plane_stratification.png` (114 KB, 300 DPI): Sensitivity breakdown across Axial, Coronal, and Sagittal planes.
- `fig8_class_heterogeneity.png` (127 KB, 300 DPI): Histopathological sensitivity profiles across Meningiomas, Gliomas, and Pituitary adenomas.
- `fig9_brisc_leakage_artifact.png` (126 KB, 300 DPI): Benchmark inflation analysis caused by 10.1% train-test duplicate leakage.
- `fig10_intervention_gallery.png` (2.28 MB, 300 DPI): 8-panel diagnostic gallery with original slice, 5-color mask topology, Method A edits, Method B edits, and residual maps.

### 2.6 Full Research Manuscript Deliverables (`paper/`)
- [`paper/manuscript.md`](file:///c:/Users/jkgga/Downloads/brain/paper/manuscript.md) (35.9 KB): Comprehensive scientific manuscript with 11 formal sections, LaTeX formulations, empirical data tables, and complete references.
- [`paper/manuscript.html`](file:///c:/Users/jkgga/Downloads/brain/paper/manuscript.html) (4.95 MB): Self-contained publication HTML with base64 embedded figures.
- [`paper/manuscript.pdf`](file:///c:/Users/jkgga/Downloads/brain/paper/manuscript.pdf) (5.08 MB): 16-page publication PDF with running headers, page numbers, and embedded figures.

---

## 3. Duplicate Upload & Integrity Status

- **Duplicate Document Check:** Identified exact copy of `Brain_MRI_Paper_Final_Corrected_v6.docx` in both `c:\Users\jkgga\Downloads\` and `c:\Users\jkgga\Downloads\brain\paper\`. Verified byte-level identity (SHA-256 match; 4,715,135 bytes). No conflicting revisions detected.
- **Corrupt File Check:** 0 corrupt files. All `.pt` checkpoints, `.csv` prediction files, `.png` figures, and Python scripts load cleanly.
- **Automated Test Suite Status:** `pytest tests -v` $\to$ **41/41 PASSED (100% green)** in 20.95 seconds.

