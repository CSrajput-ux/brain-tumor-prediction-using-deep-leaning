# Cross-fold near-duplicate investigation

**Decision: NO-GO remains in force. No model training was performed.**

## Scope and method

- Preserved source review rows: 1254; filtered cross-patient/cross-fold candidates: 236.
- Pair row order and existing `group_id` values were preserved. The pair ID is the original `group_id`.
- pHash candidate list originates from the prior audit at Hamming distance <= 4/64; this investigation did not generate or reorder candidate pairs.
- The prior SSIM values were computed on prepared per-image min-max normalized uint8 grayscale PNGs; no registration; `scipy.ndimage.gaussian_filter` sigma=1.5, truncate=4.0 (13x13 support), reflect boundary mode; `C1=(0.01*255)^2`, `C2=(0.03*255)^2`; global mean SSIM.
- This run independently reopened source MATs to compare original `cjdata.image` arrays, dimensions, dtypes, intensity ranges, encoded source SHA-256, and dtype/shape/pixel-aware array SHA-256 against metadata.
- Contact-sheet thumbnails preserve aspect ratio. The 50/50 blend and contrast-scaled absolute-difference panel are diagnostic visualizations, not identity evidence.

## Automated evidence

- Pair records produced: 236; source evidence errors: 0.
- Source file hash-equal pairs: 0; exact image-array-equal pairs: 0.
- Original-array Pearson correlation median/max: 0.664900/0.881530; pairs >=0.90: 0; maximum exact-pixel fraction: 0.325287.
- Cross-fold pairs with existing SSIM >= 0.80: 2.
- SSIM range/median for reviewed pairs: 0.396994 / 0.603067 / 0.809674.
- pHash distance distribution: `{4: 217, 2: 19}`.
- Source identity-to-metadata mismatches: 0; original candidate row-to-current metadata mismatches: 0.
- Review status for every pair: `automated_evidence_only_no_human_review`. No human review was performed or inferred.
- Automated categories are limited to `exact_duplicate_confirmed` when source SHA-256 or exact image-array equality proves equality; all other non-identical cases remain `unresolved`.

## Contact sheets

- Pair counts by SSIM severity: `{'ssim_ge_0_80': 2, 'ssim_0_70_to_0_80': 59, 'ssim_lt_0_70': 175, 'low_similarity_controls': 12}`.
- Contact-sheet pages: 63; index: `contact_sheets/contact_sheet_index.csv`.
- Every pair appears in its SSIM-severity group. The low-similarity control set is a deterministic sample of up to 12 lowest-SSIM pairs.
- Image panels are labeled with pair ID, sample IDs, pseudonymous PIDs, classes, folds, SSIM, pHash distance, dimensions, and array-equality evidence.

## Source provenance findings

- Available dataset documentation describes a collection from two hospitals (Nanfang Hospital and Tianjin Medical University General Hospital), acquired 2005-09 through 2010-10, and says further acquisition details are unavailable due to the passage of time.
- No per-slice acquisition/volume identifiers, DICOM series linkage, or mapping from MAT files to source scans was found in the inspected documentation or `cjdata` fields.
- Repeated exports, shared acquisitions, and different-PID duplication cannot therefore be conclusively established or excluded from the available files.
- Different PIDs in a candidate pair are retained as supplied; this report does not merge identities or infer that similar images depict the same person.

## Integrity preservation

- Review CSV SHA-256 before/after: `3a15554290ef8db234d7590455976576dc5766f797d5affd3b561c938b58a9d7` / `3a15554290ef8db234d7590455976576dc5766f797d5affd3b561c938b58a9d7`.
- Split manifest SHA-256 before/after: `c45e0eea02f00f7c3d80f20d3f4764f758d8471300a81ff4d25ea31c2387d622` / `c45e0eea02f00f7c3d80f20d3f4764f758d8471300a81ff4d25ea31c2387d622`.
- Metadata CSV SHA-256 before/after: `c15f35073d4f03e6a91b13b9ff2d9076b5ece0dce7a8b0f2613d376886fc27f4` / `c15f35073d4f03e6a91b13b9ff2d9076b5ece0dce7a8b0f2613d376886fc27f4`.
- Input files unchanged: **True**. Source files, prepared images/masks, metadata, labels, PIDs, and fold assignments were not modified.
- No deletion, relabeling, patient-ID merge, or fold reassignment was performed.

## Limitations

- SSIM and pHash are not patient-identity or acquisition-identity tests. Similar normal anatomy and acquisition patterns can elevate similarity; dissimilar slices from one volume can also evade detection.
- No human reviewer inspected the images during this automated investigation; all human conclusion fields remain blank.
- The imaging arrays are 2-D slices and do not provide reliable slice position, series UID, scanner identifiers, or original DICOM provenance.
- The investigation does not establish that candidate pairs are duplicate scans or that leakage has occurred.

## Commands

```powershell
py -3 .\scripts\investigate_duplicates.py --review-csv .\experiments\baseline\near_duplicate_crossfold_review.csv --split-csv .\prepared_full_run\patient_splits.csv --metadata-csv .\prepared_full_run\metadata.csv --prepared-dir .\prepared_full_run --output-dir .\reports\duplicate_investigation
py -3 -m pytest .\tests\test_duplicate_investigation.py -q
py -3 -m pytest .\tests -q

Regression result from this execution: 15 tests passed (7 duplicate-investigation tests and 8 prior finalization tests).
```

For machine-readable pair-level evidence, see `automated_evidence.json` and `duplicate_pair_review.csv`.
