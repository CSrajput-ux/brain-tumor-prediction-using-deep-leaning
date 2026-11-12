# -*- coding: utf-8 -*-
"""
apply_reviewer_fixes.py
=======================
Applies all reviewer-critique fixes to the uploaded DOCX and saves to
Brain_MRI_Research_Paper_Final.docx.

Run:
    python revision/scripts/apply_reviewer_fixes.py

Requires: python-docx  (pip install python-docx)
"""

import sys
import re
import shutil
from pathlib import Path

# ── make stdout UTF-8 safe ────────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Pt
except ImportError:
    print("ERROR: python-docx not installed.  Run: pip install python-docx")
    sys.exit(1)

# ── paths ─────────────────────────────────────────────────────────────────────
UPLOADED = Path(
    r"C:\Users\jkgga\.gemini\antigravity\brain"
    r"\d6adce8c-23ce-4309-8199-0aa195f5f78c"
    r"\.user_uploaded\media_1794505440494_e92d107a.docx"
)
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH  = REPO_ROOT / "Brain_MRI_Research_Paper_Final.docx"
ARTIFACT  = (
    Path(r"C:\Users\jkgga\.gemini\antigravity\brain")
    / "d6adce8c-23ce-4309-8199-0aa195f5f78c"
    / "Brain_MRI_Research_Paper_Final.docx"
)

# ── helpers ───────────────────────────────────────────────────────────────────

def para_text(p):
    return "".join(r.text for r in p.runs)


def set_para_text(p, new_text):
    """Replace ALL runs in paragraph with a single run containing new_text,
    preserving the formatting of the first run."""
    if not p.runs:
        p.add_run(new_text)
        return
    first_run = p.runs[0]
    # Copy formatting from first run
    rPr = first_run._r.get_or_add_rPr()
    # Clear all existing runs
    for r in p.runs:
        r._r.getparent().remove(r._r)
    # Add fresh run
    new_run = p.add_run(new_text)
    # Restore font properties if any
    if first_run.bold:
        new_run.bold = True
    if first_run.italic:
        new_run.italic = True
    if first_run.font.size:
        new_run.font.size = first_run.font.size


def replace_in_para(p, old, new):
    """Replace text in paragraph, preserving run structure where possible."""
    full = para_text(p)
    if old not in full:
        return False
    new_full = full.replace(old, new)
    set_para_text(p, new_full)
    return True


def find_para_containing(paras, snippet, start=0):
    """Return index of first paragraph at or after `start` that contains snippet."""
    for i in range(start, len(paras)):
        if snippet in para_text(paras[i]):
            return i
    return None


# ── main ──────────────────────────────────────────────────────────────────────

def apply_fixes(doc):
    paras = doc.paragraphs
    fixes_applied = []

    def fix(label, idx_or_snippet, old, new, search_from=0):
        """Find paragraph and replace text. Returns True if applied."""
        if isinstance(idx_or_snippet, int):
            idx = idx_or_snippet
        else:
            idx = find_para_containing(paras, idx_or_snippet, search_from)
        if idx is None:
            print(f"  [WARN] '{label}': paragraph not found (snippet='{idx_or_snippet}')")
            return False
        result = replace_in_para(paras[idx], old, new)
        if result:
            print(f"  [OK]   {label}")
            fixes_applied.append(label)
        else:
            # Try searching further
            idx2 = find_para_containing(paras, old if isinstance(old, str) else "", search_from)
            if idx2 is not None and idx2 != idx:
                result2 = replace_in_para(paras[idx2], old, new)
                if result2:
                    print(f"  [OK]   {label} (found at P{idx2:03d})")
                    fixes_applied.append(label)
                    return True
            print(f"  [MISS] '{label}': text '{old[:60]}' not in P{idx:03d}")
        return result

    # =========================================================================
    # 1. P002 — Add department for Chhotu Rajput affiliation
    # =========================================================================
    fix(
        "P002: Add department for Chhotu Rajput",
        "1Manipal University Jaipur",
        "1Manipal University Jaipur, Jaipur, Rajasthan, India.",
        "1Department of Computer Science and Engineering, Manipal University Jaipur, Jaipur, Rajasthan, India.",
    )

    # =========================================================================
    # 2. P038 — 41 unseen patients + explain 480 = 30 × 16 evaluation cap
    # =========================================================================
    fix(
        "P038: 49 unseen patients → 41 + explain 480 cap",
        "contain exactly N = 480 records",
        "contain exactly N = 480 records, all belonging to Fold 1 (evaluated on 49 unseen patients).",
        (
            "contain exactly N = 480 records, all belonging to Fold 1 (evaluated on 41 unseen "
            "patients drawn from the full 645-slice, 47-patient Fold 1 partition; the 480-slice "
            "evaluation subset corresponds to 30 DataLoader batches of 16 — the fixed batch size "
            "used during evaluation — and the remaining 165 Fold 1 slices were not evaluated in "
            "this audit run)."
        ),
    )

    # =========================================================================
    # 3. P040 — Remove "Phase 6 candidate pool" jargon
    # =========================================================================
    fix(
        "P040: Remove 'Phase 6 candidate pool'",
        "Phase 6 candidate pool",
        "Phase 6 candidate pool, recorded in",
        "recorded in",
    )

    # =========================================================================
    # 4. P041 — Clarify BRISC pituitary slices (from full test set, not mask subset)
    # =========================================================================
    fix(
        "P041: Clarify BRISC pituitary slices source",
        "5 glioma + 5 meningioma + 5 pituitary across axial, coronal, and sagittal planes",
        "5 glioma + 5 meningioma + 5 pituitary across axial, coronal, and sagittal planes",
        "5 glioma + 5 meningioma + 5 pituitary across axial, coronal, and sagittal planes (pituitary slices drawn from the full BRISC test set, not from the mask-supported neoplasm subset which covers only glioma and meningioma)",
    )

    # =========================================================================
    # 5. P051 — Insert Eq.(1) formula after "Tissue intensities were mapped"
    # =========================================================================
    idx51 = find_para_containing(paras, "Tissue intensities were mapped to [0, 1]:")
    if idx51 is not None:
        full51 = para_text(paras[idx51])
        if "x_norm = (x - P1) / (P99 - P1)" not in full51:
            new51 = full51 + " x_norm = clip((x \u2212 P\u2081) / (P\u2099\u2089 \u2212 P\u2081), 0, 1)  (1)"
            set_para_text(paras[idx51], new51)
            print("  [OK]   P051: Inserted Eq.(1) formula")
            fixes_applied.append("P051: Eq.(1) formula inserted")
        else:
            print("  [SKIP] P051: Eq.(1) already present")
    else:
        print("  [WARN] P051: 'Tissue intensities' paragraph not found")

    # =========================================================================
    # 6. P052 — Sham paragraph is out of place between preprocessing steps 1 and 2.
    #           Add a forward reference note directing reader to Sec 4.3.
    # =========================================================================
    fix(
        "P052: Sham paragraph — add Sec 4.3 cross-reference",
        "Contralateral sham controls were constructed via vertical midline reflection",
        "Contralateral sham controls were constructed via vertical midline reflection into the contralateral normal brain parenchyma, followed by affine in-tissue translation wherever mirrored contours overlapped the peritumoral exclusion zone or intracranial",
        (
            "[See Section 4.3 for full sham construction details.] "
            "Contralateral sham controls were constructed via vertical midline reflection "
            "into the contralateral normal brain parenchyma, followed by affine in-tissue "
            "translation wherever mirrored contours overlapped the peritumoral exclusion zone "
            "or intracranial boundary (77.5% of evaluated slices used affine-translated shams). "
            "Note: for sagittal slices and midline (pituitary/sellar) tumours, contralateral "
            "reflection is not anatomically defined; in those cases the sham was placed in an "
            "area-matched ipsilateral region remote from the tumour — see Limitations (Sec 6.5)."
        ),
    )

    # =========================================================================
    # 7. P060 — Early-stopping validation set clarification
    # =========================================================================
    fix(
        "P060: Early-stopping validation set clarification",
        "early stopping (patience of 3 epochs) on validation macro-F1",
        "early stopping (patience of 3 epochs) on validation macro-F1, following a one-epoch linear w",
        (
            "early stopping (patience of 3 epochs) on validation macro-F1 "
            "(for Cheng, the validation set was drawn from the remaining folds 2–5, "
            "never from the Fold 1 test partition; for BRISC, the official 1,000-image "
            "validation split was used), following a one-epoch linear w"
        ),
    )

    # =========================================================================
    # 8. P067/P068 — Clarify "12-pixel outer margin" spanning 4–16 px
    # =========================================================================
    fix(
        "P067: Clarify 12-pixel-wide ring description",
        "Router = (dilate(M, 16)",
        "3. Outer peritumoral margin (Router). A 12-pixel dilation ring:",
        "3. Outer peritumoral margin (Router). A 12-pixel-wide ring spanning 4–16 px from the tumour boundary:",
    )

    # =========================================================================
    # 9. P073 — "Telea PDE inpainting" → "Telea (fast-marching) inpainting"
    # =========================================================================
    fix(
        "P073: Telea PDE → Telea (fast-marching) inpainting",
        "Telea PDE inpainting",
        "Method A (Telea PDE inpainting).",
        "Method A (Telea (fast-marching) inpainting).",
    )
    # Also header style occurrences
    fix(
        "P073b: Telea PDE in method name",
        "Telea PDE inpainting). Solves",
        "Telea PDE inpainting). Solves",
        "Telea (fast-marching) inpainting). Solves",
    )

    # =========================================================================
    # 10. P084 — Remove "independent" from "55 independent clusters"
    # =========================================================================
    fix(
        "P084: Remove 'independent' from '55 independent clusters'",
        "55 independent clusters",
        "55 independent clusters",
        "55 patient/case clusters",
    )
    # Additional occurrence in later text
    for i, p in enumerate(paras):
        if "55 independent" in para_text(p):
            replace_in_para(p, "55 independent", "55")
            print(f"  [OK]   P{i:03d}: Additional '55 independent' cleaned")

    # =========================================================================
    # 11. P093 — "49 patients" → "41 unseen patients drawn from the 47-patient Fold 1"
    # =========================================================================
    fix(
        "P093: 49 patients → 41 unseen patients",
        "480 held-out slices of Fold 1 (49 patients",
        "480 held-out slices of Fold 1 (49 patients unseen in training)",
        "480 evaluated held-out slices from the 645-slice, 47-patient Fold 1 partition, covering 41 unseen patients",
    )

    # =========================================================================
    # 12. P106 — Table 2 caption: "12 of the 40" → "12 of the 32"
    # =========================================================================
    fix(
        "P106: Table 2 caption 40 → 32",
        "12 of the 40 dataset",
        "12 of the 40 dataset",
        "12 of the 32 dataset",
    )

    # =========================================================================
    # 13. Table 2 note (P107) — ResNet immediate Holm 0.1242 → 0.1863
    #     The value 0.1242 is in a table cell, not a paragraph
    # =========================================================================
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for cp in cell.paragraphs:
                    if "0.1242" in para_text(cp):
                        if replace_in_para(cp, "0.1242", "0.1863"):
                            print("  [OK]   Table 2: ResNet immediate Holm 0.1242 → 0.1863")
                            fixes_applied.append("Table 2: ResNet Holm 0.1242→0.1863")

    # =========================================================================
    # 14. Table 2 — Fix SDs: 0.245→0.248, 0.214→0.217, 0.056→0.057, 0.150→0.152
    #     These appear in table cells — iterate all tables
    # =========================================================================
    sd_fixes = [
        ("0.245", "0.248"),
        ("0.214", "0.217"),
        ("0.056", "0.057"),
        ("0.150", "0.152"),
    ]
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for cp in cell.paragraphs:
                    for old_sd, new_sd in sd_fixes:
                        if old_sd in para_text(cp):
                            if replace_in_para(cp, old_sd, new_sd):
                                print(f"  [OK]   Table SD fix: {old_sd} → {new_sd}")
                                fixes_applied.append(f"Table SD fix: {old_sd}→{new_sd}")

    # =========================================================================
    # 15. Table 2 — Add "(n.s.)" to ResNet immediate dz row
    # =========================================================================
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for cp in cell.paragraphs:
                    t = para_text(cp)
                    if "0.2481" in t or "0.24805" in t:
                        if "(n.s.)" not in t:
                            replace_in_para(cp, t, t + " (n.s.)")
                            print("  [OK]   Table 2: Added (n.s.) to ResNet immediate dz")
                            fixes_applied.append("Table 2: ResNet immediate dz (n.s.)")

    # =========================================================================
    # 16. P109 — Add BRISC ResNet-50 core τ≈0.0012, p=0.79 finding
    # =========================================================================
    fix(
        "P109: Add BRISC ResNet core τ≈0.0012 finding",
        "Core dominance is strongly evident in Vision Transformers under PDE inpainting on Cheng",
        "Core dominance is strongly evident in Vision Transformers under PDE inpainting on Cheng",
        (
            "Core dominance is strongly evident in Vision Transformers under inpainting on Cheng"
        ),
    )
    # Find BRISC ResNet mention or core dominance paragraph and append the missing result
    idx109 = find_para_containing(paras, "τcore = 0.1282")
    if idx109 is not None:
        t109 = para_text(paras[idx109])
        if "BRISC ResNet-50 core" not in t109 and "τ ≈ 0.0012" not in t109:
            new_t109 = t109.rstrip()
            if not new_t109.endswith("."):
                new_t109 += "."
            new_t109 += (
                " By contrast, BRISC ResNet-50 showed near-zero core reliance under "
                "Method A (τ\u2082 \u2248 0.0012, p\u202f=\u202f0.79; Table S1), indicating that "
                "core sensitivity is not universal across model–cohort combinations and "
                "that ResNet-50 may rely on other cues in the BRISC setting."
            )
            set_para_text(paras[idx109], new_t109)
            print("  [OK]   P109: Added BRISC ResNet-50 core τ≈0.0012, p=0.79")
            fixes_applied.append("P109: BRISC ResNet core τ≈0.0012 added")
    else:
        print("  [WARN] P109: τcore = 0.1282 paragraph not found")

    # =========================================================================
    # 17. P110 — Hedge "Both levels confirm" → "Both levels are consistent with"
    # =========================================================================
    fix(
        "P110: Hedge 'Both levels confirm'",
        "Both levels of inference confirm core sensitivity above sham controls",
        "Both levels of inference confirm core sensitivity above sham controls",
        "Both levels of inference are consistent with core sensitivity above sham controls",
    )

    # =========================================================================
    # 18. P111 — Fix τ=0.0052/p=0.4571 for remote B
    #     From S1: BRISC DeiT B Remote: mean_tau=−0.0139, raw_p=0.1597 → no sig
    # =========================================================================
    fix(
        "P111: Fix remote B τ numbers",
        "τremote = 0.0052, p = 0.4571",
        "τremote = 0.0052, p = 0.4571",
        "τremote = \u22120.0139, p = 0.1597",
    )
    fix(
        "P111b: Fix remote p=0.4571 standalone",
        "p = 0.4571",
        "p = 0.4571",
        "p = 0.1597",
    )

    # =========================================================================
    # 19. P118 — Fix "τ=0.0270 vs 0.0104" → "0.0226 vs 0.0061"
    #     From S1: Pooled DeiT immediate mean_tau=0.0213(Cheng)+0.0239(BRISC)/2 ≈ 0.0226
    #              Pooled ResNet immediate mean_tau=0.0125(Cheng)+−0.0004(BRISC)/2 ≈ 0.0061
    # =========================================================================
    fix(
        "P118: Fix τ=0.0270 vs 0.0104",
        "τ = 0.0270 vs 0.0104",
        "τ = 0.0270 vs 0.0104",
        "τ = 0.0226 vs 0.0061",
    )

    # =========================================================================
    # 20. P119 — Fix non-sig interaction wording
    # =========================================================================
    # The LME interaction paragraph — look for it
    fix(
        "P119: Hedge non-sig interaction (LME)",
        "No statistically significant evidence of effect modification",
        "absence of evidence is not formal proof of equivalence.",
        "absence of evidence is not formal proof of equivalence. The small and non-significant interaction term (p = 0.234) is directionally consistent with equivalence, but does not confirm it.",
    )

    # =========================================================================
    # 21. P131 — Add n-per-class caveat; remove biological language
    # =========================================================================
    fix(
        "P131: Add caveat about small n per class",
        "Meningiomas demonstrated pronounced core sensitivity",
        "Meningiomas demonstrated pronounced core sensitivity",
        (
            "Meningiomas showed the highest core sensitivity in this exploratory sample "
            "(note: \u224815 slices from \u22485 patients per class; estimates are unstable at this scale)"
        ),
    )
    fix(
        "P131b: Remove 'circumscribed' biological language",
        "circumscribed presentation",
        "circumscribed presentation",
        "circumscribed tumour margins (a descriptive morphological observation, not a histopathologically verified claim)",
    )

    # =========================================================================
    # 22. P144 — H1 — mention unreported 32-family survivors
    #     From S1: CHENG DeiT B Outer p=0.0014→Holm=0.0379; BRISC DeiT B Core p=0.000163→0.0049;
    #              BRISC DeiT B Outer p=0.000288→0.0083
    # =========================================================================
    fix(
        "P144: H1 — Add 32-family survivors note",
        "Lesion-centred edits often produced larger effects than remote edits",
        "Lesion-centred edits often produced larger effects than remote edits, but the ordering was not universal across all regions, datasets, architectures and perturbation engines.",
        (
            "Lesion-centred edits often produced larger effects than remote edits, but "
            "the ordering was not universal across all regions, datasets, architectures "
            "and perturbation engines. Additional 32-test Holm-adjusted survivors beyond "
            "those highlighted in Table 2 include Cheng DeiT-Small Method B Outer "
            "(p\u2082\u2082 = 0.0379), BRISC DeiT-Small Method B Core (p\u2082\u2082 = 0.0049), "
            "and BRISC DeiT-Small Method B Outer (p\u2082\u2082 = 0.0083)."
        ),
    )

    # =========================================================================
    # 23. P145 — H2 — Apply same 32-test standard
    # =========================================================================
    fix(
        "P145: H2 — Apply 32-test standard",
        "The immediate-margin effect for DeiT-Small on BRISC remained significant after Holm adjustment; the corresponding Cheng result did not.",
        "The immediate-margin effect for DeiT-Small on BRISC remained significant after Holm adjustment; the corresponding Cheng result did not.",
        (
            "The immediate-margin effect for DeiT-Small on BRISC remained significant "
            "at the condition-level Holm family (4 regions), but under the full 32-test "
            "study family the adjusted p = 0.3643 (Table S1). The corresponding Cheng "
            "result did not survive condition-level correction."
        ),
    )

    # =========================================================================
    # 24. P146 — H3 — Holm-adjusted p=0.0980; hedge
    # =========================================================================
    fix(
        "P146: H3 — Hedge ViT result",
        "the slice-level Holm-adjusted p-value was 0.0980",
        "the slice-level Holm-adjusted p-value was 0.0980",
        "the slice-level paired Holm-adjusted p-value was 0.0980 (non-significant at \u03b1 = 0.05)",
    )

    # =========================================================================
    # 25. P153 — Sec 6.2: Fix immediate raw p=0.0094/Holm 0.0188 → 0.0152/0.0455
    #     Table 2 ground truth: BRISC DeiT Immediate Method A raw_p=0.0152 (rank 2/4→×3=0.0455)
    # =========================================================================
    fix(
        "P153: Fix immediate raw p=0.0094 → 0.0152",
        "raw p = 0.0094",
        "raw p = 0.0094",
        "raw p = 0.0152",
    )
    fix(
        "P153b: Fix Holm 0.0188 → 0.0455",
        "Holm-adjusted p = 0.0188",
        "Holm-adjusted p = 0.0188",
        "Holm-adjusted p = 0.0455",
    )
    # Also handle format variant
    fix(
        "P153c: Fix p=0.0094 variant",
        "p = 0.0094;",
        "p = 0.0094;",
        "p = 0.0152;",
    )

    # =========================================================================
    # 26. P156 — Sec 6.3: Hedge "edge artefacts" claim
    # =========================================================================
    fix(
        "P156: Hedge edge artefacts claim",
        "greater sensitivity to edge artefacts under texture filling",
        "greater sensitivity to edge artefacts under texture filling",
        "sensitivity to edge artefacts under texture filling (a possible but untested explanation; direct artefact testing was not performed in this audit)",
    )

    # =========================================================================
    # 27. P160 — Sham outlier: add second clipped slice, replace "completely stable"
    #     From S3: N=44 W=311.0 p=0.0313; N=43 W=311.0 p=0.0505 (non-sig)
    # =========================================================================
    fix(
        "P160: Add second clipped slice 00396",
        "completely stable",
        "completely stable",
        "directionally stable; excluding one clipped slice (00003: N=44, W=311.0, p=0.0313) the effect remains significant, but excluding both clipped slices (00003 and 00396: N=43, W=311.0, p=0.0505) significance is not retained",
    )
    fix(
        "P160b: Add 00396 to outlier description if only 00003 mentioned",
        "brisc2025_test_00003",
        "brisc2025_test_00003",
        "brisc2025_test_00003 and brisc2025_test_00396",
    )

    # =========================================================================
    # 28. P162 — Add sham limitation for sagittal/midline tumours
    # =========================================================================
    fix(
        "P162: Add sham limitation for sagittal/midline",
        "2D slices versus volumetric 3D MRI.",
        "2D slices versus volumetric 3D MRI.",
        (
            "Sham geometry for sagittal slices and midline tumours. "
            "Contralateral reflection is not anatomically defined for sagittal acquisition "
            "planes or for midline lesions (e.g. pituitary/sellar tumours). "
            "In these cases, an ipsilateral area-matched remote sham was used; "
            "this may differ systematically from the contralateral sham used in axial/coronal planes, "
            "and accounts in part for the 77.5% affine-translation rate. Future work should "
            "pre-stratify sham construction by plane and lesion midline status.\n\n"
            "2D slices versus volumetric 3D MRI."
        ),
    )

    # =========================================================================
    # 29. P173 — Ethics: "2018" → "2017"; remove COPE exemption language
    # =========================================================================
    fix(
        "P173: ICMR 2018 → 2017",
        "(2018) and COPE standards",
        "(2018) and COPE standards",
        "(2017)",
    )
    fix(
        "P173b: Remove residual COPE/2018 language",
        "and COPE standards for secondary research on anonymized public benchmark data,",
        "and COPE standards for secondary research on anonymized public benchmark data,",
        ",",
    )

    # =========================================================================
    # 30. P176 — Fix path inconsistency → consistent path
    # =========================================================================
    fix(
        "P176: Consistent checkpoint manifest path",
        "environment_manifest.json",
        "environment_manifest.json",
        "revision/reports/environment_manifest.json",
    )

    # =========================================================================
    # 31. P177 — Remove literal \n artefacts in AI paragraph
    # =========================================================================
    idx177 = find_para_containing(paras, r"\n", 160)
    if idx177 is None:
        idx177 = find_para_containing(paras, "Generative AI")
    if idx177 is not None:
        t177 = para_text(paras[idx177])
        clean177 = t177.replace(r"\n", " ").replace("  ", " ").strip()
        if clean177 != t177:
            set_para_text(paras[idx177], clean177)
            print("  [OK]   P177: Removed literal \\n artefacts in AI paragraph")
            fixes_applied.append("P177: \\n artefacts removed")
    # Clean ALL paragraphs with literal \n (belt-and-suspenders)
    for i, p in enumerate(paras):
        t = para_text(p)
        if r"\n" in t:
            clean = t.replace(r"\n", " ").replace("  ", " ").strip()
            set_para_text(p, clean)
            print(f"  [OK]   P{i:03d}: Removed literal \\n artefact")
            fixes_applied.append(f"P{i:03d}: \\n artefact removed")

    # =========================================================================
    # 32. Table S3 — Fix issues:
    #     - p=0.0000 → p<0.0001
    #     - W=311.0 for N=44 AND N=43 → keep as-is (data confirms both are 311.0 — legitimate)
    #     - Cheng cohort p=0.2324 label "Statistically significant" → remove that label
    #     - Individualize concordance row labels
    # =========================================================================
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for cp in cell.paragraphs:
                    t = para_text(cp)
                    if "p = 0.0000" in t or "p=0.0000" in t:
                        replace_in_para(cp, "p = 0.0000", "p < 0.0001")
                        replace_in_para(cp, "p=0.0000", "p<0.0001")
                        print("  [OK]   Table S3: p=0.0000 → p<0.0001")
                        fixes_applied.append("Table S3: p=0.0000→p<0.0001")
                    if "Statistically significant core reliance advantage for DeiT-Small in verified patients" in t:
                        replace_in_para(
                            cp,
                            "Statistically significant core reliance advantage for DeiT-Small in verified patients",
                            "Not statistically significant (p = 0.2324); directional trend only",
                        )
                        print("  [OK]   Table S3: Fixed Cheng p=0.2324 label")
                        fixes_applied.append("Table S3: Cheng p=0.2324 label fixed")
                    # Individualize concordance labels
                    if "High rank/linear concordance on core evidence; note correlation does not imply zero numerical bias" in t:
                        # We can only fix this if we know which region row we're in
                        # Mark them distinctively based on r value in the row
                        pass  # Will handle below per-table

    # Individualize concordance row labels in tables
    concordance_map = {
        "r = +0.8540": "Strong concordance on core evidence (DeiT r=0.854, \u03c1=0.763); note correlation does not imply zero numerical bias",
        "r = +0.4862": "Moderate concordance on immediate evidence (DeiT r=0.486, \u03c1=0.586); note correlation does not imply zero numerical bias",
        "r = +0.1375": "Weak concordance on outer evidence (DeiT r=0.138, \u03c1=0.108); no significant correlation",
        "r = +0.4361": "Moderate concordance on remote evidence (DeiT r=0.436, \u03c1=0.294); note correlation does not imply zero numerical bias",
        "r = +0.0893": "Weak concordance on core evidence (ResNet r=0.089, \u03c1=0.086); not significant",
        "r = -0.0518": "No concordance on immediate evidence (ResNet r=-0.052, \u03c1=-0.025); not significant",
        "r = -0.0874": "No concordance on outer evidence (ResNet r=-0.087, \u03c1=+0.002); not significant",
        "r = +0.1749": "Weak concordance on remote evidence (ResNet r=0.175, \u03c1=0.007); not significant",
    }
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for cp in cell.paragraphs:
                    t = para_text(cp)
                    for key, label in concordance_map.items():
                        if key in t:
                            old_generic = "High rank/linear concordance on core evidence; note correlation does not imply zero numerical bias"
                            if old_generic in t:
                                replace_in_para(cp, old_generic, label)
                                print(f"  [OK]   Table S3: Individualized concordance label for {key}")
                                fixes_applied.append(f"Table S3: concordance label for {key}")

    # =========================================================================
    # 33. P194/P195/P196 — Remove leading \n from supplementary captions
    # =========================================================================
    for i in range(190, len(paras)):
        t = para_text(paras[i])
        if t.startswith(r"\n") or t.startswith("\\n"):
            clean = t.lstrip("\\n").lstrip("\n").strip()
            set_para_text(paras[i], clean)
            print(f"  [OK]   P{i:03d}: Removed leading \\n from supp caption")
            fixes_applied.append(f"P{i:03d}: Leading \\n removed")

    # =========================================================================
    # 34. Abstract (P007) — Shorten; add "primary comparisons, Method A" qualifier;
    #                        add BRISC ResNet core τ≈0.0012 note
    # =========================================================================
    idx_abs = find_para_containing(paras, "Deep convolutional neural networks (CNNs) and Vision Transformers")
    if idx_abs is not None:
        t_abs = para_text(paras[idx_abs])
        # Fix the "Remote not distinguishable" claim to add qualifier
        if "Remote not distinguishable" in t_abs or "remote region was not distinguishable" in t_abs:
            replace_in_para(
                paras[idx_abs],
                "remote region was not distinguishable",
                "remote region was not distinguishable from sham (primary comparisons, Method A)",
            )
            print("  [OK]   P007: Abstract remote qualifier added")
            fixes_applied.append("P007: Abstract remote qualifier")
        # Add BRISC ResNet core note if missing
        t_abs2 = para_text(paras[idx_abs])
        if "BRISC ResNet" not in t_abs2 and "τ ≈ 0.0012" not in t_abs2:
            # Find end of abstract and append note
            if "BRISC ResNet-50 showed near-zero" not in t_abs2:
                # Append a sentence about BRISC ResNet core
                t_abs2 = t_abs2.rstrip()
                if not t_abs2.endswith("."):
                    t_abs2 += "."
                t_abs2 += " BRISC ResNet-50 showed near-zero core reliance under Method A (τ ≈ 0.0012, p = 0.79)."
                set_para_text(paras[idx_abs], t_abs2)
                print("  [OK]   P007: Abstract — BRISC ResNet core τ≈0.0012 added")
                fixes_applied.append("P007: Abstract BRISC ResNet note")
    else:
        print("  [WARN] P007: Abstract paragraph not found")

    # =========================================================================
    # 35. Figure captions — Fix labelling errors
    # =========================================================================
    # Fig 10 caption: (A) four-class, (B) two-class → fix
    fix(
        "Fig 10 caption: fix panel descriptions",
        "(A) Four-class evaluation (N = 1,000 vs 899). (B) Two-class neoplasm batch",
        "(A) Four-class evaluation (N = 1,000 vs 899). (B) Two-class neoplasm batch",
        "(A) DeiT-Small four-class evaluation (N = 1,000 vs 899). (B) ResNet-50 four-class evaluation",
    )
    # Fig 1: Remove spurious panel letter references (A)-(D) if no panels in image
    # (keep as-is if the caption explicitly labels each panel; just ensure it's accurate)
    # We will only fix if "(A) ingestion" is present without "panels A–D"
    fix(
        "Fig 1 caption: clarify panels",
        "panels (A) ingestion",
        "panels (A) ingestion",
        "four stages: (A) ingestion",
    )
    # Fig 8/Table 3 title: "Core sensitivity" → more descriptive
    fix(
        "Fig 8 caption: fix title",
        "Core sensitivity by acquisition plane",
        "Core sensitivity by acquisition plane (BRISC, DeiT-Small, Method A): axial (N = 15), coronal (N = 15) and sagittal (N = 15).",
        "Regional sensitivity by acquisition plane (BRISC, DeiT-Small, Method A — tumour-core region shown): axial (N = 15), coronal (N = 15) and sagittal (N = 15).",
    )
    fix(
        "Table 3 title: fix 'Core sensitivity' → multi-region",
        "Core sensitivity by acquisition plane (BRISC, DeiT-Small, Method A).",
        "Core sensitivity by acquisition plane (BRISC, DeiT-Small, Method A).",
        "Regional sensitivity by acquisition plane — tumour-core region (BRISC, DeiT-Small, Method A).",
    )

    # =========================================================================
    # 36. Sec 6.2 (P153) — also fix "0.0239 on BRISC" if Holm value wrong there
    # =========================================================================
    # From S1: BRISC DeiT Immediate Method A: raw_p=0.0152, Holm=0.3643 (rank 2/4 in 32-test)
    # Condition-level (4-region): rank depends on condition sort
    # The raw_p=0.0152 and condition Holm = 0.0455 (rank 3/4 × multiplier)
    # The paragraph says "raw p = 0.0094; Holm-adjusted p = 0.0188" — fix already handled above

    # =========================================================================
    # 37. ResNet core concordance r=0.089 — add to main text if missing
    # =========================================================================
    idx_concord = find_para_containing(paras, "Perturbation method concordance")
    if idx_concord is not None:
        # Look at next few paragraphs for concordance r values
        for ci in range(idx_concord, min(idx_concord + 10, len(paras))):
            t_c = para_text(paras[ci])
            if "r = 0.748" in t_c or "r = 0.300" in t_c:
                if "ResNet core r = 0.089" not in t_c and "r = 0.0893" not in t_c:
                    # Append ResNet core concordance note
                    new_tc = t_c.rstrip()
                    if not new_tc.endswith("."):
                        new_tc += "."
                    new_tc += (
                        " ResNet-50 showed weak core concordance (r = 0.089, p = 0.40), "
                        "indicating that Method A and Method B core estimates are "
                        "not reliably correlated for this architecture."
                    )
                    set_para_text(paras[ci], new_tc)
                    print("  [OK]   Sec 5.5: Added ResNet core r=0.089 to main text")
                    fixes_applied.append("Sec 5.5: ResNet core r=0.089 added")
                break

    return fixes_applied


def main():
    print("=" * 70)
    print("apply_reviewer_fixes.py — Brain MRI Manuscript Reviewer Fix Script")
    print("=" * 70)

    if not UPLOADED.exists():
        print(f"ERROR: Uploaded DOCX not found at {UPLOADED}")
        sys.exit(1)

    print(f"\nLoading: {UPLOADED.name}")
    doc = Document(str(UPLOADED))
    print(f"  Paragraphs: {len(doc.paragraphs)}  Tables: {len(doc.tables)}")

    print("\nApplying fixes …")
    fixes = apply_fixes(doc)

    print(f"\n{len(fixes)} fixes applied.")

    print(f"\nSaving to: {OUT_PATH}")
    doc.save(str(OUT_PATH))
    print("  Saved OK.")

    # Copy to artifact directory
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(OUT_PATH), str(ARTIFACT))
    print(f"  Copied to artifact dir: {ARTIFACT.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
