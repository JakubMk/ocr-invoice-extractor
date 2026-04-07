from pydantic import BaseModel
from typing import Optional


class InvoiceDataResponse(BaseModel):
    seller_name: Optional[str]
    seller_address: str
    seller_nip: int
    total_amount: float

class InvoiceProcessResponse(InvoiceDataResponse):
    file_name: str
    process_id: int
    