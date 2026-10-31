import sys, docx
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(r"c:\Users\jkgga\Downloads\brain")
rev_docx = ROOT / "revision" / "Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Revised.docx"

doc = docx.Document(str(rev_docx))
print(f"Total Paragraphs: {len(doc.paragraphs)}")
print(f"Total Tables: {len(doc.tables)}")

# Check for figure captions
print("\n--- Figure Captions Found ---")
for i, p in enumerate(doc.paragraphs):
    if p.text.startswith("Fig.") or p.text.startswith("Figure "):
        print(f"P{i:03d}: {p.text[:90]}...")

# Check for table captions & sizes
print("\n--- Tables Found ---")
for i, t in enumerate(doc.tables):
    rows = len(t.rows)
    cols = len(t.columns)
    header_text = [cell.text.replace("\n", " ").strip() for cell in t.rows[0].cells[:4]]
    print(f"Table {i+1}: {rows} rows x {cols} cols | Header: {header_text}")

# Check for key terms
full_text = "\n".join([p.text for p in doc.paragraphs])
for t in doc.tables:
    for row in t.rows:
        full_text += " " + " ".join([c.text for c in row.cells])

terms = [
    "Fold 1 test partition", "Official Test (N=1,000)", "Clean Test (N=899)",
    "Neoplasm Batch (N=480)", "Neoplasm Batch (N=397)", "Holm-Bonferroni",
    "Supplementary Table S1", "Supplementary Table S2", "159 exact SHA-256 duplicate image pairs",
    "Wallis", "Ya\u011f\u0131\u015f", "Sourget", "Fateh", "0.7131", "0.7431"
]
print("\n--- Key Audit Term Search ---")
for term in terms:
    count = full_text.count(term)
    print(f"'{term}': {count} occurrences")

# Check for unresolved bracketed placeholders
import re
placeholders = re.findall(r"\[(?:TODO|TBD|INSERT|XXX|\?\?\?)[^\]]*\]", full_text, flags=re.I)
print(f"\nUnresolved placeholders found: {placeholders}")

