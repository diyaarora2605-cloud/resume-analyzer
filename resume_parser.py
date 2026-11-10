from io import BytesIO
from pathlib import Path
import fitz
from docx import Document

MAX_FILE_BYTES = 5 * 1024 * 1024

class ResumeParseError(ValueError):
    """Raised when a resume cannot be safely parsed."""

def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    if not file_bytes:
        raise ResumeParseError("The uploaded file is empty.")
    if len(file_bytes) > MAX_FILE_BYTES:
        raise ResumeParseError("File exceeds the 5 MB upload limit.")
    suffix = Path(filename or "").suffix.lower()
    try:
        if suffix == ".pdf":
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                if doc.is_encrypted:
                    raise ResumeParseError("This PDF is password-protected. Upload an unlocked PDF.")
                pages = [page.get_text("text", sort=True) for page in doc]
                text = "\n".join(pages)
        elif suffix == ".docx":
            document = Document(BytesIO(file_bytes))
            chunks = [p.text for p in document.paragraphs if p.text.strip()]
            for table in document.tables:
                for row in table.rows:
                    chunks.append(" | ".join(cell.text.strip() for cell in row.cells))
            text = "\n".join(chunks)
        else:
            raise ResumeParseError("Unsupported file type. Upload a PDF or DOCX file.")
    except ResumeParseError:
        raise
    except Exception as exc:
        raise ResumeParseError("The file could not be read. It may be damaged or incorrectly formatted.") from exc
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not text:
        raise ResumeParseError("No readable text was found. Scanned/image-only PDFs are not supported; run OCR and upload a searchable PDF.")
    return text[:50000]
