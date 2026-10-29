"""Read Cheng MATLAB records without altering the raw source files."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import numpy as np


CLASS_LABELS = {1: "meningioma", 2: "glioma", 3: "pituitary"}


def _scalar(value: Any) -> Any:
    while hasattr(value, "shape") and getattr(value, "shape", ()) == (1, 1):
        value = value[0, 0]
    try:
        return value.item()
    except AttributeError:
        return value


def _patient_id(value: Any) -> str:
    """Decode the v7.3 MATLAB character vector used by the Cheng PID field."""
    import numpy as np
    array = np.asarray(value).squeeze()
    if array.ndim == 0:
        return str(array.item())
    if array.dtype.kind in {"u", "i"} and array.ndim == 1:
        try:
            return "".join(chr(int(code)) for code in array)
        except (TypeError, ValueError):
            pass
    return str(array.tolist())


def load_cheng_mat(path: Path) -> dict[str, Any]:
    """Load conventional or MATLAB 7.3 records and retain discovered field names.

    `cjdata` is expected from the official release, but this function raises a
    descriptive error rather than inventing fields if a local file differs.
    """
    try:
        from scipy.io import loadmat
        data = loadmat(path, struct_as_record=False, squeeze_me=True)
        record = data.get("cjdata")
        if record is None:
            raise ValueError("missing cjdata variable")
        fields = getattr(record, "_fieldnames", None)
        if not fields:
            raise ValueError("cjdata has no readable MATLAB struct fields")
        output = {field: _scalar(getattr(record, field)) for field in fields}
    except NotImplementedError:
        output = _load_hdf5_cjdata(path)
    output["_fields"] = sorted(output)
    return output


def _load_hdf5_cjdata(path: Path) -> dict[str, Any]:
    import h5py
    import numpy as np
    with h5py.File(path, "r") as handle:
        if "cjdata" not in handle:
            raise ValueError("missing cjdata variable")
        group = handle["cjdata"]
        output: dict[str, Any] = {}
        for field in group.keys():
            value = group[field][()]
            # MATLAB v7.3 struct fields are usually object references.
            if isinstance(value, np.ndarray) and value.dtype == h5py.ref_dtype:
                ref = value.flat[0]
                value = handle[ref][()] if ref else None
            output[field] = np.asarray(value).squeeze()
    return output


def cheng_record(path: Path, root: Path) -> dict[str, Any]:
    data = load_cheng_mat(path)
    required = {"image", "label", "PID", "tumorMask", "tumorBorder"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"missing required cjdata field(s): {', '.join(missing)}")
    label = int(_scalar(data["label"]))
    if label not in CLASS_LABELS:
        raise ValueError(f"unknown Cheng label: {label}")
    image, mask = data["image"], data["tumorMask"]
    return {
        "dataset": "cheng",
        "sample_id": path.relative_to(root).with_suffix("").as_posix().replace("/", "__"),
        "relative_image_path": path.relative_to(root).as_posix(),
        "relative_mask_path": path.relative_to(root).as_posix() + "#cjdata.tumorMask",
        "official_split": "",
        "class_label": CLASS_LABELS[label],
        "class_id": label - 1,
        "patient_id": _patient_id(data["PID"]),
        "plane": "",
        "image_array": image,
        "mask_array": mask,
        "available_fields": ";".join(data["_fields"]),
    }


class ChengDataset:
    """PyTorch Dataset for Cheng Brain Tumor MRI slices."""
    def __init__(
        self,
        manifest_path: Path | None = None,
        cheng_root: Path | None = None,
        split: str | list[str] | None = None,
        target_size: tuple[int, int] = (224, 224),
        is_training: bool = False,
        normalize_imagenet: bool = True,
        seed: int = 42,
    ):
        import csv
        import torch
        from src.data.preprocessing import preprocess_sample

        self.root = cheng_root or Path(__file__).resolve().parents[2] / "cheng"
        manifest_file = manifest_path or Path(__file__).resolve().parents[2] / "manifests" / "cheng_manifest.csv"
        with manifest_file.open("r", encoding="utf-8") as f:
            all_records = list(csv.DictReader(f))

        if split is not None:
            splits_set = {split} if isinstance(split, str) else set(split)
            self.records = [r for r in all_records if r["official_split"] in splits_set]
        else:
            self.records = all_records

        self.target_size = target_size
        self.is_training = is_training
        self.normalize_imagenet = normalize_imagenet
        self.rng = np.random.default_rng(seed)

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        import torch
        from src.data.preprocessing import preprocess_sample
        record = self.records[idx]
        mat_path = self.root / record["relative_image_path"]
        data = cheng_record(mat_path, self.root)

        raw_image = np.asarray(data["image_array"], dtype=np.float32)
        raw_mask = np.asarray(data["mask_array"], dtype=np.uint8)

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
            "patient_id": record["patient_id"],
            "class_label": record["class_label"],
            "official_split": record["official_split"],
            "metadata": meta,
        }

