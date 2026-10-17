# Source Provenance Report — Cheng Brain Tumor MRI Dataset

**Phase:** 1.6 — Independent Review and Alternative Evaluation Design  
**Date:** 2026-10-17  
**Purpose:** Document verifiable evidence about dataset origin, PID reliability, acquisition-level identifiers, and `cvind.mat` mapping.

---

## 1. Dataset identification

| Property | Value | Source |
|---|---|---|
| **Name** | Brain Tumor Dataset | Figshare repository [1] |
| **DOI** | 10.6084/m9.figshare.1512427 | Figshare [1] |
| **Author** | Jun Cheng, Shenzhen University | Dataset README [2], Publications [3][4] |
| **Total samples** | 3064 T1-weighted CE-MRI 2D slices | Dataset README [2] |
| **Patients** | 233 | Dataset README [2], verified from `cjdata.PID` |
| **Classes** | Meningioma (708), Glioma (1426), Pituitary (930) | Dataset README [2], verified from `cjdata.label` |
| **Archives** | 4 ZIP files of 766 `.mat` files each | Dataset README [2] |

---

## 2. Acquisition provenance

### 2.1 What is documented

From the dataset's own README (`README 2024.txt`, lines 42–45):

> All images in our dataset (T1-weighted contrast-enhanced MRI) were acquired after Gd-DTPA injection at Nanfang Hospital, Guangzhou, China and General Hospital, Tianjin Medical University, China from 2005.9 to 2010.10. The images have an in-plane resolution of 512 × 512 with pixel dimensions of 0.49 × 0.49 mm². The slice thickness is 6 mm and the slice gap is 1 mm. The Gd dose was 0.1 mmol/kg at a rate of 2 ml/s.
>
> **No further details are available due to the long passage of time.**

### 2.2 What is NOT available

| Information sought | Available? | Evidence |
|---|---|---|
| Per-slice DICOM headers | **No** | Data stored as MATLAB `.mat` files with `cjdata` struct only |
| Series UID / Study UID | **No** | Not present in `cjdata` fields |
| Scanner model or site identifier per slice | **No** | Only aggregate information in README |
| Acquisition date per slice | **No** | Only aggregate date range (2005-09 to 2010-10) |
| Volume or sequence identifier | **No** | Each `.mat` file is a standalone 2D slice |
| Mapping from slice to 3D volume | **No** | Multiple slices per patient but no explicit volume grouping |
| Slice position within volume | **No** | Slice thickness (6 mm) and gap (1 mm) reported but per-slice position not stored |
| Hospital identity per slice | **Partial** | PID naming convention (numeric vs MR-prefix) correlates with hospitals but is not documented as reliable |
| Ground truth annotation provenance | **Yes** | "Three experienced radiologists" (from Cheng et al. 2015 [3]) |

### 2.3 Two-hospital PID naming patterns

Observed in the dataset (not documented but empirically consistent):

| Pattern | Example PIDs | Likely hospital | Basis |
|---|---|---|---|
| Numeric only | 97461, 100360, 111532 | Nanfang Hospital, Guangzhou | Naming convention; not confirmed |
| MR-prefix + alphanumeric | MR024780B, MR048994B, MR051796 | General Hospital, Tianjin Medical University | Naming convention; not confirmed |

**Limitation:** This association is inferred from PID format patterns only. The dataset documentation does not explicitly map PID prefixes to institutions. The naming convention could reflect hospital database systems, but it is not independently verified.

---

## 3. Meaning and reliability of PID

### 3.1 What PID represents

The `cjdata.PID` field is described only as "patient ID" in the dataset README. No further specification is provided about:

- Whether PID is a medical record number, study accession number, or arbitrary identifier.
- Whether the same physical patient could have different PIDs (e.g., from different hospital visits, different institutions, or data-entry variations).
- Whether PID suffixes (e.g., the "B" in "MR048994B" vs a potential "MR048994A") indicate different patients, different visits, or different scan sequences.

### 3.2 PID suffix patterns

Several PIDs share a numeric root but differ in suffix:

| Root | Variants observed | Same class? |
|---|---|---|
| MR024780 | MR024780B, MR024780G | Both glioma |
| MR026175 | MR026175C, MR026175E | Both glioma |
| MR048994 | MR048994B | — |
| MR051461 | MR051461B | — |
| MR051651 | MR051651B | — |

**Open question:** Do suffixed variants represent different patients or different encounters/series for the same patient? The dataset provides no documentation on this. If "MR024780B" and "MR024780G" are the same patient, then slices across these PIDs could represent cross-patient-fold leakage despite having nominally different PIDs.

### 3.3 Multiple slices per patient

Each patient contributes between 1 and 38 slices (median 13). These are described as 2D axial slices from 3D T1-CE MRI volumes. Adjacent slices from the same volume share substantial anatomical context, which explains expected similarity within a patient. However:

- No volume identifier separates slices within a patient.
- It is unknown whether any patient was scanned in multiple sessions.
- Consecutive file numbers within the same archive folder do NOT reliably indicate consecutive slices from the same patient (the files are organized by archive, not by patient).

---

## 4. `cvind.mat` assessment

### 4.1 Structure

| Property | Value |
|---|---|
| Shape (HDF5 stored) | [1, 3064] |
| MATLAB-native shape (inferred) | [3064, 1] |
| Values | Integers 1–5 |
| Fold counts | {1: 542, 2: 679, 3: 572, 4: 628, 5: 643} |

### 4.2 Intended mapping

The community consensus and web documentation suggest that `cvind(i)` corresponds to file `i.mat` when files are sorted numerically (1.mat, 2.mat, ..., 3064.mat). This is described in the dataset's README as providing "5-fold cross-validation indices."

### 4.3 Verification status: UNVERIFIED

The project's `cvind_inspection.json` records:

> "mapping_status": "UNVERIFIED: numeric filenames provide a possible 1-based candidate order, but the supplied README does not establish that cvind position i corresponds to file i.mat. No fold assignments were mapped."

**Why unverified:**

1. The README does not explicitly state that `cvind(i)` maps to `i.mat`.
2. The community assumption relies on numeric filename ordering, but across four archive folders, the global filename ordering is ambiguous (each archive contains 766 files numbered from different starting points).
3. The `cvind.mat` fold counts (542, 679, 572, 628, 643) do not match the current patient-grouped split counts (613, 614, 611, 613, 613), confirming that `cvind` was not used for the current split and uses a different (likely slice-level, not patient-grouped) partitioning.
4. Whether `cvind` groups patients or splits at the slice level has not been independently verified from the original publications.

### 4.4 Implications

- `cvind.mat` was NOT used for any split assignment in this project.
- The current patient-grouped 5-fold split was created independently using `cjdata.PID`.
- If the original `cvind` split is slice-level rather than patient-grouped, using it would introduce patient-level leakage (slices from the same patient in different folds).
- The `cvind.mat` SHA-256 is: `b4310122ee77e08cab74332c11d77ee4c34754fbcd9d5376cbbb88f7debbd5e8`.

---

## 5. Publication provenance

### 5.1 Primary publications

1. Cheng, Jun, et al. "Enhanced Performance of Brain Tumor Classification via Tumor Region Augmentation and Partition." *PLoS ONE* 10.10 (2015). DOI: 10.1371/journal.pone.0140381 [3]

2. Cheng, Jun, et al. "Retrieval of Brain Tumors by Adaptive Spatial Pooling and Fisher Vector Representation." *PLoS ONE* 11.6 (2016). [4]

### 5.2 What the publications add

- The 2015 paper describes the tumour-region augmentation approach and uses 5-fold cross-validation.
- Tumour borders were manually delineated and verified by three experienced radiologists.
- The dataset was collected retrospectively; no prospective acquisition protocol documentation is available.
- Neither publication provides per-slice acquisition metadata, DICOM fields, or volume-level identifiers.

### 5.3 Source code

The associated GitHub repository (`https://github.com/chengjun583/brainTumorRetrieval`) provides MATLAB code for the retrieval experiments but does not contain dataset metadata beyond what is in the `.mat` files.

---

## 6. Evidence about the 236 candidate pairs

### 6.1 Can repeated exports explain any pairs?

For a pair to represent a "repeated export" (the same slice exported twice), the source file SHA-256 values or image arrays would need to be identical. **Neither condition is met for any of the 236 pairs.** All source files and all image arrays are distinct.

### 6.2 Can shared volumes explain pairs?

If two PIDs belong to the same patient, their slices could come from the same 3D volume, producing high similarity between adjacent slices. However:

- No volume identifiers exist to test this hypothesis.
- Without DICOM headers or slice-position metadata, the spatial relationship between any two slices cannot be established.
- The naming-convention clustering (PID suffix patterns, numeric vs MR-prefix) is suggestive but not conclusive.

### 6.3 Can shared protocol explain pairs?

All 3064 slices used identical acquisition parameters (512×512, T1 CE-MRI, 0.49 mm pixels, 6 mm thickness, Gd contrast). For patients with similar pathology (especially same class), slices from the same anatomical level will share:

- Skull shape and position
- Ventricle structure
- Background signal characteristics
- General tissue contrast

This protocol-driven similarity is a known source of false-positive near-duplicate detection in medical imaging datasets. The 89 cross-class pairs in the candidate set are particularly likely to be protocol-driven false positives, as different tumour types at similar anatomical levels would still share background structures.

---

## 7. Missing evidence summary

| Evidence | Status | Impact |
|---|---|---|
| Per-slice DICOM metadata | Unavailable | Cannot verify acquisition identity |
| Volume or series identifiers | Unavailable | Cannot group slices by acquisition |
| Hospital identity per slice | Inferred only | Cannot confirm institution-level patterns |
| PID suffix meaning | Undocumented | Cannot determine if suffix variants are same patient |
| `cvind.mat` mapping verification | Unverified | Cannot use for validated fold assignments |
| Original publication split details | Unverified at slice level | Cannot confirm whether original split was patient-grouped |
| Dataset author confirmation | Not obtained | Cannot resolve ambiguous cases externally |

---

## 8. Source references

| Ref | Source |
|---|---|
| [1] | Figshare: https://doi.org/10.6084/m9.figshare.1512427 |
| [2] | Dataset README (`README 2024.txt` in repository root) |
| [3] | Cheng et al., "Enhanced Performance of Brain Tumor Classification via Tumor Region Augmentation and Partition," PLoS ONE 10.10 (2015), DOI: 10.1371/journal.pone.0140381 |
| [4] | Cheng et al., "Retrieval of Brain Tumors by Adaptive Spatial Pooling and Fisher Vector Representation," PLoS ONE 11.6 (2016) |
| [5] | GitHub: https://github.com/chengjun583/brainTumorRetrieval |
| [6] | ScienceDB mirror: https://www.scidb.cn (alternative hosting) |

---

## 9. Integrity

This report was generated from the repository's existing files and publicly available documentation. No source files were modified. No patient identity inferences were made. All provenance claims cite their source. Where information is unavailable, this is explicitly stated.
