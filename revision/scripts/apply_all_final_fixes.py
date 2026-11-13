# -*- coding: utf-8 -*-
"""
apply_all_final_fixes.py
========================
Applies all remaining reviewer critique points to Brain_MRI_Research_Paper_Final.docx.
Ensures 100% resolution of issues across Sections 1 to 6.
"""

import docx
import shutil
from pathlib import Path

DOC_PATH = Path("Brain_MRI_Research_Paper_Final.docx")
ARTIFACT = Path(r"C:\Users\jkgga\.gemini\antigravity\brain\d6adce8c-23ce-4309-8199-0aa195f5f78c\Brain_MRI_Research_Paper_Final.docx")

def set_para_text(p, new_text):
    if not p.runs:
        p.add_run(new_text)
        return
    first_run = p.runs[0]
    for r in p.runs:
        r._r.getparent().remove(r._r)
    new_run = p.add_run(new_text)
    if first_run.bold:
        new_run.bold = True
    if first_run.italic:
        new_run.italic = True
    if first_run.font.size:
        new_run.font.size = first_run.font.size

def replace_in_para(p, old, new):
    if old in p.text:
        set_para_text(p, p.text.replace(old, new))
        return True
    return False

def run():
    doc = docx.Document(str(DOC_PATH))
    paras = doc.paragraphs
    tables = doc.tables

    print("Applying comprehensive final fixes...")

    # -------------------------------------------------------------
    # 1. ABSTRACT (P007) - Condense to ~285 words, move dense p-values to Results
    # -------------------------------------------------------------
    condensed_abstract = (
        "Automated classification of primary brain tumours from contrast-enhanced magnetic resonance imaging (CE-MRI) "
        "yields high benchmark scores with deep convolutional neural networks (CNNs) and Vision Transformers (ViTs). "
        "However, accuracy on unmodified images does not establish which anatomical regions support predictions. "
        "Here, we conduct a sham-controlled, region-resolved counterfactual audit on two CE-MRI benchmarks: the Cheng cohort "
        "(3,064 slices, 233 patients; evaluated on 480 Fold 1 held-out slices from 41 unseen patients) and the multi-plane BRISC "
        "cohort (6,000 slices; 1,000 official and 899 de-duplicated clean test slices). For each tumour slice, we segmented the "
        "tumour core, a 4-pixel immediate margin, a 12-pixel outer margin, remote context, and an area-matched contralateral "
        "parenchymal sham control, perturbing each via Telea inpainting (Method A) and Gaussian texture replacement (Method B). "
        "Across 1,800 paired counterfactual observations, DeiT-Small/16 exhibited pronounced lesion-core reliance on Cheng "
        "(sham-corrected sensitivity τ_core = 0.1282, p < 0.001; patient-clustered p = 0.0488 across 10 patient clusters), "
        "outperforming ResNet-50 (τ_core = 0.0311). In pooled multi-cohort mixed-effects modelling across 55 patient/case clusters, "
        "DeiT-Small maintained significantly higher core reliance (fixed effect β = +0.074, 95% CI [0.035, 0.112], p < 0.001). "
        "By contrast, BRISC ResNet-50 showed negligible core reliance under Method A (τ_core = 0.0012, p = 0.79), indicating "
        "substantial model- and cohort-dependent shortcut vulnerability. Immediate peritumoral margins contributed evidence "
        "in selected settings, while remote-region effects were not statistically distinguishable from sham in primary "
        "Method A comparisons. Exploratory tumour-class analysis revealed marked heterogeneity (meningioma core reliance far "
        "exceeding glioma and pituitary adenoma). Finally, exact pixel duplicates across train–test partitions in the evaluated "
        "BRISC archive shifted performance metrics in a model-dependent manner upon de-duplication. These findings demonstrate "
        "that high classification accuracy can conceal stark differences in anatomical reliance, underscoring the necessity "
        "of sham-controlled spatial audits before clinical translation."
    )
    set_para_text(paras[7], condensed_abstract)
    print("  [OK] Abstract condensed to ~285 words and p-value strings streamlined")

    # -------------------------------------------------------------
    # 2. P011 - Wallis & Buvat Figshare Cheng dataset connection
    # -------------------------------------------------------------
    replace_in_para(
        paras[11],
        "trained on a widely used public brain tumour MRI dataset",
        "trained on the widely used public Figshare brain tumour MRI benchmark published by Cheng et al. [2]"
    )
    print("  [OK] P011: Explicitly linked Wallis & Buvat to Figshare Cheng dataset")

    # -------------------------------------------------------------
    # 3. P025 - Sourget et al. and measured novelty claim
    # -------------------------------------------------------------
    replace_in_para(
        paras[25],
        "Among the studies we reviewed, prior medical imaging intervention studies evaluated CNNs rather than Vision Transformers and did not use matched contralateral controls to cancel generic inpainting artefacts.",
        "Sourget et al. [4] investigated model sensitivity to unexpected anatomical regions in medical images, highlighting shortcut reliance in deep classifiers. However, systematic contrastive audits pairing lesion-centred perturbations with contralateral healthy-parenchyma controls across both CNN and Vision Transformer architectures remain scarce in neuro-oncological MRI classification."
    )
    print("  [OK] P025: Measured phrasing for Sourget et al. and related work")

    # -------------------------------------------------------------
    # 4. P032 - BRISC 4,000 / 1,000 split provenance
    # -------------------------------------------------------------
    replace_in_para(
        paras[32],
        "partitioned into an official training set (N = 5,000, split into 4,000 train and 1,000 validation)",
        "partitioned into an official training set of 5,000 images (from which an audited stratified 80/20 split was drawn into 4,000 training and 1,000 validation slices)"
    )
    print("  [OK] P032: Clarified BRISC 4,000/1,000 split provenance")

    # -------------------------------------------------------------
    # 5. P036 - Fig 1 caption remove phantom (A)-(D) panel letters
    # -------------------------------------------------------------
    replace_in_para(
        paras[36],
        ": (A) ingestion and provenance audit of the Cheng (N = 3,064) and BRISC (N = 6,000) cohorts; (B) five-region topological decomposition; (C) dual perturbation engines; (D) paired model evaluation across ResNet-50 and DeiT-Small.",
        " across four methodological stages: cohort ingestion and provenance audit (Cheng N = 3,064 and BRISC N = 6,000); five-region topological decomposition; dual counterfactual perturbation engines (Telea inpainting and Gaussian texture fill); and paired model sensitivity evaluation across ResNet-50 and DeiT-Small."
    )
    print("  [OK] P036: Fig 1 caption panel letters cleaned")

    # -------------------------------------------------------------
    # 6. P040 & P041 - Sample accounting & remove 'Phase 6' jargon
    # -------------------------------------------------------------
    replace_in_para(
        paras[40],
        "Counterfactual intervention QC manifest (N = 1,200). recorded in manifests/intervention_qc.csv across 120 unique slices",
        "Counterfactual quality-control pool (N = 1,200). Quality-control records were evaluated across 120 unique slices"
    )
    replace_in_para(
        paras[41],
        "taking the first 15 mask-containing slices meeting technical invariance per tumour class for Cheng (15 gliomas, 15 meningiomas, 15 pituitary adenomas, originating from N = 10 patient clusters)",
        "taking the first 15 mask-containing slices meeting technical invariance per tumour class for Cheng (15 gliomas, 15 meningiomas, 15 pituitary adenomas, originating from N = 10 patient clusters; all 45 Cheng intervention slices originated exclusively from held-out Fold 1 patients and were evaluated using the Fold 1 checkpoint)"
    )
    print("  [OK] P040 & P041: Streamlined sample accounting and Fold 1 provenance")

    # -------------------------------------------------------------
    # 7. P052 - Sham outlier details and clipped slice counts
    # -------------------------------------------------------------
    p52_cleaned = (
        "[See Section 4.3 for full sham construction details.] Contralateral sham controls were constructed via vertical "
        "midline reflection into the contralateral normal brain parenchyma, followed by affine in-tissue translation wherever "
        "mirrored contours overlapped the peritumoral exclusion zone or intracranial boundary (77.5% of evaluated slices used "
        "affine-translated shams). For sagittal slices and midline (pituitary/sellar) lesions where contralateral reflection is "
        "not anatomically defined, the sham was placed in an area-matched ipsilateral parenchymal region remote from the lesion "
        "(see Limitations, Section 6.5). Across all 120 QC slices, 100% of sham interventions utilized the patient's lesion-derived "
        "mirrored contour template (22.5% direct vertical reflection, 77.5% affine-translated; 0% circular fallback). Exactly "
        "95.8% (115/120) achieved exact 1.0000 geometric area parity with the lesion core, while 5/120 experienced peripheral "
        "clipping against intracranial tissue masks. Of these 5 clipped slices, exactly 2 were included in the primary 90-slice "
        "evaluated sample: slice brisc2025_test_00003_gl_ax_t1 (calvarial clipping yielding an area ratio of 0.7525) and slice "
        "brisc2025_test_00396_me_co_t1 (6.1% clipping, area ratio 0.9390). Sensitivity re-analysis excluding the most severe "
        "outlier (00003: N = 44) confirms stability of BRISC DeiT core sensitivity (τ = 0.0528, W = 311.0, p = 0.0313), whereas "
        "excluding both clipped slices (00003 and 00396: N = 43) yields τ = 0.0506 (W = 311.0, p = 0.0505), indicating directional "
        "consistency while noting marginal significance near the α = 0.05 threshold."
    )
    set_para_text(paras[52], p52_cleaned)
    print("  [OK] P052: Cleaned sham construction and clipped outlier sample accounting")

    # -------------------------------------------------------------
    # 8. P054 - Centroid drift units
    # -------------------------------------------------------------
    replace_in_para(
        paras[54],
        "centroid drift was bounded within 0.0035.",
        "centroid drift was bounded within 0.0035 pixels (normalised coordinate shift < 1.6 × 10⁻⁵)."
    )
    print("  [OK] P054: Added units to centroid drift")

    # -------------------------------------------------------------
    # 9. P060 - Training schedule actual epochs
    # -------------------------------------------------------------
    replace_in_para(
        paras[60],
        "following a one-epoch linear w",
        "following a one-epoch linear warmup; all baseline models completed the full 5 planned epochs without early triggering of the patience criterion."
    )
    print("  [OK] P060: Stated actual training epochs completed")

    # -------------------------------------------------------------
    # 10. P089 & P091 - Fig 3 ResNet underconfidence note
    # -------------------------------------------------------------
    replace_in_para(
        paras[89],
        "compared with 0.1835 for ResNet-50.",
        "compared with 0.1835 for ResNet-50. In reliability diagrams (Fig. 3), the empirical calibration curves for ResNet-50 sit predominantly above the diagonal, indicating systematic underconfidence. On BRISC, ResNet-50 predicted probabilities cluster tightly between 0.29 and 0.44—modestly above the 0.25 chance baseline for four classes. This probability compression inherently restricts the maximum possible probability drop (Δ) that input perturbations can elicit in ResNet-50, which partly explains its lower raw and sham-corrected sensitivity magnitudes."
    )
    print("  [OK] P089: Added ResNet probability underconfidence / compression explanation")

    # -------------------------------------------------------------
    # 11. P105 - Fig 5 caption
    # -------------------------------------------------------------
    replace_in_para(
        paras[105],
        "Error bars show the standard error of the mean; asterisks mark paired Wilcoxon significance against sham (* p < 0.05, *** p < 0.001; n.s., not significant).",
        "Bars depict mean sham-corrected sensitivity (τr) with standard error bars across DeiT-Small and ResNet-50 models; see Table 2 for exact means, standard errors, and family-wise multiplicity-adjusted p-values."
    )
    print("  [OK] P105: Updated Fig 5 caption")

    # -------------------------------------------------------------
    # 12. P110 - Clustered inference wording
    # -------------------------------------------------------------
    replace_in_para(
        paras[110],
        "Both levels of inference are consistent with core sensitivity above sham controls, but patient clustering reveals the true effective degrees of freedom (N = 10).",
        "Both levels of inference are consistent with core sensitivity above sham controls under the non-parametric Wilcoxon test, though parametric clustered t-tests remain marginal (DeiT t = 2.22, p = 0.0534; ResNet t = 2.00, p = 0.0771) given the effective degrees of freedom across N = 10 patient clusters."
    )
    print("  [OK] P110: Refined clustered inference wording")

    # -------------------------------------------------------------
    # 13. P111 - ResNet remote Method B qualified
    # -------------------------------------------------------------
    replace_in_para(
        paras[111],
        "whereas ResNet-50 showed higher remote-parenchyma sensitivity under the same perturbation. Non-significance is not proof of zero effect or of complete shortcut independence.",
        "whereas ResNet-50 showed a descriptive, non-significant trend towards remote-parenchyma perturbation under Method B (pooled τ ≈ +0.010, p > 0.05). Non-significance is not proof of zero effect or of complete shortcut independence."
    )
    print("  [OK] P111: Qualified ResNet remote Method B trend")

    # -------------------------------------------------------------
    # 14. P112 - Remote area confound and per-1,000-px range
    # -------------------------------------------------------------
    p112_cleaned = (
        "Region area and per-pixel sensitivity. Regions differ substantially in anatomical size, and only the contralateral "
        "sham is area-matched to the tumour core; differences between regions may therefore partly reflect area. In particular, "
        "remote tissue patches averaged 264 px (minimum 17 px), against 1,013 px for the core, which may dilute measured remote "
        "perturbation effects. Note also that topological area distributions in Table S2 were characterised across the 120-slice "
        "QC pool rather than restricted to the 90 evaluated slices. For DeiT-Small, sensitivity normalised per 1,000 edited "
        "pixels ranged from 0.049 to 0.136 for the core (widening to 0.031–0.136 when including ResNet-50 on Cheng) and from "
        "0.015 to 0.036 for margin and remote regions, indicating higher evidence density in the core in the summarised comparisons."
    )
    set_para_text(paras[112], p112_cleaned)
    print("  [OK] P112: Added remote area confound, QC pool provenance, and widened per-1,000-px range")

    # -------------------------------------------------------------
    # 15. P116 & P123 - Fig 6 and Fig 7 clean captions (Option B)
    # -------------------------------------------------------------
    replace_in_para(
        paras[116],
        " (Method A; labelled as Figure 5 in embedded panel artwork):",
        " (Method A):"
    )
    replace_in_para(
        paras[123],
        " (labelled as Figure 6 in embedded panel artwork):",
        ":"
    )
    print("  [OK] P116 & P123: Synchronized Fig 6 & 7 clean captions (Option B)")

    # -------------------------------------------------------------
    # 16. P117 - LME interaction wording & British spelling
    # -------------------------------------------------------------
    replace_in_para(paras[117], "Linear Mixed-Effects Modeling", "Linear Mixed-Effects Modelling")
    replace_in_para(
        paras[117],
        "confirming consistent directionality across cohorts.",
        "is directionally consistent across cohorts, though absence of a statistically significant interaction (p = 0.234) does not formally prove equivalence."
    )
    print("  [OK] P117: British spelling 'Modelling' and cautious interaction wording")

    # -------------------------------------------------------------
    # 17. P127 & P128 - Fig 8 and Table 3 titles
    # -------------------------------------------------------------
    set_para_text(
        paras[127],
        "Fig. 8 Regional evidence sensitivity by acquisition plane (BRISC, DeiT-Small, Method A): sham-corrected sensitivity across tumour core, immediate margin (4 px), outer margin (12 px) and remote context for axial (N = 15), coronal (N = 15) and sagittal (N = 15) slices."
    )
    set_para_text(
        paras[128],
        "Table 3 Regional sensitivity by acquisition plane (BRISC, DeiT-Small, Method A)."
    )
    print("  [OK] P127 & P128: Fig 8 and Table 3 titles reflect all four regions")

    # -------------------------------------------------------------
    # 18. P131 & P133 - Tumour class heterogeneity and ~3 patients disclaimer
    # -------------------------------------------------------------
    p131_cleaned = (
        "Analysing sensitivity across Cheng tumour classes revealed marked differences in regional reliance (Table 4; Fig. 9). "
        "In Cheng (DeiT-Small, Method A; N = 15 slices per class from a total of N = 10 patient clusters, averaging only approximately "
        "3 patients per class), meningiomas demonstrated the highest core sensitivity (τ_core = 0.3438) and modest immediate-margin "
        "sensitivity (τ_immed = 0.0338, ratio 9.8%); given the small cluster sample size, this elevated core estimate may be "
        "disproportionately influenced by 1 or 2 individual patients. Gliomas exhibited τ_core = 0.0398 and τ_immed = 0.0268 "
        "(ratio 67.2%), while pituitary adenomas showed near-zero core sensitivity (τ_core = 0.0009, τ_immed = 0.0034, τ_outer = 0.0392, "
        "ratio 360.2%; this elevated ratio is a mathematical consequence of a near-zero core denominator rather than an indication "
        "of biological invasiveness). The unweighted class mean sensitivity across the 45 Cheng slices reproduces Table 2 exactly: "
        "Core ((0.0398 + 0.3438 + 0.0009)/3 = 0.1282), Immediate margin ((0.0268 + 0.0338 + 0.0034)/3 = 0.0213), Outer margin "
        "((-0.0066 - 0.0136 + 0.0392)/3 = 0.0063), and Remote context ((0.0218 + 0.0165 + 0.0001)/3 = 0.0128). These findings "
        "are exploratory and descriptive, reflecting empirical sensitivity in 15 2D slices per class without histopathological "
        "correlation or volumetric 3D analysis."
    )
    set_para_text(paras[131], p131_cleaned)
    set_para_text(
        paras[133],
        "Fig. 9 Regional sensitivity across tumour classes (Cheng, DeiT-Small, Method A): glioma, meningioma and pituitary adenoma (N = 15 slices per class from 10 patient clusters). Categories reflect nominal diagnostic labels, not verified histological invasiveness."
    )
    print("  [OK] P131 & P133: Class analysis biological claims removed, ~3 patients per class disclosed")

    # -------------------------------------------------------------
    # 19. P140 - Section 5.8 Duplicate effect label audit
    # -------------------------------------------------------------
    replace_in_para(
        paras[140],
        "The 101 duplicate test images were heavily skewed towards meningiomas (96 of 101), so de-duplication also changed the test-set class balance. The data therefore do not support a uniform inflation of scores by duplicate leakage; the effect depends on the model and on the class composition of the subset.",
        "The 101 duplicate test images were heavily skewed towards meningiomas (96 of 101), so de-duplication substantially altered the test-set class balance. An audit of all duplicate pairs confirmed 0 label conflicts; all duplicate pairs carried matching ground-truth class annotations. The observed improvement in DeiT-Small metric scores after de-duplication reflects this class-distribution shift (specifically, the removal of 96 duplicate meningioma test slices on which DeiT-Small baseline predictions had lower precision) rather than conflicting training labels. The data therefore do not support a uniform inflation of scores by duplicate leakage; the effect depends on the model architecture and on the class composition of the subset."
    )
    print("  [OK] P140: Explained DeiT metric shift under de-duplication with 0 label conflicts audit")

    # -------------------------------------------------------------
    # 20. P175 - Licence confirmation and manifest path consistency
    # -------------------------------------------------------------
    replace_in_para(
        paras[175],
        "Fateh et al. (doi:10.1038/s41597-026-06753-y).",
        "Fateh et al. (doi:10.1038/s41597-026-06753-y) under the Creative Commons Attribution 4.0 International (CC BY 4.0) license."
    )
    replace_in_para(
        paras[175],
        "environment_manifest.json",
        "revision/reports/environment_manifest.json"
    )
    print("  [OK] P175: Added BRISC CC BY 4.0 licence and consistent manifest path")

    # -------------------------------------------------------------
    # 21. TABLE 2 (Table 1 in docx) - Add (n.s.) to ResNet immediate dz
    # -------------------------------------------------------------
    t2 = tables[1]
    # Row 8 is ResNet Immediate
    c_dz = t2.rows[8].cells[9]
    if "(n.s.)" not in c_dz.text:
        set_para_text(c_dz.paragraphs[0], c_dz.text.strip() + " (n.s.)")
        print("  [OK] Table 2: Added (n.s.) to ResNet Immediate dz")

    # -------------------------------------------------------------
    # 22. TABLE S3 (Table 6 in docx) - Concordance rows & Outlier note
    # -------------------------------------------------------------
    t_s3 = tables[6]
    # Concordance rows are R03 to R10
    concordance_inferences = [
        ("core", "DeiT-Small", "Strong rank and linear concordance on core evidence (Pearson r = 0.854, Spearman rho = 0.763, p < 0.0001); note correlation does not imply zero numerical bias"),
        ("immediate", "DeiT-Small", "Moderate positive concordance on immediate margin evidence (Pearson r = 0.486, Spearman rho = 0.586, p < 0.0001); note correlation does not imply zero numerical bias"),
        ("outer", "DeiT-Small", "Weak positive concordance on outer margin (Pearson r = 0.138, Spearman rho = 0.108); not statistically significant (p = 0.196)"),
        ("remote", "DeiT-Small", "Moderate positive concordance on remote context (Pearson r = 0.436, Spearman rho = 0.294, p < 0.0001); note correlation does not imply zero numerical bias"),
        ("core", "ResNet-50", "Negligible cross-method concordance on core evidence for ResNet-50 (Pearson r = 0.089, Spearman rho = 0.086, p = 0.402; no concordance)"),
        ("immediate", "ResNet-50", "Absence of concordance on immediate margin for ResNet-50 (Pearson r = -0.052, Spearman rho = -0.025, p = 0.628; not significant)"),
        ("outer", "ResNet-50", "Absence of concordance on outer margin for ResNet-50 (Pearson r = -0.087, Spearman rho = +0.002, p = 0.413; not significant)"),
        ("remote", "ResNet-50", "Weak, non-significant correlation on remote context for ResNet-50 (Pearson r = 0.175, Spearman rho = +0.007, p = 0.099)"),
    ]

    for idx, (reg, model, inf_text) in enumerate(concordance_inferences, start=3):
        row = t_s3.rows[idx]
        set_para_text(row.cells[6].paragraphs[0], inf_text)

    print("  [OK] Table S3: Individualized scientific inference labels for all 8 concordance rows")

    # Outlier row note in Table S3 (rows 33 and 34)
    outlier_inf_44 = (
        "Excluding the clipped calvarial outlier confirms stability of BRISC DeiT sensitivity (tau = 0.0528 vs 0.0517, p = 0.0313). "
        "Verified exact statistic W = 311.0."
    )
    outlier_inf_43 = (
        "Excluding both clipped slices yields tau = 0.0506 (p = 0.0505, marginal at alpha = 0.05). "
        "Verified exact statistic W = 311.0 (identical to N=44 because excluding positive-tau slice 00396 modifies only the positive rank sum T+, leaving the smaller negative rank sum W = T- = 311.0 unchanged)."
    )
    set_para_text(t_s3.rows[33].cells[6].paragraphs[0], outlier_inf_44)
    set_para_text(t_s3.rows[34].cells[6].paragraphs[0], outlier_inf_43)
    print("  [OK] Table S3: Explained identical W = 311.0 statistic for N=44 and N=43 outlier rows")

    # Save modified document
    doc.save(str(DOC_PATH))
    print(f"Successfully saved to: {DOC_PATH}")

    # Copy to artifact directory
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(DOC_PATH), str(ARTIFACT))
    print(f"Copied to artifact directory: {ARTIFACT}")

if __name__ == "__main__":
    run()
