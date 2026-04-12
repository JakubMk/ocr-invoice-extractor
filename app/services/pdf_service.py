import logging
import pymupdf
from PIL import Image

from app.schemas.invoice import TextExtractionResult
from app.services.ocr_service import paddle_ocr

logger = logging.getLogger("ocr_app")


def try_extract_text_from_pdf(file_stream: bytes) -> str:
    doc = pymupdf.open(stream=file_stream, filetype="pdf")

    pages_text: list[str] = []

    for page in doc: # iterate the document pages
        text = page.get_text(sort=True)
        if text:
            logger.debug(f"[PDF TEXT] Located string length: {len(text)}")
            pages_text.append(text)

    full_text = "\n".join(pages_text).strip()
    logger.debug(f"[PDF TEXT] First 500 chars: \n{full_text[:500]}")
    return full_text


def render_pdf_to_images(file_stream: bytes, dpi: int = 200) -> list[Image.Image]:
    doc = pymupdf.open(stream=file_stream, filetype="pdf")
    matrix = pymupdf.Matrix(dpi/96, dpi/96)
    pages_img: list[Image.Image] = []

    for page in doc:
        pix = page.get_pixmap(matrix=matrix)
        image = pix.pil_image()
        pages_img.append(image)

        logger.debug(f"[PDF RENDER] Rendered to image: {image.size}, mode={image.mode}")
    
    return pages_img


def run_ocr_on_pdf_pages(images: list[Image.Image]) -> str:
    page_texts: list[str] = []

    for i, image in enumerate(images, start=1):
        logger.debug(f"[PDF OCR] Starting OCR for page {i}")
        ocr_result = paddle_ocr(image)
        
        if ocr_result.text.strip():
            page_texts.append(ocr_result.text)
    
    text = "\n".join(page_texts).strip()

    logger.debug("[PDF OCR] Total OCR text length: %d", len(text))
    logger.debug("[PDF OCR] First 500 chars:\n%s", text[:500])

    return text


def extract_text_from_pdf(file_stream: bytes) -> TextExtractionResult:
    text = try_extract_text_from_pdf(file_stream)

    if text.strip():
        logger.debug("[PDF] Used embedded text extraction.")
        return TextExtractionResult(text=text, extraction_mode="pdf_text")

    logger.debug("[PDF] Embedded text empty, switching to OCR fallback.")

    images = render_pdf_to_images(file_stream)
    text = run_ocr_on_pdf_pages(images)

    if text.strip():
        logger.debug("[PDF] Used OCR extraction.")
        return TextExtractionResult(text=text, extraction_mode="pdf_ocr")
    
    logger.debug("[PDF] No text extracted from PDF.")

    return TextExtractionResult(text="", extraction_mode="pdf_ocr")
