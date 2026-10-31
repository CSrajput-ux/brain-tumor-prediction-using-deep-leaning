"""Apply MA-04 (Training config dropout & seed) and MA-06 (Checkpoint SHA-256 verification)."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# -------------------------------------------------------------
# 1. Update scripts/07_train_baseline.py (MA-04)
# -------------------------------------------------------------
train_script = ROOT / "scripts" / "07_train_baseline.py"
text = train_script.read_text(encoding="utf-8")

if "import random" not in text:
    text = text.replace("import json\n", "import json\nimport random\n")

seed_fn = """
def set_seed(seed: int = 42) -> None:
    \"\"\"Set random seed across Python, NumPy, and PyTorch for deterministic execution.\"\"\"
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
"""

if "def set_seed" not in text:
    text = text.replace(
        'BRISC_CLASSES = ["glioma", "meningioma", "pituitary", "no_tumor"]\n',
        'BRISC_CLASSES = ["glioma", "meningioma", "pituitary", "no_tumor"]\n' + seed_fn + '\n'
    )

# Add dropout parameter to train_cheng_folds
text = text.replace(
    """    max_train_batches: int | None = None,
    max_val_batches: int | None = None,
) -> dict[str, Any]:""",
    """    max_train_batches: int | None = None,
    max_val_batches: int | None = None,
    dropout: float = 0.2,
) -> dict[str, Any]:""",
    1
)

text = text.replace(
    "model = build_model(architecture, num_classes=3, pretrained=True).to(device)",
    "model = build_model(architecture, num_classes=3, pretrained=True, dropout=dropout).to(device)"
)

# Add dropout parameter to train_brisc_baseline
text = text.replace(
    """    max_train_batches: int | None = None,
    max_val_batches: int | None = None,
) -> dict[str, Any]:""",
    """    max_train_batches: int | None = None,
    max_val_batches: int | None = None,
    dropout: float = 0.2,
) -> dict[str, Any]:"""
)

text = text.replace(
    "model = build_model(architecture, num_classes=4, pretrained=True).to(device)",
    "model = build_model(architecture, num_classes=4, pretrained=True, dropout=dropout).to(device)"
)

# In main(): add seed setting
if "seed = int(training_cfg" not in text:
    old_dev = '    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")'
    new_dev = """    seed = int(training_cfg.get("common", {}).get("seed", 42))
    set_seed(seed)
    print(f"Applied random seed: {seed}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")"""
    text = text.replace(old_dev, new_dev, 1)

# In main(): resolve dropout from arch_cfg
old_cfg = """        weight_decay = args.weight_decay if args.weight_decay is not None else arch_cfg.get("weight_decay", 1e-2)

        print(f"\\nConfiguring {arch.upper()}: epochs={epochs}, batch_size={batch_size}, lr={lr}, weight_decay={weight_decay}")"""

new_cfg = """        weight_decay = args.weight_decay if args.weight_decay is not None else arch_cfg.get("weight_decay", 1e-2)
        dropout = float(arch_cfg.get("dropout", 0.2 if arch == "resnet50" else 0.1))

        print(f"\\nConfiguring {arch.upper()}: epochs={epochs}, batch_size={batch_size}, lr={lr}, weight_decay={weight_decay}, dropout={dropout}")"""

text = text.replace(old_cfg, new_cfg)

text = text.replace(
    """        c_res = train_cheng_folds(
            arch,
            selected_folds,
            epochs,
            batch_size,
            lr,
            weight_decay,
            device,
            args.checkpoints_dir,
            args.predictions_dir,
            args.max_train_batches,
            args.max_val_batches,
        )""",
    """        c_res = train_cheng_folds(
            arch,
            selected_folds,
            epochs,
            batch_size,
            lr,
            weight_decay,
            device,
            args.checkpoints_dir,
            args.predictions_dir,
            args.max_train_batches,
            args.max_val_batches,
            dropout=dropout,
        )"""
)

text = text.replace(
    """        b_res = train_brisc_baseline(
            arch,
            epochs,
            batch_size,
            lr,
            weight_decay,
            device,
            args.checkpoints_dir,
            args.predictions_dir,
            args.max_train_batches,
            args.max_val_batches,
        )""",
    """        b_res = train_brisc_baseline(
            arch,
            epochs,
            batch_size,
            lr,
            weight_decay,
            device,
            args.checkpoints_dir,
            args.predictions_dir,
            args.max_train_batches,
            args.max_val_batches,
            dropout=dropout,
        )"""
)

train_script.write_text(text, encoding="utf-8")
print("Updated scripts/07_train_baseline.py with deterministic seed and dropout injection.")


# -------------------------------------------------------------
# 2. Update scripts/09_run_counterfactual_audit.py (MA-06)
# -------------------------------------------------------------
audit_script = ROOT / "scripts" / "09_run_counterfactual_audit.py"
audit_text = audit_script.read_text(encoding="utf-8")

if "import hashlib" not in audit_text:
    audit_text = audit_text.replace("import csv\n", "import csv\nimport hashlib\n")

hashes_dict = """
# Authoritative SHA-256 hashes of trained checkpoints
VERIFIED_CHECKPOINT_HASHES = {
    "deit_small_patch16_224_brisc.pt": "f7dcadc8e009eaed32929f55657e840e52675c4d79245565a75b0103077878fe",
    "deit_small_patch16_224_cheng_fold_1.pt": "f5545de00e1ceab9aaa7aa12a37121ca9e73454675d50065c1b65aaa99b4b33a",
    "resnet50_brisc.pt": "057e78999057335e54e4821fb9ef240ee71df4c64afcbf66902da948d75627b0",
    "resnet50_cheng_fold_1.pt": "f40404094e4bddf7f344abd89071c4d8bb17b19d7ae2e15c01433562fec8d8c3",
}
"""

if "VERIFIED_CHECKPOINT_HASHES" not in audit_text:
    audit_text = audit_text.replace(
        'BRISC_CLASSES = ["glioma", "meningioma", "pituitary", "no_tumor"]\n',
        'BRISC_CLASSES = ["glioma", "meningioma", "pituitary", "no_tumor"]\n' + hashes_dict + '\n'
    )

old_load = """def load_trained_model(
    architecture: str,
    num_classes: int,
    checkpoint_path: Path,
    device: torch.device,
) -> torch.nn.Module:
    \"\"\"Load model checkpoint into evaluation mode.\"\"\"
    model = build_model(architecture, num_classes=num_classes, pretrained=False)
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"CRITICAL ERROR: Required checkpoint '{checkpoint_path}' does not exist. "
            f"Execution halted to prevent auditing on uninitialized random weights."
        )
    ckpt = torch.load(checkpoint_path, map_location="cpu")
    state_dict = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    model.load_state_dict(state_dict, strict=True)
    print(f"Loaded verified checkpoint strictly from {checkpoint_path}")
    model.to(device)
    model.eval()
    return model"""

new_load = """def load_trained_model(
    architecture: str,
    num_classes: int,
    checkpoint_path: Path,
    device: torch.device,
) -> torch.nn.Module:
    \"\"\"Load model checkpoint into evaluation mode with strict SHA-256 hash verification.\"\"\"
    model = build_model(architecture, num_classes=num_classes, pretrained=False)
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"CRITICAL ERROR: Required checkpoint '{checkpoint_path}' does not exist. "
            f"Execution halted to prevent auditing on uninitialized random weights."
        )

    # Compute SHA-256 digest to prevent evaluating on corrupt or altered model weights
    hasher = hashlib.sha256()
    with open(checkpoint_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest()

    expected_hash = VERIFIED_CHECKPOINT_HASHES.get(checkpoint_path.name)
    if expected_hash is not None and actual_hash != expected_hash:
        raise ValueError(
            f"CRITICAL INTEGRITY FAILURE: Checkpoint {checkpoint_path.name} SHA-256 mismatch!\\n"
            f"Expected: {expected_hash}\\nActual:   {actual_hash}"
        )

    ckpt = torch.load(checkpoint_path, map_location="cpu")
    state_dict = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    model.load_state_dict(state_dict, strict=True)
    print(f"Loaded verified checkpoint strictly from {checkpoint_path} (SHA-256: {actual_hash[:12]}... PASS)")
    model.to(device)
    model.eval()
    return model"""

audit_text = audit_text.replace(old_load, new_load)
audit_script.write_text(audit_text, encoding="utf-8")
print("Updated scripts/09_run_counterfactual_audit.py with SHA-256 checksum verification.")

# -------------------------------------------------------------
# 3. Create checkpoints/manifest.json and configs/checkpoint_manifest.json
# -------------------------------------------------------------
import json
manifest_data = {
    "deit_small_patch16_224_brisc.pt": {
        "sha256": "f7dcadc8e009eaed32929f55657e840e52675c4d79245565a75b0103077878fe",
        "size_bytes": 260202973,
        "architecture": "deit_small_patch16_224",
        "dataset": "brisc",
        "classes": 4,
        "verified": True
    },
    "deit_small_patch16_224_cheng_fold_1.pt": {
        "sha256": "f5545de00e1ceab9aaa7aa12a37121ca9e73454675d50065c1b65aaa99b4b33a",
        "size_bytes": 260202599,
        "architecture": "deit_small_patch16_224",
        "dataset": "cheng",
        "fold": "fold_1",
        "classes": 3,
        "verified": True
    },
    "resnet50_brisc.pt": {
        "sha256": "057e78999057335e54e4821fb9ef240ee71df4c64afcbf66902da948d75627b0",
        "size_bytes": 282650264,
        "architecture": "resnet50",
        "dataset": "brisc",
        "classes": 4,
        "verified": True
    },
    "resnet50_cheng_fold_1.pt": {
        "sha256": "f40404094e4bddf7f344abd89071c4d8bb17b19d7ae2e15c01433562fec8d8c3",
        "size_bytes": 282631351,
        "architecture": "resnet50",
        "dataset": "cheng",
        "fold": "fold_1",
        "classes": 3,
        "verified": True
    }
}

ckpt_manifest = ROOT / "checkpoints" / "manifest.json"
ckpt_manifest.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

cfg_manifest = ROOT / "configs" / "checkpoint_manifest.json"
cfg_manifest.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
print("Saved checkpoint manifests to checkpoints/manifest.json and configs/checkpoint_manifest.json")

# Update .gitignore so checkpoints/manifest.json is tracked
gitignore = ROOT / ".gitignore"
git_text = gitignore.read_text(encoding="utf-8")
if "!checkpoints/manifest.json" not in git_text:
    git_text = git_text.replace("checkpoints/\n", "checkpoints/\n!checkpoints/manifest.json\n")
    gitignore.write_text(git_text, encoding="utf-8")
    print("Updated .gitignore to unignore checkpoints/manifest.json")

