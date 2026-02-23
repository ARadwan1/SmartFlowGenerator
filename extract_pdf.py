import sys
import subprocess

def ensure_pymupdf():
    try:
        import fitz
        return fitz
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
        import fitz
        return fitz

def extract_pdf(pdf_path, txt_path):
    fitz = ensure_pymupdf()
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n\n"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == '__main__':
    extract_pdf(sys.argv[1], sys.argv[2])
