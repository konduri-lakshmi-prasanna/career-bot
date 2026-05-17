"""
memory.py — Conversation memory management for CareerBot.

CHANGES:
  • Added save_history() — saves messages to data/chat_history.json
  • Added load_history() — loads messages from disk on startup
"""

import json
import os
from typing import List, Dict
from core.config import MEMORY_WINDOW_SIZE, BASE_DIR

HISTORY_FILE = os.path.join(BASE_DIR, "data", "chat_history.json")


def save_history(messages: List[Dict[str, str]]) -> None:
    """Save the current message list to disk as JSON."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)


def load_history() -> List[Dict[str, str]]:
    """Load message history from disk. Returns empty list if file doesn't exist."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def format_history(messages: List[Dict[str, str]]) -> str:
    if not messages:
        return ""
    window = messages[-(MEMORY_WINDOW_SIZE * 2):]
    lines: List[str] = []
    for msg in window:
        role = "Human" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


def trim_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    max_items = MEMORY_WINDOW_SIZE * 2
    if len(messages) <= max_items:
        return messages
    return messages[-max_items:]