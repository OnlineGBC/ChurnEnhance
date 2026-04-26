"""LangGraph agent state definitions."""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state for all agents in the graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    crew: str
    llm_model: str
    customer_no: str | None
    segment: str | None
    # Data passed between agents
    customer_data: dict | None
    churn_scores: list | None
    diagnoses: list | None
    interventions: list | None
    icp_profiles: list | None
    lead_scores: list | None
    feedback: list | None
    # Tracking
    tokens_used: int
    status: str
