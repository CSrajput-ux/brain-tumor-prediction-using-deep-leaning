"""Synchronize paper/manuscript.md and Brain_MRI_Research_Paper_Final.md with all reviewer findings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

for fname in ["paper/manuscript.md", "Brain_MRI_Research_Paper_Final.md"]:
    p = ROOT / fname
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")

    # Abstract Cheng Holm p-values & Wilcoxon
    text = text.replace(
        "Holm-adjusted $p = 2.74 \\times 10^{-5}$, patient-clustered Wilcoxon $p = 0.0488$, $d_z = 0.518$)",
        "Holm-adjusted $p = 3.65 \\times 10^{-5}$, patient-clustered Wilcoxon $W = 8.0, p = 0.0488$ [one-sided $W = 47.0, p = 0.0244$], $d_z = 0.518$)"
    )
    text = text.replace(
        "Holm-adjusted $p = 1.96 \\times 10^{-3}$, patient-clustered $p = 0.0488$, $d_z = 0.548$)",
        "Holm-adjusted $p = 2.62 \\times 10^{-3}$, patient-clustered Wilcoxon $W = 8.0, p = 0.0488$ [one-sided $W = 47.0, p = 0.0244$], $d_z = 0.548$)"
    )

    # Abstract BRISC DeiT Core p-value transparent disclosure
    text = text.replace(
        "On BRISC ($N=45$), DeiT-Small demonstrated $\\tau_{\\text{core}} = 0.0517 \\pm 0.120$ (raw drop $0.0367 \\pm 0.096$, Wilcoxon $p = 0.0320$, $d_z = 0.432$) under inpainting.",
        "On BRISC ($N=45$), DeiT-Small demonstrated $\\tau_{\\text{core}} = 0.0517 \\pm 0.120$ (raw drop $0.0367 \\pm 0.096$, raw Wilcoxon $p = 0.0320$, 4-region Holm-adjusted $p = 0.0639$, 32-test family Holm-adjusted $p = 0.6072$, $d_z = 0.432$; non-significant after Holm adjustment) under inpainting."
    )

    # Abstract 55 clusters clarification
    text = text.replace(
        "cluster-level Wilcoxon $p = 0.0162$ across 55 independent patient/case clusters",
        "cluster-level Wilcoxon $W = 483.0, p = 0.0162$, paired t-test $t(54) = 3.29, p = 0.00177$ across 55 independent patient/case clusters"
    )

    # Table 2 updates
    text = text.replace(
        "| **Cheng ($N=45$)** | DeiT-Small | Method A (Telea) | **Core** | $0.1212 \\pm 0.244$ | **$0.1282 \\pm 0.248$** | 13.3% | **$9.13 \\times 10^{-6}$** | **$2.74 \\times 10^{-5}$** | **0.518** |",
        "| **Cheng ($N=45$)** | DeiT-Small | Method A (Telea) | **Core** | $0.1212 \\pm 0.244$ | **$0.1282 \\pm 0.248$** | 13.3% | **$9.13 \\times 10^{-6}$** | **$3.65 \\times 10^{-5}$** | **0.518** |"
    )
    text = text.replace(
        "| **Cheng ($N=45$)** | ResNet-50 | Method A (Telea) | **Core** | $0.0264 \\pm 0.041$ | **$0.0311 \\pm 0.057$** | 8.9% | **$6.54 \\times 10^{-4}$** | **$1.96 \\times 10^{-3}$** | **0.548** |",
        "| **Cheng ($N=45$)** | ResNet-50 | Method A (Telea) | **Core** | $0.0264 \\pm 0.041$ | **$0.0311 \\pm 0.057$** | 8.9% | **$6.54 \\times 10^{-4}$** | **$2.62 \\times 10^{-3}$** | **0.548** |"
    )
    text = text.replace(
        "| **BRISC ($N=45$)** | DeiT-Small | Method A (Telea) | **Core** | $0.0367 \\pm 0.096$ | **$0.0517 \\pm 0.120$** | 8.9% | **0.0320** | 0.0639 | **0.432** |",
        "| **BRISC ($N=45$)** | DeiT-Small | Method A (Telea) | **Core** | $0.0367 \\pm 0.096$ | **$0.0517 \\pm 0.120$** | 8.9% | **0.0320** | 0.0639* | **0.432** |"
    )

    # Footnote under Table 2
    old_t2_post = "1. **Core Evidence Dominance vs Method Dependency:**"
    new_t2_post = """*Note on Multiplicity Control: Primary Table 2 reports step-down Holm-Bonferroni correction within each 4-region hypothesis family (Core, Immediate, Outer, Remote). In BRISC DeiT Method A, Core is Rank 3 (multiplier 2), yielding p_adj = 0.0639. Under the complete 32-test study-wide family (Table S1), BRISC DeiT Core yields p_adj = 0.6072. Both multiplicity strategies confirm that this BRISC Core result is not statistically significant at alpha = 0.05.

1. **Core Evidence Dominance vs Method Dependency:**"""
    if "*Note on Multiplicity Control:" not in text:
        text = text.replace(old_t2_post, new_t2_post, 1)

    # Section 5.3 patient clustering
    old_clust = "patient-clustered analysis across the 10 patient-mean sensitivities yields clustered Wilcoxon **$p = 0.0488$** for both architectures (clustered one-sample t-test: DeiT $p = 0.0534$, ResNet $p = 0.0771$)."
    new_clust = "patient-clustered analysis across the 10 patient-mean sensitivities yields clustered Wilcoxon **$W = 8.0$, two-sided $p = 0.0488$** (one-sided $W = 47.0, p = 0.0244$) for both architectures (clustered one-sample t-test: DeiT $t = 2.22, p = 0.0534$, ResNet $t = 2.00, p = 0.0771$)."
    text = text.replace(old_clust, new_clust)

    # Section 5.4 cluster inference details
    old_s54 = "cluster-level Wilcoxon **$p = 0.0162$**, cluster-level t-test **$p = 0.00177$**, and Linear Mixed-Effects Modeling fixed effect $\\beta_{\\text{ViT}} = +0.074$ ($z = 3.756$, $p < 0.001$)."
    new_s54 = "cluster-level Wilcoxon **$W = 483.0$, two-sided $p = 0.0162$**, cluster-level paired t-test **$t(54) = 3.29, p = 0.00177$**, and Linear Mixed-Effects Modeling fixed effect $\\beta_{\\text{ViT}} = +0.074$ (SE = 0.020, Wald $z = 3.756$, $p < 0.001$)."
    text = text.replace(old_s54, new_s54)

    # References update
    text = text.replace(
        "3. Rossi, F., Lopez, R. and Comminiello, D. (2024). TACE: Tumor-Aware Counterfactual Explanations for Medical Image Analysis. *arXiv preprint*, arXiv:2409.13045. doi:10.48550/arXiv.2409.13045.",
        "3. Rossi, E.B., Lopez, E. and Comminiello, D. (2024). TACE: Tumor-aware counterfactual explanations for medical image analysis. *arXiv preprint*, arXiv:2409.13045. doi:10.48550/arXiv.2409.13045."
    )
    text = text.replace(
        "4. Sourget, T., Pizurica, A. et al. (2025). Mask of Truth: Model Sensitivity to Unexpected Regions of Medical Images. *Journal of Imaging Informatics in Medicine*, doi:10.1007/s10278-025-01531-5.",
        "4. Sourget, T., Hestbek-Møller, M., Jiménez-Sánchez, A., Xu, J.J. and Cheplygina, V. (2025). Mask of truth: model sensitivity to unexpected regions of medical images. *Journal of Imaging Informatics in Medicine*, doi:10.1007/s10278-025-01531-5."
    )
    text = text.replace(
        "5. Fateh, A. et al. (2026). BRISC: Annotated Dataset for Brain Tumor Segmentation and Classification. *Scientific Data*, 13, p.412. doi:10.1038/s41597-026-06753-y.",
        "5. Fateh, A. et al. (2026). BRISC: annotated dataset for brain tumor segmentation and classification. *Scientific Data*, 13, 361. doi:10.1038/s41597-026-06753-y."
    )
    # Remove Bentaieb reference 15
    text = text.replace(
        "\n15. Bentaieb, A. and Hamarneh, G. (2016). Topology Preserving Deep Networks for Medical Image Analysis. *MICCAI*, pp.437–445. doi:10.1007/978-3-319-46723-8_51.",
        ""
    )

    p.write_text(text, encoding="utf-8")
    print(f"Successfully synchronized {fname}")

