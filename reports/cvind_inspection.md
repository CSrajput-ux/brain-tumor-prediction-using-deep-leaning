# `cvind.mat` inspection

## Verified from the supplied file
- Path: `C:\Users\jkgga\Downloads\ChengResearch\cvind.mat`
- Variable: `cvind`; HDF5 stored dimensions: `[1, 3064]`; MATLAB-native dimensions inferred by reversing HDF5 dimension order: `[3064, 1]`.
- Assignment count: 3064; dtype: `float64`; MATLAB class: `double`.
- Fold values and counts: `{5: 643, 3: 572, 4: 628, 1: 542, 2: 679}`.
- Numeric sample filenames form a unique contiguous 1..N sequence: `True`.

## Mapping and grouping limitations
- Although the filenames form a numeric sequence, the supplied README does not explicitly state that vector position i maps to i.mat. Therefore the mapping remains **UNVERIFIED** and no cvind values have been attached to samples.
- The available evidence does not establish whether the folds are slice-level or patient-level; five folds alone do not demonstrate patient independence.
- Patient-grouped folds generated separately by `create_patient_splits.py` must be used for patient-independent evaluation.

## Additional checks
- Numeric indices without files: `[]`
- Numeric file indices outside the cvind range: `[]`
- Duplicate numeric filename indices: `{}`
- Non-numeric `.mat` filenames: `[]`
