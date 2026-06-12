"""
Debate Module
Orchestrates the sequential AI analyst debate and voting system.
"""

from app.agents.debate.debate_engine import AgentState, build_debate_engine_graph

__all__ = [
    "AgentState",
    "build_debate_engine_graph"
]
