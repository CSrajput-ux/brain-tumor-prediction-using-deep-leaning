import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PUB_DIR = ROOT / 'publication' / 'manuscript_v1'
FIG_DIR = PUB_DIR / 'figures'
TAB_DIR = PUB_DIR / 'tables'


def test_publication_package_deliverables_exist():
    """Verify all 16 required publication deliverables exist and are non-empty."""
    required = [
        'manuscript.md',
        'manuscript.docx',
        'abstract.md',
        'figure_captions.md',
        'supplementary_methods.md',
        'supplementary_results.md',
        'references.bib',
        'reference_verification.csv',
        'claim_evidence_matrix.csv',
        'reproducibility_checklist.md',
        'missing_evidence_and_author_questions.md',
        'manuscript_quality_audit.md',
        'README.md'
    ]
    for fname in required:
        fpath = PUB_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"


def test_all_publication_figures_exist_in_png_and_pdf():
    """Verify all 10 figures exist in both high-res PNG and vector PDF format."""
    for i in range(1, 11):
        # find matching png and pdf
        pngs = list(FIG_DIR.glob(f"fig{i}_*.png"))
        pdfs = list(FIG_DIR.glob(f"fig{i}_*.pdf"))
        assert len(pngs) == 1, f"Missing or multiple PNG for Figure {i}: {pngs}"
        assert len(pdfs) == 1, f"Missing or multiple PDF for Figure {i}: {pdfs}"
        assert pngs[0].stat().st_size > 10000, f"Figure {i} PNG unexpectedly small"
        assert pdfs[0].stat().st_size > 10000, f"Figure {i} PDF unexpectedly small"


def test_publication_tables_numerical_fidelity():
    """Verify publication tables match canonical metrics and contrast numbers."""
    t4 = pd.read_csv(TAB_DIR / 'table4_baseline_metrics.csv')
    assert len(t4) == 3
    s0_c0 = t4[t4['scenario'] == 'S0'].iloc[0]
    assert np.isclose(s0_c0['macro_f1'], 0.9333, atol=1e-3)
    
    t5 = pd.read_csv(TAB_DIR / 'table5_intervention_metrics.csv')
    assert len(t5) == 18, f"Expected 18 rows (3 scenarios x 6 conditions), got {len(t5)}"
    s0_c1 = t5[(t5['scenario'] == 'S0') & (t5['condition'] == 'C1_historical_dc_offset')].iloc[0]
    assert np.isclose(s0_c1['macro_f1'], 0.6290, atol=1e-3)
    
    s0_c2 = t5[(t5['scenario'] == 'S0') & (t5['condition'] == 'C2_seam_suppressed')].iloc[0]
    assert np.isclose(s0_c2['macro_f1'], 0.4525, atol=1e-3)
    
    t6 = pd.read_csv(TAB_DIR / 'table6_canonical_contrasts.csv')
    assert len(t6) in (15, 27), f"Expected 27 or 15 canonical contrasts, got {len(t6)}"
    c2_vs_c0_s0 = t6[(t6['scenario'] == 'S0') & (t6['contrast_id'] == 'C2_vs_C0')].iloc[0]
    assert np.isclose(c2_vs_c0_s0['signed_difference_A_minus_B'], 0.4808, atol=1e-3)
    assert c2_vs_c0_s0['bootstrap_ci_lower'] > 0.40


def test_manuscript_docx_validity():
    """Verify that manuscript.docx is a valid, readable Word document."""
    import docx
    doc = docx.Document(PUB_DIR / 'manuscript.docx')
    assert len(doc.paragraphs) > 50, "DOCX has too few paragraphs"
    assert len(doc.tables) >= 2, "DOCX has too few tables"


def test_manuscript_claims_and_safeguards():
    """Verify that manuscript.md enforces required claim boundaries."""
    md_text = (PUB_DIR / 'manuscript.md').read_text(encoding='utf-8')
    assert "Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity" in md_text
    assert "72.2%" in md_text
    assert "shortcut" in md_text.lower()
    assert "limitations" in md_text.lower()
    assert "declarations" in md_text.lower()
