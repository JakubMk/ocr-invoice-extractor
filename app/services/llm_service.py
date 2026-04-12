import logging
from dotenv import load_dotenv
from openai import OpenAI
from app.schemas.invoice import InvoiceDataResponse

load_dotenv()
logger = logging.getLogger("ocr_app")
client = OpenAI()


class InvoiceParsingError(Exception):
    pass

def build_invoice_prompt(text: str) -> str:
    return f"""
Wyciągnij następujące pola z tekstu faktury:
- nazwa sprzedawcy
- adres sprzedawcy
- NIP sprzedawcy
- kwota całkowita do zapłaty (float — tylko liczba, bez waluty, kropka jako separator dziesiętny)

Zwróć ściśle poprawny JSON zgodny z poniższym schematem:
{InvoiceDataResponse.model_json_schema()}

Tekst faktury:
{text}""".strip()


def extract_invoice_data(text: str) -> InvoiceDataResponse:
    if not text.strip():
        raise InvoiceParsingError("Cannot parse invoice data from empty text.")
    
    prompt = build_invoice_prompt(text)

    try:
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=prompt,
            text_format=InvoiceDataResponse
        )
        parsed = response.output_parsed

        if parsed is None:
            raise InvoiceParsingError("LLM returned no parsed output.")
        
        return parsed
    except Exception as exc:
        logger.exception("Invoice parsing failed.")
        raise InvoiceParsingError("Failed to parse invoice data.") from exc