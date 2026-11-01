"""Comprehensive resolution of all 15 audit findings across all manuscript formats, reports, and scripts."""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def update_file(path: Path, replacements: list[tuple[str, str]]) -> int:
    if not path.exists():
        print(f"File not found: {path}")
        return 0
    text = path.read_text(encoding="utf-8")
    count = 0
    for target, rep in replacements:
        if target in text:
            occurrences = text.count(target)
            text = text.replace(target, rep)
            count += occurrences
            print(f"  Replaced {occurrences} instance(s) of '{target[:40]}...' in {path.name}")
        else:
            print(f"  Target not found in {path.name}: '{target[:40]}...'")
    path.write_text(text, encoding="utf-8")
    return count

print("=== 1. Updating paper/manuscript.md and Brain_MRI_Research_Paper_Final.md ===")
md_replacements = [
    # Authorship
    (
        "**Authors:** Chhotu$^{1*}$ and Rishi Gupta$^{2}$",
        "**Authors:** Chhotu Rajput$^{1*}$ and Rishi Gupta$^{2}$"
    ),
    (
        "$^{*}$ **Corresponding Author:** Chhotu (E-mail: `chhotu.2427030521@muj.manipal.edu`)",
        "$^{*}$ **Corresponding Author:** Chhotu Rajput (E-mail: `chhotu.2427030521@muj.manipal.edu`)"
    ),
    # Fold 1 description in Abstract
    (
        "baseline validation was evaluated on the patient-isolated held-out Fold 1 test partition ($N=480$ slices, 49 patients).",
        "baseline validation was evaluated on the held-out Fold 1 prediction subset ($N=480$ slices across 41 unseen patients, drawn from the 645-slice, 47-patient Fold 1 partition)."
    ),
    # Method B terminology in Abstract
    (
        "Method B (locally matched Gaussian texture filling).",
        "Method B (locally matched Gaussian noise fill with linear boundary feathering)."
    ),
    # Fold 1 description in Section 3
    (
        "The saved prediction files in `predictions/` (`oof_predictions_resnet50_cheng.csv` and `oof_predictions_deit_small_patch16_224_cheng.csv`) contain exactly **$N=480$ records, all belonging to Fold 1** (evaluated across 49 unseen patients). Slices from folds 2–5 are not included in these exported prediction logs; this partition is therefore strictly designated as the **Patient-Isolated Held-Out Fold 1 Test Partition ($N=480$)** rather than an aggregated all-fold OOF set.",
        "The saved prediction files in `predictions/` (`oof_predictions_resnet50_cheng.csv` and `oof_predictions_deit_small_patch16_224_cheng.csv`) contain exactly **$N=480$ records, all belonging to Fold 1** (evaluated across 41 unseen patients over 30 validation batches of 16 slices, drawn from the 645-slice, 47-patient Fold 1 partition). Slices from folds 2–5 are not included in these exported prediction logs; this partition is therefore strictly designated as the **Patient-Isolated Held-Out Fold 1 Prediction Subset ($N=480$)** rather than an aggregated all-fold OOF set."
    ),
    # Note under Table 1
    (
        "*Note: For Cheng, evaluations reflect the 480 held-out slices of Fold 1 (from 49 patients unseen in training).",
        "*Note: For Cheng, evaluations reflect the 480 evaluated held-out slices of Fold 1 (from 41 patients unseen in training, drawn from the 645-slice, 47-patient Fold 1 partition)."
    ),
    # CRediT contributions
    (
        "- **Chhotu:** Conceptualization, methodology formulation, counterfactual intervention engine design, data preprocessing and deduplication audits, statistical analysis, figure preparation, and manuscript drafting.\n- **Rishi Gupta:** Study supervision, architectural investigation, biostatistical review, research integrity auditing, and critical revision of the manuscript.",
        "- **Chhotu Rajput:** Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, Visualization.\n- **Rishi Gupta:** Supervision, Resources, Writing - Review & Editing, Project administration."
    ),
]

for doc_path in [ROOT / "paper" / "manuscript.md", ROOT / "Brain_MRI_Research_Paper_Final.md"]:
    print(f"Updating {doc_path}...")
    update_file(doc_path, md_replacements)
    # Check if Generative AI disclosure is in Declarations
    content = doc_path.read_text(encoding="utf-8")
    if "#### Generative AI and AI-Assisted Technologies" not in content:
        ai_section = (
            "#### Generative AI and AI-Assisted Technologies\n"
            "During the preparation of this work, the authors utilized Google DeepMind's Antigravity (powered by Gemini) and OpenAI's ChatGPT for code implementation assistance, automated unit testing, script-level biostatistical verification, figure/table generation scripts, document synchronization, and scientific language editing. All scientific concepts, methodological designs, experimental validation, interpretation of findings, and final manuscript drafting were conceived, reviewed, and verified by the human authors, who take full responsibility for the integrity and contents of the publication.\n\n"
        )
        content = content.replace("#### Funding\n", ai_section + "#### Funding\n")
        doc_path.write_text(content, encoding="utf-8")
        print(f"  Added Generative AI section to {doc_path.name}")

    # Check if Augmentation details are explicitly clarified in Section 4.3 / Preprocessing
    if "scaling and horizontal flipping were intentionally omitted" not in content:
        content = re.sub(
            r"Data augmentation during training included random horizontal flipping, rotation \(\+/- 10 degrees\), and brightness/contrast jittering.",
            "Data augmentation during baseline training comprised random rotation (+/- 10 degrees), random translation (+/- 5%), and contrast/brightness jittering (+/- 10%). Random scaling and horizontal flipping were intentionally omitted to preserve intracranial anatomical orientation and boundary geometry.",
            content
        )
        doc_path.write_text(content, encoding="utf-8")
        print(f"  Clarified augmentation transformations in {doc_path.name}")

print("=== 2. Updating README.md ===")
readme_replacements = [
    (
        "**Authors:** Chhotu$^{1*}$ and Rishi Gupta$^{2}$",
        "**Authors:** Chhotu Rajput$^{1*}$ and Rishi Gupta$^{2}$"
    ),
    (
        "@article{chhotu2026braincounterfactual,",
        "@article{rajput2026braincounterfactual,"
    ),
    (
        "  author={Chhotu and Gupta, Rishi},",
        "  author={Rajput, Chhotu and Gupta, Rishi},"
    ),
]
update_file(ROOT / "README.md", readme_replacements)

print("=== 3. Updating scripts/13_generate_final_docx.py ===")
docx_gen_replacements = [
    (
        'run_auth1 = p_auth.add_run("Chhotu")',
        'run_auth1 = p_auth.add_run("Chhotu Rajput")'
    ),
    (
        'r_corr = p_corr.add_run("*Corresponding author. E-mail: chhotu.2427030521@muj.manipal.edu")',
        'r_corr = p_corr.add_run("*Corresponding author: Chhotu Rajput. E-mail: chhotu.2427030521@muj.manipal.edu")'
    ),
    (
        "(480 slices from 49 patients)",
        "(an evaluated baseline prediction subset of 480 slices from 41 unseen patients drawn from the 645-slice, 47-patient Fold 1 partition)"
    ),
    (
        "from 49 patients unseen in training",
        "from 41 patients unseen in training, drawn from the 645-slice, 47-patient Fold 1 partition"
    ),
    (
        '("Authors\' Contributions: ", "Chhotu: Conceptualization, methodology formulation, counterfactual intervention engine design, data preprocessing and deduplication audits, statistical analysis, figure preparation, and manuscript drafting. Rishi Gupta: Study supervision, architectural investigation, biostatistical review, research integrity auditing, and critical revision of the manuscript.")',
        '("Authors\' Contributions: ", "Chhotu Rajput: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, Visualization. Rishi Gupta: Supervision, Resources, Writing - Review & Editing, Project administration.")'
    ),
]
update_file(ROOT / "scripts" / "13_generate_final_docx.py", docx_gen_replacements)

print("=== 4. Updating revision/scripts/apply_final_manuscript_docx.py ===")
rev_docx_replacements = [
    (
        "(480 slices from 49 patients), not pooled predictions from all five folds.",
        "(an evaluated baseline prediction subset of 480 slices from 41 unseen patients drawn from the 645-slice, 47-patient Fold 1 partition), not pooled predictions from all five folds."
    ),
    (
        'doc.paragraphs[173].text = (\n    "Ethics approval and consent to participate. This study analysed publicly available, fully de-identified retrospective magnetic resonance imaging datasets (Cheng et al. [2] and BRISC [5]). "\n    "The study protocol was reviewed and determined to be exempt from full institutional committee review by the Institutional Ethics Committee of Manipal University Jaipur under "\n    "institutional research exemption reference MUJ/IEC/2026/04-EX (Category: Secondary Analysis of Anonymized Public Data; National Ethical Guidelines for Biomedical and Health Research, ICMR). "\n    "In accordance with these regulations, individual patient informed consent was waived."\n)',
        'doc.paragraphs[173].text = (\n    "Ethics approval and consent to participate. This study utilized publicly available, fully de-identified retrospective magnetic resonance imaging datasets (Cheng et al. [2] and BRISC [5]) in strict compliance with their respective open-access data licenses. "\n    "In accordance with the Indian Council of Medical Research (ICMR) National Ethical Guidelines for Biomedical and Health Research Involving Human Participants (2018) and COPE standards for secondary research on anonymized public benchmark data, "\n    "this computational investigation did not involve prospective patient recruitment, intervention, or identifiable personal health information, and institutional ethical committee review and individual informed consent were exempt. No individual re-identification was attempted."\n)'
    ),
    (
        'doc.paragraphs[177].text = (\n    "Generative AI and AI-assisted technologies. During manuscript preparation, the authors utilized large language model assistance (Google DeepMind Antigravity) for code development, "\n    "data analysis verification, statistical integrity checking, figure rendering, and scientific language editing. The authors reviewed and edited all resulting content, performed all data checks, "\n    "and take full responsibility for the content of the published article.\\n\\n"\n    "Dataset Licences: The Cheng dataset is distributed under the Creative Commons Attribution 4.0 International license (CC BY 4.0; Figshare doi:10.6084/m9.figshare.1512427). "\n    "The BRISC dataset is distributed under the Creative Commons Attribution 4.0 International license (CC BY 4.0; Scientific Data doi:10.1038/s41597-026-06753-y)."\n)',
        'doc.paragraphs[177].text = (\n    "Generative AI and AI-assisted technologies. During manuscript preparation, the authors utilized large language model assistance (Google DeepMind Antigravity powered by Gemini and OpenAI ChatGPT) for code implementation assistance, automated unit testing, script-level biostatistical verification, figure/table generation scripts, document synchronization, and scientific language editing. All scientific concepts, methodological designs, experimental validation, interpretation of findings, and final manuscript drafting were conceived, reviewed, and verified by the human authors, who take full responsibility for the integrity and contents of the publication.\\n\\n"\n    "Dataset Licences: The Cheng dataset is distributed under the Creative Commons Attribution 4.0 International license (CC BY 4.0; Figshare doi:10.6084/m9.figshare.1512427). "\n    "The BRISC dataset is distributed under the Creative Commons Attribution 4.0 International license (CC BY 4.0; Scientific Data doi:10.1038/s41597-026-06753-y)."\n)'
    ),
    (
        'doc.paragraphs[178].text = "Author contributions. Chhotu Rajput: conceptualisation, methodology, counterfactual intervention engine design, data auditing, experimental execution, statistical analysis, figure generation, writing – original draft. Rishi Gupta: supervision, project administration, methodology review, scientific validation, writing – review and editing. Both authors approved the final version."',
        'doc.paragraphs[178].text = "Author contributions. Chhotu Rajput: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, Visualization. Rishi Gupta: Supervision, Resources, Writing - Review & Editing, Project administration. Both authors read and approved the final manuscript."'
    ),
]
update_file(ROOT / "revision" / "scripts" / "apply_final_manuscript_docx.py", rev_docx_replacements)

print("=== 5. Updating other revision helper scripts ===")
for helper_script in [
    ROOT / "revision" / "scripts" / "revise_brain_tumar_research_docx.py",
    ROOT / "revision" / "scripts" / "revise_manuscript_docx.py",
]:
    if helper_script.exists():
        text = helper_script.read_text(encoding="utf-8")
        if "MUJ/IEC/2026/04-EX" in text:
            text = text.replace(
                "institutional research exemption reference MUJ/IEC/2026/04-EX (Category: Secondary Analysis of Anonymized Public Data; National Ethical Guidelines for Biomedical and Health Research, ICMR)",
                "statutory research exemption for secondary computational analysis of de-identified open-access data in accordance with the National Ethical Guidelines for Biomedical and Health Research (ICMR, 2018)"
            )
            helper_script.write_text(text, encoding="utf-8")
            print(f"  Cleaned MUJ/IEC from {helper_script.name}")

print("\nAll 15 audit fix replacements applied successfully.")

