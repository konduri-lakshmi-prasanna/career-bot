"""
loaders.py — Document loading logic.

Handles:
  • Normal PDFs (text-based)          → PyPDFLoader
  • Scanned / image-based PDFs        → ocr.ocr_scanned_pdf()
  • TXT files                         → TextLoader
  • Image files (JPG, PNG, TIFF …)    → ocr.ocr_image_file()

Auto-detection: If a PDF yields fewer than MIN_TEXT_CHARS characters it is
automatically rerouted through the OCR pipeline.
"""

import os
from typing import List, Optional, Tuple

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from core.config import DATA_FOLDER
from core.ocr import (
    is_scanned_pdf,
    is_image_file,
    ocr_scanned_pdf,
    ocr_image_file,
    IMAGE_EXTENSIONS,
)


# ── Supported extensions (used by the sidebar uploader) ──────────────────────
SUPPORTED_EXTENSIONS = {".pdf", ".txt"} | IMAGE_EXTENSIONS


def load_documents(
    only_files: Optional[List[str]] = None,
) -> Tuple[List[Document], List[str]]:
    """
    Load documents from the data folder.

    Args:
        only_files: If provided, only load these specific filenames.
                    Otherwise, load all supported files in DATA_FOLDER.

    Returns:
        (documents, errors)
        documents — list of LangChain Document objects with source_file metadata
        errors    — list of human-readable error strings
    """
    documents: List[Document] = []
    errors: List[str] = []

    target_files = only_files or os.listdir(DATA_FOLDER)

    for filename in target_files:
        filepath = os.path.join(DATA_FOLDER, filename)
        if not os.path.exists(filepath):
            continue

        ext = os.path.splitext(filename)[1].lower()

        # ── Image file → OCR ─────────────────────────────────────────────────
        if is_image_file(filename):
            docs, errs = ocr_image_file(filepath)
            errors.extend(errs)
            documents.extend(docs)
            continue

        # ── PDF ──────────────────────────────────────────────────────────────
        if ext == ".pdf":
            if is_scanned_pdf(filepath):
                # Scanned PDF → rasterise pages → Tesseract OCR
                docs, errs = ocr_scanned_pdf(filepath)
                errors.extend(errs)
                documents.extend(docs)
            else:
                # Normal text-based PDF → PyPDFLoader
                try:
                    loader = PyPDFLoader(filepath)
                    loaded = loader.load()
                    for doc in loaded:
                        doc.metadata["source_file"] = filename
                        doc.metadata["ocr"] = False
                    documents.extend(loaded)
                except Exception as exc:
                    errors.append(f"PyPDFLoader failed for {filename}: {exc}")
            continue

        # ── TXT ──────────────────────────────────────────────────────────────
        if ext == ".txt":
            try:
                loader = TextLoader(filepath, encoding="utf-8")
                loaded = loader.load()
                for doc in loaded:
                    doc.metadata["source_file"] = filename
                    doc.metadata["ocr"] = False
                documents.extend(loaded)
            except Exception as exc:
                errors.append(f"TextLoader failed for {filename}: {exc}")
            continue

        # ── Unknown / unsupported ─────────────────────────────────────────────
        # Silently skip; the uploader already restricts accepted types.

    return documents, errors


def describe_file_type(filename: str) -> str:
    """Return a short human-readable label for display in the sidebar."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return "📕 PDF"
    if ext == ".txt":
        return "📄 TXT"
    if ext in IMAGE_EXTENSIONS:
        return "🖼️ Image (OCR)"
    return "📎 File"
