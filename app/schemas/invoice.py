from pydantic import BaseModel


class TextExtractionResult(BaseModel):
    text: str
    extraction_mode: str
    
class InvoiceDataResponse(BaseModel):
    seller_name: str | None = None
    seller_address: str | None = None
    seller_nip: str | None = None
    total_amount: float | None = None

class InvoiceStoredResponse(InvoiceDataResponse):
    invoice_id: str
    filename: str
    content_type: str
    extraction_mode: str

class InvoiceDebugResponse(InvoiceDataResponse):
    invoice_id: str
    filename: str
    content_type: str
    extracted_text: str
    extraction_mode: str
