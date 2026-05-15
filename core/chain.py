"""
chain.py — RAG chain construction.

The chain object returned by build_chain() is kept for compatibility with
the rest of the codebase but actual invocation goes through ask() which
handles memory injection and works with both FAISS and HybridRetriever.
"""

from typing import List, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from core.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    RETRIEVER_K,
    RETRIEVAL_MODE,
)
from core.prompts import RAG_PROMPT
from core.memory import format_history


# ── Singleton LLM ─────────────────────────────────────────────────────────────
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


def _format_docs(docs) -> str:
    """Format retrieved documents into a labelled context string."""
    if not docs:
        return "[NO DOCUMENTS]"
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source_file", doc.metadata.get("source", "unknown"))
        parts.append(f"[Document {i} — {source}]:\n{doc.page_content}")
    return "\n\n".join(parts)


def build_chain(vectorstore, all_chunks: Optional[List[Document]] = None):
    """
    Build the RAG chain from a FAISS vectorstore.

    Args:
        vectorstore: FAISS vectorstore object.
        all_chunks:  Full list of Document chunks — required for hybrid search.
                     If None, falls back to pure vector retrieval.

    Returns:
        Tuple of (chain, retriever).
        chain is a simple callable wrapper — use ask() for actual invocation.
    """
    # ── Choose retriever ──────────────────────────────────────────────────────
    if RETRIEVAL_MODE == "hybrid" and all_chunks:
        from core.hybrid_retriever import build_hybrid_retriever
        retriever = build_hybrid_retriever(vectorstore, all_chunks, k=RETRIEVER_K)
    else:
        retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})

    llm = get_llm()

    # ── Simple prompt-only chain (no retriever piping) ────────────────────────
    # We do NOT pipe retriever | _format_docs here because HybridRetriever is
    # not a LangChain Runnable and the | operator would raise a TypeError.
    # The ask() function below handles retrieval + history injection manually.
    prompt = PromptTemplate(
        template=RAG_PROMPT,
        input_variables=["context", "question", "history"],
    )
    chain = prompt | llm | StrOutputParser()

    return chain, retriever


def ask(chain, retriever, question: str, messages: list) -> str:
    """
    Invoke the chain with memory-injected history.

    This is the single entry point for all chat queries. It:
      1. Pulls relevant docs via the retriever (FAISS or HybridRetriever)
      2. Formats prior conversation history
      3. Builds the full prompt and calls the LLM

    Args:
        chain:     The LangChain prompt | llm | parser chain.
        retriever: FAISS retriever or HybridRetriever.
        question:  The user's current message.
        messages:  Full st.session_state.messages list (EXCLUDING this turn).

    Returns:
        The assistant's answer string.
    """
    # Retrieve relevant document chunks
    if hasattr(retriever, "invoke"):
        docs = retriever.invoke(question)
    else:
        docs = retriever.get_relevant_documents(question)

    context      = _format_docs(docs)
    history_text = format_history(messages)

    return chain.invoke({
        "context":  context,
        "question": question,
        "history":  history_text,
    })