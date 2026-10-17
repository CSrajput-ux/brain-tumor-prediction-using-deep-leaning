# Resolution recommendations

**Current final status: NO-GO.** No pair has human-reviewed identity or acquisition conclusions; the pre-training gate must remain closed.

## Evidence categories

- `exact_duplicate_confirmed`: 0 pairs, using exact source SHA-256 or dtype/shape/pixel equality.
- `probable_same_image`: 0 pairs. This category requires human review and is not assigned automatically.
- `possible_related_slices`: 0 pairs. Acquisition provenance is unavailable, so this cannot be assigned from image similarity alone.
- `visually_similar_not_confirmed`: 0 pairs. Automated similarity is recorded, but no human visual conclusion is made.
- `unresolved`: 236 pairs.

## Actions

1. Request expert review of the 236 cross-patient/cross-fold pairs, prioritizing SSIM >= 0.80, then the highest SSIM and lowest pHash distances. The generated contact-sheet index preserves pair labels and page locations.
2. Request source-level acquisition provenance from the dataset provider, if available. The available README reports no further acquisition detail.
3. Record each reviewer decision, evidence, reviewer/date, and confidence in a separate human-authored adjudication file. Do not overwrite automated evidence or imply review occurred.
4. Retain all samples, labels, PIDs, and original folds while unresolved. Do not merge patients based on similarity.
5. If exact duplicate images are confirmed across folds, create a new versioned split manifest and resolution log; retain original split and data, document duplicate-linked groups, regroup conservatively, and rerun integrity, patient-overlap, and gate tests.
6. If ambiguity cannot be resolved, use an explicitly conservative sensitivity protocol with candidate-linked groups kept together where justified by expert evidence; report exclusions/retentions and quantify sample/fold changes. If grouping evidence is not defensible, keep training blocked rather than silently changing folds.

A separate candidate-grouped sensitivity split is not generated here because similarity alone does not establish that the candidate records belong to one acquisition or patient. Any sensitivity analysis must be versioned, justified, and validated independently.

## Conclusion

Available evidence does not conclusively resolve potential cross-fold relatedness. The 236 candidates are not confirmed leakage, but they remain a material unresolved risk for held-out-fold evaluation. **Keep the pre-training gate closed pending human/source-provenance review or a defensible, documented alternative evaluation protocol.**
