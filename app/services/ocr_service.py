import logging
from dataclasses import dataclass
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageFilter

logger = logging.getLogger("ocr_app")

ocr = PaddleOCR(lang='pl')


@dataclass
class OCRrow:
    text: str
    score: float
    coords: list[list[int]]

@dataclass
class OCRResult:
    text: str
    rows: list[OCRrow]


def resize_keep_ratio(img: Image.Image, max_size: int = 512) -> Image.Image:
    w, h = img.size

    scale = min(max_size / w, max_size / h)
    new_size = (int(w * scale), int(h * scale))

    return img.resize(new_size)


def paddle_ocr(image: Image.Image) -> OCRResult:
    image = image.convert("RGB")

    image = resize_keep_ratio(image)
    image = image.filter(ImageFilter.SHARPEN)

    image_np = np.array(image)
    result = ocr.predict(image_np)

    if not result:
        logger.debug("[OCR] No OCR result returned.")
        return OCRResult(text="", rows=[])
    

    page = result[0]
    texts = page['rec_texts']
    scores = page['rec_scores']
    boxes = page['rec_polys']

    lines: list[OCRrow] = []
    plain_text: list[str] = []

    for t, s, b in zip(texts, scores, boxes):
        # b is np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        coords = b.astype(int).tolist()
        lines.append(OCRrow(text=t, score=float(s), coords=coords))
        plain_text.append(t)

    text =  "\n".join(plain_text).strip()

    logger.debug("[OCR] Extracted %d lines, total text length=%d", len(lines), len(text))
    logger.debug("[OCR] First 500 chars:\n%s", text[:500])

    return OCRResult(text=text, rows=lines)