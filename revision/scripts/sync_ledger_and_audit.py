"""Synchronize reports/result_ledger.csv and reports/manuscript_consistency_audit.csv with Table 3 and Table 4 values."""
import csv
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

# 1. Update result_ledger.csv using exact column 'value'
ledger_path = ROOT / "reports" / "result_ledger.csv"
if ledger_path.exists():
    df_l = pd.read_csv(ledger_path)
    df_l.loc[df_l["result_id"] == "RES-025", ["value", "notes"]] = ["0.0492", "Table 3 primary (DeiT Method A, N=15); pooled-models reference=0.0337"]
    df_l.loc[df_l["result_id"] == "RES-026", ["value", "notes"]] = ["0.0370", "Table 3 primary (DeiT Method A, N=15); pooled-models reference=0.0298"]
    df_l.loc[df_l["result_id"] == "RES-027", ["value", "notes"]] = ["0.0690", "Table 3 primary (DeiT Method A, N=15); pooled-models reference=0.0582"]
    df_l.loc[df_l["result_id"] == "RES-028", ["value", "notes"]] = ["0.672", "Table 4 primary (Cheng DeiT Method A, N=15, 67.2%); cross-dataset pooled reference=0.350"]
    df_l.loc[df_l["result_id"] == "RES-029", ["value", "notes"]] = ["0.098", "Table 4 primary (Cheng DeiT Method A, N=15, 9.8%); cross-dataset pooled reference=0.331"]
    df_l.loc[df_l["result_id"] == "RES-030", ["value", "notes"]] = ["3.602", "Table 4 primary (Cheng DeiT Method A, N=15, 360.2%); cross-dataset pooled reference=0.151"]
    df_l.to_csv(ledger_path, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Updated {ledger_path}")

# 2. Update manuscript_consistency_audit.csv using exact columns:
# ['claim_or_value', 'manuscript_locations', 'source_of_truth', 'observed_values', 'consistency_status', 'resolution', 'verification_notes']
audit_path = ROOT / "reports" / "manuscript_consistency_audit.csv"
if audit_path.exists():
    df_a = pd.read_csv(audit_path)
    for idx, row in df_a.iterrows():
        claim = str(row["claim_or_value"])
        if "Axial" in claim:
            df_a.at[idx, "observed_values"] = "0.0492"
            df_a.at[idx, "resolution"] = "Table 3 primary (DeiT Method A, N=15); pooled-models ref=0.0337"
        elif "Coronal" in claim:
            df_a.at[idx, "observed_values"] = "0.0370"
            df_a.at[idx, "resolution"] = "Table 3 primary (DeiT Method A, N=15); pooled-models ref=0.0298"
        elif "Sagittal" in claim:
            df_a.at[idx, "observed_values"] = "0.0690"
            df_a.at[idx, "resolution"] = "Table 3 primary (DeiT Method A, N=15); pooled-models ref=0.0582"
        elif "Glioma" in claim:
            df_a.at[idx, "observed_values"] = "67.2%"
            df_a.at[idx, "resolution"] = "Table 4 primary (Cheng DeiT Method A, N=15); cross-dataset pooled ref=35.0%"
        elif "Meningioma" in claim:
            df_a.at[idx, "observed_values"] = "9.8%"
            df_a.at[idx, "resolution"] = "Table 4 primary (Cheng DeiT Method A, N=15); cross-dataset pooled ref=33.1%"
        elif "Pituitary" in claim:
            df_a.at[idx, "observed_values"] = "360.2%"
            df_a.at[idx, "resolution"] = "Table 4 primary (Cheng DeiT Method A, N=15); cross-dataset pooled ref=15.1%"
    df_a.to_csv(audit_path, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Updated {audit_path}")
