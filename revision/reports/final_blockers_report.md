# Final Blockers & Outstanding Author Decisions Report

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
