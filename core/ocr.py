"""
ocr.py — OCR (Optical Character Recognition) support for CareerBot.

Handles:
  • Scanned / image-based PDFs  → converts pages to images → Tesseract OCR
  • Uploaded image files (JPG, JPEG, PNG, TIFF, BMP, WEBP)
  • Auto-detect: if a PDF yields < MIN_TEXT_CHARS of text it is treated as scanned

Dependencies (add to requirements.txt):
    pytesseract
    pdf2image
    Pillow

System dependency (install once):
    sudo apt-get install -y tesseract-ocr poppler-utils
    # For Hindi/regional Indian languages (optional):
    # sudo apt-get install -y tesseract-ocr-hin tesseract-ocr-tel ...
"""

from __future__ import annotations

import os
import io
from pathlib import Path
from typing import List, Tuple

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from langchain_core.documents import Document

# ── Constants ─────────────────────────────────────────────────────────────────

# If a PDF page has fewer than this many characters after normal text extraction,
# it is considered scanned/image-based and handed to OCR.
MIN_TEXT_CHARS = 50

# Tesseract language string.  "eng" covers English.
# Add "+hin" or "+tel" etc. if regional language packs are installed.
TESSERACT_LANG = "eng"

# DPI used when rasterising PDF pages.  Higher = better quality but slower.
PDF_RENDER_DPI = 250


# ── Image extensions supported ────────────────────────────────────────────────
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp"}


def is_image_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


# ── Internal helpers ──────────────────────────────────────────────────────────

def _preprocess_image(img: Image.Image) -> Image.Image:
    """
    Apply light pre-processing to improve Tesseract accuracy.
    Steps: convert to greyscale → sharpen → increase contrast.
    """
    img = img.convert("L")                          # greyscale
    img = img.filter(ImageFilter.SHARPEN)           # sharpen edges
    img = ImageEnhance.Contrast(img).enhance(2.0)   # boost contrast
    return img


def _ocr_image(img: Image.Image) -> str:
    """Run Tesseract on a single PIL Image and return extracted text."""
    processed = _preprocess_image(img)
    text = pytesseract.image_to_string(processed, lang=TESSERACT_LANG)
    return text.strip()


# ── Public API ────────────────────────────────────────────────────────────────

def ocr_image_file(filepath: str) -> Tuple[List[Document], List[str]]:
    """
    Run OCR on a standalone image file (JPG, PNG, TIFF, BMP, WEBP).

    Returns:
        (documents, errors)
        documents — one Document with the full extracted text
        errors    — list of error strings (empty on success)
    """
    filename = Path(filepath).name
    try:
        img  = Image.open(filepath)
        text = _ocr_image(img)
        if not text:
            return [], [f"OCR returned no text from image: {filename}"]
        doc = Document(
            page_content=text,
            metadata={"source_file": filename, "page": 0, "ocr": True},
        )
        return [doc], []
    except Exception as exc:
        return [], [f"OCR failed for {filename}: {exc}"]


def ocr_scanned_pdf(filepath: str) -> Tuple[List[Document], List[str]]:
    """
    Rasterise every page of a scanned PDF and run OCR on each page.

    Returns:
        (documents, errors)
        documents — one Document per page
        errors    — any pages that failed
    """
    # pdf2image is imported lazily so the app still starts if poppler is absent
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return [], ["pdf2image not installed. Run: pip install pdf2image"]

    filename = Path(filepath).name
    documents: List[Document] = []
    errors: List[str] = []

    try:
        pages = convert_from_path(filepath, dpi=PDF_RENDER_DPI)
    except Exception as exc:
        return [], [f"Could not rasterise {filename}: {exc}"]

    for page_num, page_img in enumerate(pages, start=1):
        try:
            text = _ocr_image(page_img)
            if text:
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source_file": filename,
                        "page": page_num,
                        "ocr": True,
                    },
                ))
        except Exception as exc:
            errors.append(f"{filename} page {page_num}: {exc}")

    return documents, errors


def is_scanned_pdf(filepath: str) -> bool:
    """
    Quick check: attempt normal text extraction from the first 3 pages.
    If total extracted text < MIN_TEXT_CHARS, the PDF is likely scanned.
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        sample_text = ""
        for page in reader.pages[:3]:
            sample_text += page.extract_text() or ""
        return len(sample_text.strip()) < MIN_TEXT_CHARS
    except Exception:
        return True   # if extraction fails, assume scanned
