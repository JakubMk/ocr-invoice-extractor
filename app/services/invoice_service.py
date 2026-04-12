import logging
from io import BytesIO
from PIL import Image
from app.schemas.invoice import TextExtractionResult, InvoiceDataResponse, InvoiceStoredResponse
from app.services.ocr_service import paddle_ocr
from app.services.pdf_service import extract_text_from_pdf
from app.services.llm_service import extract_invoice_data

logger = logging.getLogger("ocr_app")

class UnsupportedContentTypeError(Exception):
    pass


def extract_text_from_image(file_bytes: bytes) -> TextExtractionResult:
    image = Image.open(BytesIO(file_bytes))
    ocr_result = paddle_ocr(image)
    return TextExtractionResult(text=ocr_result.text, extraction_mode="image_ocr")


def extract_text_from_file(file_bytes: bytes, content_type: str) -> TextExtractionResult:
    if content_type in {"image/png", "image/jpeg"}:
        return extract_text_from_image(file_bytes)
    
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    
    raise UnsupportedContentTypeError(f"Unsupported content type: {content_type}")


def process_invoice_file(file_bytes: bytes,
                    content_type: str) -> tuple[InvoiceDataResponse,
                                                TextExtractionResult]:
    logger.debug("Przed wykonaniem ekstrakcji tekstu")
    extraction_result = extract_text_from_file(file_bytes, content_type)
    logger.debug("Przed wykonaniem LLM")
    invoice_data = extract_invoice_data(extraction_result.text)
    return invoice_data, extraction_result