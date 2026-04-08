import logging
logger = logging.getLogger("ocr_app")

from typing import BinaryIO, List, Tuple
from io import BytesIO

import numpy as np
import pymupdf
from dotenv import load_dotenv
from fastapi import File, HTTPException, UploadFile
from openai import OpenAI
from paddleocr import PaddleOCR
from PIL import Image, ImageFilter
from typing import Optional

from app.schemas.invoice import InvoiceDataResponse, TextExtractionResult

load_dotenv()

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}

ocr = PaddleOCR(lang='pl')
client = OpenAI()


async def validate_invoice_file(file: UploadFile = File(...)) -> UploadFile:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning("Unsupported file type: %s", file.content_type)
        raise HTTPException(status_code=415, detail="Unsupported file type. Only '.pdf', '.png', '.jpg' file types are supported.")
        
    content = await file.read()
    
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")
    
    file.file.seek(0)

    return file


def resize_keep_ratio(img: Image.Image, max_size: int = 512) -> Image.Image:
    w, h = img.size

    scale = min(max_size / w, max_size / h)
    new_size = (int(w * scale), int(h * scale))

    return img.resize(new_size)


def paddle_ocr(image: Image.Image) -> str:
    image = image.convert("RGB")

    image = resize_keep_ratio(image)
    # image = image.convert("L")
    image = image.filter(ImageFilter.SHARPEN)

    image_np = np.array(image)
    result = ocr.predict(image_np)

    text = ""
    page = result[0]
    texts = page['rec_texts']
    scores = page['rec_scores']
    boxes = page['rec_polys']

    for t, s, b in zip(texts, scores, boxes):
        # b is np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        coords = b.astype(int).tolist()
        text += f"{t:25} | {s:.3f} | {coords}"

    return text


def try_extract_text_from_pdf(file_stream: bytes) -> str:
    doc = pymupdf.open(stream=file_stream, filetype="pdf")

    pages_text = []

    for page in doc: # iterate the document pages
        text = page.get_text(sort=True)
        if text:
            logger.debug(f"[PDF] Located string length: {len(text)}")
            pages_text.append(text)

    full_text = "\n".join(pages_text).strip()
    logger.debug(f"[PDF] First 500 chars: \n{full_text[:500]}")
    return full_text


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


def render_pdf_to_images(file_stream: bytes, dpi: int = 200) -> List[Image.Image]:
    doc = pymupdf.open(stream=file_stream, filetype="pdf")
    matrix = pymupdf.Matrix(dpi/96, dpi/96)
    pages_img = []

    for page in doc:
        pix = page.get_pixmap(matrix=matrix)
        image = pix.pil_image()
        pages_img.append(image)

        logger.debug(f"[PDF RENDER] Rendered to image: {image.size}, mode={image.mode}")
    
    return pages_img


def run_ocr_on_pdf_pages(images: List[Image.Image]) -> str:
    page_texts = []

    for i, image in enumerate(images):
        logger.debug(f"[PDF OCR] Starting OCR for page {i}")
        page_text = paddle_ocr(image)
        
        if page_text.strip():
            page_texts.append(page_text)
    
    text = "\n".join(page_texts).strip()

    logger.debug(f"[PDF OCR] Total OCR text length: {len(text)}")
    logger.debug(f"[PDF OCR] First 500 chars:\n{text[:500]}")

    return text


def extract_text_from_image(file_bytes: bytes) -> TextExtractionResult:
    image = Image.open(BytesIO(file_bytes))
    text = paddle_ocr(image)
    return TextExtractionResult(text=text, extraction_mode="image_ocr")

# =============================================================================================

def extract_text_from_file(file_bytes: bytes, content_type: Optional[str]) -> TextExtractionResult:
    if content_type in {"image/png", "image/jpeg"}:
        return extract_text_from_image(file_bytes)
    
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    
    raise ValueError(f"Unsupported content type: {content_type}")


def extract_invoice_data(text: str) -> Optional[InvoiceDataResponse]:
    prompt = f"""
Wyciągnij następujące pola z tekstu faktury:
- nazwa sprzedawcy
- adres sprzedawcy
- NIP sprzedawcy
- kwota całkowita do zapłaty (float — tylko liczba, bez waluty, kropka jako separator dziesiętny)

Zwróć ściśle poprawny JSON zgodny z poniższym schematem:
{InvoiceDataResponse.model_json_schema()}

Tekst faktury:
{text}"""
    
    try:
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=prompt,
            text_format=InvoiceDataResponse
        )
        return response.output_parsed
    except Exception:
        return None