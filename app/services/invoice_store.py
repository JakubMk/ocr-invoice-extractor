from uuid import uuid4
from typing import Optional
from app.schemas.invoice import InvoiceStoredResponse

INVOICE_STORE: dict[str, InvoiceStoredResponse] = {}

def save_invoice_data(invoice: InvoiceStoredResponse) -> InvoiceStoredResponse:
    INVOICE_STORE[invoice.invoice_id] = invoice
    return invoice

def create_and_save_invoice_data(
        seller_name: Optional[str],
        seller_address: str,
        seller_nip: int,
        total_amount: float,
        filename: str,
        content_type: str,
        extraction_mode: str
) -> InvoiceStoredResponse:
    invoice = InvoiceStoredResponse(
        invoice_id=str(uuid4()),
        seller_name=seller_name,
        seller_address=seller_address,
        seller_nip=seller_nip,
        total_amount=total_amount,
        filename=filename,
        content_type=content_type,
        extraction_mode=extraction_mode
    )
    INVOICE_STORE[invoice.invoice_id] = invoice
    return invoice

def get_invoice_data(
        invoice_id: str
        ) -> Optional[InvoiceStoredResponse]:
    return INVOICE_STORE.get(invoice_id)