# Baseline pre-training gate

**Decision: NO-GO**

## Verified dataset and split checks

- Prepared metadata samples: 3064; split rows: 3064.
- Class counts: `{'meningioma': 708, 'glioma': 1426, 'pituitary': 930}`.
- Unique patients: 233; missing patient IDs: 0.
- Patient overlap across folds: 0.
- Missing/extra split assignments: 0/0.
- Source MAT files re-opened and labels/PIDs checked directly against `cjdata`: 3064 with no recorded source failures.
- Missing/unreadable or malformed generated outputs: 0.
- Source checksum mismatches: 0; exact duplicate source contents: 0.

## Near-duplicate leakage review

- Pairwise candidates in the prepared audit: 1254.
- Candidates with different patient IDs and different folds: 236.
- Those cross-patient/cross-fold candidates with SSIM >= 0.80: 2.
- pHash and SSIM are screening measures, not proof that two slices are the same acquisition or patient.
- The pair list is preserved in `near_duplicate_crossfold_review.csv`; candidate pairs remain unconfirmed and require manual/source-provenance review.
- No candidate or source sample was deleted or reassigned.

## Fold distributions

| Fold | Patients | Slices | Class distribution |
|---|---:|---:|---|
| fold_1 | 47 | 613 | `{'meningioma': 142, 'pituitary': 185, 'glioma': 286}` |
| fold_2 | 47 | 614 | `{'meningioma': 142, 'glioma': 286, 'pituitary': 186}` |
| fold_3 | 46 | 611 | `{'meningioma': 142, 'pituitary': 185, 'glioma': 284}` |
| fold_4 | 46 | 613 | `{'meningioma': 141, 'glioma': 285, 'pituitary': 187}` |
| fold_5 | 47 | 613 | `{'meningioma': 141, 'glioma': 285, 'pituitary': 187}` |

## Decision rationale

- **Unresolved:** 236 cross-patient near-duplicate candidates span different evaluation folds and have not been manually resolved; this is a potential leakage risk.

Training is blocked. Resolve the cross-patient/cross-fold candidate pairs using source provenance or a documented expert review, then rerun this gate. Do not change folds based only on pHash/SSIM, and do not treat perceptual similarity alone as confirmed patient identity.

## Provenance and limitations

- Dataset manifest SHA-256: `4ef492323314630596da8aef0871c5e3708413aec5fe6e3796aef53b8741ca05`.
- Split manifest SHA-256: `c45e0eea02f00f7c3d80f20d3f4764f758d8471300a81ff4d25ea31c2387d622`.
- `cvind.mat` structure: stored shape `[1, 3064]`, inferred MATLAB shape `[3064, 1]`, fold counts `{'1': 542, '2': 679, '3': 572, '4': 628, '5': 643}`; mapping remains unverified.
- `cvind.mat` remains unverified for file-to-index mapping and was not used.
- The gate re-opens source MAT files, confirms class labels and exact PIDs against `cjdata`, validates masks and generated image/array paths, and checks sample/split accounting.
- Near-duplicate similarity screening can create false positives from shared anatomy and background; expert review or reliable acquisition linkage is required before conclusions about leakage.
