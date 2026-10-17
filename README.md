# Cheng Brain Tumor Dataset preparation

This project prepares the four already-extracted Cheng Brain Tumor Dataset folders. It does not download, extract, modify, or relabel source files. Class labels are read from `cjdata.label` (`1=meningioma`, `2=glioma`, `3=pituitary`); folder names are treated only as archive identifiers.

## Requirements

Use Python 3.10 or newer on Windows. From PowerShell in this project directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The scripts support conventional MATLAB MAT files via SciPy and MATLAB 7.3/HDF5 MAT files via h5py. They recursively scan folders named `brainTumorDataPublic_*` directly under the input root. No dataset download or extraction is part of this workflow.

## Reproduce preparation and audit

Run from the project root in PowerShell:

```powershell
python .\scripts\prepare_cheng_dataset.py --input-root . --output-dir .\prepared
python .\scripts\inspect_cvind.py --cvind .\cvind.mat --input-root . --output-dir .\prepared --report-dir .\reports
python .\scripts\create_patient_splits.py --metadata .\prepared\metadata.csv --output .\prepared\patient_splits.csv --report .\reports\patient_split_summary.md --folds 5 --seed 42
python .\scripts\validate_cheng_dataset.py --output-dir .\prepared --report-dir .\reports
```

For a pilot, use a separate output directory, validate it without requiring all source files, and only then run the complete preparation:

```powershell
python .\scripts\prepare_cheng_dataset.py --input-root . --output-dir .\prepared_pilot --limit 12
python .\scripts\validate_cheng_dataset.py --output-dir .\prepared_pilot --report-dir .\reports\pilot --allow-partial
```

If the extracted folders are elsewhere, pass their actual root with `--input-root C:\path\to\extracted-root`. To specify archive folders individually, pass one or more `--input-dir C:\path\to\archive` arguments.

Safe reruns and finalization:

```powershell
python .\scripts\prepare_cheng_dataset.py --input-root . --output-dir .\prepared --run-label full
# existing final outputs are protected by default; use --replace-existing only when you explicitly intend to replace the current finalized dataset
python .\scripts\prepare_cheng_dataset.py --input-root . --output-dir .\prepared --run-label full --replace-existing
```

The preparation workflow stages all generated artifacts in a temporary run directory, validates them before promotion, and preserves a backup of the previous final output until the new one is confirmed. The final promotion uses a same-filesystem rename where supported; on unsupported filesystems, the script documents the actual limitations and refuses unsafe replacement by default.

## Outputs

- `prepared/images/<class>/`: per-image min-max normalized 8-bit grayscale PNG. This normalization is for a convenient lossless image export; it is not a replacement for the source MRI intensities.
- `prepared/masks/<class>/`: grayscale PNG masks where values fit in 8 bits. Mask annotations are never generated or replaced by predictions.
- `prepared/raw_arrays/<sample_id>.npz`: original image, mask (when present), and tumour-border arrays with original pixel values and dtypes.
- `prepared/overlays/<class>/`: red tumour-mask overlays for masks with binary values and matching image dimensions.
- `prepared/metadata.csv`: source paths and identifiers, label/PID, shapes and dtypes, mask checks, tumour-pixel statistics, checksums, output paths, and processing outcome.
- `prepared/inventory.csv`, `class_summary.csv`, `patient_summary.csv`, `duplicate_audit.csv`, `validation_errors.csv`, and `manifest.json`: input inventory, observed counts, duplicate/quality findings, errors, and processing provenance.
- `prepared/cvind_inspection.json` and `reports/cvind_inspection.md`: structural inspection and explicit order/grouping caveats for the supplied cross-validation vector.
- `prepared/patient_splits.csv` and `reports/patient_split_summary.md`: reproducible patient-grouped folds, created only when the available PIDs support the requested grouping and stratification.
- `reports/DATASET_AUDIT_REPORT.md`: complete audit with verified findings, assumptions, and unresolved issues.
- `reports/quality_control_montage.png`: one example per available class, with a tumour overlay when its mask passes binary/dimension checks.

Sample IDs are derived from the source-relative path, so same-named files in different archive folders cannot overwrite one another. The source file SHA-256 is stored separately. Duplicate and suspicious data are reported and retained.

## Scientific and annotation limitations

Tumour area and fraction are pixel-space quantities; physical area must not be inferred without verified image spacing. The supplied `cvind.mat` vector is not attached to files unless a documented sample-order mapping can be verified. Numeric filenames alone are not considered proof of that mapping or of patient-level folds.

For later controlled experiments, retain this prepared original image/mask pair as the baseline. Isolated-tumour or tumour-removed images can be constructed from the annotation mask, but mask-edge seams, interpolation/inpainting, altered intensity distributions, and loss of clinically meaningful peritumoural anatomy are potential confounds. Placebo masks should be matched in shape/area/location constraints and reported as controls; background/context manipulations should preserve clinically relevant anatomy where possible. Prediction changes after masking do not alone establish causal tumour reliance. No model training or causal/performance claim is part of this preparation pipeline.
