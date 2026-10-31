"""Synchronize paper/manuscript.md and Brain_MRI_Research_Paper_Final.md with all Pass 3 scientific qualifications."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

for fname in ["paper/manuscript.md", "Brain_MRI_Research_Paper_Final.md"]:
    p = ROOT / fname
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")

    # 1. Abstract Class Ratios
    old_abs_class = "Exploratory radiologic analysis showed that gliomas exhibited a substantial margin-to-core sensitivity ratio (35.0%), whereas sellar-confined pituitary adenomas showed minimal margin dependence (15.1%)."
    new_abs_class = "Exploratory radiologic analysis showed that gliomas exhibited a substantial immediate-margin-to-core sensitivity ratio (67.2%; $\\tau_{\\text{immed}} = 0.0268$ vs $\\tau_{\\text{core}} = 0.0398$), meningiomas exhibited pronounced core reliance ($\\tau_{\\text{core}} = 0.3438$ vs $\\tau_{\\text{immed}} = 0.0338$; ratio 9.8%), and pituitary adenomas showed minimal immediate margin dependence ($\\tau_{\\text{immed}} = 0.0034$ vs $\\tau_{\\text{core}} = 0.0009$; outer margin $\\tau_{\\text{outer}} = 0.0392$, ratio 360.2%)."
    text = text.replace(old_abs_class, new_abs_class)

    # 2. Abstract 55 clusters qualification
    old_abs_55 = "cluster-level Wilcoxon $W = 483.0, p = 0.0162$, paired t-test $t(54) = 3.29, p = 0.00177$ across 55 independent patient/case clusters"
    new_abs_55 = "cluster-level Wilcoxon $W = 483.0, p = 0.0162$, paired t-test $t(54) = 3.29, p = 0.00177$ across 55 evaluation clusters comprising 10 verified Cheng patient clusters and 45 BRISC image-level sample clusters (patient-level linkage was unavailable for BRISC)"
    text = text.replace(old_abs_55, new_abs_55)

    # 3. Section 3.3 Cross-Dataset Independence qualification
    old_s33 = "confirm that Cheng and BRISC represent completely independent clinical cohorts"
    new_s33 = "demonstrate that Cheng and BRISC contain zero identical 2D slices. However, the absence of exact image duplicates does not formally exclude latent patient overlap or shared multi-center referral sources between the archives, as individual patient linkage was not released for BRISC (Fateh et al. [5])"
    text = text.replace(old_s33, new_s33)

    # 4. Section 3.6 Sham Geometry Outlier Disclosure
    old_s36 = "yielding an overall mean sham-to-core area ratio of 0.9975 +/- 0.0227 and mean template Dice overlap of 0.9986 +/- 0.0130."
    new_s36 = """yielding an overall mean sham-to-core area ratio of 0.9975 +/- 0.0227 and mean template Dice overlap of 0.9986 +/- 0.0130. Among the 5 clipped slices, one marked outlier occurred in a peripheral cortical lesion abutting the inner calvarium (`brisc2025_test_00003_gl_ax_t1`), where boundary masking against normal brain parenchyma produced an area ratio of 0.7525 (24.75% area reduction) and template Dice of 0.8588. Sensitivity re-analysis excluding this outlier confirmed that BRISC DeiT core sensitivity (\\tau = 0.0528, p = 0.0313) and pooled architectural differences (+0.0746, p = 0.0118) remain completely stable."""
    text = text.replace(old_s36, new_s36)

    # 5. Section 5.4 Architecture comparison exploratory qualification & 55 clusters wording
    old_s54 = "Crucially, under cluster-level inference accounting for the 55 independent clusters (10 Cheng patient clusters + 45 independent BRISC cases; potential scanner/source lineage overlap per Fateh et al. 2026), the architectural superiority remains robust: cluster-level Wilcoxon **$W = 483.0$, two-sided $p = 0.0162$**, cluster-level paired t-test **$t(54) = 3.29, p = 0.00177$**, and Linear Mixed-Effects Modeling fixed effect $\\beta_{\\text{ViT}} = +0.074$ (SE = 0.020, Wald $z = 3.756$, $p < 0.001$). In the Cheng-specific subset ($N=45$), the core sensitivity difference was $0.1282 - 0.0311 = +0.0971$ (slice-level Wilcoxon $p = 0.156$; patient-clustered Wilcoxon $p = 0.232$, clustered t-test $p = 0.148$). Statistical significance for architectural divergence is thus achieved when pooling across the combined multi-cohort ($N=90$, 55 clusters)."
    new_s54 = """The pooled analysis comprised 10 verified Cheng patient-level clusters and 45 BRISC image-level sample clusters. Patient-level linkage within BRISC was unavailable; therefore, the BRISC units should not be interpreted as 45 independently verified patients. Across these 55 units, cluster-level inference showed cluster Wilcoxon **$W = 483.0$, two-sided $p = 0.0162$**, paired t-test **$t(54) = 3.29, p = 0.00177$**, and Linear Mixed-Effects Modeling fixed effect $\\beta_{\\text{ViT}} = +0.074$ (SE = 0.020, Wald $z = 3.756$, $p < 0.001$). In a cohort-interaction sensitivity model (`tau ~ is_vit * is_brisc + (1|cluster_id)`), the interaction term was not statistically significant ($\\beta = -0.047$, SE = 0.039, $z = -1.191, p = 0.234$), confirming consistent directionality. However, this architectural divergence represents an exploratory finding: after 8-test step-down Holm-Bonferroni adjustment across regions and methods, the slice-level pooled adjusted p-value was $p_{\\text{adj}} = 0.0980$, and the difference did not achieve statistical significance within the smaller Cheng-only partition ($p = 0.156$)."""
    text = text.replace(old_s54, new_s54)

    # 6. Section 6.2 Biological causation claim softening
    old_s62 = "These margin effects directly correspond to histopathological infiltrative tumour margins and perilesional edema biology."
    new_s62 = "These transitional margin effects reflect the sensitivity of trained 2D neural networks to boundary contrast enhancement and surrounding edema patterns, and must not be conflated with histopathological tumour cell infiltration or in vivo biological causation without tissue biopsy correlation."
    text = text.replace(old_s62, new_s62)

    p.write_text(text, encoding="utf-8")
    print(f"Synchronized Pass 3 fixes to {fname}")
