import os
import subprocess

pts = []
for root, _, files in os.walk('experiments/phase_2_baseline'):
    for f in sorted(files):
        if f.endswith('.pt'):
            pts.append(os.path.join(root, f).replace("\\", "/"))

print(f"Found {len(pts)} checkpoint files to commit.")
for idx, pt in enumerate(pts):
    subprocess.run(f'git add "{pt}"', shell=True)
    msg = f"model: checkpoint {idx+1}/{len(pts)} - {os.path.basename(pt)} ({os.path.basename(os.path.dirname(pt))})"
    res = subprocess.run(f'git commit -m "{msg}"', shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[{idx+1}/{len(pts)}] Committed: {msg}")
    else:
        print(f"Error on {pt}: {res.stderr}")

print("All checkpoints committed successfully!")
