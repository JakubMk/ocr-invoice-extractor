# OCR Invoice Extractor

End-to-end OCR + LLM pipeline for extracting structured data from invoices using FastAPI and OpenAI API.

## Overview

This project provides a backend API for processing invoices (PDF/images) and extracting structured data such as:

- seller name
- seller address
- seller NIP
- total amount

The pipeline combines OCR and LLM-based parsing to transform unstructured documents into clean JSON.

---

## How it works

1. Upload invoice (PDF / image)
2. OCR extracts raw text
3. LLM processes text and extracts structured data
4. API returns validated JSON

---

## Project structure
```bash
app/
├── main.py
├── routers/
├── services/
├── schemas/
```
---

## Run locally
```bash
pip install -r requirements.txt
python -m fastapi run app.main
```

```json
{
  "seller_name": "Example Company",
  "seller_address": "Some Street 1, Warsaw",
  "seller_nip": "1234567890",
  "total_amount": 1234.56
}
```