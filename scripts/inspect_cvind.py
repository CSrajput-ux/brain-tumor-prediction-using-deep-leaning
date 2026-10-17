from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import h5py
import numpy as np
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parent.parent


def inspect(cvind_path: Path, input_root: Path, output_dir: Path, report_dir: Path) -> dict:
    stored_shape = None
    matlab_shape = None
    with h5py.File(cvind_path, "r") as handle:
        if "cvind" not in handle:
            raise ValueError("cvind.mat does not contain a cvind variable")
        dataset = handle["cvind"]
        values = np.asarray(dataset[()])
        stored_shape = list(values.shape)
        matlab_shape = list(reversed(values.shape)) if values.ndim > 1 else list(values.shape)
        matlab_order_values = np.transpose(values, axes=tuple(reversed(range(values.ndim)))) if values.ndim > 1 else values
        values = matlab_order_values.ravel(order="F")
        matlab_class = dataset.attrs.get("MATLAB_class")
        if isinstance(matlab_class, bytes):
            matlab_class = matlab_class.decode("ascii", errors="replace")

    if values.size == 0 or not np.issubdtype(values.dtype, np.number):
        raise ValueError("cvind must be a non-empty numeric array")
    finite = np.isfinite(values)
    integral = bool(finite.all() and np.equal(values, np.floor(values)).all())
    folds = [int(value) for value in values] if integral else []
    counts = Counter(folds)
    archive_files = []
    for folder in sorted(input_root.glob("brainTumorDataPublic_*")):
        if folder.is_dir():
            archive_files.extend(folder.rglob("*.mat"))
    numeric = {}
    nonnumeric = []
    for path in archive_files:
        try:
            index = int(path.stem)
        except ValueError:
            nonnumeric.append(str(path))
            continue
        numeric.setdefault(index, []).append(str(path))
    expected = set(range(1, len(values) + 1))
    missing_indices = sorted(expected - set(numeric))
    extra_indices = sorted(set(numeric) - expected)
    duplicate_indices = {str(k): v for k, v in numeric.items() if len(v) != 1}
    numeric_contiguous = not missing_indices and not extra_indices and not duplicate_indices and not nonnumeric
    valid_fold_values = integral and set(folds).issubset({1, 2, 3, 4, 5})

    result = {
        "cvind_path": str(cvind_path.resolve()),
        "variable": "cvind",
        "stored_hdf5_shape": stored_shape,
        "matlab_native_shape_inferred_from_hdf5_dimension_order": matlab_shape,
        "dtype": str(values.dtype),
        "MATLAB_class": matlab_class,
        "number_of_assignments": int(values.size),
        "values_are_finite_integers": integral,
        "fold_values": sorted(counts),
        "fold_assignment_counts": {str(k): counts[k] for k in sorted(counts)},
        "five_fold_values_1_to_5": valid_fold_values,
        "sample_files_discovered": len(archive_files),
        "numeric_filename_indices_contiguous_and_unique": numeric_contiguous,
        "filename_order_candidate_exists": numeric_contiguous and len(archive_files) == values.size,
        "mapping_verified": False,
        "mapping_status": (
            "UNVERIFIED: numeric filenames provide a possible 1-based candidate order, but the supplied README "
            "does not establish that cvind position i corresponds to file i.mat. No fold assignments were mapped."
        ),
        "indices_represent": (
            "The vector assigns each of 3064 positional entries to one of five values. The available README calls "
            "these five-fold cross-validation indices but does not define the index-to-file order or patient grouping."
        ),
        "fold_unit": "Unverified; cannot establish slice-level versus patient-level grouping from cvind alone.",
        "missing_numeric_file_indices": missing_indices,
        "extra_numeric_file_indices": extra_indices,
        "duplicate_numeric_file_indices": duplicate_indices,
        "nonnumeric_mat_filenames": nonnumeric,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cvind_inspection.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = [
        "# `cvind.mat` inspection",
        "",
        "## Verified from the supplied file",
        f"- Path: `{cvind_path.resolve()}`",
        f"- Variable: `cvind`; HDF5 stored dimensions: `{stored_shape}`; MATLAB-native dimensions inferred by reversing HDF5 dimension order: `{matlab_shape}`.",
        f"- Assignment count: {values.size}; dtype: `{values.dtype}`; MATLAB class: `{matlab_class}`.",
        f"- Fold values and counts: `{dict(counts)}`.",
        f"- Numeric sample filenames form a unique contiguous 1..N sequence: `{numeric_contiguous}`.",
        "",
        "## Mapping and grouping limitations",
        "- Although the filenames form a numeric sequence, the supplied README does not explicitly state that vector position i maps to i.mat. Therefore the mapping remains **UNVERIFIED** and no cvind values have been attached to samples.",
        "- The available evidence does not establish whether the folds are slice-level or patient-level; five folds alone do not demonstrate patient independence.",
        "- Patient-grouped folds generated separately by `create_patient_splits.py` must be used for patient-independent evaluation.",
        "",
        "## Additional checks",
        f"- Numeric indices without files: `{missing_indices}`",
        f"- Numeric file indices outside the cvind range: `{extra_indices}`",
        f"- Duplicate numeric filename indices: `{duplicate_indices}`",
        f"- Non-numeric `.mat` filenames: `{nonnumeric}`",
    ]
    (report_dir / "cvind_inspection.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect cvind.mat without assuming a file-order mapping.")
    parser.add_argument("--cvind", type=Path, default=ROOT / "cvind.mat")
    parser.add_argument("--input-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "prepared")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    print(json.dumps(inspect(args.cvind, args.input_root, args.output_dir, args.report_dir), indent=2))


if __name__ == "__main__":
    main()
