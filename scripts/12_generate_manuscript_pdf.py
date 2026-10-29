"""Generate publication-quality PDF from paper/manuscript.md.

This script parses paper/manuscript.md, integrates all 10 high-resolution
publication figures from figures/ (base64-encoded for guaranteed offline rendering),
applies journal-quality typography (Medical Image Analysis / IEEE TMI styling),
renders tables and equations, and exports paper/manuscript.pdf via headless Chrome.
"""

from __future__ import annotations

import base64
import os
import re
import subprocess
import sys
from pathlib import Path

import markdown
import pypdf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def encode_image_base64(image_path: Path) -> str:
    """Read an image file and return its data URI string."""
    with open(image_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    suffix = image_path.suffix.lower().replace(".", "")
    mime = "image/png" if suffix == "png" else f"image/{suffix}"
    return f"data:{mime};base64,{b64}"


def build_figure_html(fig_num: int, title: str, caption: str, img_data_uri: str) -> str:
    """Format a publication figure with image container and caption."""
    return f"""
    <div class="figure-container" id="fig{fig_num}">
        <div class="figure-image-wrapper">
            <img src="{img_data_uri}" alt="Figure {fig_num}: {title}" class="figure-image" />
        </div>
        <div class="figure-caption">
            <strong>Figure {fig_num}: {title}.</strong> {caption}
        </div>
    </div>
    """


def clean_math_for_html(text: str) -> str:
    """Convert common LaTeX math notations to clean typographic representations.

    Replaces standard mathematical and statistical symbols with appropriate HTML entities.
    """
    # Replace display math $$...$$
    def replace_display_math(match: re.Match) -> str:
        eq = match.group(1).strip()
        # Clean common math patterns
        eq_clean = (
            eq.replace(r"\tilde{x}", "x&#771;")
            .replace(r"\text{clip}", "clip")
            .replace(r"\text{mean}", "mean")
            .replace(r"\text{std}", "std")
            .replace(r"\text{sham}", "sham")
            .replace(r"\text{edit}, r", "edit, r")
            .replace(r"\text{core}", "core")
            .replace(r"\tau_{core}", "&tau;<sub>core</sub>")
            .replace(r"\tau_r", "&tau;<sub>r</sub>")
            .replace(r"\Delta_r", "&Delta;<sub>r</sub>")
            .replace(r"\Delta_{sham}", "&Delta;<sub>sham</sub>")
            .replace(r"\oplus", "&oplus;")
            .replace(r"\setminus", "&#8726;")
            .replace(r"\cap", "&cap;")
            .replace(r"\cup", "&cup;")
            .replace(r"\emptyset", "&empty;")
            .replace(r"\equiv", "&equiv;")
            .replace(r"\forall", "&forall;")
            .replace(r"\notin", "&notin;")
            .replace(r"\mathbb{I}", "<b>1</b>")
            .replace(r"\arg\max", "arg max")
            .replace(r"\ne", "&ne;")
            .replace(r"\mathcal{N}", "<i>N</i>")
            .replace(r"\mu_{local}", "&mu;<sub>local</sub>")
            .replace(r"\sigma_{local}", "&sigma;<sub>local</sub>")
            .replace(r"\times", "&times;")
            .replace(r"\le", "&le;")
            .replace(r"\ge", "&ge;")
        )
        return f'<div class="display-math"><span class="equation">{eq_clean}</span></div>'

    # Replace display math
    text = re.sub(r"\$\$(.*?)\$\$", replace_display_math, text, flags=re.DOTALL)

    # Replace inline math $...$
    def replace_inline_math(match: re.Match) -> str:
        eq = match.group(1).strip()
        eq_clean = (
            eq.replace(r"\tau_{core}", "&tau;<sub>core</sub>")
            .replace(r"\tau_{immediate}", "&tau;<sub>immediate</sub>")
            .replace(r"\tau_{immed}", "&tau;<sub>immed</sub>")
            .replace(r"\tau_{outer}", "&tau;<sub>outer</sub>")
            .replace(r"\tau_{remote}", "&tau;<sub>remote</sub>")
            .replace(r"\tau_{sham}", "&tau;<sub>sham</sub>")
            .replace(r"\tau_{diff}", "&tau;<sub>diff</sub>")
            .replace(r"\tau_{core, ViT}", "&tau;<sub>core, ViT</sub>")
            .replace(r"\tau_{core, CNN}", "&tau;<sub>core, CNN</sub>")
            .replace(r"\tau_{ViT}", "&tau;<sub>ViT</sub>")
            .replace(r"\tau_{CNN}", "&tau;<sub>CNN</sub>")
            .replace(r"\tau_r", "&tau;<sub>r</sub>")
            .replace(r"\Delta_r", "&Delta;<sub>r</sub>")
            .replace(r"\Delta_{sham}", "&Delta;<sub>sham</sub>")
            .replace(r"\Delta", "&Delta;")
            .replace(r"\mu", "&mu;")
            .replace(r"\sigma", "&sigma;")
            .replace(r"\rho", "&rho;")
            .replace(r"\times", "&times;")
            .replace(r"\le", "&le;")
            .replace(r"\ge", "&ge;")
            .replace(r"\ne", "&ne;")
            .replace(r"\approx", "&asymp;")
            .replace(r"\pm", "&plusmn;")
            .replace(r"\cdot", "&middot;")
            .replace(r"R_{core}", "<i>R</i><sub>core</sub>")
            .replace(r"R_{immediate}", "<i>R</i><sub>immediate</sub>")
            .replace(r"R_{outer}", "<i>R</i><sub>outer</sub>")
            .replace(r"R_{remote}", "<i>R</i><sub>remote</sub>")
            .replace(r"R_{sham}", "<i>R</i><sub>sham</sub>")
            .replace(r"d_z", "<i>d</i><sub>z</sub>")
            .replace(r"p_y", "<i>p</i><sub>y</sub>")
            .replace(r"p(x)", "<i>p(x)</i>")
            .replace(r"x_{edit, r}", "<i>x</i><sub>edit, r</sub>")
            .replace(r"P_1", "<i>P</i><sub>1</sub>")
            .replace(r"P_{99}", "<i>P</i><sub>99</sub>")
            .replace(r"H_0", "<i>H</i><sub>0</sub>")
            .replace(r"N=", "<i>N</i> = ")
            .replace(r"p <", "<i>p</i> &lt;")
            .replace(r"p >", "<i>p</i> &gt;")
            .replace(r"p =", "<i>p</i> =")
        )
        return f'<span class="inline-math">{eq_clean}</span>'

    text = re.sub(r"\$([^\$\n]+?)\$", replace_inline_math, text)
    return text


def build_manuscript_html(md_path: Path, figures_dir: Path) -> str:
    """Parse Markdown, embed figures and equations, and wrap in journal styling."""
    raw_md = md_path.read_text(encoding="utf-8")

    # Mapping of figure number to filename and metadata
    fig_data = {
        1: ("fig1_study_design.png", "Study Design & Sham-Controlled Counterfactual Intervention Pipeline",
            "Flowchart depicting data ingestion, duplicate leakage audits, patient-isolated cross-validation, 5-region intervention engine, dual perturbation engines, and biostatistical evaluation across ResNet-50 and DeiT-Small."),
        2: ("fig2_preprocessing_alignment.png", "Preprocessing Pipeline & Mask Geometric Alignment Verification",
            "Multi-panel diagnostic display illustrating raw slice, percentile intensity scaling [P1, P99], aspect-ratio-preserving letterbox padding (224 × 224), and binary mask boundary alignment."),
        3: ("fig3_calibration_reliability.png", "Reliability Diagrams & Calibration Curves",
            "Empirical calibration curves and Expected Calibration Error (ECE) comparing ResNet-50 and DeiT-Small across Cheng patient out-of-fold validation and BRISC clean test sets."),
        4: ("fig4_regional_evidence_effects.png", "Regional Evidence Sensitivity Across Architectures (Method A: Inpainting)",
            "Bar chart comparing sham-corrected sensitivity (tau_r) across Tumour Core, Immediate Margin (4px), Outer Margin (12px), and Remote Context with paired Wilcoxon significance indicators."),
        5: ("fig5_architecture_comparison.png", "Architectural Inductive Bias: ViT vs CNN Regional Sensitivity Profile",
            "Difference plot (tau_ViT - tau_CNN) highlighting DeiT-Small's enhanced reliance on intra-lesion core and transitional margin evidence."),
        6: ("fig6_method_robustness.png", "Perturbation Method Invariance (Method A vs Method B)",
            "Paired sensitivity comparison between Telea boundary PDE inpainting and locally matched Gaussian texture filling across ResNet-50 and DeiT-Small."),
        7: ("fig7_plane_stratification.png", "Imaging Plane Stratification of Regional Evidence (BRISC)",
            "Regional evidence sensitivity stratified across Axial (N=15), Coronal (N=15), and Sagittal (N=15) acquisition planes."),
        8: ("fig8_class_heterogeneity.png", "Class Heterogeneity in Peritumoral vs Core Evidence",
            "Comparative sensitivity and margin-to-core ratios across Meningiomas, Gliomas, and Pituitary adenomas."),
        9: ("fig9_brisc_leakage_artifact.png", "Impact of Train-Test Duplicate Leakage on Benchmark Evaluation (BRISC)",
            "Dual-benchmark comparison between the Contaminated Official Test (N=1,000, 10.1% leakage) and the Clean De-duplicated Test (N=899)."),
        10: ("fig10_intervention_gallery.png", "Counterfactual Intervention & Residual Montage Gallery",
             "High-resolution 8-panel diagnostic gallery displaying original slice, 5-color segmentation topology, Method A inpainted core/sham, Method B texture-filled core/sham, and residual difference maps.")
    }

    # Encode all figures to base64 URIs
    fig_uris = {}
    for num, (filename, _, _) in fig_data.items():
        img_path = figures_dir / filename
        if img_path.exists():
            fig_uris[num] = encode_image_base64(img_path)
        else:
            print(f"Warning: Figure {filename} not found in {figures_dir}")
            fig_uris[num] = ""

    # Replace Section 8 (Figure Captions) with full embedded figure containers
    fig_html_blocks = []
    for num in range(1, 11):
        filename, title, caption = fig_data[num]
        uri = fig_uris.get(num, "")
        if uri:
            fig_html_blocks.append(build_figure_html(num, title, caption, uri))

    all_figs_html = "\n".join(fig_html_blocks)

    # Pre-clean LaTeX math in markdown
    cleaned_md = clean_math_for_html(raw_md)

    # Convert Markdown to HTML
    html_body = markdown.markdown(
        cleaned_md,
        extensions=["tables", "fenced_code", "sane_lists", "toc"]
    )

    # Replace the Figure Captions list with the rich embedded figures
    pattern_fig_section = re.compile(r"<h2[^>]*>(?:8\.\s*Figure Captions|Appendix A:.*?Figures.*?)</h2>\s*<ul>.*?</ul>", re.DOTALL)
    replacement_fig_section = f"<h2 id='figures-visual-evidence'>Appendix A: Figures & Visual Evidence Gallery</h2>\n<div class='figures-gallery'>{all_figs_html}</div>"
    html_body = pattern_fig_section.sub(replacement_fig_section, html_body)

    # Wrap Abstract in styled card
    pattern_abstract = re.compile(r"<h2[^>]*>Abstract</h2>\s*<h3[^>]*>Background</h3>(.*?)<hr />", re.DOTALL)
    def wrap_abstract(match: re.Match) -> str:
        content = match.group(1)
        return f"""
        <div class="abstract-box">
            <h2 class="abstract-title">Structured Abstract</h2>
            <h3>Background</h3>
            {content}
        </div>
        <hr class="abstract-divider" />
        """
    html_body = pattern_abstract.sub(wrap_abstract, html_body)

    # Compose full HTML document with MedIA/TMI CSS styling
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 18mm 22mm 18mm;
        @bottom-right {{
            content: "Page " counter(page);
            font-size: 8.5pt;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            color: #718096;
        }}
        @top-left {{
            content: "Region-Resolved Counterfactual Evidence in Brain Tumour MRI";
            font-size: 8pt;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            color: #a0aec0;
            font-style: italic;
        }}
    }}

    body {{
        font-family: "Georgia", "Times New Roman", serif;
        font-size: 10.5pt;
        line-height: 1.6;
        color: #1a202c;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}

    /* Title & Metadata Header */
    h1 {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 20pt;
        font-weight: 700;
        line-height: 1.25;
        color: #0f2d59;
        margin-top: 0;
        margin-bottom: 14pt;
        border-bottom: 2.5pt solid #0f2d59;
        padding-bottom: 10pt;
    }}

    h2 {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 13pt;
        font-weight: 700;
        color: #1e3a8a;
        margin-top: 18pt;
        margin-bottom: 8pt;
        border-bottom: 1pt solid #e2e8f0;
        padding-bottom: 4pt;
        page-break-after: avoid;
    }}

    h3 {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 11pt;
        font-weight: 600;
        color: #2b6cb0;
        margin-top: 12pt;
        margin-bottom: 4pt;
        page-break-after: avoid;
    }}

    p {{
        margin-top: 0;
        margin-bottom: 8pt;
        text-align: justify;
    }}

    strong {{
        font-weight: 600;
        color: #0f172a;
    }}

    /* Abstract Box */
    .abstract-box {{
        background-color: #f8fafc;
        border: 1pt solid #cbd5e1;
        border-left: 4pt solid #1e3a8a;
        padding: 12pt 14pt;
        margin-top: 14pt;
        margin-bottom: 14pt;
        border-radius: 4pt;
        page-break-inside: avoid;
    }}

    .abstract-title {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 12pt;
        color: #1e3a8a;
        border: none;
        margin-top: 0;
        margin-bottom: 8pt;
        padding: 0;
    }}

    .abstract-divider {{
        border: none;
        border-top: 1pt solid #e2e8f0;
        margin: 16pt 0;
    }}

    /* Tables */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10pt;
        margin-bottom: 14pt;
        font-size: 8.5pt;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        page-break-inside: avoid;
    }}

    th {{
        background-color: #1e3a8a;
        color: #ffffff;
        font-weight: 600;
        text-align: left;
        padding: 6pt 8pt;
        border: 1pt solid #1e3a8a;
    }}

    td {{
        padding: 5pt 8pt;
        border: 1pt solid #e2e8f0;
        vertical-align: middle;
    }}

    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}

    /* Figures */
    .figure-container {{
        margin-top: 14pt;
        margin-bottom: 20pt;
        page-break-inside: avoid;
        text-align: center;
        border: 1pt solid #e2e8f0;
        padding: 10pt;
        background-color: #ffffff;
        border-radius: 4pt;
        box-shadow: 0 1pt 3pt rgba(0,0,0,0.05);
    }}

    .figure-image-wrapper {{
        width: 100%;
        margin-bottom: 8pt;
    }}

    .figure-image {{
        max-width: 95%;
        max-height: 520pt;
        height: auto;
        display: block;
        margin: 0 auto;
        border-radius: 2pt;
    }}

    .figure-caption {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        font-size: 8.5pt;
        line-height: 1.45;
        color: #334155;
        text-align: left;
        padding: 4pt 6pt;
        background-color: #f8fafc;
        border-radius: 3pt;
        border-left: 2.5pt solid #2563eb;
    }}

    /* Math & Symbols */
    .inline-math {{
        font-family: "Cambria Math", "Times New Roman", serif;
        font-style: italic;
    }}

    .display-math {{
        text-align: center;
        margin: 8pt 0;
        font-family: "Cambria Math", "Times New Roman", serif;
        font-size: 11pt;
        background-color: #f8fafc;
        padding: 6pt;
        border-radius: 3pt;
        page-break-inside: avoid;
    }}

    /* Lists */
    ul, ol {{
        margin-top: 2pt;
        margin-bottom: 8pt;
        padding-left: 18pt;
    }}

    li {{
        margin-bottom: 3pt;
    }}

    /* Code & Pre */
    code {{
        font-family: "Consolas", "Courier New", monospace;
        font-size: 9pt;
        background-color: #f1f5f9;
        padding: 1pt 3pt;
        border-radius: 2pt;
        color: #0f172a;
    }}

    pre {{
        background-color: #f8fafc;
        border: 1pt solid #e2e8f0;
        border-left: 3pt solid #64748b;
        padding: 8pt 10pt;
        font-size: 8.5pt;
        font-family: "Consolas", monospace;
        overflow-x: auto;
        page-break-inside: avoid;
        margin: 8pt 0;
    }}

    /* References */
    ol li {{
        margin-bottom: 6pt;
        font-size: 9.5pt;
        line-height: 1.45;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""
    return full_html


def generate_pdf(html_path: Path, pdf_path: Path) -> Path:
    """Invoke Chrome headless to print html_path to pdf_path."""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    browser_exe = chrome_path if Path(chrome_path).exists() else edge_path
    if not Path(browser_exe).exists():
        raise FileNotFoundError(f"Neither Chrome nor Edge was found at {chrome_path} or {edge_path}")

    # Build file URI
    html_uri = html_path.resolve().as_uri()

    args = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_uri,
    ]

    print(f"Executing: {browser_exe} to produce {pdf_path}")
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    if not pdf_path.exists():
        raise RuntimeError(f"Browser completed but PDF was not created: {result.stderr}")

    return pdf_path


def verify_pdf(pdf_path: Path) -> dict:
    """Verify generated PDF with pypdf and extract core metrics."""
    reader = pypdf.PdfReader(str(pdf_path))
    num_pages = len(reader.pages)
    file_size_kb = pdf_path.stat().st_size / 1024

    first_page_text = reader.pages[0].extract_text()
    has_title = "Tumour-Core" in first_page_text or "Counterfactual" in first_page_text

    return {
        "num_pages": num_pages,
        "file_size_kb": file_size_kb,
        "has_title": has_title,
    }


def main():
    paper_dir = ROOT / "paper"
    figures_dir = ROOT / "figures"
    md_path = paper_dir / "manuscript.md"
    html_path = paper_dir / "manuscript.html"
    pdf_path = paper_dir / "manuscript.pdf"

    print(f"Reading manuscript from {md_path}...")
    html_content = build_manuscript_html(md_path, figures_dir)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"Saved styled HTML to {html_path} ({len(html_content):,} chars)")

    print(f"Rendering PDF with Chrome headless to {pdf_path}...")
    generate_pdf(html_path, pdf_path)

    metrics = verify_pdf(pdf_path)
    print("\n=== PDF Generation Verification ===")
    print(f"PDF Location: {pdf_path}")
    print(f"Total Pages:  {metrics['num_pages']}")
    print(f"File Size:    {metrics['file_size_kb']:.1f} KB")
    print(f"Title Check:  {'PASS' if metrics['has_title'] else 'FAIL'}")
    print("===================================\n")


if __name__ == "__main__":
    main()
