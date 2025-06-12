from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from transformers import pipeline
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from typing import Optional
import uvicorn

app = FastAPI()

# Helper: extract text from PDF (with OCR fallback)
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        full_text += page.get_text()
    pdf_document.close()
    if not full_text.strip():
        # OCR fallback
        images = convert_from_bytes(pdf_bytes)
        for image in images:
            full_text += pytesseract.image_to_string(image) + "\n"
    return full_text

@app.post("/summarize")
async def summarize(
    file: UploadFile = File(...),
    model_name: str = Form("t5-small"),
    max_length: int = Form(150),
    min_length: int = Form(40)
):
    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)
    if not text.strip():
        return JSONResponse({"error": "No extractable text found in PDF."}, status_code=400)
    summarizer = pipeline("summarization", model=model_name)
    summary = summarizer(text[:2000], max_length=max_length, min_length=min_length, do_sample=False)
    return {"summary": summary[0]['summary_text']}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
