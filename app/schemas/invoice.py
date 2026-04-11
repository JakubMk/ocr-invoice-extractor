from pydantic import BaseModel


class TextExtractionResult(BaseModel):
    text: str
    extraction_mode: str
    
class InvoiceDataResponse(BaseModel):
    seller_name: str
    seller_address: str
    seller_nip: int
    total_amount: float

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
    