# Missing Artifacts, Dependencies & Verification Questions

**Audit Date:** 2026-10-29  
**Phase:** Phase 0 (File Ingestion & Project Inventory)  

---

## 1. Dependency & Artifact Status

| Category | Item | Status | Resolution / Notes |
|:---|:---|:---:|:---|
| **Python Libraries** | PyTorch 2.14.0, torchvision 0.29.2, timm 1.0.30 | **Present** | Installed in environment; verified via test suite |
| **Document Processing** | python-docx, pypdf, python-markdown | **Present** | Installed and functioning |
| **PDF Rendering** | Google Chrome Headless (`chrome.exe`) | **Present** | Verified at `C:\Program Files\Google\Chrome\Application\chrome.exe` |
| **Raw Datasets** | Cheng CE-T1 Dataset (`cheng/`, 3,064 .mat) | **Present** | Full dataset available locally; audited in `manifests/cheng_manifest.csv` |
| **Raw Datasets** | BRISC CE-MRI Benchmark (`brisc/`, 6,000 slices) | **Present** | Full dataset available locally; audited in `manifests/brisc_manifest.csv` |
| **Reference Draft** | `Brain_MRI_Paper_Final_Corrected_v6.docx` | **Present** | Located in `paper/` and `c:\Users\jkgga\Downloads\` |
| **Publication Figures**| Figures 1 through 10 (`figures/*.png`) | **Present** | All 10 figures rendered at 300 DPI |
| **Checkpoints** | ResNet-50 & DeiT-Small weights (`checkpoints/*.pt`)| **Present** | Preserved locally and tracked in `.gitignore` |
| **Predictions** | OOF and counterfactual logs (`predictions/*.csv`) | **Present** | 1,800 paired intervention rows available |

---

## 2. Author & Study Alignment Queries

To ensure complete alignment as we transition from Phase 0 to the subsequent audit and production phases (Phases 1 through 12), the following items are catalogued for confirmation:

### Query 1: Authorship & Institutional Affiliation
- The reference Word document ([`paper/Brain_MRI_Paper_Final_Corrected_v6.docx`](file:///c:/Users/jkgga/Downloads/brain/paper/Brain_MRI_Paper_Final_Corrected_v6.docx)) lists:
  - **Authors:** Chhotu$^1$ and Rishi Gupta$^2$
  - **Affiliations:** $^1$Manipal University Jaipur, Jaipur, Rajasthan, India; $^2$Department of Computer Science & Engineering, School of Computer Science and Engineering, Faculty of Science, Technology and Education, Manipal University Jaipur, Jaipur, Rajasthan, India.
  - **Corresponding Email:** `chhotu.2427030521@muj.manipal.edu`
- **Current Manuscript Placeholder:** Listed as `Multidisciplinary Medical Imaging & Machine Learning Research Team`.
- **Action for Phase 8/11:** When generating the final DOCX (`Brain_MRI_Research_Paper_Final.docx`) and final paper deliverables, we will adopt the authors, affiliations, and Declarations format from `Brain_MRI_Paper_Final_Corrected_v6.docx`, unless otherwise instructed by the user.

### Query 2: Scope Reconciliation
- The reference Word document documents an earlier investigation into **tile-scrambling permutations and seam artefacts** on Cheng.
- The actual completed codebase, checkpoints, prediction logs, statistical analysis, and figures implement the **sham-controlled, 5-region counterfactual intervention audit ($R_{core}, R_{immediate}, R_{outer}, R_{remote}, R_{sham}$)** across CNN and ViT models on both Cheng and BRISC.
- **Verification Rule:** As explicitly mandated by the Master Prompt (*"The actual code, datasets, experimental outputs and user-confirmed objectives determine the study"*), all numerical results, tables, figures, and statistical tests in the final paper will be strictly derived from the verified counterfactual audit pipeline, while formatting conventions, section hierarchy, equation layouts, and Declarations will mirror `Brain_MRI_Paper_Final_Corrected_v6.docx`.

---

## 3. Blocking Issues

- **None.** All code, data, models, predictions, figures, and libraries required to audit the project and produce the final publication deliverables are present, readable, and verified with 41/41 passing unit tests.

