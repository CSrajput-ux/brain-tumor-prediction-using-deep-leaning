"""Synchronize reports/result_ledger.csv and reports/manuscript_consistency_audit.csv with Table 3 and Table 4 values."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

# 1. Update result_ledger.csv
ledger_path = ROOT / "reports" / "result_ledger.csv"
df_l = pd.read_csv(ledger_path)

# Update RES-025, RES-026, RES-027 to primary Table 3 values
df_l.loc[df_l["result_id"] == "RES-025", ["reported_value", "notes"]] = [0.0492, "Table 3 primary (DeiT Method A, N=15); pooled-models ref=0.0337"]
df_l.loc[df_l["result_id"] == "RES-026", ["reported_value", "notes"]] = [0.0370, "Table 3 primary (DeiT Method A, N=15); pooled-models ref=0.0298"]
df_l.loc[df_l["result_id"] == "RES-027", ["reported_value", "notes"]] = [0.0690, "Table 3 primary (DeiT Method A, N=15); pooled-models ref=0.0582"]

# Update RES-028, RES-029, RES-030 to primary Table 4 values
df_l.loc[df_l["result_id"] == "RES-028", ["reported_value", "notes"]] = [0.672, "Table 4 primary (Cheng DeiT Method A, N=15, 67.2%); cross-dataset ref=0.350"]
df_l.loc[df_l["result_id"] == "RES-029", ["reported_value", "notes"]] = [0.098, "Table 4 primary (Cheng DeiT Method A, N=15, 9.8%); cross-dataset ref=0.331"]
df_l.loc[df_l["result_id"] == "RES-030", ["reported_value", "notes"]] = [3.602, "Table 4 primary (Cheng DeiT Method A, N=15, 360.2%); cross-dataset ref=0.151"]

df_l.to_csv(ledger_path, index=False)
print(f"Updated {ledger_path}")

# 2. Update manuscript_consistency_audit.csv
audit_path = ROOT / "reports" / "manuscript_consistency_audit.csv"
if audit_path.exists():
    df_a = pd.read_csv(audit_path)
    # Update claim and expected values
    for idx, row in df_a.iterrows():
        claim = str(row["Claim_or_Metric"])
        if "Axial" in claim:
            df_a.at[idx, "Claim_or_Metric"] = "BRISC Axial Mean Core Sensitivity (0.0492)"
            df_a.at[idx, "Value_in_Manuscript"] = "0.0492"
            df_a.at[idx, "Expected_Value_or_Formula"] = "0.0492"
            df_a.at[idx, "Notes_or_Source"] = "Table 3 (DeiT Method A, N=15); pooled reference 0.0337"
        elif "Coronal" in claim:
            df_a.at[idx, "Claim_or_Metric"] = "BRISC Coronal Mean Core Sensitivity (0.0370)"
            df_a.at[idx, "Value_in_Manuscript"] = "0.0370"
            df_a.at[idx, "Expected_Value_or_Formula"] = "0.0370"
            df_a.at[idx, "Notes_or_Source"] = "Table 3 (DeiT Method A, N=15); pooled reference 0.0298"
        elif "Sagittal" in claim:
            df_a.at[idx, "Claim_or_Metric"] = "BRISC Sagittal Mean Core Sensitivity (0.0690)"
            df_a.at[idx, "Value_in_Manuscript"] = "0.0690"
            df_a.at[idx, "Expected_Value_or_Formula"] = "0.0690"
            df_a.at[idx, "Notes_or_Source"] = "Table 3 (DeiT Method A, N=15); pooled reference 0.0582"
        elif "Glioma" in claim:
            df_a.at[idx, "Claim_or_Metric"] = "Cheng Glioma Margin-to-Core Ratio (67.2%)"
            df_a.at[idx, "Value_in_Manuscript"] = "67.2%"
            df_a.at[idx, "Expected_Value_or_Formula"] = "67.2%"
            df_a.at[idx, "Notes_or_Source"] = "Table 4 (Cheng DeiT Method A, N=15); cross-dataset pooled reference 35.0%"
        elif "Meningioma" in claim:
            df_a.at[idx, "Claim_or_Metric"] = "Cheng Meningioma Margin-to-Core Ratio (9.8%)"
            df_a.at[idx, "Value_in_Manuscript"] = "9.8%"
            df_a.at[idx, "Expected_Value_or_Formula"] = "9.8%"
            df_a.at[idx, "Notes_or_Source"] = "Table 4 (Cheng DeiT Method A, N=15); cross-dataset pooled reference 33.1%"
        elif "Pituitary" in claim:
            df_a.at[idx, "Claim_or_Metric"] = "Cheng Pituitary Margin-to-Core Ratio (360.2%)"
            df_a.at[idx, "Value_in_Manuscript"] = "360.2%"
            df_a.at[idx, "Expected_Value_or_Formula"] = "360.2%"
            df_a.at[idx, "Notes_or_Source"] = "Table 4 (Cheng DeiT Method A, N=15); cross-dataset pooled reference 15.1%"
        elif "BRISC DeiT" in claim and "Core" in claim:
            df_a.at[idx, "Claim_or_Metric"] = "BRISC DeiT-Small Telea Core Sensitivity"
            df_a.at[idx, "Value_in_Manuscript"] = "0.0517 (raw p=0.0320, holm p=0.0639 / 0.6072)"
            df_a.at[idx, "Expected_Value_or_Formula"] = "0.0517 (raw p=0.0320, 4-reg holm=0.0639, 32-family holm=0.6072)"
            df_a.at[idx, "Notes_or_Source"] = "Non-significant after family-wise correction under both 4-region and 32-family"

    df_a.to_csv(audit_path, index=False)
    print(f"Updated {audit_path}")
