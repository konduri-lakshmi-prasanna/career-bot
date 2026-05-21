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


CAREERBOT_SYSTEM_PROMPT = """You are CareerBot — an AI career guidance assistant.
You help students with resume analysis, interview preparation,
career path guidance, and job search strategies.
Answer ONLY using the provided context. Do not hallucinate.
If you don't have enough information, say so clearly."""


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
        Returns list[dict] with keys: text, metadata, distance.
        """
        return retrieve_chunks(
            query,
            collection_name=self.COLLECTION,
            k=self.top_k * 3,
        )

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