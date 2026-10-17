# Cheng Brain Tumor Dataset Audit

**Validation status: WARN**

## Verified findings

- Extracted archive-folder counts: brainTumorDataPublic_1-766=766, brainTumorDataPublic_1533-2298=766, brainTumorDataPublic_2299-3064=766, brainTumorDataPublic_767-1532=766.
- Discovered `.mat` sample files: 3064; metadata records: 3064.
- Successfully processed: 3064; failed processing: 0.
- Class counts (reference counts are comparisons only, not enforced): `{'meningioma': 708, 'glioma': 1426, 'pituitary': 930}`.
- Unique non-missing patient IDs: 233; missing patient IDs: 0.
- Slices per identified patient: min=1, median=13.0, max=38.
- Tumour masks missing: 0; available but invalid/empty/misaligned: 0; image-mask size mismatches: 0.
- Valid non-empty binary masks: 3064; empty masks: 0; median tumour area fraction among dimension-matched masks: 0.01285552978515625.
- Duplicate source SHA-256 copies: 0; duplicate filename groups: 0; possible near-duplicate image pairs (pHash distance <=4): 1254.
- Among those perceptual-hash candidates: 960 pairs are within one PID, 294 cross PIDs; 1148 share a class and 106 cross class labels. These candidates are not treated as confirmed duplicate files.
- Identical raw image arrays with conflicting class labels: 0; PIDs containing multiple class labels: 0.
- Missing/unreadable generated output paths: 0.
- Every discovered original sample accounted for: True.

### Patient-grouped folds

- Patient overlap: **PASS**.
| Fold | Patients | Slices | Class counts |
|---|---:|---:|---|
| fold_1 | 47 | 645 | `{'meningioma': 156, 'pituitary': 204, 'glioma': 285}` |
| fold_2 | 47 | 536 | `{'meningioma': 136, 'pituitary': 190, 'glioma': 210}` |
| fold_3 | 46 | 602 | `{'meningioma': 154, 'pituitary': 179, 'glioma': 269}` |
| fold_4 | 46 | 685 | `{'meningioma': 132, 'pituitary': 215, 'glioma': 338}` |
| fold_5 | 47 | 596 | `{'meningioma': 130, 'glioma': 324, 'pituitary': 142}` |

### Processing failures

- None.

### Mask issues

- None.

## `cvind.mat`

- Stored HDF5 shape: `[1, 3064]`; inferred MATLAB-native shape: `[3064, 1]`.
- Assignment count and fold counts: 3064, `{'1': 542, '2': 679, '3': 572, '4': 628, '5': 643}`.
- File-order mapping verified: **False**. UNVERIFIED: numeric filenames provide a possible 1-based candidate order, but the supplied README does not establish that cvind position i corresponds to file i.mat. No fold assignments were mapped.
- Fold unit: Unverified; cannot establish slice-level versus patient-level grouping from cvind alone.
- See `reports/cvind_inspection.md` for the detailed structural report.

## Assumptions and unresolved issues

- This audit treats each `.mat` file under the four extracted archive folders as one candidate sample. A file is a successful sample only when `cjdata.label` is recognized and a finite 2-D image is readable.
- Image PNGs are per-image min-max scaled to uint8 for convenient model input. These are display/model exports, not original intensities; exact arrays and dtypes are retained in compressed NPZ files.
- The provided README describes `cvind` as five-fold indices but does not define the order mapping or patient grouping. Its mapping therefore remains unverified.
- Perceptual-hash matches are candidates for review, not proof of duplicates; no data were removed.
- The dataset does not include voxel spacing in each sample struct here; do not infer physical tumour area from pixel area alone.
- Mask overlay/masking interventions can introduce boundary and distribution artifacts. Prediction changes alone do not establish causal tumour reliance; surrounding anatomy may be clinically meaningful.

## Fatal validation issues

- None.

## Reproducibility notes

- Original input MAT files are read-only inputs and were not modified.
- Stable sample IDs derive from the source-relative path; source SHA-256 separately identifies exact source bytes.
- The preparation manifest records image normalization and mask encoding.
- Duplicate and suspicious files remain in the output and are listed in `prepared/duplicate_audit.csv`.
