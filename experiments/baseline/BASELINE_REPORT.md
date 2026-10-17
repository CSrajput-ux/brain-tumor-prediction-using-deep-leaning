# Baseline experiment status

**Status: NO-GO — training was not started.**

No fold metrics, predictions, confusion matrix, training log, model checkpoint, or inference timings are reported because no model was trained.

The pre-training verification is documented in `NO_GO_REPORT.md` and the pair-level audit is in `near_duplicate_crossfold_review.csv`.

## Exact gate command

```powershell
py -3 .\scripts\pretraining_gate.py --prepared-dir .\prepared_full_run --source-root . --output-dir .\experiments\baseline
```

The gate exited with status 2 because 236 pHash near-duplicate candidate pairs cross both patient IDs and evaluation folds. Two of these pairs had SSIM >= 0.80. These are unconfirmed candidates, not proof of duplicate patients, but they require manual/source-provenance review before training.

## Outputs not created

- `metrics.json`, `fold_metrics.csv`, `predictions.csv`, `confusion_matrix.png`, `training_log.csv`, model checkpoints, and model predictions were intentionally not generated.
- No training or intervention experiment was run.
