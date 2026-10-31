import sys
from pathlib import Path
import win32com.client
import pythoncom

def convert_to_pdf(docx_path, pdf_path):
    print(f"Converting {docx_path} -> {pdf_path}...")
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    try:
        doc = word.Documents.Open(str(docx_path.resolve()))
        # 17 corresponds to wdFormatPDF
        doc.SaveAs(str(pdf_path.resolve()), FileFormat=17)
        doc.Close()
        print(f"Successfully generated: {pdf_path} ({pdf_path.stat().st_size} bytes)")
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        raise
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    rev_docx = Path(r"c:\Users\jkgga\Downloads\brain\revision\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Revised.docx")
    rev_pdf = Path(r"c:\Users\jkgga\Downloads\brain\revision\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Revised.pdf")
    convert_to_pdf(rev_docx, rev_pdf)
    
    fmt_docx = Path(r"c:\Users\jkgga\Downloads\brain\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).docx")
    fmt_pdf = Path(r"c:\Users\jkgga\Downloads\brain\Brain_Tumour_MRI_Counterfactual_Audit_Manuscript_Format (1).pdf")
    convert_to_pdf(fmt_docx, fmt_pdf)

