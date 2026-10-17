"""Phase 2.1 Tests — Independent Baseline Completion Audit Integrity and Reconciliation.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "experiments" / "phase_2_baseline_audit"
CHECKSUMS_JSON = AUDIT_DIR / "audit_checksums.json"
SPLITS_CSV = ROOT / "prepared_full_run" / "patient_splits.csv"
METADATA_CSV = ROOT / "prepared_full_run" / "metadata.csv"
P18_CHECKSUMS = ROOT / "experiments" / "phase_1_8" / "phase_1_8_checksums.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# 1. Authoritative baseline manifest preservation
def test_authoritative_manifest_preservation():
    assert SPLITS_CSV.exists()
    assert METADATA_CSV.exists()
    with open(P18_CHECKSUMS, encoding="utf-8") as f:
        p18 = json.load(f)
    assert _sha256(SPLITS_CSV) == p18["artifacts"]["patient_splits_csv"]["sha256"], "Authoritative splits modified!"
    assert _sha256(METADATA_CSV) == p18["artifacts"]["metadata_csv"]["sha256"], "Authoritative metadata modified!"


# 2. Phase 2.1 deliverables presence and cryptographic checksums
def test_audit_deliverables_and_checksums():
    assert CHECKSUMS_JSON.exists(), "audit_checksums.json missing"
    with open(CHECKSUMS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_artifacts"] == 4
    for k, v in data["artifacts"].items():
        p = ROOT / v["path"]
        assert p.exists(), f"Audit artifact missing: {p}"
        assert _sha256(p) == v["sha256"], f"Checksum mismatch: {p}"


# 3. Metric reconciliation zero mismatches
def test_metric_reconciliation_zero_mismatches():
    rec_p = AUDIT_DIR / "metric_reconciliation.csv"
    assert rec_p.exists()
    with open(rec_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 102, f"Expected 102 reconciled metrics, got {len(rows)}"
    for r in rows:
        assert r["status"] == "EXACT_MATCH", f"Mismatch in {r['scenario']} {r['fold']} {r['metric_name']}"
        assert float(r["absolute_difference"]) < 1e-5


# 4. Split isolation all disjoint and test data unused for selection
def test_split_isolation_all_disjoint():
    iso_p = AUDIT_DIR / "split_isolation_audit.json"
    assert iso_p.exists()
    with open(iso_p, encoding="utf-8") as f:
        data = json.load(f)

    assert data["all_partitions_disjoint"] is True
    assert len(data["details"]) == 15
    for entry in data["details"]:
        assert entry["status"] == "PASS"
        assert entry["selection_used_test_data"] is False
        assert entry["patient_overlap"]["train_val"] == 0
        assert entry["patient_overlap"]["train_test"] == 0
        assert entry["patient_overlap"]["val_test"] == 0


# 5. Audit report content and decision
def test_audit_report_content_and_decision():
    report_p = AUDIT_DIR / "INDEPENDENT_AUDIT_REPORT.md"
    assert report_p.exists()
    content = report_p.read_text(encoding="utf-8")
    assert "AUDIT-PASS-WITH-LIMITATIONS" in content
    assert "102 out of 102" in content or "102" in content
    assert "STATISTICAL INTERPRETATION OF ZERO-CROSSING INTERVALS" in content
