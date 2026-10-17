"""Tests for Phase 1.6 deliverable integrity and artifact preservation."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INDEPENDENT_REVIEW_DIR = ROOT / "reports" / "independent_review"
DUPLICATE_INVESTIGATION_DIR = ROOT / "reports" / "duplicate_investigation"
BASELINE_DIR = ROOT / "experiments" / "baseline"
PREPARED_DIR = ROOT / "prepared_full_run"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ──────────────────────────────────────────────
# 1. Artifact preservation tests
# ──────────────────────────────────────────────

class TestArtifactPreservation:
    """Verify that critical source artifacts have not been modified during Phase 1.6."""

    def test_metadata_csv_checksum(self) -> None:
        path = PREPARED_DIR / "metadata.csv"
        assert path.is_file(), "metadata.csv missing"
        assert _sha256(path) == "c15f35073d4f03e6a91b13b9ff2d9076b5ece0dce7a8b0f2613d376886fc27f4"

    def test_patient_splits_csv_checksum(self) -> None:
        path = PREPARED_DIR / "patient_splits.csv"
        assert path.is_file(), "patient_splits.csv missing"
        assert _sha256(path) == "c45e0eea02f00f7c3d80f20d3f4764f758d8471300a81ff4d25ea31c2387d622"

    def test_manifest_json_checksum(self) -> None:
        path = PREPARED_DIR / "manifest.json"
        assert path.is_file(), "manifest.json missing"
        assert _sha256(path) == "4ef492323314630596da8aef0871c5e3708413aec5fe6e3796aef53b8741ca05"

    def test_gate_report_json_checksum(self) -> None:
        path = BASELINE_DIR / "gate_report.json"
        assert path.is_file(), "gate_report.json missing"
        assert _sha256(path) == "42ce324232c8b559ae27c230c533fcb562e9eff059b0c546c7d48bad381a43ff"

    def test_near_duplicate_review_csv_checksum(self) -> None:
        path = BASELINE_DIR / "near_duplicate_crossfold_review.csv"
        assert path.is_file(), "near_duplicate_crossfold_review.csv missing"
        assert _sha256(path) == "3a15554290ef8db234d7590455976576dc5766f797d5affd3b561c938b58a9d7"

    def test_duplicate_pair_review_csv_checksum(self) -> None:
        path = DUPLICATE_INVESTIGATION_DIR / "duplicate_pair_review.csv"
        assert path.is_file(), "duplicate_pair_review.csv missing"
        assert _sha256(path) == "a06e79bc379abee2968f49cd57f486fc9ba738fc209916112a04515d71b3fb09"

    def test_automated_evidence_json_checksum(self) -> None:
        path = DUPLICATE_INVESTIGATION_DIR / "automated_evidence.json"
        assert path.is_file(), "automated_evidence.json missing"
        assert _sha256(path) == "12c58b838cbf97ea05e7d0bdd9fdec729f131c985ce8f3f935100f008998dfb7"

    def test_phase_1_6_checksums_file_exists_and_consistent(self) -> None:
        checksums_path = INDEPENDENT_REVIEW_DIR / "phase_1_6_checksums.json"
        assert checksums_path.is_file(), "phase_1_6_checksums.json missing"
        checksums = json.loads(checksums_path.read_text(encoding="utf-8"))
        # Verify internal consistency: the checksums file records the same values we check above
        artifacts = checksums["artifacts"]
        assert artifacts["metadata_csv"]["sha256"] == _sha256(PREPARED_DIR / "metadata.csv")
        assert artifacts["patient_splits_csv"]["sha256"] == _sha256(PREPARED_DIR / "patient_splits.csv")
        assert artifacts["manifest_json"]["sha256"] == _sha256(PREPARED_DIR / "manifest.json")


# ──────────────────────────────────────────────
# 2. Phase 1.6 deliverable existence tests
# ──────────────────────────────────────────────

class TestPhase16Deliverables:
    """Verify all required Phase 1.6 deliverables exist and have valid structure."""

    def test_expert_review_package_exists(self) -> None:
        path = INDEPENDENT_REVIEW_DIR / "EXPERT_REVIEW_PACKAGE.md"
        assert path.is_file()
        content = path.read_text(encoding="utf-8")
        assert "SSIM" in content
        assert "reviewer_id" in content
        assert "NO-GO" in content or "no model" in content.lower()

    def test_reviewer_decision_template_exists_and_valid(self) -> None:
        path = INDEPENDENT_REVIEW_DIR / "reviewer_decision_template.csv"
        assert path.is_file()
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 236, f"Expected 236 rows, got {len(rows)}"
        # Verify required human-review fields exist and are blank
        required_human_fields = [
            "reviewer_id", "review_date", "review_decision",
            "evidence_notes", "confidence", "follow_up_required",
        ]
        for field in required_human_fields:
            assert field in rows[0], f"Missing field: {field}"
        assert all(
            row["reviewer_id"] == "" and row["review_date"] == "" and row["review_decision"] == ""
            for row in rows
        ), "Human review fields must be blank — no reviewer decisions were invented"

    def test_reviewer_template_sorted_by_ssim_descending(self) -> None:
        path = INDEPENDENT_REVIEW_DIR / "reviewer_decision_template.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        ssim_values = [float(row["export_ssim"]) for row in rows]
        assert ssim_values == sorted(ssim_values, reverse=True), "Rows must be sorted by SSIM descending"

    def test_reviewer_template_has_priority_tiers(self) -> None:
        path = INDEPENDENT_REVIEW_DIR / "reviewer_decision_template.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        tiers = {row["review_priority"] for row in rows}
        assert "tier_1_highest" in tiers, "Must have tier_1_highest priority pairs"
        tier_1_count = sum(1 for row in rows if row["review_priority"] == "tier_1_highest")
        assert tier_1_count == 2, f"Expected 2 tier_1 pairs (SSIM >= 0.80), got {tier_1_count}"

    def test_provenance_report_exists(self) -> None:
        path = INDEPENDENT_REVIEW_DIR / "PROVENANCE_REPORT.md"
        assert path.is_file()
        content = path.read_text(encoding="utf-8")
        assert "Figshare" in content or "figshare" in content
        assert "PID" in content
        assert "cvind" in content
        assert "Nanfang" in content or "Tianjin" in content

    def test_alternative_protocol_assessment_exists(self) -> None:
        path = INDEPENDENT_REVIEW_DIR / "ALTERNATIVE_PROTOCOL_ASSESSMENT.md"
        assert path.is_file()
        content = path.read_text(encoding="utf-8")
        assert "Protocol A" in content
        assert "Protocol B" in content
        assert "Protocol C" in content
        assert "Protocol D" in content
        assert "sensitivity" in content.lower()

    def test_recommendation_json_exists_and_valid(self) -> None:
        path = INDEPENDENT_REVIEW_DIR / "recommendation.json"
        assert path.is_file()
        rec = json.loads(path.read_text(encoding="utf-8"))
        assert rec["final_decision"] in {"NO-GO", "CONDITIONAL-GO", "GO"}
        assert "conditions_for_go" in rec
        assert "recommended_protocol" in rec
        assert "unresolved_limitations" in rec
        assert "prohibited_actions" in rec
        assert "artifact_checksums_verified" in rec


# ──────────────────────────────────────────────
# 3. Scientific integrity tests
# ──────────────────────────────────────────────

class TestScientificIntegrity:
    """Verify that Phase 1.6 does not violate scientific constraints."""

    def test_no_model_training_occurred(self) -> None:
        """Ensure no model checkpoints, predictions, or training logs exist."""
        for pattern in ["*.pth", "*.pt", "predictions.csv", "training_log.csv", "metrics.json"]:
            matches = list(BASELINE_DIR.glob(pattern))
            assert not matches, f"Model artifact found: {matches}"

    def test_no_pairs_pre_labeled_as_duplicate(self) -> None:
        """All pairs must remain unresolved — no automated duplicate confirmation."""
        path = DUPLICATE_INVESTIGATION_DIR / "duplicate_pair_review.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        categories = {row["automated_category"] for row in rows}
        # In the actual data, all should be 'unresolved' since no SHA/array equality was found
        for row in rows:
            assert row["automated_category"] == "unresolved", (
                f"Pair {row['pair_id']} has category '{row['automated_category']}' — "
                "only 'unresolved' is valid when no exact equality was found"
            )
            assert row["human_review_status"] == "automated_evidence_only_no_human_review"

    def test_recommendation_decision_is_not_go(self) -> None:
        """The decision must not be GO — conditions remain unmet."""
        rec = json.loads((INDEPENDENT_REVIEW_DIR / "recommendation.json").read_text(encoding="utf-8"))
        assert rec["final_decision"] != "GO", (
            "Decision must not be GO while conditions remain unmet"
        )

    def test_recommendation_has_blocking_conditions(self) -> None:
        """At least one blocking condition must exist."""
        rec = json.loads((INDEPENDENT_REVIEW_DIR / "recommendation.json").read_text(encoding="utf-8"))
        blocking = [c for c in rec["conditions_for_go"] if c.get("blocking")]
        assert len(blocking) >= 1, "Must have at least one blocking condition"

    def test_no_fold_assignments_modified(self) -> None:
        """Verify fold assignments match the original split."""
        path = PREPARED_DIR / "patient_splits.csv"
        assert _sha256(path) == "c45e0eea02f00f7c3d80f20d3f4764f758d8471300a81ff4d25ea31c2387d622"

    def test_reviewer_template_does_not_invent_reviews(self) -> None:
        """All human fields must be empty."""
        path = INDEPENDENT_REVIEW_DIR / "reviewer_decision_template.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            assert row["reviewer_id"] == "", f"reviewer_id not blank for pair {row['pair_id']}"
            assert row["review_date"] == "", f"review_date not blank for pair {row['pair_id']}"
            assert row["review_decision"] == "", f"review_decision not blank for pair {row['pair_id']}"


# ──────────────────────────────────────────────
# 4. Report determinism test
# ──────────────────────────────────────────────

class TestReportDeterminism:
    """Verify that re-reading the reviewer template produces consistent results."""

    def test_reviewer_template_pair_count_matches_evidence(self) -> None:
        """The template must cover all 236 cross-patient cross-fold pairs."""
        template_path = INDEPENDENT_REVIEW_DIR / "reviewer_decision_template.csv"
        evidence_path = DUPLICATE_INVESTIGATION_DIR / "duplicate_pair_review.csv"
        with template_path.open(newline="", encoding="utf-8-sig") as f:
            template_rows = list(csv.DictReader(f))
        with evidence_path.open(newline="", encoding="utf-8-sig") as f:
            evidence_rows = list(csv.DictReader(f))
        assert len(template_rows) == len(evidence_rows) == 236

    def test_reviewer_template_pair_ids_match_evidence(self) -> None:
        """Pair IDs in the template must match those in the evidence CSV."""
        template_path = INDEPENDENT_REVIEW_DIR / "reviewer_decision_template.csv"
        evidence_path = DUPLICATE_INVESTIGATION_DIR / "duplicate_pair_review.csv"
        with template_path.open(newline="", encoding="utf-8-sig") as f:
            template_ids = {row["pair_id"] for row in csv.DictReader(f)}
        with evidence_path.open(newline="", encoding="utf-8-sig") as f:
            evidence_ids = {row["pair_id"] for row in csv.DictReader(f)}
        assert template_ids == evidence_ids, "Pair ID sets must match exactly"
