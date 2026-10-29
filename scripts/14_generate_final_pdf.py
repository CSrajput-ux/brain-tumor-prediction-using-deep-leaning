"""Compile Brain_MRI_Research_Paper_Final.md into Brain_MRI_Research_Paper_Final.pdf."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import importlib

gen_pdf = importlib.import_module("scripts.12_generate_manuscript_pdf")
build_manuscript_html = gen_pdf.build_manuscript_html
generate_pdf = gen_pdf.generate_pdf
verify_pdf = gen_pdf.verify_pdf


def main():
    md_path = ROOT / "Brain_MRI_Research_Paper_Final.md"
    html_path = ROOT / "Brain_MRI_Research_Paper_Final.html"
    pdf_path = ROOT / "Brain_MRI_Research_Paper_Final.pdf"
    figures_dir = ROOT / "figures"

    print(f"Building HTML from {md_path}...")
    html_content = build_manuscript_html(md_path, figures_dir)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"Saved HTML to {html_path} ({len(html_content):,} chars)")

    print(f"Rendering PDF with Chrome headless to {pdf_path}...")
    generate_pdf(html_path, pdf_path)

    metrics = verify_pdf(pdf_path)
    print("\n=== Final PDF Verification ===")
    print(f"PDF Location: {pdf_path}")
    print(f"Total Pages:  {metrics['num_pages']}")
    print(f"File Size:    {metrics['file_size_kb']:.1f} KB")
    print(f"Title Check:  {'PASS' if metrics['has_title'] else 'FAIL'}")
    print("==============================\n")


if __name__ == "__main__":
    main()
