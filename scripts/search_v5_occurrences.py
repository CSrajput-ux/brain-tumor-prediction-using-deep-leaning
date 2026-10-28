import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx
import re

doc = docx.Document('Brain_MRI_Paper_Final_Corrected_v5.docx')

print("=== SEARCHING OCCURRENCES FOR FIXES 1-9 ===")

def search_text(pattern, label):
    print(f"\n--- {label} (pattern: {pattern}) ---")
    matches = []
    for idx, p in enumerate(doc.paragraphs):
        if re.search(pattern, p.text, re.IGNORECASE):
            matches.append((idx, p.text.strip()))
            print(f"P{idx}: {p.text.strip()[:140]}...")
    return matches

search_text(r"clinical margin|standard error|\bSE\b|practical-significance", "FIX 1: Threshold wording")
search_text(r"perturbation dose|class-asymmetric|tumour size.*leave|88%|91%|dose varies", "FIX 2: Dose claim")
search_text(r"2167|3073|1558|2107", "FIX 3: Input HF energy")
search_text(r"pituitary prior|pituitary slices labelled glioma|labelled pituitary tumour|remain near zero across all", "FIX 4: Class transitions")
search_text(r"demonstrat|establish|prove|confirm|clearly shows|\bexact\b|is exactly what", "FIX 5: Overstated language")
search_text(r"primarily axial|predominantly coronal|commonly used imaging planes", "FIX 6: Table 2 imaging plane")
search_text(r"pre-specified|preregistered|hypotheses were formulated|immutable external registry", "FIX 7: Pre-registration caveat")
search_text(r"stricter near-duplicate|grouping stringency|merges only two", "FIX 8: Grouping stringency")
search_text(r"disentangling", "FIX 9: Title & Disentangling")
