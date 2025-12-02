"LangGraph orchestration across specialized agents."

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from agents import ComparativeAgent, PlaybookAgent, TimelineAgent
from core.scoring import DealScorer


class GraphState(TypedDict, total=False):
    raw_context: str
    deal_summary: str
    retrieved_chunks: list[str]
    timeline: dict[str, Any]
    comparative: dict[str, Any]
    playbook: dict[str, Any]
    scorecard: dict[str, float]


@dataclass
class DealForensicsGraph:
    timeline_agent: TimelineAgent
    comparative_agent: ComparativeAgent
    playbook_agent: PlaybookAgent
    scorer: DealScorer

    def __post_init__(self) -> None:
        graph = StateGraph(GraphState)
        graph.add_node("timeline", self._timeline_node)
        graph.add_node("comparative", self._comparative_node)
        graph.add_node("playbook", self._playbook_node)
        graph.add_node("score", self._score_node)

        graph.set_entry_point("timeline")
        graph.add_edge("timeline", "comparative")
        graph.add_edge("comparative", "playbook")
        graph.add_edge("playbook", "score")
        graph.add_edge("score", END)

        self._graph = graph.compile()

    def _timeline_node(self, state: GraphState) -> GraphState:
        timeline = self.timeline_agent.analyze(state["raw_context"])
        return {**state, "timeline": timeline}

    def _comparative_node(self, state: GraphState) -> GraphState:
        comparative = self.comparative_agent.analyze(
            deal_summary=state["deal_summary"],
            timeline=state["timeline"],
            retrieved=state.get("retrieved_chunks", []),
        )
        return {**state, "comparative": comparative}

    def _playbook_node(self, state: GraphState) -> GraphState:
        playbook = self.playbook_agent.analyze(
            deal_summary=state["deal_summary"],
            timeline=state["timeline"],
            comparative=state["comparative"],
            raw_document=state.get("raw_context", ""),  # Pass raw document for document-specific analysis
        )
        return {**state, "playbook": playbook}

    def _score_node(self, state: GraphState) -> GraphState:
        scorecard = self.scorer.score(
            timeline=state["timeline"],
            comparative=state["comparative"],
            playbook=state["playbook"],
        )
        return {**state, "scorecard": scorecard.as_dict()}

    def run(self, initial_state: GraphState) -> GraphState:
        return self._graph.invoke(initial_state)

