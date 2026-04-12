from fastapi import File, HTTPException, UploadFile
import logging

logger = logging.getLogger("ocr_app")

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}

async def validate_invoice_file(file: UploadFile = File(...)) -> UploadFile:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning("Unsupported file type: %s", file.content_type)
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Only '.pdf', '.png', '.jpg' file types are supported."
            )
        
    content = await file.read()
    
    if not content:
        logger.warning("Empty file upload: %s", file.filename)
        raise HTTPException(
            status_code=400,
            detail="Empty file."
            )
    
    file.file.seek(0)

    return file