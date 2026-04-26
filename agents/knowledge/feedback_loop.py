"""Cross-crew feedback logic."""

from agents.knowledge.knowledge_store import KnowledgeStore
from agents.knowledge.data_access import DataAccessLayer


def retention_to_market_access():
    """Send churned customer archetypes from retention to market access crew."""
    archetypes_df = DataAccessLayer.get_churned_customer_archetypes()
    if archetypes_df.empty:
        return None

    insight_data = {
        "churned_archetypes": archetypes_df.to_dict(orient="records"),
        "summary": f"Found {len(archetypes_df)} churn archetype patterns to exclude from ICP",
    }

    return KnowledgeStore.save_feedback(
        source_crew="retention",
        target_crew="market_access",
        insight_type="churned_archetypes",
        insight_data=insight_data,
    )


def market_access_to_retention():
    """Send high-performing segment benchmarks from market access to retention crew."""
    segment_df = DataAccessLayer.get_revenue_by_segment()
    if segment_df.empty:
        return None

    # Find top-performing segments as benchmarks
    top_segments = segment_df.nlargest(10, "total_revenue")
    insight_data = {
        "top_segments": top_segments.to_dict(orient="records"),
        "summary": f"Top {len(top_segments)} segments by revenue as retention benchmarks",
    }

    return KnowledgeStore.save_feedback(
        source_crew="market_access",
        target_crew="retention",
        insight_type="segment_benchmarks",
        insight_data=insight_data,
    )


def run_feedback_sync():
    """Run both directions of cross-crew feedback."""
    r2m = retention_to_market_access()
    m2r = market_access_to_retention()
    return {"retention_to_market": r2m, "market_to_retention": m2r}
