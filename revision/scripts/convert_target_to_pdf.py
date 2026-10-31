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
    root = Path(r"c:\Users\jkgga\Downloads\brain")
    docx_p = root / "brain _tumar_research.docx"
    pdf_p = root / "brain _tumar_research.pdf"
    convert_to_pdf(docx_p, pdf_p)
    
    rev_docx_p = root / "brain _tumar_research_Revised.docx"
    rev_pdf_p = root / "brain _tumar_research_Revised.pdf"
    convert_to_pdf(rev_docx_p, rev_pdf_p)

