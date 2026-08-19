"""
core/web_search.py — DuckDuckGo Web Search helper.
"""

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches DuckDuckGo for the given query and returns results formatted as RAG chunks.
    
    Args:
        query: The user query or rewritten query.
        max_results: Maximum results to retrieve.
        
    Returns:
        List of dicts: [{
            "text": "...",
            "metadata": {"source": "web_search", "url": "...", "title": "..."},
            "distance": 0.25
        }]
    """
    chunks = []
    try:
        from duckduckgo_search import DDGS
        print(f"[web_search] Searching DuckDuckGo for: '{query}'")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            for r in results:
                title = r.get("title", "Untitled")
                body = r.get("body", "")
                url = r.get("href", "")
                if not body:
                    continue
                chunks.append({
                    "text": f"Title: {title}\nSnippet: {body}",
                    "metadata": {
                        "source": "web_search",
                        "url": url,
                        "title": title
                    },
                    "distance": 0.25
                })
    except ImportError:
        print("[web_search] Warning: duckduckgo_search is not installed. Skipping web search.")
    except Exception as e:
        print(f"[web_search] Error during DuckDuckGo search: {e}")
    return chunks
