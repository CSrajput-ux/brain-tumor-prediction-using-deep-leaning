"""Download and verify canonical model checkpoints against SHA-256 manifest."""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS_DIR = ROOT / "checkpoints"
MANIFEST_FILE = ROOT / "configs" / "checkpoint_manifest.json"

def verify_checksum(file_path: Path, expected_hash: str) -> bool:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest()
    return actual_hash == expected_hash, actual_hash

def main():
    parser = argparse.ArgumentParser(description="Download and verify baseline checkpoints.")
    parser.add_argument("--verify-only", action="store_true", help="Audit local checkpoints without downloading")
    parser.add_argument("--mirror-base-url", type=str, default="", help="Base URL for remote checkpoint hosting")
    args = parser.parse_args()

    if not MANIFEST_FILE.exists():
        print(f"Error: Manifest {MANIFEST_FILE} not found.")
        sys.exit(1)

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_pass = True
    print(f"Auditing {len(manifest)} checkpoints from {MANIFEST_FILE.name}:\n")

    for fname, meta in manifest.items():
        expected_hash = meta["sha256"]
        local_path = CHECKPOINTS_DIR / fname

        if not local_path.exists():
            if args.mirror_base_url:
                url = f"{args.mirror_base_url.rstrip('/')}/{fname}"
                print(f"Downloading {fname} from {url}...")
                CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(url, local_path)
            else:
                print(f"[MISSING] {fname}: File not present on disk. Deposit weight file or specify --mirror-base-url.")
                all_pass = False
                continue

        ok, actual_hash = verify_checksum(local_path, expected_hash)
        if ok:
            print(f"[PASS] {fname} (SHA-256: {actual_hash[:16]}...) - Verified")
        else:
            print(f"[FAIL] {fname}: Hash mismatch!\n  Expected: {expected_hash}\n  Actual:   {actual_hash}")
            all_pass = False

    if all_pass:
        print("\nAll registered model checkpoints verified strictly.")
    else:
        print("\nOne or more checkpoint integrity checks failed.")
        if args.verify_only:
            sys.exit(1)

if __name__ == "__main__":
    main()
