import os
import sys
import subprocess
import time

BATCH_SIZE = 10

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def push_file_list(file_list, category_name):
    total_files = len(file_list)
    if total_files == 0:
        print(f"[{category_name}] No files to push.")
        return True
        
    total_batches = (total_files + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\n=======================================================")
    print(f"Starting {category_name}: {total_files} files in {total_batches} batches (10 files/batch)")
    print(f"=======================================================")
    
    for i in range(total_batches):
        batch = file_list[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        print(f"\n[{category_name}] Batch {i + 1}/{total_batches} ({len(batch)} files)...")
        
        # 1. Stage files
        add_cmd = 'git add ' + ' '.join([f'"{f}"' for f in batch])
        c, out, err = run_cmd(add_cmd)
        if c != 0:
            print(f"Error staging batch {i + 1}: {err}")
            return False
            
        # 2. Commit
        commit_msg = f"{category_name.lower()}: batch {i + 1}/{total_batches} ({len(batch)} files)"
        c, out, err = run_cmd(f'git commit -m "{commit_msg}"')
        if c != 0:
            # Check if there were no changes
            if "nothing to commit" in out or "nothing to commit" in err:
                print(f"Batch {i + 1} already committed or no changes.")
                continue
            print(f"Error committing batch {i + 1}: {err}")
            return False
            
        # 3. Push
        print(f"Pushing batch {i + 1}/{total_batches} to origin main...")
        max_retries = 3
        success = False
        for attempt in range(max_retries):
            c, out, err = run_cmd("git push origin main")
            if c == 0:
                print(f"Batch {i + 1}/{total_batches} pushed successfully!")
                success = True
                break
            else:
                print(f"Push attempt {attempt + 1} failed: {err}. Retrying in 3s...")
                time.sleep(3)
                
        if not success:
            print(f"Push failed permanently for batch {i + 1}.")
            return False
            
        time.sleep(1)
        
    print(f"Completed {category_name} successfully!")
    return True

def get_files_in_dir(directory, exclude_exts=None):
    if not os.path.exists(directory):
        return []
    res = []
    for root, _, files in os.walk(directory):
        for f in sorted(files):
            if exclude_exts and any(f.endswith(ext) for ext in exclude_exts):
                continue
            fp = os.path.join(root, f).replace("\\", "/")
            res.append(fp)
    return res

def main():
    print("=== Brain MRI Research Incremental 10-File Batch Pusher ===")
    
    # Category 1: tests/ (~57 files)
    test_files = get_files_in_dir("tests")
    if not push_file_list(test_files, "Tests"):
        sys.exit(1)
        
    # Category 2: publication/ (~55 files)
    pub_files = get_files_in_dir("publication")
    if not push_file_list(pub_files, "Publication"):
        sys.exit(1)
        
    # Category 3: reports/ (~84 files)
    rep_files = get_files_in_dir("reports")
    if not push_file_list(rep_files, "Reports"):
        sys.exit(1)
        
    # Category 4: experiments/ (excluding .pt checkpoints for now, ~219 files)
    exp_text_files = get_files_in_dir("experiments", exclude_exts=[".pt"])
    if not push_file_list(exp_text_files, "Experiments-Metadata"):
        sys.exit(1)
        
    print("\nAll initial research assets (~415 files) successfully committed and pushed in batches of 10!")

if __name__ == "__main__":
    main()
