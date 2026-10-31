"""Properly format reports/result_ledger.csv and update values with Table 3 and Table 4."""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]
ledger_path = ROOT / "reports" / "result_ledger.csv"

lines = ledger_path.read_text(encoding="utf-8").splitlines()
header = lines[0].split(",")

rows = []
for line in lines[1:]:
    if not line.strip():
        continue
    # parse first 16 fields, remainder is notes
    parts = line.split(",")
    if len(parts) > 17:
        fixed = parts[:16] + [",".join(parts[16:])]
    else:
        fixed = parts
    rows.append(fixed)

for r in rows:
    res_id = r[0]
    if res_id == "RES-025":
        r[2] = "0.0492"
        r[16] = "Table 3 primary (DeiT Method A, N=15); pooled-models reference=0.0337"
    elif res_id == "RES-026":
        r[2] = "0.0370"
        r[16] = "Table 3 primary (DeiT Method A, N=15); pooled-models reference=0.0298"
    elif res_id == "RES-027":
        r[2] = "0.0690"
        r[16] = "Table 3 primary (DeiT Method A, N=15); pooled-models reference=0.0582"
    elif res_id == "RES-028":
        r[2] = "0.672"
        r[16] = "Table 4 primary (Cheng DeiT Method A, N=15, 67.2%); cross-dataset pooled reference=0.350"
    elif res_id == "RES-029":
        r[2] = "0.098"
        r[16] = "Table 4 primary (Cheng DeiT Method A, N=15, 9.8%); cross-dataset pooled reference=0.331"
    elif res_id == "RES-030":
        r[2] = "3.602"
        r[16] = "Table 4 primary (Cheng DeiT Method A, N=15, 360.2%); cross-dataset pooled reference=0.151"

with open(ledger_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Successfully formatted and updated {ledger_path}")

# Now update reports/manuscript_consistency_audit.csv
audit_path = ROOT / "reports" / "manuscript_consistency_audit.csv"
if audit_path.exists():
    a_lines = audit_path.read_text(encoding="utf-8").splitlines()
    a_header = a_lines[0].split(",")
    a_rows = []
    for line in a_lines[1:]:
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) > 7:
            fixed = parts[:6] + [",".join(parts[6:])]
        else:
            fixed = parts
        a_rows.append(fixed)

    for r in a_rows:
        claim = r[0]
        if "Axial" in claim:
            r[0] = "BRISC Axial Mean Core Sensitivity (0.0492)"
            r[3] = "0.0492"
            r[5] = "Table 3 (DeiT Method A, N=15); pooled reference 0.0337"
        elif "Coronal" in claim:
            r[0] = "BRISC Coronal Mean Core Sensitivity (0.0370)"
            r[3] = "0.0370"
            r[5] = "Table 3 (DeiT Method A, N=15); pooled reference 0.0298"
        elif "Sagittal" in claim:
            r[0] = "BRISC Sagittal Mean Core Sensitivity (0.0690)"
            r[3] = "0.0690"
            r[5] = "Table 3 (DeiT Method A, N=15); pooled reference 0.0582"
        elif "Glioma" in claim:
            r[0] = "Cheng Glioma Margin-to-Core Ratio (67.2%)"
            r[3] = "67.2%"
            r[5] = "Table 4 (Cheng DeiT Method A, N=15); cross-dataset pooled reference 35.0%"
        elif "Meningioma" in claim:
            r[0] = "Cheng Meningioma Margin-to-Core Ratio (9.8%)"
            r[3] = "9.8%"
            r[5] = "Table 4 (Cheng DeiT Method A, N=15); cross-dataset pooled reference 33.1%"
        elif "Pituitary" in claim:
            r[0] = "Cheng Pituitary Margin-to-Core Ratio (360.2%)"
            r[3] = "360.2%"
            r[5] = "Table 4 (Cheng DeiT Method A, N=15); cross-dataset pooled reference 15.1%"
        elif "BRISC DeiT" in claim and "Core" in claim:
            r[0] = "BRISC DeiT-Small Telea Core Sensitivity"
            r[3] = "0.0517 (raw p=0.0320, holm p=0.0639 / 0.6072)"
            r[5] = "Non-significant after family-wise correction under both 4-region (p=0.0639) and 32-family (p=0.6072)"

    with open(audit_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(a_header)
        writer.writerows(a_rows)

    print(f"Successfully formatted and updated {audit_path}")

