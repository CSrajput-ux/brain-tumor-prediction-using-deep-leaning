"""
Unit and regression test suite for Phase 8: Deep Novelty Discovery, Research Redesign & Contribution Validation.
Verifies artifact integrity, schema compliance, checksum validity, and gate decision.
"""

import os
import csv
import json
import hashlib
import pytest

PHASE8_DIR = os.path.join("experiments", "phase_8_novelty_discovery")

EXPECTED_FILES = [
    "PHASE_8_NOVELTY_DISCOVERY_REPORT.md",
    "current_research_reconstruction.md",
    "independent_search_protocol.md",
    "independent_search_log.csv",
    "independent_prior_art_audit.csv",
    "candidate_research_directions.csv",
    "novelty_stress_test.md",
    "contribution_overlap_matrix.csv",
    "selected_research_direction.md",
    "proposed_preregistration.md",
    "minimum_experiment_decision.md",
    "limitations_and_unresolved_questions.md",
    "verified_bibliography.bib",
    "reference_verification.csv",
    "checksums.json",
]


def test_phase_8_files_exist_and_non_empty():
    """Verify that all 15 required Phase 8 deliverables exist and are non-empty."""
    for fname in EXPECTED_FILES:
        fpath = os.path.join(PHASE8_DIR, fname)
        assert os.path.isfile(fpath), f"Missing required file: {fname}"
        assert os.path.getsize(fpath) > 0, f"File is empty: {fname}"


def test_phase_8_checksums_match():
    """Verify that checksums.json correctly hashes all Phase 8 deliverables."""
    checksum_path = os.path.join(PHASE8_DIR, "checksums.json")
    with open(checksum_path, "r", encoding="utf-8") as f:
        stored_hashes = json.load(f)

    for fname, expected_hash in stored_hashes.items():
        fpath = os.path.join(PHASE8_DIR, fname)
        assert os.path.isfile(fpath), f"File in checksums.json not found: {fname}"
        with open(fpath, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == expected_hash, f"SHA-256 mismatch for {fname}"


def test_phase_8_csv_schemas():
    """Verify that all CSV deliverables parse cleanly and have correct headers."""
    # 1. independent_search_log.csv
    log_path = os.path.join(PHASE8_DIR, "independent_search_log.csv")
    with open(log_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        log_rows = list(reader)
        assert len(log_rows) >= 10, "Search log must contain at least 10 query rows"
        assert "search_id" in reader.fieldnames
        assert "query_string" in reader.fieldnames

    # 2. independent_prior_art_audit.csv
    audit_path = os.path.join(PHASE8_DIR, "independent_prior_art_audit.csv")
    with open(audit_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        audit_rows = list(reader)
        assert len(audit_rows) >= 15, "Prior art audit must contain at least 15 verified studies"
        expected_cols = [
            "title", "authors", "year", "verified_identifier", "source_url",
            "full_text_status", "research_question", "dataset", "experimental_method",
            "intervention_controls", "statistical_method", "principal_findings",
            "limitations", "overlap_with_current_project", "potential_contradiction",
            "contribution_already_established", "unresolved_difference", "verification_notes"
        ]
        for col in expected_cols:
            assert col in reader.fieldnames, f"Missing column in prior art audit: {col}"

    # 3. candidate_research_directions.csv
    cand_path = os.path.join(PHASE8_DIR, "candidate_research_directions.csv")
    with open(cand_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cand_rows = list(reader)
        assert len(cand_rows) == 6, "Must evaluate exactly 6 candidate research directions"
        for row in cand_rows:
            assert float(row["weighted_total_score"]) >= 0.0

    # 4. contribution_overlap_matrix.csv
    overlap_path = os.path.join(PHASE8_DIR, "contribution_overlap_matrix.csv")
    with open(overlap_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        overlap_rows = list(reader)
        assert len(overlap_rows) >= 5, "Overlap matrix must contain key comparisons"

    # 5. reference_verification.csv
    ref_path = os.path.join(PHASE8_DIR, "reference_verification.csv")
    with open(ref_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ref_rows = list(reader)
        assert len(ref_rows) >= 15, "Reference verification must contain at least 15 studies"


def test_phase_8_gate_decision():
    """Verify that PHASE_8_NOVELTY_DISCOVERY_REPORT.md specifies GATE A."""
    report_path = os.path.join(PHASE8_DIR, "PHASE_8_NOVELTY_DISCOVERY_REPORT.md")
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "GATE A: STRONG CANDIDATE IDENTIFIED" in content, "Gate decision must be GATE A"
