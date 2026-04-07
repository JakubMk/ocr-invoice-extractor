import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.routers import invoices

# logging.basicConfig(filename="ocr_app.log",
#                         level=logging.DEBUG,
#                         format="{asctime}:{lineno}:{funcName}:{message}",
#                         style="{",
#                         datefmt="%H:%M %d-%m-%Y",
#                         force=True)

# logger = logging.getLogger(__name__)
logger = logging.getLogger("ocr_app")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("ocr_app.log")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("{asctime}:{levelname}:{name}:{lineno}:{funcName}:{message}",
                              style="{",
                              datefmt="%H:%M %d-%m-%Y")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = False

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def form_page():
    return """
    <html>
        <body>
            <h2>Wczytaj fakturę:</h2>
            <form action="/invoices/process" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit" value="Wczytaj">
            </form>
        </body>
    </html>
    """

app.include_router(invoices.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Catastrophic failure.")
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected server error."},
    )