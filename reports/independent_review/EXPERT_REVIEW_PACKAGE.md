# Expert Review Package — Cross-fold Near-Duplicate Candidate Assessment

**Phase:** 1.6 — Independent Review and Alternative Evaluation Design  
**Date prepared:** 2026-10-17  
**Status:** Ready for independent human review  
**Decision before review:** NO-GO (no model has been trained)

---

## 1. Purpose

This package provides an independent reviewer with all available automated evidence about 236 cross-patient/cross-fold near-duplicate candidate pairs identified in the Cheng Brain Tumor MRI dataset (3064 T1-weighted contrast-enhanced slices from 233 patients). The reviewer is asked to evaluate whether each candidate pair represents a genuine data-integrity risk (same patient, same acquisition, or duplicated data across evaluation folds) or a false positive from normal anatomical similarity.

**No pair has been pre-labeled as a confirmed duplicate.** All automated similarity measures are presented as screening evidence, not as identity proof. The reviewer's independent judgment is the authoritative record.

---

## 2. Dataset context

| Property | Value |
|---|---|
| Total slices | 3064 |
| Unique patients (by `cjdata.PID`) | 233 |
| Tumour classes | meningioma (708), glioma (1426), pituitary (930) |
| Evaluation protocol | 5-fold patient-grouped cross-validation |
| Patient overlap across folds | 0 (verified) |
| Slices per patient | 1–38 (median 13) |
| Source institutions | Nanfang Hospital, Guangzhou; General Hospital, Tianjin Medical University |
| Acquisition period | 2005-09 to 2010-10 |
| Resolution | 512×512, 0.49×0.49 mm², slice thickness 6 mm, gap 1 mm |

---

## 3. Candidate pair summary

| Statistic | Value |
|---|---|
| Total near-duplicate candidate pairs (pHash Hamming ≤ 4/64) | 1254 |
| Cross-patient AND cross-fold candidates | 236 |
| Pairs with SSIM ≥ 0.80 | 2 |
| Pairs with SSIM ≥ 0.75 | 27 |
| Pairs with SSIM ≥ 0.70 | 61 |
| Pairs with SSIM ≥ 0.60 | 119 |
| pHash distance = 2 | 19 |
| pHash distance = 4 | 217 |
| Source file SHA-256 equal pairs | 0 |
| Exact image-array equal pairs | 0 |
| Maximum Pearson correlation (original arrays) | 0.8816 |
| Maximum stored pixel-equal fraction | 0.3253 |
| Unique patient IDs involved | 123 |
| Unique sample IDs involved | 291 |
| Same-class pairs | 147 |
| Different-class pairs | 89 |

---

## 4. Similarity methodology

| Measure | Specification |
|---|---|
| **SSIM** | Computed on prepared per-image min-max normalized uint8 grayscale PNGs; no geometric registration; `scipy.ndimage.gaussian_filter` sigma=1.5, truncate=4.0 (13×13 support), reflect boundary mode; C₁=(0.01×255)², C₂=(0.03×255)²; global mean SSIM |
| **pHash** | Perceptual hash Hamming distance; candidate threshold ≤ 4/64 bits |
| **Pearson correlation** | Computed on original `cjdata.image` int16 arrays flattened to 1-D |
| **Pixel equality** | Fraction of identical pixel values in stored image arrays |
| **Source file SHA-256** | Full-file SHA-256 of original `.mat` files |
| **Array SHA-256** | dtype/shape/pixel-aware SHA-256 of the `cjdata.image` array |

**What these measures establish:** Perceptual and statistical similarity between exported images or source arrays. They can identify identical file copies (SHA-256 equality) and quantify visual resemblance.

**What these measures do NOT establish:** Patient identity, acquisition identity, whether two slices come from the same MRI volume, whether similarity is due to shared scanner/protocol/anatomy rather than shared identity, or whether the dataset's PID field is incorrect.

---

## 5. Priority review tiers

### Tier 1: SSIM ≥ 0.80 (2 pairs — highest priority)

#### Pair 1 (SSIM = 0.810)

| Field | Sample A | Sample B |
|---|---|---|
| **Sample ID** | `cheng_7e75...2a7` | `cheng_9984...232` |
| **Source MAT** | `brainTumorDataPublic_1533-2298/1892.mat` | `brainTumorDataPublic_1533-2298/2043.mat` |
| **Patient ID** | MR048994B | MR051796 |
| **Class** | glioma | glioma |
| **Fold** | fold_2 | fold_4 |
| **Original shape** | [512, 512] | [512, 512] |
| **Original dtype** | int16 | int16 |
| **Intensity range** | [0, 5408] | [0, 5603] |
| **pHash distance** | 2 | |
| **Pearson correlation** | 0.8804 | |
| **Pixel equal fraction** | 0.2748 | |
| **Mean abs. difference** | 172.4 | |
| **Max abs. difference** | 5260 | |
| **Source file SHA-256 equal** | False | |
| **Stored array equal** | False | |

**Automated interpretation:** Highest SSIM in the candidate set. Different source files, different arrays, similar intensity ranges. The two PIDs share the same hospital naming pattern (MR-prefix). Same class, different folds. Could represent adjacent slices from the same patient under different IDs, slices from different patients with similar pathology, or a coincidental match from shared acquisition parameters.

**Contact sheet:** `reports/duplicate_investigation/contact_sheets/ssim_ge_0_80_page_001.png`

---

#### Pair 2 (SSIM = 0.803)

| Field | Sample A | Sample B |
|---|---|---|
| **Sample ID** | `cheng_4332...b07` | `cheng_2ad2...3ca` |
| **Source MAT** | `brainTumorDataPublic_1533-2298/1989.mat` | `brainTumorDataPublic_1533-2298/2240.mat` |
| **Patient ID** | MR026175C | MR024780B |
| **Class** | glioma | glioma |
| **Fold** | fold_4 | fold_1 |
| **Original shape** | [512, 512] | [512, 512] |
| **Original dtype** | int16 | int16 |
| **Intensity range** | [0, 4372] | [0, 4061] |
| **pHash distance** | 4 | |
| **Pearson correlation** | 0.8318 | |
| **Pixel equal fraction** | 0.3207 | |
| **Mean abs. difference** | 122.0 | |
| **Max abs. difference** | 3316 | |
| **Source file SHA-256 equal** | False | |
| **Stored array equal** | False | |

**Automated interpretation:** Second-highest SSIM. Both from the same archive folder, different source files and arrays. Similar but not identical intensity ranges. Same class, different folds. PID MR024780B appears in 18 pair-appearances total across the candidate set, suggesting this patient's slices are frequently matched.

**Contact sheet:** `reports/duplicate_investigation/contact_sheets/ssim_ge_0_80_page_001.png`

---

### Tier 2: SSIM 0.75–0.80 with strongest combined evidence (5 representative pairs)

#### Pair 3 (SSIM = 0.797)

| Field | Sample A | Sample B |
|---|---|---|
| **Source MAT** | `1920.mat` | `2222.mat` |
| **Patient ID** | MR049453 | MR029209G |
| **Class** | glioma | glioma |
| **Fold** | fold_2 | fold_4 |
| **pHash distance** | 4 |
| **Pearson correlation** | 0.7984 |
| **Intensity range A** | [0, 8383] |
| **Intensity range B** | [0, 7708] |
| **Source file equal** | False |
| **Array equal** | False |

#### Pair 4 (SSIM = 0.794)

| Field | Sample A | Sample B |
|---|---|---|
| **Source MAT** | `1890.mat` | `2015.mat` |
| **Patient ID** | MR048994B | MR051461B |
| **Class** | glioma | glioma |
| **Fold** | fold_2 | fold_4 |
| **pHash distance** | 4 |
| **Pearson correlation** | 0.8201 |
| **Intensity range A** | [0, 5214] |
| **Intensity range B** | [0, 5413] |
| **Source file equal** | False |
| **Array equal** | False |

**Note:** PID MR048994B appears in 24 pair-appearances — the most frequent PID in the candidate set. This patient has many slices (suggesting a large tumour volume or multiple acquisitions).

#### Pair 5 (SSIM = 0.788)

| Field | Sample A | Sample B |
|---|---|---|
| **Source MAT** | `132.mat` | `200.mat` |
| **Patient ID** | 111532 | 99089 |
| **Class** | meningioma | meningioma |
| **Fold** | fold_1 | fold_5 |
| **pHash distance** | 4 |
| **Pearson correlation** | 0.8803 |
| **Intensity range A** | [0, 3014] |
| **Intensity range B** | [0, 2150] |
| **Source file equal** | False |
| **Array equal** | False |

**Note:** These PIDs use numeric format (suggesting Nanfang Hospital), while MR-prefixed PIDs suggest Tianjin Medical University. Different naming conventions may indicate different institutions.

#### Pair 6 (SSIM = 0.786)

| Field | Sample A | Sample B |
|---|---|---|
| **Source MAT** | `132.mat` | `159.mat` |
| **Patient ID** | 111532 | 113435 |
| **Class** | meningioma | meningioma |
| **Fold** | fold_1 | fold_3 |
| **pHash distance** | 2 |
| **Pearson correlation** | 0.8815 |
| **Intensity range A** | [0, 3014] |
| **Intensity range B** | [0, 3015] |
| **Source file equal** | False |
| **Array equal** | False |

**Note:** Nearly identical intensity ranges (3014 vs 3015). PID 111532 appears in multiple pairs with different counterparts. The intensity similarity is notable but does not alone prove shared acquisition.

#### Pair 7 (SSIM = 0.784)

| Field | Sample A | Sample B |
|---|---|---|
| **Source MAT** | `1891.mat` | `2043.mat` |
| **Patient ID** | MR048994B | MR051796 |
| **Class** | glioma | glioma |
| **Fold** | fold_2 | fold_4 |
| **pHash distance** | 2 |
| **Pearson correlation** | 0.8656 |
| **Source file equal** | False |
| **Array equal** | False |

**Note:** Same PID pair as Pair 1 (MR048994B vs MR051796), different slices. Multiple pairs from the same two patients appearing together strengthens the possibility of a relationship but does not confirm it.

---

### Tier 3: Moderate-similarity controls (SSIM 0.60–0.70)

58 pairs fall in SSIM range 0.60–0.70. These represent the typical level of similarity between brain MRI slices from different patients acquired with the same protocol. At this level, anatomical similarity from shared acquisition parameters (512×512, T1 CE-MRI, similar slice positioning) is expected.

**Representative examples are documented in contact sheets:** `ssim_0_70_to_0_80_page_*.png` and `ssim_lt_0_70_page_*.png`.

---

### Tier 4: Low-similarity controls (SSIM < 0.50)

12 pairs from the lowest-SSIM stratum are provided as controls in `low_similarity_controls_page_*.png`. These demonstrate what dissimilar brain MRI pairs look like under the same similarity measures.

---

## 6. Recurring patient patterns

The following PIDs appear most frequently across candidate pairs:

| Patient ID | Pair appearances | Hospital pattern |
|---|---|---|
| MR048994B | 24 | Tianjin (MR prefix) |
| MR024780G | 18 | Tianjin |
| MR049453 | 14 | Tianjin |
| 97461 | 14 | Nanfang (numeric) |
| MR034694 | 13 | Tianjin |
| MR051796 | 9 | Tianjin |
| 107747 | 9 | Nanfang |
| MR051651B | 8 | Tianjin |
| 104281 | 8 | Nanfang |
| MR037458B | 8 | Tianjin |

Frequent appearance may reflect: (a) patients with many slices producing more pairwise candidates, (b) shared acquisition characteristics across similar pathology, or (c) genuine relatedness that the PID field does not capture. The automated evidence cannot distinguish these explanations.

---

## 7. Cross-class pairs

89 of 236 candidate pairs involve samples with **different class labels**. This is an important consideration: if two slices have genuinely different pathologies (meningioma vs glioma), high visual similarity would be unusual for the tumour region but plausible for the surrounding brain anatomy. This could indicate that the pHash-based screening is capturing background/skull similarity rather than tumour-region similarity.

| Class pair | Count |
|---|---|
| glioma–glioma | 92 |
| meningioma–glioma | 78 |
| pituitary–pituitary | 34 |
| meningioma–meningioma | 21 |
| pituitary–glioma | 6 |
| meningioma–pituitary | 3 |
| glioma–pituitary | 2 |

---

## 8. Reference materials

All contact sheets are in: `reports/duplicate_investigation/contact_sheets/`  
Contact sheet index: `reports/duplicate_investigation/contact_sheets/contact_sheet_index.csv`  
Full pair-level evidence: `reports/duplicate_investigation/duplicate_pair_review.csv`  
Machine-readable evidence summary: `reports/duplicate_investigation/automated_evidence.json`  
Prior investigation report: `reports/duplicate_investigation/DUPLICATE_INVESTIGATION_REPORT.md`  
Prior recommendations: `reports/duplicate_investigation/resolution_recommendations.md`  
Gate report: `experiments/baseline/gate_report.json`  
Pre-training gate NO-GO: `experiments/baseline/NO_GO_REPORT.md`

---

## 9. What the automated evidence does and does not establish

### Established

- No two candidate source `.mat` files are byte-identical (SHA-256 confirms).
- No two candidate image arrays are element-identical.
- All 236 pairs involve different patient IDs in different evaluation folds.
- SSIM and pHash capture visual similarity; the distribution is continuous with no sharp boundary separating "duplicates" from "non-duplicates."
- Patient IDs, class labels, and fold assignments in the prepared data match the source `cjdata` fields exactly.

### NOT established

- Whether any pair represents the same patient under different PIDs.
- Whether any pair comes from the same MRI acquisition or volume.
- Whether similarity is due to shared identity, shared anatomy, shared scanner protocol, or coincidence.
- Whether the dataset's PID field is reliable as a unique patient identifier or whether patients were scanned at multiple sessions.
- Whether `cvind.mat` position mapping corresponds to filesystem ordering.
- Whether SSIM ≥ 0.80 is an appropriate threshold for identifying leakage in this imaging modality.

---

## 10. Reviewer instructions

Use the accompanying `reviewer_decision_template.csv` to record your assessment. For each pair, fill in:

| Field | Description |
|---|---|
| `reviewer_id` | Your unique identifier |
| `review_date` | Date of review (YYYY-MM-DD) |
| `review_decision` | One of: `confirmed_duplicate`, `probable_same_patient`, `possible_related_slices`, `visually_similar_not_related`, `insufficient_evidence`, `not_a_duplicate` |
| `evidence_notes` | Specific observations supporting your decision |
| `confidence` | `high`, `medium`, or `low` |
| `follow_up_required` | `yes` or `no` — whether additional evidence is needed |

**Do not** base your decision solely on SSIM or any single metric. Consider:
1. Do the images show the same anatomical structures in the same spatial arrangement?
2. Are tumour characteristics (location, shape, size, contrast enhancement) consistent with the same lesion?
3. Do the source paths, patient IDs, intensity ranges, and acquisition patterns suggest a common origin?
4. Could the similarity be explained by shared scanner protocol and normal anatomical variation?
5. If the classes differ, is the visual similarity confined to non-tumour regions?

**Explicitly flag** any pair where you believe an independent second reviewer should also examine the evidence.

---

## 11. Integrity

| Artifact | SHA-256 |
|---|---|
| `prepared_full_run/metadata.csv` | `c15f35073d4f03e6a91b13b9ff2d9076b5ece0dce7a8b0f2613d376886fc27f4` |
| `prepared_full_run/patient_splits.csv` | `c45e0eea02f00f7c3d80f20d3f4764f758d8471300a81ff4d25ea31c2387d622` |
| `reports/duplicate_investigation/duplicate_pair_review.csv` | `a06e79bc379abee2968f49cd57f486fc9ba738fc209916112a04515d71b3fb09` |
| `experiments/baseline/gate_report.json` | `42ce324232c8b559ae27c230c533fcb562e9eff059b0c546c7d48bad381a43ff` |
| `prepared_full_run/manifest.json` | `4ef492323314630596da8aef0871c5e3708413aec5fe6e3796aef53b8741ca05` |

No source MAT files, prepared images, masks, metadata, labels, patient IDs, or fold assignments were modified, deleted, relabeled, merged, or reassigned during the preparation of this review package.
