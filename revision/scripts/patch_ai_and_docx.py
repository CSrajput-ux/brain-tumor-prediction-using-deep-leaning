import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1. Update scripts/13_generate_final_docx.py
p13 = ROOT / "scripts" / "13_generate_final_docx.py"
t13 = p13.read_text(encoding="utf-8")
t13 = t13.replace(
    "(N = 480 slices, 49 patients)",
    "(an evaluated baseline prediction subset of 480 slices from 41 unseen patients drawn from the 645-slice, 47-patient Fold 1 partition)"
)
t13 = t13.replace(
    "(evaluated across 49 unseen patients)",
    "(evaluated across 41 unseen patients drawn from the 645-slice, 47-patient Fold 1 partition)"
)
p13.write_text(t13, encoding="utf-8")
print("Updated scripts/13_generate_final_docx.py")

# 2. Update revision/scripts/apply_final_manuscript_docx.py
p_rev = ROOT / "revision" / "scripts" / "apply_final_manuscript_docx.py"
t_rev = p_rev.read_text(encoding="utf-8")
old_ai = '''doc.paragraphs[177].text = (
    "Generative AI and AI-assisted technologies. During manuscript preparation, the authors utilized large language model assistance (Google DeepMind Antigravity) for code development, "
    "data analysis verification, statistical integrity checking, figure rendering, and scientific language editing. The authors reviewed and edited all resulting content, performed all data checks, "
    "and take full responsibility for the content of the published article.\\\\n\\\\n"'''

new_ai = '''doc.paragraphs[177].text = (
    "Generative AI and AI-assisted technologies. During manuscript preparation, the authors utilized large language model assistance (Google DeepMind Antigravity powered by Gemini and OpenAI ChatGPT) for code implementation assistance, automated unit testing, script-level biostatistical verification, figure/table generation scripts, document synchronization, and scientific language editing. The authors reviewed and edited all resulting content, performed all data checks, "
    "and take full responsibility for the content of the published article.\\\\n\\\\n"'''

if old_ai in t_rev:
    t_rev = t_rev.replace(old_ai, new_ai)
    p_rev.write_text(t_rev, encoding="utf-8")
    print("Updated AI disclosure in apply_final_manuscript_docx.py")
else:
    print("old_ai string not found directly, performing regex replacement...")
    t_rev = re.sub(
        r'doc\.paragraphs\[177\]\.text = \(\s*"Generative AI and AI-assisted technologies\..*?"and take full responsibility for the content of the published article\.\\\\n\\\\n"',
        new_ai[len('doc.paragraphs[177].text = (\n    '):],
        t_rev,
        flags=re.DOTALL
    )
    p_rev.write_text(t_rev, encoding="utf-8")
    print("Regex replacement completed for apply_final_manuscript_docx.py")
