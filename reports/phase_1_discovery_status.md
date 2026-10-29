# Phase 1: local discovery status

Observed on 2026-10-29 (Asia/Kolkata), without modifying raw data:

- Cheng source root: `cheng/`, containing four `brainTumorDataPublic_*` directories, `cvind.mat`, and 3,064 numbered source `.mat` records plus the CV index file (3,065 `.mat` files total).
- The sampled Cheng record has the header `MATLAB 7.3 MAT-file`; the ingestion module therefore uses HDF5 fallback rather than assuming classic MATLAB serialization.
- BRISC official release root: `brisc/brisc2025/`, with `manifest.csv`, `manifest.json`, checksums and README. The official manifest contains 15,586 rows covering classification records and segmentation image/mask records.
- A separate `brisc/Data/` directory is present but is not enumerated by `brisc2025/manifest.csv`; it is excluded from BRISC analysis until provenance is supplied.
- The BRISC manifest reports 6,000 classification rows (5,000 train and 1,000 test) and 9,586 segmentation rows. The current local tree has only 2,028 files under `segmentation_task`, so the release is likely incomplete or its manifest and files disagree. This is a local-file observation, not a claim about the published dataset.
- The official BRISC manifest has no patient identifier field. Any BRISC uncertainty analysis must be described as image-level unless reliable grouping metadata is supplied.

## Execution status

An isolated Python 3.12 runtime was installed under `.tools/python312` after the system Chocolatey shim was found to be broken. The initial manifest build verified Cheng successfully (3,064 readable records; 233 PIDs; meningioma 708, glioma 1,426, pituitary 930). BRISC's initial build exposed an implementation defect: manifest presence was incorrectly treated as local mask-file presence. The code has been corrected and the complete rebuild is in progress. No BRISC mask-availability count, duplicate finding, or model result is final until that corrected rebuild and audit complete.
