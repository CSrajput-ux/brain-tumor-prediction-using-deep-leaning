# Novelty Stress Test & Adversarial Audit

**Document ID:** `NOVELTY_STRESS_TEST`  
**Phase:** 8 — Deep Novelty Discovery, Research Redesign & Contribution Validation  
**Date:** 2026-10-17  
**Authoritative Standard:** Adversarial Peer Review & Falsification Audit  

---

## 1. Adversarial Methodology

To ensure that proposed contributions survive rigorous peer review and avoid superficial novelty claims, each candidate research direction is interrogated from the perspective of an expert, skeptical reviewer in medical imaging machine learning (e.g., senior reviewers for *Nature Machine Intelligence*, *Medical Image Analysis*, or *IEEE TMI*).

---

## 2. Adversarial Stress-Testing by Candidate Direction

### Direction A: Intervention-Validity Measurement (Boundary Step-Edge Confound Audit)
- **Hardest Question:** *"Hooker et al. (NeurIPS 2019) already established with ROAR that masking features on frozen models causes distribution shift, and Fong & Vedaldi (ICCV 2017) already showed that naive zero-filling creates artificial step-edge artifacts. Isn't this just restating Fong's point on a medical dataset?"*
- **The Defense:** 
  1. Fong & Vedaldi used smoothing as an optimization heuristic for generating pixel-level saliency heatmaps on ImageNet. They did not measure hypothesis-driven concentric margin rings or provide matched anatomical placebo controls.
  2. Hooker's ROAR requires retraining dozens of neural networks from scratch across every ablation threshold, which is computationally prohibitive and changes the underlying decision manifold.
  3. Direction A establishes that in clinical deep learning, **apparent reliance on parenchymal penumbra in zero-fill ablations ($\Delta \approx +0.025$) is an artifact of artificial boundary step-edge gradients ($236.7$), and completely vanishes ($\Delta < 0.008$) under PDE inpainting without altering the lesion core.** This is an actionable, testable validation principle for medical XAI.
- **Skeptical Reviewer Demand:** Quantitative proof that inpainting does not introduce its own confounding distribution shift (e.g., texture blurring) that happens to compensate for lost margin features.
- **Verdict:** **HIGHLY DEFENSIBLE**.

---

### Direction B: Orthogonal Perturbation Triangulation
- **Hardest Question:** *"Benchmarking a model against multiple corruptions is the standard paradigm of Hendrycks & Dietterich (ImageNet-C, ICLR 2019). Why is applying four perturbations to brain MRI novel?"*
- **The Defense:** ImageNet-C evaluated generic image robustness against environmental noise (fog, snow, blur). Direction B specifically tests whether the classifier's dependency on remote anatomical context is invariant across geometrically distinct operators.
- **The Weakness:** Without a clear theoretical mechanism unifying the operators, this direction risks degenerating into an exploratory benchmark exercise ("we tried 6 filters and here are the accuracy drops").
- **Verdict:** **VIABLE BUT INCREMENTAL**.

---

### Direction C: Anatomical Compartment Subgroup Heterogeneity
- **Hardest Question:** *"Isn't reporting results by tumor class (glioma vs meningioma vs pituitary) simply standard error analysis rather than a methodological contribution?"*
- **The Defense:** Prior medical shortcut literature (e.g., DeGrave 2021) reports aggregate performance drops. Direction C uncovers a fundamental neuroanatomical inductive bias: **intra-axial tumors (gliomas) and extra-axial tumors (pituitary adenomas) exhibit radically asymmetric failure dynamics under spatial disruption.** When cranial context is scrambled, ResNet-50 systematically inverts gliomas into pituitary predictions (56.5% error rate across 83 patients) because it relies on cranial coordinates to resolve ambiguity.
- **The Weakness:** It remains primarily an empirical characterization of this specific ResNet-50 checkpoint rather than a new general machine learning method.
- **Verdict:** **STRONG SCIENTIFIC EXPLANATION, MODERATE METHODOLOGICAL NOVELTY**.

---

### Direction D: Decoupling Spatial Layout from High-Frequency Seam Corruption
- **Hardest Question:** *"In Phase 6, you celebrated the $C_{5\text{LP}}$ tile-scrambling result ($\Delta \approx +0.42$) as definitive proof that the model uses cranial landmark layout. But Phase 6.1 showed that tile scrambling doubled the Sobel high-frequency gradient energy (+97.9%). Isn't your headline finding confounded by checkerboard edge noise?"*
- **The Defense:** **This is precisely the research gap.** Existing literature in computer vision and medical imaging routinely scrambles or permutes image tiles without accounting for the high-frequency grid seams introduced at tile borders. Direction D proposes the first **frequency-matched, seamless spatial permutation framework** (e.g., using multiresolution wavelet shuffling or seamless Poisson boundary reconstruction) that disrupts macroscopic anatomical layout while holding both radiometric statistics (mean/variance) AND high-frequency edge energy strictly invariant.
- **Skeptical Reviewer Demand:** Demonstrate that when grid seams are eliminated and high-frequency edge energy matches the original baseline, the classifier still suffers a substantial diagnostic drop ($\Delta > 0.15$), proving true anatomical layout reliance.
- **What if the hypothesis fails? (Valuable Negative Result):** If the performance collapse disappears when seams are removed, it would yield a sensational, paradigm-shifting finding: **deep brain MRI classifiers do NOT rely on cranial landmark topography at all; their apparent collapse under scrambling was entirely driven by sensitivity to high-frequency edge noise!** Either outcome produces a major, publication-grade contribution.
- **Verdict:** **STRONGEST CANDIDATE — MAXIMUM SCIENTIFIC VALUE & FALSIFIABILITY**.

---

### Direction E: Cross-Cohort Generalization on External Datasets (BraTS / TCGA)
- **Hardest Question:** *"Why haven't you tested your conclusions on an independent hospital cohort?"*
- **The Defense:** Cross-dataset validation is the gold standard for clinical generalizability.
- **The Reality Check:**
  1. BraTS datasets are exclusively high-grade and low-grade gliomas with 3D multi-modal volumes (T1, T1-CE, T2, FLAIR). They contain zero pituitary adenomas and zero meningiomas. Cross-testing a 3-class model directly on BraTS is impossible without retraining or discarding classes.
  2. Ingesting, de-identifying, slice-extracting, and skull-stripping external TCGA datasets cannot be completed within the current resource envelope.
- **Verdict:** **REJECTED DUE TO FEASIBILITY AND LABEL INCOMPATIBILITY CONSTRAINTS**.

---

### Direction F: Formalized Decision Framework for Calibrated Medical XAI Audits
- **Hardest Question:** *"Isn't this just repackaging good experimental design into a workflow paper?"*
- **The Defense:** Most published medical imaging papers still claim "model interpretability" using uncalibrated heatmaps or naive masking. Providing a pre-registered, open-source decision protocol that integrates matched placebos, PDE inpainting, and cluster bootstrap provides immediate practical value.
- **The Weakness:** Reviewers frequently dismiss protocol/framework papers unless accompanied by a decisive new empirical discovery.
- **Verdict:** **VALUABLE AS A SECONDARY/METHODOLOGICAL SYNTHESIS, BUT STRONGEST WHEN COUPLED WITH DIRECTION D**.

---

## 3. Summary of Novelty Stress-Test Rankings

1. **Top Primary Direction:** **Direction D (Decoupling Spatial Layout from Seam Noise)** — Rigorously resolves the deepest methodological flaw of Phase 6; produces high-impact conclusions whether the hypothesis holds or is falsified.
2. **Top Backup Direction:** **Direction A (Intervention-Validity Measurement)** — Provides the mathematical and empirical foundation proving that naive zero-filling creates artificial edge artifacts, substantiated by our Phase 6 Navier-Stokes inpainting evidence.
3. **Synergistic Integration:** Directions A and D naturally unify into a coherent, groundbreaking manuscript: **"Quantifying Anatomical Context and Artifact Sensitivity in Brain MRI Deep Classifiers: Decoupling True Evidence Reliance from Boundary and Seam Confounds."**
