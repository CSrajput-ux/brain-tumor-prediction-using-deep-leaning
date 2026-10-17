# Missing Evidence and Author Questions Log

**Project:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification  
**Target Publication Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17  

---

### Category A: Blocking Scientific Issues
- **None Identified.**  
  All empirical calculations, model predictions, image invariants, and bootstrap contrasts are 100% complete, reproducible, and internally consistent across the 36,768 forward evaluations.

---

### Category B: Missing Evidence (Documented Study Limitations)
1. **External Multi-Center Cohort Validation:**
   - *Missing Evidence:* The study is evaluated exclusively on the public Cheng Figshare dataset (Nanfang Hospital and General Hospital of Tianjin Medical University). External datasets (such as BraTS or TCGA-LGG/GBM) were not tested under this exact 4-condition pipeline.
   - *Impact on Manuscript:* The manuscript must explicitly limit its empirical claims to the evaluated Figshare cohort and state multi-center generalization as an open research question.
2. **Alternative Neural Network Architectures:**
   - *Missing Evidence:* All primary experiments were conducted using ResNet-50. Vision Transformers (ViT, Swin) and DenseNet architectures were not evaluated under matched $C_1$ and $C_2$ conditions.
   - *Impact on Manuscript:* The manuscript must state that the degree of spatial-context vs. seam-edge reliance in self-attention models remains to be established in future work.
3. **Acquisition Scanner Metadata:**
   - *Missing Evidence:* The public Figshare 1512427 repository does not include full DICOM headers (such as exact scanner vendor, magnetic field strength 1.5T vs 3.0T, repetition time TR, echo time TE, or slice thickness).
   - *Impact on Manuscript:* The manuscript explicitly documents this missing clinical metadata in Section 3 and the Limitations section.

---

### Category C: Author Decisions Required Prior to Submission
1. **Target Journal & Author Order:**
   - *Question for Authors:* Which journal is targeted? (Recommended: *Nature Machine Intelligence*, *Medical Image Analysis*, *IEEE Transactions on Medical Imaging*, or *Radiology: Artificial Intelligence*).
   - *Action:* Confirm author order, corresponding author details, and target word/figure limits.
2. **Data & Code Availability Hosting:**
   - *Question for Authors:* Where will the open-source reproducibility repository be publicly hosted upon acceptance? (e.g., GitHub / Zenodo repository URL).
   - *Action:* Replace placeholder URLs in the Declarations section prior to final submission.
3. **Funding & Ethics Declarations:**
   - *Question for Authors:* Provide the specific grant numbers, funding bodies, and institutional review board (IRB) exemption reference numbers for the public dataset usage.
   - *Action:* Fill in the designated declaration blocks in the manuscript.

---

### Category D: Optional Presentation Improvements
1. **Interactive Web Demonstration:**
   - An optional interactive viewer (e.g., Streamlit / Gradio) allowing users to dynamically adjust seam blending widths and view real-time difference maps could enhance paper visibility.
2. **3D Interactive Slice Fly-Through:**
   - While the dataset consists of 2D axial slices, an illustrative 3D cranial reconstruction showing the stereotactic location of pituitary vs glioma cases could be included in supplementary web materials.
