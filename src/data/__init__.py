"""Dataset ingestion and preprocessing modules for the MRI region-sensitivity audit."""
from src.data.brisc_dataset import BriscDataset, read_brisc_records, CLASS_IDS as BRISC_CLASS_IDS
from src.data.cheng_dataset import ChengDataset, cheng_record, load_cheng_mat, CLASS_LABELS as CHENG_CLASS_LABELS
from src.data.preprocessing import (
    preprocess_sample,
    scale_intensity,
    resize_and_pad,
    to_model_tensor,
    apply_mild_augmentation,
)

__all__ = [
    "BriscDataset",
    "ChengDataset",
    "read_brisc_records",
    "cheng_record",
    "load_cheng_mat",
    "preprocess_sample",
    "scale_intensity",
    "resize_and_pad",
    "to_model_tensor",
    "apply_mild_augmentation",
    "BRISC_CLASS_IDS",
    "CHENG_CLASS_LABELS",
]
