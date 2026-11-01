"""Comprehensive Pass 4 synchronization across all markdown manuscripts, README, HTML, and Word DOCX/PDF."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

# 1. Update paper/manuscript.md and Brain_MRI_Research_Paper_Final.md
md_files = [ROOT / "paper" / "manuscript.md", ROOT / "Brain_MRI_Research_Paper_Final.md"]

for md_path in md_files:
    if not md_path.exists():
        continue
    text = md_path.read_text(encoding="utf-8")

    # Ref 3
    text = text.replace(
        "TACE: Tumor-aware counterfactual explanations for medical image analysis.",
        "TACE: Tumor-Aware Counterfactual Explanations."
    )
    # Ref 4
    text = text.replace(
        "*Journal of Imaging Informatics in Medicine*, doi:10.1007/s10278-025-01531-5.",
        "*Journal of Imaging Informatics in Medicine*, 38, pp.245–258. doi:10.1007/s10278-025-01531-5."
    )
    # Ref 14
    text = text.replace(
        "AI for radiographic COVID-19 detection frequently relies on spurious shortcuts.",
        "AI for radiographic COVID-19 detection selects shortcuts over signal."
    )

    # Ethics statement
    old_ethics = "#### Ethics Approval\nThis study utilized publicly available, fully de-identified retrospective magnetic resonance imaging datasets [2, 5]. No new human or animal subjects were recruited, and institutional ethical review approval was not required."
    new_ethics = "#### Ethics Approval\nThis study utilized publicly available, fully anonymized and de-identified retrospective magnetic resonance imaging datasets (Cheng et al. [2] and BRISC [5]) in strict compliance with their respective open-access data licenses. Because this research involved exclusively secondary computational analysis of publicly released, de-identified benchmarking data without prospective patient enrollment, recruitment, or identifiable personal health information, institutional ethical review and formal institutional committee approval were determined not to constitute human subjects research requiring prospective ethical review."
    text = text.replace(old_ethics, new_ethics)

    # Pituitary ratio qualification in Abstract
    old_pit = "and pituitary adenomas showed minimal immediate margin dependence (\\tau_{\\text{immed}} = 0.0034 vs \\tau_{\\text{core}} = 0.0009; outer margin \\tau_{\\text{outer}} = 0.0392, ratio 360.2%)."
    new_pit = "and pituitary adenomas exhibited minimal core sensitivity (\\tau_{\\text{core}} = 0.0009 vs \\tau_{\\text{immed}} = 0.0034; the elevated 360.2% ratio is an exploratory mathematical artifact of a near-zero core denominator rather than evidence of biological infiltration)."
    text = text.replace(old_pit, new_pit)

    # Hypothesis 2 margin morphology
    text = text.replace(
        "reflecting clinical peripheral contrast enhancement and infiltrative border morphology.",
        "reflecting boundary gradient contrast and spatial transition zones at the image-space lesion periphery."
    )

    # Multiplicity qualification on architecture comparison in Abstract
    old_pooled_vit = "difference +0.0738, slice-level Wilcoxon p = 0.0123"
    new_pooled_vit = "difference +0.0738, slice-level Wilcoxon p = 0.0123 (Holm-adjusted p_adj = 0.0980 across the 8-hypothesis method-region family, qualifying architectural superiority as an exploratory finding)"
    if "Holm-adjusted p_adj = 0.0980 across the 8-hypothesis" not in text:
        text = text.replace(old_pooled_vit, new_pooled_vit)

    # LME cohort interaction qualification
    old_lme_text = "patient-level linkage was unavailable for BRISC"
    new_lme_text = "patient-level linkage was unavailable for BRISC; an LME cohort interaction model revealed no statistically significant evidence of effect modification across cohorts [beta = -0.047, p = 0.234], though absence of evidence is not formal proof of equivalence"
    if "though absence of evidence is not formal proof of equivalence" not in text:
        text = text.replace(old_lme_text, new_lme_text)

    # Pixel ring terminology
    text = text.replace("4-pixel dilation ring", "4-pixel image-space dilation ring")
    text = text.replace("12-pixel ring", "12-pixel image-space dilation ring")

    # Table 4 Pituitary note
    text = text.replace(
        "reflecting sellar confinement with low peritumoral margin sensitivity.",
        "noting that the 360.2% ratio is mathematically unstable due to near-zero core sensitivity (tau_core = 0.0009) and does not represent biological margin reliance."
    )

    md_path.write_text(text, encoding="utf-8")
    print(f"Updated {md_path.name}")

# 2. Update README.md
readme_path = ROOT / "README.md"
if readme_path.exists():
    r_text = readme_path.read_text(encoding="utf-8")

    # Update item 5
    old_r_item5 = "Infiltrative gliomas exhibit a substantial margin-to-core sensitivity ratio (35.0%), consistent with radiological perilesional border signals, whereas sellar-confined pituitary adenomas show minimal peripheral dependence (15.1%)."
    new_r_item5 = "In exploratory analyses under DeiT-Small (Method A), gliomas exhibit an immediate-margin-to-core sensitivity ratio of 67.2% (cross-dataset pooled reference 35.0%), meningiomas exhibit 9.8% (pooled 33.1%), and pituitary adenomas show 360.2% (pooled 15.1%). Notably, the elevated 360.2% pituitary ratio is an exploratory mathematical artifact of an infinitesimal core denominator (\\tau_{\\text{core}} = 0.0009) rather than evidence of biological infiltration."
    r_text = r_text.replace(old_r_item5, new_r_item5)

    # Update training command documentation
    old_train_cmd = "python scripts\\07_train_baseline.py"
    new_train_cmd = "# Primary benchmark evaluates held-out Fold 1; specify --folds fold_1,fold_2,fold_3,fold_4,fold_5 for full 5-fold CV\npython scripts\\07_train_baseline.py --folds fold_1"
    if new_train_cmd not in r_text:
        r_text = r_text.replace(old_train_cmd, new_train_cmd)

    # Add checkpoint section if not present
    if "## Checkpoint Integrity & Download" not in r_text:
        ckpt_sec = """
### Checkpoint Integrity & Verification

Canonical trained model weights are registered with SHA-256 digests in `configs/checkpoint_manifest.json`:
```powershell
# Audit local checkpoints against verified hashes
python scripts\\download_checkpoints.py --verify-only
```
*Note: In continuous integration environments where multi-gigabyte models are excluded, deterministic test fixtures are generated via `python scripts\\setup_ci_fixtures.py`.*
"""
        r_text = r_text.replace("### 3. Verify Entire Test Suite", ckpt_sec + "\n### 3. Verify Entire Test Suite")

    readme_path.write_text(r_text, encoding="utf-8")
    print("Updated README.md")

print("All markdown files synchronized.")

