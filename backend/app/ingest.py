import io
import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)

_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

# Below this many chars, a PDF page is considered scanned/image-only and
# sent to Tesseract OCR instead of trusting pypdf's (empty) output.
OCR_MIN_CHARS_PER_PAGE = 50


def ingest_text(text: str, source: str) -> int:
    chunks = _splitter.split_text(text)
    docs = [
        Document(page_content=chunk, metadata={"source": source, "chunk": i})
        for i, chunk in enumerate(chunks)
    ]

    if not docs:
        return 0

    get_vectorstore().add_documents(docs)
    return len(docs)


def _ocr_pdf_page(content: bytes, page_number: int) -> str:
    """Render one PDF page to image and OCR it with Tesseract.

    Imported lazily so the app still runs when tesseract/poppler or the
    python bindings aren't installed — caller catches and logs instead.
    """
    import pytesseract
    from pdf2image import convert_from_bytes

    images = convert_from_bytes(
        content, first_page=page_number, last_page=page_number, dpi=300
    )
    if not images:
        return ""
    return pytesseract.image_to_string(images[0]) or ""


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if len(text) >= OCR_MIN_CHARS_PER_PAGE:
            pages.append(text)
            continue
        # Scanned/image page — pypdf gives nothing useful, try OCR.
        try:
            ocr_text = _ocr_pdf_page(content, i).strip()
        except Exception as exc:  # noqa: BLE001 — missing binary, corrupt page, etc.
            logger.warning("OCR fallback failed on page %d: %s", i, exc)
            ocr_text = ""
        pages.append(ocr_text or text)
    return "\n".join(pages)


def _ocr_image(content: bytes) -> str:
    """OCR for direct image uploads (.png/.jpg)."""
    import io as _io

    import pytesseract
    from PIL import Image

    return pytesseract.image_to_string(Image.open(_io.BytesIO(content))) or ""


def extract_text_from_upload(filename: str, content: bytes) -> str:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        return extract_pdf_text(content)
    if lowered.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        try:
            return _ocr_image(content).strip()
        except Exception as exc:  # noqa: BLE001 — corrupt image, missing tesseract
            logger.warning("Image OCR failed for %s: %s", filename, exc)
            return ""
    return content.decode("utf-8", errors="replace")
