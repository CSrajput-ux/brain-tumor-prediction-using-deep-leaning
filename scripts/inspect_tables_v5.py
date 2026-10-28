import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx

doc = docx.Document('Brain_MRI_Paper_Final_Corrected_v5.docx')

for t_idx, table in enumerate(doc.tables):
    first_cell = table.rows[0].cells[0].text.strip().replace('\n', ' ')
    print(f'Table {t_idx} (rows: {len(table.rows)}, cols: {len(table.columns)}): first cell = "{first_cell[:40]}"')
