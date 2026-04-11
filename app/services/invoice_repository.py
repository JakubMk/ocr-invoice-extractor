from uuid import uuid4
from app.schemas.invoice import InvoiceStoredResponse
from app.services.invoice_db import get_db_connection


def create_invoice_result(
        seller_name: str | None,
        seller_address: str | None,
        seller_nip: str | None,
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
    query = """
INSERT INTO invoices (
    invoice_id,
    seller_name,
    seller_address,
    seller_nip,
    total_amount,
    filename,
    content_type,
    extraction_mode
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    invoice.invoice_id,
                    invoice.seller_name,
                    invoice.seller_address,
                    invoice.seller_nip,
                    invoice.total_amount,
                    invoice.filename,
                    invoice.content_type,
                    invoice.extraction_mode
                )
            )
        conn.commit()

    return invoice

def get_invoice_result(invoice_id: str) -> InvoiceStoredResponse | None:
    query = """
SELECT
    invoice_id,
    seller_name,
    seller_address,
    seller_nip,
    total_amount,
    filename,
    content_type,
    extraction_mode
FROM invoices
WHERE invoice_id = %s
"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (invoice_id,))
            row = cur.fetchone()
    
    if row is None:
        return None
    
    return InvoiceStoredResponse(
        invoice_id=str(row[0]),
        seller_name=row[1],
        seller_address=row[2],
        seller_nip=row[3],
        total_amount=row[4],
        filename=row[5],
        content_type=row[6],
        extraction_mode=row[7],
    )