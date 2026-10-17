# Patient-grouped cross-validation splits

- Stratifier: `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`.
- Samples assigned: 3064; distinct patients: 233.
- All slices with the same exact PID are assigned to one fold. PID is not modified or synthesized.
- Fold overlap check: **PASS** (no patient ID appears in more than one fold).
- The provided `cvind.mat` vector remains unverified; no file-to-fold mapping was inferred from numeric ordering alone.

| Fold | Patients | Slices | Class distribution |
|---|---:|---:|---|
| fold_1 | 47 | 613 | `{'meningioma': 142, 'pituitary': 185, 'glioma': 286}` |
| fold_2 | 47 | 614 | `{'meningioma': 142, 'glioma': 286, 'pituitary': 186}` |
| fold_3 | 46 | 611 | `{'meningioma': 142, 'pituitary': 185, 'glioma': 284}` |
| fold_4 | 46 | 613 | `{'meningioma': 141, 'glioma': 285, 'pituitary': 187}` |
| fold_5 | 47 | 613 | `{'meningioma': 141, 'glioma': 285, 'pituitary': 187}` |

Per-class balance is approximate at the patient-group level; slices are not independent observations. Use only the assignments in the CSV, and do not use the original `cvind.mat` as a patient-independent split. The split was generated from verified patient IDs, not from an unproven `cvind.mat` order.
