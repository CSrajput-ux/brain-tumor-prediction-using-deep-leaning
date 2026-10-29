"""End-to-end intervention generation and evaluation pipeline."""
from __future__ import annotations

from typing import Any
import numpy as np

from src.interventions.inpainting import fill_region_matched_texture, inpaint_region_telea
from src.interventions.quality_metrics import compute_intervention_quality
from src.interventions.regions import generate_regions


def process_sample_interventions(
    image: np.ndarray,
    mask: np.ndarray,
    sample_id: str,
    dataset_name: str,
    class_label: str,
    seed: int = 42,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]]]:
    """Generate all region-specific counterfactual interventions and compute QC metrics."""
    regions = generate_regions(mask, image)
    tissue = regions["tissue_mask"]

    target_regions = ["core", "immediate", "outer", "remote", "sham"]
    edited_images: dict[str, np.ndarray] = {"original": image}
    qc_records: list[dict[str, Any]] = []

    for reg_name in target_regions:
        reg_mask = regions[reg_name]

        # Method A: Telea inpainting
        edit_a = inpaint_region_telea(image, reg_mask, inpaint_radius=3, method="telea")
        qc_a = compute_intervention_quality(image, edit_a, reg_mask)
        edited_images[f"{reg_name}_method_a"] = edit_a
        qc_records.append({
            "sample_id": sample_id,
            "dataset": dataset_name,
            "class_label": class_label,
            "region": reg_name,
            "method": "telea_inpaint",
            "mask_pixels": qc_a["mask_pixels"],
            "max_diff_outside": qc_a["max_diff_outside"],
            "mean_diff_outside": qc_a["mean_diff_outside"],
            "mad_inside": qc_a["mad_inside"],
            "rmsd_inside": qc_a["rmsd_inside"],
            "intensity_shift": qc_a["intensity_shift"],
            "boundary_discontinuity": qc_a["boundary_discontinuity_index"],
            "passed_qc": qc_a["passed_qc"],
        })

        # Method B: Locally matched texture fill
        edit_b = fill_region_matched_texture(image, reg_mask, tissue_mask=tissue, feather_radius=2, seed=seed)
        qc_b = compute_intervention_quality(image, edit_b, reg_mask)
        edited_images[f"{reg_name}_method_b"] = edit_b
        qc_records.append({
            "sample_id": sample_id,
            "dataset": dataset_name,
            "class_label": class_label,
            "region": reg_name,
            "method": "matched_texture_fill",
            "mask_pixels": qc_b["mask_pixels"],
            "max_diff_outside": qc_b["max_diff_outside"],
            "mean_diff_outside": qc_b["mean_diff_outside"],
            "mad_inside": qc_b["mad_inside"],
            "rmsd_inside": qc_b["rmsd_inside"],
            "intensity_shift": qc_b["intensity_shift"],
            "boundary_discontinuity": qc_b["boundary_discontinuity_index"],
            "passed_qc": qc_b["passed_qc"],
        })

    return edited_images, qc_records

