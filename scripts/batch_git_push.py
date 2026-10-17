import os
import sys
import subprocess

BATCH_SIZE = 10

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def get_untracked_and_modified_files():
    code, stdout, stderr = run_cmd("git status --porcelain")
    if code != 0:
        print("Error checking git status:", stderr)
        return []
    
    files = []
    for line in stdout.splitlines():
        if not line.strip(): continue
        # Porcelain status is XY PATH or "?? PATH"
        status = line[:2]
        path = line[3:].strip().strip('"')
        if os.path.exists(path):
            if os.path.isdir(path):
                # Expand directory to individual files
                for root, dirs, fnames in os.walk(path):
                    for fn in fnames:
                        fp = os.path.join(root, fn).replace("\\", "/")
                        files.append(fp)
            else:
                files.append(path.replace("\\", "/"))
    return files

def main():
    print("=== Automated 10-File Batch Git Commit & Push ===")
    files = get_untracked_and_modified_files()
    print(f"Total files detected to stage: {len(files)}")
    
    if not files:
        print("No files to commit. Checking if commits need to be pushed...")
        code, out, err = run_cmd("git push origin main")
        print(out, err)
        return

    # Process in batches of 10
    total_batches = (len(files) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Grouping into {total_batches} batches of {BATCH_SIZE} files each.")
    
    for b_idx in range(total_batches):
        batch = files[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
        print(f"\n--- Batch {b_idx + 1}/{total_batches} ({len(batch)} files) ---")
        
        # Add files
        add_cmd = 'git add ' + ' '.join([f'"{f}"' for f in batch])
        c_add, out_add, err_add = run_cmd(add_cmd)
        if c_add != 0:
            print(f"Error staging batch {b_idx + 1}:", err_add)
            continue
            
        # Commit
        msg = f"feat: batch {b_idx + 1}/{total_batches} - adding {len(batch)} files"
        c_com, out_com, err_com = run_cmd(f'git commit -m "{msg}"')
        if c_com != 0:
            print(f"Error committing batch {b_idx + 1}:", err_com)
            continue
        print(f"Committed batch {b_idx + 1}: {msg}")
        
        # Push
        c_push, out_push, err_push = run_cmd("git push origin main")
        if c_push != 0:
            print(f"Push failed for batch {b_idx + 1}:", err_push)
            print("Aborting remaining batches. Please ensure git authentication is configured.")
            sys.exit(1)
        else:
            print(f"Successfully pushed batch {b_idx + 1} to GitHub!")

    print("\nAll batches committed and pushed successfully!")

if __name__ == "__main__":
    main()
