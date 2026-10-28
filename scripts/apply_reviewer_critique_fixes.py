import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import shutil
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jkgga\Downloads\ChengResearch")
DOCX_PATH = BASE_DIR / "Brain_MRI_Paper_Final_Corrected_v4.docx"
BACKUP_PATH = BASE_DIR / "Brain_MRI_Paper_Final_Corrected_v4_pre_critique.docx"

if not BACKUP_PATH.exists():
    shutil.copyfile(DOCX_PATH, BACKUP_PATH)
    print(f"Created backup at {BACKUP_PATH}")

doc = docx.Document(DOCX_PATH)

# Helper function for cell styling
def style_cell(cell, bg_color=None, bold=False, font_size=8.5, color=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    if bg_color:
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    for p in cell.paragraphs:
        p.alignment = align
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.05
        for r in p.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(font_size)
            r.font.bold = bold
            if color:
                r.font.color.rgb = color

print("Updating Table 2 to include Patient distribution per class...")
t2 = doc.tables[1]  # Table 2
# Current table has 5 rows, 4 columns. We want to update it to include patients.
# Let's inspect Table 2 row 0
print("Current T2 cols:", len(t2.columns), "rows:", len(t2.rows))

# Replace paragraphs in document
p_count = len(doc.paragraphs)
print(f"Total paragraphs in document: {p_count}")

# 1. Update Abstract (P6)
abstract_p = doc.paragraphs[6]
abstract_new = (
    "Tile scrambling is widely used as an interpretability probe for spatial-context reliance, "
    "but it inherently introduces artificial boundary seams that can confound performance evaluation. "
    "We examine this on the Cheng Figshare cohort (233 patients across three classes; 3,064 slices) "
    "using 15 frozen ResNet-50 checkpoints across three evaluation scenarios and six input conditions: "
    "baseline (C0), tile-mean-offset (C1), seam-attenuated permutation (C2), raw scramble (C3) and two "
    "seam-only controls (C4a, C4b) that perturb only two pixels flanking each seam. Tumour core and a "
    "15-pixel margin were strictly preserved. Over 55,152 forward predictions evaluated on 233 independent "
    "patient clusters with paired cluster-bootstrap inference (B = 25,000) and Holm–Bonferroni control, "
    "patient-disjoint Macro-F1 fell from 0.9333 (C0) to 0.8127 (C4a) and 0.7811 (C4b), 0.6290 (C1), 0.5118 (C3) "
    "and 0.4525 (C2) in S0. Seam steps alone reliably degrade performance, but the decline varies across checkpoints "
    "and is much smaller than under scrambling; partial seam attenuation (39.0% excess boundary reduction at input) "
    "does not restore accuracy. Misclassifications show an asymmetric collapse: glioma slices were disproportionately "
    "labelled pituitary tumour under perturbation (0.1% baseline; 6.5–23.4% under seam steps; 55–64% under scrambling "
    "or suppression across scenarios), consistent with loss of orientation and cranial-contour priors. These results "
    "demonstrate the co-presence of both boundary-artifact sensitivity and distant-content sensitivity, but caution "
    "that complete linear apportionment requires full 2×2 factorial designs with energy-matched controls, as tumour "
    "class is partially confounded with imaging plane."
)
abstract_p.text = abstract_new
print("Updated Abstract (P6).")

# 2. Update Section 3.1 Dataset (P62)
p62 = doc.paragraphs[62]
p62_new = (
    "Experiments use the public Cheng brain-tumour dataset (Figshare article 1512427, DOI 10.6084/m9.figshare.1512427) [3, 4]: "
    "3,064 two-dimensional T1-weighted contrast-enhanced slices acquired between 2005 and 2010 at Nanfang Hospital (Guangzhou) "
    "and General Hospital, Tianjin Medical University. Original raw MATLAB v7.3 .mat files containing 16-bit signed integer pixel "
    "matrices (cjdata.image) were converted to 8-bit unsigned integer arrays via deterministic per-slice min-max normalization: "
    "I_8 = uint8(255 * (I - I_min) / (I_max - I_min)). Paired binary tumour masks (cjdata.tumorMask) were verified for strict binary "
    "integrity ({0, 1}), and tumour border coordinates and patient identifiers (PID) were extracted. The 233 unique patient identifiers "
    "comprise 89 glioma (38.2%), 82 meningioma (35.2%), and 62 pituitary tumour (26.6%) patients (Table 2). The target is a "
    "three-class slice label, not a patient-level clinical diagnosis."
)
p62.text = p62_new
print("Updated Section 3.1 Dataset (P62).")

# 3. Update Section 3.1 Plane Confound (P64)
p64 = doc.paragraphs[64]
p64_new = (
    "The example slices in Fig. 2 have visual appearances consistent with different viewing orientations. Clinical MRI protocols "
    "routinely acquire pituitary tumours in coronal and sagittal planes to evaluate the sella turcica, pituitary stalk, and optic "
    "chiasm, whereas supratentorial gliomas are predominantly imaged in axial planes. Because the source Cheng MAT files lack embedded "
    "acquisition-plane headers or orientation matrices, tumour class and imaging plane are partially confounded. Distant background "
    "permutations obliterate cranial-vault silhouettes, orbital landmarks, and skull-base contours that provide strong orientation cues. "
    "Imaging plane was not recorded as an explicit stratification variable in the original repository, representing a first-order "
    "anatomical confound that directly informs the directional error collapse documented below. The repository also lacks full acquisition "
    "parameters (field strength, TR, TE, slice thickness), precluding scanner-level stratification."
)
p64.text = p64_new
print("Updated Section 3.1 Plane Confound (P64).")

# 4. Update Section 3.2 Evaluation scenarios & SSIM (P68)
p68 = doc.paragraphs[68]
p68_new = (
    "Three five-fold scenarios were evaluated to examine sensitivity to leakage control and patient grouping. Candidate near-duplicate "
    "grouping was performed on full-resolution 512×512 images using structural similarity (SSIM, window size 11×11, Gaussian weighting "
    "sigma = 1.5). S0 groups slices strictly by patient identifier (233 clusters), so no patient appears in both training and held-out folds. "
    "S1 additionally merges patient clusters that contain slice pairs with structural similarity SSIM >= 0.80 [21], resulting in 231 clusters "
    "(a merge of only two patient clusters relative to S0). S2 applies a broader threshold SSIM >= 0.75, yielding 217 clusters. "
    "Merging is performed over connected components of the similarity graph. Because S1 merges only two clusters, differences in fold sizes "
    "and performance drops between S0 and S1 reflect fold-level checkpoint training variance rather than grouping stringency (Table 3)."
)
p68.text = p68_new
print("Updated Section 3.2 Scenarios (P68).")

# 5. Update Hypotheses & Clinical Non-inferiority Margin (P38)
p38 = doc.paragraphs[38]
p38_new = (
    "The hypotheses were formulated in the phased research protocol before model execution: H0, the C1 perturbation accounts for the "
    "entire scrambling decline (i.e. C3 is not worse than C1); H1, the C1 perturbation alone degrades performance; H2, the seam-suppressed "
    "rearrangement degrades performance by more than a pre-specified clinical margin of 0.150 Macro-F1 (approximately 2.5 times the fold-level "
    "standard error, SE ≈ 0.015); H3, a mixed outcome where H1 and H2 are both supported. Importantly, H0 and H1 were originally framed "
    "around C1 as a proxy for boundary artifacts; subsequent diagnostic measurements revealed that C1 carries coarse tile-mean rearrangement, "
    "making the post hoc C4a and C4b interventions essential to isolate clean boundary steps. Section 4.9 provides verdicts for each."
)
p38.text = p38_new
print("Updated Hypotheses (P38).")

# 6. Update Section 4.5 Class-level error structure (P146)
p146 = doc.paragraphs[146]
p146_new = (
    "The aggregate performance drop conceals a pronounced directional error structure (Table 8, Fig. 7, Fig. 8). In S0, the proportion "
    "of the 1,426 glioma slices misclassified as pituitary tumour rises from 0.14% (C0) to 16.48% (C4a) and 23.35% (C4b), escalating to "
    "31.28% (C1), 56.45% (C3), and 63.53% (C2). Across all three evaluation scenarios, seam-only misclassification spans 6.52%–23.35% "
    "(6.52% in S1, 6.94% in S2 for C4a; 8.49% in S1, 9.89% in S2 for C4b), while scrambling and suppression induce 55.12%–63.53% misclassification "
    "(57.01% in S1, 55.12% in S2 for C2; 60.66% in S1, 57.29% in S2 for C3). Glioma recall drops from 0.950 at baseline to 0.806 (C4a), "
    "0.747 (C4b), 0.425 (C1), 0.183 (C3), and 0.086 (C2) in S0. Conversely, pituitary slices labelled glioma remain near zero across all conditions "
    "(0.0% under C2 and 0.9% under C3), demonstrating that distant scrambling systematically pushes predictions toward the pituitary prior."
)
p146.text = p146_new
print("Updated Section 4.5 Class transitions (P146).")

# 7. Update Section 5.1 Principal findings (P178)
p178 = doc.paragraphs[178]
p178_new = (
    "The study asked whether a performance drop under distant-context scrambling can be attributed to synthetic seams introduced by "
    "the intervention, to rearrangement of distant context, or to both. Four observations bear on this. (i) A seam-only perturbation "
    "modifying only the two pixels flanking each seam reliably lowers Macro-F1 across all scenarios (by 0.05–0.12 at gain 1.0 and 0.07–0.15 "
    "at gain 1.8), establishing that boundary discontinuities alone suffice to degrade frozen checkpoints. (ii) The magnitude of this drop "
    "varies substantially between checkpoints and folds (ranging from +0.006 to +0.247 across single-seed folds in S0), indicating that the "
    "apparent decline between S0 and S1 reflects training and fold-level variance rather than near-duplicate grouping stringency (as S1 merges "
    "only two patient clusters). (iii) The tile-mean-offset control (C1), raw scramble (C3) and seam-attenuated permutation (C2) produce drops "
    "of 0.29–0.48 Macro-F1, substantially exceeding the seam-only drop, and C3 is reliably worse than C1. (iv) Seam attenuation (39.0% excess "
    "boundary reduction at model input) did not recover performance. Together, these observations demonstrate the co-presence of both "
    "boundary-artifact sensitivity and distant-content sensitivity, while demonstrating that complete mathematical apportionment requires a "
    "full 2×2 factorial design with energy-matched controls."
)
p178.text = p178_new
print("Updated Section 5.1 Principal findings (P178).")

# 8. Update Section 5.4 Alternative explanations & Confounds (P186, P187)
p186 = doc.paragraphs[186]
p186_new = (
    "Acquisition plane as a first-order confound. The Cheng Figshare cohort pools axial, coronal, and sagittal scans without embedded plane "
    "metadata. Slices with pituitary tumours are predominantly acquired in coronal and sagittal orientations to capture sellar anatomy, whereas "
    "gliomas are primarily imaged axially. Scrambling the distant anatomy destroys skull-vault geometry, orbital landmarks, and cranial "
    "orientation cues that implicitly encode scan orientation. The directional collapse of glioma slices into pituitary tumour under scrambling "
    "and seam attenuation (rising from 0.1% to 55–64% across scenarios) is exactly what the loss of plane-specific anatomical priors predicts. "
    "Establishing true lesion-context reliance versus orientation-cue destruction requires plane-stratified controls or tumour-only baselines."
)
p186.text = p186_new

p187 = doc.paragraphs[187]
p187_new = (
    "Scale of interventions and OOD representation fragility. C1, C2, and C3 alter 88.7%–90.7% of image pixels (leaving 9.3%–11.3% intact). "
    "Because the ResNet-50 checkpoints were trained on unperturbed images using standard spatial flips and rotations, rewriting ~90% of pixels "
    "presents an extreme out-of-distribution (OOD) shift. The resulting accuracy decline may reflect representation fragility to unnatural image "
    "statistics rather than loss of clinically meaningful anatomical context. Furthermore, C4 perturbs a 2-pixel band flanking tile boundaries "
    "while leaving tile interiors unchanged, producing a thin line grid whose source high-frequency Fourier energy (3578 and 5791) exceeds "
    "that of C3 (2598). Bilinear resizing to 224×224 partially attenuates this thin boundary feature (reducing input HF energy to 2167 and 3073). "
    "Finally, perturbation dose varies systematically with tumour size: compact pituitary tumours leave ~91% of the background perturbed, "
    "whereas large gliomas protect larger contiguous margins (~88% perturbed), contributing to class-asymmetric sensitivity."
)
p187.text = p187_new
print("Updated Section 5.4 Alternative explanations (P186, P187).")

# 9. Update Section 5.5 Implications (P192)
p192 = doc.paragraphs[192]
p192_new = (
    "For researchers designing spatial perturbation experiments as interpretability probes, these findings highlight three methodological "
    "recommendations. First, boundary-localized artifact controls should be routinely tested alongside scramble interventions to establish "
    "whether performance declines arise from artificial seam discontinuities. Second, dual-resolution diagnostics (quantifying boundary gradients "
    "and spectral energy at both source and network-input resolutions) should accompany accuracy metrics. Third, performance drops should not be "
    "conflated with anatomical context reliance without testing for out-of-distribution fragility, positive controls (e.g. models fine-tuned on "
    "scrambled inputs), and potential acquisition-plane confounds."
)
p192.text = p192_new
print("Updated Section 5.5 Implications (P192).")

# 10. Update Table 2 to reflect patient counts
print("Updating Table 2 cell contents...")
# R0: Header: ['Class', 'Patients', 'Patient Share (%)', 'Slices', 'Slice Share (%)', 'Typical anatomical location']
# Wait, let's see current row cells of Table 2:
for r_idx, r in enumerate(t2.rows):
    cells = r.cells
    if r_idx == 0:
        cells[0].text = "Class"
        cells[1].text = "Patients (%)"
        cells[2].text = "Slices (%)"
        cells[3].text = "Typical Anatomical Location & Acquisition Views"
    elif r_idx == 1: # Meningioma
        cells[0].text = "Meningioma"
        cells[1].text = "82 (35.19%)"
        cells[2].text = "708 (23.11%)"
        cells[3].text = "Dural-based, extra-axial (parasagittal, convexity); primarily axial & coronal views"
    elif r_idx == 2: # Glioma
        cells[0].text = "Glioma"
        cells[1].text = "89 (38.20%)"
        cells[2].text = "1,426 (46.54%)"
        cells[3].text = "Intra-axial cerebral/cerebellar parenchyma; predominantly axial views"
    elif r_idx == 3: # Pituitary
        cells[0].text = "Pituitary tumour"
        cells[1].text = "62 (26.61%)"
        cells[2].text = "930 (30.35%)"
        cells[3].text = "Sella turcica & skull base; predominantly coronal & sagittal views"
    elif r_idx == 4: # Total
        cells[0].text = "Total"
        cells[1].text = "233 (100.0%)"
        cells[2].text = "3,064 (100.0%)"
        cells[3].text = "233 unique patient clusters (mean 13.2 slices/patient)"

for r in t2.rows:
    for c in r.cells:
        for p in c.paragraphs:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(8.5)

# Save document
UPDATED_PATH = BASE_DIR / "Brain_MRI_Paper_Final_Corrected_v4_updated.docx"
V5_PATH = BASE_DIR / "Brain_MRI_Paper_Final_Corrected_v5.docx"
doc.save(str(UPDATED_PATH))
print(f"Successfully saved updated {UPDATED_PATH}!")

shutil.copyfile(UPDATED_PATH, V5_PATH)
print(f"Saved copy as {V5_PATH}!")

pub_docx = BASE_DIR / "publication" / "manuscript_v1" / "manuscript.docx"
shutil.copyfile(UPDATED_PATH, pub_docx)
print(f"Synced to {pub_docx}!")

try:
    shutil.copyfile(UPDATED_PATH, DOCX_PATH)
    print(f"Successfully updated {DOCX_PATH}!")
except PermissionError:
    print(f"Note: {DOCX_PATH} is currently open in Microsoft Word. Updated version is saved as {UPDATED_PATH} and {V5_PATH}.")
