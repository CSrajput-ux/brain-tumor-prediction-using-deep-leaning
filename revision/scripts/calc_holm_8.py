import pandas as pd
import numpy as np
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests

df = pd.read_csv("predictions/intervention_effects.csv")
tests = []
for method in ["telea_inpaint", "matched_texture_fill"]:
    for reg in ["core", "immediate", "outer", "remote"]:
        sub_cnn = df[(df["architecture"] == "resnet50") & (df["method"] == method) & (df["region"] == reg)]
        sub_vit = df[(df["architecture"] == "deit_small_patch16_224") & (df["method"] == method) & (df["region"] == reg)]
        merged = pd.merge(sub_cnn, sub_vit, on=["sample_id", "dataset"], suffixes=("_cnn", "_vit"))
        diff = merged["tau_sham_corrected_vit"].values - merged["tau_sham_corrected_cnn"].values
        w = stats.wilcoxon(diff, alternative="two-sided")
        tests.append({
            "method": method,
            "region": reg,
            "tau_cnn_mean": float(np.mean(merged["tau_sham_corrected_cnn"].values)),
            "tau_cnn_std": float(np.std(merged["tau_sham_corrected_cnn"].values, ddof=1)),
            "tau_vit_mean": float(np.mean(merged["tau_sham_corrected_vit"].values)),
            "tau_vit_std": float(np.std(merged["tau_sham_corrected_vit"].values, ddof=1)),
            "diff_mean": float(np.mean(diff)),
            "diff_std": float(np.std(diff, ddof=1)),
            "pval": float(w.pvalue),
            "dz": float(np.mean(diff) / np.std(diff, ddof=1))
        })

pvals = [t["pval"] for t in tests]
reject, pvals_holm, _, _ = multipletests(pvals, method="holm")
for t, ph in zip(tests, pvals_holm):
    t["p_holm"] = float(ph)
    print(f"{t['method']:20s} {t['region']:10s} | diff={t['diff_mean']:+.4f} | raw_p={t['pval']:.4f} | holm_p={t['p_holm']:.4f} | dz={t['dz']:.3f}")
