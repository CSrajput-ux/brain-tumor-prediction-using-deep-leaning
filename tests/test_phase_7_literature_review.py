import json
import hashlib
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PHASE_7_DIR = ROOT / 'experiments' / 'phase_7_literature_review'

def test_phase_7_required_artifacts_exist():
    """Verify all 15 required Phase 7 deliverables exist and are non-empty."""
    required = [
        'PHASE_7_SYSTEMATIC_REVIEW_REPORT.md',
        'search_protocol.md',
        'search_log.csv',
        'screening_log.csv',
        'prior_art_matrix.csv',
        'intervention_comparison_matrix.csv',
        'five_research_questions.md',
        'research_gap_statement.md',
        'novelty_claim_matrix.csv',
        'additional_experiment_decision.md',
        'bibliography.bib',
        'reference_verification.csv',
        'PRISMA_flow.md',
        'limitations_and_uncertainty.md',
        'checksums.json'
    ]
    for fname in required:
        fpath = PHASE_7_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"

def test_phase_7_checksum_integrity():
    """Verify recorded SHA-256 hashes in checksums.json match files on disk."""
    with open(PHASE_7_DIR / 'checksums.json', 'r') as f:
        recorded = json.load(f)
    for fname, meta in recorded.items():
        fpath = PHASE_7_DIR / fname
        assert fpath.exists(), f"File {fname} from checksums.json does not exist!"
        h = hashlib.sha256()
        with open(fpath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        assert h.hexdigest() == meta['sha256'], f"SHA-256 mismatch for {fname}"
        assert fpath.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_phase_7_csv_integrity_and_columns():
    """Verify that all generated CSVs have valid structures and required headers."""
    prior_art = pd.read_csv(PHASE_7_DIR / 'prior_art_matrix.csv')
    assert len(prior_art) >= 10, "Prior art matrix contains fewer than 10 core studies"
    assert 'DOI' in prior_art.columns
    assert 'relevance_to_our_work' in prior_art.columns
    
    interventions = pd.read_csv(PHASE_7_DIR / 'intervention_comparison_matrix.csv')
    assert len(interventions) >= 10, "Intervention matrix contains fewer than 10 interventions"
    assert 'intervention_method' in interventions.columns
    
    novelty = pd.read_csv(PHASE_7_DIR / 'novelty_claim_matrix.csv')
    assert len(novelty) == 10, "Novelty matrix must evaluate exactly the 10 audited claims"
    assert 'final_status' in novelty.columns

def test_phase_7_report_gate_decision_and_epistemic_humility():
    """Verify that report concludes PASS and prohibits causal/biological overclaiming."""
    with open(PHASE_7_DIR / 'PHASE_7_SYSTEMATIC_REVIEW_REPORT.md', 'r', encoding='utf-8') as f:
        content = f.read()
    assert "**Final Gate Decision:** **`PASS`**" in content
    assert "NOT_SUPPORTED_BY_CURRENT_EVIDENCE" in content or "prohibited" in content.lower()
    assert "Bissoto" in content
    assert "DeGrave" in content
    assert "Cheng" in content
