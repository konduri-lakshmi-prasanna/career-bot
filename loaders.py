"""
loaders.py — Document loading logic.
Handles reading PDF and TXT files from the data folder.
"""

import os
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from config import DATA_FOLDER


def load_documents(only_files: Optional[List[str]] = None) -> List[Document]:
    """
    Load documents from the data folder.

    Args:
        only_files: If provided, only load these specific filenames.
                    Otherwise, load all PDF/TXT files in DATA_FOLDER.

    Returns:
        List of LangChain Document objects with source_file metadata.
    """
    documents = []
    errors    = []

    target_files = only_files or os.listdir(DATA_FOLDER)

    for filename in target_files:
        filepath = os.path.join(DATA_FOLDER, filename)
        if not os.path.exists(filepath):
            continue

        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            elif filename.endswith(".txt"):
                loader = TextLoader(filepath, encoding="utf-8")
            else:
                continue

            loaded = loader.load()

            # Tag each document with its source filename
            for doc in loaded:
                doc.metadata["source_file"] = filename

            documents.extend(loaded)

        except Exception as e:
            errors.append((filename, str(e)))

    return documents, errors
