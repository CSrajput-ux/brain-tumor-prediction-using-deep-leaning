# Patient split audit

- The supplied `cvind.mat` vector remains **unverified** for file-to-sample mapping.
- Numeric filename order is suggestive but not sufficient evidence that `cvind[i]` corresponds to file `i.mat`.
- Therefore, patient-independent cross-validation is generated from observed `PID` values only, not from the raw `cvind` vector.
- The patient assignment is enforced by group membership, and no patient ID appears in more than one fold.
- Any earlier assumption that five folds alone imply patient independence is not used here.
