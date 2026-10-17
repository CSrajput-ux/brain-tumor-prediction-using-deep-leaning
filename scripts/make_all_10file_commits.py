import os
import subprocess

BATCH_SIZE = 10

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def commit_in_batches(directory, category_name, exclude_exts=None):
    if not os.path.exists(directory):
        return 0
    files = []
    for root, _, fnames in os.walk(directory):
        for f in sorted(fnames):
            if exclude_exts and any(f.endswith(ext) for ext in exclude_exts):
                continue
            fp = os.path.join(root, f).replace("\\", "/")
            files.append(fp)
            
    # Check untracked/modified
    c, out, err = run_cmd("git status --porcelain")
    untracked_or_mod = set()
    for line in out.splitlines():
        if line.strip():
            untracked_or_mod.add(line[3:].strip().strip('"').replace("\\", "/"))
            
    # Filter files that actually have changes
    pending = []
    for f in files:
        # Check if f or any prefix is in untracked_or_mod
        if f in untracked_or_mod:
            pending.append(f)
        else:
            # check directory prefix
            parts = f.split('/')
            for i in range(1, len(parts)):
                prefix = '/'.join(parts[:i])
                if prefix in untracked_or_mod or prefix + '/' in untracked_or_mod:
                    pending.append(f)
                    break
                    
    # Remove duplicates
    pending = sorted(list(set(pending)))
    print(f"[{category_name}] Total pending files: {len(pending)}")
    if not pending:
        return 0
        
    total_batches = (len(pending) + BATCH_SIZE - 1) // BATCH_SIZE
    commits_made = 0
    
    for i in range(total_batches):
        batch = pending[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        add_cmd = 'git add ' + ' '.join([f'"{f}"' for f in batch])
        c, out, err = run_cmd(add_cmd)
        if c != 0:
            print(f"Error staging batch {i+1}:", err)
            continue
            
        msg = f"{category_name.lower()}: batch {i + 1}/{total_batches} ({len(batch)} files)"
        c, out, err = run_cmd(f'git commit -m "{msg}"')
        if c == 0:
            print(f"Committed {category_name} Batch {i+1}/{total_batches} ({len(batch)} files)")
            commits_made += 1
        else:
            if "nothing to commit" not in out and "nothing to commit" not in err:
                print(f"Error committing batch {i+1}:", err)
                
    return commits_made

def main():
    print("=== Creating 10-File Batch Commits ===")
    commit_in_batches("tests", "Tests")
    commit_in_batches("publication", "Publication")
    commit_in_batches("reports", "Reports")
    commit_in_batches("experiments", "Experiments", exclude_exts=[".pt"])
    print("=== All 10-File Batches Committed Successfully! ===")

if __name__ == "__main__":
    main()
