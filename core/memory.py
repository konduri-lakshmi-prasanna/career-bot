"""
memory.py — Conversation memory management for CareerBot.

Provides a window-buffered chat history that is injected into the RAG prompt,
giving the LLM awareness of previous turns without exploding the context window.
"""

from typing import List, Dict
from core.config import MEMORY_WINDOW_SIZE


def format_history(messages: List[Dict[str, str]]) -> str:
    """
    Convert the last MEMORY_WINDOW_SIZE message-pairs from session state into
    a plain-text block suitable for prompt injection.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."} dicts.

    Returns:
        A formatted string like:
            Human: ...
            Assistant: ...
        or an empty string if there is no prior history.
    """
    if not messages:
        return ""

    # Take only the last N *pairs* (user + assistant) — each pair = 2 messages
    window = messages[-(MEMORY_WINDOW_SIZE * 2):]

    lines: List[str] = []
    for msg in window:
        role = "Human" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")

    return "\n".join(lines)


def trim_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Return a trimmed copy of the message list, keeping only the last
    MEMORY_WINDOW_SIZE pairs.  Used by state.py to prevent unbounded growth.

    Args:
        messages: Full message history.

    Returns:
        Trimmed list (at most MEMORY_WINDOW_SIZE * 2 items).
    """
    max_items = MEMORY_WINDOW_SIZE * 2
    if len(messages) <= max_items:
        return messages
    return messages[-max_items:]