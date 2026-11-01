import os
import sys

search_terms = sys.argv[1:] if len(sys.argv) > 1 else ["MUJ/IEC", "Chhotu", "49 patient"]
ignore_dirs = {'.git', '__pycache__', '.pytest_cache', 'checkpoints', '.vscode', '.idea'}

results = {term: [] for term in search_terms}

for root, dirs, files in os.walk('.'):
    # filter in-place
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for f in files:
        if f.endswith(('.py', '.md', '.csv', '.json', '.txt', '.tex')):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    for term in search_terms:
                        if term.lower() in content.lower():
                            results[term].append(p)
            except Exception:
                pass

for term, matched_files in results.items():
    print(f"=== Term: '{term}' ({len(matched_files)} files) ===")
    for mf in matched_files[:15]:
        print("  ", mf)
