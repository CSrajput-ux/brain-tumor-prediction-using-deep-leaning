# Limitations, Search Blind Spots & Unresolved Questions

**Document ID:** `LIMITATIONS_AND_UNRESOLVED_QUESTIONS`  
**Phase:** 8 — Deep Novelty Discovery, Research Redesign & Contribution Validation  
**Date:** 2026-10-17  
**Authoritative Standard:** Epistemic Transparency & Uncertainty Disclosure  

---

## 1. Search Coverage Gaps & Access Limitations

1. **Proprietary Database Inaccessibility:**  
   Scopus and Web of Science core collections were not directly queryable via automated API in this environment; search coverage relied on PubMed/MEDLINE, Europe PMC, Google Scholar, Semantic Scholar, Crossref, arXiv, and direct publisher repositories.
2. **Abstract-Only Literature:**  
   A minority of older conference workshop proceedings were accessible only via abstract and metadata records. In all such cases, papers were classified as `ABSTRACT_ONLY` in the audit log and were not used as primary pillars for novelty refutation.
3. **Terminology Fragmentation:**  
   Literature investigating model shortcut learning uses fragmented terminology across fields: computer vision often uses "spurious correlations", "inductive bias", or "background reliance"; medical imaging often uses "confounding", "institutional bias", or " Clever Hans effects"; clinical epidemiology uses "spectrum bias" or "collider stratification". While our 12 queries captured cross-disciplinary variants, papers using highly idiosyncratic phrasing may remain undiscovered.

---

## 2. In Silico Experimental Limits vs. Biological Ground Truth

1. **The In Silico Epistemic Boundary:**  
   All interventions in this project ($I_{\text{tumor}}, I_{\text{placebo}}, I_{\text{margin}}, I_{\text{C3NS}}, I_{\text{C5LP}}$) are computational manipulations performed on digital pixel matrices. As rigorously established by Castro et al. (*Nature Communications*, 2020), pixel-level ablations probe the internal associative representations of an artificial neural network; **they have zero causal authority over human tumor biology, cellular infiltration, or clinical etiology.**
2. **No Claim of Biological Absence:**  
   Demonstrating that Navier-Stokes margin inpainting restores model accuracy ($\Delta \le 0.0077$) proves that a 2D ResNet-50 does not exploit parenchymal margin textures. It does **not** prove that perilesional brain parenchyma in human patients is free of microscopic glioma infiltration or diagnostic biomarkers.

---

## 3. Methodological Confounds in Current Interventions

1. **The Tile-Seam Confound in $C_{5\text{LP}}$:**  
   As audited in Phase 6.1, permuting $16 \times 16$ distant tiles doubled Sobel gradient energy (+97.9%), introducing periodic high-frequency boundary seams across the brain slice. Because deep CNNs possess convolutional inductive biases sensitive to high-frequency periodic patterns, part of the $\Delta \approx +0.42$ collapse may reflect out-of-distribution edge noise rather than pure spatial disorientation.
2. **Whole-Brain vs. Skull-Base Confound:**  
   Because $C_{5\text{LP}}$ scrambled all distant tiles simultaneously, the disproportionate misclassification of gliomas into pituitary adenomas (56.5% error rate) cannot be specifically attributed to a "skull-base coordinate shortcut." It reflects global spatial vulnerability, but isolating specific cranial landmarks remains unresolved.
3. **2D Slices vs. 3D Volumetric Anatomy:**  
   The Cheng dataset provides 2D T1-CE slices sampled from axial, coronal, and sagittal planes without 3D volume reconstruction. 2D interventions cannot capture out-of-plane anatomical context or continuous 3D spatial geometry.

---

## 4. Architectural and Dataset Generalizability Uncertainties

1. **Single Architecture Scope:**  
   All frozen checkpoints evaluated across Phases 2–6.1 are ResNet-50 convolutional networks. Modern architectures with different inductive biases—such as Vision Transformers (ViTs) with global self-attention, Swin Transformers with shifted windows, or ConvNeXt backbones—may exhibit fundamentally different spatial sensitivity profiles.
2. **Single-Center Public Benchmark:**  
   The Cheng dataset represents a single institution’s acquisition protocol from 2005–2010. While evaluated under strict patient-disjoint splits ($S_0, S_1, S_2$), whether these exact spatial reliance proportions generalize to multi-institutional datasets (e.g., BraTS, TCGA, or modern clinical PACS archives) remains an unverified empirical question.
