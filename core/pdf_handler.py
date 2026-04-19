# core/pdf_handler.py
#Handles PDF upload and text extraction.
import pdfplumber
import io

def extract_text_from_pdf(uploaded_file):
    """Extract raw text from uploaded PDF file."""
    text = ""
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()
