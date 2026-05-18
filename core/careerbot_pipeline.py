"""
careerbot_pipeline.py

Careerbot's own pipeline extending the shared rag-core.
This is the Open/Closed Principle:
  - rag-core (IRagPipeline) never changes
  - CareerBotPipeline extends it with careerbot-specific behaviour
"""

from rag_core.default_pipeline import DefaultRagPipeline
from core.vectorstore import build_index, load_index, get_embeddings
from core.chunkers import chunk_documents
from core.loaders import load_documents
from core.chain import ask, build_chain, get_llm
from core.hybrid_retriever import build_hybrid_retriever
from core.config import RETRIEVER_K


CAREERBOT_SYSTEM_PROMPT = """You are CareerBot — an AI career guidance assistant.
You help students with resume analysis, interview preparation,
career path guidance, and job search strategies.
Answer ONLY using the provided context. Do not hallucinate.
If you don't have enough information, say so clearly."""


class CareerBotPipeline(DefaultRagPipeline):
    """
    Careerbot's custom RAG pipeline.
    Extends DefaultRagPipeline with careerbot-specific settings.
    Uses careerbot's own ChromaDB, hybrid retriever, and chunker.
    """

    def __init__(self):
        super().__init__(
            collection_name="careerbot",
            top_k=6,
            rerank_strategy="rrf",
            context_hint="career guidance, resume analysis, placement preparation",
            system_prompt=CAREERBOT_SYSTEM_PROMPT,
        )
        # careerbot uses its own vectorstore and hybrid retriever
        self._vectorstore = None
        self._retriever = None
        self._chain = None
        self._load_existing()

    def _load_existing(self):
        """Load existing ChromaDB index on startup."""
        try:
            vectorstore, all_chunks = load_index()
            if vectorstore:
                self._vectorstore = vectorstore
                self._chain, self._retriever = build_chain(vectorstore, all_chunks)
        except Exception as e:
            print(f"[careerbot_pipeline] Could not load index: {e}")

    def rebuild(self):
        """Rebuild the knowledge base from scratch."""
        vectorstore, all_chunks, errors = build_index()
        if vectorstore:
            self._vectorstore = vectorstore
            self._chain, self._retriever = build_chain(vectorstore, all_chunks)
        return errors

    def retrieve(self, query: str) -> list:
        """Stage 2: Use careerbot's own HybridRetriever."""
        if not self._retriever:
            return []
        if hasattr(self._retriever, "invoke"):
            docs = self._retriever.invoke(query)
        else:
            docs = self._retriever.get_relevant_documents(query)
        # convert LangChain docs to plain dicts for rag-core compatibility
        return [{"text": d.page_content, "metadata": d.metadata, "distance": 0.5}
                for d in docs]

    def generate(self, query: str, context: str) -> str:
        """Stage 5: Use careerbot's own LLM chain with memory support."""
        if self._chain:
            from core.chain import _format_docs
            return self._chain.invoke({
                "context": context,
                "question": query,
                "history": "",
            })
        return "Knowledge base not loaded. Please upload documents first."

    def insert(self, text: str, metadata: dict = None) -> dict:
        """Stage 6: Insert document into careerbot's ChromaDB."""
        from rag_core.stages.insert import insert_document
        return insert_document(text, "careerbot", metadata=metadata)