import logging
logger = logging.getLogger("ocr_app")

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.schemas.invoice import (
    InvoiceDebugResponse,
    InvoiceStoredResponse
)

from app.services.file_validation import validate_invoice_file
from app.services.invoice_service import process_invoice_file, UnsupportedContentTypeError
from app.services.llm_service import InvoiceParsingError
from app.services.invoice_repository import create_invoice_result, get_invoice_result

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/process", response_model=InvoiceStoredResponse | InvoiceDebugResponse)
async def process_invoice(file: UploadFile = Depends(validate_invoice_file),
                          debug: bool = False):
    # validate file type
    content = await file.read()

    logger.debug(f"[ROUTER] Received file: {file.filename}")
    logger.debug(f"[ROUTER] Content type: {file.content_type}")
    logger.debug(f"[ROUTER] File size: {len(content)}")

    # process file with ocr to extract text
    try:
        invoice_data, extraction_result = process_invoice_file(file_bytes=content,
                                                          content_type=file.content_type)
    except InvoiceParsingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except UnsupportedContentTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Invoice processing failed.") from exc
    

    stored_invoice = create_invoice_result(
        seller_name=invoice_data.seller_name,
        seller_address=invoice_data.seller_address,
        seller_nip=invoice_data.seller_nip,
        total_amount=invoice_data.total_amount,
        filename=file.filename,
        content_type=file.content_type,
        extraction_mode=extraction_result.extraction_mode
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
            extracted_text=extraction_result.text,
            extraction_mode=stored_invoice.extraction_mode,
        )
    
    return stored_invoice

@router.get("/{invoice_id}", response_model=InvoiceStoredResponse)
async def get_invoice(invoice_id: str):
    invoice = get_invoice_result(invoice_id)

    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    
    return invoice