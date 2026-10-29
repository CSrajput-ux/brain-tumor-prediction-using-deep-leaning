# Template & Reference Document Audit: `Brain_MRI_Paper_Final_Corrected_v6.docx`

**Audit Date:** 2026-10-29  
**Reference Document:** [`paper/Brain_MRI_Paper_Final_Corrected_v6.docx`](file:///c:/Users/jkgga/Downloads/brain/paper/Brain_MRI_Paper_Final_Corrected_v6.docx)  
**File Size:** 4,715,135 bytes (4.72 MB)  
**Paragraph Count:** 265  
**Table Count:** 13  

---

## 1. Document Overview & Metadata

- **Title in Reference:** *“Seam Artefacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Audit Across Deep Architectures”*
- **Authors:** Chhotu$^1$ and Rishi Gupta$^2$
- **Affiliation:**
  - $^1$Manipal University Jaipur, Jaipur, Rajasthan, India
  - $^2$Department of Computer Science & Engineering, School of Computer Science and Engineering, Faculty of Science, Technology and Education, Manipal University Jaipur, Jaipur, Rajasthan, India
- **Corresponding Author:** Chhotu (`chhotu.2427030521@muj.manipal.edu`)
- **Key Sections in Reference:**
  1. Title & Authorship Block
  2. Abstract (Structured narrative: Background, Problem, Interventions, Findings)
  3. Keywords
  4. Nomenclature (Formal acronym and mathematical notation glossary)
  5. Section 1: Introduction (Motivation, Clever Hans problem, tile scrambling, contribution summary)
  6. Section 2: Related Work (2.1 Shortcut learning, 2.2 Spatial interventions & attribution, 2.3 Brain tumour MRI & dataset audits, 2.4 Research gap)
  7. Section 3: Methods (3.1 Dataset, 3.2 Evaluation scenarios & patient grouping, 3.3 Model & training configuration, 3.4 Protected-zone invariant, 3.5 Tile partition, 3.6 Input conditions, 3.7 Image diagnostics, 3.8 Out-of-fold inference, 3.9 Metrics & statistical inference, 3.10 Algorithm, 3.11 Software & reproducibility)
  8. Section 4: Experimental Setup and Results (4.1 Protocol & integrity checks, 4.2 Baseline performance, 4.3 Intervention effects, 4.4 Paired contrasts & multiplicity, 4.5 Class-level error structure, 4.6 Image diagnostics, 4.7 Stability across folds, 4.8 Summary of results, 4.9 Evaluation of hypotheses)
  9. Section 5: Discussion (5.1 Principal findings, 5.2 Seams vs rearrangement, 5.3 Connection to shortcut learning, 5.4 Alternative explanations, 5.5 Implications for evaluation, 5.6 Recommended follow-up controls)
  10. Section 6: Limitations
  11. Section 7: Conclusion
  12. Declarations (Funding, Conflicts of interest, Ethics approval, Consent, Data availability, Code availability, Authors' contributions)
  13. References (Formal Vancouver / MedIA citation format)
  14. Appendix A: Fold-level metrics and confusion matrices

---

## 2. Typographic & Layout Conventions Extracted

- **Typography:**
  - Primary Font: Times New Roman
  - Title: 16–18 pt, Bold
  - Author Names: 12 pt, Bold
  - Affiliations: 10.5 pt, Regular / Italic
  - Headings 1: 14 pt, Bold, numbered with Arabic numerals (`1  Introduction`)
  - Headings 2: 12 pt, Bold, numbered with decimal levels (`2.1  Shortcut learning...`)
  - Body Text: 11 pt, 1.15–1.5 line spacing, 6 pt space after paragraph
  - Abstract & Keywords: 10 pt
- **Nomenclature Structure:** Two-column formatted block listing Acronyms followed by mathematical notation.
- **Table Formatting:** Formal academic tables (horizontal rules above and below header, bottom border, no vertical rules, centered numerical columns).
- **Equation Formatting:** Centered mathematical expressions with right-aligned numbering `(1)`, `(2)`, etc.
- **Declarations:** Seven standardized sub-headings (Funding, Conflicts of Interest, Ethics Approval, Consent to Participate/Publish, Availability of Data and Materials, Code Availability, Authors' Contributions).

---

## 3. Methodological Distinctions & Mapping

| Element | Reference Draft (`v6.docx`) | Current Implemented Study (Source of Truth) | Final Paper Execution Strategy |
|:---|:---|:---|:---|
| **Intervention Concept** | Tile scrambling ($2 \times 2, 4 \times 4$) with artificial grid seams | 5-region anatomical counterfactual ablation ($R_{\text{core}}, R_{\text{immediate}}, R_{\text{outer}}, R_{\text{remote}}, R_{\text{sham}}$) | Present the 5-region counterfactual audit as the primary study; reference seam artifacts as historical motivation. |
| **Datasets** | Cheng dataset only ($N=3,064$) | Cheng dataset ($N=3,064$) + BRISC dataset ($N=6,000$, multi-plane) | Include full dual-dataset audit, plane stratification, and 10.1% duplicate leakage discovery. |
| **Model Architectures** | CNNs (ResNet) | ResNet-50 (CNN) vs DeiT-Small/16 (Vision Transformer) | Report inductive bias comparison (global attention vs local convolutions). |
| **Perturbation Control** | Grid line seam overlay & boundary smoothing | Contralateral sham control ($R_{\text{sham}}$) + Telea PDE vs Gaussian texture fill | Maintain strict non-target invariance ($0.00 \times 10^0$ outside mask). |
| **Statistical Methods** | Paired differences, bootstrap CIs | Paired Wilcoxon signed-rank tests, Cohen's $d_z$, ECE calibration, Brier score | Full biostatistical inference with exact $p$-values and effect sizes. |
| **Author Details** | Chhotu & Rishi Gupta (Manipal University Jaipur) | Placeholder in earlier markdown drafts | **Adopt Chhotu & Rishi Gupta (Manipal University Jaipur)** as confirmed primary authors. |

---

## 4. Retained & Adapted Presentation Elements

1. The exact title structure, author affiliation, email contact, and Declarations format are retained.
2. The rigorous mathematical nomenclature section is adapted to define our five anatomical regions ($R_{\text{core}}, R_{\text{immediate}}, R_{\text{outer}}, R_{\text{remote}}, R_{\text{sham}}$), causal sensitivity estimands ($\Delta_r, \tau_r, F_r$), and calibration metrics ($\text{ECE}, \text{Brier}$).
3. The 7-section numbered hierarchy (Introduction, Related Work, Methods, Results, Discussion, Limitations, Conclusion) is preserved.
4. All numerical figures, tables, and claims are populated strictly from our audited result ledger.

