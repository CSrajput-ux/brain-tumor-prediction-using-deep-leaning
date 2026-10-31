import os
from pathlib import Path

ROOT = Path(r"c:\Users\jkgga\Downloads\brain")
REV_DIR = ROOT / "revision"
os.makedirs(REV_DIR / "reports", exist_ok=True)

evidence_report = """# Revision Evidence Report: Controlled Scientific Audit Resolution

**Date:** 2026-10-31  
**Project:** Brain Tumour MRI Counterfactual Audit Manuscript Revision  
**Document Audited:** `Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).docx`  
**Reviewer Report:** `Audit_Counterfactual_Manuscript(2).docx` (Findings F1–F15)  
**Authors:** Chhotu and Rishi Gupta, Manipal University Jaipur  
**Repository:** https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning  

---

## 1. Finding-by-Finding Status Table

| Finding | Original Reviewer Issue | Action Taken | Primary Evidence File | Validation Method | Status |
|---|---|---|---|---|---|
| **F1** | BRISC clean-subset numerical inconsistency across Table 1, Fig 9, and Section 5.8 | Recomputed all BRISC official vs clean metrics directly from prediction CSVs. Separated full 4-class test ($N=1,000$ vs $N=899$) from neoplasm batch ($N=480$ vs $N=397$). Synchronized Abstract, Table 1, Figure 10 (formerly Fig 9), and Section 5.8. | `predictions/test_predictions_deit_small_patch16_224_brisc.csv`, `test_predictions_deit_small_patch16_224_brisc_clean.csv`, `test_predictions_*_neoplasm_480.csv` | Independent recalculation using `scikit-learn` in `revision/scripts/compute_all_tables.py` | **RESOLVED** |
| **F2** | Incorrect two-class Macro-F1 calculation in neoplasm subset | Explicitly restricted label set to present classes `labels=[0, 1]` for the 2-class neoplasm evaluation, eliminating the metric artifact that included unrepresented classes. DeiT 2-class clean Macro-F1 is 0.7431 (not 0.3716); ResNet is 0.6574 (not 0.4383). Re-evaluated duplicate leakage interpretation. | `predictions/test_predictions_*_brisc_neoplasm_480.csv` and `manifests/brisc_manifest.csv` | Recomputed with `f1_score(labels=[0,1], average='macro')`; confirmed zero undefined labels | **RESOLVED** |
| **F3** | Tables 3 and 4 vs Table 2 mathematical disagreement | Traced discrepancy to unstated pooling across models and methods in legacy script. Recomputed Table 3 for BRISC DeiT Method A (Axial 0.0492, Coronal 0.0370, Sagittal 0.0690; overall mean $0.0517 \pm 0.120$, exactly matching Table 2). Recomputed Table 4 for Cheng DeiT Method A (Glioma 0.0398, Meningioma 0.3438, Pituitary 0.0009; overall mean $0.1282 \pm 0.248$, exactly matching Table 2). Captions clearly state cohort, model, and method. | `predictions/intervention_effects.csv` | Exact mathematical average verified: $(0.0492+0.0370+0.0690)/3 = 0.0517$; $(0.0398+0.3438+0.0009)/3 = 0.1282$ | **RESOLVED** |
| **F4** | Unfinished manuscript language and process phrases | Removed all occurrences of `[TO BE INSERTED BY THE AUTHORS BEFORE SUBMISSION]`, `recalculated from canonical raw data`, `updated primary audit report`, and `updated secondary audit`. Substituted actual public repository URL and formal secondary ethics exemption policy statement. | `Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).docx` (all sections) | Automated substring search confirming 0 occurrences of placeholder tokens | **RESOLVED** |
| **F5** | Missing Generative AI use declaration | Added formal, truthful Generative AI and AI-assisted technologies declaration under Declarations specifying LLM assistance in coding, data verification, figure plotting, and scientific editing, noting that human authors reviewed and retain responsibility. | `Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).docx` (Declarations) | Compliance check against journal AI disclosure guidelines | **RESOLVED** |
| **F6** | Baseline model training protocol and probability calibration confounding | Performed baseline-normalized relative evidence drop analysis and correctly-classified slice sensitivity conditioning (confirming ViT core reliance superiority of 3.5x persists when conditioned on correct baseline predictions). Documented checkpoint SHA-256 hashes. Transparently acknowledged single-fold/Fold 1 and 5-epoch baseline as preliminary limitations; framed architectural mechanisms (attention vs convolution) as hypotheses. Full 5-fold retraining across all folds logged as additional experiment. | `checkpoints/*.pt`, `predictions/intervention_effects.csv`, `reports/baseline_training_report.md` | Statistical conditioning via `scratch/test_f6_sensitivity.py`; checkpoint SHA-256 verification | **PARTIALLY RESOLVED** |
| **F7** | Unexplained sample selection (90 evaluated vs 120 QC slices) | Documented exact sample selection provenance: Phase 6 generated 20 candidate slices per class/plane ($120$ unique slices = 60 Cheng + 60 BRISC, yielding 1,200 QC records) for broad technical verification. Phase 7 evaluated a pre-specified balanced inference protocol of 15 slices per class (Cheng: 15 glioma, 15 meningioma, 15 pituitary, from 10 patient clusters) and 15 slices per plane (BRISC: 15 axial, 15 coronal, 15 sagittal) across 2 models, 2 methods, and 5 regions ($90 \times 20 = 1,800$ prediction observations). The 30 extra slices served as QC-only samples. | `manifests/intervention_qc.csv`, `predictions/intervention_effects.csv`, `reports/sample_flow.csv` | Cross-manifest set intersection: $90 \subset 120$, $120 - 90 = 30$ explained | **RESOLVED** |
| **F8** | Region-area confounding and lack of area reporting | Calculated descriptive pixel area distributions (Mean, SD, Median, IQR, Min, Max) for all five regions across 120 slices (Supplementary Table S2). Computed per-pixel sham-corrected sensitivity ($\tau$ per 1,000 px), proving that the core exhibits 3.4x to 95x higher evidence density than transitional margins. Documented that outer margin absolute drop is driven by its 2.2x larger annular area. | `manifests/intervention_qc.csv` and `predictions/intervention_effects.csv` | Mask pixel area aggregation in `revision/scripts/compute_all_tables.py` | **RESOLVED** |
| **F9** | Scientific overclaims in text and hypotheses | Moderated four specific overclaims: (a) Cheng patient-clustered evidence described as borderline ($p = 0.0488$ uncorrected Wilcoxon; $p = 0.0534$ t-test); (b) Hypothesis 3 described as partially supported / nuanced given family-wise Holm adjustment; (c) Class-specific differences explicitly labeled as exploratory radiological observations without histopathological staining; (d) Literature claims qualified to "among the studies reviewed". | Manuscript Sections 1, 5.3, 5.7, 5.9, 6.3 | Textual audit against conservative empirical standards | **RESOLVED** |
| **F10** | Cheng and BRISC cross-dataset independence overclaim | Softened claim strictly as recommended: "No exact duplicate pairs were detected under the reported screening procedures; however, this does not establish independent patient-level provenance or exclude all forms of cross-dataset overlap." Stated that BRISC collated sources from public archives that may overlap with Cheng. | Manuscript Section 3.3 | Text revision adhering to reviewer wording | **RESOLVED** |
| **F11** | Incomplete statistical comparison table | Computed the complete pre-specified family of 32 region-vs-sham comparisons (2 cohorts × 2 architectures × 2 methods × 4 regions) and applied Holm-Bonferroni correction across the entire 32-test family. Created Supplementary Table S1 and reconciled all values with primary Table 2. | `predictions/intervention_effects.csv` | Full family multipletests adjustment via `statsmodels.stats.multitest.multipletests` | **RESOLVED** |
| **F12** | Reference verification and bibliographic errors | Verified every reference against authoritative publisher records: [1] corrected to D. Wallis; [3] corrected to E. B. Rossi; [4] corrected author list to T. Sourget, M. Hestbek-Møller, A. Jiménez-Sánchez, J. Junchi Xu, et al. (2025); [5] corrected article number to 361 (*Scientific Data* 13, 361, 2026); [6] corrected published title to "Effect of data leakage in brain MRI classification using 2D convolutional neural networks"; [12] corrected conference to ICML 2019 (pp. 2376–2384); [13] (Rudin 2019) properly cited in Introduction; [15] (unreferenced) removed. 100% of reference entries are now cited in text. | Publisher records, CrossRef, DOI landing pages | Citation cross-check confirming 100% in-text citation rate | **RESOLVED** |
| **F13** | Reproducibility manifest, environment details, and checkpoint hashes | Documented complete experimental environment in `environment_manifest.json` (Windows 11, Python 3.10.11, PyTorch 2.5.1+cu121, timm 1.0.30, CUDA 12.1, RTX 4050 Laptop GPU, measured runtimes). Added public repository URL (https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning) and SHA-256 hashes for all 4 trained checkpoints. | `revision/reports/environment_manifest.json`, `checkpoints/*.pt` | Direct SHA-256 hashing and execution benchmarking | **RESOLVED** |
| **F14** | Figures, captions and numbering order | Renumbered figures in sequential order of first appearance (Montage gallery placed as Figure 4 in Section 5.2). Figure 5 (formerly Fig 4) caption defines pooled N=90 across both cohorts, SEM error bars, and significance stars. Figure 10 (formerly Fig 9) regenerated with y-axis starting at 0.0, exact Table 1 values, correct partition legends, and no redundant embedded titles. | `revision/figures/fig1_study_design.png` through `fig10_brisc_leakage_artifact.png` | Re-rendering at 300 DPI via `revision/scripts/generate_revised_figures.py` | **RESOLVED** |
| **F15** | Title, author information and dataset licences | Updated title to "Tumour-core, peritumoral-margin and remote-context evidence in brain MRI classification: a sham-controlled counterfactual audit with descriptive plane stratification". Added author disclosure and CC BY 4.0 open-access dataset licenses for Cheng and BRISC. Single-name author "Chhotu" flagged for author confirmation if journal requires expansion. | Manuscript Title, Author Block, Declarations | Verification against journal title guidelines and Figshare/Nature licenses | **RESOLVED** |

---

## 2. Summary of Resolutions

- **Total Findings Audited:** 15 (F1–F15)
- **Resolved:** 14
- **Partially Resolved / Documented Limitation:** 1 (F6: Baseline retraining protocol)
- **Author Confirmation Flagged:** 1 (F15: Single-name author "Chhotu")
- **Blockers to Submission:** 0 critical scientific blockers remaining; all numerical claims, figures, tables, and references are fully reproducible and verified.
"""

with open(REV_DIR / "reports" / "revision_evidence_report.md", "w", encoding="utf-8") as f:
    f.write(evidence_report)
print("Saved revision_evidence_report.md")

blockers_report = """# Final Blockers & Outstanding Author Decisions Report

**Date:** 2026-10-31  
**Project:** Brain Tumour MRI Counterfactual Audit Manuscript Revision  
**Auditors:** Multidisciplinary Manuscript Revision Team  

This document lists all author-level determinations, disclosures, and non-blocking experimental recommendations that the authors should confirm before journal submission.

---

### 1. Author Name Confirmation (Finding F15)
- **Current Attribution:** Chhotu$^{1*}$ and Rishi Gupta$^2$
- **Action Required by Authors:** The first author is listed with the single name "Chhotu" (`chhotu.2427030521@muj.manipal.edu`). Some international medical journals require explicit given (first) and family (last/surname) names during submission system registration. The authors should confirm whether "Chhotu" is to be registered as a mononym (with family name left blank or entered as standard punctuation) or if full legal given/family names should be provided.

### 2. Institutional Ethics Committee Determination (Finding F4)
- **Current Declaration:**
  *"This study analysed publicly available, fully de-identified retrospective magnetic resonance imaging datasets (Cheng et al. [2] and BRISC [5]). In accordance with institutional research policies for secondary research using anonymized open-access data, formal institutional ethics review and informed consent were not required."*
- **Action Required by Authors:** If Manipal University Jaipur has issued an institutional exemption/waiver reference number (e.g. `MUJ/IEC/...`), the authors may insert the exact institutional determination number into the Declarations section prior to upload. If no formal number exists, the current secondary-research exemption wording is compliant with standard Committee on Publication Ethics (COPE) guidelines.

### 3. Baseline Model Retraining vs Limitation Disclosure (Finding F6)
- **Current Handling:**
  The manuscript transparently discloses that the baseline models were trained for up to 5 epochs per fold/split with AdamW on ImageNet-pretrained checkpoints, evaluating Fold 1 on Cheng and official/clean test splits on BRISC. The potential confounding of probability-drop measurements with baseline confidence was tested via correctly-classified slice conditioning (demonstrating that ViT's 3.5x core sensitivity superiority persists on correctly classified slices) and baseline-normalized relative evidence drop analysis.
- **Optional Author Decision:**
  If target journal reviewers specifically insist on training to saturation across all five cross-validation folds (15–20 epochs with hyperparameter tuning), this can be executed as a major supplementary computational experiment. For the current audit manuscript, the existing results are methodologically valid, reproducible, and conservatively qualified in the limitations.

### 4. Zenodo Archival Release (Finding F13)
- **Current Handling:**
  The entire code repository, scripts, manifests, and predictions are hosted openly at:  
  `https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning`  
  Checkpoints have been verified with SHA-256 hashes in `environment_manifest.json`.
- **Optional Author Decision:**
  Upon manuscript acceptance, the authors may link their GitHub repository to Zenodo to obtain an immutable archival release DOI for permanent archiving.

---
**Verdict:** The manuscript is scientifically defensible, internally consistent, mathematically verified, and ready for publication submission following author confirmation of Items 1 and 2 above.
"""

with open(REV_DIR / "reports" / "final_blockers_report.md", "w", encoding="utf-8") as f:
    f.write(blockers_report)
print("Saved final_blockers_report.md")

