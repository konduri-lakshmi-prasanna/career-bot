from rag_core.default_pipeline import DefaultRagPipeline

# Initialize pipeline once (important)
pipeline = DefaultRagPipeline(collection_name="careerbot")

def ask(query: str) -> str:
    """
    Sends query through RAG pipeline and returns final answer
    """
    try:
        result = pipeline.run(query)

        # Adjust based on your pipeline output format
        if isinstance(result, dict):
            return result.get("answer", str(result))

        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"