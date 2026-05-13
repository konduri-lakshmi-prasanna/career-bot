"""
chain.py — RAG chain construction.
Builds the retrieval-augmented generation chain with a grounded prompt.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, RETRIEVER_K


# ── Singleton LLM ───────────────────────────────────────────────────────────
_llm = None


def get_llm() -> ChatGroq:
    """Return a cached LLM instance."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
        )
    return _llm


# ── Prompt Template ──────────────────────────────────────────────────────────
RAG_PROMPT = """You are CareerBot — an AI career guidance assistant.

You MUST answer ONLY using the document excerpts provided below in the CONTEXT section.
Do NOT use your own training knowledge. Do NOT guess or fabricate any information.

RULES:
- If CONTEXT is empty or says "[NO DOCUMENTS]", reply: "📂 No relevant information found in your uploaded documents. Please upload documents and rebuild the knowledge base."
- If CONTEXT exists but doesn't have enough info for the question, say so honestly and suggest uploading more documents.
- Quote or paraphrase directly from the CONTEXT. Cite which document section you are referencing.
- Use structured formatting with markdown headers and bullet points.

--- CONTEXT FROM UPLOADED DOCUMENTS ---
{context}
--- END CONTEXT ---

User Question: {question}

Answer (based strictly on the above context):"""


def _format_docs(docs) -> str:
    """Format retrieved documents into a labelled context string."""
    if not docs:
        return "[NO DOCUMENTS]"
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source_file", doc.metadata.get("source", "unknown"))
        parts.append(f"[Document {i} — {source}]:\n{doc.page_content}")
    return "\n\n".join(parts)


def build_chain(vectorstore):
    """
    Build the RAG chain from a FAISS vectorstore.

    Returns:
        Tuple of (chain, retriever).
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})
    llm       = get_llm()

    prompt = PromptTemplate(
        template=RAG_PROMPT,
        input_variables=["context", "question"],
    )

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever
