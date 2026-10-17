# Systematic Literature Search Protocol: Phase 7

**Document ID:** `PHASE_7_SEARCH_PROTOCOL`  
**Phase:** 7 — Systematic Literature Review and Novelty Verification  
**Authoritative Standard:** PRISMA-Informed Medical Imaging ML Review Protocol  
**Date of Execution:** 2026-10-17  
**Auditor:** Independent Scientific and Robustness Reviewer  

---

## 1. Objective and Research Scope

The purpose of this systematic search is to identify, map, and critically evaluate the prior art concerning:
1. Shortcut learning, confounding, and background bias in medical image classification (specifically brain MRI).
2. Spatial intervention techniques (lesion masking, whole-tumor excision, tumor-only evaluation, and distant context ablation).
3. Matched placebo regions, perilesional margin analyses, and inpainting controls for intervention-induced artifacts.
4. Patient-level data leakage and cluster-synchronized uncertainty estimation.
5. Specific prior art on the Figshare brain tumor dataset (Cheng et al.).

---

## 2. Databases and Information Sources

Searches were conducted across the following databases, academic discovery indexes, and repositories on **2026-10-17**:
- **PubMed / MEDLINE & Europe PMC** (Biomedical and neuro-oncological literature)
- **arXiv & OpenReview** (Preprints on computer vision, medical imaging with deep learning [MIDL], and ML robustness)
- **IEEE Xplore & CVF** (Computer vision, image processing, and IEEE transactions)
- **Google Scholar & Semantic Scholar** (Cross-disciplinary citation graphs and forward tracking)
- **Publisher Archives:** *Nature Communications*, *Nature Machine Intelligence*, *PLOS ONE*, *PLOS Medicine*, *JAMA Dermatology*, *ACM CHIL*

---

## 3. Systematic Search Queries by Family

The following exact boolean search queries were executed:

### Family A: Brain MRI Shortcuts, Confounding, and Spurious Correlations
- `Query A1:` `("brain tumor" OR "brain tumour") AND "MRI" AND ("shortcut learning" OR "spurious correlations" OR "confounding")`
- `Query A2:` `"medical imaging" AND "shortcut learning" AND "classification"`
- `Query A3:` `"MRI classification" AND ("anatomical bias" OR "spatial bias")`

### Family B: Lesion and Tumor Spatial Interventions
- `Query B1:` `("brain tumor" OR "brain tumour") AND "MRI" AND ("occlusion sensitivity" OR "lesion masking")`
- `Query B2:` `"brain MRI" AND ("tumor removal" OR "lesion ablation") AND "deep learning"`
- `Query B3:` `"medical image classification" AND "counterfactual" AND ("inpainting" OR "masking")`

### Family C: Context, Foreground vs. Background, and Localization Bias
- `Query C1:` `"medical imaging" AND "context dependence" AND "deep learning"`
- `Query C2:` `"medical imaging" AND ("background bias" OR "foreground vs background")`
- `Query C3:` `"The Role of Image Backgrounds" OR "Noise or Signal: The Role of Image Backgrounds"`

### Family D: Intervention Artifacts, Discontinuities, and Infilling
- `Query D1:` `"medical imaging" AND "inpainting" AND "occlusion sensitivity"`
- `Query D2:` `"image masking" AND "distribution shift" AND ("CNN" OR "deep learning")`
- `Query D3:` `"Navier-Stokes" AND "inpainting" AND ("Bertalmio" OR "OpenCV")`
- `Query D4:` `"Meaningful Perturbation" AND "Fong" AND "Vedaldi"`

### Family E: Evaluation Methodology, Leakage, and Cluster Statistics
- `Query E1:` `"medical imaging" AND "patient-level data leakage" AND "MRI"`
- `Query E2:` `("brain MRI" OR "neuroimaging") AND ("slice leakage" OR "patient leakage") AND "classification"`
- `Query E3:` `"medical imaging" AND "cluster bootstrap" AND "paired"`

### Family F: Figshare Cheng Dataset Prior Art
- `Query F1:` `"Cheng" AND "1512427" AND "brain tumor" AND ("classification" OR "leakage")`
- `Query F2:` `"Enhanced Performance of Brain Tumor Classification via Tumor Region Augmentation and Partition"`
- `Query F3:` `"Scores That Hold, Benchmarks That Leak: Measuring Dataset Contamination in Public Brain-Tumor MRI Classification"`

---

## 4. Screening, Inclusion, and Exclusion Criteria

### Inclusion Criteria:
1. Studies evaluating machine learning or deep learning on brain MRI classification or close medical analogs (e.g., chest X-ray, dermoscopy) where spatial confounding, shortcut learning, or feature attribution was tested.
2. Studies employing physical or in silico image ablations (e.g., masking, zero-fill, cropping, tile scrambling, or inpainting).
3. Foundational papers defining shortcut learning, hidden stratification, data contamination, and meaningful perturbations in vision.
4. Studies directly analyzing the Cheng brain tumor MRI benchmark (Figshare 1512427).

### Exclusion Criteria:
1. Pure segmentation challenge papers that do not evaluate classification or feature dependency.
2. Clinical trial papers using "occlusion" solely in the context of vascular stroke (e.g., large vessel occlusion).
3. Generic classification papers that merely train standard CNNs on the Cheng dataset without investigating feature attribution, leakage, or robustness.
4. Papers where full text was unverifiable or metadata was contradictory.
