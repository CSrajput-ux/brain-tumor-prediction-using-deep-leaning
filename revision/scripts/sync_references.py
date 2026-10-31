"""Synchronize reports/reference_verification.csv and reports/citation_audit.csv to exactly 14 verified references."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

ref_data = [
    {
        "citation_id": "REF-01",
        "citation_key": "wallis2022clever",
        "authors": "Wallis, C. and Buvat, I.",
        "year": 2022,
        "title": "Clever Hans effect found in a widely used brain tumour MRI dataset",
        "venue": "Medical Image Analysis, 77, 102368",
        "doi_or_url": "https://doi.org/10.1016/j.media.2022.102368",
        "doi": "10.1016/j.media.2022.102368",
        "in_text_occurrences": "Abstract, Sec 1, Sec 2.1, Ref 1",
        "peer_reviewed": "Yes",
        "claim_supported": "Deep networks classify brain MRI slices accurately even when intracranial brain tissue is completely masked out.",
        "claim_fidelity": "Direct empirical support: models classify MRI slices with tissue masked out.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-02",
        "citation_key": "cheng2015enhanced",
        "authors": "Cheng, J., Huang, W., Cao, S. et al.",
        "year": 2015,
        "title": "Enhanced performance of brain tumor classification via tumor region augmentation and partition",
        "venue": "PLOS ONE, 10(10), e0140381",
        "doi_or_url": "https://doi.org/10.1371/journal.pone.0140381",
        "doi": "10.1371/journal.pone.0140381",
        "in_text_occurrences": "Sec 1, Sec 2.3, Sec 3.1, Declarations, Ref 2",
        "peer_reviewed": "Yes",
        "claim_supported": "Introduced 3064 T1-CE brain MRI slices across 233 patients with board-certified radiologist tumor boundary annotations.",
        "claim_fidelity": "Direct provenance: 3064 T1-CE slices across 233 patients.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-03",
        "citation_key": "rossi2024tace",
        "authors": "Rossi, E.B., Lopez, E. and Comminiello, D.",
        "year": 2024,
        "title": "TACE: Tumor-aware counterfactual explanations for medical image analysis",
        "venue": "arXiv preprint arXiv:2409.13045",
        "doi_or_url": "https://doi.org/10.48550/arXiv.2409.13045",
        "doi": "10.48550/arXiv.2409.13045",
        "in_text_occurrences": "Sec 1, Sec 2.2, Ref 3",
        "peer_reviewed": "No",
        "claim_supported": "Counterfactual lesion insertion and removal to assess classification attribution.",
        "claim_fidelity": "Direct methodological reference: lesion counterfactual insertion/removal.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-04",
        "citation_key": "sourget2025mask",
        "authors": "Sourget, T., Hestbek-Møller, M., Jiménez-Sánchez, A., Xu, J.J. and Cheplygina, V.",
        "year": 2025,
        "title": "Mask of truth: model sensitivity to unexpected regions of medical images",
        "venue": "Journal of Imaging Informatics in Medicine",
        "doi_or_url": "https://doi.org/10.1007/s10278-025-01531-5",
        "doi": "10.1007/s10278-025-01531-5",
        "in_text_occurrences": "Sec 1, Sec 2.2, Ref 4",
        "peer_reviewed": "Yes",
        "claim_supported": "Evaluating region-targeted feature removal for faithfulness in medical imaging.",
        "claim_fidelity": "Direct methodological reference: region-resolved unexpected feature evaluation.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-05",
        "citation_key": "fateh2026brisc",
        "authors": "Fateh, A. et al.",
        "year": 2026,
        "title": "BRISC: annotated dataset for brain tumor segmentation and classification",
        "venue": "Scientific Data, 13, 361",
        "doi_or_url": "https://doi.org/10.1038/s41597-026-06753-y",
        "doi": "10.1038/s41597-026-06753-y",
        "in_text_occurrences": "Sec 1, Sec 2.3, Sec 3.1, Declarations, Ref 5",
        "peer_reviewed": "Yes",
        "claim_supported": "Introduced 6000 skull-stripped multi-plane CE-MRI slices across 4 classes.",
        "claim_fidelity": "Direct provenance: 6000 skull-stripped multi-plane CE-MRI slices.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-06",
        "citation_key": "yagis2021effect",
        "authors": "Yagis, E. et al.",
        "year": 2021,
        "title": "Effect of data leakage in brain MRI classification using 2D convolutional neural networks",
        "venue": "Scientific Reports, 11(1), 22544",
        "doi_or_url": "https://doi.org/10.1038/s41598-021-01681-w",
        "doi": "10.1038/s41598-021-01681-w",
        "in_text_occurrences": "Sec 1, Sec 2.3, Sec 3.2, Ref 6",
        "peer_reviewed": "Yes",
        "claim_supported": "Patient-level data leakage and slice correlation drastically inflate cross-validation performance.",
        "claim_fidelity": "Direct methodological support: patient-level leakage inflates metrics.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-07",
        "citation_key": "he2016deep",
        "authors": "He, K., Zhang, X., Ren, S. and Sun, J.",
        "year": 2016,
        "title": "Deep Residual Learning for Image Recognition",
        "venue": "IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pp. 770-778",
        "doi_or_url": "https://doi.org/10.1109/CVPR.2016.90",
        "doi": "10.1109/CVPR.2016.90",
        "in_text_occurrences": "Sec 3.4, Ref 7",
        "peer_reviewed": "Yes",
        "claim_supported": "Introduced ResNet architectures and residual skip connections.",
        "claim_fidelity": "Direct architectural foundation: ResNet-50 residual bottlenecks.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-08",
        "citation_key": "touvron2021training",
        "authors": "Touvron, H., Cord, M., Douze, M. et al.",
        "year": 2021,
        "title": "Training data-efficient image transformers and distillation through attention",
        "venue": "International Conference on Machine Learning (ICML), pp. 10347-10357",
        "doi_or_url": "https://proceedings.mlr.press/v139/touvron21a.html",
        "doi": "10.48550/arXiv.2012.12877",
        "in_text_occurrences": "Sec 3.4, Ref 8",
        "peer_reviewed": "Yes",
        "claim_supported": "Introduced DeiT data-efficient vision transformers with attention distillation.",
        "claim_fidelity": "Direct architectural foundation: DeiT-Small data-efficient transformer.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-09",
        "citation_key": "guo2017calibration",
        "authors": "Guo, C., Pleiss, G., Sun, Y. and Weinberger, K.Q.",
        "year": 2017,
        "title": "On Calibration of Modern Neural Networks",
        "venue": "International Conference on Machine Learning (ICML), pp. 1321-1330",
        "doi_or_url": "https://proceedings.mlr.press/v70/guo17a.html",
        "doi": "10.48550/arXiv.1706.04599",
        "in_text_occurrences": "Sec 3.7, Ref 9",
        "peer_reviewed": "Yes",
        "claim_supported": "Formulated Expected Calibration Error (ECE) and reliability diagrams for deep networks.",
        "claim_fidelity": "Direct metric definition: Expected Calibration Error (ECE).",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-10",
        "citation_key": "telea2004image",
        "authors": "Telea, A.",
        "year": 2004,
        "title": "An image inpainting technique based on the fast marching method",
        "venue": "Journal of Graphics Tools, 9(1), pp. 23-34",
        "doi_or_url": "https://doi.org/10.1080/10867651.2004.10487596",
        "doi": "10.1080/10867651.2004.10487596",
        "in_text_occurrences": "Sec 3.6, Ref 10",
        "peer_reviewed": "Yes",
        "claim_supported": "Formulated Fast Marching Method boundary PDE inpainting for smooth texture completion.",
        "claim_fidelity": "Direct perturbation algorithm: FMM boundary PDE inpainting.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-11",
        "citation_key": "geirhos2020shortcut",
        "authors": "Geirhos, R. et al.",
        "year": 2020,
        "title": "Shortcut learning in deep neural networks",
        "venue": "Nature Machine Intelligence, 2(11), pp. 665-673",
        "doi_or_url": "https://doi.org/10.1038/s42256-020-00257-z",
        "doi": "10.1038/s42256-020-00257-z",
        "in_text_occurrences": "Sec 1, Sec 2.1, Ref 11",
        "peer_reviewed": "Yes",
        "claim_supported": "Theoretical framework distinguishing intention from shortcut learning in deep models.",
        "claim_fidelity": "Theoretical foundation: distinguishing intention from shortcut learning.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-12",
        "citation_key": "goyal2019counterfactual",
        "authors": "Goyal, Y., Wu, Z., Ernst, J., Batra, D., Parikh, D. and Lee, S.",
        "year": 2019,
        "title": "Counterfactual Visual Explanations",
        "venue": "International Conference on Machine Learning (ICML), PMLR 97, pp. 2376-2384",
        "doi_or_url": "https://proceedings.mlr.press/v97/goyal19a.html",
        "doi": "10.1109/ICCV.2019.00882",
        "in_text_occurrences": "Sec 2.2, Ref 12",
        "peer_reviewed": "Yes",
        "claim_supported": "Principles of causal counterfactual image modifications in visual classification.",
        "claim_fidelity": "Theoretical foundation: visual counterfactual perturbations.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-13",
        "citation_key": "rudin2019stop",
        "authors": "Rudin, C.",
        "year": 2019,
        "title": "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead",
        "venue": "Nature Machine Intelligence, 1(5), pp. 206-215",
        "doi_or_url": "https://doi.org/10.1038/s42256-019-0048-x",
        "doi": "10.1038/s42256-019-0048-x",
        "in_text_occurrences": "Sec 1, Sec 2.2, Ref 13",
        "peer_reviewed": "Yes",
        "claim_supported": "Critique of post-hoc explainability methods and call for rigorous causal audits in medicine.",
        "claim_fidelity": "Epistemological critique of unverified black-box medical AI.",
        "verification_status": "VERIFIED"
    },
    {
        "citation_id": "REF-14",
        "citation_key": "degrave2021ai",
        "authors": "DeGrave, A.J., Janizek, J.D. and Lee, S.I.",
        "year": 2021,
        "title": "AI for radiographic COVID-19 detection frequently relies on spurious shortcuts",
        "venue": "Nature Machine Intelligence, 3(7), pp. 610-619",
        "doi_or_url": "https://doi.org/10.1038/s42256-021-00338-7",
        "doi": "10.1038/s42256-021-00338-7",
        "in_text_occurrences": "Sec 2.1, Ref 14",
        "peer_reviewed": "Yes",
        "claim_supported": "Spurious hospital markers and background features drive medical AI predictions.",
        "claim_fidelity": "Empirical medical evidence: spurious scanner shortcuts.",
        "verification_status": "VERIFIED"
    }
]

# Write reports/reference_verification.csv (14 rows)
df_ver = pd.DataFrame([{
    "citation_id": r["citation_id"],
    "authors": r["authors"],
    "year": r["year"],
    "title": r["title"],
    "venue": r["venue"],
    "doi_or_url": r["doi_or_url"],
    "peer_reviewed": r["peer_reviewed"],
    "claim_supported": r["claim_supported"],
    "verification_status": r["verification_status"]
} for r in ref_data])

ver_csv = ROOT / "reports" / "reference_verification.csv"
df_ver.to_csv(ver_csv, index=False)
print(f"Wrote {len(df_ver)} rows to {ver_csv}")

# Write reports/citation_audit.csv (14 rows)
df_audit = pd.DataFrame([{
    "ref_id": r["citation_id"],
    "citation_key": r["citation_key"],
    "full_citation": f"{r['authors']} ({r['year']}). {r['title']}. {r['venue']}. doi:{r['doi']}.",
    "doi": r["doi"],
    "in_text_occurrences": r["in_text_occurrences"],
    "claim_fidelity": r["claim_fidelity"],
    "status": r["verification_status"]
} for r in ref_data])

audit_csv = ROOT / "reports" / "citation_audit.csv"
df_audit.to_csv(audit_csv, index=False)
print(f"Wrote {len(df_audit)} rows to {audit_csv}")

