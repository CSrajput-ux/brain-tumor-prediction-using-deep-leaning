# Missing Evidence and Author Questions Log

**Project:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification  
**Target Publication Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17  

---

### Category A: Internal Scientific & Statistical Verification Status
- **Empirical Pipeline Verified:** All 55,152 out-of-fold forward evaluations ($3\text{ scenarios} \times 6\text{ conditions} \times 3,064\text{ slices}$) across 15 checkpoints are complete, bit-for-bit verified, and internally consistent.
- **Statistical Procedures Audited:** Paired patient-cluster bootstrap ($B=25,000$ resamples) serves as the primary uncertainty analysis. Log-space exact two-sided binomial McNemar p-values prevent underflow without chi-square fallback substitution. Holm FWER control applied within declared hypothesis families.
- **Submission Gate Status:** **NOT YET VERIFIED — PENDING AUTHOR AND JOURNAL ACTIONS**.

---

### Category B: Missing Evidence & Unresolved Dataset Confounders
1. **Acquisition-Plane Confound (UNRESOLVED — DATASET LIMITATION):**
   - *Provenance Audit:* Exhaustive provenance audit of Cheng Figshare `cjdata` confirmed absence of DICOM headers, view angles, or orientation matrices. True anatomical plane labels (axial, coronal, sagittal) do not exist.
   - *Epistemic Verdict:* Explicitly designated as **UNRESOLVED — DATASET LIMITATION**.
   - *Resolution Stratification Caveat:* While resolution sensitivity analysis confirms stability between $512\times512$ (99.51%) and $256\times256$ (0.49%) slices ($< 0.002$ Macro-F1 divergence), **resolution stratification does not resolve acquisition-plane confounding**.
2. **External Multi-Center Cohort Validation:**
   - *Missing Evidence:* Evaluated on the public Cheng Figshare cohort (Nanfang Hospital and General Hospital of Tianjin Medical University). External datasets (such as BraTS or TCGA-LGG/GBM) were not tested under this matched 6-condition pipeline.
   - *Impact on Manuscript:* Empirical claims are strictly bounded to the evaluated Figshare cohort; multi-center clinical generalization is an open question.
3. **Alternative Neural Network Architectures:**
   - *Missing Evidence:* Evaluated across ResNet-50 backbones. Vision Transformers (ViT, Swin) and DenseNet architectures were not evaluated under matched boundary controls.
4. **Clinical Acquisition Scanner Metadata:**
   - *Missing Evidence:* Source repository lacks field strength (1.5T vs 3.0T), scanner vendor, TR, TE, and slice thickness.

---

### Category C: Author-Action Checklist Prior to Journal Submission
The submission gate is held at **NOT YET VERIFIED — PENDING AUTHOR AND JOURNAL ACTIONS** until the following items are completed by the human authors:

- [ ] **1. Author Identification & Affiliations:**
  - Insert genuine author full names, academic affiliations, institutional email addresses, and ORCID identifiers.
  - Designate corresponding author(s).
  - Note: Keep blinded placeholders if the selected journal requires double-blind peer review.
- [ ] **2. Target Journal Selection:**
  - Select target journal (status: PENDING AUTHOR SELECTION; candidate shortlist provided in `remaining_work_audit/springer_target_journals.md`).
  - Confirm journal formatting guidelines, reference style, word count, and review policy (single-blind vs double-blind).
- [ ] **3. Permanent Archive & DOI Deposition:**
  - Deposit code repository, split manifests, trained checkpoints, and reproducibility artifacts to a permanent scientific archive (e.g., Zenodo / OSF).
  - Update `[PENDING DEPOSITION PRIOR TO PUBLICATION — DO NOT FABRICATE DOI]` with genuine archive DOI. Pinned commit: `main` branch.
- [ ] **4. Funding Statement:**
  - Insert genuine funding agency names and grant identifiers into Declarations (do not invent funding sources).
- [ ] **5. Institutional Ethics Declaration:**
  - Verify and record institutional review board (IRB) exemption reference numbers or formal exemption declarations for secondary open-data analysis.
- [ ] **6. Competing Interests & Author Contributions:**
  - Confirm individual CRediT author contribution roles and finalize competing interest disclosure.

---

### Category D: Optional Presentation Improvements
1. **Interactive Web Demonstration:**
   - An interactive viewer (e.g., Streamlit / Gradio) allowing users to dynamically adjust seam blending widths and view real-time difference maps could enhance paper visibility.
2. **3D Cranial Anatomical Diagram:**
   - An illustrative cranial schematic showing the relative anatomical compartments of supratentorial gliomas vs sellar pituitary adenomas to visualize the categorical prior collapse.
