import os
import shutil

art_dir = r"C:\Users\jkgga\.gemini\antigravity\brain\d6adce8c-23ce-4309-8199-0aa195f5f78c"
src_files = [
    r"c:\Users\jkgga\Downloads\brain\brain _tumar_research.docx",
    r"c:\Users\jkgga\Downloads\brain\brain _tumar_research.pdf",
    r"c:\Users\jkgga\Downloads\brain\brain _tumar_research_Revised.docx",
    r"c:\Users\jkgga\Downloads\brain\brain _tumar_research_Revised.pdf",
    r"c:\Users\jkgga\Downloads\brain\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).docx",
    r"c:\Users\jkgga\Downloads\brain\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).pdf",
    r"c:\Users\jkgga\Downloads\brain\revision\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Revised.docx",
    r"c:\Users\jkgga\Downloads\brain\revision\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Revised.pdf",
    r"c:\Users\jkgga\Downloads\brain\paper\manuscript.pdf",
    r"c:\Users\jkgga\Downloads\brain\Brain_MRI_Research_Paper_Final.pdf",
    r"c:\Users\jkgga\Downloads\brain\reports\sample_flow.csv",
    r"c:\Users\jkgga\Downloads\brain\reports\split_and_leakage_report.md",
    r"c:\Users\jkgga\Downloads\brain\reports\result_ledger.csv",
    r"c:\Users\jkgga\Downloads\brain\reports\manuscript_consistency_audit.csv",
    r"c:\Users\jkgga\Downloads\brain\revision\tables\table_s3_secondary_and_clustered_statistics.csv",
    r"c:\Users\jkgga\Downloads\brain\reports\sham_geometry_report.md",
    r"c:\Users\jkgga\Downloads\brain\reports\secondary_robustness_report.md",
]

for src in src_files:
    if os.path.exists(src):
        dst = os.path.join(art_dir, os.path.basename(src))
        shutil.copy2(src, dst)
        print(f"Copied: {os.path.basename(src)} ({os.path.getsize(dst):,} bytes)")
    else:
        print(f"Source not found: {src}")

print("All deliverables copied to artifact directory.")

