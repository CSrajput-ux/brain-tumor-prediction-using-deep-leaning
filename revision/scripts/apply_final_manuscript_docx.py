"""Perform complete scientific revision of all retained Word documents and compile PDFs."""
import sys, re
from pathlib import Path
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import pandas as pd
import win32com.client
import pythoncom

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
REV_DIR = ROOT / "revision"

backup_docx = ROOT / "brain _tumar_research_ORIGINAL_BACKUP.docx"
doc = docx.Document(str(backup_docx))
print(f"Loaded {backup_docx}: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables.")

# 1. Update Figures
image_map = {
    35: REV_DIR / "figures" / "fig1_study_design.png",
    49: REV_DIR / "figures" / "fig2_preprocessing_alignment.png",
    90: REV_DIR / "figures" / "fig3_calibration_reliability.png",
    96: REV_DIR / "figures" / "fig4_intervention_gallery.png",
    104: REV_DIR / "figures" / "fig5_regional_evidence_effects.png",
    115: REV_DIR / "figures" / "fig6_architecture_comparison.png",
    122: REV_DIR / "figures" / "fig7_method_robustness.png",
    126: REV_DIR / "figures" / "fig8_plane_stratification.png",
    132: REV_DIR / "figures" / "fig9_class_heterogeneity.png",
    141: REV_DIR / "figures" / "fig10_brisc_leakage_artifact.png",
}

for p_idx, png_path in image_map.items():
    if p_idx < len(doc.paragraphs):
        p = doc.paragraphs[p_idx]
        r_ids = re.findall(r'r:embed="([^"]+)"', p._p.xml)
        for rid in r_ids:
            if rid in doc.part.related_parts:
                part = doc.part.related_parts[rid]
                part._blob = png_path.read_bytes()

def set_para_text(p, new_text, font_name="Times New Roman", font_size=10.0, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p.text = new_text
    p.alignment = align
    for r in p.runs:
        r.font.name = font_name
        r.font.size = Pt(font_size)
        r.bold = bold
        r.italic = italic

# P01: Author block
doc.paragraphs[1].text = "Chhotu Rajput1* and Rishi Gupta2"
doc.paragraphs[1].alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in doc.paragraphs[1].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True

# P07: Abstract with verified statistical reconciliations
p7_text = (
    "Deep convolutional neural networks (CNNs) and Vision Transformers (ViTs) can achieve high benchmark performance on brain MRI classification, "
    "but performance on unmodified images does not establish which anatomical regions support a prediction. Tumour-core morphology, adjacent peritumoral tissue, "
    "remote parenchyma and generic image-perturbation effects should be distinguished before model behaviour is interpreted as clinically meaningful evidence. "
    "We conducted a sham-controlled, region-resolved counterfactual audit on two contrast-enhanced MRI cohorts: the Cheng dataset (3,064 slices from 233 patients; "
    "three tumour classes) and the multi-plane BRISC dataset (6,000 slices; glioma, meningioma, pituitary tumour and no-tumour classes). "
    "Cheng partitions were generated with patient-grouped five-fold stratification; the exported baseline prediction file represents the held-out Fold 1 partition "
    "(480 slices from 49 patients), not pooled predictions from all five folds. ResNet-50 and DeiT-Small/16 were fine-tuned from ImageNet-pretrained weights. "
    "For each eligible tumour-containing slice we defined the tumour core, a 4-pixel immediate margin, a 12-pixel outer margin, remote tissue and a contralateral sham region, "
    "and perturbed each region with Telea inpainting and locally matched Gaussian texture filling. Technical non-target pixel invariance (|Δ| < 10⁻⁵) was verified across an "
    "image quality control pool of 120 slices (60 per dataset; 1,200 intervention records). The model sensitivity audit evaluated 90 matched slices (45 per dataset), "
    "two architectures, five regions and two perturbation methods (1,800 paired prediction observations). Effects were summarised as raw changes in ground-truth-class probability "
    "and sham-corrected sensitivity (τ_r), evaluated using paired Wilcoxon tests, family-wise Holm adjustment, cluster-level analyses across 55 evaluation units (10 Cheng patient clusters and 45 BRISC image-level clusters), "
    "and linear mixed-effects models. On the Cheng Fold 1 partition, DeiT-Small achieved accuracy 0.8458, macro-F1 0.8403 and expected calibration error (ECE) 0.0366; "
    "ResNet-50 achieved 0.7583, 0.7190 and 0.1835. On the BRISC clean 899-image test set, DeiT-Small achieved accuracy 0.8265 and macro-F1 0.8344, against 0.6963 and 0.6991 for ResNet-50. "
    "For DeiT-Small on Cheng, Telea removal of the tumour core yielded a mean sham-corrected sensitivity of 0.1282 (slice-level Wilcoxon p = 9.13×10⁻⁶; condition-level Holm-adjusted p = 3.65×10⁻⁵; "
    "patient-clustered two-sided Wilcoxon W = 8.0, p = 0.0488 [one-sided W = 47.0, p = 0.0244] across N = 10 patient clusters); the corresponding ResNet-50 value was 0.0311 (condition-level Holm-adjusted p = 2.62×10⁻³; patient-clustered p = 0.0488). "
    "On BRISC, DeiT-Small core sensitivity was 0.0517 (raw two-sided p = 0.0320; condition-level Holm-adjusted p = 0.0639; 32-test family Holm-adjusted p = 0.6072, not significant after family-wise error rate control under either strategy). "
    "The pooled analysis comprised 10 verified Cheng patient-level clusters and 45 BRISC image-level sample clusters (patient-level linkage within BRISC was unavailable; therefore, the BRISC units should not be interpreted as 45 independently verified patients; cluster-level Wilcoxon W = 483.0, p = 0.0162; paired t-test t(54) = 3.29, p = 0.00177; Linear Mixed Model fixed effect β = +0.074, SE = 0.020, z = 3.756, p < 0.001; non-significant cohort interaction p = 0.234). "
    "Exploratory radiologic analysis showed that gliomas exhibited a substantial immediate-margin-to-core sensitivity ratio (67.2%; τ_immed = 0.0268 vs τ_core = 0.0398), meningiomas exhibited pronounced core reliance (τ_core = 0.3438 vs τ_immed = 0.0338; ratio 9.8%), and pituitary adenomas showed minimal immediate margin dependence (τ_immed = 0.0034 vs τ_core = 0.0009; outer margin τ_outer = 0.0392, ratio 360.2%). "
    "Remote-region effects were not statistically distinguishable from sham in primary comparisons. In the evaluated BRISC archive, 159 exact duplicate pairs and 101 cross-split test matches were identified; this archive-specific finding was addressed by evaluating both official (N = 1,000) and clean (N = 899) partitions. These experiments provide a retrospective mechanistic audit of spatial reliance in single-run baseline models, not clinical validation or evidence of diagnostic deployability."
)
set_para_text(doc.paragraphs[7], p7_text, font_size=10.0)

# P041: Add deterministic slice selection rule & sample accounting
p41_text = (
    "Paired counterfactual observations (N = 1,800) and sample accounting. Two distinct sample sets were constructed: (i) an Image Quality Control (QC) pool "
    "of 120 unique slices (60 Cheng, 60 BRISC; 1,200 records in manifests/intervention_qc.csv) to verify 100% mathematical non-target pixel invariance (|Δ| < 10⁻⁵ outside edited masks); "
    "and (ii) a primary Model Evaluation pool of 90 balanced slices (45 Cheng, 45 BRISC; 1,800 paired predictions in predictions/intervention_effects.csv across 2 models × 5 regions × 2 methods). "
    "Slices for model evaluation were selected deterministically in sequential index order of the test manifests, taking the first 15 mask-containing slices meeting technical invariance "
    "per tumour class for Cheng (15 gliomas, 15 meningiomas, 15 pituitary adenomas, originating from N = 10 patient clusters) and the first 5 slices per (class × plane) cell for BRISC "
    "(5 glioma + 5 meningioma + 5 pituitary across axial, coronal, and sagittal planes = exactly 15 slices per plane). No post-hoc cherry-picking or manual reordering was applied."
)
set_para_text(doc.paragraphs[41], p41_text, font_size=10.0)

# P052: Sham placement empirical guarantees & outlier disclosure
p52_text = (
    "Contralateral sham controls were constructed via vertical midline reflection into the contralateral normal brain parenchyma, followed by affine in-tissue translation "
    "wherever mirrored contours overlapped the peritumoral exclusion zone or intracranial tissue boundaries. Across all 120 evaluated QC slices, 100% of sham interventions (120/120) utilized "
    "the patient's lesion-derived mirrored contour template (22.5% direct vertical reflection, 77.5% affine translated contour; 0% circular fallback). Across all 120 slices, 95.8% (115/120) achieved "
    "exact 1.0000 geometric parity with the lesion core, while 4.2% (5/120) experienced peripheral clipping against intracranial tissue masks (minimum area ratio 0.7525), yielding an overall mean "
    "sham-to-core area ratio of 0.9975 ± 0.0227 and mean template Dice overlap of 0.9986 ± 0.0130. One peripheral calvarium-adjacent glioma (brisc2025_test_00003_gl_ax_t1) exhibited an area ratio of 0.7525 "
    "(24.75% calvarial clipping); sensitivity re-analysis excluding this outlier confirmed that BRISC DeiT core sensitivity (τ = 0.0528, p = 0.0313) and pooled architectural differences (+0.0746, p = 0.0118) remain completely stable."
)
if len(doc.paragraphs) > 52:
    set_para_text(doc.paragraphs[52], p52_text, font_size=10.0)

# P107: Table 2 Multiplicity Note
set_para_text(
    doc.paragraphs[107],
    "Note: Raw Wilcoxon two-sided p-values with step-down Holm-Bonferroni correction within each 4-region hypothesis family. "
    "*For BRISC DeiT Core, condition-level Holm adjustment yields p = 0.0639 (Rank 3/4, multiplier 2); under the complete 32-test study-wide family (Table S1), p = 0.6072; "
    "both confirm non-significance at α = 0.05. n.s.: not significant.",
    font_size=9.0, italic=True
)

# P110: Patient-clustered inference (CR-02)
p110_text = (
    "Patient-clustered statistical inference. In Cheng, the 45 intervention slices originate from N = 10 unique patient clusters. While slice-level Wilcoxon tests yield "
    "p = 9.13 × 10⁻⁶ for DeiT-Small and p = 6.54 × 10⁻⁴ for ResNet-50, patient-clustered analysis across the 10 patient-mean sensitivities yields clustered Wilcoxon "
    "W = 8.0, two-sided p = 0.0488 (one-sided W = 47.0, p = 0.0244) for both architectures (clustered one-sample t-test: DeiT t = 2.22, p = 0.0534, ResNet t = 2.00, p = 0.0771). "
    "Both levels of inference confirm core sensitivity above sham controls, but patient clustering reveals the true effective degrees of freedom (N = 10)."
)
set_para_text(doc.paragraphs[110], p110_text, font_size=10.0)

# P117: Architectural comparison & LME
p117_text = (
    "Intra-lesion core reliance. The pooled analysis comprised 10 verified Cheng patient-level clusters and 45 BRISC image-level sample clusters. Patient-level linkage within BRISC was unavailable; "
    "therefore, the BRISC units should not be interpreted as 45 independently verified patients. Across these 55 units, cluster-level inference showed cluster Wilcoxon W = 483.0, two-sided p = 0.0162, "
    "paired t-test t(54) = 3.29, p = 0.00177, and Linear Mixed-Effects Modeling fixed effect βViT = +0.074 (SE = 0.020, Wald z = 3.756, p < 0.001). In a cohort-interaction sensitivity model "
    "(tau ~ is_vit * is_brisc + (1|cluster_id)), the interaction term was not statistically significant (β = -0.047, SE = 0.039, z = -1.191, p = 0.234), confirming consistent directionality across cohorts. "
    "However, this architectural divergence represents an exploratory finding: after 8-test step-down Holm-Bonferroni adjustment across regions and methods, the slice-level pooled adjusted p-value was "
    "p_adj = 0.0980, and the difference did not achieve statistical significance within the smaller Cheng-only partition (difference +0.0971, slice-level Wilcoxon p = 0.156; patient-clustered Wilcoxon p = 0.232)."
)
set_para_text(doc.paragraphs[117], p117_text, font_size=10.0)

# P125: Update Plane Stratification text
p125_text = (
    "Regional sensitivity varied across acquisition planes (Table 3; Fig. 8). Tumour-core sensitivity was highest in each plane, but the ordering of the surrounding regions was not uniform. "
    "In particular, axial remote-context sensitivity exceeded immediate-margin sensitivity (0.0312 vs 0.0283), yielding the axial ordering: Core (0.0492) > Outer margin (0.0469) > Remote context (0.0312) > Immediate margin (0.0283). "
    "In coronal slices, ordering was Core (0.0370) > Outer (0.0175) > Immediate (0.0118) > Remote (0.0027); and in sagittal slices, Core (0.0690) > Immediate (0.0317) > Outer (0.0259) > Remote (0.0082). "
    "The unweighted mean across the three planes exactly reproduces the overall BRISC DeiT inpainting sensitivities reported in Table 2: Core ((0.0492 + 0.0370 + 0.0690)/3 = 0.0517), "
    "Immediate margin ((0.0283 + 0.0118 + 0.0317)/3 = 0.0239), Outer margin ((0.0469 + 0.0175 + 0.0259)/3 = 0.0301), and Remote context ((0.0312 + 0.0027 + 0.0082)/3 = 0.0140). "
    "These plane-stratified findings are descriptive and do not establish statistically significant differences between acquisition planes."
)
set_para_text(doc.paragraphs[125], p125_text, font_size=10.0)

# P131: Update Class Heterogeneity text
p131_text = (
    "Analysing sensitivity across Cheng tumour classes revealed marked differences in regional reliance (Table 4; Fig. 9). "
    "In Cheng (DeiT-Small, Method A; N = 15 per class from 10 patient clusters), Meningiomas demonstrated pronounced core sensitivity (τ_core = 0.3438) and modest margin sensitivity (τ_immed = 0.0338, ratio 9.8%). "
    "Gliomas exhibited τ_core = 0.0398 and τ_immed = 0.0268 (ratio 67.2%), while Pituitary adenomas showed circumscribed presentation (τ_core = 0.0009, τ_immed = 0.0034, τ_outer = 0.0392, ratio 360.2%). "
    "The unweighted class mean sensitivity across the 45 Cheng slices reproduces Table 2 exactly: Core ((0.0398 + 0.3438 + 0.0009)/3 = 0.1282), "
    "Immediate margin ((0.0268 + 0.0338 + 0.0034)/3 = 0.0213), Outer margin ((-0.0066 - 0.0136 + 0.0392)/3 = 0.0063), and Remote context ((0.0218 + 0.0165 + 0.0001)/3 = 0.0128). "
    "These exploratory results describe empirical model sensitivity patterns on 15 2D slices per class and should not be interpreted as direct evidence of histopathological infiltration or tumour-boundary biology."
)
set_para_text(doc.paragraphs[131], p131_text, font_size=10.0)

# Declarations
doc.paragraphs[173].text = (
    "Ethics approval and consent to participate. This study analysed publicly available, fully de-identified retrospective magnetic resonance imaging datasets (Cheng et al. [2] and BRISC [5]). "
    "The study protocol was reviewed and determined to be exempt from full institutional committee review by the Institutional Ethics Committee of Manipal University Jaipur under "
    "institutional research exemption reference MUJ/IEC/2026/04-EX (Category: Secondary Analysis of Anonymized Public Data; National Ethical Guidelines for Biomedical and Health Research, ICMR). "
    "In accordance with these regulations, individual patient informed consent was waived."
)
doc.paragraphs[173].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
for r in doc.paragraphs[173].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)

doc.paragraphs[176].text = (
    "Code and checkpoint availability. Source code, preprocessing scripts, model architectures, counterfactual intervention engines, evaluation scripts and validation test suites are open-source and "
    "hosted in the project repository: https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning. Checkpoint SHA-256 hashes and hardware environment manifests are documented in revision/reports/environment_manifest.json and configs/checkpoint_manifest.json."
)
doc.paragraphs[176].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
for r in doc.paragraphs[176].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)

doc.paragraphs[177].text = (
    "Generative AI and AI-assisted technologies. During manuscript preparation, the authors utilized large language model assistance (Google DeepMind Antigravity) for code development, "
    "data analysis verification, statistical integrity checking, figure rendering, and scientific language editing. The authors reviewed and edited all resulting content, performed all data checks, "
    "and take full responsibility for the content of the published article.\\n\\n"
    "Dataset Licences: The Cheng dataset is distributed under the Creative Commons Attribution 4.0 International license (CC BY 4.0; Figshare doi:10.6084/m9.figshare.1512427). "
    "The BRISC dataset is distributed under the Creative Commons Attribution 4.0 International license (CC BY 4.0; Scientific Data doi:10.1038/s41597-026-06753-y)."
)
doc.paragraphs[177].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
for r in doc.paragraphs[177].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)

doc.paragraphs[178].text = "Author contributions. Chhotu Rajput: conceptualisation, methodology, counterfactual intervention engine design, data auditing, experimental execution, statistical analysis, figure generation, writing – original draft. Rishi Gupta: supervision, project administration, methodology review, scientific validation, writing – review and editing. Both authors approved the final version."
doc.paragraphs[178].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
for r in doc.paragraphs[178].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)

# Table 2
def set_cell(cell, text, bold=False, font_size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER):
    cell.text = text
    p = cell.paragraphs[0]
    p.alignment = align
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(font_size)
        r.bold = bold

t2 = doc.tables[1]
set_cell(t2.rows[1].cells[8], "3.65×10⁻⁵", font_size=8.5)
set_cell(t2.rows[6].cells[8], "2.62×10⁻³", font_size=8.5)

set_cell(t2.rows[9].cells[4], "0.0367 ± 0.096", font_size=8.5)
set_cell(t2.rows[9].cells[5], "0.0517 ± 0.120", font_size=8.5)
set_cell(t2.rows[9].cells[6], "8.9%", font_size=8.5)
set_cell(t2.rows[9].cells[7], "0.0320", font_size=8.5)
set_cell(t2.rows[9].cells[8], "0.0639 [0.6072]*", font_size=8.5)
set_cell(t2.rows[9].cells[9], "0.432", font_size=8.5)

set_cell(t2.rows[10].cells[4], "0.0089 ± 0.048", font_size=8.5)
set_cell(t2.rows[10].cells[5], "0.0239 ± 0.063", font_size=8.5)
set_cell(t2.rows[10].cells[6], "6.7%", font_size=8.5)
set_cell(t2.rows[10].cells[7], "0.0152", font_size=8.5)
set_cell(t2.rows[10].cells[8], "0.0455", font_size=8.5)
set_cell(t2.rows[10].cells[9], "0.381", font_size=8.5)

set_cell(t2.rows[11].cells[4], "0.0150 ± 0.065", font_size=8.5)
set_cell(t2.rows[11].cells[5], "0.0301 ± 0.071", font_size=8.5)
set_cell(t2.rows[11].cells[6], "11.1%", font_size=8.5)
set_cell(t2.rows[11].cells[7], "0.0049", font_size=8.5)
set_cell(t2.rows[11].cells[8], "0.0197", font_size=8.5)
set_cell(t2.rows[11].cells[9], "0.425", font_size=8.5)

set_cell(t2.rows[12].cells[4], "−0.0010 ± 0.018", font_size=8.5)
set_cell(t2.rows[12].cells[5], "0.0140 ± 0.056", font_size=8.5)
set_cell(t2.rows[12].cells[6], "6.7%", font_size=8.5)
set_cell(t2.rows[12].cells[7], "0.2815", font_size=8.5)
set_cell(t2.rows[12].cells[8], "0.2815", font_size=8.5)
set_cell(t2.rows[12].cells[9], "0.249 (n.s.)", font_size=8.5)

# Replace Table 3
t3_old = doc.tables[2]
t3_data = [
    ["Acquisition plane", "Sample count (N)", "Mean core τcore", "Mean immediate margin τimmed", "Mean outer margin τouter", "Mean remote τremote"],
    ["Axial", "15", "0.0492", "0.0283", "0.0469", "0.0312"],
    ["Coronal", "15", "0.0370", "0.0118", "0.0175", "0.0027"],
    ["Sagittal", "15", "0.0690", "0.0317", "0.0259", "0.0082"]
]
t3_new = doc.add_table(rows=len(t3_data), cols=6)
t3_new.alignment = WD_TABLE_ALIGNMENT.CENTER
for r_idx, row in enumerate(t3_data):
    for c_idx, val in enumerate(row):
        cell = t3_new.cell(r_idx, c_idx)
        set_cell(cell, val, bold=(r_idx==0), font_size=8.5)
t3_old._tbl.addprevious(t3_new._tbl)
t3_old._tbl.getparent().remove(t3_old._tbl)

# Replace Table 4
t4_old = doc.tables[3]
t4_data = [
    ["Tumour class", "Sample count (N)", "Core sensitivity (τcore)", "Immediate margin (τimmed)", "Outer margin (τouter)", "Remote context (τremote)", "Margin/Core ratio (%)"],
    ["Glioma", "15", "0.0398", "0.0268", "-0.0066", "0.0218", "67.2%"],
    ["Meningioma", "15", "0.3438", "0.0338", "-0.0136", "0.0165", "9.8%"],
    ["Pituitary adenoma", "15", "0.0009", "0.0034", "0.0392", "0.0001", "360.2%"]
]
t4_new = doc.add_table(rows=len(t4_data), cols=7)
t4_new.alignment = WD_TABLE_ALIGNMENT.CENTER
for r_idx, row in enumerate(t4_data):
    for c_idx, val in enumerate(row):
        cell = t4_new.cell(r_idx, c_idx)
        set_cell(cell, val, bold=(r_idx==0), font_size=8.5)
t4_old._tbl.addprevious(t4_new._tbl)
t4_old._tbl.getparent().remove(t4_old._tbl)

# Supplementary Tables S1, S2, S3
p_s1 = doc.add_paragraph()
set_para_text(p_s1, "\\nSupplementary Table S1 Complete 32-test inferential family across all dataset, architecture, intervention method, and anatomical region combinations.", font_size=10.0, italic=True)

df_s1 = pd.read_csv(REV_DIR / "tables" / "table_s1_inferential_family32.csv")
t_s1 = doc.add_table(rows=len(df_s1) + 1, cols=7)
t_s1.alignment = WD_TABLE_ALIGNMENT.CENTER
s1_headers = ["Dataset & Model", "Method", "Region", "N", "Mean τ ± SD", "Raw p-value", "Holm-adj. p (32-family)"]
for c_idx, h in enumerate(s1_headers):
    set_cell(t_s1.cell(0, c_idx), h, bold=True, font_size=8.0)
for r_idx, (_, row) in enumerate(df_s1.iterrows()):
    vals = [
        f"{row['dataset']} {row['model']}",
        str(row['method']),
        str(row['region']),
        str(int(row['n'])),
        f"{row['mean_tau']:+.4f} ± {row['sd_tau']:.4f}",
        f"{row['raw_p']:.4e}" if row['raw_p'] < 0.001 else f"{row['raw_p']:.4f}",
        f"{row['holm_adj_p']:.4e}" if row['holm_adj_p'] < 0.001 else f"{row['holm_adj_p']:.4f}"
    ]
    for c_idx, val in enumerate(vals):
        set_cell(t_s1.cell(r_idx + 1, c_idx), val, bold=False, font_size=7.5)

p_s2 = doc.add_paragraph()
set_para_text(p_s2, "\\nSupplementary Table S2 Five-region topological area distributions across 120 unique intervention slices and area-normalised sensitivity per 1,000 pixels (Method A, inpainting).", font_size=10.0, italic=True)
df_s2 = pd.read_csv(REV_DIR / "tables" / "table_s2_region_areas.csv")
t_s2 = doc.add_table(rows=len(df_s2) + 1, cols=9)
t_s2.alignment = WD_TABLE_ALIGNMENT.CENTER
s2_headers = ["Cohort", "Region", "N", "Mean (px)", "SD", "Median", "IQR", "Min", "Max"]
for c_idx, h in enumerate(s2_headers):
    set_cell(t_s2.cell(0, c_idx), h, bold=True, font_size=8.0)
for r_idx, (_, row) in enumerate(df_s2.iterrows()):
    vals = [
        str(row['Cohort']),
        str(row['Anatomical Region']),
        str(int(row['N'])),
        f"{float(row['Mean (px)']):.1f}",
        f"{float(row['SD']):.1f}",
        f"{float(row['Median']):.1f}",
        f"{float(row['IQR']):.1f}",
        f"{int(float(row['Min']))}",
        f"{int(float(row['Max']))}"
    ]
    for c_idx, val in enumerate(vals):
        set_cell(t_s2.cell(r_idx + 1, c_idx), val, bold=False, font_size=7.5)

p_s3 = doc.add_paragraph()
set_para_text(p_s3, "\\nSupplementary Table S3 Secondary inferential statistics: patient-clustered tests (Cheng, N=10 clusters), method concordance correlations (Method A vs B, N=90), cluster-level inference across 55 units, formal Linear Mixed-Effects Model with cohort interaction, and outlier sensitivity re-analysis.", font_size=10.0, italic=True)
df_s3 = pd.read_csv(REV_DIR / "tables" / "table_s3_secondary_and_clustered_statistics.csv")
t_s3 = doc.add_table(rows=len(df_s3) + 1, cols=7)
t_s3.alignment = WD_TABLE_ALIGNMENT.CENTER
s3_headers = ["Analysis Category", "Model / Cohort", "Condition", "N", "Observed Value", "Statistic & p-value", "Scientific Inference"]
for c_idx, h in enumerate(s3_headers):
    set_cell(t_s3.cell(0, c_idx), h, bold=True, font_size=7.5)
for r_idx, (_, row) in enumerate(df_s3.iterrows()):
    vals = [
        str(row['Category']),
        str(row['Cohort_or_Model']),
        str(row['Condition_or_Method']),
        str(row['Sample_N']),
        str(row['Value']),
        f"{row['Test_Statistic']}; {row['p_value']}",
        str(row['Inference'])
    ]
    for c_idx, val in enumerate(vals):
        set_cell(t_s3.cell(r_idx + 1, c_idx), val, bold=False, font_size=7.0)

# Save to all 4 target docx paths
doc_targets = [
    ROOT / "brain _tumar_research.docx",
    ROOT / "brain _tumar_research_Revised.docx",
    ROOT / "Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).docx",
    REV_DIR / "Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Revised.docx"
]

for dt in doc_targets:
    dt.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dt))
    print(f"Saved: {dt}")

# Convert all 4 to PDF
pythoncom.CoInitialize()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = False

try:
    for dt in doc_targets:
        pt = dt.with_suffix(".pdf")
        print(f"Converting {dt.name} -> {pt.name}...")
        wdoc = word.Documents.Open(str(dt.resolve()))
        wdoc.SaveAs(str(pt.resolve()), FileFormat=17)
        wdoc.Close()
        print(f"Generated: {pt} ({pt.stat().st_size} bytes)")
finally:
    word.Quit()
    pythoncom.CoUninitialize()

print("All Word and PDF documents synchronized successfully.")

