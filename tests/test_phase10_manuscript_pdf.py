"""Phase 10 verification test for research manuscript and generated publication PDF."""

from pathlib import Path
import pypdf

ROOT = Path(__file__).resolve().parent.parent


def test_manuscript_markdown_exists_and_complete():
    """Verify paper/manuscript.md exists and contains all required sections."""
    md_path = ROOT / "paper" / "manuscript.md"
    assert md_path.exists(), "paper/manuscript.md does not exist"
    content = md_path.read_text(encoding="utf-8")
    assert len(content) > 20000, f"Manuscript content too short ({len(content)} chars)"

    required_headers = [
        "# Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence",
        "## Abstract",
        "### Background",
        "### Methods",
        "### Results",
        "### Discussion",
        "## 1. Introduction",
        "## 2. Related Work",
        "## 3. Datasets, Provenance & Data Leakage Audit",
        "## 4. Materials and Methods",
        "## 5. Experimental Results",
        "## 6. Discussion",
        "## 7. Reproducibility & Open Science",
        "## 8. Figure Captions",
        "## 9. References",
    ]
    for header in required_headers:
        assert header in content, f"Missing required header: {header}"


def test_manuscript_html_and_pdf_exist_and_valid():
    """Verify generated PDF exists, has >= 10 pages, non-empty, and embeds all 10 figures."""
    pdf_path = ROOT / "paper" / "manuscript.pdf"
    html_path = ROOT / "paper" / "manuscript.html"

    assert html_path.exists(), "paper/manuscript.html does not exist"
    assert pdf_path.exists(), "paper/manuscript.pdf does not exist"

    # PDF size should be > 1 MB (since it embeds 10 high-res PNG figures)
    assert pdf_path.stat().st_size > 1_000_000, f"PDF file size suspiciously small: {pdf_path.stat().st_size} bytes"

    reader = pypdf.PdfReader(str(pdf_path))
    assert len(reader.pages) >= 12, f"Expected at least 12 pages in publication PDF, got {len(reader.pages)}"

    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() + "\n"

    # Verify core title and content
    assert "Tumour-Core" in extracted_text or "Counterfactual" in extracted_text
    assert "DeiT-Small" in extracted_text
    assert "ResNet-50" in extracted_text

    # Verify all 10 figures are present in the PDF text
    for i in range(1, 11):
        assert f"Figure {i}:" in extracted_text, f"Figure {i} missing from PDF text"

