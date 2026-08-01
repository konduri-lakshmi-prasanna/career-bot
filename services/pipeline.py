"""
services/pipeline.py  ←  CHANGED

What changed and why
─────────────────────
BEFORE: rebuild_knowledge_base() returned (chain, retriever, errors).
        load_existing_knowledge_base() returned (chain, retriever).
        Callers stored chain + retriever in session_state manually.

AFTER:  rebuild_knowledge_base() returns only errors.
        load_existing_knowledge_base() returns a bool.
        run_query(query) is the single entry point for all chat queries —
        it calls pipeline.run() which executes all 6 rag-core stages.
        No chain or retriever ever leaks into the UI layer.

        NEW: run_query() now checks if the user typed more than one
        question in the same message. If so, it runs the full pipeline
        once per question instead of once for the whole message.
"""

from core.careerbot_pipeline import CareerBotPipeline
from rag_core.db.chromadb_store import get_collection
from rag_core.llm.factory import get_llm

_pipeline: CareerBotPipeline | None = None


def get_pipeline() -> CareerBotPipeline:
    """Return (or create) the singleton CareerBotPipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = CareerBotPipeline()
    return _pipeline


def rebuild_knowledge_base() -> list:
    """
    Rebuild the knowledge base. Returns list of error strings.
    """
    pipeline = get_pipeline()
    return pipeline.rebuild()


def load_existing_knowledge_base() -> bool:
    """
    Returns True if the ChromaDB collection exists and has documents.
    """
    try:
        collection = get_collection(CareerBotPipeline.COLLECTION)
        return collection.count() > 0
    except Exception:
        return False


def split_questions(query: str) -> list[str]:
    """
    Checks if the user typed more than one question in a single message.
    If yes, splits it into separate questions.
    If no, returns the original message unchanged (as a list with 1 item).
    """
    llm = get_llm()

    prompt = f"""Look at the message below and decide if it contains more
than one distinct question or request.

If it contains only ONE question, reply with exactly:
ONE

If it contains MULTIPLE questions, reply with each question on its own
line, rewritten so it can be understood on its own (no "and", no shared
pronouns between them). Do not number them. Do not add any explanation.

Message: {query}
"""

    try:
        response = llm.invoke(prompt)
        text = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        print(f"[split_questions] Warning: split failed ({e}), using original query")
        return [query]

    if text == "ONE" or not text:
        return [query]

    questions = [line.strip() for line in text.split("\n") if line.strip()]
    return questions if questions else [query]


def run_query(query: str) -> str:
    """
    Run the full 6-stage RAG pipeline for a user query.
    Stages: rewrite → retrieve → rerank → refine → generate

    If the user asked more than one question in the same message,
    each question is run through the pipeline separately (its own
    retrieval + generation), then the answers are combined. This
    avoids one question's retrieval "drowning out" the other's.
    """
    pipeline = get_pipeline()
    questions = split_questions(query)

    if len(questions) == 1:
        return pipeline.run(questions[0])

    parts = []
    for question in questions:
        answer = pipeline.run(question)
        parts.append(f"{question}\n{answer}")

    return "\n\n".join(parts)