import logging
logger = logging.getLogger("ocr_app")

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from typing import Union

from app.schemas.invoice import (
    InvoiceDataResponse,
    InvoiceDebugResponse,
    InvoiceStoredResponse
)

from app.services.invoice_service import (
    extract_invoice_data,
    extract_text_from_file,
    validate_invoice_file,
)

from app.services.invoice_store import (
    create_and_save_invoice_data,
    get_invoice_data
)

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/process", response_model=Union[InvoiceStoredResponse, InvoiceDebugResponse])
async def process_invoice(file: UploadFile = Depends(validate_invoice_file), debug: bool = False):
    # validate file type
    content = await file.read()

    logger.debug(f"[ROUTER] Received file: {file.filename}")
    logger.debug(f"[ROUTER] Content type: {file.content_type}")
    logger.debug(f"[ROUTER] File size: {len(content)}")

    # process file with ocr to extract text
    try:
        extraction_result = extract_text_from_file(file_bytes=content, content_type=file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    text = extraction_result.text
    extraction_mode = extraction_result.extraction_mode

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from file.")
    
    # retrive information from the invoice
    invoice_data = extract_invoice_data(text)

    if invoice_data is None:
        raise HTTPException(status_code=422, detail="Could not extract invoice data.")

    stored_invoice = create_and_save_invoice_data(
        seller_name=invoice_data.seller_name,
        seller_address=invoice_data.seller_address,
        seller_nip=invoice_data.seller_nip,
        total_amount=invoice_data.total_amount,
        filename=file.filename,
        content_type=file.content_type,
        extraction_mode=extraction_mode
        )

    if debug:
        return InvoiceDebugResponse(
            invoice_id=stored_invoice.invoice_id,
            seller_name=stored_invoice.seller_name,
            seller_address=stored_invoice.seller_address,
            seller_nip=stored_invoice.seller_nip,
            total_amount=stored_invoice.total_amount,
            filename=stored_invoice.filename,
            content_type=stored_invoice.content_type,
            extracted_text=text,
            extraction_mode=stored_invoice.extraction_mode,
        )
    
    return stored_invoice

@router.get("/{invoice_id}", response_model=InvoiceStoredResponse)
async def get_invoice(invoice_id: str):
    invoice = get_invoice_data(invoice_id)

    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    
    return invoice