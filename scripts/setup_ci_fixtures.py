"""Deterministic CI test fixture generator.

Ensures real-data integration tests and model architecture tests run deterministically in CI runners
where multi-gigabyte raw MRI volumes and large binary checkpoints are excluded from git.
"""
import csv
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image
import torch
from scipy.io import savemat

ROOT = Path(__file__).resolve().parents[1]

def setup_fixtures():
    print("Setting up deterministic CI test fixtures...")

    # 1. Cheng dataset fixtures for ChengDataset across splits
    cheng_manifest = ROOT / "manifests" / "cheng_manifest.csv"
    if cheng_manifest.exists():
        cheng_paths = set()
        with open(cheng_manifest, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            if reader:
                cheng_paths.add(reader[0]["relative_image_path"])
                seen_splits = set()
                for row in reader:
                    sp = row.get("official_split")
                    if sp and sp not in seen_splits:
                        seen_splits.add(sp)
                        cheng_paths.add(row["relative_image_path"])

        mock_cjdata = {
            "label": 1,
            "PID": "PATIENT_001",
            "image": np.ones((512, 512), dtype=np.int16) * 100,
            "tumorMask": np.pad(np.ones((64, 64), dtype=np.uint8), 224),
            "tumorBorder": np.array([[224, 224], [288, 288]], dtype=np.float64),
        }
        for rel_path in cheng_paths:
            target_mat = ROOT / "cheng" / rel_path
            if not target_mat.exists():
                target_mat.parent.mkdir(parents=True, exist_ok=True)
                savemat(str(target_mat), {"cjdata": mock_cjdata})
                print(f"Created Cheng test fixture: {target_mat}")

    # 2. BRISC dataset fixtures for BriscDataset across splits
    brisc_manifest = ROOT / "manifests" / "brisc_manifest.csv"
    if brisc_manifest.exists():
        brisc_pairs = []
        with open(brisc_manifest, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            if reader:
                brisc_pairs.append((reader[0]["relative_image_path"], reader[0].get("relative_mask_path", "")))
                seen_splits = set()
                for row in reader:
                    sp = row.get("official_split")
                    if sp and sp not in seen_splits:
                        seen_splits.add(sp)
                        brisc_pairs.append((row["relative_image_path"], row.get("relative_mask_path", "")))

        for rel_img, rel_mask in brisc_pairs:
            rel_img = rel_img.replace("\\", "/")
            target_img = ROOT / "brisc" / "brisc2025" / rel_img
            if not target_img.exists():
                target_img.parent.mkdir(parents=True, exist_ok=True)
                img = Image.fromarray(np.ones((512, 512), dtype=np.uint8) * 128, mode="L")
                img.save(target_img)
                print(f"Created BRISC image fixture: {target_img}")

            if rel_mask:
                rel_mask = rel_mask.replace("\\", "/")
                target_mask = ROOT / "brisc" / "brisc2025" / rel_mask
                if not target_mask.exists():
                    target_mask.parent.mkdir(parents=True, exist_ok=True)
                    mask = Image.fromarray(np.pad(np.ones((64, 64), dtype=np.uint8) * 255, 224), mode="L")
                    mask.save(target_mask)
                    print(f"Created BRISC mask fixture: {target_mask}")

    # 3. Checkpoint fixtures for test_checkpoint_structure in CI
    # Check each required checkpoint individually so partial sets are completed.
    ckpts_dir = ROOT / "checkpoints"
    ckpts_dir.mkdir(parents=True, exist_ok=True)

    required_ckpts = [
        ("resnet50", 3, "resnet50_cheng_fold_1.pt"),
        ("resnet50", 4, "resnet50_brisc.pt"),
        ("deit_small_patch16_224", 3, "deit_small_patch16_224_cheng_fold_1.pt"),
        ("deit_small_patch16_224", 4, "deit_small_patch16_224_brisc.pt"),
    ]

    missing_ckpts = [item for item in required_ckpts if not (ckpts_dir / item[2]).exists()]
    if missing_ckpts:
        print(f"Generating {len(missing_ckpts)} missing checkpoint test fixtures...")
        sys_path = str(ROOT)
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from src.models import build_model

        for arch, num_cls, fname in missing_ckpts:
            pt_path = ckpts_dir / fname
            model = build_model(arch, num_classes=num_cls, pretrained=False)
            ckpt_obj = {
                "epoch": 5,
                "model_state_dict": model.state_dict(),
                "config": {"architecture": arch, "num_classes": num_cls, "batch_size": 16, "learning_rate": 1e-4},
                "metrics": {"macro_f1": 0.84, "accuracy": 0.85, "balanced_accuracy": 0.84},
                "val_metrics": {"macro_f1": 0.84, "accuracy": 0.85}
            }
            torch.save(ckpt_obj, pt_path)
            print(f"Generated test checkpoint fixture: {pt_path.name}")

    print("CI test fixtures successfully initialized.")

if __name__ == "__main__":
    setup_fixtures()
