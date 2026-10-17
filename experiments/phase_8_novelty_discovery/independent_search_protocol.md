# Independent Search Protocol: Novelty Discovery & Prior-Art Mapping

**Document ID:** `INDEPENDENT_SEARCH_PROTOCOL`  
**Phase:** 8 — Deep Novelty Discovery, Research Redesign & Contribution Validation  
**Date:** 2026-10-17  
**Authoritative Standard:** Systematic Multi-Area Prior-Art Discovery & Citation Verification  

---

## 1. Search Objectives & Epistemic Boundaries

Phase 7 conducted a systematic literature review centered primarily around the current experimental protocol. Phase 8 expands beyond this scope to conduct an **independent, adversarial prior-art audit** designed to:
1. Search the **underlying research problems**, rather than matching dataset keywords.
2. Probe whether competing literature already solves the core methodological questions using different terminology or in adjacent imaging domains.
3. Establish verified bibliographic records (DOIs, full-text access, venues) for all candidate prior art.
4. Prevent the project from claiming novelty on methods that are already established standards in machine learning interpretability or medical imaging validation.

---

## 2. Seven Core Research Problem Areas

The independent search systematically interrogates seven distinct methodological domains:

### Area 1 — Shortcut Learning & Confounding in Medical Imaging
- **Focus:** Models that exploit patient positioning, hospital markers, scanner hardware artifacts, or spurious background correlations instead of pathological biomarkers.
- **Key Concepts:** Shortcut learning, Clever Hans predictors, spurious correlations, out-of-distribution failure.
- **Benchmark Prior Art:** Geirhos et al. (*Nature Machine Intelligence*, 2020); DeGrave et al. (*Nature Machine Intelligence*, 2021); Zech et al. (*PLOS Medicine*, 2018).

### Area 2 — Counterfactual Medical Imaging & Inpainting Interventions
- **Focus:** Pixel-level disease removal, healthy counterfactual generation, generative inpainting, and lesion swapping.
- **Key Concepts:** Counterfactual explanations, inpainting, diffusion counterfactuals, lesion ablation, structural causal models.
- **Benchmark Prior Art:** Castro et al. (*Nature Communications*, 2020); Atad et al. (*CheXcounterfactual*, 2022); Bissoto et al. (*CVPRW*, 2019).

### Area 3 — Spatial Context, Anatomical Priors & Location Bias
- **Focus:** Models exploiting spatial coordinates, organ location, anatomical landmarks, or contextual anatomy to classify pathology.
- **Key Concepts:** Spatial priors, location bias, background reliance, anatomical coordinate shortcuts.
- **Benchmark Prior Art:** Xiao et al. (*ICLR*, 2021); Gao et al. (*MICCAI*, 2023).

### Area 4 — Intervention Validity & Artifact Confounding
- **Focus:** Distinguishing the intended effect of feature removal from artificial edge discontinuities, synthetic fill artifacts, and distribution shifts.
- **Key Concepts:** Remove and Retrain (ROAR), feature missingness baselines, boundary step artifacts, meaningful perturbations.
- **Benchmark Prior Art:** Hooker et al. (*NeurIPS*, 2019); Fong & Vedaldi (*ICCV*, 2017); Sturmfels et al. (*Distill*, 2020).

### Area 5 — Robustness, Hidden Stratification & Benchmark Leakage
- **Focus:** Patient-level data leakage, subgroup performance disparity, and benchmark contamination in medical computer vision.
- **Key Concepts:** Hidden stratification, patient-level splits, near-duplicate contamination, dataset auditing.
- **Benchmark Prior Art:** Oakden-Rayner et al. (*ACM CHIL*, 2020); Vangala et al. (*arXiv*, 2026).

### Area 6 — Reproducibility & Statistical Inference in Medical AI
- **Focus:** Clustered slice dependence, paired resampling, multiple comparisons, and standardized biomedical metric selection.
- **Key Concepts:** Problem fingerprinting, clustered bootstrap, paired permutation tests, metric pitfalls.
- **Benchmark Prior Art:** Maier-Hein, Reinke et al. (*Nature Methods*, 2024 — Metrics Reloaded); Campello et al. (*Medical Image Analysis*, 2020).

### Area 7 — Brain Tumour MRI Benchmark Prior Art
- **Focus:** Studies utilizing the Cheng Figshare 1512427 dataset or equivalent public brain tumor MRI benchmarks.
- **Key Concepts:** Concentric ring dilation, capsule networks, deep feature transfer, random vs patient splitting.
- **Benchmark Prior Art:** Cheng et al. (*PLOS ONE*, 2015); Afshar et al. (*IEEE ICIP*, 2018); Paul et al. (*IEEE Access*, 2017).

---

## 3. Information Sources & Access Modalities

Searches were executed across:
1. **PubMed / MEDLINE & Europe PMC:** Biomedical literature, peer-reviewed clinical imaging studies.
2. **Google Scholar & Semantic Scholar:** Comprehensive cross-disciplinary citation graphs and forward tracking.
3. **Crossref API:** Metadata and DOI verification.
4. **arXiv / OpenReview:** Recent preprints in machine learning interpretability and benchmark audits.
5. **Publisher Repositories:** Nature Portfolio, IEEE Xplore, PLOS, ACM Digital Library.

---

## 4. Screening, Deduplication & Quality Rules

1. **Exact Bibliographic Verification:** Every paper cited must possess a verified DOI or permanent stable URL. Titles, authors, publication year, and venues are cross-checked against publisher landing pages.
2. **Preprint Deduplication:** When a study exists as both an arXiv preprint and a peer-reviewed journal/conference article, the peer-reviewed version is authoritative; they are never counted as two independent studies.
3. **Full-Text vs. Abstract-Only:** Full text is accessed wherever available. If inaccessible behind a paywall, it is explicitly flagged as `ABSTRACT_ONLY` or `INACCESSIBLE`.
4. **Substantive Difference Test:** A paper is considered competing prior art if it shares the core experimental mechanism (e.g., masking lesion vs background, smoothing boundary edges, or testing patient leakage), even if it uses different clinical jargon.
