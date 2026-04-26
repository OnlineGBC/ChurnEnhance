"""LangChain tools for Market Access agents."""

from langchain_core.tools import tool
from agents.knowledge.data_access import DataAccessLayer


@tool
def get_revenue_by_segment() -> str:
    """Get revenue and customer metrics aggregated by industry/segment."""
    df = DataAccessLayer.get_revenue_by_segment()
    return df.to_string(index=False, max_rows=50)


@tool
def get_product_performance() -> str:
    """Get product-level performance metrics including revenue and customer counts."""
    df = DataAccessLayer.get_product_performance()
    return df.to_string(index=False, max_rows=50)


@tool
def get_region_performance() -> str:
    """Get region-level performance including churn rates."""
    df = DataAccessLayer.get_region_performance()
    return df.to_string(index=False)


@tool
def get_churned_archetypes() -> str:
    """Get archetypes of churned customers for ICP exclusion."""
    df = DataAccessLayer.get_churned_customer_archetypes()
    if df.empty:
        return "No churned customer archetypes found."
    return df.to_string(index=False)


MARKET_ACCESS_TOOLS = [
    get_revenue_by_segment,
    get_product_performance,
    get_region_performance,
    get_churned_archetypes,
]
