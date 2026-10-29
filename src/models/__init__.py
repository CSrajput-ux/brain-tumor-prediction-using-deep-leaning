"""Model definitions, architecture adapters, and training modules."""
from src.models.deit_classifier import DeiTSmallClassifier
from src.models.resnet_classifier import ResNet50Classifier
from src.models.training import (
    build_model,
    compute_calibration_metrics,
    compute_classification_metrics,
    evaluate,
    get_cosine_schedule_with_warmup,
    load_checkpoint,
    save_checkpoint,
    train_model,
    train_one_epoch,
)

__all__ = [
    "DeiTSmallClassifier",
    "ResNet50Classifier",
    "build_model",
    "compute_calibration_metrics",
    "compute_classification_metrics",
    "evaluate",
    "get_cosine_schedule_with_warmup",
    "load_checkpoint",
    "save_checkpoint",
    "train_model",
    "train_one_epoch",
]
