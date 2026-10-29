"""Build auditable Cheng and BRISC indices without copying or renaming raw data."""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.brisc_dataset import read_brisc_records
from src.data.cheng_dataset import cheng_record

FIELDS = [
    "dataset", "sample_id", "relative_image_path", "relative_mask_path",
    "official_split", "class_label", "class_id", "patient_id", "plane",
    "image_width", "image_height", "mask_width", "mask_height", "mask_available",
    "mask_area_pixels", "image_sha256", "decoded_pixel_hash", "perceptual_hash",
    "duplicate_group", "quality_flags", "exclusion_reason", "available_fields",
    "mask_pair_status",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def array_hash(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    return hashlib.sha256(arr.tobytes()).hexdigest()


def phash(image: Image.Image) -> str:
    """Dependency-free average perceptual hash, only a candidate-discovery signal."""
    arr = np.asarray(image.convert("L").resize((8, 8), Image.Resampling.LANCZOS), dtype=np.float32)
    bits = arr >= arr.mean()
    return f"{int(''.join('1' if x else '0' for x in bits.flat), 2):016x}"


def array_phash(array: np.ndarray) -> str:
    """Stable visual candidate hash after robust per-image grayscale scaling."""
    values = np.asarray(array, dtype=np.float32)
    lo, hi = np.percentile(values, (1, 99))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        scaled = np.zeros(values.shape, dtype=np.uint8)
    else:
        scaled = np.clip((values - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)
    return phash(Image.fromarray(scaled, mode="L"))


def image_metadata(path: Path) -> tuple[np.ndarray, int, int, str, str, list[str]]:
    flags: list[str] = []
    try:
        with Image.open(path) as image:
            gray = np.asarray(image.convert("L"))
            width, height = image.size
            return gray, width, height, array_hash(gray), phash(image), flags
    except Exception as exc:  # noqa: BLE001 -- audit must preserve failure detail
        flags.append(f"unreadable_image:{type(exc).__name__}")
        return np.empty((0, 0), dtype=np.uint8), "", "", "", "", flags


def standard_row(record: dict) -> dict:
    return {field: "" for field in FIELDS} | {key: value for key, value in record.items() if key in FIELDS}


def build_brisc(root: Path) -> list[dict]:
    rows: list[dict] = []
    for record in read_brisc_records(root):
        row = standard_row(record)
        image_path = record.pop("image_path")
        mask_path = record.pop("mask_path")
        image, width, height, decoded_hash, perceptual, flags = image_metadata(image_path)
        row.update(image_width=width, image_height=height, decoded_pixel_hash=decoded_hash,
                   perceptual_hash=perceptual, image_sha256=sha256_file(image_path) if image_path.exists() else "")
        if not image_path.exists():
            flags.append("missing_manifest_image")
        if mask_path is not None and mask_path.exists():
            mask, mw, mh, _, _, mask_flags = image_metadata(mask_path)
            flags.extend(mask_flags)
            row.update(mask_width=mw, mask_height=mh, mask_available=True,
                       mask_area_pixels=int(np.count_nonzero(mask)))
            if (width, height) != (mw, mh):
                flags.append("image_mask_dimension_mismatch")
            if record["class_label"] != "no_tumor" and not np.any(mask):
                flags.append("empty_tumor_mask")
        elif record["class_label"] != "no_tumor":
            flags.append("missing_mask")
            row["mask_available"] = False
        row["quality_flags"] = ";".join(flags)
        rows.append(row)
    return rows


def build_cheng(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(root.glob("brainTumorDataPublic_*/*.mat")):
        row = standard_row({"dataset": "cheng", "relative_image_path": path.relative_to(root).as_posix()})
        try:
            record = cheng_record(path, root)
            row.update(standard_row(record))
            image = np.asarray(record["image_array"])
            mask = np.asarray(record["mask_array"])
            row.update(image_width=image.shape[1], image_height=image.shape[0],
                       mask_width=mask.shape[1], mask_height=mask.shape[0], mask_available=True,
                       mask_area_pixels=int(np.count_nonzero(mask)), image_sha256=sha256_file(path),
                       decoded_pixel_hash=array_hash(image), perceptual_hash=array_phash(image))
            flags = []
            if image.shape != mask.shape:
                flags.append("image_mask_dimension_mismatch")
            unique = np.unique(mask)
            if not np.all(np.isin(unique, [0, 1])):
                flags.append("nonbinary_mask")
            if not np.any(mask):
                flags.append("empty_tumor_mask")
            row["quality_flags"] = ";".join(flags)
        except Exception as exc:  # preserve malformed records in the index
            row["sample_id"] = path.relative_to(root).with_suffix("").as_posix().replace("/", "__")
            row["quality_flags"] = f"unreadable_or_malformed_mat:{type(exc).__name__}:{str(exc)}"
        rows.append(row)
    return rows


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cheng-root", type=Path, default=ROOT / "cheng")
    parser.add_argument("--brisc-root", type=Path, default=ROOT / "brisc" / "brisc2025")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "manifests")
    args = parser.parse_args()
    write_rows(args.output_dir / "cheng_manifest.csv", build_cheng(args.cheng_root))
    write_rows(args.output_dir / "brisc_manifest.csv", build_brisc(args.brisc_root))


if __name__ == "__main__":
    main()
