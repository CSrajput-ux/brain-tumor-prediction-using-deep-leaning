from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

with open(ROOT / "revision" / "scripts" / "apply_pass3_fixes.py", "r", encoding="utf-8") as f:
    text = f.read()

old_ci_marker = "# 3. Create scripts/setup_ci_fixtures.py for GitHub Actions runner"
old_dl_marker = "# 4. Create scripts/download_checkpoints.py"
old_sec_marker = "# 5. Update scripts/11_run_secondary_robustness.py to eliminate contradictions"

with open(ROOT / "scripts" / "setup_ci_fixtures.py", "r", encoding="utf-8") as f:
    actual_ci = f.read().replace('"""', '\\"\\"\\"')

with open(ROOT / "scripts" / "download_checkpoints.py", "r", encoding="utf-8") as f:
    actual_dl = f.read().replace('"""', '\\"\\"\\"')

part1 = text.split(old_ci_marker)[0]
part3 = text.split(old_sec_marker)[1]

new_text = part1 + old_ci_marker + "\n# -------------------------------------------------------------\n"
new_text += 'ci_script = ROOT / "scripts" / "setup_ci_fixtures.py"\nci_code = """' + actual_ci + '"""\n'
new_text += 'ci_script.write_text(ci_code, encoding="utf-8")\nprint("Created scripts/setup_ci_fixtures.py.")\n\n'
new_text += "# -------------------------------------------------------------\n" + old_dl_marker + "\n# -------------------------------------------------------------\n"
new_text += 'dl_script = ROOT / "scripts" / "download_checkpoints.py"\ndl_code = """' + actual_dl + '"""\n'
new_text += 'dl_script.write_text(dl_code, encoding="utf-8")\nprint("Created scripts/download_checkpoints.py.")\n\n# -------------------------------------------------------------\n'
new_text += old_sec_marker + part3

with open(ROOT / "revision" / "scripts" / "apply_pass3_fixes.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("Updated revision/scripts/apply_pass3_fixes.py successfully.")

