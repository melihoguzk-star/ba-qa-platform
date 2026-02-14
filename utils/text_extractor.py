"""BRD dosyasından text çıkarma: PDF, DOCX, TXT."""
import io

def extract_text(uploaded_file) -> str:
    """Streamlit UploadedFile'dan text çıkarır."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    uploaded_file.seek(0)

    if name.endswith(".pdf"):
        return _extract_pdf(raw)
    elif name.endswith(".docx"):
        return _extract_docx(raw)
    elif name.endswith(".txt"):
        return raw.decode("utf-8", errors="replace")
    else:
        return raw.decode("utf-8", errors="replace")


def _extract_pdf(raw: bytes) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(io.BytesIO(raw))
    pages = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            pages.append(t)
    return "\n\n".join(pages)


def _extract_docx(raw: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(raw))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)
