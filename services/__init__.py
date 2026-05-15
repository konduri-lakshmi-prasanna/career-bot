"""
services — Orchestration layer for CareerBot.

Sits between the core logic and the UI. Coordinates multi-step workflows
(e.g. ingest → chunk → index → chain) and shared business actions.
"""

from services.pipeline import rebuild_knowledge_base
from services.actions import run_quick_action
