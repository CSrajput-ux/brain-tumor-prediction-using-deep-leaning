import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx
import re

doc = docx.Document('Brain_MRI_Paper_Final_Corrected_v5.docx')

words = ['demonstrat', 'establish', 'prove', 'confirm', 'exact', 'clearly shows', 'clinical margin', 'standard error', 'seam share', 'pituitary prior', 'disentangl']

for w in words:
    print(f"\n==================== SEARCH FOR: {w} ====================")
    for p_idx, p in enumerate(doc.paragraphs):
        if re.search(r'\b' + w, p.text, re.IGNORECASE) or (w == 'seam share' and 'seam share' in p.text.lower()) or (w == 'clinical margin' and 'clinical margin' in p.text.lower()) or (w == 'standard error' and 'standard error' in p.text.lower()):
            # Print sentence containing the word
            sentences = re.split(r'(?<=[.!?])\s+', p.text)
            for s in sentences:
                if re.search(w, s, re.IGNORECASE):
                    print(f"P{p_idx}: {s.strip()}")
