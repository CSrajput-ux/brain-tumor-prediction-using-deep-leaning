# Research correction log — 2026-10-22

## Proposed corrections on branch `research-audit-corrections-2026-10-22`

### Applied
1. Removed the unsupported attribution of a greater-than-40-percentage-point tile-scrambling Macro-F1 drop to Vangala et al. (arXiv:2610.00421). The preprint is a benchmark-contamination audit and does not report the spatial tile-scrambling experiment examined in this project.
2. Corrected `scripts/run_dual_resolution_diagnostics.py` so C2 generation follows the evaluated Phase 9 operator: 9×9 Gaussian blur, sigma 2.5, and distance-weighted blend max(0, 1 - D/4).
3. Withdrew stale C2 seam/Spectral attenuation percentages from the manuscript and figure caption. The canonical diagnostics CSV now marks the C2 row pending instead of preserving numbers computed with the wrong operator.
4. Corrected the gain-1.8 true-seam statistic in the manuscript/evidence tables: Macro-F1 is 0.7811 in S0 (delta +0.1522, 95% CI [0.1182, 0.1904]), 0.8341 in S1, and 0.8580 in S2. The `_w3` suffix is a legacy identifier; the high-gain condition modifies the same two boundary-adjacent pixels as the gain-1.0 control.
5. Updated the reproducibility checklist to mark the C2 diagnostic rerun pending.

### Still required before submission
- Checkout this branch and run `python scripts/run_dual_resolution_diagnostics.py` against the full prepared dataset, then reconcile the new diagnostics CSV, publication Table 7, Figure 8 and manuscript. The prepared dataset was not available in this editing environment, so new diagnostic measurements have not been generated here.
- `remaining_work_audit/true_seam_oof_predictions.csv` is empty on the current default branch. Regenerate true-seam OOF predictions before rerunning `scripts/run_task5_cluster_bootstrap.py`; configuration alone is not proof of a successful run.
- Preserve acquisition plane as an unresolved dataset limitation unless reliable plane metadata or a pre-specified expert-annotation protocol is available.
- Verify every reference/DOI and confirm author contributions, ethics/funding declarations, journal choice and review policy with the human authors.
- Keep the DOCX as a corrected working draft; do not mark the paper final until diagnostics and bootstrap outputs are rerun and reconciled.
