"""Manifest-driven BRISC ingestion; files outside the official manifest are ignored."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator


CLASS_IDS = {"glioma": 0, "meningioma": 1, "pituitary": 2, "no_tumor": 3}


def read_brisc_records(root: Path) -> Iterator[dict]:
    """Yield classification records paired to segmentation masks by manifest filename.

    A missing segmentation pair is represented explicitly; no filename-only pairing
    outside of the release manifest is performed.
    """
    manifest = root / "manifest.csv"
    with manifest.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    segmentation_images = {
        row["filename"]: row
        for row in rows
        if row["task"] == "segmentation" and row["is_mask"] == "False"
    }
    segmentation_masks = {
        row["filename"]: row
        for row in rows
        if row["task"] == "segmentation" and row["is_mask"] == "True"
    }
    for row in rows:
        if row["task"] != "classification" or row["is_mask"] != "False":
            continue
        filename = row["filename"]
        image_path = root / row["relative_path"]
        seg_image = segmentation_images.get(filename)
        mask_name = Path(filename).with_suffix(".png").name
        mask_row = segmentation_masks.get(mask_name)
        mask_path = root / mask_row["relative_path"] if mask_row else None
        label = row["tumor_label"]
        yield {
            "dataset": "brisc",
            "sample_id": filename.rsplit(".", 1)[0],
            "relative_image_path": row["relative_path"],
            "relative_mask_path": mask_row["relative_path"] if mask_row else "",
            "official_split": row["split"],
            "class_label": label,
            "class_id": CLASS_IDS[label],
            "patient_id": "",  # no patient identifier is supplied by this release manifest
            "plane": row["plane_label"],
            "declared_image_width": row["width"],
            "declared_image_height": row["height"],
            "mask_available": bool(mask_row),
            "mask_pair_status": (
                "not_applicable_no_tumor" if label == "no_tumor" else
                "paired" if mask_row and seg_image else "missing_or_incomplete_pair"
            ),
            "source_sha256": row["sha256"],
            "image_path": image_path,
            "mask_path": mask_path,
        }


class BriscDataset:
    """PyTorch Dataset for BRISC 2025 brain tumor MRI slices."""
    def __init__(
        self,
        manifest_path: Path | None = None,
        brisc_root: Path | None = None,
        split: str | list[str] | None = None,
        clean_only: bool = False,
        mask_required: bool = False,
        target_size: tuple[int, int] = (224, 224),
        is_training: bool = False,
        normalize_imagenet: bool = True,
        seed: int = 42,
    ):
        import csv
        import numpy as np
        from PIL import Image

        self.root = brisc_root or Path(__file__).resolve().parents[2] / "brisc" / "brisc2025"
        manifest_file = manifest_path or Path(__file__).resolve().parents[2] / "manifests" / "brisc_manifest.csv"
        with manifest_file.open("r", encoding="utf-8") as f:
            all_records = list(csv.DictReader(f))

        filtered = all_records
        if split is not None:
            splits_set = {split} if isinstance(split, str) else set(split)
            filtered = [r for r in filtered if r["official_split"] in splits_set]
        if clean_only:
            filtered = [r for r in filtered if not r.get("exclusion_reason")]
        if mask_required:
            filtered = [r for r in filtered if r.get("mask_available") == "True"]

        self.records = filtered
        self.target_size = target_size
        self.is_training = is_training
        self.normalize_imagenet = normalize_imagenet
        self.rng = np.random.default_rng(seed)

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        import torch
        import numpy as np
        from PIL import Image
        from src.data.preprocessing import preprocess_sample

        record = self.records[idx]
        img_path = self.root / record["relative_image_path"]
        with Image.open(img_path) as img:
            raw_image = np.asarray(img.convert("L"), dtype=np.float32)

        raw_mask = None
        if record.get("mask_available") == "True" and record.get("relative_mask_path"):
            mask_path = self.root / record["relative_mask_path"]
            if mask_path.exists():
                with Image.open(mask_path) as m_img:
                    raw_mask = (np.asarray(m_img.convert("L")) > 0).astype(np.uint8)

        model_tensor, binary_mask, display_img, meta = preprocess_sample(
            raw_image,
            raw_mask,
            target_size=self.target_size,
            is_training=self.is_training,
            normalize_imagenet=self.normalize_imagenet,
            rng=self.rng,
        )

        return {
            "image": torch.from_numpy(model_tensor),
            "mask": torch.from_numpy(binary_mask) if binary_mask is not None else torch.zeros(self.target_size, dtype=torch.uint8),
            "display_image": torch.from_numpy(display_img),
            "label": int(record["class_id"]),
            "sample_id": record["sample_id"],
            "plane": record["plane"],
            "class_label": record["class_label"],
            "official_split": record["official_split"],
            "has_mask": binary_mask is not None,
            "metadata": meta,
        }

