import logging
logger = logging.getLogger("ocr_app")

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.schemas.invoice import InvoiceDataResponse
from app.services.invoice_service import (
    extract_invoice_data,
    extract_text_from_file,
    validate_invoice_file,
)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/process", response_model=InvoiceDataResponse)
async def process_invoice(file: UploadFile = Depends(validate_invoice_file)):
    # validate file type
    content = await file.read()

    # process file with ocr to extract text
    try:
        text = extract_text_from_file(file_bytes=content, content_type=file.content_type)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from file.")
    
    # retrive information from the invoice
    invoice_data = extract_invoice_data(text)

    if invoice_data is None:
        raise HTTPException(status_code=422, detail="Could not extract invoice data.")

    return invoice_data
