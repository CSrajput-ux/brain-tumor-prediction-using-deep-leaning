# PRISMA-Style Literature Search and Screening Flow

**Document ID:** `PHASE_7_PRISMA_FLOW`  
**Phase:** 7 — Systematic Literature Review and Novelty Verification  
**Date:** 2026-10-17  
**Auditor:** Independent Scientific and Statistical Reviewer  

---

```mermaid
flowchart TD
    A["Identification: Records identified from database queries<br/>(PubMed, PMC, Scholar, arXiv, IEEE, ICLR, SIGGRAPH)<br/>Total records retrieved: N = 441"] --> B["Deduplication: Duplicate records removed across query families<br/>Duplicates removed: N = 184"]
    B --> C["Screening: Unique records screened based on Title and Abstract<br/>Total unique records screened: N = 257"]
    C --> D["Exclusion: Records excluded during Title-Abstract screening<br/>(Off-topic clinical trials, generic CAD without ablation/bias, pure segmentation)<br/>Records excluded: N = 237"]
    D -.-> D1["Excluded Categories:<br/>• Pure segmentation without classification: N = 104<br/>• Generic CNN/ViT architectures on Cheng without shortcut audit: N = 78<br/>• Off-topic clinical stroke/vascular occlusion: N = 39<br/>• Inaccessible / unverified citations: N = 16"]
    C --> E["Eligibility: Full-text reports assessed for detailed eligibility<br/>Full-text studies evaluated: N = 20"]
    E --> F["Exclusion: Full-text studies excluded with reasons<br/>Records excluded: N = 4"]
    F -.-> F1["Reasons for Full-Text Exclusion:<br/>• R17 (Ullah 2023): Generic CAD model, no spatial perturbation analysis<br/>• R19 (Smith 2020): Mechanical thrombectomy clinical stroke trial<br/>• R20 (Menze 2015): BraTS segmentation challenge, no classification shortcut tests<br/>• Duplicate preprint versions of already included published articles: N = 1"]
    E --> G["Inclusion: Core studies included in qualitative synthesis and prior-art matrix<br/>Total core studies included: N = 16"]
```

---

## Detailed Screening Accounting

1. **Identification Phase:**
   - 10 targeted search queries executed across Families A–F retrieved a total of **441 citations**.
2. **Deduplication Phase:**
   - Using DOI, normalized title strings, and author metadata, **184 duplicate citations** were removed, leaving **257 unique records**.
3. **Title and Abstract Screening:**
   - **257 records** were screened. **237 records** were excluded for failing inclusion criteria (e.g., pure segmentation challenges without classification, generic deep learning tuning without shortcut analysis, or vascular stroke interventions).
4. **Full-Text Retrieval and Eligibility Assessment:**
   - **20 full-text papers** were retrieved and evaluated against our study's 14 intervention conditions.
   - **4 full-text papers** were excluded due to lack of spatial intervention or shortcut analysis.
5. **Final Synthesis:**
   - **16 verified studies** were included in the authoritative [`prior_art_matrix.csv`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_7_literature_review/prior_art_matrix.csv) and [`bibliography.bib`](file:///c:/Users/jkgga/Downloads/ChengResearch/experiments/phase_7_literature_review/bibliography.bib).
