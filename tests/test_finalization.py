from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.io import savemat

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from prepare_cheng_dataset import _finalize_staged_run, _validate_staging, _write_atomic_npz, prepare


def _build_sample(path: Path, label: int, patient_id: str, class_index: int = 0) -> None:
    image = (class_index + 1) * np.arange(16, dtype=np.float32).reshape(4, 4)
    mask = np.zeros_like(image, dtype=np.uint8)
    mask[1:3, 1:3] = 1
    savemat(
        str(path),
        {
            "cjdata": {
                "label": np.array(label, dtype=np.int32),
                "PID": patient_id,
                "image": image,
                "tumorMask": mask,
                "tumorBorder": np.array([[0, 0], [3, 3]], dtype=np.int32),
            }
        },
    )


@pytest.fixture
def dataset_root(tmp_path: Path) -> Path:
    root = tmp_path / "dataset"
    archive = root / "brainTumorDataPublic_1"
    archive.mkdir(parents=True)
    for idx in range(3):
        _build_sample(archive / f"sample_{idx}.mat", label=(idx % 3) + 1, patient_id=f"P{idx + 1}", class_index=idx)
    return root


def test_fresh_output_directory_finalizes(dataset_root: Path) -> None:
    output_dir = dataset_root / "prepared_final"
    result = prepare(dataset_root, output_dir, replace_existing=False)
    assert result["status"] == "finalized"
    assert output_dir.is_dir()
    assert (output_dir / "metadata.csv").is_file()
    assert (output_dir / "manifest.json").is_file()


def test_existing_output_requires_explicit_replacement(dataset_root: Path) -> None:
    output_dir = dataset_root / "prepared_final"
    output_dir.mkdir()
    with pytest.raises(FileExistsError):
        prepare(dataset_root, output_dir, replace_existing=False)


def test_existing_output_can_be_replaced(dataset_root: Path) -> None:
    output_dir = dataset_root / "prepared_final"
    output_dir.mkdir()
    (output_dir / "stale.txt").write_text("old", encoding="utf-8")
    prepare(dataset_root, output_dir, replace_existing=True)
    assert (output_dir / "metadata.csv").is_file()
    backups = list(output_dir.parent.glob("prepared_final.backup.*"))
    assert backups


def test_atomic_npz_write_round_trips(dataset_root: Path) -> None:
    target = dataset_root / "tmp" / "sample.npz"
    _write_atomic_npz(target, {"image": np.ones((2, 2), dtype=np.float32)})
    assert target.is_file()
    with np.load(target) as payload:
        assert payload["image"].shape == (2, 2)


def test_failed_staging_run_is_detected(dataset_root: Path) -> None:
    bad_stage = dataset_root / "bad_stage"
    bad_stage.mkdir()
    with pytest.raises(FileNotFoundError):
        _validate_staging(bad_stage)


def test_simulated_promotion_failure_preserves_authoritative_output(dataset_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    final_dir = dataset_root / "prepared_final"
    final_dir.mkdir()
    (final_dir / "stale.txt").write_text("old", encoding="utf-8")

    staging_dir = dataset_root / ".staged_test_run"
    staging_dir.mkdir()
    (staging_dir / "inventory.csv").write_text("folder_name,mat_file_count\narchive,1\n", encoding="utf-8")
    (staging_dir / "metadata.csv").write_text("sample_id,source_path\ncheng_a,src.mat\n", encoding="utf-8")
    (staging_dir / "class_summary.csv").write_text("class_label,class_name\n1,meningioma\n", encoding="utf-8")
    (staging_dir / "patient_summary.csv").write_text("patient_id,slices\nP1,1\n", encoding="utf-8")
    (staging_dir / "duplicate_audit.csv").write_text("classification,group_id\nnot_flagged,NA\n", encoding="utf-8")
    (staging_dir / "validation_errors.csv").write_text("sample_id,severity,issue_type,message\n", encoding="utf-8")
    (staging_dir / "validation_issues.csv").write_text("sample_id,severity,issue_type,message\n", encoding="utf-8")
    (staging_dir / "manifest.json").write_text('{"discovered_mat_files": 1}', encoding="utf-8")

    original_replace = os.replace

    def fake_replace(src, dst):
        if os.fspath(src) == str(final_dir) and str(dst).startswith(str(final_dir.parent)):
            raise OSError("simulated promotion failure")
        return original_replace(src, dst)

    monkeypatch.setattr(os, "replace", fake_replace)
    with pytest.raises(OSError):
        _finalize_staged_run(staging_dir, final_dir, replace_existing=True)
    assert final_dir.is_dir()
    assert (final_dir / "stale.txt").read_text(encoding="utf-8") == "old"


def test_repeated_pilot_then_full_run_stays_isolated(dataset_root: Path) -> None:
    pilot_dir = dataset_root / "pilot_output"
    full_dir = dataset_root / "full_output"
    result_pilot = prepare(dataset_root, pilot_dir, run_label="pilot", limit=1)
    assert result_pilot["status"] == "finalized"
    result_full = prepare(dataset_root, full_dir, run_label="full")
    assert result_full["status"] == "finalized"
    assert (pilot_dir / "metadata.csv").is_file()
    assert (full_dir / "metadata.csv").is_file()
    assert pilot_dir != full_dir


def test_interrupted_execution_remains_unfinalized(dataset_root: Path) -> None:
    staged = dataset_root / ".staging_interrupted"
    staged.mkdir()
    (staged / "RUN_STATE.json").write_text('{"status": "in_progress"}', encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        _validate_staging(staged)
