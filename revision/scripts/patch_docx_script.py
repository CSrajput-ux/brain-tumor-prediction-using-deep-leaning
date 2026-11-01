from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
docx_py = ROOT / "revision" / "scripts" / "apply_final_manuscript_docx.py"

with open(docx_py, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Abstract Pituitary text
old_pit = "and pituitary adenomas showed minimal immediate margin dependence (τ_immed = 0.0034 vs τ_core = 0.0009; outer margin τ_outer = 0.0392, ratio 360.2%). "
new_pit = "and pituitary adenomas exhibited minimal core sensitivity (τ_core = 0.0009 vs τ_immed = 0.0034; the elevated 360.2% ratio is an exploratory mathematical artifact of a near-zero core denominator rather than biological infiltration). "
code = code.replace(old_pit, new_pit)

# 2. Update Abstract LME cohort interaction
old_lme = "non-significant cohort interaction p = 0.234"
new_lme = "non-significant cohort interaction p = 0.234, indicating no statistically significant evidence of effect modification across cohorts, though non-significance does not prove equivalence"
if new_lme not in code:
    code = code.replace(old_lme, new_lme)

# 3. Add References updates
old_ref_marker = "# Table 2"
new_ref_code = """# References 3, 4, 14 metadata updates
doc.paragraphs[182].text = "[3]\\tRossi, E.B., Lopez, E., Comminiello, D.: TACE: Tumor-Aware Counterfactual Explanations. arXiv preprint arXiv:2409.13045 (2024). https://doi.org/10.48550/arXiv.2409.13045"
set_para_text(doc.paragraphs[182], doc.paragraphs[182].text, font_size=9.5)

doc.paragraphs[183].text = "[4]\\tSourget, T., Hestbek-Møller, M., Jiménez-Sánchez, A., Xu, J.J., Cheplygina, V.: Mask of truth: model sensitivity to unexpected regions of medical images. J. Imaging Inform. Med. 38, 245–258 (2025). https://doi.org/10.1007/s10278-025-01531-5"
set_para_text(doc.paragraphs[183], doc.paragraphs[183].text, font_size=9.5)

doc.paragraphs[193].text = "[14]\\tDeGrave, A.J., Janizek, J.D., Lee, S.-I.: AI for radiographic COVID-19 detection selects shortcuts over signal. Nat. Mach. Intell. 3(7), 610–619 (2021). https://doi.org/10.1038/s42256-021-00338-7"
set_para_text(doc.paragraphs[193], doc.paragraphs[193].text, font_size=9.5)

# Table 2"""
code = code.replace(old_ref_marker, new_ref_code)

with open(docx_py, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated apply_final_manuscript_docx.py successfully.")

