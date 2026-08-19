"""
careerbot_pipeline.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: overrode retrieve() with HybridRetriever, generate() with LangChain
        chain, and insert() with a local helper. Imported from core.vectorstore,
        core.chain, core.hybrid_retriever.

AFTER:  Only overrides what is genuinely careerbot-specific:
        • __init__  — collection name, top_k, system prompt
        • retrieve() — delegates to rag_core.stages.retrieval
        • rebuild() — uses careerbot loaders/chunkers, then rag_core insert
        generate(), rewrite(), rerank(), refine(), insert() are all
        inherited from DefaultRagPipeline unchanged.
"""

from rag_core.default_pipeline import DefaultRagPipeline
from rag_core.stages.insert import insert_document
from rag_core.stages.retrieval import retrieve_chunks

from core.loaders import load_documents
from core.chunkers import chunk_documents


CAREERBOT_SYSTEM_PROMPT = """You are CareerBot, an AI career guidance assistant.

You will receive CONTEXT containing information retrieved from the user's uploaded
documents such as their resume, education, skills, projects, experience, and achievements.

IMPORTANT RULES:

1. Treat the retrieved CONTEXT as the user's actual profile.
2. For personal questions such as:
   - "What career suits me?"
   - "What jobs are suitable for me?"
   - "What are my strengths?"
   - "What skills do I have?"
   - "What should I prepare for?"
   use the user's uploaded-document information from CONTEXT.
3. Do NOT say that the user's education, skills, or experience are unavailable if those
   details are present anywhere in CONTEXT.
4. Base factual claims about the user ONLY on CONTEXT.
5. You may reason over the information in CONTEXT. For example, if the resume contains
   Java, Python, React, FastAPI, AI/RAG projects, and full-stack experience, you may
   conclude that software engineering, full-stack development, and AI-oriented roles
   are relevant career directions.
6. Do not invent qualifications, experience, companies, salaries, or achievements that
   are not present in CONTEXT.
7. If the context genuinely does not contain enough information, clearly say what is
   missing.
8. Give a direct, personalized answer rather than asking the user to repeat information
   that is already present in CONTEXT.
"""


class CareerBotPipeline(DefaultRagPipeline):
    """
    Careerbot's custom RAG pipeline.
    Extends DefaultRagPipeline — only careerbot-specific behaviour lives here.
    All 6 rag-core stages run via pipeline.run(query).
    """

    COLLECTION = "careerbot"

    def __init__(self):
        super().__init__(
            collection_name=self.COLLECTION,
            top_k=6,
            rerank_strategy="rrf",
            context_hint="career guidance, resume analysis, placement preparation",
            system_prompt=CAREERBOT_SYSTEM_PROMPT,
        )

    # ── Stage 2 override ─────────────────────────────────────────────────────

    def retrieve(self, query: str) -> list:
        """
        Stage 2: Retrieve from careerbot's ChromaDB collection via rag-core.
        Also retrieves from the web if web search is enabled or if local documents are empty.
        Returns list[dict] with keys: text, metadata, distance.
        """
        # 1. Retrieve from local database (if documents are uploaded)
        chunks = []
        try:
            chunks = retrieve_chunks(
                query,
                collection_name=self.COLLECTION,
                k=self.top_k * 3,
            )
        except Exception as e:
            print(f"[pipeline] ChromaDB retrieval failed: {e}")

        # 2. Check if web search should be used
        web_search_enabled = False
        try:
            import streamlit as st
            # Default to True if st is active but state doesn't have it yet
            web_search_enabled = st.session_state.get("web_search_enabled", True)
        except Exception:
            # Safe default outside Streamlit (e.g. testing / evaluation)
            web_search_enabled = False

        # If local DB is empty, auto-fallback to web search even if toggle is off
        # so the user can still get answers.
        local_db_empty = len(chunks) == 0
        if web_search_enabled or local_db_empty:
            from core.web_search import search_web
            web_chunks = search_web(query, max_results=self.top_k)
            # Combine chunks. Rerank (Stage 3) will handle filtering and ranking them!
            chunks.extend(web_chunks)

        return chunks

    # ── Rebuild: careerbot loaders + chunkers → rag-core insert ──────────────

    def rebuild(self) -> list:
        """
        1. Load docs via careerbot's loaders (PDF, TXT, OCR).
        2. Chunk via careerbot's semantic/section-aware chunker.
        3. Insert each chunk via rag_core.stages.insert.
        Returns list of loading error strings.
        """
        documents, errors = load_documents()
        if not documents:
            return errors

        chunks = chunk_documents(documents)
        for chunk in chunks:
            insert_document(
                text=chunk.page_content,
                collection_name=self.COLLECTION,
                metadata=dict(chunk.metadata),
                chunk_size=9999,   # already chunked; send as-is
                overlap=0,
                doc_id_prefix="careerbot",
            )
        return errors