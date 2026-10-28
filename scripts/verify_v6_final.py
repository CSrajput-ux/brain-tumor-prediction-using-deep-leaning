import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx
import difflib

v5 = docx.Document('Brain_MRI_Paper_Final_Corrected_v5.docx')
v6 = docx.Document('Brain_MRI_Paper_Final_Corrected_v6.docx')

print(f"v5 paragraphs: {len(v5.paragraphs)}, v6 paragraphs: {len(v6.paragraphs)}")
assert len(v5.paragraphs) == len(v6.paragraphs), "Paragraph count mismatch!"

print(f"v5 tables: {len(v5.tables)}, v6 tables: {len(v6.tables)}")
assert len(v5.tables) == len(v6.tables), "Table count mismatch!"

changed_p = []
for idx in range(len(v5.paragraphs)):
    t5 = v5.paragraphs[idx].text
    t6 = v6.paragraphs[idx].text
    if t5 != t6:
        changed_p.append((idx, t5, t6))

print(f"Total changed paragraphs in v6 relative to v5: {len(changed_p)}")
for idx, t5, t6 in changed_p:
    print(f"\n==================== Paragraph P{idx} ====================")
    s = difflib.ndiff([t5], [t6])
    print('\n'.join(s))

# Verify all changed paragraphs are known and intentional:
# P0: Title
# P6: Abstract
# P7: Keywords
# P38: Hypotheses
# P64: §3.1 Plane
# P68: §3.2 Variance
# P133: §4.3 Variance
# P146: §4.5 Transitions
# P147: §4.5 2nd paragraph
# P178: §5.1 Principal findings
# P186: §5.4 Plane
# P187: §5.4 Dose & Input HF
# P215: §7 Conclusion
expected_p_indices = {0, 6, 7, 38, 64, 68, 133, 146, 147, 178, 186, 187, 215}
actual_p_indices = {idx for idx, _, _ in changed_p}
assert actual_p_indices == expected_p_indices, f"Mismatch in changed paragraphs: {actual_p_indices ^ expected_p_indices}"

# Verify tables
changed_tables = []
for t_idx in range(len(v5.tables)):
    tbl5 = v5.tables[t_idx]
    tbl6 = v6.tables[t_idx]
    for r_idx in range(len(tbl5.rows)):
        for c_idx in range(len(tbl5.rows[r_idx].cells)):
            c5 = tbl5.rows[r_idx].cells[c_idx].text.strip()
            c6 = tbl6.rows[r_idx].cells[c_idx].text.strip()
            if c5 != c6:
                changed_tables.append((t_idx, r_idx, c_idx, c5, c6))

print(f"\nTotal changed table cells: {len(changed_tables)}")
for t_idx, r_idx, c_idx, c5, c6 in changed_tables:
    print(f"Table {t_idx}, Row {r_idx}, Col {c_idx}:")
    print(f"  v5: {c5}")
    print(f"  v6: {c6}")

expected_tbl_cells = {(1, 0, 3), (1, 1, 3), (1, 2, 3), (1, 3, 3)}
actual_tbl_cells = {(t, r, c) for t, r, c, _, _ in changed_tables}
assert actual_tbl_cells == expected_tbl_cells, f"Mismatch in changed table cells: {actual_tbl_cells ^ expected_tbl_cells}"

print("\n>>> ALL CHECKS PASSED: ZERO UNINTENDED EDITS, ZERO NEW ERRORS <<<")
