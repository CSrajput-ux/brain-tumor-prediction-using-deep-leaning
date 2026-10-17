# D — Unresolved Risk Record and Epistemic Boundary Audit

**Phase:** 1.8 — Final Protocol Ratification  
**Date:** 2026-10-17  
**Auditor:** Independent Medical Imaging & ML Evaluation Specialist  
**Authoritative Basis:** Cheng Dataset (3,064 slices, Figshare 2017)  
**Candidate Pairs Evaluated:** 236 cross-patient / cross-fold candidates (`reports/duplicate_investigation/duplicate_pair_review.csv`)  

---

## 1. Executive Summary

A core tenet of reproducibility engineering is maintaining an unambiguous record of what experimental risks have been **empirically controlled** by the evaluation design versus what risks remain **epistemically unknowable** from the available public artifacts.

We confirm:
- **No human review was fabricated:** All 236 candidate rows in `reports/independent_review/reviewer_decision_template.csv` retain unpopulated human review fields.
- **No source files, metadata, labels, or patient IDs were merged, deleted, or relabeled.**
- **No candidate pair is claimed as a confirmed biological duplicate or confirmed non-duplicate.**
- Exact source-file SHA-256 and stored-array hashes confirmed that zero candidate pairs are exact byte-level clones.

---

## 2. Risks Controlled by the Ratified Protocol

The ratified sensitivity evaluation protocol (Protocol C) directly controls the following major evaluation risks:

| Risk Category | Mechanism of Control | Verification Status |
|---|---|---|
| **Cross-Fold Near-Duplicate Leakage (SSIM ≥ 0.75 / 0.80)** | Indivisible combined evaluation groups co-assign all candidate pairs with $\text{SSIM} \ge \tau$ to the same evaluation fold in Scenarios S1 and S2. | **VERIFIED:** Zero residual cross-fold candidate pairs above threshold. |
| **Patient ID Leakage** | All slices sharing the same clinical patient ID are strictly assigned to a single fold across all scenarios. | **VERIFIED:** Zero patient ID crossings across all 5 folds. |
| **Intra-Patient Correlation Bias** | Uncertainty estimation uses patient-level cluster bootstrap ($B = 1,000$), preserving within-patient slice dependencies. | **VERIFIED:** Formalized in pre-registration protocol. |
| **Over-Fitting to Unproven Duplicate Assumptions** | Models are evaluated across a family of grouping assumptions (S0, S1, S2). Conclusions are accepted only if robust across assumptions. | **VERIFIED:** Pre-registered 3-tier sensitivity design. |
| **Masking Edge Artifact Confounding** | A matched contralateral placebo condition ($I_{\text{placebo}}$) isolates artificial boundary effects from true tumor reliance. | **VERIFIED:** Defined in pre-registration contrast battery. |
| **Test-Set Optimization Leakage** | Strict inner 80/20 train/validation split on 4 training folds; outer test fold evaluated once on frozen checkpoint. | **VERIFIED:** Enforced in model selection protocol. |

---

## 3. Risks That Remain Unknowable from Available Data

Despite rigorous protocol design, the following fundamental limitations cannot be resolved without access to original clinical hospital records:

| Unknowable Risk | Underlying Evidence Limitation | Impact on Research Interpretation |
|---|---|---|
| **True Patient Identity Across Hospitals** | The dataset merges cases from Nanfang Hospital (numeric PIDs like `108945`) and General Hospital of Tianjin Medical University (alphanumeric PIDs like `MR024780B`). Original medical record numbers were stripped during anonymization. | Cross-hospital duplicate acquisitions cannot be confirmed or ruled out. |
| **Suffix-Variant Relationships** | Pairs with identical numeric stems but differing suffix letters (e.g. `MR024780B` vs `MR024780G`) may represent sequential MRI exams of the same patient or different patients. | Treated as potential candidates under SSIM grouping, but biological identity is unconfirmed. |
| **Acquisition-Level Metadata** | Original DICOM headers (StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID, AcquisitionDate, slice thickness, repetition time) were not included in the public `.mat` release. | Slices cannot be reconstructed into 3D volumes or matched to specific imaging series. |
| **Screening Horizon Below pHash Threshold** | The candidate search screened pairs with pHash Hamming distance $\le 4/64$. Slices from the same patient with different head tilt or slice level with Hamming distance $> 4$ were not analyzed. | Unknown near-duplicates with higher perceptual divergence remain outside the candidate set. |
| **Ground-Truth Radiologist Annotations** | Tumor boundary masks provided in `cjdata.tumorMask` were created during the original 2015/2017 study by manual contouring. Inter-observer variability was not documented. | Slight contour imprecision cannot be distinguished from true anatomical boundaries. |
| **Public `cvind.mat` Mapping** | The 3,064-element `cvind` vector contains fold indices 1–5, but lacks an authoritative mapping to file numbers. | Cannot be used as an authoritative benchmark without risking unverified ordering assumptions. |

---

## 4. Epistemic Boundary Statement

The scientific community must evaluate brain tumor MRI classifier reliance with full awareness of these boundaries:
> *"The sensitivity analysis guarantees that observed findings are robust against candidate leakage at SSIM thresholds 0.75 and 0.80. However, it does not transform an anonymized 2D slice dataset into a fully traceable 3D clinical trial repository. Findings must be reported as characteristics of 2D MRI slice representations under controlled ablation, not as certified clinical diagnostic safety."*
