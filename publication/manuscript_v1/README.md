# Publication Package: Brain MRI Spatial Disentanglement Study

This directory contains the complete scientific manuscript, publication figures, data tables, and reproducibility artifacts for:

> **Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Study**

---

## Directory Contents

- `manuscript.md`: Complete scientific paper in Markdown format.
- `manuscript.docx`: Formatted, editable Microsoft Word manuscript.
- `abstract.md`: Standalone abstract with keywords.
- `figure_captions.md`: Detailed captions for all 10 publication figures.
- `tables/`: Publication-ready tables in CSV format.
  - `table1_dataset_composition.csv`: Dataset slice counts and clinical anatomical predilections.
  - `table2_evaluation_scenarios.csv`: Cross-validation scenarios ($S_0, S_1, S_2$) and fold partitions.
  - `table3_model_configuration.csv`: ResNet-50 hyperparameters and training configuration.
  - `table4_baseline_metrics.csv`: Out-of-fold performance under original baseline ($C_0$).
  - `table5_intervention_metrics.csv`: Classification metrics across $C_0, C_1, C_2, C_3$.
  - `table6_canonical_contrasts.csv`: Paired contrasts, 95% bootstrap CIs, fold std, McNemar $\chi^2$, and Holm FWER status.
  - `table7_image_diagnostics.csv`: Sobel gradient and Fourier spectral diagnostics.
  - `table8_claim_evidence_matrix.csv`: Claim-evidence matrix and epistemic bounds.
  - `table_s1_prediction_accounting.csv`: Checkpoint-to-prediction verification table.
- `figures/`: High-resolution figures in PNG (300 DPI) and vector PDF format:
  - `fig1_dataset_and_masks.{png,pdf}`: Genuine dataset slices and tumour/margin overlays.
  - `fig2_experimental_workflow.{png,pdf}`: Complete end-to-end experimental workflow diagram.
  - `fig3_intervention_geometry.{png,pdf}`: 4-condition intervention geometry on genuine patient slices.
  - `fig4_baseline_performance.{png,pdf}`: Baseline performance comparison across scenarios.
  - `fig5_intervention_macro_f1.{png,pdf}`: Multi-condition performance comparison across scenarios.
  - `fig6_contrast_forest_plot.{png,pdf}`: Forest plot of paired statistical contrasts with bootstrap CIs.
  - `fig7_confusion_matrices.{png,pdf}`: Confusion matrices across conditions in Scenario $S_0$.
  - `fig8_artifact_diagnostics.{png,pdf}`: Seam energy, interior texture, and Fourier high-frequency energy.
  - `fig9_glioma_prior_collapse.{png,pdf}`: Mechanistic glioma-to-pituitary flip rate dynamics.
  - `fig10_cross_validation_stability.{png,pdf}`: Fold-level cross-validation stability of $C_2 \text{ vs } C_0$.
- `figure_source/`:
  - `generate_figures_and_tables.py`: Standalone script to reproduce all figures and tables from raw data.
- `supplementary_methods.md`: Full mathematical definitions of $C_0, C_1, C_2, C_3$, structuring elements, and cluster bootstrap.
- `supplementary_results.md`: Per-fold checkpoint breakdown and complete confusion matrix transitions.
- `references.bib`: BibTeX bibliography file with complete DOIs.
- `reference_verification.csv`: Audit verification table for all cited references.
- `claim_evidence_matrix.csv`: Full claim-evidence matrix.
- `reproducibility_checklist.md`: Comprehensive reproducibility checklist.
- `missing_evidence_and_author_questions.md`: Log of missing evidence and author decisions required prior to submission.
- `manuscript_quality_audit.md`: Audit report verifying numerical consistency and epistemic claim boundaries.

---

## Regeneration Instructions

To regenerate all figures and tables from source artifacts, run:
```bash
python publication/manuscript_v1/figure_source/generate_figures_and_tables.py
```

To run the automated regression test suite:
```bash
pytest tests/ -v
```
